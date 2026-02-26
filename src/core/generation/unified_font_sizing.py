#!/usr/bin/env python3
"""
Unified font sizing system that consolidates all font sizing logic.
This module replaces the repetitive font sizing functions across the codebase.
"""

from __future__ import annotations

import logging
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from src.core.utils.common import calculate_text_complexity
import json
import os

logger = logging.getLogger(__name__)

def _load_font_sizing_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'font_sizing_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            raw = json.load(f)
        # Convert all int thresholds to float for compatibility
        for orientation in raw:
            for field in raw[orientation]:
                raw[orientation][field] = [(float(th), float(sz)) for th, sz in raw[orientation][field]]
        return {'standard': raw}
    else:
        # Fallback to built-in defaults (copied from previous FONT_SIZING_CONFIG)
        return {
            'standard': {
                'mini': {
                    'description': [(5, 18), (20, 17), (30, 16), (35, 15), (40, 14), (45, 13), (50, 12), (60, 11), (70, 10), (100, 9), (float('inf'), 8)],
                    'brand': [(5, 10.5), (10, 9.5), (20, 8), (30, 7.5), (float('inf'), 6.5)],
                    'price': [(1, 18), (2, 16), (float('inf'), 14)],
                    'lineage': [(5, 12), (10, 11), (15, 10), (20, 9), (float('inf'), 8)],
                    'ratio': [(3, 12), (6, 11), (9, 10), (12, 9), (float('inf'), 8)],
                    'thc_cbd': [(5, 10), (10, 9), (15, 8), (20, 7), (float('inf'), 6)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(5, 12), (10, 10), (15, 8), (float('inf'), 6)],
                    'doh': [(5, 12), (10, 11), (float('inf'), 10)],
                    'vendor': [(10, 6), (float('inf'), 5)],
                    'qr': [(float('inf'), 24)],  # QR codes: Small size for mini template
                    'default': [(10, 12), (20, 11), (float('inf'), 10)]
                },
                'double': {
                    # Canonical double-template unified font sizing configuration
                    'description': [(5, 32), (10, 30), (15, 28), (20, 26), (25, 25), (30, 24), (35, 23), (40, 22), (45, 20), (50, 19), (60, 18), (80, 17), (100, 16), (120, 14), (float('inf'), 14)],
                    'brand': [(10, 14), (20, 12), (40, 11), (60, 10), (80, 9), (float('inf'), 6.5)],
                    'price': [(10, 26), (15, 20), (float('inf'), 14)],
                    'lineage': [(15, 12), (25, 12), (35, 10), (45, 9), (float('inf'), 9)],
                    'ratio': [(10, 9), (20, 8), (30, 7), (float('inf'), 6.5)],
                    'thc_cbd': [(20, 7),(float('inf'), 6.5)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 14), (25, 12), (35, 10), (float('inf'), 7)],
                    'doh': [(15, 20), (25, 16), (float('inf'), 13)],
                    'vendor': [(10, 6), (float('inf'), 5)],
                    'qr': [(float('inf'), 36)],  # QR codes: Medium size for double template
                    'default': [(20, 16), (40, 14), (60, 12), (float('inf'), 10)]
                },  
                'vertical': {
                    'description': [(10, 36), (20, 34), (25, 32), (30, 30), (40, 28), (50, 26), (60, 25), (80, 24), (100, 22), (120, 20), (140, 18), (float('inf'), 14)],
                    'brand': [(10, 16), (20, 14), (30, 12), (60, 11), (float('inf'), 10)],
                    'price': [(2, 36), (3, 30), (float('inf'), 26)],  # $1/$11 = 36pt, $111+ = 30pt
                    'lineage': [(100, 18), (float('inf'), 14)],  # Max 18pt for lineage to prevent 20pt sizing
                    'ratio': [(10, 14), (20, 12), (30, 9), (float('inf'), 9)],
                    'thc_cbd': [(10, 12), (float('inf'), 12)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 18), (25, 16), (35, 14), (float('inf'), 12)],
                    'doh': [(15, 24), (25, 20), (float('inf'), 18)],
                    'vendor': [(10, 6), (float('inf'), 5)],
                    'qr': [(float('inf'), 45)],  # QR codes: Large size for vertical template
                    'default': [(30, 16), (60, 14), (100, 12), (float('inf'), 10)]
                },
                'horizontal': {
                    'description': [(10, 36), (20, 34), (25, 32), (30, 30), (35, 28), (40, 27), (45, 26), (50, 25), (55, 24), (60, 23), (65, 22), (70, 21), (100, 20), (120, 18), (130, 16), (140, 15), (float('inf'), 14)],
                    'brand': [(20, 18), (40, 16), (120, 14), (140, 12), (160, 10), (float('inf'), 10)],
                    'price': [(5, 40), (10, 38), (20, 36), (80, 20), (float('inf'), 18)],
                    'lineage': [(80, 18), (float('inf'), 10)],
                    'ratio': [(10, 14), (20, 12), (30, 10), (40, 9), (50, 8), (60, 7), (70, 6), (float('inf'), 5)],
                    'thc_cbd': [(10, 14), (float('inf'), 14)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 16), (25, 14), (35, 12), (float('inf'), 10)],
                    'doh': [(15, 22), (25, 18), (float('inf'), 16)],
                    'vendor': [(10, 6), (float('inf'), 6)],
                    'qr': [(float('inf'), 45)],  # QR codes: Large size for horizontal template
                    'default': [(20, 18), (40, 16), (60, 14), (float('inf'), 12)]
                },
                'preroll': {
                    # Canonical double-template unified font sizing configuration
                    'description': [(5, 32), (10, 30), (15, 28), (20, 26), (25, 25), (30, 24), (35, 23), (40, 22), (45, 20), (50, 19), (60, 18), (80, 17), (100, 16), (120, 14), (float('inf'), 14)],
                    'brand': [(10, 12), (20, 10), (40, 9), (60, 8), (100, 7.5), (100, 7), (float('inf'), 6.5)],
                    'price': [(10, 34), (15, 24), (float('inf'), 14)],
                    'lineage': [(15, 12), (25, 12), (35, 10), (45, 9), (float('inf'), 9)],
                    'ratio': [(10, 9), (20, 8), (30, 7), (float('inf'), 6.5)],
                    'thc_cbd': [(20, 7),(float('inf'), 6.5)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 14), (25, 12), (35, 10), (float('inf'), 7)],
                    'doh': [(15, 20), (25, 16), (float('inf'), 13)],
                    'vendor': [(10, 6), (float('inf'), 5)],
                    'qr': [(float('inf'), 40)],  # QR codes: Medium size for double template
                    'default': [(20, 16), (40, 14), (60, 12), (float('inf'), 10)]
                }
            }
        }

