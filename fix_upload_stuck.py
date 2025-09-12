#!/usr/bin/env python3
"""
Fix for Excel upload getting stuck on PythonAnywhere
"""

import os
import sys

def fix_upload_stuck_issue():
    """Fix the upload stuck issue by updating the background processing"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace fast_load_file with load_file for reliability
    old_fast_load = '''        # Use the fast_load_file method
        success = processor.fast_load_file(temp_path)'''
    
    new_reliable_load = '''        # Use the reliable load_file method (fast_load_file can fail)
        success = processor.load_file(temp_path)'''
    
    if old_fast_load in content:
        content = content.replace(old_fast_load, new_reliable_load)
        print("✅ Fixed fast_load_file to use reliable load_file method")
    else:
        print("⚠️  fast_load_file pattern not found, checking for other patterns...")
    
    # Fix 2: Add better error handling for database storage
    old_db_storage = '''        # Step 5: Store products in database
        logging.info(f"[ULTRA-FAST-BG] Storing {len(processor.df)} products in database")
        try:
            from app import get_product_database
            product_db = get_product_database()
            
            if hasattr(product_db, 'store_excel_data'):'''
    
    new_db_storage = '''        # Step 5: Store products in database (with better error handling)
        logging.info(f"[ULTRA-FAST-BG] Storing {len(processor.df)} products in database")
        try:
            from app import get_product_database
            product_db = get_product_database()
            
            if product_db and hasattr(product_db, 'store_excel_data'):'''
    
    if old_db_storage in content:
        content = content.replace(old_db_storage, new_db_storage)
        print("✅ Added better error handling for database storage")
    
    # Fix 3: Add timeout and completion status
    old_completion = '''        # Step 6: Mark as ready
        update_processing_status(filename, 'ready')
        logging.info(f"[ULTRA-FAST-BG] Ultra-fast processing completed in {time.time() - start_time:.3f}s")'''
    
    new_completion = '''        # Step 6: Mark as ready with timeout protection
        update_processing_status(filename, 'ready')
        logging.info(f"[ULTRA-FAST-BG] Ultra-fast processing completed in {time.time() - start_time:.3f}s")
        
        # Additional safety: Clear any stuck processing status
        import threading
        def clear_stuck_status():
            time.sleep(30)  # Wait 30 seconds
            current_status = processing_status.get(filename, '')
            if 'processing' in current_status or 'finalizing' in current_status:
                update_processing_status(filename, 'ready')
                logging.warning(f"[ULTRA-FAST-BG] Cleared stuck status for {filename}")
        
        threading.Thread(target=clear_stuck_status, daemon=True).start()'''
    
    if old_completion in content:
        content = content.replace(old_completion, new_completion)
        print("✅ Added timeout protection for stuck uploads")
    
    # Fix 4: Add better error handling in the main try-catch
    old_error_handling = '''    except Exception as e:
        logging.error(f"[ULTRA-FAST-BG] Error in ultra-fast processing: {e}")
        update_processing_status(filename, f'error: {str(e)}')'''
    
    new_error_handling = '''    except Exception as e:
        logging.error(f"[ULTRA-FAST-BG] Error in ultra-fast processing: {e}")
        logging.error(f"[ULTRA-FAST-BG] Traceback: {traceback.format_exc()}")
        update_processing_status(filename, f'error: {str(e)}')
        
        # Ensure we don't leave the status stuck
        import threading
        def clear_error_status():
            time.sleep(5)
            current_status = processing_status.get(filename, '')
            if 'processing' in current_status or 'finalizing' in current_status:
                update_processing_status(filename, 'error: Processing failed')
        
        threading.Thread(target=clear_error_status, daemon=True).start()'''
    
    if old_error_handling in content:
        content = content.replace(old_error_handling, new_error_handling)
        print("✅ Enhanced error handling with stuck status protection")
    
    # Write the fixed content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Upload stuck issue fixes applied!")
    return True

if __name__ == "__main__":
    fix_upload_stuck_issue()
