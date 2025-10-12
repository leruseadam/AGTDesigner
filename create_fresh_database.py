#!/usr/bin/env python3
"""
Create a fresh, clean database with the correct schema
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase

def create_fresh_database():
    """Create a new, clean database with the correct schema."""
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    print("=" * 60)
    print("Creating Fresh Database")
    print("=" * 60)
    print(f"\nDatabase path: {db_path}")
    
    # Remove any existing files
    for ext in ['', '-shm', '-wal']:
        filepath = db_path + ext
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed old file: {filepath}")
    
    print("\nInitializing new database...")
    
    try:
        # Create new database instance - this will initialize the schema
        db = ProductDatabase(db_path)
        
        # Force initialization
        db._initialized = False
        conn = db._get_connection()
        
        if conn:
            print("✅ Database created successfully!")
            
            # Verify the schema
            cursor = conn.cursor()
            
            # Check strains table
            cursor.execute("PRAGMA table_info(strains)")
            strain_cols = [col[1] for col in cursor.fetchall()]
            print(f"\n✓ Strains table columns ({len(strain_cols)}): {', '.join(strain_cols[:5])}...")
            
            # Check products table
            cursor.execute("PRAGMA table_info(products)")
            product_cols = [col[1] for col in cursor.fetchall()]
            print(f"✓ Products table columns ({len(product_cols)}): {', '.join(product_cols[:5])}...")
            
            # Verify normalized_name exists
            if 'normalized_name' in strain_cols:
                print("\n✓ normalized_name column exists in strains table")
            else:
                print("\n⚠️  WARNING: normalized_name column missing!")
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result[0] == 'ok':
                print("✓ Database integrity check: PASSED")
            else:
                print(f"⚠️  Database integrity check: {result[0]}")
            
            # Get file size
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"✓ Database file size: {size_mb:.2f} MB")
            
            conn.close()
            
            print("\n" + "=" * 60)
            print("SUCCESS! Fresh database created.")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Start your Flask app")
            print("2. Upload your Excel inventory file to populate the database")
            print("3. The database will be automatically populated with your products")
            
            return True
        else:
            print("❌ Failed to create database connection")
            return False
            
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_fresh_database()
    sys.exit(0 if success else 1)