FONT_SIZING_CONFIG = _load_font_sizing_config()

def _normalize_brand_text(text):
    """Normalize brand text so apostrophes (curly/Unicode) don't break sizing. Returns stripped str."""
    if text is None:
        return ""
    s = str(text).strip()
    # Replace Unicode apostrophes/quotations with ASCII so letter count and word-split are consistent
    for uc, ascii_char in [
        ("\u2019", "'"),   # RIGHT SINGLE QUOTATION MARK (common in Word/Excel)
        ("\u2018", "'"),   # LEFT SINGLE QUOTATION MARK
        ("\u2032", "'"),   # PRIME
        ("\u00b4", "'"),   # ACUTE ACCENT (often used as apostrophe)
    ]:
        s = s.replace(uc, ascii_char)
    return s


def _vertical_brand_should_use_11pt(text) -> bool:
    """True if brand has more than one word and any word has more than 9 letters (vertical template rule)."""
    if not text:
        return False
    s = _normalize_brand_text(text)
    words = s.split()
    if len(words) <= 1:
        return False
    for w in words:
        letter_count = sum(1 for c in w if c.isalpha())
        if letter_count > 9:
            return True
    return False


def _brand_letter_count(text) -> int:
    """Calculate brand complexity based on letter count."""
    if text is None:
        return 0
    text = _normalize_brand_text(text)
    if not text:
        return 0
    
    # CRITICAL FIX: Extract brand name from markers before counting
    # Handle PRODUCTBRAND_CENTER_START...PRODUCTBRAND_CENTER_END markers
    import re
    brand_match = re.search(r'PRODUCTBRAND(?:_CENTER)?_START(.+?)PRODUCTBRAND(?:_CENTER)?_END', text, re.IGNORECASE)
    if brand_match:
        # Extract just the brand name from between the markers
        text = _normalize_brand_text(brand_match.group(1))
    
    letter_count = sum(1 for ch in text if ch.isalpha())
    if letter_count > 0:
        return letter_count
    # Fallback to non-space characters if no letters are present
    return len(text.replace(" ", ""))


