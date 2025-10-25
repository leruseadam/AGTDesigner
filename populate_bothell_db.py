#!/usr/bin/env python3
"""
Script to populate the Bothell database with Excel data.
This will add more products to the existing Bothell database.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.core.data.product_database import ProductDatabase
from src.core.data.excel_processor import ExcelProcessor

def populate_bothell_database():
    """Populate the Bothell database with Excel data."""
    
    print("🚀 Starting Bothell database population...")
    
    # Paths
    db_path = os.path.join(project_root, 'uploads', 'product_database_AGT_Bothell.db')
    excel_path = os.path.join(project_root, 'uploads', 'A Greener Today - Default Inventory.xlsx')
    
    # Check if files exist
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel file not found: {excel_path}")
        return
    
    print(f"📁 Database: {db_path}")
    print(f"📁 Excel file: {excel_path}")
    
    # Get current database stats
    print(f"\n📊 Current database stats:")
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        current_count = cursor.fetchone()[0]
        conn.close()
        print(f"   Current products: {current_count}")
    except Exception as e:
        print(f"   Error getting current count: {e}")
        current_count = 0
    
    # Load Excel data
    print(f"\n📖 Loading Excel data...")
    try:
        df = pd.read_excel(excel_path)
        print(f"   Loaded {len(df)} rows from Excel")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return
    
    # Initialize database
    print(f"\n🗄️ Initializing database...")
    try:
        product_db = ProductDatabase(db_path)
        product_db.init_database()
        print(f"   Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return
    
    # Store Excel data in database
    print(f"\n💾 Storing Excel data in database...")
    try:
        result = product_db.store_excel_data(df, excel_path)
        print(f"   Storage result: {result}")
    except Exception as e:
        print(f"❌ Error storing Excel data: {e}")
        return
    
    # Get final database stats
    print(f"\n📊 Final database stats:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        added_count = final_count - current_count
        print(f"   Final products: {final_count}")
        print(f"   Products added: {added_count}")
        
        if added_count > 0:
            print(f"✅ Successfully added {added_count} products to Bothell database!")
        else:
            print(f"ℹ️  No new products were added (may be duplicates)")
            
    except Exception as e:
        print(f"   Error getting final count: {e}")
    
    # Get file size
    try:
        file_size = os.path.getsize(db_path) / (1024*1024)  # MB
        print(f"   Database size: {file_size:.2f} MB")
    except Exception as e:
        print(f"   Error getting file size: {e}")
    
    print(f"\n✅ Bothell database population complete!")

if __name__ == "__main__":
    populate_bothell_database()
