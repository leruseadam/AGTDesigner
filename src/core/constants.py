from typing import Dict
import copy

# Lineage color mapping - SYNCHRONIZED WITH FRONTEND CSS
LINEAGE_COLOR_MAP: Dict[str, str] = {
    "SATIVA": "#ED4123",
    "INDICA": "#9900FF",
    "HYBRID": "#009900",
    "HYBRID/SATIVA": "#ED4123",
    "HYBRID/INDICA": "#9900FF",
    "CBD": "#F1C232",
    "MIXED": "#0021F5",
    "PARAPHERNALIA": "#FFC0CB",
}

# Product type mapping
TYPE_OVERRIDES: Dict[str, str] = {
    "all-in-one": "Disposable Vape",
    "aio": "Disposable Vape",
    "disposable": "Disposable Vape",
    "rosin": "Concentrate",
    "mini buds": "Flower",
    "bud": "Flower",
    "pre-roll": "Pre-Roll",  # Normalize to title case
    "Pre-Roll": "Pre-Roll",  # Keep title case
    "preroll": "Pre-Roll",  # Map variations to title case
    "Infused Pre-Roll": "Infused Pre-Roll",  # Keep title case
    "infused pre-roll": "Infused Pre-Roll",  # Map lowercase to title case
    "infused preroll": "Infused Pre-Roll",  # Map variations to title case
    "alcohol/ethanol extract": "RSO/CO2 Tankers",
    "Alcohol/Ethanol Extract": "RSO/CO2 Tankers",
    "alcohol ethanol extract": "RSO/CO2 Tankers",
    "Alcohol Ethanol Extract": "RSO/CO2 Tankers",
    "c02/ethanol extract": "RSO/CO2 Tankers",
    "CO2 Concentrate": "RSO/CO2 Tankers",
    "co2 concentrate": "RSO/CO2 Tankers",
}

# Text scaling constants
WORD_WEIGHT = 5
SCALE_FACTOR = 1.0

# Font schemes for different template types
FONT_SCHEME_HORIZONTAL = {
    'Description': {'min': 12, 'max': 34, 'weight': 1},
    'WeightUnits': {'min': 12, 'max': 34, 'weight': 1},
    'ProductBrand': {'min': 12, 'max': 30, 'weight': 1},
    'Price': {'min': 12, 'max': 28, 'weight': 1},
    'Lineage': {'min': 10, 'max': 24, 'weight': 1},
    'DOH': {'min': 8, 'max': 12, 'weight': 1},
    'THC_CBD': {'min': 10, 'max': 24, 'weight': 1},
    'Ratio': {'min': 10, 'max': 24, 'weight': 1}
}

FONT_SCHEME_VERTICAL = {
    'Description': {'min': 12, 'max': 30, 'weight': 1},
    'WeightUnits': {'min': 12, 'max': 30, 'weight': 1},
    'ProductBrand': {'min': 12, 'max': 28, 'weight': 1},
    'Price': {'min': 12, 'max': 26, 'weight': 1},
    'Lineage': {'min': 10, 'max': 22, 'weight': 1},
    'DOH': {'min': 8, 'max': 12, 'weight': 1},
    'THC_CBD': {'min': 10, 'max': 22, 'weight': 1},
    'Ratio': {'min': 10, 'max': 22, 'weight': 1}
}

FONT_SCHEME_MINI = {
    'Description': {'min': 8, 'max': 20, 'weight': 1},
    'WeightUnits': {'min': 8, 'max': 20, 'weight': 1},
    'ProductBrand': {'min': 8, 'max': 18, 'weight': 1},
    'Price': {'min': 8, 'max': 16, 'weight': 1},
    'Lineage': {'min': 8, 'max': 14, 'weight': 1},
    'DOH': {'min': 6, 'max': 10, 'weight': 1},
    'THC_CBD': {'min': 8, 'max': 14, 'weight': 1},
    'Ratio': {'min': 8, 'max': 14, 'weight': 1}
}

FONT_SCHEME_DOUBLE = {
    'Description': {'min': 10, 'max': 24, 'weight': 1},
    'WeightUnits': {'min': 10, 'max': 24, 'weight': 1},
    'ProductBrand': {'min': 10, 'max': 22, 'weight': 1},
    'Price': {'min': 10, 'max': 20, 'weight': 1},
    'Lineage': {'min': 8, 'max': 18, 'weight': 1},
    'DOH': {'min': 6, 'max': 12, 'weight': 1},
    'THC_CBD': {'min': 8, 'max': 18, 'weight': 1},
    'Ratio': {'min': 8, 'max': 18, 'weight': 1}
}

