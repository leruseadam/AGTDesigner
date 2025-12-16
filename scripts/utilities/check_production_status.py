#!/usr/bin/env python3
"""
Quick diagnostic tool to check production status
Run this on PythonAnywhere to verify the current state
"""

import os
import sqlite3
import requests
import json

def check_production_status():
    print("🔍 PRODUCTION STATUS CHECK")
    print("=" * 50)
    
    # Check 1: Database file status
    print("1. Checking database file...")
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"   ✅ Database exists: {size_mb:.1f} MB")
        
        # Check product count
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
            
            print(f"   📊 Product count: {count}")
            
            if count > 10000:
                print("   ✅ Database has correct number of products")
            elif count > 0:
                print("   ⚠️  Database has some products but fewer than expected")
            else:
                print("   ❌ Database is empty")
                
        except Exception as e:
            print(f"   ❌ Database error: {e}")
    else:
        print("   ❌ Database file not found")
    
    # Check 2: JavaScript files
    print("\n2. Checking JavaScript fixes...")
    js_files = [
        "static/js/production_error_fix.js",
        "static/js/tags_table.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"   ✅ {js_file} exists")
        else:
            print(f"   ❌ {js_file} missing")
    
    # Check 3: Try to access the API locally
    print("\n3. Testing local API...")
    try:
        # This would work if running on PythonAnywhere
        from app import app
        with app.test_client() as client:
            response = client.get('/api/database-stats')
            if response.status_code == 200:
                data = response.get_json()
                product_count = data.get('stats', {}).get('total_products', 0)
                print(f"   ✅ Local API working: {product_count} products")
            else:
                print(f"   ❌ Local API error: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Cannot test local API: {e}")
    
    # Check 4: Test external API
    print("\n4. Testing external API...")
    try:
        response = requests.get('https://www.agtpricetags.com/api/database-stats', timeout=10)
        if response.status_code == 200:
            data = response.json()
            product_count = data.get('stats', {}).get('total_products', 0)
            print(f"   ✅ External API working: {product_count} products")
            
            if product_count > 10000:
                print("   ✅ Production is working correctly!")
            else:
                print("   ❌ Production still showing wrong data")
        else:
            print(f"   ❌ External API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot access external API: {e}")
    
    print("\n" + "=" * 50)
    print("📋 RECOMMENDATIONS:")
    
    if not os.path.exists(db_path):
        print("   🚀 UPLOAD DATABASE: Upload complete_production_fix_20251012_143859.zip")
    elif os.path.exists(db_path) and os.path.getsize(db_path) < 100 * 1024 * 1024:  # Less than 100MB
        print("   🔄 REPLACE DATABASE: Current database is too small, replace with fixed version")
    else:
        print("   ✅ Database looks good")
    
    if not os.path.exists("static/js/production_error_fix.js"):
        print("   🔧 FIX JAVASCRIPT: Upload JavaScript error fixes")
    
    print("   🔄 RELOAD WEB APP: Make sure to reload the web app after changes")
    print("   ⏱️  WAIT: Allow 30-60 seconds after reload for changes to take effect")

if __name__ == "__main__":
    check_production_status()
