#!/usr/bin/env python3
"""
Find and fix database on PythonAnywhere
"""

import sqlite3
import os
import glob

def find_database():
    """Find the database file on PythonAnywhere."""
    print("🔍 Searching for database file...")
    
    # Common locations to search
    search_paths = [
        ".",
        "..",
        "../..",
        "~/AGTDesigner",
        "/home/adamcordova/AGTDesigner",
        "/home/adamcordova",
        "uploads",
        "data",
        "src/core/data"
    ]
    
    # Search for database files
    db_files = []
    for path in search_paths:
        try:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                # Look for .db files
                for db_file in glob.glob(os.path.join(expanded_path, "*.db")):
                    db_files.append(db_file)
                # Look for product_database.db specifically
                specific_db = os.path.join(expanded_path, "product_database.db")
                if os.path.exists(specific_db):
                    db_files.append(specific_db)
        except Exception as e:
            print(f"Error searching {path}: {e}")
    
    # Remove duplicates
    db_files = list(set(db_files))
    
    if db_files:
        print("✅ Found database files:")
        for db_file in db_files:
            print(f"   - {db_file}")
        return db_files[0]  # Return the first one
    else:
        print("❌ No database files found")
        return None

def fix_database_columns(db_path):
    """Fix missing columns in the database."""
    print(f"🔧 Fixing database columns in: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Columns to add
        columns_to_add = [
            ('sovereign_lineage', 'TEXT'),
            ('strain_name', 'TEXT'),
            ('thc_content', 'TEXT'),
            ('cbd_content', 'TEXT')
        ]
        
        # Add missing columns
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                print(f"Adding {column_name} column...")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}")
                print(f"✅ {column_name} column added successfully")
            else:
                print(f"✅ {column_name} column already exists")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("🎉 Database columns fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Database Finder and Fixer for PythonAnywhere")
    print("=" * 50)
    
    # Find database
    db_path = find_database()
    
    if db_path:
        print(f"\n📁 Using database: {db_path}")
        
        # Fix columns
        success = fix_database_columns(db_path)
        
        if success:
            print("\n✅ Database fix completed successfully!")
        else:
            print("\n❌ Database fix failed!")
    else:
        print("\n❌ No database found. Please check the file locations.")
        print("\n💡 Try running this command to find .db files:")
        print("   find /home/adamcordova -name '*.db' 2>/dev/null")

if __name__ == "__main__":
    main() 