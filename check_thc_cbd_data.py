#!/usr/bin/env python3
"""
Check THC/CBD data in the database
"""

import sqlite3
import os
from collections import Counter

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
        print("\n🔍 THC Data Analysis:")
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
        
        # Check THC test result data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC test result\" IS NOT NULL AND \"THC test result\" != ''")
        thc_test_count = cursor.fetchone()[0]
        print(f"   Products with THC test result: {thc_test_count} ({thc_test_count/total_products*100:.1f}%)")
        
        # Check CBD test result data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"CBD test result\" IS NOT NULL AND \"CBD test result\" != ''")
        cbd_test_count = cursor.fetchone()[0]
        print(f"   Products with CBD test result: {cbd_test_count} ({cbd_test_count/total_products*100:.1f}%)")
        
        # Sample some THC values
        print("\n📋 Sample THC values:")
        cursor.execute("SELECT \"Product Name*\", \"THC\", \"THC test result\" FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != '' LIMIT 10")
        thc_samples = cursor.fetchall()
        for name, thc, thc_test in thc_samples:
            print(f"   {name[:50]:<50} | THC: {thc} | Test: {thc_test}")
        
        # Sample some CBD values
        print("\n📋 Sample CBD values:")
        cursor.execute("SELECT \"Product Name*\", \"CBD\", \"CBD test result\" FROM products WHERE \"CBD\" IS NOT NULL AND \"CBD\" != '' LIMIT 10")
        cbd_samples = cursor.fetchall()
        for name, cbd, cbd_test in cbd_samples:
            print(f"   {name[:50]:<50} | CBD: {cbd} | Test: {cbd_test}")
        
        # Check for products with Ratio data that might contain THC/CBD
        print("\n📋 Products with Ratio data (might contain THC/CBD):")
        cursor.execute("SELECT \"Product Name*\", \"Ratio\" FROM products WHERE \"Ratio\" IS NOT NULL AND \"Ratio\" != '' AND (\"Ratio\" LIKE '%THC%' OR \"Ratio\" LIKE '%CBD%') LIMIT 10")
        ratio_samples = cursor.fetchall()
        for name, ratio in ratio_samples:
            print(f"   {name[:50]:<50} | Ratio: {ratio}")
        
        # Check for products with Ratio_or_THC_CBD data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"Ratio_or_THC_CBD\" IS NOT NULL AND \"Ratio_or_THC_CBD\" != ''")
        ratio_thc_cbd_count = cursor.fetchone()[0]
        print(f"\n📊 Products with Ratio_or_THC_CBD data: {ratio_thc_cbd_count} ({ratio_thc_cbd_count/total_products*100:.1f}%)")
        
        if ratio_thc_cbd_count > 0:
            print("\n📋 Sample Ratio_or_THC_CBD values:")
            cursor.execute("SELECT \"Product Name*\", \"Ratio_or_THC_CBD\" FROM products WHERE \"Ratio_or_THC_CBD\" IS NOT NULL AND \"Ratio_or_THC_CBD\" != '' LIMIT 10")
            ratio_thc_cbd_samples = cursor.fetchall()
            for name, ratio_thc_cbd in ratio_thc_cbd_samples:
                print(f"   {name[:50]:<50} | Ratio_or_THC_CBD: {ratio_thc_cbd}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_thc_cbd_data()
