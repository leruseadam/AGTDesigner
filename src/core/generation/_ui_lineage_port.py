import re
from functools import lru_cache
from typing import Any, Dict

from src.core.constants import CLASSIC_TYPES


def canonical_product_type_for_classic_check(lower_pt: str) -> str:
    """
    Map authoritative Product Type* strings to a key that exists in CLASSIC_TYPES.
    Uses **only** the type field (never product name) so we don't misclassify
    dessert/fruit strain names as something else.
    """
    t = (lower_pt or "").strip().lower()
    if t in ("unknown", "not_found", "nan", "none"):
        return ""
    if "disposable vape" in t or ("disposable" in t and "vape" in t):
        return "disposable"
    if "disposable cart" in t:
        return "vape cartridge"
    if "vaporizer" in t or "vapouriser" in t or "vapourizer" in t:
        return "disposable"
    return t


@lru_cache(maxsize=512)
def _lookup_product_type_from_db(json_token: str) -> str:
    """Cached DB lookup for product type by JSON token. Opens connection once per unique token."""
    try:
        import sqlite3
        from src.core.data.product_database import get_database_path
        db_path = get_database_path('AGT_Bothell')
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute('SELECT "Product Type*" FROM products WHERE JSON = ? COLLATE NOCASE', (json_token,))
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip().lower()
        finally:
            conn.close()
    except Exception:
        pass
    return ""


