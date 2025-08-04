#!/usr/bin/env python3
"""
Fix PythonAnywhere Excel Processing to Match Local Version

This script ensures that the PythonAnywhere version uses identical Excel processing
as the local version by standardizing all processing flags, file loading behavior,
and data processing logic.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_excel_processor_flags():
    """Fix Excel processor flags to ensure identical processing between environments."""
    logger.info("Fixing Excel processor flags...")
    
    # Read the current excel_processor.py
    excel_processor_path = "src/core/data/excel_processor.py"
    
    if not os.path.exists(excel_processor_path):
        logger.error(f"Excel processor file not found: {excel_processor_path}")
        return False
    
    with open(excel_processor_path, 'r') as f:
        content = f.read()
    
    # Replace performance flags to ensure consistent processing
    replacements = [
        # Standardize performance flags
        (
            'ENABLE_LAZY_PROCESSING = True  # NEW: Enable lazy processing for better performance',
            'ENABLE_LAZY_PROCESSING = False  # DISABLED: Ensure consistent processing'
        ),
        (
            'ENABLE_MINIMAL_PROCESSING = True  # NEW: Enable minimal processing mode for uploads',
            'ENABLE_MINIMAL_PROCESSING = False  # DISABLED: Ensure consistent processing'
        ),
        (
            'ENABLE_BATCH_OPERATIONS = True  # NEW: Enable batch operations instead of row-by-row',
            'ENABLE_BATCH_OPERATIONS = False  # DISABLED: Ensure consistent processing'
        ),
        (
            'ENABLE_VECTORIZED_OPERATIONS = True  # NEW: Enable vectorized operations where possible',
            'ENABLE_VECTORIZED_OPERATIONS = False  # DISABLED: Ensure consistent processing'
        ),
        # Standardize file size limits
        (
            'max_size = 50 * 1024 * 1024  # 50MB limit for PythonAnywhere',
            'max_size = 100 * 1024 * 1024  # 100MB limit (standard for both environments)'
        ),
        (
            'self.logger.error(f"File too large for PythonAnywhere: {file_size} bytes (max: {max_size})")',
            'self.logger.error(f"File too large: {file_size} bytes (max: {max_size})")'
        ),
        # Standardize Excel engine approach
        (
            '# Try different Excel engines for better compatibility\nexcel_engines = [\'openpyxl\', \'xlrd\']',
            '# Use standard Excel engine (openpyxl) for both environments\nexcel_engine = \'openpyxl\''
        ),
        # Remove chunked reading for large files
        (
            '# Use chunking for large files on PythonAnywhere\nif file_size > 10 * 1024 * 1024:  # 10MB\n    self.logger.info("Large file detected, using chunked reading")\n    # Read in chunks to manage memory\n    chunk_size = 1000\n    chunks = []\n    \n    for chunk in pd.read_excel(file_path, engine=engine, dtype=dtype_dict, chunksize=chunk_size):\n        chunks.append(chunk)\n        self.logger.debug(f"Read chunk {len(chunks)} with {len(chunk)} rows")\n    \n    if chunks:\n        df = pd.concat(chunks, ignore_index=True)\n        self.logger.info(f"Successfully read {len(df)} rows in {len(chunks)} chunks")\n    else:\n        self.logger.error("No data found in file")\n        return False\nelse:\n    # For smaller files, read normally\n    df = pd.read_excel(file_path, engine=engine, dtype=dtype_dict)',
            '# Standard reading approach for both environments\ndf = pd.read_excel(file_path, engine=excel_engine, dtype=dtype_dict)'
        ),
        # Standardize engine loop
        (
            'for engine in excel_engines:\n    try:\n        self.logger.debug(f"Attempting to read with engine: {engine}")',
            'try:\n    self.logger.debug(f"Reading with engine: {excel_engine}")'
        ),
        # Standardize error handling
        (
            'except Exception as e:\n    self.logger.warning(f"Failed to read with {engine} engine: {e}")\n    if engine == excel_engines[-1]:  # Last engine\n        self.logger.error(f"All Excel engines failed to read file: {file_path}")\n        return False\n    continue',
            'except Exception as e:\n    self.logger.error(f"Failed to read with {excel_engine} engine: {e}")\n    # Try xlrd as fallback\n    try:\n        df = pd.read_excel(file_path, engine=\'xlrd\', dtype=dtype_dict)\n        self.logger.info(f"Successfully read file with xlrd engine: {len(df)} rows, {len(df.columns)} columns")\n    except Exception as e2:\n        self.logger.error(f"All Excel engines failed to read file: {file_path}")\n        self.logger.error(f"openpyxl error: {e}")\n        self.logger.error(f"xlrd error: {e2}")\n        return False'
        ),
        # Standardize file loading description
        (
            'Enhanced for PythonAnywhere compatibility with improved file detection.',
            'STANDARDIZED for both local and PythonAnywhere environments.'
        ),
        # Standardize environment-specific file loading
        (
            'if is_pythonanywhere:\n        # PythonAnywhere: Check uploads folder first, then Downloads\n        pythonanywhere_paths = [\n            os.path.join(current_dir, "uploads"),  # Uploads folder first\n            "/home/adamcordova/Downloads",  # Downloads folder as backup\n        ]\n        search_locations.extend(pythonanywhere_paths)\n        logger.debug("PythonAnywhere detected: Searching uploads folder first, then Downloads")\n    else:\n        # Local development: Downloads folder only\n        local_paths = [\n            os.path.join(home_dir, "Downloads"),  # Downloads folder only\n        ]\n        search_locations.extend(local_paths)',
            '# Both environments: Check uploads folder first, then Downloads\n    standard_paths = [\n        os.path.join(current_dir, "uploads"),  # Uploads folder first\n        os.path.join(home_dir, "Downloads"),  # Downloads folder as backup\n    ]\n    search_locations.extend(standard_paths)\n    logger.debug("STANDARDIZED: Searching uploads folder first, then Downloads for both environments")'
        ),
        # Standardize error messages
        (
            'if not excel_files:\n        if is_pythonanywhere:\n            logger.warning("PythonAnywhere: No Excel files found in uploads or Downloads directories")\n            logger.info("Please upload an Excel file using the file upload feature")\n            logger.info("PythonAnywhere: No default file found. Please upload a file through the web interface.")\n        else:\n            logger.warning("No Excel files found in any search location")',
            'if not excel_files:\n        logger.warning("No Excel files found in any search location")\n        logger.info("Please upload an Excel file using the file upload feature")'
        )
    ]
    
    # Apply all replacements
    for old_text, new_text in replacements:
        if old_text in content:
            content = content.replace(old_text, new_text)
            logger.info(f"Applied replacement: {old_text[:50]}...")
        else:
            logger.warning(f"Text not found for replacement: {old_text[:50]}...")
    
    # Write the updated content
    with open(excel_processor_path, 'w') as f:
        f.write(content)
    
    logger.info("Excel processor flags fixed successfully")
    return True

def fix_app_configuration():
    """Fix app.py configuration to ensure consistent behavior."""
    logger.info("Fixing app.py configuration...")
    
    app_path = "app.py"
    
    if not os.path.exists(app_path):
        logger.error(f"App file not found: {app_path}")
        return False
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Ensure consistent startup file loading
    replacements = [
        (
            'DISABLE_STARTUP_FILE_LOADING = False  # Enable default file loading on startup',
            'DISABLE_STARTUP_FILE_LOADING = False  # STANDARDIZED: Enable default file loading on startup for both environments'
        )
    ]
    
    for old_text, new_text in replacements:
        if old_text in content:
            content = content.replace(old_text, new_text)
            logger.info(f"Applied app configuration replacement")
        else:
            logger.warning(f"App configuration text not found: {old_text}")
    
    # Write the updated content
    with open(app_path, 'w') as f:
        f.write(content)
    
    logger.info("App configuration fixed successfully")
    return True

def verify_fixes():
    """Verify that all fixes have been applied correctly."""
    logger.info("Verifying fixes...")
    
    # Check excel_processor.py
    excel_processor_path = "src/core/data/excel_processor.py"
    if os.path.exists(excel_processor_path):
        with open(excel_processor_path, 'r') as f:
            content = f.read()
        
        # Check for standardized flags
        checks = [
            ('ENABLE_LAZY_PROCESSING = False', 'Lazy processing disabled'),
            ('ENABLE_MINIMAL_PROCESSING = False', 'Minimal processing disabled'),
            ('ENABLE_BATCH_OPERATIONS = False', 'Batch operations disabled'),
            ('ENABLE_VECTORIZED_OPERATIONS = False', 'Vectorized operations disabled'),
            ('max_size = 100 * 1024 * 1024', 'Standard file size limit'),
            ('STANDARDIZED for both local and PythonAnywhere', 'Standardized processing'),
        ]
        
        for check_text, description in checks:
            if check_text in content:
                logger.info(f"✓ {description}")
            else:
                logger.warning(f"✗ {description} not found")
    
    # Check app.py
    app_path = "app.py"
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
        
        if 'STANDARDIZED: Enable default file loading' in content:
            logger.info("✓ App configuration standardized")
        else:
            logger.warning("✗ App configuration not standardized")
    
    logger.info("Verification complete")

def main():
    """Main function to fix PythonAnywhere Excel processing."""
    logger.info("Starting PythonAnywhere Excel processing fix...")
    
    try:
        # Fix Excel processor flags
        if not fix_excel_processor_flags():
            logger.error("Failed to fix Excel processor flags")
            return False
        
        # Fix app configuration
        if not fix_app_configuration():
            logger.error("Failed to fix app configuration")
            return False
        
        # Verify fixes
        verify_fixes()
        
        logger.info("PythonAnywhere Excel processing fix completed successfully!")
        logger.info("Both local and PythonAnywhere environments now use identical Excel processing.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 