import re
import logging
from typing import Optional, Dict, List, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

# Module-level cache for auto-detected subbrands (populated per batch)
_auto_detected_subbrands: Dict[str, str] = {}


def auto_detect_subbrands(records: List[Dict[str, Any]]) -> Dict[str, str]:
    """Auto-detect infused pre-roll subbrands from product names.

    Scans all infused pre-roll product names, extracts candidate n-grams
    from the end of the prefix before "Infused Pre-Roll", and returns those
    that appear with 3+ DISTINCT preceding strain contexts.

    This distinguishes real subbrands (e.g. "Honey Stixx" appears after
    "Blueberry x Purple Churro", "Cherry Pie x Sour Patch Kiss", etc.)
    from strain fragments (e.g. "Cheese" always appears after "Blue").

    Returns:
        Dict mapping lowercase subbrand -> Canonical cased name.
        Example: {'honey stixx': 'Honey Stixx', 'snickerdoobie': 'SnickerDoobie'}
    """
    global _auto_detected_subbrands

    # Regex to capture everything before "Infused Pre-Roll"
    prefix_re = re.compile(
        r'^(.+?)\s+Infused\s+Pre[-\s]?Rolls?\b',
        re.IGNORECASE
    )
    # Also handle "Infused ... Blunt" pattern
    blunt_re = re.compile(
        r'^(.+?)\s+Infused\s+(Palm\s+)?Blunts?\b',
        re.IGNORECASE
    )

    # Words that disqualify ANY n-gram they appear in (type/filler words)
    always_stop = {
        'infused', 'pre-roll', 'preroll', 'pre', 'roll', 'rolls',
        'by', 'the', 'a', 'an', 'and', 'or', 'of', 'in', 'for',
        'pack', 'gram', 'grams', 'oil', 'resin', 'live', 'cured',
    }
    # Common strain tokens — only block as 1-gram candidates, NOT within multi-word subbrands.
    # E.g. "OG" alone is blocked, but "Sugar Cone" (2-gram) is allowed despite "sugar".
    strain_tokens = {
        'og', 'kush', 'haze', 'diesel', 'cookies', 'cake', 'gelato',
        'dream', 'widow', 'cheese', 'berry', 'purple', 'blue', 'white',
        'sour', 'super', 'lemon', 'mango', 'cherry', 'banana', 'grape',
        'strawberry', 'watermelon', 'pineapple', 'runtz', 'zkittlez',
        'glue', 'jack', 'gorilla', 'punch', 'mint', 'ice', 'cream',
        'pie', 'candy', 'butter', 'cough',
    }

    # Track: candidate -> set of distinct preceding contexts (strain names)
    candidate_contexts: Dict[str, Set[str]] = defaultdict(set)
    candidate_canonical: Dict[str, str] = {}  # first-seen casing

    for record in records:
        product_name = str(
            record.get('Product Name*', '') or
            record.get('ProductName', '') or ''
        ).strip()
        if not product_name:
            continue

        pn_lower = product_name.lower()
        if 'infused' not in pn_lower:
            continue

        # Extract prefix (everything before "Infused Pre-Roll")
        m = prefix_re.match(product_name)
        if not m:
            m = blunt_re.match(product_name)
        if not m:
            continue

        prefix = m.group(1).strip()
        prefix = re.sub(r'\s+by\s+.*$', '', prefix, flags=re.IGNORECASE).strip()

        words = prefix.split()
        if not words:
            continue

        # Try 1-gram, 2-gram, 3-gram from the END of the prefix
        for n in (1, 2, 3):
            if len(words) < n + 1:  # need at least n+1 words (strain + subbrand)
                continue

            ngram_words = words[-n:]
            ngram_lower = ' '.join(w.lower() for w in ngram_words)
            ngram_original = ' '.join(ngram_words)

            # Skip if any word is an always-stop word or single letter
            if any(w.lower() in always_stop or len(w) <= 1 for w in ngram_words):
                continue
            # For 1-grams, also skip common strain tokens
            if n == 1 and ngram_lower in strain_tokens:
                continue

            # The preceding context is everything BEFORE the n-gram
            preceding_words = words[:-n]
            preceding_context = ' '.join(preceding_words).lower().strip()
            if not preceding_context:
                continue

            candidate_contexts[ngram_lower].add(preceding_context)
            if ngram_lower not in candidate_canonical:
                candidate_canonical[ngram_lower] = ngram_original

    # A real subbrand appears with 3+ DISTINCT preceding strains.
    # Strain fragments like "Cheese" (from "Blue Cheese") may appear 2x
    # but always with the same or very few preceding words.
    MIN_DISTINCT_CONTEXTS = 3

    detected = {}
    for candidate_lower, contexts in candidate_contexts.items():
        if len(contexts) >= MIN_DISTINCT_CONTEXTS:
            detected[candidate_lower] = candidate_canonical[candidate_lower]
            logger.info(
                f"AUTO-DETECT SUBBRAND: '{candidate_canonical[candidate_lower]}' "
                f"found with {len(contexts)} distinct strains: "
                f"{sorted(list(contexts))[:5]}..."
            )

    # Deduplicate: if "honey stixx" (2-gram) and "stixx" (1-gram) both qualify,
    # remove the shorter one that's a suffix of the longer
    to_remove = set()
    sorted_keys = sorted(detected.keys(), key=lambda k: len(k), reverse=True)
    for i, longer in enumerate(sorted_keys):
        for shorter in sorted_keys[i + 1:]:
            if longer.endswith(shorter):
                to_remove.add(shorter)
    for key in to_remove:
        detected.pop(key, None)

    _auto_detected_subbrands = detected

    if detected:
        logger.info(f"AUTO-DETECT SUBBRANDS: Found {len(detected)} subbrands: {list(detected.values())}")
    else:
        logger.info("AUTO-DETECT SUBBRANDS: No subbrands detected from product names")

    return detected


