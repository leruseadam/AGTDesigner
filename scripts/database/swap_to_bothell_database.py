import sqlite3
import shutil
from pathlib import Path

def swap_databases():
    """Swap Bothell database (with 8,825 products) to be the main database."""
    
    current_dir = Path(__file__).parent
    main_db = current_dir / 'uploads' / 'product_database.db'
    bothell_db = current_dir / 'uploads' / 'product_database_AGT_Bothell.db'
    
    print("🔄 Swapping databases...")
    print(f"   Main DB: {main_db}")
    print(f"   Bothell DB: {bothell_db}")
    
    if not bothell_db.exists():
        print(f"❌ Bothell database not found: {bothell_db}")
        return
    
    # Check counts
    conn = sqlite3.connect(bothell_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    bothell_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n📦 Bothell database has {bothell_count} products")
    
    # Backup main database
    if main_db.exists():
        backup_db = current_dir / 'uploads' / 'product_database_backup_before_swap.db'
        print(f"\n📦 Backing up main database to: {backup_db}")
        shutil.copy2(main_db, backup_db)
    
    # Copy Bothell database to main
    print(f"\n📤 Copying Bothell database to main...")
    shutil.copy2(bothell_db, main_db)
    
    # Verify
    conn = sqlite3.connect(main_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    main_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n✅ Swap complete!")
    print(f"   Main database now has {main_count} products")
    print(f"   Bothell database has {bothell_count} products")
    
    if main_count == bothell_count == 8825:
        print(f"\n🎉 SUCCESS: Both databases now have 8,825 products with prices!")
    else:
        print(f"\n⚠️  WARNING: Product counts don't match!")

if __name__ == "__main__":
    swap_databases()
