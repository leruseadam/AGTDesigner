#!/usr/bin/env python3
"""
Populate THC/CBD data in the database from available sources
"""

import sqlite3
import os
import re
from typing import Optional, Tuple

def extract_thc_cbd_from_ratio(ratio_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract THC and CBD values from ratio text."""
    if not ratio_text:
        return None, None
    
    thc_value = None
    cbd_value = None
    
    # Look for THC: X% pattern
    thc_match = re.search(r'THC:\s*([0-9.]+)%?', ratio_text, re.IGNORECASE)
    if thc_match:
        thc_value = thc_match.group(1)
    
    # Look for CBD: X% pattern
    cbd_match = re.search(r'CBD:\s*([0-9.]+)%?', ratio_text, re.IGNORECASE)
    if cbd_match:
        cbd_value = cbd_match.group(1)
    
    # Look for X:Y THC:CBD pattern
    ratio_match = re.search(r'([0-9.]+):([0-9.]+)\s*(?:THC:CBD|CBD:THC)', ratio_text, re.IGNORECASE)
    if ratio_match:
        val1, val2 = ratio_match.groups()
        if 'THC:CBD' in ratio_text.upper():
            thc_value, cbd_value = val1, val2
        else:  # CBD:THC
            cbd_value, thc_value = val1, val2
    
    # Look for X:Y CBD:THC pattern
    cbd_thc_match = re.search(r'([0-9.]+):([0-9.]+)\s*CBD:THC', ratio_text, re.IGNORECASE)
    if cbd_thc_match:
        cbd_value, thc_value = cbd_thc_match.groups()
    
    return thc_value, cbd_value

def extract_thc_cbd_from_test_result(test_result: str) -> Optional[str]:
    """Extract numeric value from test result string."""
    if not test_result:
        return None
    
    # Look for numeric values with optional % sign
    match = re.search(r'([0-9.]+)%?', test_result)
    if match:
        return match.group(1)
    
    return None

def populate_thc_cbd_data():
    """Populate THC/CBD data from available sources."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all products
        cursor.execute("SELECT id, \"Product Name*\", \"THC\", \"CBD\", \"THC test result\", \"CBD test result\", \"Ratio\", \"Ratio_or_THC_CBD\" FROM products")
        products = cursor.fetchall()
        
        print(f"📊 Processing {len(products)} products...")
        
        updated_count = 0
        
        for product in products:
            product_id, name, thc, cbd, thc_test, cbd_test, ratio, ratio_thc_cbd = product
            
            # Skip if already has THC and CBD data
            if thc and cbd:
                continue
            
            new_thc = thc
            new_cbd = cbd
            updated = False
            
            # Try to extract from Ratio_or_THC_CBD first
            if not new_thc or not new_cbd:
                if ratio_thc_cbd:
                    extracted_thc, extracted_cbd = extract_thc_cbd_from_ratio(ratio_thc_cbd)
                    if extracted_thc and not new_thc:
                        new_thc = extracted_thc
                        updated = True
                    if extracted_cbd and not new_cbd:
                        new_cbd = extracted_cbd
                        updated = True
            
            # Try to extract from Ratio
            if not new_thc or not new_cbd:
                if ratio:
                    extracted_thc, extracted_cbd = extract_thc_cbd_from_ratio(ratio)
                    if extracted_thc and not new_thc:
                        new_thc = extracted_thc
                        updated = True
                    if extracted_cbd and not new_cbd:
                        new_cbd = extracted_cbd
                        updated = True
            
            # Try to extract from test results
            if not new_thc and thc_test:
                extracted_thc = extract_thc_cbd_from_test_result(thc_test)
                if extracted_thc:
                    new_thc = extracted_thc
                    updated = True
            
            if not new_cbd and cbd_test:
                extracted_cbd = extract_thc_cbd_from_test_result(cbd_test)
                if extracted_cbd:
                    new_cbd = extracted_cbd
                    updated = True
            
            # Update the database if we found new data
            if updated:
                cursor.execute("""
                    UPDATE products 
                    SET "THC" = ?, "CBD" = ? 
                    WHERE id = ?
                """, (new_thc, new_cbd, product_id))
                
                print(f"✅ Updated {name[:50]:<50} | THC: {new_thc} | CBD: {new_cbd}")
                updated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Updated {updated_count} products with THC/CBD data")
        
        # Run the check again to see the results
        print("\n" + "="*60)
        print("UPDATED DATA SUMMARY:")
        print("="*60)
        
        # Re-run the check
        check_thc_cbd_data()
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")

def check_thc_cbd_data():
    """Check what THC/CBD data exists in the database."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total number of products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"📊 Total products in database: {total_products}")
        
        # Check THC data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != ''")
        thc_count = cursor.fetchone()[0]
        print(f"   Products with THC data: {thc_count} ({thc_count/total_products*100:.1f}%)")
        
        # Check CBD data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"CBD\" IS NOT NULL AND \"CBD\" != ''")
        cbd_count = cursor.fetchone()[0]
        print(f"   Products with CBD data: {cbd_count} ({cbd_count/total_products*100:.1f}%)")
        
        # Check both THC and CBD
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != '' AND \"CBD\" IS NOT NULL AND \"CBD\" != ''")
        both_count = cursor.fetchone()[0]
        print(f"   Products with both THC and CBD: {both_count} ({both_count/total_products*100:.1f}%)")
        
        # Sample some THC values
        print("\n📋 Sample THC values:")
        cursor.execute("SELECT \"Product Name*\", \"THC\" FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != '' LIMIT 10")
        thc_samples = cursor.fetchall()
        for name, thc in thc_samples:
            print(f"   {name[:50]:<50} | THC: {thc}")
        
        # Sample some CBD values
        print("\n📋 Sample CBD values:")
        cursor.execute("SELECT \"Product Name*\", \"CBD\" FROM products WHERE \"CBD\" IS NOT NULL AND \"CBD\" != '' LIMIT 10")
        cbd_samples = cursor.fetchall()
        for name, cbd in cbd_samples:
            print(f"   {name[:50]:<50} | CBD: {cbd}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    populate_thc_cbd_data()
