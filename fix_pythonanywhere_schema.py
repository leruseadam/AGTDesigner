#!/usr/bin/env python3
"""
Script to fix the database schema on PythonAnywhere by adding missing normalized_name column
"""
import sqlite3
import os
import sys

def fix_database_schema(db_path):
    """Add normalized_name column to strains table if missing."""
    try:
        print(f"Checking database at: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"ERROR: Database file not found at {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current strains table schema
        cursor.execute("PRAGMA table_info(strains)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\nCurrent strains table columns: {column_names}")
        
        if 'normalized_name' not in column_names:
            print("\n⚠️  normalized_name column is MISSING")
            print("Adding normalized_name column to strains table...")
            
            cursor.execute("ALTER TABLE strains ADD COLUMN normalized_name TEXT")
            print("✓ Column added successfully")
            
            # Update existing rows with normalized names
            print("Updating existing strain records...")
            cursor.execute("""
                UPDATE strains 
                SET normalized_name = LOWER(REPLACE(REPLACE(strain_name, ' ', ''), '-', ''))
                WHERE normalized_name IS NULL
            """)
            updated_count = cursor.rowcount
            print(f"✓ Updated {updated_count} existing strain records")
            
            conn.commit()
            print("\n✅ Database schema fixed successfully!")
            
            # Verify the fix
            cursor.execute("PRAGMA table_info(strains)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"\nUpdated strains table columns: {column_names}")
            
            return True
        else:
            print("\n✓ normalized_name column already exists")
            print("✅ Database schema is correct!")
            return True
            
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Default path for PythonAnywhere
    default_path = "/home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db"
    
    # Allow custom path as command line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    print("=" * 60)
    print("PythonAnywhere Database Schema Fix")
    print("=" * 60)
    
    success = fix_database_schema(db_path)
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS! You can now reload your web app.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("FAILED! Please check the errors above.")
        print("=" * 60)
        sys.exit(1)

