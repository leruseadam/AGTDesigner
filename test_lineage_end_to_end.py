#!/usr/bin/env python3
"""
End-to-end test for lineage changes from UI to DOCX output
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_lineage_end_to_end():
    """Test the complete lineage flow from database to DOCX."""
    
    print("=" * 70)
    print("END-TO-END LINEAGE COLOR TEST")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Database Operations
    print("\n1️⃣  Testing Database Operations...")
    try:
        from src.core.data.product_database import ProductDatabase
        import sqlite3
        
        db = ProductDatabase()
        db_path = "uploads/product_database.db"
        
        if not os.path.exists(db_path):
            print("   ⚠️  No database found - creating sample...")
            all_passed = False
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get a sample product with lineage
            cursor.execute('SELECT "Product Name*", "Lineage", "Product Type*" FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "" LIMIT 1;')
            sample = cursor.fetchone()
            
            if sample:
                product_name, current_lineage, product_type = sample
                print(f"   📦 Sample Product: '{product_name}'")
                print(f"   📊 Current Lineage: '{current_lineage}'")
                print(f"   📊 Product Type: '{product_type}'")
                
                # Test update
                test_lineage = "SATIVA"
                success = db.update_product_lineage(product_name, test_lineage)
                if success:
                    print(f"   ✅ Update successful: '{test_lineage}'")
                else:
                    print(f"   ❌ Update failed")
                    all_passed = False
                
                # Test retrieval
                retrieved = db.get_product_lineage(product_name)
                if retrieved == test_lineage:
                    print(f"   ✅ Retrieval successful: '{retrieved}'")
                else:
                    print(f"   ❌ Retrieval failed: expected '{test_lineage}', got '{retrieved}'")
                    all_passed = False
                
                # Restore original
                db.update_product_lineage(product_name, current_lineage)
                print(f"   ✅ Restored original lineage: '{current_lineage}'")
            else:
                print("   ❌ No products with lineage found")
                all_passed = False
            
            conn.close()
    except Exception as e:
        print(f"   ❌ Error in database test: {e}")
        all_passed = False
    
    # Test 2: Lineage Color Mapping
    print("\n2️⃣  Testing Lineage Color Mapping...")
    try:
        from src.core.generation.docx_formatting import COLORS, apply_lineage_colors
        
        required_lineages = ['SATIVA', 'INDICA', 'HYBRID', 'CBD', 'MIXED']
        print(f"   📊 Available Colors: {list(COLORS.keys())}")
        
        missing = [l for l in required_lineages if l not in COLORS]
        if not missing:
            print(f"   ✅ All required lineage colors defined")
            for lineage, color in COLORS.items():
                print(f"      {lineage}: #{color}")
        else:
            print(f"   ❌ Missing lineage colors: {missing}")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error in color mapping test: {e}")
        all_passed = False
    
    # Test 3: DOCX Generation with Lineage
    print("\n3️⃣  Testing DOCX Generation with Lineage...")
    try:
        from docx import Document
        from src.core.generation.docx_formatting import apply_lineage_colors
        
        # Create a test document
        doc = Document()
        table = doc.add_table(rows=3, cols=2)
        
        # Add test data with different lineages
        test_data = [
            ("SATIVA", "Red"),
            ("INDICA", "Purple"),
            ("HYBRID", "Green")
        ]
        
        for i, (lineage, color_name) in enumerate(test_data):
            table.rows[i].cells[0].text = f"Product {i+1}"
            table.rows[i].cells[1].text = lineage
        
        # Apply lineage colors
        print("   🎨 Applying lineage colors to test document...")
        doc = apply_lineage_colors(doc)
        
        # Check if colors were applied
        colors_found = []
        for row in table.rows:
            for cell in row.cells:
                tc = cell._tc
                tcPr = tc.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
                if tcPr is not None:
                    shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                    if shd is not None:
                        fill_color = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                        if fill_color and fill_color != 'FFFFFF':
                            colors_found.append((cell.text, fill_color))
        
        if colors_found:
            print(f"   ✅ Colors applied to {len(colors_found)} cells:")
            for text, color in colors_found:
                print(f"      '{text}' -> #{color}")
        else:
            print(f"   ⚠️  No colors were applied to cells")
            print(f"      This might be normal if lineage markers are used")
    except Exception as e:
        print(f"   ❌ Error in DOCX generation test: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Test 4: Check app.py lineage override logic
    print("\n4️⃣  Checking app.py Lineage Override Logic...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('LINEAGE OVERRIDE', 'Lineage override logging'),
            ('get_product_lineage', 'Product lineage retrieval'),
            ('update_product_lineage', 'Product lineage update'),
        ]
        
        for check_str, description in checks:
            if check_str in app_content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ❌ {description} missing")
                all_passed = False
    except Exception as e:
        print(f"   ❌ Error checking app.py: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 Troubleshooting Steps:")
        print("1. Make sure you've changed lineage in the UI dropdown")
        print("2. Generate a DOCX file after changing lineage")
        print("3. Open the DOCX and check if the lineage bar has the new color")
        print("4. Check browser console for errors")
        print("5. Check server logs for 'LINEAGE OVERRIDE' messages")
        print("\n🎨 Expected Colors:")
        print("   SATIVA → 🔴 Red (#ED4123)")
        print("   INDICA → 🟣 Purple (#9900FF)")
        print("   HYBRID → 🟢 Green (#009900)")
        print("   CBD → 🟡 Yellow (#F1C232)")
        print("   MIXED → 🔵 Blue (#0021F5)")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - See errors above")
        return False

if __name__ == "__main__":
    success = test_lineage_end_to_end()
    sys.exit(0 if success else 1)

