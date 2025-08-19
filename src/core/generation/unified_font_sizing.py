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
                    'description': [(10, 16), (40, 14), (60, 12), (80, 10), (100, 9), (120, 8), (float('inf'), 7)],
                    'brand': [(10, 10), (20, 8), (30, 7.5), (40, 7), (float('inf'), 6)],
                    'price': [(30, 14), (40, 12), (50, 10), (float('inf'), 8)],
                    'lineage': [(10, 10), (20, 9), (30, 8), (40, 7), (float('inf'), 6)],
                    'ratio': [(5, 10), (8, 9), (12, 8), (20, 7), (float('inf'), 6)],
                    'thc_cbd': [(10, 8), (20, 7), (25, 6), (35, 5), (float('inf'), 4)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(10, 16), (20, 9), (30, 8), (float('inf'), 7)],
                    'doh': [(10, 10), (20, 9), (float('inf'), 8)],
                    'vendor': [(10, 4), (20, 3), (30, 2), (40, 1), (50, 1), (float('inf'), 1)],
                    'default': [(20, 10), (40, 9), (float('inf'), 8)]
                },
                'double': {
                    'description': [(10, 24), (20, 22), (60, 18), (80, 16), (100, 14), (120, 12), (140, 10), (float('inf'), 10)],
                    'brand': [(10, 14), (15, 12), (20, 10), (25, 8), (float('inf'), 7.5)],
                    'price': [(5, 20), (10, 18), (float('inf'), 14)],
                    'lineage': [(15, 13), (25, 12), (35, 10), (45, 9), (float('inf'), 9)],
                    'ratio': [(10, 9), (20, 7), (30, 5.5), (float('inf'), 5)],
                    'thc_cbd': [(1, 6.5),(float('inf'), 6.5)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(15, 16), (25, 14), (35, 12), (float('inf'), 9)],
                    'doh': [(15, 18), (25, 16), (float('inf'), 13)],
                    'vendor': [(10, 3), (20, 2), (40, 1), (70, 1),(float('inf'), 1)],
                    'default': [(20, 16), (40, 14), (60, 12), (float('inf'), 10)]
                },
                'vertical': {
                    'description': [(5, 34), (30, 32), (40, 28), (60, 26), (70, 24), (80, 22), (100, 20), (float('inf'), 14)],
                    'brand': [(10, 16), (20, 14), (30, 12), (float('inf'), 10)],
                    'price': [(5, 30), (8, 28), (float('inf'), 14)],
                    'lineage': [(20, 18), (40, 16), (60, 12), (float('inf'), 8)],
                    'ratio': [(10, 14), (20, 12), (30, 9), (float('inf'), 9)],
                    'thc_cbd': [(10, 12), (float('inf'), 12)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'vendor': [(10, 6), (20, 5), (40, 4), (70, 3),(float('inf'), 2)],
                    'default': [(30, 16), (60, 14), (100, 12), (float('inf'), 10)]
                },
                'horizontal': {
                    'description': [(10, 36), (15, 34), (20, 32), (40, 28), (50, 26), (55, 23), (70, 22), (80, 21), (90, 20), (float('inf'), 18)],
                    'brand': [(20, 18), (30, 16), (80, 14), (50, 12), (60, 10), (float('inf'), 10)],
                    'price': [(5, 36), (10, 34), (80, 20), (float('inf'), 18)],
                    'lineage': [(10, 20), (20, 18), (30, 16), (50, 12), (60, 10), (float('inf'), 10)],
                    'ratio': [(5, 14), (10, 12), (15, 10), (20, 9), (30, 8), (40, 7), (50, 6), (float('inf'), 5)],
                    'thc_cbd': [(10, 14), (float('inf'), 14)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'vendor': [(10, 6), (20, 5), (40, 4), (70, 3),(float('inf'), 2)],
                    'default': [(20, 18), (40, 16), (60, 14), (float('inf'), 12)]
                },
                'mini': {
                    'description': [(10, 16), (20, 14), (30, 12), (40, 10), (50, 9), (float('inf'), 8)],
                    'brand': [(10, 10), (20, 9), (30, 8), (40, 7), (float('inf'), 6)],
                    'price': [(5, 14), (10, 13), (15, 12), (20, 11), (float('inf'), 9)],
                    'lineage': [(10, 10), (20, 9), (30, 8), (40, 7), (float('inf'), 6)],
                    'ratio': [(5, 10), (10, 9), (15, 8), (20, 7), (float('inf'), 6)],
                    'thc_cbd': [(10, 10), (20, 9), (30, 8), (40, 7), (float('inf'), 6)],
                    'strain': [(10, 1), (20, 1), (30, 1), (float('inf'), 1)],
                    'weight': [(10, 12), (20, 10), (30, 8), (float('inf'), 6)],
                    'doh': [(10, 8), (20, 7), (float('inf'), 6)],
                    'vendor': [(10, 6), (20, 5), (40, 4), (float('inf'), 3)],
                    'default': [(20, 10), (40, 9), (60, 8), (float('inf'), 7)]
                }
            }
        }

