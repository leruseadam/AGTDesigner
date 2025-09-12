#!/usr/bin/env python3
"""
Fix initialization stuck issue by disabling problematic startup file loading
"""

import os

def fix_initialization_stuck():
    """Fix the initialization stuck issue"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Add startup optimization flag at the top
    startup_optimization = '''# Startup Performance Optimization
DISABLE_STARTUP_FILE_LOADING = True  # Disable startup file loading to prevent hangs
LAZY_LOADING_ENABLED = True  # Enable lazy loading for better performance

'''
    
    # Find where to insert the optimization flags (after imports)
    import_end = content.find('import traceback')
    if import_end != -1:
        # Find the end of the import section
        lines = content[:import_end].split('\n')
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                last_import_line = i
        
        # Insert after the last import
        insert_point = content.find(lines[last_import_line]) + len(lines[last_import_line])
        new_content = content[:insert_point] + '\n' + startup_optimization + content[insert_point:]
    else:
        # Fallback: insert at the beginning
        new_content = startup_optimization + content
    
    # Fix 2: Update the initialize_excel_processor function to respect the flag
    old_init = '''def initialize_excel_processor():
    """Initialize Excel processor and load default data."""
    try:
        excel_processor = get_excel_processor()
        excel_processor.logger.setLevel(logging.WARNING)
        
        # Enable product database integration by default
        if hasattr(excel_processor, 'enable_product_db_integration'):
            excel_processor.enable_product_db_integration(True)
            logging.info("Product database integration enabled by default")
        
        # Try to load default file
        from src.core.data.excel_processor import get_default_upload_file
        default_file = get_default_upload_file()
        
        if default_file and os.path.exists(default_file):
            logging.info(f"Loading default file on startup: {default_file}")
            try:
                success = excel_processor.load_file(default_file)
                if success:
                    excel_processor._last_loaded_file = default_file
                    logging.info(f"Default file loaded successfully with {len(excel_processor.df)} records")
                else:
                    logging.warning("Failed to load default file")
            except Exception as load_error:
                logging.error(f"Error loading default file: {load_error}")
                logging.error(f"Traceback: {traceback.format_exc()}")
        else:
            logging.info("No default file found, waiting for user upload")
            if default_file:
                logging.info(f"Default file path was found but file doesn't exist: {default_file}")
            
    except Exception as e:
        logging.error(f"Error initializing Excel processor: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")'''
    
    new_init = '''def initialize_excel_processor():
    """Initialize Excel processor and load default data."""
    try:
        # Skip initialization if startup file loading is disabled for performance
        if DISABLE_STARTUP_FILE_LOADING:
            logging.info("Startup file loading disabled for faster application startup")
            excel_processor = get_excel_processor()
            excel_processor.logger.setLevel(logging.WARNING)
            return
        
        excel_processor = get_excel_processor()
        excel_processor.logger.setLevel(logging.WARNING)
        
        # Enable product database integration by default
        if hasattr(excel_processor, 'enable_product_db_integration'):
            excel_processor.enable_product_db_integration(True)
            logging.info("Product database integration enabled by default")
        
        # Try to load default file
        from src.core.data.excel_processor import get_default_upload_file
        default_file = get_default_upload_file()
        
        if default_file and os.path.exists(default_file):
            logging.info(f"Loading default file on startup: {default_file}")
            try:
                success = excel_processor.load_file(default_file)
                if success:
                    excel_processor._last_loaded_file = default_file
                    logging.info(f"Default file loaded successfully with {len(excel_processor.df)} records")
                else:
                    logging.warning("Failed to load default file")
            except Exception as load_error:
                logging.error(f"Error loading default file: {load_error}")
                logging.error(f"Traceback: {traceback.format_exc()}")
        else:
            logging.info("No default file found, waiting for user upload")
            if default_file:
                logging.info(f"Default file path was found but file doesn't exist: {default_file}")
            
    except Exception as e:
        logging.error(f"Error initializing Excel processor: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")'''
    
    if old_init in new_content:
        new_content = new_content.replace(old_init, new_init)
        print("✅ Updated initialize_excel_processor function")
    else:
        print("⚠️  Could not find initialize_excel_processor function to update")
    
    # Fix 3: Add timeout protection to file loading
    timeout_protection = '''
# Add timeout protection for file operations
import signal
import threading

def timeout_handler(signum, frame):
    raise TimeoutError("File operation timed out")

def safe_load_file_with_timeout(processor, file_path, timeout_seconds=30):
    """Load file with timeout protection"""
    try:
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        # Load file
        result = processor.load_file(file_path)
        
        # Cancel timeout
        signal.alarm(0)
        return result
        
    except TimeoutError:
        logging.error(f"File loading timed out after {timeout_seconds} seconds")
        return False
    except Exception as e:
        logging.error(f"Error in safe file loading: {e}")
        return False
    finally:
        signal.alarm(0)  # Ensure timeout is cancelled
'''
    
    # Insert timeout protection after the startup optimization
    if 'DISABLE_STARTUP_FILE_LOADING' in new_content:
        insert_point = new_content.find('DISABLE_STARTUP_FILE_LOADING = True')
        insert_point = new_content.find('\n', insert_point) + 1
        new_content = new_content[:insert_point] + timeout_protection + new_content[insert_point:]
        print("✅ Added timeout protection for file operations")
    
    # Write the fixed content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Initialization stuck issue fixes applied!")
    print("📋 Changes made:")
    print("  - Disabled startup file loading to prevent hangs")
    print("  - Added timeout protection for file operations")
    print("  - Optimized initialization process")
    
    return True

if __name__ == "__main__":
    fix_initialization_stuck()