def _get_price_font_size(text: str, orientation_norm: str, scale_factor: float) -> Pt:
    """
    Get font size for price field based on digit count.
    
    Rules:
    - Mini: 1-2 digits = 20pt, 3+ = 15pt
    - Double: 1-2 digits = 28pt, 3 digits = 20pt, 4+ = 16pt
    - Vertical: 1-2 digits = 36pt, 3+ = 30pt
    """
    clean_text = ''.join(ch for ch in str(text or '') if ch.isdigit())
    num_digits = len(clean_text)

    if orientation_norm == 'mini':
        base_size = 20 if num_digits <= 2 else 15
    elif orientation_norm == 'double':
        if num_digits <= 2:
            base_size = 28
        elif num_digits == 3:
            base_size = 20
        else:
            base_size = 16
    else:  # vertical
        base_size = 36 if num_digits <= 2 else 30

    final_size = base_size * scale_factor
    logger.debug(
        f"Price digit rule: text='{text}', digits={num_digits}, "
        f"orientation={orientation_norm}, size={final_size}pt"
    )
    return Pt(final_size)


def _get_brand_guardrail_size(text: str, orientation_norm: str, scale_factor: float) -> Pt | None:
    """
    Get early-return font size for brand fields with length-based guardrails.
    
    Returns:
        Pt if guardrail applies, None if normal sizing should proceed
    """
    brand_len = _brand_letter_count(text)
    
    # Mini/preroll: very long brands (20+ letters) → 6.5pt
    if orientation_norm in ('mini', 'preroll') and brand_len >= 20:
        final_size = 6.5 * scale_factor
        logger.debug(
            f"Mini/preroll brand length rule: text='{text}' "
            f"(letters={brand_len}) -> {final_size}pt"
        )
        return Pt(final_size)
    
    # Double: brands with 8+ letters → 8pt
    if orientation_norm == 'double' and brand_len >= 8:
        final_size = 8 * scale_factor
        logger.debug(
            f"Double brand length rule: text='{text}' "
            f"(letters={brand_len}) -> {final_size}pt"
        )
        return Pt(final_size)
    
    return None


def _apply_vertical_brand_rules(text: str, base_size: float, scale_factor: float) -> float:
    """
    Apply vertical template brand special rules.
    
    Rule: If brand has more than one word and any word has >9 letters → 11pt
    """
    if _vertical_brand_should_use_11pt(text):
        final_size = 11 * scale_factor
        logger.debug(
            f"Vertical brand long-word rule: text='{text}' has >1 word and a word with >9 letters -> 11pt"
        )
        return final_size
    return base_size


