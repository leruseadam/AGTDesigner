#!/usr/bin/env python3
"""
Dynamic font sizing functions specifically optimized for Mini tags.
These functions are designed to work within the constraints of small label spaces
while maintaining readability and visual hierarchy.
"""

import logging
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
import re
from src.core.utils.common import calculate_text_complexity

logger = logging.getLogger(__name__)

# Performance optimization: disable debug logging in production
DEBUG_ENABLED = False

def _complexity(text):
    """Legacy complexity function - use calculate_text_complexity from common.py instead."""
    return calculate_text_complexity(text, 'mini')

def get_mini_font_size_description(text, scale_factor=1.0):
    """
    Optimized font sizing for description text in Mini tags.
    Prioritizes readability in small spaces.
    """
    comp = _complexity(text)
    
    # Mini-specific sizing for descriptions
    if comp < 15:
        size = 16
    elif comp < 25:
        size = 14
    elif comp < 35:
        size = 12
    elif comp < 45:
        size = 10
    elif comp < 55:
        size = 9
    else:
        size = 8
    
    return Pt(size * scale_factor)

def get_mini_font_size_price(text, scale_factor=1.0):
    """
    Optimized font sizing for price text in Mini tags.
    Prices should be prominent but fit in small spaces.
    """
    if not text:
        return Pt(10 * scale_factor)
    
    # Clean price text (remove currency symbols, spaces)
    clean_text = re.sub(r'[^\d.]', '', str(text))
    length = len(clean_text)
    
    # Mini-specific price sizing
    if length <= 3:  # $9
        size = 14
    elif length <= 4:  # $99
        size = 13
    elif length <= 5:  # $9.99
        size = 12
    elif length <= 6:  # $99.99
        size = 11
    elif length <= 7:  # $999.99
        size = 10
    else:  # Very long prices
        size = 9
    
    return Pt(size * scale_factor)

def get_mini_font_size_brand(text, scale_factor=1.0):
    """
    Optimized font sizing for brand names in Mini tags.
    Brand names should be readable but not dominate the label.
    """
    comp = _complexity(text)
    
    # Mini-specific brand sizing
    if comp < 8:
        size = 12
    elif comp < 15:
        size = 10
    elif comp < 25:
        size = 9
    elif comp < 35:
        size = 8
    else:
        size = 7
    
    return Pt(size * scale_factor)

def get_mini_font_size_lineage(text, scale_factor=1.0):
    """
    Optimized font sizing for lineage text in Mini tags.
    Lineage should be clear but compact.
    """
    comp = _complexity(text)
    
    # Mini-specific lineage sizing
    if comp < 10:
        size = 10
    elif comp < 20:
        size = 9
    elif comp < 30:
        size = 8
    elif comp < 40:
        size = 7
    else:
        size = 6
    
    return Pt(size * scale_factor)

def get_mini_font_size_ratio(text, scale_factor=1.0):
    """
    Optimized font sizing for ratio text in Mini tags with multiple tiers.
    Ratio information should be readable but not take up too much space.
    """
    comp = _complexity(text)
    length = len(text)
    
    # Multiple tiers based on content type and length
    # Tier 1: Very short ratio content (e.g., "1:1", "2:1")
    if length <= 5 and ':' in text and any(c.isdigit() for c in text):
        size = 10
    
    # Tier 2: Short ratio content (e.g., "1:1:1", "3:1:2")
    elif length <= 8 and ':' in text and any(c.isdigit() for c in text):
        size = 9
    
    # Tier 3: Medium ratio content (e.g., "1:1:1:1", "5:2:1:1")
    elif length <= 12 and ':' in text and any(c.isdigit() for c in text):
        size = 8
    
    # Tier 4: Long ratio content (e.g., "10:5:2:1:1", "15:10:5:2:1")
    elif length <= 20 and ':' in text and any(c.isdigit() for c in text):
        size = 7
    
    # Tier 5: Very long ratio content
    elif length > 20 and ':' in text and any(c.isdigit() for c in text):
        size = 6
    
    # Tier 6: Other ratio-like content (fallback)
    else:
        if comp < 15:
            size = 9
        elif comp < 25:
            size = 8
        elif comp < 35:
            size = 7
        else:
            size = 6
    
    return Pt(size * scale_factor)

