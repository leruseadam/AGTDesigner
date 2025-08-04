import os
import re
import logging
import traceback
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd
import datetime
from flask import send_file
from src.core.formatting.markers import wrap_with_marker, unwrap_marker
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from src.core.generation.text_processing import (
    format_cannabinoid_content,
    safe_get,
    safe_get_text,
    format_ratio_multiline,
    make_nonbreaking_hyphens,
)
from collections import OrderedDict
from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES, EXCLUDED_PRODUCT_TYPES, EXCLUDED_PRODUCT_PATTERNS, TYPE_OVERRIDES
from src.core.utils.common import calculate_text_complexity

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add at the top of the file (after imports)
VALID_LINEAGES = [
    "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD", "MIXED", "PARAPHERNALIA"
]

# Performance optimization flags
ENABLE_STRAIN_SIMILARITY_PROCESSING = True  # ALWAYS ENABLED: Lineage persistence is critical
ENABLE_FAST_LOADING = True
ENABLE_LAZY_PROCESSING = True  # NEW: Enable lazy processing for better performance
ENABLE_MINIMAL_PROCESSING = True  # NEW: Enable minimal processing mode for uploads
ENABLE_BATCH_OPERATIONS = True  # NEW: Enable batch operations instead of row-by-row
ENABLE_VECTORIZED_OPERATIONS = True  # NEW: Enable vectorized operations where possible
ENABLE_LINEAGE_PERSISTENCE = True  # ALWAYS ENABLED: Lineage changes must persist in database

# Performance constants
BATCH_SIZE = 1000  # Process data in batches
MAX_STRAINS_FOR_SIMILARITY = 50  # Limit strain similarity processing
CACHE_SIZE = 128  # Increase cache size for better performance
LINEAGE_BATCH_SIZE = 100  # Batch size for lineage database operations

# Optimized helper functions for performance
def vectorized_string_operations(series, operations):
    """Apply multiple string operations efficiently using vectorized operations."""
    if not ENABLE_VECTORIZED_OPERATIONS:
        return series
    
    result = series.astype(str)
    
    for op_type, params in operations:
        if op_type == 'strip':
            result = result.str.strip()
        elif op_type == 'lower':
            result = result.str.lower()
        elif op_type == 'upper':
            result = result.str.upper()
        elif op_type == 'replace':
            result = result.str.replace(params['old'], params['new'], regex=params.get('regex', False))
        elif op_type == 'fillna':
            result = result.fillna(params['value'])
    
    return result

def batch_process_dataframe(df, batch_size=BATCH_SIZE):
    """Process DataFrame in batches for better memory management."""
    if not ENABLE_BATCH_OPERATIONS:
        return df
    
    processed_chunks = []
    for i in range(0, len(df), batch_size):
        chunk = df.iloc[i:i + batch_size].copy()
        # Process chunk here if needed
        processed_chunks.append(chunk)
    
    return pd.concat(processed_chunks, ignore_index=True)

def optimized_column_processing(df, column_configs):
    """Apply optimized column processing configurations."""
    for col, config in column_configs.items():
        if col in df.columns:
            operations = config.get('operations', [])
            df[col] = vectorized_string_operations(df[col], operations)
    return df

def fast_ratio_extraction(product_names, product_types, classic_types):
    """Fast ratio extraction using vectorized operations."""
    if not ENABLE_VECTORIZED_OPERATIONS:
        return product_names
    
    # Vectorized ratio extraction logic
    ratios = pd.Series([''] * len(product_names))
    
    # Apply ratio extraction rules vectorized
    classic_mask = product_types.isin(classic_types)
    ratios[classic_mask] = 'THC:|BR|CBD:'
    
    return ratios

def optimized_lineage_assignment(df, product_types, lineages, classic_types):
    """Optimized lineage assignment using vectorized operations."""
    if not ENABLE_VECTORIZED_OPERATIONS:
        return lineages
    
    # Vectorized lineage assignment
    result = lineages.copy()
    
    # Apply lineage rules vectorized
    classic_mask = product_types.isin(classic_types)
    empty_lineage_mask = (lineages.isna()) | (lineages.astype(str).str.strip() == '')
    
    # Set default lineage for classic types with empty lineage
    default_mask = classic_mask & empty_lineage_mask
    result[default_mask] = 'HYBRID'
    
    return result

def handle_duplicate_columns(df):
    """Handle duplicate columns efficiently."""
    cols = df.columns.tolist()
    unique_cols = []
    seen_cols = set()
    
    for col in cols:
        if col not in seen_cols:
            unique_cols.append(col)
            seen_cols.add(col)
        else:
            # Keep the first occurrence, remove duplicates
            pass
        
    if len(unique_cols) != len(cols):
        df = df[unique_cols]
        
    return df
    
def optimized_lineage_persistence(processor, df):
    """Optimized lineage persistence that's always enabled and performs well."""
    if not ENABLE_LINEAGE_PERSISTENCE:
        return df
    
    try:
        from .product_database import ProductDatabase
        from src.core.constants import CLASSIC_TYPES
        product_db = ProductDatabase()
        
        # Process lineage persistence in batches for performance
        classic_mask = df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
        classic_df = df[classic_mask].copy()
        
        # Immediately fix any MIXED lineage for classic types in the current DataFrame
        mixed_lineage_mask = (df["Lineage"] == "MIXED") & classic_mask
        if mixed_lineage_mask.any():
            df.loc[mixed_lineage_mask, "Lineage"] = "HYBRID"
            processor.logger.info(f"Fixed {mixed_lineage_mask.sum()} classic products with MIXED lineage, changed to HYBRID")
        
        if classic_df.empty:
            return df
        
        # Get unique strains for batch processing
        unique_strains = classic_df["Product Strain"].dropna().unique()
        valid_strains = [s for s in unique_strains if normalize_strain_name(s)]
        
        if not valid_strains:
            return df
        
        # Use constant for valid lineages for classic types
        valid_classic_lineages = VALID_CLASSIC_LINEAGES
        
        # Process strains in batches
        strain_batches = [valid_strains[i:i + LINEAGE_BATCH_SIZE] 
                         for i in range(0, len(valid_strains), LINEAGE_BATCH_SIZE)]
        
        for batch in strain_batches:
            # Get lineage information from database for this batch
            strain_lineage_map = {}
            
            for strain_name in batch:
                strain_info = product_db.get_strain_info(strain_name)
                if strain_info and strain_info.get('display_lineage'):
                    db_lineage = strain_info['display_lineage']
                    # Only use database lineage if it's valid for classic types
                    # Explicitly reject MIXED lineage for classic types
                    if db_lineage and db_lineage.upper() in valid_classic_lineages and db_lineage.upper() != 'MIXED':
                        strain_lineage_map[strain_name] = db_lineage
                    else:
                        # Log invalid lineage for classic types
                        processor.logger.warning(f"Invalid lineage '{db_lineage}' for classic strain '{strain_name}', skipping database update")
            
            # Apply lineage updates vectorized
            if strain_lineage_map:
                for strain_name, db_lineage in strain_lineage_map.items():
                    strain_mask = (df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)) & \
                                (df["Product Strain"] == strain_name)
                    
                    # Only update if current lineage is empty or different
                    current_lineage_mask = (df.loc[strain_mask, "Lineage"].isna()) | \
                                         (df.loc[strain_mask, "Lineage"].astype(str).str.strip() == '') | \
                                         (df.loc[strain_mask, "Lineage"] != db_lineage)
                    
                    update_mask = strain_mask & current_lineage_mask
                    if update_mask.any():
                        df.loc[update_mask, "Lineage"] = db_lineage
                        
                        # Log the updates
                        updated_count = update_mask.sum()
                        if updated_count > 0:
                            processor.logger.debug(f"Updated {updated_count} products with strain '{strain_name}' to lineage '{db_lineage}' from database")
        
        return df
        
    except Exception as e:
        processor.logger.error(f"Error in optimized lineage persistence: {e}")
        return df

def batch_lineage_database_update(processor, df):
    """Batch update lineage information in the database."""
    if not ENABLE_LINEAGE_PERSISTENCE:
        return
    
    try:
        from .product_database import ProductDatabase
        from src.core.constants import CLASSIC_TYPES
        product_db = ProductDatabase()
        
        # Process in batches for performance
        classic_mask = df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
        classic_df = df[classic_mask]
        
        if classic_df.empty:
            return
        
        # Group by strain for efficient batch processing
        strain_groups = classic_df.groupby('Product Strain')
        
        for strain_name, group in strain_groups:
            if not strain_name or pd.isna(strain_name):
                continue
                
            # Get the most common lineage for this strain in this dataset
            lineage_counts = group['Lineage'].value_counts()
            if not lineage_counts.empty:
                most_common_lineage = lineage_counts.index[0]
                
                # Validate lineage for classic types - never save MIXED lineage
                from src.core.constants import VALID_CLASSIC_LINEAGES
                if most_common_lineage and str(most_common_lineage).strip():
                    lineage_to_save = most_common_lineage
                    
                    # For classic types, ensure we never save MIXED lineage
                    if most_common_lineage.upper() == 'MIXED':
                        lineage_to_save = 'HYBRID'
                        processor.logger.warning(f"Preventing MIXED lineage save for classic strain '{strain_name}', using HYBRID instead")
                    
                    # Only save if it's a valid lineage for classic types
                    if lineage_to_save.upper() in VALID_CLASSIC_LINEAGES:
                        product_db.add_or_update_strain(strain_name, lineage_to_save, sovereign=True)
                    else:
                        processor.logger.warning(f"Invalid lineage '{lineage_to_save}' for classic strain '{strain_name}', skipping database save")
        
    except Exception as e:
        processor.logger.error(f"Error in batch lineage database update: {e}")

def get_default_upload_file() -> Optional[str]:
    """
    Returns the path to the most recent "A Greener Today" Excel file.
    Searches multiple locations and returns the most recently modified file.
    Enhanced for PythonAnywhere compatibility.
    """
    import os
    from pathlib import Path
    
    # Check if we should disable default file loading for testing
    # Set this to True to disable default file loading for JSON matching testing
    DISABLE_DEFAULT_FOR_TESTING = False
    
    if DISABLE_DEFAULT_FOR_TESTING:
        logger.info("Default file loading temporarily disabled for JSON matching testing")
        return None
    
    # Get the current working directory (should be the project root)
    current_dir = os.getcwd()
    home_dir = os.path.expanduser('~')
    print(f"Current working directory: {current_dir}")
    print(f"Home directory: {home_dir}")
    
    # Enhanced PythonAnywhere detection
    is_pythonanywhere = (
        os.path.exists("/home/adamcordova") or
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or
        "pythonanywhere" in current_dir.lower()
    )
    
    print(f"Running on PythonAnywhere: {is_pythonanywhere}")
    
    # Define search locations
    search_locations = [
        os.path.join(current_dir, "uploads"),  # Local uploads directory
        os.path.join(home_dir, "Downloads"),  # Downloads folder (local only)
    ]
    
    # Add PythonAnywhere specific paths
    if is_pythonanywhere:
        pythonanywhere_paths = [
            "/home/adamcordova/uploads",  # PythonAnywhere uploads directory
            "/home/adamcordova/AGTDesigner/uploads",  # Project-specific uploads
            "/home/adamcordova/AGTDesigner/AGTDesigner/uploads",  # Nested project structure
            "/home/adamcordova/Downloads",  # PythonAnywhere Downloads
            "/home/adamcordova/AGTDesigner",  # Root project directory
            "/home/adamcordova/AGTDesigner/AGTDesigner",  # Nested project structure
        ]
        search_locations.extend(pythonanywhere_paths)
    
    # Find all "A Greener Today" files
    agt_files = []
    
    for location in search_locations:
        if os.path.exists(location):
            print(f"Searching in: {location}")
            try:
                for filename in os.listdir(location):
                    if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                        file_path = os.path.join(location, filename)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            file_size = os.path.getsize(file_path)
                            agt_files.append((file_path, filename, mod_time, file_size))
                            print(f"Found AGT file: {filename} (modified: {mod_time}, size: {file_size:,} bytes)")
            except Exception as e:
                print(f"Error searching {location}: {e}")
        else:
            print(f"Location does not exist: {location}")
    
    if not agt_files:
        logger.warning("No 'A Greener Today' files found in any search location")
        return None
    
    # Sort by modification time (most recent first)
    agt_files.sort(key=lambda x: x[2], reverse=True)
    
    # Return the most recent file
    most_recent_file_path, most_recent_filename, most_recent_mod_time, most_recent_file_size = agt_files[0]
    logger.info(f"Found most recent AGT file: {most_recent_filename} (modified: {most_recent_mod_time}, size: {most_recent_file_size:,} bytes)")
    return most_recent_file_path

def _complexity(text):
    """Legacy complexity function - use calculate_text_complexity from common.py instead."""
    return calculate_text_complexity(text, 'standard')


def normalize_name(name):
    """Normalize product names for robust matching."""
    if not isinstance(name, str):
        return ""
    # Lowercase, strip, replace multiple spaces/hyphens, remove non-breaking hyphens, etc.
    name = name.lower().strip()
    name = name.replace('\u2011', '-')  # non-breaking hyphen to normal
    name = re.sub(r'[-\s]+', ' ', name)  # collapse hyphens and spaces
    name = re.sub(r'[^\w\s-]', '', name)  # remove non-alphanumeric except hyphen/space
    return name


def is_real_ratio(text: str) -> bool:
    """Check if a string represents a valid ratio format."""
    if not text or not isinstance(text, str):
        return False
    
    # Clean the text
    text = text.strip()
    
    # Check for common invalid values
    if text in ["", "CBD", "THC", "CBD:", "THC:", "CBD:\n", "THC:\n"]:
        return False
    
    # Check for mg values (e.g., "100mg", "500mg THC", "10mg CBD")
    if 'mg' in text.lower():
        return True
    
    # Check for ratio format with numbers and separators
    if any(c.isdigit() for c in text) and any(sep in text for sep in [":", "/", "-"]):
        return True
    
    # Check for specific cannabinoid patterns
    cannabinoid_patterns = [
        r'\b(?:THC|CBD|CBC|CBG|CBN)\b',
        r'\d+mg',
        r'\d+:\d+',
        r'\d+:\d+:\d+'
    ]
    
    for pattern in cannabinoid_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def is_weight_with_unit(text: str) -> bool:
    """Check if a string represents a weight with unit format (e.g., '1g', '3.5g', '1oz')."""
    if not text or not isinstance(text, str):
        return False
    
    # Clean the text
    text = text.strip()
    
    # Check for weight + unit patterns
    weight_patterns = [
        r'^\d+(?:\.\d+)?\s*(?:g|gram|grams|gm|oz|ounce|ounces)$',  # 1g, 3.5g, 1oz, etc.
        r'^\d+(?:\.\d+)?\s*(?:g|gram|grams|gm|oz|ounce|ounces)\s*$',  # with trailing space
    ]
    
    for pattern in weight_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    
    return False