def _apply_double_template_description_rules(text: str, base_size: float, scale_factor: float) -> float:
    """
    Apply all special rules for double template descriptions.
    
    Rules (applied in order):
    1. Words with 10+ letters → reduce by 1pt
    2. Words with 12+ letters → reduce by 2pt (additional reduction)
    3. Words with >10 letters (11+) → cap at 19pt
    4. Words with >11 letters (12+) → cap at 16pt
    
    Args:
        text: The description text to analyze
        base_size: The base font size (already scaled)
        scale_factor: Scale factor for minimum size calculations
        
    Returns:
        Adjusted font size (scaled)
    """
    words = str(text).split()
    if not words:
        return base_size
    
    final_size = base_size
    min_size = 8 * scale_factor
    
    # Check for word lengths
    has_10_letter_word = any(len(word) >= 10 for word in words)
    has_12_letter_word = any(len(word) >= 12 for word in words)
    has_word_longer_than_10 = any(len(word) > 10 for word in words)  # 11+ letters
    has_long_word = any(len(word) > 11 for word in words)  # 12+ letters
    
    # Rule 1: 10+ letter words → reduce by 1pt
    if has_10_letter_word:
        final_size = max(min_size, final_size - 1 * scale_factor)
        logger.debug(
            f"Double template description: text='{text}' has word(s) with 10+ letters, "
            f"reducing font size by 1pt -> {final_size}pt"
        )
    
    # Rule 2: 12+ letter words → reduce by 2pt (additional reduction)
    if has_12_letter_word:
        final_size = max(min_size, final_size - 2 * scale_factor)
        logger.debug(
            f"Double template description: text='{text}' has word(s) with 12+ letters, "
            f"reducing font size by 2pt -> {final_size}pt"
        )
    
    # Rule 3: >10 letter words (11+) → cap at 19pt
    if has_word_longer_than_10 and final_size > 19 * scale_factor:
        final_size = 19 * scale_factor
        logger.debug(
            f"Double template description: text='{text}' has word(s) with >10 letters, "
            f"capping font size at 19pt"
        )
    
    # Rule 4: >11 letter words (12+) → cap at 16pt (overrides 19pt cap)
    if has_long_word and final_size > 16 * scale_factor:
        final_size = 16 * scale_factor
        logger.debug(
            f"Double template description: text='{text}' has word(s) with >11 letters, "
            f"capping font size at 16pt"
        )
    
    return final_size


def _apply_vertical_template_description_rules(text: str, base_size: float, scale_factor: float) -> float:
    """
    Apply special rules for vertical template descriptions.
    
    Rules:
    - Words with >11 letters (12+) → cap at 22pt
    
    Args:
        text: The description text to analyze
        base_size: The base font size (already scaled)
        scale_factor: Scale factor for minimum size calculations
        
    Returns:
        Adjusted font size (scaled)
    """
    words = str(text).split()
    if not words:
        return base_size
    
    final_size = base_size
    
    # Check for words with >11 letters (12+)
    has_word_over_11 = any(len(word) > 11 for word in words)
    
    # Rule: >11 letter words (12+) → cap at 22pt
    if has_word_over_11 and final_size > 22 * scale_factor:
        final_size = 22 * scale_factor
        logger.debug(
            f"Vertical template description: text='{text}' has word(s) with >11 letters, "
            f"capping font size at 22pt"
        )
    
    return final_size


def _apply_field_specific_rules(
    text: str,
    field: str,
    orientation_norm: str,
    base_size: float,
    scale_factor: float
) -> float:
    """
    Apply all field-specific and template-specific rules to a base font size.
    
    This consolidates all post-calculation adjustments:
    - Double template description rules (10+/12+ letter words, 19pt/16pt caps)
    - Vertical template description rules (>11 letter words → 22pt cap)
    - Vertical template brand rules (11pt for multi-word with >9 letter words)
    
    Args:
        text: The text being sized
        field: Field type (description, brand, etc.)
        orientation_norm: Template orientation (double, vertical, etc.)
        base_size: Base font size (already scaled)
        scale_factor: Scale factor for calculations
        
    Returns:
        Adjusted font size (scaled)
    """
    final_size = base_size
    
    # Double template description rules
    if field == 'description' and orientation_norm == 'double':
        final_size = _apply_double_template_description_rules(text, final_size, scale_factor)
    
    # Vertical template description rules
    if field == 'description' and orientation_norm == 'vertical':
        final_size = _apply_vertical_template_description_rules(text, final_size, scale_factor)
    
    # Vertical template brand rules
    if field == 'brand' and orientation_norm == 'vertical':
        final_size = _apply_vertical_brand_rules(text, final_size, scale_factor)

    # Horizontal template description rule
    # If the description has more than 4 words and at least one word is 8+ letters,
    # reduce the computed font size by 1pt (but not below sensible minimum).
    if field == 'description' and orientation_norm == 'horizontal':
        words = [w for w in str(text).split() if w]
        if len(words) > 4 and any(len(w) >= 8 for w in words):
            min_size = 8 * scale_factor
            final_size = max(min_size, final_size - 1 * scale_factor)
            logger.debug(
                f"Horizontal description rule: text='{text}' has >4 words and a word>=8 letters, "
                f"reducing font size by 1pt -> {final_size}pt"
            )
    
    return final_size


