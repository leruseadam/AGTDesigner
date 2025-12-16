#!/usr/bin/env python3
"""
Database diagnostic script for PythonAnywhere
Shows what's actually in the database
"""

import os
import sys
import sqlite3

def diagnose_database():
    """Diagnose the current database state"""
    
    print("=======================================")
    print("DATABASE DIAGNOSTIC")
    print("=======================================")
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    if not os.path.exists(db_path):
        print("❌ No database file found!")
        return False
    
    # Get database info
    db_size = os.path.getsize(db_path)
    print(f"📊 Database file size: {db_size:,} bytes ({db_size/1024/1024:.1f} MB)")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ 'products' table does not exist!")
            print("Available tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                print(f"   - {table[0]}")
            conn.close()
            return False
        
        print("✅ 'products' table exists")
        
        # Get table schema
        print("\n📋 Table schema:")
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL OK'}")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM products;")
        row_count = cursor.fetchone()[0]
        print(f"\n📦 Total rows: {row_count:,}")
        
        if row_count > 0:
            # Show sample data
            print("\n📄 Sample data (first 3 rows):")
            cursor.execute("SELECT * FROM products LIMIT 3;")
            rows = cursor.fetchall()
            
            for i, row in enumerate(rows, 1):
                print(f"\n   Row {i}:")
                for j, col in enumerate(columns):
                    value = row[j] if j < len(row) else "NULL"
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    print(f"      {col[1]}: {value}")
        
        # Check for common issues
        print("\n🔍 Checking for common issues:")
        
        # Check for blank entries using actual column names
        name_cols = []
        for col in columns:
            if 'name' in col[1].lower() or 'product' in col[1].lower():
                name_cols.append(col[1])
        
        if name_cols:
            for col_name in name_cols:
                # Handle column names with spaces by wrapping in square brackets
                safe_col_name = f'"{col_name}"' if ' ' in col_name else col_name
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM products WHERE {safe_col_name} IS NULL OR {safe_col_name} = '';")
                    blank_count = cursor.fetchone()[0]
                    if blank_count > 0:
                        print(f"   ⚠️  {blank_count} blank entries in {col_name}")
                except Exception as e:
                    print(f"   ⚠️  Could not check {col_name}: {e}")
        
        # Check database integrity
        print("\n🔍 Checking database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"❌ Database integrity check failed: {integrity_result}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main diagnostic function"""
    
    print("🚀 Starting database diagnosis...")
    
    if not os.path.exists("uploads"):
        print("❌ Not in the correct directory. Please run from the AGTDesigner directory.")
        return False
    
    success = diagnose_database()
    
    if success:
        print("\n✅ DATABASE DIAGNOSIS COMPLETE!")
    else:
        print("\n❌ Database diagnosis failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