def normalize_strain_name(strain):
    """Normalize strain names for accurate matching."""
    if not isinstance(strain, str):
        return ""
    
    # Convert to string and clean
    strain = str(strain).strip()
    
    # Skip invalid strains
    if not strain or strain.lower() in ['mixed', 'unknown', 'n/a', 'none', '']:
        return ""
    
    # Normalize the strain name
    strain = strain.lower()
    
    # Remove common prefixes/suffixes that don't affect strain identity
    strain = re.sub(r'^(strain|variety|cultivar)\s+', '', strain)
    strain = re.sub(r'\s+(strain|variety|cultivar)$', '', strain)
    
    # Normalize common abbreviations and variations
    strain = re.sub(r'\bog\b', 'og kush', strain)  # "OG" -> "OG Kush"
    strain = re.sub(r'\bblue\s*dream\b', 'blue dream', strain)
    strain = re.sub(r'\bwhite\s*widow\b', 'white widow', strain)
    strain = re.sub(r'\bpurple\s*haze\b', 'purple haze', strain)
    strain = re.sub(r'\bjack\s*herer\b', 'jack herer', strain)
    strain = re.sub(r'\bnorthern\s*lights\b', 'northern lights', strain)
    strain = re.sub(r'\bsour\s*diesel\b', 'sour diesel', strain)
    strain = re.sub(r'\bafghan\s*kush\b', 'afghan kush', strain)
    strain = re.sub(r'\bcheese\b', 'uk cheese', strain)
    strain = re.sub(r'\bamnesia\s*haze\b', 'amnesia haze', strain)
    
    # Remove extra spaces and normalize punctuation
    strain = re.sub(r'\s+', ' ', strain)
    strain = re.sub(r'[^\w\s-]', '', strain)  # Keep only alphanumeric, spaces, and hyphens
    
    return strain.strip()


def get_strain_similarity(strain1, strain2):
    """Calculate similarity between two strain names. Optimized for performance."""
    if not strain1 or not strain2:
        return 0.0
    
    # Fast exact match check first
    if strain1 == strain2:
        return 1.0
    
    norm1 = normalize_strain_name(strain1)
    norm2 = normalize_strain_name(strain2)
    
    if not norm1 or not norm2:
        return 0.0
    
    # Exact match after normalization
    if norm1 == norm2:
        return 1.0
    
    # Fast substring check (most common case)
    if norm1 in norm2 or norm2 in norm1:
        return 0.9
    
    # Only do expensive similarity calculation for very similar strings
    if abs(len(norm1) - len(norm2)) <= 3:  # Only compare strings of similar length
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        return similarity if similarity > 0.8 else 0.0  # Only return high similarity
    
    return 0.0


def group_similar_strains(strains, similarity_threshold=0.8):
    """Group similar strain names together. Optimized for performance."""
    if not strains:
        return {}
    
    # Fast path: if similarity processing is disabled, return empty groups
    if not ENABLE_STRAIN_SIMILARITY_PROCESSING:
        return {}
    
    # Limit the number of strains to process to avoid O(n²) complexity
    max_strains = 100  # Only process first 100 strains to avoid performance issues
    if len(strains) > max_strains:
        strains = list(strains)[:max_strains]
    
    # Normalize all strains
    normalized_strains = {}
    for strain in strains:
        norm = normalize_strain_name(strain)
        if norm:
            normalized_strains[strain] = norm
    
    # Group similar strains (optimized algorithm)
    groups = {}
    processed = set()
    
    # Sort strains by length to process shorter ones first (better for substring matching)
    sorted_strains = sorted(normalized_strains.items(), key=lambda x: len(x[1]))
    
    for strain1, norm1 in sorted_strains:
        if strain1 in processed:
            continue
            
        # Start a new group
        group_key = strain1
        groups[group_key] = [strain1]
        processed.add(strain1)
        
        # Find similar strains (only check unprocessed strains)
        for strain2, norm2 in sorted_strains:
            if strain2 in processed:
                continue
                
            # Fast similarity check
            similarity = get_strain_similarity(strain1, strain2)
            if similarity >= similarity_threshold:
                groups[group_key].append(strain2)
                processed.add(strain2)
    
    return groups


