#!/usr/bin/env python3
"""
Unified font sizing system that consolidates all font sizing logic.
This module replaces the repetitive font sizing functions across the codebase.
"""

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
                    'description': [(5, 18), (20, 17), (30, 16), (35, 15), (40, 14), (50, 13), (60, 12), (80, 10), (120, 9), (float('inf'), 8)],
                    'brand': [(5, 9), (20, 8), (30, 7), (float('inf'), 6.5)],
                    'price': [(1, 18), (2, 16), (float('inf'), 14)],
                    'lineage': [(5, 12), (10, 11), (15, 10), (20, 9), (float('inf'), 8)],
                    'ratio': [(3, 12), (6, 11), (9, 10), (12, 9), (float('inf'), 8)],
                    'thc_cbd': [(5, 10), (10, 9), (15, 8), (20, 7), (float('inf'), 6)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(5, 14), (10, 12), (15, 10), (float('inf'), 8)],
                    'doh': [(5, 12), (10, 11), (float('inf'), 10)],
                    'vendor': [(5, 6), (10, 5), (15, 4), (20, 3), (float('inf'), 2)],
                    'qr': [(float('inf'), 24)],  # QR codes: Small size for mini template
                    'default': [(10, 12), (20, 11), (float('inf'), 10)]
                },
                'double': {
                    'description': [(10, 28), (20, 26), (30, 23), (40, 22), (50, 20), (60, 19), (70, 18), (80, 17), (90, 16), (100, 15), (110, 14), (120, 13), (130, 12), (float('inf'), 10)],
                    'brand': [(5, 12), (15, 10), (20, 8), (30, 7.5), (40, 7), (float('inf'), 6.5)],
                    'price': [(10, 26), (15, 20), (float('inf'), 14)],
                    'lineage': [(15, 13), (25, 12), (35, 10), (45, 9), (float('inf'), 9)],
                    'ratio': [(10, 9), (20, 8), (30, 7), (float('inf'), 6.5)],
                    'thc_cbd': [(20, 7),(float('inf'), 6.5)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 16), (25, 14), (35, 12), (float('inf'), 9)],
                    'doh': [(15, 20), (25, 16), (float('inf'), 13)],
                    'vendor': [(10, 8), (20, 7), (40, 6), (70, 5), (float('inf'), 4)],
                    'qr': [(float('inf'), 36)],  # QR codes: Medium size for double template
                    'default': [(20, 16), (40, 14), (60, 12), (float('inf'), 10)]
                },
                'vertical': {
                    'description': [(10, 36), (20, 34), (30, 30), (40, 28), (45, 26), (50, 24), (60, 23), (70, 22), (80, 20), (float('inf'), 18)],
                    'brand': [(10, 16), (15, 14), (25, 12), (35, 11), (float('inf'), 10)],
                    'price': [(2, 36), (3, 30), (float('inf'), 26)],  # $1/$11 = 36pt, $111+ = 30pt
                    'lineage': [(100, 18), (float('inf'), 14)],  # Max 18pt for lineage to prevent 20pt sizing
                    'ratio': [(10, 14), (20, 12), (30, 9), (float('inf'), 9)],
                    'thc_cbd': [(10, 12), (float('inf'), 12)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'vendor': [(10, 10), (20, 9), (40, 8), (70, 7), (float('inf'), 6)],
                    'qr': [(float('inf'), 45)],  # QR codes: Large size for vertical template
                    'default': [(30, 16), (60, 14), (100, 12), (float('inf'), 10)]
                },
                'horizontal': {
                    'description': [(10, 36), (20, 34), (25, 32), (30, 28), (35, 27), (40, 26), (45, 24), (50, 22), (70, 21), (100, 20), (120, 18), (float('inf'), 16)],
                    'brand': [(20, 18), (40, 16), (120, 14), (140, 12), (160, 10), (float('inf'), 10)],
                    'price': [(5, 40), (10, 38), (20, 36), (80, 20), (float('inf'), 18)],
                    'lineage': [(10, 20), (80, 18), (60, 10), (float('inf'), 10)],
                    'ratio': [(10, 14), (20, 12), (30, 10), (40, 9), (50, 8), (60, 7), (70, 6), (float('inf'), 5)],
                    'thc_cbd': [(10, 14), (float('inf'), 14)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'vendor': [(10, 10), (20, 9), (40, 8), (70, 7), (float('inf'), 6)],
                    'qr': [(float('inf'), 45)],  # QR codes: Large size for horizontal template  
                    'default': [(20, 18), (40, 16), (60, 14), (float('inf'), 12)]
                },
                'preroll': {
                    # Preroll template: Copy all settings from mini template (identical font sizing)
                    'description': [(5, 18), (20, 17), (30, 16), (35, 15), (40, 14), (50, 13), (60, 12), (80, 10), (120, 9), (float('inf'), 8)],
                    'brand': [(5, 9), (20, 8), (30, 6.5), (float('inf'), 6)],
                    'price': [(1, 22), (2, 20), (float('inf'), 18)],
                    'lineage': [(5, 12), (10, 11), (15, 10), (20, 9), (float('inf'), 8)],
                    'ratio': [(3, 12), (6, 11), (9, 10), (12, 9), (float('inf'), 8)],
                    'thc_cbd': [(5, 10), (10, 9), (15, 8), (20, 7), (float('inf'), 6)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(5, 14), (10, 12), (15, 10), (float('inf'), 8)],
                    'doh': [(5, 12), (10, 11), (float('inf'), 10)],
                    'vendor': [(5, 6), (10, 5), (15, 4), (20, 3), (float('inf'), 2)],
                    'qr': [(float('inf'), 30)],  # QR codes: Small size for preroll template (same as mini)
                    'default': [(10, 12), (20, 11), (float('inf'), 10)]
                }
            }
        }

