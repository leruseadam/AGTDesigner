#!/usr/bin/env python3
"""
Comprehensive THC/CBD data population for the database
"""

import sqlite3
import os
import re
from typing import Optional, Tuple, Dict, Any

def extract_thc_cbd_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract THC and CBD values from any text."""
    if not text:
        return None, None
    
    thc_value = None
    cbd_value = None
    
    # Look for THC: X% pattern
    thc_match = re.search(r'THC:\s*([0-9.]+)%?', text, re.IGNORECASE)
    if thc_match:
        thc_value = thc_match.group(1)
    
    # Look for CBD: X% pattern
    cbd_match = re.search(r'CBD:\s*([0-9.]+)%?', text, re.IGNORECASE)
    if cbd_match:
        cbd_value = cbd_match.group(1)
    
    # Look for X:Y THC:CBD pattern
    ratio_match = re.search(r'([0-9.]+):([0-9.]+)\s*(?:THC:CBD|CBD:THC)', text, re.IGNORECASE)
    if ratio_match:
        val1, val2 = ratio_match.groups()
        if 'THC:CBD' in text.upper():
            thc_value, cbd_value = val1, val2
        else:  # CBD:THC
            cbd_value, thc_value = val1, val2
    
    # Look for X:Y CBD:THC pattern
    cbd_thc_match = re.search(r'([0-9.]+):([0-9.]+)\s*CBD:THC', text, re.IGNORECASE)
    if cbd_thc_match:
        cbd_value, thc_value = cbd_thc_match.groups()
    
    # Look for standalone THC values
    if not thc_value:
        thc_standalone = re.search(r'\bTHC\s*([0-9.]+)%?\b', text, re.IGNORECASE)
        if thc_standalone:
            thc_value = thc_standalone.group(1)
    
    # Look for standalone CBD values
    if not cbd_value:
        cbd_standalone = re.search(r'\bCBD\s*([0-9.]+)%?\b', text, re.IGNORECASE)
        if cbd_standalone:
            cbd_value = cbd_standalone.group(1)
    
    return thc_value, cbd_value

def extract_numeric_value(text: str) -> Optional[str]:
    """Extract numeric value from text."""
    if not text:
        return None
    
    # Look for numeric values with optional % sign
    match = re.search(r'([0-9.]+)%?', text)
    if match:
        return match.group(1)
    
    return None

def comprehensive_thc_cbd_population():
    """Comprehensively populate THC/CBD data from all available sources."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all products with all relevant columns
        cursor.execute("""
            SELECT id, "Product Name*", 
                   "THC", "CBD", 
                   "THC test result", "CBD test result", 
                   "Ratio", "Ratio_or_THC_CBD",
                   "Total THC", "Total CBD",
                   "THCA", "CBDA", "CBN", "CBGA", "CBG", "Total CBG",
                   "CBC", "CBDV", "THCV", "CBGV", "CBNV", "CBGVA"
            FROM products
        """)
        products = cursor.fetchall()
        
        print(f"📊 Processing {len(products)} products for comprehensive THC/CBD population...")
        
        updated_count = 0
        
        for product in products:
            product_id = product[0]
            name = product[1]
            
            # Current values
            current_thc = product[2]
            current_cbd = product[3]
            
            # Test results
            thc_test = product[4]
            cbd_test = product[5]
            
            # Ratio fields
            ratio = product[6]
            ratio_thc_cbd = product[7]
            
            # Total values
            total_thc = product[8]
            total_cbd = product[9]
            
            # Other cannabinoids
            thca = product[10]
            cbda = product[11]
            cbn = product[12]
            cbga = product[13]
            cbg = product[14]
            total_cbg = product[15]
            cbc = product[16]
            cbdv = product[17]
            thcv = product[18]
            cbgv = product[19]
            cbnv = product[20]
            cbgva = product[21]
            
            # Skip if already has both THC and CBD data
            if current_thc and current_cbd:
                continue
            
            new_thc = current_thc
            new_cbd = current_cbd
            updated = False
            update_reason = []
            
            # Priority 1: Try to extract from Ratio_or_THC_CBD
            if not new_thc or not new_cbd:
                if ratio_thc_cbd:
                    extracted_thc, extracted_cbd = extract_thc_cbd_from_text(ratio_thc_cbd)
                    if extracted_thc and not new_thc:
                        new_thc = extracted_thc
                        updated = True
                        update_reason.append("Ratio_or_THC_CBD")
                    if extracted_cbd and not new_cbd:
                        new_cbd = extracted_cbd
                        updated = True
                        update_reason.append("Ratio_or_THC_CBD")
            
            # Priority 2: Try to extract from Ratio
            if not new_thc or not new_cbd:
                if ratio:
                    extracted_thc, extracted_cbd = extract_thc_cbd_from_text(ratio)
                    if extracted_thc and not new_thc:
                        new_thc = extracted_thc
                        updated = True
                        update_reason.append("Ratio")
                    if extracted_cbd and not new_cbd:
                        new_cbd = extracted_cbd
                        updated = True
                        update_reason.append("Ratio")
            
            # Priority 3: Use test results
            if not new_thc and thc_test:
                extracted_thc = extract_numeric_value(thc_test)
                if extracted_thc:
                    new_thc = extracted_thc
                    updated = True
                    update_reason.append("THC test result")
            
            if not new_cbd and cbd_test:
                extracted_cbd = extract_numeric_value(cbd_test)
                if extracted_cbd:
                    new_cbd = extracted_cbd
                    updated = True
                    update_reason.append("CBD test result")
            
            # Priority 4: Use Total THC/CBD if available
            if not new_thc and total_thc:
                extracted_thc = extract_numeric_value(total_thc)
                if extracted_thc:
                    new_thc = extracted_thc
                    updated = True
                    update_reason.append("Total THC")
            
            if not new_cbd and total_cbd:
                extracted_cbd = extract_numeric_value(total_cbd)
                if extracted_cbd:
                    new_cbd = extracted_cbd
                    updated = True
                    update_reason.append("Total CBD")
            
            # Priority 5: Use THCA/CBDA if available (these are the acid forms)
            if not new_thc and thca:
                extracted_thc = extract_numeric_value(thca)
                if extracted_thc:
                    new_thc = extracted_thc
                    updated = True
                    update_reason.append("THCA")
            
            if not new_cbd and cbda:
                extracted_cbd = extract_numeric_value(cbda)
                if extracted_cbd:
                    new_cbd = extracted_cbd
                    updated = True
                    update_reason.append("CBDA")
            
            # Update the database if we found new data
            if updated:
                cursor.execute("""
                    UPDATE products 
                    SET "THC" = ?, "CBD" = ? 
                    WHERE id = ?
                """, (new_thc, new_cbd, product_id))
                
                reason_str = ", ".join(update_reason)
                print(f"✅ Updated {name[:50]:<50} | THC: {new_thc} | CBD: {new_cbd} | Source: {reason_str}")
                updated_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Updated {updated_count} products with THC/CBD data")
        
        # Run the final check
        print("\n" + "="*80)
        print("FINAL THC/CBD DATA SUMMARY:")
        print("="*80)
        
        check_final_data()
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")

def check_final_data():
    """Check the final state of THC/CBD data."""
    
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
        
        # Show all products with THC/CBD data
        print("\n📋 All products with THC/CBD data:")
        cursor.execute("SELECT \"Product Name*\", \"THC\", \"CBD\" FROM products WHERE (\"THC\" IS NOT NULL AND \"THC\" != '') OR (\"CBD\" IS NOT NULL AND \"CBD\" != '') ORDER BY \"Product Name*\"")
        all_samples = cursor.fetchall()
        for name, thc, cbd in all_samples:
            thc_display = thc if thc else "N/A"
            cbd_display = cbd if cbd else "N/A"
            print(f"   {name[:60]:<60} | THC: {thc_display:<8} | CBD: {cbd_display}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking final data: {e}")

if __name__ == "__main__":
    comprehensive_thc_cbd_population()
