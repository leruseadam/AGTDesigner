#!/usr/bin/env python3
"""
Verify THC/CBD database is ready for production use
"""

import sqlite3
import os
from typing import List, Dict, Any

def verify_thc_cbd_database():
    """Verify the THC/CBD database is ready for production use."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 VERIFYING THC/CBD DATABASE READINESS")
        print("="*60)
        
        # Check database structure
        print("\n1. 📋 Database Structure Check:")
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        
        required_columns = ["THC", "CBD", "Total THC", "Total CBD", "Ratio", "Ratio or THC/CBD"]
        missing_columns = []
        
        existing_column_names = [col[1] for col in columns]
        for req_col in required_columns:
            if req_col not in existing_column_names:
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        else:
            print(f"   ✅ All required columns present ({len(required_columns)} columns)")
        
        # Check data population
        print("\n2. 📊 Data Population Check:")
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"   Total products: {total_products}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != ''")
        thc_count = cursor.fetchone()[0]
        print(f"   Products with THC data: {thc_count} ({thc_count/total_products*100:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"CBD\" IS NOT NULL AND \"CBD\" != ''")
        cbd_count = cursor.fetchone()[0]
        print(f"   Products with CBD data: {cbd_count} ({cbd_count/total_products*100:.1f}%)")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != '' AND \"CBD\" IS NOT NULL AND \"CBD\" != ''")
        both_count = cursor.fetchone()[0]
        print(f"   Products with both THC and CBD: {both_count} ({both_count/total_products*100:.1f}%)")
        
        # Check data quality
        print("\n3. 🔍 Data Quality Check:")
        cursor.execute("SELECT \"Product Name*\", \"THC\", \"CBD\" FROM products WHERE (\"THC\" IS NOT NULL AND \"THC\" != '') OR (\"CBD\" IS NOT NULL AND \"CBD\" != '')")
        thc_cbd_products = cursor.fetchall()
        
        valid_thc_cbd_count = 0
        for name, thc, cbd in thc_cbd_products:
            thc_valid = thc and thc.strip() and thc != '0'
            cbd_valid = cbd and cbd.strip() and cbd != '0'
            if thc_valid or cbd_valid:
                valid_thc_cbd_count += 1
        
        print(f"   Products with valid THC/CBD data: {valid_thc_cbd_count}")
        
        # Show sample data
        print("\n4. 📋 Sample THC/CBD Data:")
        cursor.execute("SELECT \"Product Name*\", \"THC\", \"CBD\", \"Ratio or THC/CBD\" FROM products WHERE (\"THC\" IS NOT NULL AND \"THC\" != '') OR (\"CBD\" IS NOT NULL AND \"CBD\" != '') LIMIT 10")
        samples = cursor.fetchall()
        
        for name, thc, cbd, ratio in samples:
            thc_display = thc if thc else "N/A"
            cbd_display = cbd if cbd else "N/A"
            ratio_display = ratio[:30] + "..." if ratio and len(ratio) > 30 else ratio or "N/A"
            print(f"   {name[:40]:<40} | THC: {thc_display:<8} | CBD: {cbd_display:<8} | Ratio: {ratio_display}")
        
        # Check for any issues
        print("\n5. ⚠️  Potential Issues Check:")
        issues = []
        
        # Check for products with no THC/CBD data
        cursor.execute("SELECT COUNT(*) FROM products WHERE (\"THC\" IS NULL OR \"THC\" = '') AND (\"CBD\" IS NULL OR \"CBD\" = '')")
        no_thc_cbd_count = cursor.fetchone()[0]
        if no_thc_cbd_count > 0:
            issues.append(f"{no_thc_cbd_count} products have no THC/CBD data")
        
        # Check for products with only THC or only CBD
        cursor.execute("SELECT COUNT(*) FROM products WHERE (\"THC\" IS NOT NULL AND \"THC\" != '') AND (\"CBD\" IS NULL OR \"CBD\" = '')")
        thc_only_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products WHERE (\"CBD\" IS NOT NULL AND \"CBD\" != '') AND (\"THC\" IS NULL OR \"THC\" = '')")
        cbd_only_count = cursor.fetchone()[0]
        
        if thc_only_count > 0:
            issues.append(f"{thc_only_count} products have only THC data (no CBD)")
        if cbd_only_count > 0:
            issues.append(f"{cbd_only_count} products have only CBD data (no THC)")
        
        if issues:
            print("   ⚠️  Potential issues found:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ No issues found")
        
        # Final assessment
        print("\n6. 🎯 Final Assessment:")
        if total_products > 0 and (thc_count > 0 or cbd_count > 0):
            coverage_percentage = max(thc_count, cbd_count) / total_products * 100
            if coverage_percentage >= 50:
                print(f"   ✅ Database is ready for production use")
                print(f"   📊 THC/CBD coverage: {coverage_percentage:.1f}%")
                return True
            else:
                print(f"   ⚠️  Database has low THC/CBD coverage: {coverage_percentage:.1f}%")
                print(f"   💡 Consider adding more products with THC/CBD data")
                return False
        else:
            print("   ❌ Database has no THC/CBD data")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    success = verify_thc_cbd_database()
    if success:
        print("\n🎉 THC/CBD database verification completed successfully!")
    else:
        print("\n⚠️  THC/CBD database verification found issues that need attention.")
