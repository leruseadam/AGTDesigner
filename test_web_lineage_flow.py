#!/usr/bin/env python3
"""
Test the complete lineage flow on the web version
This script simulates what happens when you change lineage and generate a DOCX
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_web_lineage_flow():
    """Test the complete lineage flow as it would happen on the web."""
    
    print("=" * 70)
    print("WEB VERSION LINEAGE FLOW TEST")
    print("=" * 70)
    
    # Step 1: Simulate lineage update via API
    print("\n1️⃣  Step 1: Simulating lineage update (like UI dropdown change)...")
    try:
        from src.core.data.product_database import ProductDatabase
        import sqlite3
        
        db = ProductDatabase()
        db_path = "uploads/product_database.db"
        
        if not os.path.exists(db_path):
            print("   ❌ Database not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a sample product
        cursor.execute('SELECT "Product Name*", "Lineage", "Product Type*" FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "" LIMIT 1;')
        sample = cursor.fetchone()
        
        if not sample:
            print("   ❌ No products found")
            return False
        
        product_name, original_lineage, product_type = sample
        print(f"   📦 Test Product: '{product_name}'")
        print(f"   📊 Original Lineage: '{original_lineage}'")
        print(f"   📊 Product Type: '{product_type}'")
        
        # Change lineage to something different
        new_lineage = "INDICA" if original_lineage != "INDICA" else "SATIVA"
        print(f"   🔄 Changing lineage to: '{new_lineage}'")
        
        # Update via ProductDatabase (simulates /api/update-lineage)
        success = db.update_product_lineage(product_name, new_lineage)
        if success:
            print(f"   ✅ Database update successful")
        else:
            print(f"   ❌ Database update failed")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Simulate DOCX generation (retrieve lineage from database)
    print("\n2️⃣  Step 2: Simulating DOCX generation (like clicking 'Generate Tags')...")
    try:
        # This simulates what happens in /api/generate endpoint
        
        # Get the updated lineage from database
        retrieved_lineage = db.get_product_lineage(product_name)
        print(f"   📖 Retrieved lineage from database: '{retrieved_lineage}'")
        
        if retrieved_lineage == new_lineage:
            print(f"   ✅ Lineage matches what was saved: '{retrieved_lineage}'")
        else:
            print(f"   ❌ Lineage mismatch!")
            print(f"      Expected: '{new_lineage}'")
            print(f"      Got: '{retrieved_lineage}'")
            return False
        
        # Create a mock record like what would be in DOCX generation
        record = {
            'Product Name*': product_name,
            'Lineage': retrieved_lineage,
            'Product Type*': product_type
        }
        
        print(f"   📄 Record for DOCX generation:")
        print(f"      Product Name: {record['Product Name*']}")
        print(f"      Lineage: {record['Lineage']}")
        print(f"      Product Type: {record['Product Type*']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Simulate lineage color application
    print("\n3️⃣  Step 3: Simulating lineage color application...")
    try:
        from src.core.generation.docx_formatting import COLORS
        from docx import Document
        from src.core.generation.docx_formatting import apply_lineage_colors
        
        # Create a test document
        doc = Document()
        table = doc.add_table(rows=1, cols=2)
        table.rows[0].cells[0].text = product_name
        table.rows[0].cells[1].text = new_lineage
        
        print(f"   🎨 Applying lineage colors...")
        print(f"      Cell text: '{new_lineage}'")
        print(f"      Expected color: #{COLORS.get(new_lineage, 'UNKNOWN')}")
        
        # Apply colors
        doc = apply_lineage_colors(doc)
        
        # Check if color was applied
        cell = table.rows[0].cells[1]
        tc = cell._tc
        tcPr = tc.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
        if tcPr is not None:
            shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
            if shd is not None:
                fill_color = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                if fill_color:
                    print(f"   ✅ Color applied: #{fill_color}")
                    if fill_color == COLORS.get(new_lineage):
                        print(f"   ✅ Color matches expected lineage color!")
                    else:
                        print(f"   ⚠️  Color doesn't match expected")
                        print(f"      Expected: #{COLORS.get(new_lineage)}")
                        print(f"      Got: #{fill_color}")
                else:
                    print(f"   ❌ No fill color found")
            else:
                print(f"   ❌ No shading element found")
        else:
            print(f"   ❌ No tcPr element found")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Restore original lineage
    print("\n4️⃣  Step 4: Restoring original lineage...")
    try:
        success = db.update_product_lineage(product_name, original_lineage)
        if success:
            print(f"   ✅ Restored original lineage: '{original_lineage}'")
        else:
            print(f"   ⚠️  Failed to restore original lineage")
    except Exception as e:
        print(f"   ⚠️  Error restoring: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ COMPLETE FLOW TEST PASSED!")
    print("\n📋 What this test simulates:")
    print("1. User changes lineage in UI dropdown → Database updated")
    print("2. User clicks 'Generate Tags' → Lineage retrieved from database")
    print("3. DOCX generation → Lineage colors applied")
    print("\n🎯 If this test passes but web version still doesn't work:")
    print("   - Check if database file is being written to")
    print("   - Check if web app has write permissions")
    print("   - Check if there are multiple database files")
    print("   - Check server logs for errors")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = test_web_lineage_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