FONT_SIZING_CONFIG = _load_font_sizing_config()

def _brand_letter_count(text) -> int:
    """Calculate brand complexity based on letter count."""
    if text is None:
        return 0
    text = str(text)
    
    # CRITICAL FIX: Extract brand name from markers before counting
    # Handle PRODUCTBRAND_CENTER_START...PRODUCTBRAND_CENTER_END markers
    import re
    brand_match = re.search(r'PRODUCTBRAND(?:_CENTER)?_START(.+?)PRODUCTBRAND(?:_CENTER)?_END', text, re.IGNORECASE)
    if brand_match:
        # Extract just the brand name from between the markers
        text = brand_match.group(1)
    
    letter_count = sum(1 for ch in text if ch.isalpha())
    if letter_count > 0:
        return letter_count
    # Fallback to non-space characters if no letters are present
    return len(text.replace(" ", ""))

def get_font_size(text: str, field_type: str = 'default', orientation: str = 'vertical', 
                 scale_factor: float = 1.0, complexity_type: str = 'standard') -> Pt:
    """
    Unified font sizing function that replaces all the repetitive font sizing functions.
    
    Args:
        text: The text to size
        field_type: Type of field ('description', 'brand', 'price', 'lineage', 'ratio', 'thc_cbd', 'strain', 'weight', 'doh', 'default')
        orientation: Template orientation ('mini', 'preroll', 'vertical', 'horizontal', 'double')
        scale_factor: Scaling factor for the font size
        complexity_type: Type of complexity calculation ('standard', 'description', 'mini')
    
    Returns:
        Font size as Pt object
    """
  
    
    # Special rule: Mini template prices based on number of digits
    if field_type.lower() == 'price' and orientation.lower() == 'mini':
        # Remove $ and any non-digit characters, then count digits
        clean_text = ''.join(char for char in str(text) if char.isdigit())
        num_digits = len(clean_text)
        
        if num_digits <= 2:  # Single or two digit prices (e.g., $12, $30)
            final_size = 20 * scale_factor
            logger.debug(f"Mini template price rule: '{text}' has {num_digits} digits, using 20pt font")
            return Pt(final_size)
        else:  # Three or more digits (e.g., $100, $1000+) - use 15pt font
            final_size = 15 * scale_factor
            logger.debug(f"Mini template price rule: '{text}' has {num_digits} digits, using 15pt font")
            return Pt(final_size)
    
    # Special rule: Mini template long brand names forced to minimum readable size
    if field_type.lower() == 'brand' and orientation.lower() == 'mini':
        text_length = _brand_letter_count(text)
        if text_length >= 20:
            final_size = 6.5 * scale_factor
            logger.debug(
                f"Mini template brand length rule: text='{text}' (length={text_length}) exceeds threshold, forcing {final_size}pt"
            )
            return Pt(final_size)
    
    # Special rule: Double template long brand names forced to 8pt minimum for readability
    if field_type.lower() == 'brand' and orientation.lower() == 'double':
        text_length = _brand_letter_count(text)
        if text_length >= 12:  # Lowered threshold to catch more long brands like "fairwinds manufacturing"
            final_size = 8 * scale_factor
            logger.debug(
                f"Double template brand length rule: text='{text}' (length={text_length}) exceeds threshold, forcing {final_size}pt"
            )
            return Pt(final_size)
    
    # Special rule: Double template prices based on number of digits
    if field_type.lower() == 'price' and orientation.lower() == 'double':
        # Remove $ and any non-digit characters, then count digits
        clean_text = ''.join(char for char in str(text) if char.isdigit())
        num_digits = len(clean_text)
        
        if num_digits <= 2:  # Two digit prices (e.g., $12, $30, $55)
            final_size = 28 * scale_factor
            logger.debug(f"Double template price rule: '{text}' has {num_digits} digits, using 26pt font")
            return Pt(final_size)
        elif num_digits == 3:  # Three digit prices (e.g., $100, $128, $250)
            final_size = 20 * scale_factor
            logger.debug(f"Double template price rule: '{text}' has {num_digits} digits, using 20pt font")
            return Pt(final_size)
        else:  # Four or more digits (e.g., $1000+)
            final_size = 16 * scale_factor
            logger.debug(f"Double template price rule: '{text}' has {num_digits} digits, using 16pt font")
            return Pt(final_size)
    
    # Special rule: Vertical template prices based on number of digits
    if field_type.lower() == 'price' and orientation.lower() == 'vertical':
        # Remove $ and any non-digit characters, then count digits
        clean_text = ''.join(char for char in str(text) if char.isdigit())
        num_digits = len(clean_text)
        
        if num_digits <= 2:  # $1 or $11 - use 36pt font
            final_size = 36 * scale_factor
            logger.debug(f"Vertical template price rule: '{text}' has {num_digits} digits, using 36pt font")
            return Pt(final_size)
        else:  # $111 or more - use 30pt font
            final_size = 30 * scale_factor
            logger.debug(f"Vertical template price rule: '{text}' has {num_digits} digits, using 30pt font")
            return Pt(final_size)
    
    if not text:
        # For empty text, use the appropriate field configuration instead of default
        config = FONT_SIZING_CONFIG.get('standard', {}).get(orientation.lower(), {}).get(field_type.lower(), [])
        if config:
            # Use the first size from the field's configuration
            first_size = config[0][1] if config else 12
            return Pt(first_size * scale_factor)
        return Pt(12 * scale_factor)
    
    # Special rule: If Description has any word longer than 9 characters in Vertical Template, reduce font size
    if field_type.lower() == 'description' and orientation.lower() == 'vertical':
        words = str(text).split()
        if words:
            max_word_length = max(len(word) for word in words)
            if max_word_length > 9:
                # Calculate appropriate font size based on the longest word
                if max_word_length <= 12:
                    font_size = 24
                elif max_word_length <= 15:
                    font_size = 20
                elif max_word_length <= 18:
                    font_size = 16
                else:
                    font_size = 11
                
                final_size = font_size * scale_factor
                logger.debug(f"Special vertical description rule: text='{text}', max_word_length={max_word_length}, using {font_size}pt font")
                return Pt(final_size)
    
    
    # Special guard: extremely long double-template brands still maintain 8pt minimum (removed 6.5pt cap)
    # Long brands (12+) are already forced to 8pt above, so this guard is no longer needed
    
    # Special rule: If double template description has multiple words with 9+ characters each, automatically reduce to 18pt
    if orientation.lower() == 'double' and field_type.lower() == 'description':
        words = str(text).split()
        long_words = [word for word in words if len(word) >= 9]
        if len(long_words) >= 2:  # Multiple words with 9+ characters each
            final_size = 18 * scale_factor
            logger.debug(f"Double template description word length rule: text='{text}' has {len(long_words)} words with 9+ chars each: {long_words}, forcing 18pt font")
            return Pt(final_size)
    
    # Get the appropriate configuration
    config = FONT_SIZING_CONFIG.get(complexity_type, {}).get(orientation.lower(), {}).get(field_type.lower(), [])
    
    if not config:
        # Fallback to default configuration
        config = FONT_SIZING_CONFIG.get('standard', {}).get(orientation.lower(), {}).get('default', [])
    
    if not config:
        # Ultimate fallback
        fallback_size = 11 * scale_factor
        logger.warning(f"No font configuration found for {field_type} in {orientation} template, using {fallback_size}pt")
        return Pt(fallback_size)
    
    # Calculate text complexity
    if field_type.lower() == 'brand' and orientation.lower() in ('mini', 'preroll', 'double'):
        comp = _brand_letter_count(text)
        logger.debug(f"Brand complexity override (letter count): text='{text}', letters={comp}, orientation={orientation}")
    else:
        comp = calculate_text_complexity(text)
    
    # Special debugging for price field
    if field_type.lower() == 'price':
        logger.info(f"PRICE DEBUG: '{text}' -> complexity: {comp}, orientation: {orientation}")
        logger.info(f"PRICE DEBUG: Config: {config}")
    
    # Special debugging for brand field with CONSTELLATION
    if field_type.lower() == 'brand' and 'CONSTELLATION' in text.upper():
        logger.info(f"🔍 CONSTELLATION FONT DEBUG: '{text}' -> complexity: {comp}, orientation: {orientation}")
        logger.info(f"🔍 CONSTELLATION FONT DEBUG: Config: {config}")
    
    logger.debug(f"Font sizing for '{text}' (field_type: {field_type}, orientation: {orientation}, complexity: {comp})")
    logger.debug(f"Config: {config}")
    
    # Find appropriate font size based on complexity
    for threshold, size in config:
        logger.debug(f"Checking threshold {threshold} -> size {size}")
        if field_type.lower() == 'price':
            logger.info(f"PRICE DEBUG: threshold {threshold} -> size {size}, comp {comp} <= threshold? {comp <= threshold}")
        if comp <= threshold:  # Fixed: Use <= instead of < for proper threshold matching
            final_size = size * scale_factor
            logger.debug(f"Selected size {size}pt (final: {final_size}pt)")
            if field_type.lower() == 'price':
                logger.info(f"PRICE DEBUG: SELECTED {size}pt for '{text}'")
            if field_type.lower() == 'brand' and 'CONSTELLATION' in text.upper():
                logger.info(f"🔍 CONSTELLATION FONT DEBUG: SELECTED {size}pt for '{text}' (complexity: {comp}, threshold: {threshold})")
            return Pt(final_size)
    
    # Fallback to smallest size - ensure price gets proper fallback
    if field_type.lower() == 'price':
        fallback_size = 12 * scale_factor  # Price should never go below 12pt
    elif field_type.lower() == 'thc_cbd':
        # Use the configured fallback size for THC_CBD instead of hardcoded 8pt
        fallback_size = 6.5 * scale_factor  # Use the configured size from the config
    else:
        fallback_size = 8 * scale_factor
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

    # Normalize context for downstream checks
    template_orientation = (template_type or '').lower()
    normalized_text = str(text or '')
    text_upper = normalized_text.upper()

    # Precompute non-classic context when product type provided
    is_nonclassic_context = False
    if product_type:
        try:
            from src.core.constants import CLASSIC_TYPES
            is_nonclassic_context = str(product_type).lower() not in CLASSIC_TYPES
        except Exception:
            # Fallback silently if CLASSIC_TYPES import fails for any reason
            is_nonclassic_context = False

    # CRITICAL FIX: Always use 'lineage' field type for LINEAGE markers by default,
    # but treat PRODUCTBRAND_CENTER content (double template brand center) as brand sizing.
    if base_marker in ('LINEAGE', 'LINEAGE_CENTER'):
        field_type = 'lineage'

        contains_brand_markers = (
            'PRODUCTBRAND_CENTER_START' in text_upper or
            'PRODUCTBRAND_CENTER_END' in text_upper
        )

        if contains_brand_markers:
            field_type = 'brand'
        elif template_orientation == 'double' and is_nonclassic_context:
            # Double template displays non-classic product brand content in the lineage field.
            field_type = 'brand'
    
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