def get_mini_font_size_thc_cbd(text, scale_factor=1.0):
    """
    Optimized font sizing for THC/CBD text in Mini tags with multiple tiers.
    THC/CBD information should be readable but compact.
    """
    comp = _complexity(text)
    length = len(text)
    
    # Multiple tiers based on content type and length
    # Tier 1: Basic THC/CBD format (e.g., "THC:|BR|CBD:")
    if 'THC:' in text and 'CBD:' in text and length <= 10:
        size = 10
    
    # Tier 2: THC/CBD with percentages (e.g., "THC: 25%\nCBD: 2%")
    elif 'THC:' in text and 'CBD:' in text and '%' in text and length <= 20:
        size = 9
    
    # Tier 3: THC/CBD with mg values (e.g., "THC: 100mg\nCBD: 10mg")
    elif 'THC:' in text and 'CBD:' in text and 'mg' in text.lower() and length <= 25:
        size = 8
    
    # Tier 4: Complex THC/CBD with multiple cannabinoids (e.g., "THC: 25%\nCBD: 2%\nCBC: 1%")
    elif 'THC:' in text and 'CBD:' in text and length <= 35:
        size = 7
    
    # Tier 5: Very complex THC/CBD content
    elif 'THC:' in text and 'CBD:' in text and length > 35:
        size = 6
    
    # Tier 6: mg-only content (e.g., "100mg THC", "500mg CBD")
    elif 'mg' in text.lower() and ('THC' in text or 'CBD' in text) and length <= 15:
        size = 9
    
    # Tier 7: Long mg content
    elif 'mg' in text.lower() and ('THC' in text or 'CBD' in text) and length > 15:
        size = 8
    
    # Tier 8: Other cannabinoid content (fallback)
    else:
        if comp < 15:
            size = 9
        elif comp < 25:
            size = 8
        elif comp < 35:
            size = 7
        else:
            size = 6
    
    return Pt(size * scale_factor)

def get_mini_font_size_weight(text, scale_factor=1.0):
    """
    Optimized font sizing for weight/units text in Mini tags.
    Weight information should be clear and readable.
    """
    comp = _complexity(text)
    
    # Mini-specific weight sizing
    if comp < 8:
        size = 10
    elif comp < 15:
        size = 9
    elif comp < 25:
        size = 8
    else:
        size = 7
    
    return Pt(size * scale_factor)

def get_mini_font_size_strain(text, scale_factor=1.0):
    """
    Optimized font sizing for strain names in Mini tags.
    Strain names should be invisible.
    """
    # Always return 1pt to make Product Strain nearly invisible
    return Pt(1 * scale_factor)

def get_mini_font_size_doh(text, scale_factor=1.0):
    """
    Optimized font sizing for DOH compliance text in Mini tags.
    DOH text should be small but legible.
    """
    # DOH text is typically short and standardized
    return Pt(6 * scale_factor)

def set_mini_run_font_size(run, font_size):
    """
    Set font size for Mini tag runs with proper XML handling.
    """
    if not isinstance(font_size, Pt):
        logger.warning(f"Font size was not Pt: {font_size}, converting to Pt.")
        font_size = Pt(font_size)
    
    run.font.size = font_size
    sz_val = str(int(font_size.pt * 2))
    rPr = run._element.get_or_add_rPr()
    sz = rPr.find(qn('w:sz'))
    if sz is None:
        sz = OxmlElement('w:sz')
        rPr.append(sz)
    sz.set(qn('w:val'), sz_val)
    
    if DEBUG_ENABLED:
        logger.debug(f"Set Mini font size to {font_size.pt}pt for text: {run.text[:20]}...")