def _get_field_fallback_size(field: str, scale_factor: float) -> float:
    """
    Get fallback font size for a field when complexity exceeds all thresholds.
    
    Rules:
    - Price: minimum 12pt
    - THC_CBD: minimum 6.5pt
    - Others: minimum 8pt
    """
    if field == 'price':
        return 12 * scale_factor  # Price should never go below 12pt
    elif field == 'thc_cbd':
        return 6.5 * scale_factor
    else:
        return 8 * scale_factor


def get_font_size(
    text: str,
    field_type: str = 'default',
    orientation: str = 'vertical',
    scale_factor: float = 1.0,
    complexity_type: str = 'standard',
) -> Pt:
    """
    Simplified unified font sizing.

    The rules are:
    - Use digit-count based rules for `price` on key templates (mini, double, vertical).
    - Use letter-count based complexity for `brand` on banner-style templates (mini, preroll, double).
    - For everything else, use `calculate_text_complexity` plus the configuration thresholds.
    - Fall back gracefully to reasonable minimum sizes when no config is found.
    """
    field = (field_type or 'default').lower()
    orientation_norm = (orientation or 'vertical').lower()
    
    # CRITICAL DEBUG: Log for horizontal template to trace font sizing issues
    if orientation_norm == 'horizontal':
        logger.info(f"🔍 UNIFIED FONT SIZE CALL: text='{text[:50]}...', field='{field}', orientation='{orientation_norm}', scale_factor={scale_factor}")

    # -----------------------------
    # 1. Special-case numeric prices
    # -----------------------------
    if field == 'price' and orientation_norm in ('mini', 'double', 'vertical'):
        return _get_price_font_size(text, orientation_norm, scale_factor)

    # -----------------------------------------
    # 2. Simple guardrails for long brand names
    # -----------------------------------------
    if field == 'brand':
        guardrail_size = _get_brand_guardrail_size(text, orientation_norm, scale_factor)
        if guardrail_size is not None:
            return guardrail_size

    # ------------------------
    # 3. Empty text fallbacks
    # ------------------------
    if not text:
        config = FONT_SIZING_CONFIG.get(complexity_type, {}).get(
            orientation_norm, {}
        ).get(field, [])
        if config:
            first_size = config[0][1]
            logger.debug(
                f"Empty text: using first configured size {first_size}pt "
                f"for field={field}, orientation={orientation_norm}"
            )
            return Pt(first_size * scale_factor)
        logger.debug(
            f"Empty text: no config found for field={field}, "
            f"orientation={orientation_norm}, using 12pt default"
        )
        return Pt(12 * scale_factor)

    # -------------------------
    # 4. Load configuration row
    # -------------------------
    config = FONT_SIZING_CONFIG.get(complexity_type, {}).get(
        orientation_norm, {}
    ).get(field, [])

    if not config:
        # Fallback to orientation default field config
        config = FONT_SIZING_CONFIG.get('standard', {}).get(
            orientation_norm, {}
        ).get('default', [])

    if not config:
        # Last resort fallback
        fallback_size = 11 * scale_factor
        logger.warning(
            f"No font configuration found for field={field}, "
            f"orientation={orientation_norm}, using {fallback_size}pt"
        )
        return Pt(fallback_size)

    # --------------------------
    # 5. Compute text complexity
    # --------------------------
    # Brand field: use letter count for banner-style templates (mini, preroll, double, horizontal)
    # so config thresholds are interpreted as letter counts
    if field == 'brand' and orientation_norm in ('mini', 'preroll', 'double', 'horizontal'):
        comp = _brand_letter_count(text)
        logger.info(
            f"Brand complexity (letter count): text='{text}', "
            f"letters={comp}, orientation={orientation_norm}, field={field}"
        )
    else:
        comp = calculate_text_complexity(text)
        logger.debug(
            f"Standard complexity: text='{text}', comp={comp}, "
            f"field={field}, orientation={orientation_norm}"
        )

    # ------------------------------------
    # 6. Pick size from thresholds by comp
    # ------------------------------------
    logger.debug(f"Config thresholds for field={field}, orientation={orientation_norm}: {config}")

    for threshold, size in config:
        logger.debug(f"Checking threshold {threshold} -> size {size} for complexity {comp}")
        if comp <= threshold:
            base_size = size * scale_factor
            final_size = _apply_field_specific_rules(text, field, orientation_norm, base_size, scale_factor)
            
            logger.debug(
                f"Selected size {size}pt (final={final_size}pt) "
                f"for text='{text}'"
            )
            return Pt(final_size)

    # --------------------------
    # 7. Smallest size fallback
    # --------------------------
    fallback_size = _get_field_fallback_size(field, scale_factor)
    fallback_size = _apply_field_specific_rules(text, field, orientation_norm, fallback_size, scale_factor)

    logger.debug(
        f"Complexity {comp} exceeded all thresholds for field={field}, "
        f"orientation={orientation_norm}; using fallback {fallback_size}pt"
    )
    return Pt(fallback_size)

