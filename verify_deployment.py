#!/usr/bin/env python3
"""
Verify the deployment package works correctly
"""

import os
import sys
import sqlite3
from pathlib import Path

def verify_deployment():
    """Verify the deployment package"""
    print("🔍 Verifying PythonAnywhere deployment package...")
    
    deploy_dir = "pythonanywhere_deployment"
    
    if not os.path.exists(deploy_dir):
        print("❌ Deployment directory not found")
        return False
    
    # Essential files check
    essential_files = [
        "app.py",
        "requirements.txt",
        "product_database.db",
        "src/core/data/product_database.py",
        "static/js/main.js",
        "templates/index.html"
    ]
    
    print("\n📁 Checking essential files...")
    all_files_present = True
    for file_path in essential_files:
        full_path = os.path.join(deploy_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_present = False
    
    if not all_files_present:
        print("\n❌ Some essential files are missing")
        return False
    
    # Database verification
    print("\n🗄️  Checking database...")
    db_path = os.path.join(deploy_dir, "product_database.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if Cost* column is removed
            cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'Cost*' in columns:
                print("❌ Cost* column still exists in database")
                conn.close()
                return False
            else:
                print("✅ Cost* column successfully removed")
            
            # Check product count
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            print(f"✅ Database contains {product_count} products")
            
            conn.close()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    else:
        print("❌ Database file not found")
        return False
    
    # Test app loading
    print("\n🐍 Testing app loading...")
    try:
        sys.path.insert(0, deploy_dir)
        from app import app
        print("✅ Flask app loads successfully")
    except Exception as e:
        print(f"❌ App loading error: {e}")
        return False
    
    # Test database connection
    print("\n🔗 Testing database connection...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        products = db.get_products_by_names(['Blue Dream'])
        print(f"✅ Database connection works - found {len(products)} products")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    print("\n🎉 Deployment package verification PASSED!")
    print("✅ Ready for PythonAnywhere deployment")
    return True

if __name__ == "__main__":
    verify_deployment()