def compute_display_lineage_like_ui(record: Dict[str, Any]) -> str:
    """
    Port of the frontend TagManager lineage/color logic.

    If the record already contains `displayLineage` (sent from the UI),
    that value is used directly. Otherwise we recompute the same logic
    the UI uses to derive displayLineage.
    """
    # Absolute first priority: value explicitly computed by the UI (unless MIXED - then re-check for CBG/CBD)
    ui_display = record.get("displayLineage") or record.get("display_lineage")
    if ui_display:
        result = str(ui_display).strip().upper()
        # When UI says MIXED, still re-check product name/description for CBG/CBD so we get yellow
        if result == "MIXED":
            name_str_check = str(
                record.get("Product Name*")
                or record.get("ProductName")
                or record.get("productName")
                or record.get("Product Name")
                or record.get("product_name")
                or ""
            ).lower()
            desc_str_check = str(record.get("Description") or record.get("description") or "").lower()
            ratio_str_check = str(record.get("Ratio") or record.get("Ratio_or_THC_CBD") or "").lower()
            tokens = ["cbd", "cbg", "cbn", "cbc"]
            if any(tok in name_str_check or tok in desc_str_check or tok in ratio_str_check for tok in tokens):
                return "CBD_BLEND"
            ratio_pattern = re.compile(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)*\b')
            for src in [name_str_check, ratio_str_check, desc_str_check]:
                if src and ratio_pattern.search(src):
                    return "CBD_BLEND"
        # Normalize CBD family (CBD, CBG, CBN, CBC) -> CBD_BLEND for yellow color
        if result in ('CBD', 'CBG', 'CBN', 'CBC'):
            result = 'CBD_BLEND'
        return result
    # Resolve lineage from most authoritative fields
    lineage_candidates = [
        record.get("sovereign_lineage"),
        record.get("canonical_lineage"),
        record.get("currentLineage"),
        record.get("Lineage"),
        record.get("lineage"),
    ]
    lineage: str | None = None
    for cand in lineage_candidates:
        if cand:
            s = str(cand).strip().upper()
            if s and s != "SOVEREIGN":
                lineage = s
                break

    # Product type normalization (matches TagManager productTypeCheck)
    product_type_check = (
        record.get("Product Type*")
        or record.get("productType")
        or record.get("ProductType")
        or ""
    )
    lower_product_type = str(product_type_check).strip().lower()

    # Defensive: if product_type is missing/ambiguous on the record, prefer the authoritative
    # database `Product Type*` when a JSON/SKU identifier is present. This prevents client-side
    # overrides or cached tag payloads from misclassifying products across different machines.
    if (not lower_product_type or lower_product_type in {"", "unknown", "not_found"}):
        json_token = record.get('JSON') or record.get('json') or record.get('product_json')
        if json_token:
            result = _lookup_product_type_from_db(str(json_token).strip())
            if result:
                lower_product_type = result

    # Classic vs nonclassic: **Product Type* only** (+ canonical aliases for that field).
    canonical_pt = canonical_product_type_for_classic_check(lower_product_type)
    is_classic_type = canonical_pt in CLASSIC_TYPES
    is_paraphernalia_type = lower_product_type == "paraphernalia"

    # Do not rewrite explicit lineage from product-name heuristics — trust lineage fields from data.

    # Default lineage when completely missing
    if not lineage:
        lineage = "HYBRID" if is_classic_type else "MIXED"

    name_str = str(
        record.get("Product Name*")
        or record.get("ProductName")
        or record.get("productName")
        or record.get("Product Name")
        or record.get("product_name")
        or ""
    ).lower()
    desc_str = str(record.get("Description") or record.get("description") or "").lower()
    brand_str = str(
        record.get("Product Brand")
        or record.get("ProductBrand")
        or record.get("productBrand")
        or record.get("brand")
        or ""
    ).lower()
    ratio_str = str(
        record.get("Ratio") or record.get("Ratio_or_THC_CBD") or ""
    ).lower()
    lineage_str = str(lineage or "").lower()

    def has_cbd_indicator() -> bool:
        # Check for CBD family tokens in name, description, brand, ratio, or lineage
        tokens = ["cbd", "cbg", "cbn", "cbc"]
        sources = [name_str, desc_str, brand_str, ratio_str, lineage_str]
        if any(token in text for token in tokens for text in sources if text):
            return True
        # CRITICAL: Ratio patterns (1:1, 2:1, 1:1:1, etc.) in name or ratio fields mean CBD
        # This is the PRIMARY way to detect CBD products when Product Strain is not used
        ratio_sources = [name_str, ratio_str, desc_str]
        ratio_pattern = re.compile(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)*\b')
        for source in ratio_sources:
            if source and ratio_pattern.search(source):
                return True
        cbd_family_in_type = [
            "high cbd",
            "cbd",
            "high cbg",
            "cbg",
            "high cbn",
            "cbn",
            "high cbc",
            "cbc",
        ]
        return any(indicator in lower_product_type for indicator in cbd_family_in_type)

    # Database lineage validity (same set as frontend)
    # CBG, CBN, CBC get same yellow color as CBD (CBD_BLEND)
    valid_db_lineages = {
        "SATIVA",
        "INDICA",
        "HYBRID",
        "HYBRID/SATIVA",
        "HYBRID/INDICA",
        "CBD",
        "CBD_BLEND",
        "CBG",
        "CBN",
        "CBC",
        "MIXED",
        "PARA",
        "PARAPHERNALIA",
    }
    has_valid_db_lineage = lineage in valid_db_lineages

    classic_lineages = [
        "SATIVA",
        "INDICA",
        "HYBRID",
        "HYBRID/SATIVA",
        "HYBRID/INDICA",
    ]
    is_classic_lineage = lineage in classic_lineages
    is_nonclassic = not is_classic_type

    # Paraphernalia override (driven by Product Type*, not name parsing)
    if is_paraphernalia_type:
        return "PARAPHERNALIA"

    display_lineage = lineage

    if is_nonclassic:
        # CRITICAL: CBD detection should rely on product name/description/ratio fields,
        # NOT Product Strain (which is no longer used as a placeholder)
        # Product Strain check is kept for backward compatibility but not required
        product_strain = (
            record.get("Product Strain")
            or record.get("productStrain")
            or record.get("ProductStrain")
            or ""
        )
        strain_str = str(product_strain).lower()
        has_cbd_in_strain = any(
            token in strain_str
            for token in ["cbd blend", "cbd", "cbn", "cbc", "cbg"]
        )
        has_cbd_in_product = has_cbd_indicator()

        # CRITICAL: For non-classic types, prioritize CBD detection from product fields
        # Product Strain is optional - CBD detection works from name/description/ratio alone
        if has_cbd_in_product:
            # Product name/description/ratio has CBD indicators (e.g., "1:1:1" ratios)
            display_lineage = "CBD_BLEND"
        elif has_cbd_in_strain:
            # Fallback: Product Strain also indicates CBD
            display_lineage = "CBD_BLEND"
        elif (not is_classic_lineage) and has_valid_db_lineage and lineage in ("CBD_BLEND", "CBD", "CBG", "CBN", "CBC"):
            # Record lineage CBD family (CBD, CBG, CBN, CBC) -> use yellow CBD color
            display_lineage = "CBD_BLEND"
        elif lower_product_type == "paraphernalia" or "paraphernalia" in strain_str:
            display_lineage = "PARAPHERNALIA"
        elif (not is_classic_lineage) and has_valid_db_lineage and lineage in {
            "PARAPHERNALIA",
            "PARA",
        }:
            display_lineage = "PARAPHERNALIA"
        else:
            display_lineage = "MIXED"
    else:
        # Classic types: force CBD_BLEND when any CBD family indicator is present
        if has_cbd_indicator():
            display_lineage = "CBD_BLEND"
        else:
            display_lineage = lineage or "HYBRID"

    return display_lineage