# Template cell dimensions (inches) - these are individual cell dimensions
CELL_DIMENSIONS: Dict[str, Dict[str, float]] = {
    'horizontal': {'width': 3.4, 'height': 2.4},  # Each cell is 3.4" wide, 2.4" tall
    'vertical': {'width': 2.4, 'height': 3.4},    # Each cell is 2.4" wide, 3.4" tall
    'mini': {'width': 1.5, 'height': 1.5},        # Each cell is 1.5" wide, 1.5" tall
    'single': {'width': 3.0, 'height': 2.0},      # Single label template
    'double': {'width': 1.75, 'height': 2.5},     # Each cell is 1.75" wide, 2.5" tall (with 0.10" horizontal and 0.05" vertical gutters)
    'inventory': {'width': 4.0, 'height': 2.0},   # Each cell is 4.0" wide, 2.0" tall
    'preroll': {'width': 1.5, 'height': 1.5}      # Each cell is 1.5" wide, 1.5" tall (same as mini)
}

# Template grid layouts
GRID_LAYOUTS: Dict[str, Dict[str, int]] = {
    'horizontal': {'rows': 3, 'cols': 3},
    'vertical': {'rows': 3, 'cols': 3},
    'mini': {'rows': 5, 'cols': 4},  # 4 columns across, 5 rows down
    'single': {'rows': 1, 'cols': 1},  # Single label template
    'double': {'rows': 3, 'cols': 4},  # 3 rows, 4 columns for 12 labels total
    'inventory': {'rows': 2, 'cols': 2},
    'preroll': {'rows': 5, 'cols': 4}  # 5 rows, 4 columns for 20 labels total (same as mini)
}

# Product type classifications
CLASSIC_TYPES = {
    # Flower types
    "flower", "bud",
    
    # Pre-roll types  
    "pre-roll", "infused pre-roll", "preroll", "blunt", "flavored blunt",
    
    # Concentrate types (all variations)
    "concentrate", "solventless concentrate",
    "live resin", "rosin", "cold cure rosin", "live rosin",
    "wax", "shatter", "hash", "kief",
    "butane extract", "distillate", "rso", "co2 extract",
    "honey crystal", "liquid diamond", "caviar",
    
    # Vape types
    "vape cartridge", "vape pen", "disposable",
    "rso/co2 tankers"
}

# Valid lineage values for classic types
VALID_CLASSIC_LINEAGES = {
    "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"
}

# Excluded product types and patterns
EXCLUDED_PRODUCT_TYPES = [
    "Samples - Educational",
    "Sample - Vendor",
    "X-DEACTIVATED 1",
    "X-DEACTIVATED 2",
    "Ounces"  # Not a valid product type - it's a weight unit
]

# Product name patterns to exclude
EXCLUDED_PRODUCT_PATTERNS = [
    "TRADE SAMPLE - Not For Sale",
    "Sample",
    "Trade Sample"
]

# Document constants
DOCUMENT_CONSTANTS = {
    'PAGE_MARGINS_INCHES': 0.5,
    'CELL_WIDTH_INCHES': 3.4,    # Individual cell width (for horizontal template)
    'CELL_HEIGHT_INCHES': 2.4,   # Individual cell height (for horizontal template)
    'MIN_FONT_SIZE': 8,
    'MAX_FONT_SIZE': 36,
    'DEFAULT_FONT': 'Arial',
    'DEFAULT_FONT_SIZE': 12,
    'DEFAULT_LINE_SPACING': 1.0,
    'DEFAULT_PARAGRAPH_SPACING': 0.0,
    'DEFAULT_TABLE_SPACING': 0.0,
    'DEFAULT_CELL_PADDING': 0.1,
    'DEFAULT_BORDER_WIDTH': 0.5,
    'DEFAULT_BORDER_COLOR': '000000',
    'DEFAULT_BACKGROUND_COLOR': 'FFFFFF',
    'DEFAULT_TEXT_COLOR': '000000'
}

# Product type to emoji mapping
PRODUCT_TYPE_EMOJIS = {
    "flower": "",
    "pre-roll": "",
    "infused pre-roll": "",
    "concentrate": "",
    "solventless concentrate": "",
    "vape cartridge": "",
    "edible (solid)": "",
    "edible (liquid)": "",
    "capsule": "",
    "tincture": "",
    "topical": "",
    "paraphernalia": "",
    "cbd": "",
    "cbd blend": "",
    "mixed": "",
    "rso/co2 tankers": "",
    # Add more as needed
}

# Allowed brands for preroll lists and output
# Only preroll products with these brands will be included in lists and QR code pages
# Set to None or empty list to allow all brands
PREROLL_ALLOWED_BRANDS = [
    # Add allowed brand names here (case-insensitive matching)
    # Example:
    # "DANK CZAR",
    # "COOKIES",
    # "PHAT PANDA",
]