def set_run_font_size(run, font_size):
    """Set font size for both the run and its XML element while preserving bold formatting."""
    if not isinstance(font_size, Pt):
        logger.warning(f"Font size was not Pt: {font_size} (type: {type(font_size)}), converting to Pt.")
        font_size = Pt(font_size)
    
    # Set font size at run level
    run.font.size = font_size
    
    # Ensure Arial Bold is always applied - NO EXCEPTIONS
    run.font.name = "Arial"
    run.font.bold = True
    
    # Set font size and bold at XML level for maximum compatibility
    sz_val = str(int(font_size.pt * 2))
    rPr = run._element.get_or_add_rPr()
    
    # Set font size
    sz = rPr.find(qn('w:sz'))
    if sz is None:
        sz = OxmlElement('w:sz')
        rPr.append(sz)
    sz.set(qn('w:val'), sz_val)
    
    # Also set szCs for complex scripts
    szCs = rPr.find(qn('w:szCs'))
    if szCs is None:
        szCs = OxmlElement('w:szCs')
        rPr.append(szCs)
    szCs.set(qn('w:val'), sz_val)
    
    # Force Arial font at XML level
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), 'Arial')
    rFonts.set(qn('w:hAnsi'), 'Arial')
    rFonts.set(qn('w:eastAsia'), 'Arial')
    rFonts.set(qn('w:cs'), 'Arial')
    
    # Force bold at XML level
    b = rPr.find(qn('w:b'))
    if b is None:
        b = OxmlElement('w:b')
        rPr.append(b)
    b.set(qn('w:val'), '1')
    
    logger.debug(f"Set font size to {font_size.pt}pt with Arial Bold for text: {run.text}")

# Legacy function aliases for backward compatibility
def get_thresholded_font_size(text, orientation='vertical', scale_factor=1.0, field_type='default'):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, field_type, orientation, scale_factor)

def get_thresholded_font_size_description(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'description', orientation, scale_factor)

