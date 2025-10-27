import sqlite3
from pathlib import Path

def check_schemas():
    """Compare schemas between main and Bothell databases."""
    
    current_dir = Path(__file__).parent
    main_db = current_dir / 'uploads' / 'product_database.db'
    bothell_db = current_dir / 'uploads' / 'product_database_AGT_Bothell.db'
    
    print("📊 Comparing database schemas...")
    
    for db_name, db_path in [("Main", main_db), ("Bothell", bothell_db)]:
        if not db_path.exists():
            print(f"❌ {db_name} database not found: {db_path}")
            continue
            
        print(f"\n{'='*60}")
        print(f"{db_name} Database: {db_path}")
        print(f"{'='*60}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(products)")
            columns = cursor.fetchall()
            
            print(f"\nColumns ({len(columns)}):")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            print(f"\nTotal products: {count}")
            
            # Get database size
            import os
            size = os.path.getsize(db_path)
            print(f"Database size: {size / (1024*1024):.2f} MB")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schemas()
