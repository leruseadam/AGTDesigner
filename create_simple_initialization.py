#!/usr/bin/env python3
"""
Create a simple initialization that won't get stuck on PythonAnywhere
"""

import os

def create_simple_initialization():
    """Create a simple initialization that bypasses problematic file loading"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a simple initialization function that won't get stuck
    simple_init = '''
def simple_initialize_excel_processor():
    """Simple initialization that won't get stuck - for PythonAnywhere"""
    try:
        logging.info("Simple initialization starting...")
        
        # Create Excel processor without loading any files
        excel_processor = get_excel_processor()
        excel_processor.logger.setLevel(logging.WARNING)
        
        # Initialize with empty DataFrame
        if not hasattr(excel_processor, 'df') or excel_processor.df is None:
            excel_processor.df = pd.DataFrame()
            logging.info("Initialized with empty DataFrame")
        
        # Disable product database integration for faster startup
        if hasattr(excel_processor, 'enable_product_db_integration'):
            excel_processor.enable_product_db_integration(False)
            logging.info("Product database integration disabled for startup performance")
        
        logging.info("Simple initialization completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error in simple initialization: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False
'''
    
    # Find where to insert the simple initialization function
    insert_location = content.find('def initialize_excel_processor():')
    
    if insert_location != -1:
        # Insert before the existing function
        new_content = content[:insert_location] + simple_init + '\n\n' + content[insert_location:]
    else:
        print("❌ Could not find initialize_excel_processor function")
        return False
    
    # Update the call to use simple initialization on PythonAnywhere
    old_call = 'initialize_excel_processor()'
    new_call = '''# Use simple initialization on PythonAnywhere to prevent hangs
if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    simple_initialize_excel_processor()
else:
    initialize_excel_processor()'''
    
    if old_call in new_content:
        new_content = new_content.replace(old_call, new_call)
        print("✅ Updated initialization call to use simple version on PythonAnywhere")
    else:
        print("⚠️  Could not find initialization call to update")
    
    # Write the updated file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Simple initialization created!")
    print("📋 Changes made:")
    print("  - Added simple_initialize_excel_processor function")
    print("  - Updated to use simple initialization on PythonAnywhere")
    print("  - Bypasses problematic file loading")
    
    return True

if __name__ == "__main__":
    create_simple_initialization()