def get_mini_font_size_by_marker(text, marker_type, scale_factor=1.0):
    """
    Unified function to get appropriate font size for Mini tags based on marker type.
    """
    if not text:
        return Pt(8 * scale_factor)
    
    marker_type = marker_type.upper()
    
    if marker_type in ['DESC', 'DESCRIPTION']:
        return get_mini_font_size_description(text, scale_factor)
    elif marker_type in ['PRICE', 'PRIC']:
        return get_mini_font_size_price(text, scale_factor)
    elif marker_type in ['BRAND', 'PRODUCTBRAND', 'PRODUCTBRAND_CENTER']:
        return get_mini_font_size_brand(text, scale_factor)
    elif marker_type in ['LINEAGE', 'LINEAGE_CENTER']:
        return get_mini_font_size_lineage(text, scale_factor)
    elif marker_type in ['RATIO']:
        from src.core.generation.unified_font_sizing import get_font_size
        # Remove line breaks so word count is based on the full placeholder
        full_text = text.replace('\n', ' ').replace('\r', ' ')
        return get_font_size(full_text, 'ratio', 'mini', scale_factor, 'mini')
    elif marker_type in ['THC_CBD']:
        return get_mini_font_size_thc_cbd(text, scale_factor)
    elif marker_type in ['WEIGHT', 'WEIGHTUNITS', 'UNITS']:
        return get_mini_font_size_weight(text, scale_factor)
    elif marker_type in ['STRAIN', 'PRODUCTSTRAIN']:
        return get_mini_font_size_strain(text, scale_factor)
    elif marker_type in ['DOH']:
        return get_mini_font_size_doh(text, scale_factor)
    else:
        # Default fallback for unknown markers
        comp = _complexity(text)
        if comp < 20:
            size = 10
        elif comp < 40:
            size = 9
        else:
            size = 8
        return Pt(size * scale_factor)

def apply_mini_font_sizing_to_paragraph(paragraph, marker_start, marker_end, marker_type, scale_factor=1.0):
    """
    Apply Mini-specific font sizing to a paragraph containing markers.
    """
    try:
        full_text = "".join(run.text for run in paragraph.runs)
        
        if marker_start in full_text and marker_end in full_text:
            # Extract content between markers
            start_idx = full_text.find(marker_start) + len(marker_start)
            end_idx = full_text.find(marker_end)
            content = full_text[start_idx:end_idx].strip()
            
            # Get appropriate font size for Mini tags
            font_size = get_mini_font_size_by_marker(content, marker_type, scale_factor)
            
            # Clear paragraph and re-add content with Mini-optimized formatting
            paragraph.clear()
            run = paragraph.add_run(content)
            run.font.name = "Arial"
            run.font.bold = True
            run.font.size = font_size
            
            # Apply Mini-specific font size setting
            set_mini_run_font_size(run, font_size)
            
            # Center alignment for brand names
            if 'BRAND' in marker_type:
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            if DEBUG_ENABLED:
                logger.debug(f"Applied Mini font sizing: {font_size.pt}pt for {marker_type} marker")
            
        elif marker_start in full_text or marker_end in full_text:
            if DEBUG_ENABLED:
                logger.debug(f"Found partial {marker_type} marker in text: '{full_text[:50]}...'")
            
    except Exception as e:
        logger.error(f"Error applying Mini font sizing for {marker_type}: {e}")
        # Fallback: remove markers and use default size
        for run in paragraph.runs:
            run.text = run.text.replace(marker_start, "").replace(marker_end, "")
            run.font.size = Pt(8 * scale_factor)

# Mini-specific font scheme constants
MINI_FONT_SCHEME = {
    "DESC": {"base_size": 12, "min_size": 8, "max_size": 16, "max_length": 60},
    "PRICE": {"base_size": 12, "min_size": 9, "max_size": 14, "max_length": 15},
    "LINEAGE": {"base_size": 9, "min_size": 6, "max_size": 10, "max_length": 25},
    "LINEAGE_CENTER": {"base_size": 9, "min_size": 6, "max_size": 10, "max_length": 25},
    "THC_CBD": {"base_size": 8, "min_size": 6, "max_size": 9, "max_length": 40},
    "RATIO": {"base_size": 8, "min_size": 6, "max_size": 9, "max_length": 25},
    "WEIGHT": {"base_size": 9, "min_size": 7, "max_size": 10, "max_length": 15},
    "UNITS": {"base_size": 9, "min_size": 7, "max_size": 10, "max_length": 15},
    "PRODUCTSTRAIN": {"base_size": 1, "min_size": 1, "max_size": 1, "max_length": 30},
    "PRODUCTBRAND_CENTER": {"base_size": 10, "min_size": 7, "max_size": 12, "max_length": 25},
    "DOH": {"base_size": 6, "min_size": 6, "max_size": 6, "max_length": 10}
}
