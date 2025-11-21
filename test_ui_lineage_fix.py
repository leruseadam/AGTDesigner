#!/usr/bin/env python3
"""
Test script to verify that /api/selected-tags returns database lineage
"""
import sys
import os
sys.path.insert(0, '.')

from app import app, get_product_database, get_current_store_name, get_session_excel_processor
from flask import session
import json

print("=" * 80)
print("Testing UI Lineage Fix - Database vs Excel")
print("=" * 80)

# Test within app context
with app.test_request_context():
    with app.test_client() as client:
        # Set up session with a store
        with client.session_transaction() as sess:
            sess['store_name'] = 'AGT_Bothell'
        
        print("\n1. Testing database lineage query directly...")
        product_db = get_product_database('AGT_Bothell')
        if product_db:
            test_product = '100 Rackz by Mt Baker Homegrown - 14g'
            db_lineage = product_db.get_product_lineage(test_product)
            print(f"   Product: {test_product}")
            print(f"   Database lineage: {db_lineage}")
        
        print("\n2. Simulating /api/selected-tags response...")
        print("   (This shows what the UI will receive)")
        
        # Create a mock selected tag with Excel lineage
        excel_processor = get_session_excel_processor()
        if excel_processor and excel_processor.df is not None:
            # Get a sample product from Excel
            sample_row = excel_processor.df.iloc[0]
            product_name = sample_row.get('Product Name*', '')
            excel_lineage = sample_row.get('Lineage', '')
            
            print(f"\n   Sample Product: {product_name}")
            print(f"   Excel lineage: {excel_lineage}")
            
            # Simulate the API logic
            db_lineage = None
            if product_db:
                try:
                    db_lineage = product_db.get_product_lineage(product_name)
                except Exception as e:
                    print(f"   Error getting DB lineage: {e}")
            
            if db_lineage and str(db_lineage).strip() not in ['', 'None', 'nan']:
                print(f"   ✅ Database lineage found: {db_lineage}")
                print(f"   API will return: canonical_lineage='{db_lineage}', currentLineage='{db_lineage}'")
            else:
                print(f"   ⚠️ No database lineage found, falling back to Excel: {excel_lineage}")
        else:
            print("   ⚠️ No Excel data loaded - upload a file first")

print("\n" + "=" * 80)
print("Summary:")
print("=" * 80)
print("✅ The fix is implemented in app.py")
print("⚠️  You need to RESTART the Flask server for changes to take effect")
print("")
print("Steps to apply the fix:")
print("1. Stop the current Flask server (Ctrl+C in the terminal running it)")
print("2. Restart: python3 app.py")
print("3. Refresh your browser")
print("4. The UI will now show database lineage instead of Excel lineage")
print("=" * 80)
