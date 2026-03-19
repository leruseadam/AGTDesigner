"""
Infer package weight from product name / description when POS or feeds send generic unit=1.

POSaBit price variants often use unit=1 as "one sellable unit", not net grams — labels then
show '- 1g' for everything. We only override when the parsed weight is clearly that generic case
and the text contains an explicit gram/ounce/joint pattern.
"""
from __future__ import annotations

import re
from typing import Optional

# Edibles / non-flower: do not guess from name (avoid replacing real "1 piece" cases).
_SKIP_INFERENCE_TYPES = frozenset(
    x.lower()
    for x in (
        "Edible (Solid)",
        "Edible (Liquid)",
        "edible (solid)",
        "edible (liquid)",
        "Tincture",
        "Topical",
        "Capsule",
        "Beverage",
        "Drink",
    )
)


def _fmt_g_num(val: str) -> str:
    s = (val or "").strip()
    if s.startswith("."):
        s = "0" + s
    try:
        f = float(s)
    except ValueError:
        return s
    if abs(f - round(f)) < 1e-9:
        return str(int(round(f)))
    t = f"{f:.3f}".rstrip("0").rstrip(".")
    return t


def is_generic_single_unit_weight(combined: Optional[str]) -> bool:
    """True when upstream weight is missing or almost certainly POS 'one unit' == 1g."""
    if combined is None:
        return True
    raw = str(combined).strip()
    if not raw:
        return True
    s = re.sub(r"\s+", "", raw.lower())
    if s in ("1g", "1.0g", "1.00g", "1gm", "1gram", "1grams"):
        return True
    m = re.match(r"^(\d+\.?\d*)g$", s)
    if m:
        try:
            return abs(float(m.group(1)) - 1.0) < 1e-9
        except ValueError:
            pass
    return False


def _product_type_allows_inference(product_type: str) -> bool:
    pt = (product_type or "").strip().lower()
    if not pt:
        return True
    if pt in _SKIP_INFERENCE_TYPES or any(sk in pt for sk in ("edible", "tincture", "topical", "capsule", "beverage", "gummy", "chocolate")):
        return False
    return True


def infer_weight_display_from_texts(
    primary_text: str,
    description: str = "",
    product_type: str = "",
) -> Optional[str]:
    """
    Return a display weight like '3.5g', '1oz', '0.5g x 5 Pack' if found in name/description.
    """
    if not _product_type_allows_inference(product_type):
        return None

    parts = [primary_text or "", description or ""]
    text = " ".join(p.strip() for p in parts if p and str(p).strip()).strip()
    if not text:
        return None

    def _prev_ok(start: int) -> bool:
        if start <= 0:
            return True
        ch = text[start - 1]
        return not (ch.isalnum() or ch in "._")

    # 1) Joint / multi-pack (prefer over lone grams)
    jm = re.search(
        r"(\d*\.\d+|\d+\.\d*|\d+)\s*g\s*x\s*(\d+)\s*(?:pack|pk)?\b",
        text,
        re.IGNORECASE,
    )
    if jm and _prev_ok(jm.start()):
        w, c = jm.group(1), jm.group(2)
        try:
            c_int = int(c)
        except ValueError:
            c_int = 1
        wg = _fmt_g_num(w) + "g"
        if c_int <= 1:
            return wg
        return f"{wg} x {c_int} Pack"

    # 2) Ounces (take last reasonable match — suffix packaging)
    oz_matches = list(
        re.finditer(r"(\d+\.?\d*)\s*(?:oz|ounces?)\b", text, re.IGNORECASE)
    )
    for om in reversed(oz_matches):
        if not _prev_ok(om.start()):
            continue
        try:
            oz = float(om.group(1))
        except ValueError:
            continue
        if not (0.05 <= oz <= 16):
            continue
        if abs(oz - round(oz)) < 1e-9:
            return f"{int(round(oz))}oz"
        t = f"{oz:.3f}".rstrip("0").rstrip(".")
        return f"{t}oz"

    # 3) Grams: grams/gm tokens and spaced "3.5 g" (not substrings of other words)
    candidates: list[tuple[int, float, str]] = []
    for m in re.finditer(r"(\d+\.?\d*|\.\d+)\s*(?:grams?|gm)\b", text, re.IGNORECASE):
        if not _prev_ok(m.start()):
            continue
        val = m.group(1)
        if val.startswith("."):
            val = "0" + val
        try:
            g = float(val)
        except ValueError:
            continue
        if not (0.2 <= g <= 448):
            continue
        if g >= 2000:
            continue
        candidates.append((m.start(), g, val))

    for m in re.finditer(r"(\d+\.?\d*|\.\d+)\s+g\b", text, re.IGNORECASE):
        if not _prev_ok(m.start()):
            continue
        # skip "mg" etc.: match is 'N g' with word boundary after g
        if m.start() >= 1 and text[m.start() - 1].lower() == "m":
            continue
        val = m.group(1)
        if val.startswith("."):
            val = "0" + val
        try:
            g = float(val)
        except ValueError:
            continue
        if not (0.2 <= g <= 448):
            continue
        if g >= 2000:
            continue
        candidates.append((m.start(), g, val))

    # Compact "3.5g", ".5g" (no space) — common in menu names
    for m in re.finditer(r"(\d+\.?\d*|\.\d+)g\b", text, re.IGNORECASE):
        if not _prev_ok(m.start()):
            continue
        if m.start() >= 1 and text[m.start() - 1].lower() == "m":
            continue
        val = m.group(1)
        if val.startswith("."):
            val = "0" + val
        try:
            g = float(val)
        except ValueError:
            continue
        if not (0.2 <= g <= 448):
            continue
        if g >= 2000:
            continue
        candidates.append((m.start(), g, val))

    if not candidates:
        return None

    # Prefer last match in string (weight suffix is most common)
    _, _g, raw = sorted(candidates, key=lambda x: x[0])[-1]
    return _fmt_g_num(raw) + "g"
