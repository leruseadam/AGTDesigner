#!/usr/bin/env python3
"""
Add debugging to see what happens to the 49 JSON matches during validation
"""

import os

def add_validation_debugging():
    """Add debug logging to the validation step in app.py to see what happens to 49 matches."""
    
    print("=" * 70)
    print("ADDING VALIDATION DEBUGGING TO APP.PY")
    print("=" * 70)
    
    # Read app.py
    app_path = "app.py"
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Find the validation section where get_products_by_names is called
    # Look for the section that processes db_records
    
    debug_code = '''
                    # VALIDATION DEBUG: Track what happens to JSON matches
                    logging.info(f"🔍 VALIDATION DEBUG: About to validate {len(normalized_tags)} normalized tags")
                    logging.info(f"🔍 VALIDATION DEBUG: First 10 tags: {normalized_tags[:10]}")
                    
                    db_records = product_db.get_products_by_names(normalized_tags)
                    
                    logging.info(f"🔍 VALIDATION DEBUG: get_products_by_names returned {len(db_records)} records")
                    
                    # Count valid vs placeholder records
                    valid_count = 0
                    placeholder_count = 0
                    for i, record in enumerate(db_records):
                        has_id = record.get('id') is not None
                        product_name = record.get('Product Name*', '')
                        vendor = record.get('Vendor/Supplier*', '')
                        
                        if has_id:
                            valid_count += 1
                            if i < 5:  # Log first 5 valid matches
                                logging.info(f"🔍 VALIDATION DEBUG: Valid match {valid_count}: '{product_name}' (Vendor: {vendor})")
                        else:
                            placeholder_count += 1
                            if i < 5:  # Log first 5 placeholders
                                logging.info(f"🔍 VALIDATION DEBUG: Placeholder {placeholder_count}: '{product_name}' (NOT FOUND IN DB)")
                    
                    logging.info(f"🔍 VALIDATION DEBUG: Found {valid_count} valid records, {placeholder_count} placeholders")'''
    
    # Find where db_records = product_db.get_products_by_names is called
    if 'db_records = product_db.get_products_by_names(normalized_tags)' in content:
        # Replace the simple call with our debug version
        content = content.replace(
            'db_records = product_db.get_products_by_names(normalized_tags)',
            debug_code
        )
        print("✅ Added validation debugging for normalized_tags")
    elif 'db_records = product_db.get_products_by_names(enhanced_tags)' in content:
        # Replace the enhanced_tags version
        content = content.replace(
            'db_records = product_db.get_products_by_names(enhanced_tags)',
            debug_code.replace('normalized_tags', 'enhanced_tags')
        )
        print("✅ Added validation debugging for enhanced_tags")
    else:
        print("❌ Could not find get_products_by_names call to replace")
        return
    
    # Write back to app.py
    with open(app_path, 'w') as f:
        f.write(content)
    
    print("✅ Validation debugging added to app.py")
    print("\n🚀 NEXT STEPS:")
    print("1. Try generating labels again")
    print("2. Check the logs to see exactly what happens to the 49 matches")
    print("3. The debug output will show how many are valid vs placeholders")

if __name__ == "__main__":
    add_validation_debugging()