def detect_preroll_subbrand(product_name: str, product_type: str = '',
                            detected_subbrands: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Detect a named subbrand for infused prerolls.

    Checks auto-detected subbrands first, then falls back to hardcoded keywords.

    Returns the canonical replacement string (e.g., 'Firecracker') or None.
    """
    try:
        pn = (product_name or '')
        pname_lower = pn.lower()
        ptype_lower = (product_type or '').lower()

        # Only attempt for infused prerolls
        if 'infused' not in pname_lower and 'infused' not in ptype_lower:
            return None

        # Priority 1: Check auto-detected subbrands
        subbrands_to_check = detected_subbrands or _auto_detected_subbrands
        if subbrands_to_check:
            for sub_lower, canonical in subbrands_to_check.items():
                if sub_lower in pname_lower:
                    return canonical

        # Priority 2: Hardcoded fallback patterns
        subbrand_keywords = {
            r"\b(sparkler|sparklers)\b": 'Sparkler',
            r"\b(firecracker|firecrackers|fire-cracker|fire-crackers)\b": 'Firecracker',
            r"\b(snickerdoobie|snickerdoobies)\b": 'SnickerDoobie',
            r"\b(bloomer|bloomers)\b": 'Bloomer',
            r"\b(honey[-\s]?stix{1,2}|honeystix|honeystixx)\b": 'Honey Stixx',
            r"\b(sugar[-\s]?stix{1,2}|sugarstix|sugarstixx)\b": 'Sugar Stix',
            r"\b(flavour[-\s]?stix|flavor[-\s]?stix|flavourstix)\b": 'Flavour Stix',
            r"\b(melt[-\s]?stix|meltstix)\b": 'Melt Stix',
            r"\b(bang[-\s]?stick|bangstick|bang-stic|bangsticks)\b": 'Bang Stick',
            r"\b(rosin[-\s]?roll|rosinrolls?)\b": 'Rosin Roll',
            r"\b(rosin[-\s]?stick|rosinstick)\b": 'Rosin Stick',
            r"\b(hash[-\s]?hole|hashhole)\b": 'Hash Hole',
            r"\b(hash[-\s]?cannon|hashcannon)\b": 'Hash Cannon',
            r"\b(bubble[-\s]?hash|bubblehash)\b": 'Bubble Hash',
            r"\b(sugar[-\s]?cone|sugarcone)\b": 'Sugar Cone',
            r"\b(rose[-\s]?wrapped|rosewrapped)\b": 'Rose Wrapped',
            r"\b(terp|terps)\b": 'Terp',
            r"\b(thca)\b": 'THCA',
        }

        for pattern, subbrand_name in subbrand_keywords.items():
            if re.search(pattern, pname_lower, re.IGNORECASE):
                return subbrand_name
    except Exception:
        return None
    return None