FONT_SIZING_CONFIG = _load_font_sizing_config()

def get_font_size(text: str, field_type: str = 'default', orientation: str = 'vertical', 
                 scale_factor: float = 1.0, complexity_type: str = 'standard') -> Pt:
    """
    Unified font sizing function that replaces all the repetitive font sizing functions.
    
    Args:
        text: The text to size
        field_type: Type of field ('description', 'brand', 'price', 'lineage', 'ratio', 'thc_cbd', 'strain', 'weight', 'doh', 'default')
        orientation: Template orientation ('mini', 'vertical', 'horizontal')
        scale_factor: Scaling factor for the font size
        complexity_type: Type of complexity calculation ('standard', 'description', 'mini')
    
    Returns:
        Font size as Pt object
    """
    # BULLETPROOF FIX: Force correct configuration for vertical price
    if field_type.lower() == 'price' and orientation.lower() == 'vertical':
        # Use hardcoded correct configuration for vertical price - BYPASS ALL OTHER SYSTEMS
        comp = calculate_text_complexity(text)
        
        # Force the correct configuration regardless of any caching or other systems
        if comp < 5:
            final_size = 30 * scale_factor
            logger.debug(f"BULLETPROOF: Vertical price '{text}' (complexity: {comp}) using 30pt font")
            return Pt(final_size)
        elif comp < 8:
            final_size = 28 * scale_factor
            logger.debug(f"BULLETPROOF: Vertical price '{text}' (complexity: {comp}) using 28pt font")
            return Pt(final_size)
        else:
            final_size = 14 * scale_factor
            logger.debug(f"BULLETPROOF: Vertical price '{text}' (complexity: {comp}) using 14pt font")
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
                    font_size = 12
                
                final_size = font_size * scale_factor
                logger.debug(f"Special vertical description rule: text='{text}', max_word_length={max_word_length}, using {font_size}pt font")
                return Pt(final_size)
    
    # Special rule: If brand contains 20 or more letters in horizontal template, force font size to 14
    if field_type.lower() == 'brand' and orientation.lower() == 'horizontal':
        if len(text) >= 20:
            final_size = 14 * scale_factor
            logger.debug(f"Special brand rule: text='{text}' ({len(text)} chars) >= 20, forcing 14pt font")
            return Pt(final_size)
        # Special rule: If brand contains multiple words and is greater than 9 characters, set font to 14
        elif len(text.split()) > 1 and len(text) > 12:
            final_size = 14 * scale_factor
            logger.debug(f"Special brand rule: text='{text}' ({len(text)} chars, {len(text.split())} words) > 9 chars and multiple words, forcing 14pt font")
            return Pt(final_size)
        # Special rule: If brand is all caps and 9 or more characters, set font to 14
        elif text.isupper() and len(text) >= 12:
            final_size = 14 * scale_factor
            logger.debug(f"Special brand rule: text='{text}' ({len(text)} chars) is all caps >= 9 chars, forcing 14pt font")
            return Pt(final_size)
    
    # Special rule: If brand name has multiple words with 8+ characters each, reduce font to 8pt
    if field_type.lower() == 'brand' and orientation.lower() == 'double':
        words = text.split()
        long_words = [word for word in words if len(word) >= 8]
        if len(long_words) >= 2:  # Multiple words with 8+ characters each
            final_size = 8 * scale_factor
            logger.debug(f"Special double template brand rule: text='{text}' has {len(long_words)} words with 8+ chars each: {long_words}, forcing 8pt font")
            return Pt(final_size)
        else:
            logger.debug(f"Special double template brand rule: text='{text}' has {len(long_words)} words with 8+ chars each: {long_words}, NOT triggering 8pt font")
    
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
        fallback_size = 12 * scale_factor
        logger.warning(f"No font configuration found for {field_type} in {orientation} template, using {fallback_size}pt")
        return Pt(fallback_size)
    
    # Calculate text complexity
    comp = calculate_text_complexity(text)
    
    logger.debug(f"Font sizing for '{text}' (field_type: {field_type}, orientation: {orientation}, complexity: {comp})")
    logger.debug(f"Config: {config}")
    
    # Find appropriate font size based on complexity
    for threshold, size in config:
        logger.debug(f"Checking threshold {threshold} -> size {size}")
        if comp < threshold:
            final_size = size * scale_factor
            logger.debug(f"Selected size {size}pt (final: {final_size}pt)")
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
    """Set font size for both the run and its XML element."""
    if not isinstance(font_size, Pt):
        logger.warning(f"Font size was not Pt: {font_size} (type: {type(font_size)}), converting to Pt.")
        font_size = Pt(font_size)
    run.font.size = font_size
    sz_val = str(int(font_size.pt * 2))
    rPr = run._element.get_or_add_rPr()
    sz = rPr.find(qn('w:sz'))
    if sz is None:
        sz = OxmlElement('w:sz')
        rPr.append(sz)
    sz.set(qn('w:val'), sz_val)
    logger.debug(f"Set font size to {font_size.pt}pt for text: {run.text}")

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