class ExcelProcessor:
    """Processes Excel files containing product data."""

    def __init__(self):
        self.df = None
        self.dropdown_cache = {}
        self.selected_tags = []
        self.logger = logger
        self._last_loaded_file = None
        self._file_cache = {}
        self._max_cache_size = 5  # Keep only 5 files in cache
        self._product_db_enabled = True  # Enable product database integration by default
        self._debug_count = 0  # Initialize debug count

    def clear_file_cache(self):
        """Clear the file cache to free memory."""
        self._file_cache.clear()
        self.logger.debug("File cache cleared")

    def _manage_cache_size(self):
        """Keep cache size under control."""
        if len(self._file_cache) > self._max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(self._file_cache.keys())[:len(self._file_cache) - self._max_cache_size]
            for key in oldest_keys:
                del self._file_cache[key]
    
    def _schedule_product_db_integration(self):
        """Schedule product database integration in background to avoid blocking file load."""
        # Check if integration is enabled
        if not getattr(self, '_product_db_enabled', True):
            self.logger.debug("[ProductDB] Integration disabled, skipping background processing")
            return
            
        try:
            import threading
            import time
            
            def background_integration():
                """Background task for product database integration."""
                try:
                    # Add a small delay to ensure main file load completes first
                    time.sleep(0.1)
                    
                    from .product_database import ProductDatabase
                    product_db = ProductDatabase()
                    
                    # Process in batches for better performance
                    batch_size = 50
                    total_rows = len(self.df)
                    product_count = 0
                    strain_count = 0
                    
                    # Count classic types for logging
                    classic_types_count = sum(1 for _, row in self.df.iterrows() 
                                            if row.get('Product Type*', '').strip().lower() in [c.lower() for c in CLASSIC_TYPES])
                    self.logger.info(f"[ProductDB] Starting background integration for {total_rows} records ({classic_types_count} classic types for strain processing)...")
                    
                    for i in range(0, total_rows, batch_size):
                        batch_end = min(i + batch_size, total_rows)
                        batch_df = self.df.iloc[i:batch_end]
                        
                        # Process batch
                        for _, row in batch_df.iterrows():
                            row_dict = row.to_dict()
                            
                            # Only process classic types through the strain database
                            product_type = row_dict.get('Product Type*', '').strip().lower()
                            if product_type in [c.lower() for c in CLASSIC_TYPES]:
                                # Add or update strain (only if strain name exists)
                                strain_name = row_dict.get('Product Strain', '')
                                if strain_name and str(strain_name).strip():
                                    strain_id = product_db.add_or_update_strain(strain_name, row_dict.get('Lineage', ''))
                                    if strain_id:
                                        strain_count += 1
                                
                                # Add or update product
                                product_id = product_db.add_or_update_product(row_dict)
                                if product_id:
                                    product_count += 1
                            else:
                                # For non-classic types, only add/update the product (no strain processing)
                                product_id = product_db.add_or_update_product(row_dict)
                                if product_id:
                                    product_count += 1
                        
                        # Log progress for large files
                        if total_rows > 100:
                            progress = (batch_end / total_rows) * 100
                            self.logger.debug(f"[ProductDB] Progress: {progress:.1f}% ({batch_end}/{total_rows})")
                    
                    self.logger.info(f"[ProductDB] Background integration complete: {strain_count} strains processed, {product_count} products added/updated")
                    
                except Exception as e:
                    self.logger.error(f"[ProductDB] Background integration error: {e}")
            
            # Start background thread
            thread = threading.Thread(target=background_integration, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"[ProductDB] Failed to schedule background integration: {e}")
    
    def enable_product_db_integration(self, enable: bool = True):
        """Enable or disable product database integration."""
        self._product_db_enabled = enable
        self.logger.info(f"[ProductDB] Integration {'enabled' if enable else 'disabled'}")
    
    def get_product_db_stats(self):
        """Get product database statistics."""
        try:
            from .product_database import ProductDatabase
            product_db = ProductDatabase()
            return product_db.get_performance_stats()
        except Exception as e:
            self.logger.error(f"[ProductDB] Error getting stats: {e}")
            return {}

    def fast_load_file(self, file_path: str) -> bool:
        """ULTRA-FAST file loading with minimal processing for maximum upload speed."""
        try:
            self.logger.debug(f"[ULTRA-FAST] Loading file: {file_path}")
            
            # Minimal validation for speed
            import os
            if not os.path.exists(file_path):
                self.logger.error(f"[ULTRA-FAST] File not found: {file_path}")
                return False
            
            # Clear previous data efficiently
            if hasattr(self, 'df') and self.df is not None:
                del self.df
            
            # Use optimized Excel reading with minimal processing
            excel_engines = ['openpyxl']
            df = None
            
            for engine in excel_engines:
                try:
                    self.logger.debug(f"Attempting to read with engine: {engine}")
                    
                    # Use optimized reading settings - minimal dtype specification for speed
                    dtype_dict = {
                        "Product Name*": "string",
                        "Product Type*": "string",
                        "Lineage": "string"
                    }
                    
                    # Read with minimal processing - no NA filtering for speed
                    df = pd.read_excel(
                        file_path, 
                        engine=engine,
                        dtype=dtype_dict,
                        na_filter=False,  # Don't filter NA values for speed
                        keep_default_na=False  # Don't use default NA values
                    )
                    
                    self.logger.info(f"Successfully read file with {engine} engine: {len(df)} rows, {len(df.columns)} columns")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"Failed to read with {engine} engine: {e}")
                    if engine == excel_engines[-1]:  # Last engine
                        self.logger.error(f"All Excel engines failed to read file: {file_path}")
                        return False
                    continue
            
            if df is None or df.empty:
                self.logger.error("No data found in Excel file")
                return False
            
            # Handle duplicate columns efficiently
            df = handle_duplicate_columns(df)
            
            # Remove duplicates efficiently - use product name as primary key for deduplication
            initial_count = len(df)
            
            # First, ensure we have a product name column
            product_name_col = None
            for col in ['Product Name*', 'ProductName', 'Product Name', 'Description']:
                if col in df.columns:
                    product_name_col = col
                    break
            
            if product_name_col:
                # Use product name as primary key for deduplication to prevent UI duplicates
                df.drop_duplicates(subset=[product_name_col], inplace=True)
                self.logger.info(f"Removed duplicates based on product name column: {product_name_col}")
            else:
                # Fallback to general deduplication if no product name column found
                df.drop_duplicates(inplace=True)
                self.logger.info("No product name column found, using general deduplication")
            
            df.reset_index(drop=True, inplace=True)
            final_count = len(df)
            if initial_count != final_count:
                self.logger.info(f"Removed {initial_count - final_count} duplicate rows")

            # Log all available columns for debugging
            self.logger.info(f"All columns in uploaded file: {df.columns.tolist()}")
            
            # Keep all columns but ensure required ones exist
            required_columns = [
                'Product Name*', 'ProductName', 'Description',
                'Product Type*', 'Lineage', 'Product Brand', 'Vendor/Supplier*',
                'Weight*', 'Weight Unit* (grams/gm or ounces/oz)', 'Units',
                'Price* (Tier Name for Bulk)', 'Price',
                'DOH Compliant (Yes/No)', 'DOH',
                'Concentrate Type', 'Ratio',
                'Joint Ratio', 'JointRatio',
                'Product Strain',
                'Quantity*', 'Quantity Received*', 'Quantity', 'qty'
            ]
            
            # Check which required columns are missing
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.warning(f"Missing required columns: {missing_columns}")
            
            # Apply minimal processing only if ENABLE_MINIMAL_PROCESSING is True
            if ENABLE_MINIMAL_PROCESSING:
                # Only do essential processing for uploads
                self.logger.debug("Applying minimal processing for fast upload")
                
                # 1. Basic column normalization (vectorized for speed)
                if "Product Name*" in df.columns:
                    df["Product Name*"] = df["Product Name*"].str.lstrip()
                
                # 2. Ensure required columns exist
                for col in ["Product Type*", "Lineage", "Product Brand"]:
                    if col not in df.columns:
                        df[col] = "Unknown"
                
                # 3. Basic filtering (exclude sample rows) - vectorized for speed
                initial_count = len(df)
                df = df[~df["Product Type*"].isin(EXCLUDED_PRODUCT_TYPES)]
                df.reset_index(drop=True, inplace=True)
                final_count = len(df)
                if initial_count != final_count:
                    self.logger.info(f"Excluded {initial_count - final_count} products by type")
                
                # 4. Basic column renaming
                rename_mapping = {}
                if "Product Name*" in df.columns and "ProductName" not in df.columns:
                    rename_mapping["Product Name*"] = "ProductName"
                if "Weight Unit* (grams/gm or ounces/oz)" in df.columns and "Units" not in df.columns:
                    rename_mapping["Weight Unit* (grams/gm or ounces/oz)"] = "Units"
                if "Price* (Tier Name for Bulk)" in df.columns and "Price" not in df.columns:
                    rename_mapping["Price* (Tier Name for Bulk)"] = "Price"
                if "Vendor/Supplier*" in df.columns and "Vendor" not in df.columns:
                    rename_mapping["Vendor/Supplier*"] = "Vendor"
                if "DOH Compliant (Yes/No)" in df.columns and "DOH" not in df.columns:
                    rename_mapping["DOH Compliant (Yes/No)"] = "DOH"
                if "Concentrate Type" in df.columns and "Ratio" not in df.columns:
                    rename_mapping["Concentrate Type"] = "Ratio"
                
                if rename_mapping:
                    df.rename(columns=rename_mapping, inplace=True)
                
                # 5. Basic lineage standardization (vectorized)
                if "Lineage" in df.columns:
                    from src.core.constants import CLASSIC_TYPES
                    df["Lineage"] = optimized_lineage_assignment(
                        df, 
                        df["Product Type*"], 
                        df["Lineage"], 
                        CLASSIC_TYPES
                    )
                
                # 6. Basic product strain handling
                if "Product Strain" not in df.columns:
                    df["Product Strain"] = ""
                df["Product Strain"] = df["Product Strain"].fillna("Mixed")
                
                # 7. Convert key fields to categorical for memory efficiency
                for col in ["Product Type*", "Lineage", "Product Brand", "Vendor", "Product Strain"]:
                    if col in df.columns:
                        df[col] = df[col].fillna("Unknown")
                        df[col] = df[col].astype("category")
                
                self.logger.debug("Minimal processing complete")
            else:
                self.logger.debug("Skipping minimal processing - using raw data")

            self.df = df
            self.logger.debug(f"Original columns: {self.df.columns.tolist()}")
            
            self._last_loaded_file = file_path
            self.logger.info(f"Ultra-fast load successful: {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
                
        except Exception as e:
            self.logger.error(f"Error in ultra-fast_load_file: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Try to provide more specific error information
            if "No module named" in str(e):
                self.logger.error("Missing required module - this might be a dependency issue")
            elif "Permission denied" in str(e):
                self.logger.error("File permission issue - check file permissions")
            elif "Memory" in str(e):
                self.logger.error("Memory issue - file might be too large")
            return False

    def load_file(self, file_path: str) -> bool:
        """Load Excel file and prepare data exactly like MAIN.py. Enhanced for PythonAnywhere compatibility."""
        try:
            # Check if we've already loaded this exact file
            if (self._last_loaded_file == file_path and 
                self.df is not None and 
                not self.df.empty):
                self.logger.debug(f"File {file_path} already loaded, skipping reload")
                return True
            
            self.logger.debug(f"Loading file: {file_path}")
            
            # Validate file exists and is accessible
            import os
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"File not readable: {file_path}")
                return False
            
            # Check file size (PythonAnywhere has memory limits)
            file_size = os.path.getsize(file_path)
            max_size = 50 * 1024 * 1024  # 50MB limit for PythonAnywhere
            if file_size > max_size:
                self.logger.error(f"File too large for PythonAnywhere: {file_size} bytes (max: {max_size})")
                return False
            
            self.logger.info(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            # Check file modification time for cache invalidation
            file_mtime = os.path.getmtime(file_path)
            cache_key = f"{file_path}_{file_mtime}"
            
            if cache_key in self._file_cache:
                self.logger.debug(f"Using cached data for {file_path}")
                self.df = self._file_cache[cache_key].copy()
                self._last_loaded_file = file_path
                return True
            
            # Clear previous data to free memory
            if hasattr(self, 'df') and self.df is not None:
                del self.df
                import gc
                gc.collect()
            
            # 1) Read & dedupe, force-key columns to string for .str ops
            # Use more conservative settings for PythonAnywhere
            dtype_dict = {
                "Product Type*": "string",
                "Lineage": "string",
                "Product Brand": "string",
                "Vendor": "string",
                "Weight Unit* (grams/gm or ounces/oz)": "string",
                "Product Name*": "string"
            }
            
            # Try different Excel engines for better compatibility
            excel_engines = ['openpyxl', 'xlrd']
            df = None
            
            for engine in excel_engines:
                try:
                    self.logger.debug(f"Attempting to read with engine: {engine}")
                    
                    # Use chunking for large files on PythonAnywhere
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.logger.info("Large file detected, using chunked reading")
                        # Read in chunks to manage memory
                        chunk_size = 1000
                        chunks = []
                        
                        for chunk in pd.read_excel(file_path, engine=engine, dtype=dtype_dict, chunksize=chunk_size):
                            chunks.append(chunk)
                            self.logger.debug(f"Read chunk {len(chunks)} with {len(chunk)} rows")
                        
                        if chunks:
                            df = pd.concat(chunks, ignore_index=True)
                            self.logger.info(f"Successfully read {len(df)} rows in {len(chunks)} chunks")
                        else:
                            self.logger.error("No data found in file")
                            return False
                    else:
                        # For smaller files, read normally
                        df = pd.read_excel(file_path, engine=engine, dtype=dtype_dict)
                    
                    self.logger.info(f"Successfully read file with {engine} engine: {len(df)} rows, {len(df.columns)} columns")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"Failed to read with {engine} engine: {e}")
                    if engine == excel_engines[-1]:  # Last engine
                        self.logger.error(f"All Excel engines failed to read file: {file_path}")
                        return False
                    continue
            
            if df is None or df.empty:
                self.logger.error("No data found in Excel file")
                return False
            
            # Handle duplicate columns before processing
            df = handle_duplicate_columns(df)
            
            # Remove duplicates and reset index to avoid duplicate labels
            initial_count = len(df)
            df.drop_duplicates(inplace=True)
            df.reset_index(drop=True, inplace=True)  # Reset index to avoid duplicate labels
            final_count = len(df)
            if initial_count != final_count:
                self.logger.info(f"Removed {initial_count - final_count} duplicate rows")

            # Log all available columns for debugging
            self.logger.info(f"All columns in uploaded file: {df.columns.tolist()}")
            
            # Keep all columns but ensure required ones exist
            required_columns = [
                'Product Name*', 'ProductName', 'Description',
                'Product Type*', 'Lineage', 'Product Brand', 'Vendor/Supplier*',
                'Weight*', 'Weight Unit* (grams/gm or ounces/oz)', 'Units',
                'Price* (Tier Name for Bulk)', 'Price',
                'DOH Compliant (Yes/No)', 'DOH',
                'Concentrate Type', 'Ratio',
                'Joint Ratio', 'JointRatio',
                'Product Strain',
                'Quantity*', 'Quantity Received*', 'Quantity', 'qty'
            ]
            
            # Check which required columns are missing
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.warning(f"Missing required columns: {missing_columns}")
            
            # Keep all columns - don't filter them out
            # df = df[existing_required]  # REMOVED - this was causing column loss

            self.df = df
            # Handle duplicate columns before any operations
            self.df = handle_duplicate_columns(self.df)
            # Reset index immediately after assignment to prevent duplicate labels
            self.df.reset_index(drop=True, inplace=True)
            self.logger.debug(f"Original columns: {self.df.columns.tolist()}")
            
            # 2) Trim product names
            if "Product Name*" in self.df.columns:
                self.df["Product Name*"] = self.df["Product Name*"].str.lstrip()
            elif "Product Name" in self.df.columns:
                self.df["Product Name*"] = self.df["Product Name"].str.lstrip()
            elif "ProductName" in self.df.columns:
                self.df["Product Name*"] = self.df["ProductName"].str.lstrip()
            else:
                self.logger.error("No product name column found")
                self.df["Product Name*"] = "Unknown"

            # 3) Ensure required columns exist
            for col in ["Product Type*", "Lineage", "Product Brand"]:
                if col not in self.df.columns:
                    self.df[col] = "Unknown"

            # 3.5) Determine product name column early (needed for lineage processing)
            product_name_col = 'Product Name*'
            if product_name_col not in self.df.columns:
                product_name_col = 'ProductName' if 'ProductName' in self.df.columns else None

            # 4) Exclude sample rows and deactivated products
            initial_count = len(self.df)
            excluded_by_type = self.df[self.df["Product Type*"].isin(EXCLUDED_PRODUCT_TYPES)]
            self.df = self.df[~self.df["Product Type*"].isin(EXCLUDED_PRODUCT_TYPES)]
            # Reset index after filtering to prevent duplicate labels
            self.df.reset_index(drop=True, inplace=True)
            self.logger.info(f"Excluded {len(excluded_by_type)} products by product type: {excluded_by_type['Product Type*'].unique().tolist()}")
            
            # Also exclude products with excluded patterns in the name
            for pattern in EXCLUDED_PRODUCT_PATTERNS:
                pattern_mask = self.df["Product Name*"].str.contains(pattern, case=False, na=False)
                excluded_by_pattern = self.df[pattern_mask]
                self.df = self.df[~pattern_mask]
                if len(excluded_by_pattern) > 0:
                    self.logger.info(f"Excluded {len(excluded_by_pattern)} products containing pattern '{pattern}': {excluded_by_pattern['Product Name*'].tolist()}")
            
            # Reset index after all filtering to prevent duplicate labels
            self.df.reset_index(drop=True, inplace=True)
            final_count = len(self.df)
            self.logger.info(f"Product filtering complete: {initial_count} -> {final_count} products (excluded {initial_count - final_count})")

            # 5) Rename for convenience (only if target columns don't already exist)
            rename_mapping = {}
            if "Product Name*" in self.df.columns and "ProductName" not in self.df.columns:
                rename_mapping["Product Name*"] = "ProductName"
            if "Weight Unit* (grams/gm or ounces/oz)" in self.df.columns and "Units" not in self.df.columns:
                rename_mapping["Weight Unit* (grams/gm or ounces/oz)"] = "Units"
            if "Price* (Tier Name for Bulk)" in self.df.columns and "Price" not in self.df.columns:
                rename_mapping["Price* (Tier Name for Bulk)"] = "Price"
            if "Vendor/Supplier*" in self.df.columns and "Vendor" not in self.df.columns:
                rename_mapping["Vendor/Supplier*"] = "Vendor"
            if "DOH Compliant (Yes/No)" in self.df.columns and "DOH" not in self.df.columns:
                rename_mapping["DOH Compliant (Yes/No)"] = "DOH"
            if "Concentrate Type" in self.df.columns and "Ratio" not in self.df.columns:
                rename_mapping["Concentrate Type"] = "Ratio"
            
            if rename_mapping:
                self.df.rename(columns=rename_mapping, inplace=True)

            # Handle duplicate columns after renaming
            self.df = handle_duplicate_columns(self.df)

            # 5.5) Normalize product types using TYPE_OVERRIDES
            if "Product Type*" in self.df.columns:
                self.logger.info("Applying product type normalization...")
                # First trim whitespace from product types
                self.df["Product Type*"] = self.df["Product Type*"].str.strip()
                # Apply TYPE_OVERRIDES to normalize product types
                self.df["Product Type*"] = self.df["Product Type*"].replace(TYPE_OVERRIDES)
                self.logger.info(f"Product type normalization complete. Sample types: {self.df['Product Type*'].unique()[:10].tolist()}")

            # Update product_name_col after renaming
            if product_name_col == 'Product Name*':
                product_name_col = 'ProductName'

            # 6) Normalize units
            if "Units" in self.df.columns:
                self.df["Units"] = self.df["Units"].str.lower().replace(
                    {"ounces": "oz", "grams": "g"}, regex=True
                )

            # 7) Standardize Lineage
            # Reset index before lineage processing to prevent duplicate labels
            self.df.reset_index(drop=True, inplace=True)
            if "Lineage" in self.df.columns:
                self.logger.info("Starting lineage standardization process...")
                # First, standardize existing values
                self.df["Lineage"] = (
                    self.df["Lineage"]
                    .str.lower()
                    .replace({
                        "indica_hybrid": "HYBRID/INDICA",
                        "sativa_hybrid": "HYBRID/SATIVA",
                        "sativa": "SATIVA",
                        "hybrid": "HYBRID",
                        "indica": "INDICA",
                        "cbd": "CBD"
                    })
                    .str.upper()
                )
                
                # Fix invalid lineage assignments for classic types
                # Classic types should never have "MIXED" lineage
                from src.core.constants import CLASSIC_TYPES
                
                classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
                mixed_lineage_mask = self.df["Lineage"] == "MIXED"
                classic_with_mixed_mask = classic_mask & mixed_lineage_mask
                
                if classic_with_mixed_mask.any():
                    self.df.loc[classic_with_mixed_mask, "Lineage"] = "HYBRID"
                    self.logger.info(f"Fixed {classic_with_mixed_mask.sum()} classic products with invalid MIXED lineage, changed to HYBRID")
                
                # For classic types, set empty lineage to HYBRID
                # For non-classic types, set empty lineage to MIXED or CBD based on content
                
                # Create mask for classic types
                classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
                
                # Set empty lineage values based on product type
                empty_lineage_mask = self.df["Lineage"].isnull() | (self.df["Lineage"].astype(str).str.strip() == "")
                
                # For classic types, set to HYBRID (never MIXED)
                classic_empty_mask = classic_mask & empty_lineage_mask
                if classic_empty_mask.any():
                    self.df.loc[classic_empty_mask, "Lineage"] = "HYBRID"
                    self.logger.info(f"Assigned HYBRID lineage to {classic_empty_mask.sum()} classic products with empty lineage")
                
                # For non-classic types, check for CBD content first
                non_classic_empty_mask = ~classic_mask & empty_lineage_mask
                if non_classic_empty_mask.any():
                    # Define edible types
                    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                    
                    # Create mask for edible products
                    edible_mask = self.df["Product Type*"].str.strip().str.lower().isin(edible_types)
                    
                    # For edibles, be more conservative about CBD lineage assignment
                    if edible_mask.any():
                        # Only assign CBD lineage to edibles if they are explicitly CBD-focused
                        cbd_edible_mask = (
                            (self.df["Product Type*"].str.strip().str.lower() == "high cbd edible liquid") |
                            (self.df["Product Strain"].astype(str).str.lower().str.strip() == "cbd blend") |
                            (self.df[product_name_col].str.contains(r"\bCBD\b", case=False, na=False) if product_name_col else False)
                        )
                        
                        # Edibles with explicit CBD focus get CBD lineage
                        cbd_edible_empty = non_classic_empty_mask & edible_mask & cbd_edible_mask
                        if cbd_edible_empty.any():
                            self.df.loc[cbd_edible_empty, "Lineage"] = "CBD"
                            self.logger.info(f"Assigned CBD lineage to {cbd_edible_empty.sum()} CBD-focused edible products")
                        
                        # All other edibles get MIXED lineage
                        non_cbd_edible_empty = non_classic_empty_mask & edible_mask & ~cbd_edible_mask
                        if non_cbd_edible_empty.any():
                            self.df.loc[non_cbd_edible_empty, "Lineage"] = "MIXED"
                            self.logger.info(f"Assigned MIXED lineage to {non_cbd_edible_empty.sum()} edible products")
                    
                    # For non-edible non-classic types, use the original logic
                    non_edible_mask = ~edible_mask
                    non_edible_empty = non_classic_empty_mask & non_edible_mask
                    if non_edible_empty.any():
                        # Check if non-edible non-classic products contain CBD-related content
                        cbd_content_mask = (
                            self.df["Description"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False) |
                            (self.df[product_name_col].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False) if product_name_col else False) |
                            (self.df["Product Strain"].astype(str).str.lower().str.strip() == "cbd blend")
                        )
                        
                        # Non-edible non-classic products with CBD content get CBD lineage
                        cbd_non_edible_empty = non_edible_empty & cbd_content_mask
                        if cbd_non_edible_empty.any():
                            self.df.loc[cbd_non_edible_empty, "Lineage"] = "CBD"
                        
                        # Non-edible non-classic products without CBD content get MIXED lineage
                        non_cbd_non_edible_empty = non_edible_empty & ~cbd_content_mask
                        if non_cbd_non_edible_empty.any():
                            self.df.loc[non_cbd_non_edible_empty, "Lineage"] = "MIXED"

            # 8) Build Description & Ratio & Strain
            if "ProductName" in self.df.columns:
                self.logger.debug("Building Description and Ratio columns")

                def get_description(name):
                    # Handle pandas Series and other non-string types
                    if name is None:
                        return ""
                    if isinstance(name, pd.Series):
                        if pd.isna(name).any():
                            return ""
                        name = name.iloc[0] if len(name) > 0 else ""
                    elif pd.isna(name):
                        return ""
                    name = str(name).strip()
                    if not name:
                        return ""
                    if ' by ' in name:
                        return name.split(' by ')[0].strip()
                    if ' - ' in name:
                        # Take all parts before the last hyphen
                        return name.rsplit(' - ', 1)[0].strip()
                    return name.strip()

                # Ensure Product Name* is string type before applying
                if product_name_col:
                    # Reset index to avoid duplicate labels before applying operations
                    self.df.reset_index(drop=True, inplace=True)
                    
                    # Ensure we get a Series, not a DataFrame
                    if isinstance(product_name_col, list):
                        product_name_col = product_name_col[0] if product_name_col else None
                    
                    if product_name_col and product_name_col in self.df.columns:
                        self.df[product_name_col] = self.df[product_name_col].astype(str)
                        # Ensure we get a Series by using .iloc[:, 0] if it's a DataFrame
                        product_names = self.df[product_name_col]
                        if isinstance(product_names, pd.DataFrame):
                            product_names = product_names.iloc[:, 0]
                        product_names = product_names.astype(str)
                        # Debug: Check if product_names is a Series or DataFrame
                        self.logger.debug(f"product_names type: {type(product_names)}, shape: {getattr(product_names, 'shape', 'N/A')}")
                        
                        # Ensure product_names is a Series before calling .str
                        if isinstance(product_names, pd.Series):
                            # Always overwrite Description with transformed ProductName values
                            self.df["Description"] = product_names.str.strip()
                        else:
                            # Fallback: convert to string and strip manually
                            self.df["Description"] = product_names.astype(str).str.strip()
                        
                        # Handle ' by ' pattern for all Description values
                        mask_by = self.df["Description"].str.contains(' by ', na=False)
                        self.df.loc[mask_by, "Description"] = self.df.loc[mask_by, "Description"].str.split(' by ').str[0].str.strip()
                        
                        # Handle ' - ' pattern, but preserve weight for classic types
                        mask_dash = self.df["Description"].str.contains(' - ', na=False)
                        # Don't remove weight for classic types (including rso/co2 tankers)
                        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
                        classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(classic_types)
                        
                        # Only remove weight for non-classic types
                        non_classic_dash_mask = mask_dash & ~classic_mask
                        self.df.loc[non_classic_dash_mask, "Description"] = self.df.loc[non_classic_dash_mask, "Description"].str.rsplit(' - ', n=1).str[0].str.strip()
                    else:
                        # Fallback to empty descriptions
                        self.df["Description"] = ""
                    
                    # Reset index again after operations to prevent duplicate labels
                    self.df.reset_index(drop=True, inplace=True)
                
                mask_para = self.df["Product Type*"].str.strip().str.lower() == "paraphernalia"
                self.df.loc[mask_para, "Description"] = (
                    self.df.loc[mask_para, "Description"]
                    .str.replace(r"\s*-\s*\d+g$", "", regex=True)
                )

                # Calculate complexity for Description column using vectorized operations
                # Reset index before applying to prevent duplicate labels
                self.df.reset_index(drop=True, inplace=True)
                # Use a safer approach for applying the complexity function
                try:
                    self.df["Description_Complexity"] = self.df["Description"].apply(_complexity)
                except Exception as e:
                    self.logger.warning(f"Error applying complexity function: {e}")
                    # Fallback: create a simple complexity based on length
                    self.df["Description_Complexity"] = self.df["Description"].str.len().fillna(0)
                # Reset index after apply operation to prevent duplicate labels
                self.df.reset_index(drop=True, inplace=True)

                # Build cannabinoid content info
                self.logger.debug("Extracting cannabinoid content from Product Name")
                # Extract text following the FINAL hyphen only, but not for classic types
                if product_name_col:
                    # Ensure we get a Series, not a DataFrame
                    product_names_for_ratio = self.df[product_name_col]
                    if isinstance(product_names_for_ratio, pd.DataFrame):
                        product_names_for_ratio = product_names_for_ratio.iloc[:, 0]
                    
                    # Don't extract weight for classic types (including rso/co2 tankers)
                    # Note: capsules are NOT classic types for ratio extraction - they should extract ratio like edibles
                    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
                    classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(classic_types)
                    
                    # Extract ratio for non-classic types only (including capsules)
                    # For classic types, preserve existing ratio values from the file
                    non_classic_mask = ~classic_mask
                    if non_classic_mask.any():
                        extracted_ratios = product_names_for_ratio.loc[non_classic_mask].str.extract(r".*-\s*(.+)").fillna("")
                        # Ensure we get the first column as a Series
                        if isinstance(extracted_ratios, pd.DataFrame):
                            extracted_ratios = extracted_ratios.iloc[:, 0]
                        self.df.loc[non_classic_mask, "Ratio"] = extracted_ratios
                else:
                    self.df["Ratio"] = ""
                self.logger.debug(f"Sample cannabinoid content values before processing: {self.df['Ratio'].head()}")
                
                # Replace "/" with space to remove backslash formatting
                self.df["Ratio"] = self.df["Ratio"].str.replace(r"/", " ", regex=True)
                
                # Replace "nan" values with empty string to trigger default THC: CBD: formatting
                self.df["Ratio"] = self.df["Ratio"].replace("nan", "")
                
                self.logger.debug(f"Sample cannabinoid content values after processing: {self.df['Ratio'].head()}")

                # Set Ratio_or_THC_CBD based on product type
                def set_ratio_or_thc_cbd(row):
                    product_type = str(row.get("Product Type*", "")).strip().lower()
                    ratio = str(row.get("Ratio", "")).strip()
                    
                    # Handle "nan" values by replacing with empty string
                    if ratio.lower() == "nan":
                        ratio = ""
                    
                    classic_types = [
                        "flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"
                    ]
                    # Note: capsules are NOT classic types for ratio processing - they should be treated as edibles
                    BAD_VALUES = {"", "CBD", "THC", "CBD:", "THC:", "CBD:\n", "THC:\n", "nan"}
                    
                    # For pre-rolls and infused pre-rolls, use JointRatio if available, otherwise default format
                    if product_type in ["pre-roll", "infused pre-roll"]:
                        joint_ratio = str(row.get("JointRatio", "")).strip()
                        if joint_ratio and joint_ratio not in BAD_VALUES:
                            # Remove leading dash if present
                            if joint_ratio.startswith("- "):
                                joint_ratio = joint_ratio[2:]
                            return joint_ratio
                        return "THC:|BR|CBD:"
                    
                    # For solventless concentrate, check if ratio is a weight + unit format
                    if product_type == "solventless concentrate":
                        if not ratio or ratio in BAD_VALUES or not is_weight_with_unit(ratio):
                            return "1g"
                        return ratio
                    
                    if product_type in classic_types:
                        if not ratio or ratio in BAD_VALUES:
                            return "THC:|BR|CBD:"
                        # If ratio contains THC/CBD values, use it directly
                        if any(cannabinoid in ratio.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                            return ratio
                        # If it's a valid ratio format, use it
                        if is_real_ratio(ratio):
                            return ratio
                        # If it's a weight format (like "1g", "28g"), use it
                        if is_weight_with_unit(ratio):
                            return ratio
                        # Otherwise, use default THC:CBD format
                        return "THC:|BR|CBD:"
                    
                    # For Edibles, Topicals, Tinctures, etc., use the ratio if it contains cannabinoid content
                    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                    if product_type in edible_types:
                        if not ratio or ratio in BAD_VALUES:
                            return "THC:|BR|CBD:"
                        # If ratio contains cannabinoid content, use it
                        if any(cannabinoid in ratio.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                            return ratio
                        # If it's a weight format, use it
                        if is_weight_with_unit(ratio):
                            return ratio
                        # Otherwise, use default THC:CBD format
                        return "THC:|BR|CBD:"
                    
                    # For any other product type, return the ratio as-is
                    return ratio

                # Reset index before applying to prevent duplicate labels
                self.df.reset_index(drop=True, inplace=True)
                # Use a safer approach for applying the ratio function
                try:
                    self.df["Ratio_or_THC_CBD"] = self.df.apply(set_ratio_or_thc_cbd, axis=1)
                except Exception as e:
                    self.logger.warning(f"Error applying ratio function: {e}")
                    # Fallback: use default values
                    self.df["Ratio_or_THC_CBD"] = "THC:|BR|CBD:"
                # Reset index after apply operation to prevent duplicate labels
                self.df.reset_index(drop=True, inplace=True)
                self.logger.debug(f"Ratio_or_THC_CBD values: {self.df['Ratio_or_THC_CBD'].head()}")

                # Ensure Product Strain exists and is categorical
                if "Product Strain" not in self.df.columns:
                    self.df["Product Strain"] = ""
                # Fill null values before converting to categorical
                self.df["Product Strain"] = self.df["Product Strain"].fillna("Mixed")
                # Don't convert to categorical yet - wait until after all Product Strain logic is complete

                # Special case: paraphernalia gets Product Strain set to "Paraphernalia"
                mask_para = self.df["Product Type*"].str.strip().str.lower() == "paraphernalia"
                if mask_para.any():
                    # Only convert to categorical if there's actually paraphernalia
                    if "Product Strain" not in self.df.columns:
                        self.df["Product Strain"] = pd.Categorical([], categories=["Paraphernalia"])
                    else:
                        if isinstance(self.df["Product Strain"].dtype, pd.CategoricalDtype):
                            if "Paraphernalia" not in self.df["Product Strain"].cat.categories:
                                self.df["Product Strain"] = self.df["Product Strain"].cat.add_categories(["Paraphernalia"])
                        else:
                            # Ensure no null values before creating categorical
                            product_strain_clean = self.df["Product Strain"].fillna("Mixed")
                            unique_values = product_strain_clean.unique().tolist()
                            if "Paraphernalia" not in unique_values:
                                unique_values.append("Paraphernalia")
                            self.df["Product Strain"] = pd.Categorical(
                                product_strain_clean,
                                categories=unique_values
                            )
                    # Set paraphernalia products to "Paraphernalia"
                    self.df.loc[mask_para, "Product Strain"] = "Paraphernalia"

                # Force CBD Blend for any ratio containing CBD, CBC, CBN or CBG
                mask_cbd_ratio = self.df["Ratio"].str.contains(
                    r"\b(?:CBD|CBC|CBN|CBG)\b", case=False, na=False
                )
                # Use .any() to avoid Series boolean ambiguity
                if mask_cbd_ratio.any():
                    self.df.loc[mask_cbd_ratio, "Product Strain"] = "CBD Blend"
                    # Debug: Log which products got CBD Blend from ratio
                    cbd_products = self.df[mask_cbd_ratio]
                    for idx, row in cbd_products.iterrows():
                        self.logger.info(f"Assigned CBD Blend from ratio: {row.get('Product Name*', 'NO NAME')} (Type: {row.get('Product Type*', 'NO TYPE')})")
                
                # If Description contains ":" or "CBD", set Product Strain to 'CBD Blend' (excluding edibles which have their own logic)
                edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                non_edible_mask = ~self.df["Product Type*"].str.strip().str.lower().isin(edible_types)
                
                mask_cbd_blend = (self.df["Description"].str.contains(":", na=False) | self.df["Description"].str.contains("CBD", case=False, na=False)) & non_edible_mask
                # Use .any() to avoid Series boolean ambiguity
                if mask_cbd_blend.any():
                    self.df.loc[mask_cbd_blend, "Product Strain"] = "CBD Blend"
                    # Debug: Log which products got CBD Blend from description
                    cbd_desc_products = self.df[mask_cbd_blend]
                    for idx, row in cbd_desc_products.iterrows():
                        self.logger.info(f"Assigned CBD Blend from description: {row.get('Product Name*', 'NO NAME')} (Type: {row.get('Product Type*', 'NO TYPE')})")
                
                # NEW: If no strain in column, check if product contains CBD CBN CBG or CBC, or a ":" in description
                # This applies when Product Strain is empty, null, or "Mixed" (excluding edibles which have their own logic)
                no_strain_mask = (
                    self.df["Product Strain"].isnull() | 
                    (self.df["Product Strain"].astype(str).str.strip() == "") |
                    (self.df["Product Strain"].astype(str).str.lower().str.strip() == "mixed")
                )
                
                # Check if description contains cannabinoids or ":"
                cannabinoid_mask = (
                    self.df["Description"].str.contains(r"\b(?:CBD|CBC|CBN|CBG)\b", case=False, na=False) |
                    self.df["Description"].str.contains(":", na=False)
                )
                
                # Apply CBD Blend to non-edible products with no strain that contain cannabinoids or ":"
                combined_cbd_mask = no_strain_mask & cannabinoid_mask & non_edible_mask
                if combined_cbd_mask.any():
                    self.df.loc[combined_cbd_mask, "Product Strain"] = "CBD Blend"
                    # Debug: Log which products got CBD Blend from combined logic
                    combined_cbd_products = self.df[combined_cbd_mask]
                    for idx, row in combined_cbd_products.iterrows():
                        self.logger.info(f"Assigned CBD Blend from combined logic: {row.get('Product Name*', 'NO NAME')} (Type: {row.get('Product Type*', 'NO TYPE')})")
                
                # Debug: Log final Product Strain values for RSO/CO2 Tankers
                rso_co2_mask = self.df["Product Type*"].str.strip().str.lower() == "rso/co2 tankers"
                if rso_co2_mask.any():
                    rso_co2_products = self.df[rso_co2_mask]
                    self.logger.info(f"=== RSO/CO2 Tankers Product Strain Debug ===")
                    for idx, row in rso_co2_products.iterrows():
                        self.logger.info(f"RSO/CO2 Tanker: {row.get('Product Name*', 'NO NAME')} -> Product Strain: '{row.get('Product Strain', 'NO STRAIN')}'")
                    self.logger.info(f"=== End RSO/CO2 Tankers Debug ===")
                
                # RSO/CO2 Tankers: if Description contains CBD, CBG, CBC, CBN, or ":", then Product Strain is "CBD Blend", otherwise "Mixed"
                rso_co2_mask = self.df["Product Type*"].str.strip().str.lower() == "rso/co2 tankers"
                if rso_co2_mask.any():
                    # Check if Description contains CBD, CBG, CBC, CBN, or ":"
                    cbd_content_mask = (
                        self.df["Description"].str.contains(r"CBD|CBG|CBC|CBN", case=False, na=False) |
                        self.df["Description"].str.contains(":", na=False)
                    )
                    
                    # For RSO/CO2 Tankers with cannabinoid content or ":" in Description, set to "CBD Blend"
                    rso_co2_cbd_mask = rso_co2_mask & cbd_content_mask
                    if rso_co2_cbd_mask.any():
                        self.df.loc[rso_co2_cbd_mask, "Product Strain"] = "CBD Blend"
                        self.logger.info(f"Assigned 'CBD Blend' to {rso_co2_cbd_mask.sum()} RSO/CO2 Tankers with cannabinoid content or ':' in Description")
                    
                    # For RSO/CO2 Tankers without cannabinoid content or ":" in Description, set to "Mixed"
                    rso_co2_mixed_mask = rso_co2_mask & ~cbd_content_mask
                    if rso_co2_mixed_mask.any():
                        self.df.loc[rso_co2_mixed_mask, "Product Strain"] = "Mixed"
                        self.logger.info(f"Assigned 'Mixed' to {rso_co2_mixed_mask.sum()} RSO/CO2 Tankers without cannabinoid content or ':' in Description")

                # Edibles: if ProductName contains CBD, CBG, CBN, or CBC, then Product Strain is "CBD Blend", otherwise "Mixed"
                edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                edible_mask = self.df["Product Type*"].str.strip().str.lower().isin(edible_types)
                if edible_mask.any():
                    # Check if ProductName contains CBD, CBG, CBN, or CBC (same as UI logic)
                    edible_cbd_content_mask = (
                        self.df["ProductName"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False)
                    )
                    
                    # For edibles with cannabinoid content in ProductName, set to "CBD Blend"
                    edible_cbd_mask = edible_mask & edible_cbd_content_mask
                    if edible_cbd_mask.any():
                        self.df.loc[edible_cbd_mask, "Product Strain"] = "CBD Blend"
                        self.logger.info(f"Assigned 'CBD Blend' to {edible_cbd_mask.sum()} edibles with cannabinoid content in ProductName")
                    
                    # For edibles without cannabinoid content in ProductName, set to "Mixed"
                    edible_mixed_mask = edible_mask & ~edible_cbd_content_mask
                    if edible_mixed_mask.any():
                        self.df.loc[edible_mixed_mask, "Product Strain"] = "Mixed"
                        self.logger.info(f"Assigned 'Mixed' to {edible_mixed_mask.sum()} edibles without cannabinoid content in ProductName")

            # 8.5) Convert Product Strain to categorical after all logic is complete
            if "Product Strain" in self.df.columns:
                self.df["Product Strain"] = self.df["Product Strain"].astype("category")

            # 9) Convert key fields to categorical
            for col in ["Product Type*", "Lineage", "Product Brand", "Vendor"]:
                if col in self.df.columns:
                    # Fill null values before converting to categorical
                    self.df[col] = self.df[col].fillna("Unknown")
                    self.df[col] = self.df[col].astype("category")

            # 10) CBD and Mixed overrides (with edible lineage protection)
            if "Lineage" in self.df.columns:
                # Define edible types for protection
                edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                edible_mask = self.df["Product Type*"].str.strip().str.lower().isin(edible_types)
                
                # If Product Strain is 'CBD Blend', set Lineage to 'CBD' (but protect edibles that already have proper lineage)
                if "Product Strain" in self.df.columns and "Lineage" in self.df.columns:
                    cbd_blend_mask = self.df["Product Strain"].astype(str).str.lower().str.strip() == "cbd blend"
                    # Only apply to non-edibles or edibles that don't already have a proper lineage
                    non_edible_cbd_blend = cbd_blend_mask & ~edible_mask
                    edible_cbd_blend_no_lineage = cbd_blend_mask & edible_mask & (
                        self.df["Lineage"].isnull() | 
                        (self.df["Lineage"].astype(str).str.strip() == "") |
                        (self.df["Lineage"].astype(str).str.strip() == "Unknown")
                    )
                    
                    combined_cbd_blend_mask = non_edible_cbd_blend | edible_cbd_blend_no_lineage
                    
                    if combined_cbd_blend_mask.any() and "Lineage" in self.df.columns:
                        if "CBD" not in self.df["Lineage"].cat.categories:
                            self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["CBD"])
                        self.df.loc[combined_cbd_blend_mask, "Lineage"] = "CBD"
                        self.logger.info(f"Assigned CBD lineage to {combined_cbd_blend_mask.sum()} products with CBD Blend strain")

                # If Description or Product Name* contains CBD, CBG, CBN, CBC, set Lineage to 'CBD' (but protect edibles)
                # Fix: ensure product_name_col is always a Series for .str methods
                if product_name_col:
                    product_names_for_cbd = self.df[product_name_col]
                    if isinstance(product_names_for_cbd, pd.DataFrame):
                        product_names_for_cbd = product_names_for_cbd.iloc[:, 0]
                else:
                    product_names_for_cbd = pd.Series("")
                cbd_mask = (
                    self.df["Description"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False) |
                    (product_names_for_cbd.str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False) if product_name_col else False)
                )
                # Only apply to non-edibles or edibles that don't already have a proper lineage
                non_edible_cbd = cbd_mask & ~edible_mask
                edible_cbd_no_lineage = cbd_mask & edible_mask & (
                    (self.df["Lineage"].isnull() if "Lineage" in self.df.columns else True) | 
                    (self.df["Lineage"].astype(str).str.strip() == "" if "Lineage" in self.df.columns else True) |
                    (self.df["Lineage"].astype(str).str.strip() == "Unknown" if "Lineage" in self.df.columns else True)
                )
                
                combined_cbd_mask = non_edible_cbd | edible_cbd_no_lineage
                
                # Use .any() to avoid Series boolean ambiguity
                if combined_cbd_mask.any() and "Lineage" in self.df.columns:
                    self.df.loc[combined_cbd_mask, "Lineage"] = "CBD"
                    self.logger.info(f"Assigned CBD lineage to {combined_cbd_mask.sum()} products with cannabinoid content")

                # DISABLED: If Lineage is missing or empty, set to 'MIXED'
                # empty_lineage_mask = self.df["Lineage"].isnull() | (self.df["Lineage"].astype(str).str.strip() == "")
                # if "MIXED" not in self.df["Lineage"].cat.categories:
                #     self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["MIXED"])
                # # Use .any() to avoid Series boolean ambiguity
                # if empty_lineage_mask.any():
                #     self.df.loc[empty_lineage_mask, "Lineage"] = "MIXED"

                # DISABLED: For all edibles, set Lineage to 'MIXED' unless already 'CBD'
                # edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
                # if "Product Type*" in self.df.columns:
                #     edible_mask = self.df["Product Type*"].str.strip().str.lower().isin([e.lower() for e in edible_types])
                #     not_cbd_mask = self.df["Lineage"].astype(str).str.upper() != "CBD"
                #     if "MIXED" not in self.df["Lineage"].cat.categories:
                #         self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["MIXED"])
                #     # Use .any() to avoid Series boolean ambiguity
                #     combined_mask = edible_mask & not_cbd_mask
                #     if combined_mask.any():
                #         self.df.loc[combined_mask, "Lineage"] = "MIXED"

            # 11) Normalize Weight* and CombinedWeight
            if "Weight*" in self.df.columns:
                self.df["Weight*"] = pd.to_numeric(self.df["Weight*"], errors="coerce") \
                    .apply(lambda x: str(int(x)) if pd.notnull(x) and float(x).is_integer() else str(x))
            if "Weight*" in self.df.columns and "Units" in self.df.columns:
                # Fill null values before converting to categorical
                combined_weight = (self.df["Weight*"] + self.df["Units"]).fillna("Unknown")
                self.df["CombinedWeight"] = combined_weight.astype("category")

            # 12) Format Price
            if "Price" in self.df.columns:
                def format_p(p):
                    if pd.isna(p) or p == '':
                        return ""
                    s = str(p).strip().lstrip("$").replace("'", "").strip()
                    try:
                        v = float(s)
                        if v.is_integer():
                            return f"${int(v)}"
                        else:
                            # Round to 2 decimal places and remove trailing zeros
                            return f"${v:.2f}".rstrip('0').rstrip('.')
                    except:
                        return f"${s}"
                self.df["Price"] = self.df["Price"].apply(lambda x: format_p(x) if pd.notnull(x) else "")
                self.df["Price"] = self.df["Price"].astype("string")

            # 13) Special pre-roll Ratio logic
            def process_ratio(row):
                t = str(row.get("Product Type*", "")).strip().lower()
                if t in ["pre-roll", "infused pre-roll"]:
                    # For pre-rolls, extract the weight/quantity part after the last hyphen
                    ratio_str = str(row.get("Ratio", ""))
                    if " - " in ratio_str:
                        parts = ratio_str.split(" - ")
                        if len(parts) >= 2:
                            # Take everything after the last hyphen
                            weight_part = parts[-1].strip()
                            return f" - {weight_part}" if weight_part and not weight_part.startswith(" - ") else weight_part
                    return ratio_str
                return row.get("Ratio", "")
            
            self.logger.debug("Applying special pre-roll ratio logic")
            self.df["Ratio"] = self.df.apply(process_ratio, axis=1)
            self.logger.debug(f"Final Ratio values after pre-roll processing: {self.df['Ratio'].head()}")

            # Create JointRatio column for Pre-Roll and Infused Pre-Roll products
            preroll_mask = self.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
            self.df["JointRatio"] = ""
            
            if preroll_mask.any():
                # Extract joint ratio from Product Name since there's no separate "Joint Ratio" column
                # Look for patterns like "0.5g x 2 Pack", "1g x 28 Pack", etc. in the product name
                def extract_joint_ratio_from_name(product_name):
                    if pd.isna(product_name) or str(product_name).strip() == '':
                        return ''
                    
                    product_name_str = str(product_name)
                    
                    # Look for patterns like "0.5g x 2 Pack", "1g x 28 Pack", etc.
                    import re
                    
                    # Pattern 1: "weight x count Pack" (e.g., "0.5g x 2 Pack", ".75g x 5 Pack")
                    pattern1 = r'(\d*\.?\d+g)\s*x\s*(\d+)\s*Pack'
                    match1 = re.search(pattern1, product_name_str, re.IGNORECASE)
                    if match1:
                        weight = match1.group(1)
                        count = match1.group(2)
                        return f"{weight} x {count} Pack"
                    
                    # Pattern 2: "weight x count" (e.g., "0.5g x 2", ".75g x 5")
                    pattern2 = r'(\d*\.?\d+g)\s*x\s*(\d+)'
                    match2 = re.search(pattern2, product_name_str, re.IGNORECASE)
                    if match2:
                        weight = match2.group(1)
                        count = match2.group(2)
                        return f"{weight} x {count}"
                    
                    # Pattern 3: Just weight (e.g., "1g", "0.5g", ".75g")
                    pattern3 = r'(\d*\.?\d+g)'
                    match3 = re.search(pattern3, product_name_str, re.IGNORECASE)
                    if match3:
                        weight = match3.group(1)
                        return weight
                    
                    return ''
                
                # Apply the extraction function to pre-roll products
                preroll_products = self.df[preroll_mask]
                for idx in preroll_products.index:
                    # Use the correct column name - check if ProductName exists, otherwise use Product Name*
                    product_name_col = 'ProductName' if 'ProductName' in self.df.columns else 'Product Name*'
                    if product_name_col in self.df.columns:
                        product_name = self.df.loc[idx, product_name_col]
                        joint_ratio = extract_joint_ratio_from_name(product_name)
                        if joint_ratio:
                            self.df.loc[idx, 'JointRatio'] = joint_ratio
                            self.logger.debug(f"Extracted JointRatio '{joint_ratio}' from product name: '{product_name}'")
                
                # For remaining pre-rolls without valid JointRatio, try to generate from Weight
                remaining_preroll_mask = preroll_mask & (self.df["JointRatio"] == '')
                for idx in self.df[remaining_preroll_mask].index:
                    weight_value = self.df.loc[idx, 'Weight*']
                    if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
                        try:
                            weight_float = float(weight_value)
                            # Generate a more descriptive format: "1g x 1" for single units
                            if weight_float == 1.0:
                                default_joint_ratio = "1g x 1"
                            else:
                                default_joint_ratio = f"{weight_float}g"
                            self.df.loc[idx, 'JointRatio'] = default_joint_ratio
                            self.logger.debug(f"Generated JointRatio for record {idx}: '{default_joint_ratio}' from Weight {weight_value}")
                        except (ValueError, TypeError):
                            pass
            
            # Ensure no NaN values remain in JointRatio column
            self.df["JointRatio"] = self.df["JointRatio"].fillna('')
            
            # Fix: Replace any 'nan' string values with empty strings
            nan_string_mask = (self.df["JointRatio"].astype(str).str.lower() == 'nan')
            self.df.loc[nan_string_mask, "JointRatio"] = ''
            
            # Fix: For still empty JointRatio, generate default from Weight (no Ratio fallback)
            still_empty_mask = preroll_mask & (self.df["JointRatio"] == '')
            for idx in self.df[still_empty_mask].index:
                weight_value = self.df.loc[idx, 'Weight*']
                if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
                    try:
                        weight_float = float(weight_value)
                        # Generate a more descriptive format: "1g x 1" for single units
                        if weight_float == 1.0:
                            default_joint_ratio = "1g x 1"
                        else:
                            default_joint_ratio = f"{weight_float}g"
                        self.df.loc[idx, 'JointRatio'] = default_joint_ratio
                        self.logger.debug(f"Fixed JointRatio for record {idx}: Generated default '{default_joint_ratio}' from Weight")
                    except (ValueError, TypeError):
                        pass
            
            # JointRatio: preserve original spacing exactly as in Excel - no normalization
            self.logger.debug(f"Sample JointRatio values after NaN fixes: {self.df.loc[preroll_mask, 'JointRatio'].head()}")
            # Add detailed logging for JointRatio values
            if preroll_mask.any():
                sample_values = self.df.loc[preroll_mask, 'JointRatio'].head(10)
                for idx, value in sample_values.items():
                    self.logger.debug(f"JointRatio value '{value}' (length: {len(str(value))}, repr: {repr(str(value))})")

            # Reorder columns to place JointRatio next to Ratio
            if "Ratio" in self.df.columns and "JointRatio" in self.df.columns:
                ratio_col_idx = self.df.columns.get_loc("Ratio")
                cols = self.df.columns.tolist()
                
                # Remove duplicates first
                unique_cols = []
                seen_cols = set()
                for col in cols:
                    if col not in seen_cols:
                        unique_cols.append(col)
                        seen_cols.add(col)
                    else:
                        self.logger.warning(f"Removing duplicate column in JointRatio reorder: {col}")
                
                cols = unique_cols
                cols.remove("JointRatio")
                cols.insert(ratio_col_idx + 1, "JointRatio")
                # Ensure Description_Complexity is preserved
                if "Description_Complexity" not in cols:
                    cols.append("Description_Complexity")
                self.df = self.df[cols]

            # --- Reorder columns: move Description_Complexity, Ratio_or_THC_CBD, CombinedWeight after Lineage ---
            # First, remove any duplicate column names to prevent DataFrame issues
            cols = self.df.columns.tolist()
            unique_cols = []
            seen_cols = set()
            for col in cols:
                if col not in seen_cols:
                    unique_cols.append(col)
                    seen_cols.add(col)
                else:
                    self.logger.warning(f"Removing duplicate column: {col}")
            
            cols = unique_cols
            
            def move_after(col_to_move, after_col):
                if col_to_move in cols and after_col in cols:
                    cols.remove(col_to_move)
                    idx = cols.index(after_col)
                    cols.insert(idx+1, col_to_move)
            move_after('Description_Complexity', 'Lineage')
            move_after('Ratio_or_THC_CBD', 'Lineage')
            move_after('CombinedWeight', 'Lineage')
            self.df = self.df[cols]

            # Normalize Joint Ratio column name for consistency
            if "Joint Ratio" in self.df.columns and "JointRatio" not in self.df.columns:
                self.df.rename(columns={"Joint Ratio": "JointRatio"}, inplace=True)
            self.logger.debug(f"Columns after JointRatio normalization: {self.df.columns.tolist()}")

            # 14) Optimized Lineage Persistence - ALWAYS ENABLED
            if ENABLE_LINEAGE_PERSISTENCE:
                self.logger.debug("Applying optimized lineage persistence from database")
                
                # Apply lineage persistence from database
                self.df = optimized_lineage_persistence(self, self.df)
                
                # Update database with current lineage information
                batch_lineage_database_update(self, self.df)
                
                self.logger.debug("Optimized lineage persistence complete")
            else:
                self.logger.debug("Lineage persistence disabled")

            # Optimize memory usage for PythonAnywhere
            self.logger.debug("Optimizing memory usage for PythonAnywhere")
            
            # Convert string columns to categorical where appropriate to save memory
            categorical_columns = ['Product Type*', 'Lineage', 'Product Brand', 'Vendor', 'Product Strain']
            for col in categorical_columns:
                if col in self.df.columns:
                    # Only convert if the column has reasonable number of unique values
                    unique_count = self.df[col].nunique()
                    if unique_count < len(self.df) * 0.5:  # Less than 50% unique values
                        self.df[col] = self.df[col].astype('category')
                        self.logger.debug(f"Converted {col} to categorical (unique values: {unique_count})")
            
            # Final cleanup: remove any remaining duplicate columns
            cols = self.df.columns.tolist()
            unique_cols = []
            seen_cols = set()
            for col in cols:
                if col not in seen_cols:
                    unique_cols.append(col)
                    seen_cols.add(col)
                else:
                    self.logger.warning(f"Final cleanup: removing duplicate column: {col}")
            
            if len(unique_cols) != len(cols):
                self.df = self.df[unique_cols]
                self.logger.info(f"Final cleanup: removed {len(cols) - len(unique_cols)} duplicate columns")
            
            # Cache dropdown values
            self._cache_dropdown_values()
            self.logger.debug(f"Final columns after all processing: {self.df.columns.tolist()}")
            self.logger.debug(f"Sample data after all processing:\n{self.df[['ProductName', 'Description', 'Ratio', 'Product Strain']].head()}")
            
            # Log memory usage for PythonAnywhere monitoring
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                self.logger.info(f"Memory usage after file load: {memory_info.rss / (1024*1024):.2f} MB")
            except ImportError:
                self.logger.debug("psutil not available for memory monitoring")
            
            # --- Product/Strain Database Integration (Background Processing) ---
            # Move this to background processing to avoid blocking the main file load
            self._schedule_product_db_integration()
            
            # Cache the processed file
            self._file_cache[cache_key] = self.df.copy()
            self._last_loaded_file = file_path
            
            # Manage cache size
            self._manage_cache_size()
            
            # Force garbage collection to free memory
            import gc
            gc.collect()

            # --- After classic type lineage logic, enforce non-classic type rules ---
            if "Product Type*" in self.df.columns and "Lineage" in self.df.columns:
                # Define specific non-classic types that should always use MIXED or CBD Blend
                nonclassic_product_types = [
                    "edible (solid)", "edible (liquid)", "Edible (Solid)", "Edible (Liquid)",
                    "tincture", "Tincture", "topical", "Topical", 
                    "capsule", "Capsule", "suppository", "Suppository", "transdermal", "Transdermal",
                    "beverage", "Beverage", "powder", "Powder",
                    "gummy", "Gummy", "chocolate", "Chocolate", "cookie", "Cookie", 
                    "brownie", "Brownie", "candy", "Candy", "drink", "Drink",
                    "tea", "Tea", "coffee", "Coffee", "soda", "Soda", "juice", "Juice", 
                    "smoothie", "Smoothie", "shot", "Shot"
                ]
                
                # Identify non-classic types - products that are NOT in CLASSIC_TYPES
                from src.core.constants import CLASSIC_TYPES
                nonclassic_mask = ~self.df["Product Type*"].str.strip().str.lower().isin([c.lower() for c in CLASSIC_TYPES])
                
                # Add debugging
                self.logger.info(f"Non-classic type processing: Found {nonclassic_mask.sum()} non-classic products")
                if nonclassic_mask.any():
                    sample_types = self.df.loc[nonclassic_mask, "Product Type*"].unique()
                    self.logger.info(f"Sample non-classic product types: {sample_types}")
                
                # Identify CBD Blend products
                is_cbd_blend = (
                    self.df["Product Strain"].astype(str).str.lower().str.strip() == "cbd blend"
                ) | (
                    self.df["Description"].astype(str).str.lower().str.contains("cbd blend", na=False)
                )
                
                # Set Lineage to 'CBD' for blends (not 'CBD Blend')
                if "CBD" not in self.df["Lineage"].cat.categories:
                    self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["CBD"])
                self.df.loc[nonclassic_mask & is_cbd_blend, "Lineage"] = "CBD"
                
                # For all other non-classic types, set Lineage to 'MIXED' unless already 'CBD'
                if "MIXED" not in self.df["Lineage"].cat.categories:
                    self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["MIXED"])
                not_cbd = ~self.df["Lineage"].astype(str).str.upper().isin(["CBD"])
                self.df.loc[nonclassic_mask & not_cbd, "Lineage"] = "MIXED"
                
                # Never allow 'HYBRID' for non-classic types
                hybrid_mask = nonclassic_mask & (self.df["Lineage"].astype(str).str.upper() == "HYBRID")
                if hybrid_mask.any():
                    self.logger.info(f"Converting {hybrid_mask.sum()} non-classic products from HYBRID to MIXED")
                    self.df.loc[hybrid_mask, "Lineage"] = "MIXED"

            # --- Set default lineage for classic types if missing ---
            if "Product Type*" in self.df.columns and "Lineage" in self.df.columns:
                classic_mask = self.df["Product Type*"].str.strip().str.lower().isin([c.lower() for c in CLASSIC_TYPES])
                empty_lineage_mask = self.df["Lineage"].isnull() | (self.df["Lineage"].astype(str).str.strip() == "")
                set_hybrid_mask = classic_mask & empty_lineage_mask
                if "HYBRID" not in self.df["Lineage"].cat.categories:
                    self.df["Lineage"] = self.df["Lineage"].cat.add_categories(["HYBRID"])
                if set_hybrid_mask.any():
                    self.df.loc[set_hybrid_mask, "Lineage"] = "HYBRID"
                
                # Fix any MIXED lineage for classic types
                mixed_lineage_mask = (self.df["Lineage"] == "MIXED") & classic_mask
                if mixed_lineage_mask.any():
                    self.df.loc[mixed_lineage_mask, "Lineage"] = "HYBRID"
                    self.logger.info(f"Fixed {mixed_lineage_mask.sum()} classic products with MIXED lineage, changed to HYBRID")

            self.logger.info(f"File loaded successfully: {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
            
        except MemoryError as me:
            self.logger.error(f"Memory error loading file: {str(me)}")
            # Clear any partial data
            if hasattr(self, 'df'):
                del self.df
                self.df = None
            import gc
            gc.collect()
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading file: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Clear any partial data
            if hasattr(self, 'df'):
                del self.df
                self.df = None
            return False

    def apply_filters(self, filters: Optional[Dict[str, str]] = None):
        """Apply filters to the DataFrame."""
        if self.df is None or not filters:
            return self.df

        self.logger.debug(f"apply_filters received filters: {filters}")
        filtered_df = self.df.copy()
        column_mapping = {
            'vendor': 'Vendor',
            'brand': 'Product Brand',
            'productType': 'Product Type*',
            'lineage': 'Lineage',
            'weight': 'Weight*',
            'strain': 'Product Strain',
            'doh': 'DOH',
            'highCbd': 'Product Type*'  # Will be processed specially
        }
        for filter_key, value in filters.items():
            if value and value != 'All':
                if filter_key == 'highCbd':
                    # Special handling for High CBD filter
                    if value == 'High CBD Products':
                        filtered_df = filtered_df[
                            filtered_df['Product Type*'].astype(str).str.lower().str.strip().str.startswith('high cbd')
                        ]
                    elif value == 'Non-High CBD Products':
                        filtered_df = filtered_df[
                            ~filtered_df['Product Type*'].astype(str).str.lower().str.strip().str.startswith('high cbd')
                        ]
                else:
                    column = column_mapping.get(filter_key)
                    if column and column in filtered_df.columns:
                        # Convert both the column and the filter value to lowercase for case-insensitive comparison
                        filtered_df = filtered_df[
                            filtered_df[column].astype(str).str.lower().str.strip() == value.lower().strip()
                        ]
        return filtered_df

    def _cache_dropdown_values(self):
        """Cache unique values for dropdown filters."""
        if self.df is None:
            logger.warning("No DataFrame loaded, cannot cache dropdown values")
            return

        filter_columns = {
            'vendor': 'Vendor',
            'brand': 'Product Brand',
            'productType': 'Product Type*',
            'lineage': 'Lineage',
            'weight': 'Weight*',
            'strain': 'Product Strain',
            'doh': 'DOH',
            'highCbd': 'Product Type*'  # Will be processed specially
        }
        self.dropdown_cache = {}
        for filter_id, column in filter_columns.items():
            if column in self.df.columns:
                values = self.df[column].dropna().unique().tolist()
                values = [str(v) for v in values if str(v).strip()]
                # Exclude unwanted product types from dropdown
                if filter_id == 'productType':
                    filtered_values = []
                    for v in values:
                        v_lower = v.strip().lower()
                        if (('trade sample' in v_lower and 'not for sale' in v_lower) or 'deactivated' in v_lower):
                            continue
                        filtered_values.append(v)
                    values = filtered_values
                self.dropdown_cache[filter_id] = sorted(values)
            else:
                self.dropdown_cache[filter_id] = []

    def get_available_tags(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Return a list of tag objects with all necessary data."""
        if self.df is None:
            logger.warning("DataFrame is None in get_available_tags")
            return []
        
        filtered_df = self.apply_filters(filters) if filters else self.df
        logger.info(f"get_available_tags: DataFrame shape {self.df.shape}, filtered shape {filtered_df.shape}")
        
        tags = []
        seen_product_names = set()  # Track seen product names to prevent duplicates
        
        for _, row in filtered_df.iterrows():
            # Get quantity from various possible column names
            quantity = row.get('Quantity*', '') or row.get('Quantity Received*', '') or row.get('Quantity', '') or row.get('qty', '') or ''
            
            # Get formatted weight with units
            weight_with_units = self._format_weight_units(row)
            raw_weight = row.get('Weight*', '')
            
            # Helper function to safely get values and handle NaN
            def safe_get_value(value, default=''):
                if value is None:
                    return default
                if isinstance(value, pd.Series):
                    if pd.isna(value).any():
                        return default
                    value = value.iloc[0] if len(value) > 0 else default
                elif pd.isna(value):
                    return default
                return str(value).strip()
            
            # Use the dynamically detected product name column
            product_name_col = 'Product Name*'
            if product_name_col not in self.df.columns:
                possible_cols = ['ProductName', 'Product Name', 'Description']
                product_name_col = next((col for col in possible_cols if col in self.df.columns), None)
                if not product_name_col:
                    product_name_col = 'Description'  # Fallback to Description
            
            # Get the product name
            product_name = safe_get_value(row.get(product_name_col, '')) or safe_get_value(row.get('Description', '')) or 'Unnamed Product'
            
            # Skip if we've already seen this product name (deduplication)
            if product_name in seen_product_names:
                logger.debug(f"Skipping duplicate product: {product_name}")
                continue
            
            # Add to seen set
            seen_product_names.add(product_name)
            
            tag = {
                'Product Name*': product_name,
                'Vendor': safe_get_value(row.get('Vendor', '')),
                'Vendor/Supplier*': safe_get_value(row.get('Vendor', '')),
                'Product Brand': safe_get_value(row.get('Product Brand', '')),
                'ProductBrand': safe_get_value(row.get('Product Brand', '')),
                'Lineage': safe_get_value(row.get('Lineage', 'MIXED')),
                'Product Type*': safe_get_value(row.get('Product Type*', '')),
                'Product Type': safe_get_value(row.get('Product Type*', '')),
                'Weight*': safe_get_value(raw_weight),
                'Weight': safe_get_value(raw_weight),
                'WeightWithUnits': safe_get_value(weight_with_units),
                'WeightUnits': safe_get_value(weight_with_units),  # Add WeightUnits for frontend compatibility
                'Quantity*': safe_get_value(quantity),
                'Quantity Received*': safe_get_value(quantity),
                'quantity': safe_get_value(quantity),
                'DOH': safe_get_value(row.get('DOH', '')),  # Add DOH field for UI display
                # Also include the lowercase versions for backward compatibility
                'vendor': safe_get_value(row.get('Vendor', '')),
                'productBrand': safe_get_value(row.get('Product Brand', '')),
                'lineage': safe_get_value(row.get('Lineage', 'MIXED')),
                'productType': safe_get_value(row.get('Product Type*', '')),
                'weight': safe_get_value(raw_weight),
                'weightWithUnits': safe_get_value(weight_with_units),
                'displayName': product_name
            }
            # --- Filtering logic ---
            product_brand = str(tag['productBrand']).strip().lower()
            product_type = str(tag['productType']).strip().lower().replace('  ', ' ')
            weight = str(tag['weight']).strip().lower()

            # Sanitize lineage
            lineage = str(row.get('Lineage', 'MIXED') or '').strip().upper()
            if lineage not in VALID_LINEAGES:
                lineage = "MIXED"
            tag['Lineage'] = lineage
            tag['lineage'] = lineage

            # Filter out samples and invalid products
            product_name_lower = product_name.lower()
            product_type_lower = product_type.lower()
            if (
                weight == '-1g' or  # Invalid weight
                'trade sample' in product_type_lower or  # Filter any trade sample product types
                'sample' in product_name_lower or  # Filter products with "Sample" in name
                'trade sample' in product_name_lower or  # Filter products with "Trade Sample" in name
                any(pattern.lower() in product_name_lower for pattern in EXCLUDED_PRODUCT_PATTERNS) or  # Filter based on excluded patterns
                any(pattern.lower() in product_type_lower for pattern in EXCLUDED_PRODUCT_PATTERNS)  # Filter product types based on excluded patterns
            ):
                continue  # Skip this tag
            tags.append(tag)
        
        # Sort tags by vendor first, then by brand, then by weight
        def sort_key(tag):
            vendor = str(tag.get('vendor', '')).strip().lower()
            brand = str(tag.get('productBrand', '')).strip().lower()
            weight = ExcelProcessor.parse_weight_str(tag.get('weight', ''), tag.get('weightWithUnits', ''))
            return (vendor, brand, weight)
        
        sorted_tags = sorted(tags, key=sort_key)
        logger.info(f"get_available_tags: Returning {len(sorted_tags)} tags (removed {len(filtered_df) - len(sorted_tags)} duplicates)")
        return sorted_tags

    def select_tags(self, tags):
        """Add tags to the selected set, preserving order and avoiding duplicates."""
        if not isinstance(tags, (list, set)):
            tags = [tags]
        for tag in tags:
            if tag not in self.selected_tags:
                self.selected_tags.append(tag)
        
        # Final deduplication to ensure no duplicates exist
        seen = set()
        deduplicated_tags = []
        for tag in self.selected_tags:
            if tag not in seen:
                deduplicated_tags.append(tag)
                seen.add(tag)
        self.selected_tags = deduplicated_tags
        
        logger.debug(f"Selected tags after selection: {self.selected_tags}")

    def unselect_tags(self, tags):
        """Remove tags from the selected set."""
        if not isinstance(tags, (list, set)):
            tags = [tags]
        self.selected_tags = [tag for tag in self.selected_tags if tag not in tags]
        logger.debug(f"Selected tags after unselection: {self.selected_tags}")

    def get_selected_tags(self) -> List[str]:
        """Return the list of selected tag names in order."""
        return self.selected_tags if self.selected_tags else []

    def get_selected_records(self, template_type: str = 'vertical') -> List[Dict[str, Any]]:
        """Get selected records from the DataFrame, ordered by lineage."""
        try:
            # Get selected tags in the order they were selected
            selected_tags = list(self.selected_tags)
            if not selected_tags:
                logger.warning("No tags selected")
                return []
            
            logger.debug(f"Selected tags: {selected_tags}")
            
            # Build a mapping from normalized product names to canonical names
            product_name_col = 'ProductName'  # The actual column name in the DataFrame
            if product_name_col not in self.df.columns:
                possible_cols = ['Product Name*', 'Product Name', 'Description']
                product_name_col = next((col for col in possible_cols if col in self.df.columns), None)
                if not product_name_col:
                    logger.error(f"Product name column not found. Available columns: {list(self.df.columns)}")
                    return []
            
            canonical_map = {normalize_name(name): name for name in self.df[product_name_col]}
            logger.debug(f"Canonical map sample: {dict(list(canonical_map.items())[:5])}")
            
            # Map incoming selected tags to canonical names
            canonical_selected = [canonical_map.get(normalize_name(tag)) for tag in selected_tags if canonical_map.get(normalize_name(tag))]
            logger.debug(f"Selected tags: {selected_tags}")
            logger.debug(f"Canonical selected tags: {canonical_selected}")
            
            # Fallback: try case-insensitive and whitespace-insensitive matching if no canonical matches
            if not canonical_selected:
                logger.warning("No canonical matches for selected tags, trying fallback matching...")
                available_names = list(self.df[product_name_col])
                fallback_selected = []
                for tag in selected_tags:
                    tag_norm = tag.strip().lower().replace(' ', '')
                    for name in available_names:
                        name_norm = str(name).strip().lower().replace(' ', '')
                        if tag_norm == name_norm:
                            fallback_selected.append(name)
                            break
                canonical_selected = fallback_selected
                logger.debug(f"Fallback canonical selected tags: {canonical_selected}")
            
            if not canonical_selected:
                logger.warning("No canonical matches for selected tags after fallback")
                logger.warning(f"Available canonical keys (sample): {list(canonical_map.keys())[:10]}")
                normalized_selected = [normalize_name(tag) for tag in selected_tags]
                logger.warning(f"Normalized selected tags: {normalized_selected}")
                logger.warning(f"Available product names: {list(self.df[product_name_col])[:10]}")
                return []
            
            logger.debug(f"Canonical selected tags: {canonical_selected}")
            
            # Filter DataFrame to only include selected records by canonical ProductName
            filtered_df = self.df[self.df[product_name_col].isin(canonical_selected)]
            logger.debug(f"Found {len(filtered_df)} matching records")
            
            # Convert to list of dictionaries
            records = filtered_df.to_dict('records')
            logger.debug(f"Converted to {len(records)} records")
            
            # Sort records by lineage order, then by the order they appear in selected_tags
            lineage_order = [
                'SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA',
                'HYBRID/INDICA', 'CBD', 'MIXED', 'PARAPHERNALIA'
            ]
            
            def get_lineage(rec):
                lineage = str(rec.get('Lineage', '')).upper()
                return lineage if lineage in lineage_order else 'MIXED'
            
            def get_selected_order(rec):
                product_name = rec.get(product_name_col, '').strip()
                # Try exact match first
                try:
                    return selected_tags.index(product_name)
                except ValueError:
                    # Try case-insensitive match
                    product_name_lower = product_name.lower()
                    for i, tag in enumerate(selected_tags):
                        if tag.lower() == product_name_lower:
                            return i
                    return len(selected_tags)  # Put unknown tags at the end
            
            # Sort by selected order only (respecting user's drag-and-drop order)
            records_sorted = sorted(records, key=lambda r: get_selected_order(r))
            
            processed_records = []
            
            for record in records_sorted:
                try:
                    # Use the correct product name column
                    product_name = record.get(product_name_col, '').strip()
                    # Use the calculated Description field (which is processed from Product Name*)
                    description = record.get('Description', '')
                    if not description:
                        description = product_name or record.get(product_name_col, '')
                    product_type = record.get('Product Type*', '').strip().lower()
                    
                    # Get ratio text and ensure it's a string
                    ratio_text = str(record.get('Ratio', '')).strip()
                    
                    # Define classic types
                    classic_types = [
                        "flower", "pre-roll", "infused pre-roll", "concentrate", 
                        "solventless concentrate", "vape cartridge", "rso/co2 tankers"
                    ]
                    
                    # For classic types, ensure proper ratio format
                    if product_type in classic_types:
                        # Check if we have a valid ratio, otherwise use default
                        if not ratio_text or ratio_text in ["", "CBD", "THC", "CBD:", "THC:", "CBD:\n", "THC:\n"]:
                            ratio_text = "THC:|BR|CBD:"
                        # If ratio contains THC/CBD values, use it directly
                        elif any(cannabinoid in ratio_text.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                            ratio_text = ratio_text  # Keep as is
                        # If it's a valid ratio format, use it
                        elif is_real_ratio(ratio_text):
                            ratio_text = ratio_text  # Keep as is
                        # Otherwise, use default THC:CBD format
                        else:
                            ratio_text = "THC:|BR|CBD:"
                    
                    # Don't apply ratio formatting here - let the template processor handle it
                    # For classic types (including RSO/CO2 Tankers), the template processor will handle the classic formatting
                    
                    # Ensure we have a valid ratio text
                    if not ratio_text:
                        if product_type in classic_types:
                            ratio_text = "THC:|BR|CBD:"
                        else:
                            ratio_text = ""
                    
                    product_name = make_nonbreaking_hyphens(product_name)
                    description = make_nonbreaking_hyphens(description)
                    
                    # Get DOH value without normalization
                    doh_value = str(record.get('DOH', '')).strip().upper()
                    logger.debug(f"Processing DOH value: {doh_value}")
                    
                    # Get original values
                    product_brand = record.get('Product Brand', '').upper()
                    
                    # If no brand name, try to extract from product name or use vendor
                    if not product_brand or product_brand.strip() == '':
                        product_name = record.get('ProductName', '') or record.get('Product Name*', '')
                        if product_name:
                            # Look for common brand patterns in product name
                            import re
                            # Pattern: product name followed by brand name (e.g., "White Widow CBG Platinum Distillate")
                            brand_patterns = [
                                r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                                r'(.+?)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                                r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)',
                            ]
                            
                            for pattern in brand_patterns:
                                match = re.search(pattern, product_name, re.IGNORECASE)
                                if match:
                                    # Extract the brand part (everything after the product name)
                                    full_match = match.group(0)
                                    product_part = match.group(1).strip()
                                    brand_part = full_match[len(product_part):].strip()
                                    if brand_part:
                                        product_brand = brand_part.upper()
                                        break
                        
                        # If still no brand, try vendor as fallback
                        if not product_brand or product_brand.strip() == '':
                            vendor = record.get('Vendor', '') or record.get('Vendor/Supplier*', '')
                            if vendor and vendor.strip() != '':
                                product_brand = vendor.strip().upper()
                    
                    original_lineage = str(record.get('Lineage', '')).upper()
                    original_product_strain = record.get('Product Strain', '')
                    
                    # For RSO/CO2 Tankers and Capsules, use Product Brand in place of Lineage
                    if product_type in ["rso/co2 tankers", "capsule"]:
                        final_lineage = product_brand if product_brand else original_lineage
                        final_product_strain = original_product_strain  # Keep Product Strain for CBD Blend/Mixed values
                    else:
                        # For other product types, use the actual Lineage value
                        final_lineage = original_lineage
                        final_product_strain = original_product_strain
                    
                    lineage_needs_centering = False  # Lineage should not be centered
                    
                    # Debug print for verification
                    print(f"Product: {product_name}, Type: {product_type}, Lineage: '{final_lineage}', ProductStrain: '{final_product_strain}'")
                    
                    # Debug ProductStrain logic
                    include_product_strain = (product_type in ["rso/co2 tankers", "capsule"] or product_type not in classic_types)
                    print(f"  ProductStrain logic: product_type='{product_type}', in special list={product_type in ['rso/co2 tankers', 'capsule']}, not in classic_types={product_type not in classic_types}, include_product_strain={include_product_strain}")
                    
                    # Extract AI and AK column values for THC and CBD
                    # Extract THC/CBD values from actual columns
                    # For THC: merge Total THC (AI) with THC test result (K), use highest value
                    total_thc_value = str(record.get('Total THC', '')).strip()
                    thca_value = str(record.get('THCA', '')).strip()
                    thc_test_result = str(record.get('THC test result', '')).strip()
                    
                    # Clean up THC test result value
                    if thc_test_result in ['nan', 'NaN', '']:
                        thc_test_result = ''
                    
                    # Convert to float for comparison, handling empty/invalid values
                    def safe_float(value):
                        if not value or value in ['nan', 'NaN', '']:
                            return 0.0
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0.0
                    
                    # Compare Total THC vs THC test result, use highest
                    total_thc_float = safe_float(total_thc_value)
                    thc_test_float = safe_float(thc_test_result)
                    thca_float = safe_float(thca_value)
                    
                    # For THC: Use the highest value among Total THC, THC test result, and THCA
                    # But if Total THC is 0 or empty, prefer THCA over THC test result
                    if total_thc_float > 0:
                        # Total THC has a valid value, compare with THC test result
                        if thc_test_float > total_thc_float:
                            ai_value = thc_test_result
                            logger.debug(f"Using THC test result ({thc_test_result}) over Total THC ({total_thc_value}) for product: {product_name}")
                        else:
                            ai_value = total_thc_value
                    else:
                        # Total THC is 0 or empty, compare THCA vs THC test result
                        if thca_float > 0 and thca_float >= thc_test_float:
                            ai_value = thca_value
                        elif thc_test_float > 0:
                            ai_value = thc_test_result
                        else:
                            ai_value = ''
                    
                    # For CBD: merge CBDA (AK) with CBD test result (L), use highest value
                    cbda_value = str(record.get('CBDA', '')).strip()
                    cbd_test_result = str(record.get('CBD test result', '')).strip()
                    
                    # Clean up CBD test result value
                    if cbd_test_result in ['nan', 'NaN', '']:
                        cbd_test_result = ''
                    
                    # Compare CBDA vs CBD test result, use highest
                    cbda_float = safe_float(cbda_value)
                    cbd_test_float = safe_float(cbd_test_result)
                    
                    if cbd_test_float > cbda_float:
                        ak_value = cbd_test_result
                        logger.debug(f"Using CBD test result ({cbd_test_result}) over CBDA ({cbda_value}) for product: {product_name}")
                    else:
                        ak_value = cbda_value
                    
                    # Clean up the values (remove 'nan', empty strings, etc.)
                    if ai_value in ['nan', 'NaN', '']:
                        ai_value = ''
                    if ak_value in ['nan', 'NaN', '']:
                        ak_value = ''
                    
                    # Get vendor information
                    vendor = record.get('Vendor', '') or record.get('Vendor/Supplier*', '')
                    if pd.isna(vendor) or str(vendor).lower() == 'nan':
                        vendor = ''
                    
                    # Build the processed record with raw values (no markers)
                    processed = {
                        'ProductName': product_name,  # Keep this for compatibility
                        product_name_col: product_name,  # Also store with original column name
                        'Description': description,
                        'WeightUnits': record.get('JointRatio', '') if product_type in {"pre-roll", "infused pre-roll"} else self._format_weight_units(record),
                        'ProductBrand': product_brand,
                        'Price': str(record.get('Price', '')).strip(),
                        'Lineage': wrap_with_marker(unwrap_marker(str(final_lineage), "LINEAGE"), "LINEAGE"),
                        'DOH': doh_value,  # Keep DOH as raw value
                        'Ratio_or_THC_CBD': ratio_text,  # Use the processed ratio_text for all product types
                        'ProductStrain': wrap_with_marker(final_product_strain, "PRODUCTSTRAIN") if include_product_strain else '',
                        'ProductType': record.get('Product Type*', ''),
                        'Ratio': str(record.get('Ratio', '')).strip(),
                        'THC': wrap_with_marker(ai_value, "THC"),  # AI column for THC
                        'CBD': wrap_with_marker(ak_value, "CBD"),  # AK column for CBD
                        'AI': ai_value,  # Total THC or THCA value for THC
                        'AJ': str(record.get('THCA', '')).strip(),  # THCA value for alternative THC
                        'AK': ak_value,  # CBDA value for CBD
                        'Vendor': vendor,  # Add vendor information
                    }
                    # Ensure leading space before hyphen is a non-breaking space to prevent Word from stripping it
                    joint_ratio = record.get('JointRatio', '')
                    # Handle NaN values properly
                    if pd.isna(joint_ratio) or joint_ratio == 'nan' or joint_ratio == 'NaN':
                        joint_ratio = ''
                    elif joint_ratio.startswith(' -'):
                        joint_ratio = ' -\u00A0' + joint_ratio[2:]
                    processed['JointRatio'] = joint_ratio
                    
                    logger.info(f"Rendered label for record: {product_name if product_name else '[NO NAME]'}")
                    logger.debug(f"Processed record DOH value: {processed['DOH']}")
                    logger.debug(f"Product Type: {product_type}, Classic: {product_type in classic_types}")
                    logger.debug(f"Original Lineage: {original_lineage}, Final Lineage: {final_lineage}")
                    logger.debug(f"Original Product Strain: {original_product_strain}, Final Product Strain: {final_product_strain}")
                    logger.debug(f"Lineage needs centering: {lineage_needs_centering}")
                    processed_records.append(processed)
                except Exception as e:
                    logger.error(f"Error processing record {product_name}: {str(e)}")
                    continue
                
            # Debug log the final processed records
            logger.debug(f"Processed {len(processed_records)} records")
            for record in processed_records:
                logger.debug(f"Processed record: {record.get('ProductName', 'NO NAME')}")
                logger.debug(f"Record DOH value: {record.get('DOH', 'NO DOH')}")
            
            return processed_records
        except Exception as e:
            logger.error(f"Error in get_selected_records: {str(e)}")
            return []

    def _format_weight_units(self, record):
        # Handle pandas Series and NA values properly
        def safe_get_value(value, default=''):
            if value is None or pd.isna(value):
                return default
            if isinstance(value, pd.Series):
                if pd.isna(value).any():
                    return default
                value = value.iloc[0] if len(value) > 0 else default
            return str(value).strip()
        
        weight_val = safe_get_value(record.get('Weight*', None))
        units_val = safe_get_value(record.get('Units', ''))
        product_type = safe_get_value(record.get('Product Type*', '')).lower()
        
        # Debug: Log first few records
        if hasattr(self, '_debug_count'):
            self._debug_count += 1
        else:
            self._debug_count = 1
            
        if self._debug_count <= 5:  # Log first 5 records for debugging
            self.logger.info(f"Record {self._debug_count}: weight_val={weight_val} (type: {type(weight_val)}), units_val={units_val} (type: {type(units_val)}), product_type={product_type}")
        
        edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
        preroll_types = {"pre-roll", "infused pre-roll"}

        # For pre-rolls and infused pre-rolls, use JointRatio if available
        if product_type in preroll_types:
            joint_ratio = safe_get_value(record.get('JointRatio', ''))
            
            # Check if JointRatio is valid (not NaN, not empty, and looks like a pack format)
            if (joint_ratio and 
                joint_ratio != 'nan' and 
                joint_ratio != 'NaN' and 
                not pd.isna(joint_ratio) and
                ('g' in str(joint_ratio).lower() and 'pack' in str(joint_ratio).lower())):
                
                # Use the JointRatio as-is for pre-rolls
                result = str(joint_ratio)
            else:
                # For pre-rolls with invalid JointRatio, generate from Weight
                weight_val = safe_get_value(record.get('Weight*', ''))
                if weight_val and weight_val not in ['nan', 'NaN'] and not pd.isna(weight_val):
                    try:
                        weight_float = float(weight_val)
                        result = f"{weight_float}g"
                    except (ValueError, TypeError):
                        result = ""
                else:
                    result = ""
        else:
            try:
                weight_val = float(weight_val) if weight_val not in (None, '', 'nan') else None
            except Exception:
                weight_val = None

            if product_type in edible_types and units_val in {"g", "grams"} and weight_val is not None:
                weight_val = weight_val * 0.03527396195
                units_val = "oz"

            # Now we can safely check the values since they've been processed by safe_get_value
            if weight_val is not None and units_val:
                weight_str = f"{weight_val:.2f}".rstrip("0").rstrip(".")
                result = f"{weight_str}{units_val}"
            elif weight_val is not None:
                result = str(weight_val)
            elif units_val:
                result = str(units_val)
            else:
                result = ""
        
        # Debug: Log result for first few records
        if self._debug_count <= 5:
            self.logger.info(f"Record {self._debug_count} result: '{result}'")
            
        return result

    def get_dynamic_filter_options(self, current_filters: Dict[str, str]) -> Dict[str, list]:
        if self.df is None:
            # Return empty options if no data is loaded
            return {
                "vendor": [],
                "brand": [],
                "productType": [],
                "lineage": [],
                "weight": [],
                "strain": [],
                "doh": [],
                "highCbd": []
            }
        df = self.df.copy()
        filter_map = {
            "vendor": "Vendor",
            "brand": "Product Brand",
            "productType": "Product Type*",
            "lineage": "Lineage",
            "weight": "Weight*",  # Changed from "CombinedWeight" to "Weight*"
            "strain": "Product Strain",
            "doh": "DOH",
            "highCbd": "Product Type*"  # Will be processed specially for high CBD detection
        }
        options = {}
        import math
        def clean_list(lst):
            return ['' if (v is None or (isinstance(v, float) and math.isnan(v))) else v for v in lst]
        # For each filter type, generate options by applying all other filters except itself
        for filter_key, col in filter_map.items():
            temp_df = df.copy()
            # Apply all other filters except the current one
            for key, value in current_filters.items():
                if key == filter_key:
                    continue  # Skip filtering by itself
                if value and value != "All":
                    filter_col = filter_map.get(key)
                    if filter_col and filter_col in temp_df.columns:
                        temp_df = temp_df[
                            temp_df[filter_col].astype(str).str.lower().str.strip() == value.lower().strip()
                        ]
            # Get unique values for this filter type
            if col in temp_df.columns:
                if filter_key == "weight":
                    # For weight, use the properly formatted weight with units
                    values = []
                    for _, row in temp_df.iterrows():
                        # Convert row to dict for _format_weight_units
                        row_dict = row.to_dict()
                        weight_with_units = self._format_weight_units(row_dict)
                        if weight_with_units and weight_with_units.strip():
                            weight_str = weight_with_units.strip()
                            
                            # Only include values that look like actual weights (with units like g, oz, mg)
                            # Exclude THC/CBD content, ratios, and other non-weight content
                            import re
                            weight_pattern = re.compile(r'^\d+\.?\d*\s*(g|oz|mg|grams?|ounces?)$', re.IGNORECASE)
                            
                            if weight_pattern.match(weight_str):
                                values.append(weight_str)
                            elif not any(keyword in weight_str.lower() for keyword in ['thc', 'cbd', 'ratio', '|br|', ':']):
                                # If it doesn't match weight pattern but also doesn't contain THC/CBD keywords, include it
                                values.append(weight_str)
                    
                    # Debug: Log what weight values are being generated
                    if values:
                        self.logger.info(f"Weight filter values generated: {values[:5]}...")  # Log first 5 values
                    else:
                        self.logger.warning("No weight values generated for filter dropdown")
                else:
                    values = temp_df[col].dropna().unique().tolist()
                    values = [str(v) for v in values if str(v).strip()]
                
                # Exclude unwanted product types from dropdown and apply product type normalization
                if filter_key == "productType":
                    filtered_values = []
                    for v in values:
                        v_lower = v.strip().lower()
                        if ("trade sample" in v_lower or "deactivated" in v_lower):
                            continue
                        # Apply product type normalization (same as TYPE_OVERRIDES)
                        normalized_v = TYPE_OVERRIDES.get(v_lower, v)
                        filtered_values.append(normalized_v)
                    values = filtered_values
                
                # Special processing for DOH filter
                elif filter_key == "doh":
                    # Only include "YES" and "NO" values, normalize case
                    filtered_values = []
                    for v in values:
                        v_upper = v.strip().upper()
                        if v_upper in ["YES", "NO"]:
                            filtered_values.append(v_upper)
                    values = filtered_values
                
                # Special processing for High CBD filter
                elif filter_key == "highCbd":
                    # Check if any product types start with "high cbd"
                    has_high_cbd = any(v.strip().lower().startswith('high cbd') for v in values)
                    values = ["High CBD Products", "Non-High CBD Products"] if has_high_cbd else ["Non-High CBD Products"]
                
                # Remove duplicates and sort
                values = list(set(values))
                values.sort()
                options[filter_key] = clean_list(values)
            else:
                options[filter_key] = []
        
        return options

    @staticmethod
    def parse_weight_str(w, u=None):
        import re
        w = str(w).strip() if w is not None else ''
        u = str(u).strip().lower() if u is not None else ''
        # Try to extract numeric value and units from weight or weightWithUnits
        match = re.match(r"([\d.]+)\s*(g|oz)?", w.lower())
        if not match and u:
            match = re.match(r"([\d.]+)\s*(g|oz)?", u)
        if match:
            val = float(match.group(1))
            unit = match.group(2)
            if unit == 'oz':
                val = val * 28.3495
            return val
        return float('inf')  # Non-numeric weights go last

    def update_lineage_in_database(self, strain_name: str, new_lineage: str):
        """Update lineage for a specific strain in the database."""
        if not ENABLE_LINEAGE_PERSISTENCE:
            self.logger.warning("Lineage persistence is disabled")
            return False
        
        try:
            from .product_database import ProductDatabase
            product_db = ProductDatabase()
            
            # Update strain with sovereign lineage
            strain_id = product_db.add_or_update_strain(strain_name, new_lineage, sovereign=True)
            
            if strain_id:
                self.logger.info(f"Updated lineage for strain '{strain_name}' to '{new_lineage}' in database")
                
                # Note: Only updating database, not Excel file (for performance)
                # Excel file is source data, database is authoritative for lineage
                
                return True
            else:
                self.logger.error(f"Failed to update lineage for strain '{strain_name}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating lineage for strain '{strain_name}': {e}")
            return False

    def batch_update_lineages(self, lineage_updates: Dict[str, str]):
        """Batch update multiple lineage changes in the database."""
        if not ENABLE_LINEAGE_PERSISTENCE:
            self.logger.warning("Lineage persistence is disabled")
            return False
        
        try:
            from .product_database import ProductDatabase
            product_db = ProductDatabase()
            
            success_count = 0
            total_count = len(lineage_updates)
            
            for strain_name, new_lineage in lineage_updates.items():
                try:
                    strain_id = product_db.add_or_update_strain(strain_name, new_lineage, sovereign=True)
                    if strain_id:
                        success_count += 1
                        
                        # Note: Only updating database, not Excel file (for performance)
                        # Excel file is source data, database is authoritative for lineage
                                
                except Exception as e:
                    self.logger.error(f"Error updating lineage for strain '{strain_name}': {e}")
            
            self.logger.info(f"Batch lineage update complete: {success_count}/{total_count} successful")
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Error in batch lineage update: {e}")
            return False

    def get_lineage_suggestions(self, strain_name: str) -> Dict[str, Any]:
        """Get lineage suggestions for a strain from the database."""
        if not ENABLE_LINEAGE_PERSISTENCE:
            return {"suggestion": None, "confidence": 0.0, "reason": "Lineage persistence disabled"}
        
        try:
            from .product_database import ProductDatabase
            product_db = ProductDatabase()
            
            return product_db.validate_and_suggest_lineage(strain_name)
            
        except Exception as e:
            self.logger.error(f"Error getting lineage suggestions for strain '{strain_name}': {e}")
            return {"suggestion": None, "confidence": 0.0, "reason": f"Error: {e}"}

    def ensure_lineage_persistence(self):
        """Ensure all lineage changes are persisted to the database."""
        if not ENABLE_LINEAGE_PERSISTENCE:
            self.logger.warning("Lineage persistence is disabled")
            return {"message": "Lineage persistence disabled", "updated_count": 0}
        
        try:
            if not hasattr(self, 'df') or self.df is None:
                return {"message": "No data loaded", "updated_count": 0}
            
            # Get all classic type products with strains
            from src.core.constants import CLASSIC_TYPES
            classic_mask = self.df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
            classic_df = self.df[classic_mask]
            
            if classic_df.empty:
                return {"message": "No classic type products found", "updated_count": 0}
            
            # Group by strain and get lineage information
            strain_groups = classic_df.groupby('Product Strain')
            updated_count = 0
            
            from .product_database import ProductDatabase
            product_db = ProductDatabase()
            
            for strain_name, group in strain_groups:
                if not strain_name or pd.isna(strain_name):
                    continue
                
                # Get the most common lineage for this strain
                lineage_counts = group['Lineage'].value_counts()
                if not lineage_counts.empty:
                    most_common_lineage = lineage_counts.index[0]
                    
                    # Update strain in database
                    if most_common_lineage and str(most_common_lineage).strip():
                        strain_id = product_db.add_or_update_strain(strain_name, most_common_lineage, sovereign=True)
                        if strain_id:
                            updated_count += 1
            
            message = f"Ensured lineage persistence for {updated_count} strains"
            self.logger.info(message)
            
            return {"message": message, "updated_count": updated_count}
            
        except Exception as e:
            error_msg = f"Error ensuring lineage persistence: {e}"
            self.logger.error(error_msg)
            return {"message": error_msg, "updated_count": 0}

    def save_data(self, file_path: Optional[str] = None) -> bool:
        """Save the current DataFrame to an Excel file."""
        try:
            if self.df is None or self.df.empty:
                self.logger.warning("No data to save")
                return False
            
            # Use the current file path if none provided
            if file_path is None:
                file_path = self.current_file_path
            
            if not file_path:
                self.logger.error("No file path specified for saving")
                return False
            
            # Save to Excel file
            self.df.to_excel(file_path, index=False, engine='openpyxl')
            self.logger.info(f"Data saved successfully to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            self.logger.error(traceback.format_exc())
            return False

    def update_lineage_in_current_data(self, tag_name: str, new_lineage: str) -> bool:
        """Update lineage for a specific product in the current data."""
        try:
            if self.df is None:
                self.logger.error("No data loaded")
                return False
            
            # Find the tag in the DataFrame and update its lineage
            self.logger.info(f"Looking for tag: '{tag_name}'")
            
            # Try different column names for product names
            product_name_columns = ['ProductName', 'Product Name*', 'Product Name']
            mask = None
            
            for col in product_name_columns:
                if col in self.df.columns:
                    mask = self.df[col] == tag_name
                    if mask.any():
                        break
            
            if mask is None or not mask.any():
                self.logger.error(f"Tag '{tag_name}' not found in any product name column")
                return False
            
            # Get the original lineage for logging
            original_lineage = 'Unknown'
            try:
                original_lineage = self.df.loc[mask, 'Lineage'].iloc[0]
            except (IndexError, KeyError):
                original_lineage = 'Unknown'
            
            # Check if this is a paraphernalia product and enforce PARAPHERNALIA lineage
            try:
                product_type = self.df.loc[mask, 'Product Type*'].iloc[0]
                if str(product_type).strip().lower() == 'paraphernalia':
                    new_lineage = 'PARAPHERNALIA'
                    self.logger.info(f"Enforcing PARAPHERNALIA lineage for paraphernalia product: {tag_name}")
                    
                    # Ensure PARAPHERNALIA is in the categorical categories
                    if 'Lineage' in self.df.columns and hasattr(self.df['Lineage'], 'cat'):
                        current_categories = list(self.df['Lineage'].cat.categories)
                        if 'PARAPHERNALIA' not in current_categories:
                            self.df['Lineage'] = self.df['Lineage'].cat.add_categories(['PARAPHERNALIA'])
            except (IndexError, KeyError):
                pass  # If we can't determine product type, proceed with user's choice
            
            # Update the lineage in the DataFrame
            self.df.loc[mask, 'Lineage'] = new_lineage
            
            self.logger.info(f"Updated lineage for tag '{tag_name}' from '{original_lineage}' to '{new_lineage}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating lineage in current data: {e}")
            return False

    def get_strain_name_for_product(self, tag_name: str) -> Optional[str]:
        """Get the strain name for a specific product."""
        try:
            if self.df is None:
                return None
            
            # Try different column names for product names
            product_name_columns = ['ProductName', 'Product Name*', 'Product Name']
            mask = None
            
            for col in product_name_columns:
                if col in self.df.columns:
                    mask = self.df[col] == tag_name
                    if mask.any():
                        break
            
            if mask is None or not mask.any():
                return None
            
            # Get the strain name
            try:
                strain_name = self.df.loc[mask, 'Product Strain'].iloc[0]
                return str(strain_name) if strain_name else None
            except (IndexError, KeyError):
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting strain name for product '{tag_name}': {e}")
            return None