def get_thresholded_font_size_brand(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'brand', orientation, scale_factor)

def get_thresholded_font_size_price(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'price', orientation, scale_factor)

def get_thresholded_font_size_lineage(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'lineage', orientation, scale_factor)

def get_thresholded_font_size_ratio(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'ratio', orientation, scale_factor)

def get_thresholded_font_size_thc_cbd(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'thc_cbd', orientation, scale_factor)

def get_thresholded_font_size_strain(text, orientation='vertical', scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'strain', orientation, scale_factor)



def get_font_size_by_marker(text, marker_type, template_type='vertical', scale_factor=1.0, product_type=None):
    """Get font size based on marker type."""
    # Handle START/END marker pairs by extracting the base marker name
    base_marker = marker_type.upper()
    if base_marker.endswith('_START') or base_marker.endswith('_END'):
        base_marker = base_marker.replace('_START', '').replace('_END', '')
    
    marker_to_field = {
        'DESC': 'description',
        'DESCRIPTION': 'description',
        'PRICE': 'price',
        'PRIC': 'price',
        'BRAND': 'brand',
        'PRODUCTBRAND': 'brand',
        'PRODUCTBRAND_CENTER': 'brand',  # PRODUCTBRAND_CENTER markers should use brand field type
        # Dynamic handling for LINEAGE based on template type: double behaves like brand center; others use lineage
        'LINEAGE': 'lineage',
        'LINEAGE_CENTER': 'lineage',
        'RATIO': 'ratio',
        'THC_CBD': 'thc_cbd',
        'WEIGHT': 'weight',
        'WEIGHTUNITS': 'weight',
        'UNITS': 'weight',
        'STRAIN': 'strain',
        'PRODUCTSTRAIN': 'strain',
        'DOH': 'doh',
        'VENDOR': 'vendor',
        'PRODUCTVENDOR': 'vendor',
        'QR': 'qr'  # QR code placeholders
    }
    # Determine base field type
    field_type = marker_to_field.get(base_marker, 'default')

    # Always treat LINEAGE markers as lineage content so they use the
    # lineage thresholds (this keeps that slot readable even when it
    # contains brand-like text).
    if base_marker in ('LINEAGE', 'LINEAGE_CENTER'):
        field_type = 'lineage'

    return get_font_size(text, field_type, template_type, scale_factor, 'standard')

def get_line_spacing_by_marker(marker_type, template_type='vertical'):
    """Get line spacing based on marker type and template type."""
    # Handle START/END marker pairs by extracting the base marker name
    base_marker = marker_type.upper()
    if base_marker.endswith('_START') or base_marker.endswith('_END'):
        base_marker = base_marker.replace('_START', '').replace('_END', '')
    
    spacing_config = {
        'RATIO': 2.4,
        'THC_CBD': 1.0,  # Use standard spacing for THC_CBD
        'DESC': 1.0,
        'DESCRIPTION': 1.0,
        'PRICE': 1.0,
        'BRAND': 1.0,
        'PRODUCTBRAND': 1.0,
        'PRODUCTBRAND_CENTER': 1.0,
        'LINEAGE': 1.0,
        'LINEAGE_CENTER': 1.0,
        'WEIGHT': 1.0,
        'WEIGHTUNITS': 1.0,
        'UNITS': 1.0,
        'STRAIN': 1.0,
        'PRODUCTSTRAIN': 1.0,
        'DOH': 1.0,
        'VENDOR': 1.0,
        'PRODUCTVENDOR': 1.0
    }
    
    # Template-specific spacing adjustments for better readability
    if base_marker == 'THC_CBD':
        return 1.0  # Use standard spacing for all templates
    
    return spacing_config.get(base_marker, 1.0)

def is_classic_type(product_type):
    """Check if product type is classic."""
    if not product_type:
        return False
    classic_types = ['classic', 'Classic', 'CLASSIC']
    return any(classic_type in str(product_type) for classic_type in classic_types)