# Mini-specific legacy functions
def get_mini_font_size_description(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'description', 'mini', scale_factor, 'mini')

def get_mini_font_size_brand(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'brand', 'mini', scale_factor, 'mini')

def get_mini_font_size_price(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'price', 'mini', scale_factor, 'mini')

def get_mini_font_size_lineage(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'lineage', 'mini', scale_factor, 'mini')

def get_mini_font_size_ratio(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'ratio', 'mini', scale_factor, 'mini')

def get_mini_font_size_thc_cbd(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'thc_cbd', 'mini', scale_factor, 'mini')

def get_mini_font_size_strain(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'strain', 'mini', scale_factor, 'mini')

def get_mini_font_size_weight(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'weight', 'mini', scale_factor, 'mini')

def get_mini_font_size_doh(text, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
    return get_font_size(text, 'doh', 'mini', scale_factor, 'mini')

def get_mini_font_size_by_marker(text, marker_type, scale_factor=1.0):
    """Legacy function - use get_font_size instead."""
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
        'PRODUCTBRAND_CENTER': 'brand',
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
        'PRODUCTVENDOR': 'vendor'
    }
    field_type = marker_to_field.get(base_marker, 'default')
    return get_font_size(text, field_type, 'mini', scale_factor, 'mini')

def set_mini_run_font_size(run, font_size):
    """Legacy function - use set_run_font_size instead."""
    return set_run_font_size(run, font_size)

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
        'PRODUCTBRAND_CENTER': 'brand',
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
        'PRODUCTVENDOR': 'vendor'
    }
    field_type = marker_to_field.get(base_marker, 'default')
    return get_font_size(text, field_type, template_type, scale_factor, 'standard')

def get_line_spacing_by_marker(marker_type, template_type='vertical'):
    """Get line spacing based on marker type and template type."""
    # Handle START/END marker pairs by extracting the base marker name
    base_marker = marker_type.upper()
    if base_marker.endswith('_START') or base_marker.endswith('_END'):
        base_marker = base_marker.replace('_START', '').replace('_END', '')
    
    spacing_config = {
        'RATIO': 2.4,
        'THC_CBD': 1.5,  # Base spacing for THC_CBD
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
        if template_type.lower() == 'double':
            return 1.5  # Double template now uses standard spacing like other templates
        elif template_type.lower() == 'vertical':
            return 1.5  # Vertical template uses standard spacing
        elif template_type.lower() == 'mini':
            return 1.3  # Mini template needs tighter spacing for small cells
        elif template_type.lower() == 'horizontal':
            return 1.35  # Horizontal template uses slightly tighter spacing
    
    return spacing_config.get(base_marker, 1.0)

def is_classic_type(product_type):
    """Check if product type is classic."""
    if not product_type:
        return False
    classic_types = ['classic', 'Classic', 'CLASSIC']
    return any(classic_type in str(product_type) for classic_type in classic_types) 