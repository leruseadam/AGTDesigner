import sqlite3
import os
from pathlib import Path

def sync_bothell_database():
    """Copy all products from main database to Bothell store database."""
    
    # Database paths
    current_dir = Path(__file__).parent
    main_db = current_dir / 'uploads' / 'product_database.db'
    bothell_db = current_dir / 'uploads' / 'product_database_AGT_Bothell.db'
    
    if not main_db.exists():
        print(f"❌ Main database not found: {main_db}")
        return
    
    print(f"📊 Syncing databases...")
    print(f"   Source: {main_db}")
    print(f"   Target: {bothell_db}")
    
    try:
        # Connect to both databases
        main_conn = sqlite3.connect(main_db)
        bothell_conn = sqlite3.connect(bothell_db)
        
        main_cursor = main_conn.cursor()
        bothell_cursor = bothell_conn.cursor()
        
        # Get count from main database
        main_cursor.execute("SELECT COUNT(*) FROM products")
        main_count = main_cursor.fetchone()[0]
        print(f"\n📦 Products in main database: {main_count}")
        
        # Get count from Bothell database
        bothell_cursor.execute("SELECT COUNT(*) FROM products")
        bothell_count = bothell_cursor.fetchone()[0]
        print(f"📦 Products in Bothell database (before): {bothell_count}")
        
        # Get all products from main database
        print(f"\n📥 Reading products from main database...")
        main_cursor.execute("SELECT * FROM products")
        columns = [description[0] for description in main_cursor.description]
        
        # Get all rows
        all_products = main_cursor.fetchall()
        print(f"   Found {len(all_products)} products")
        
        # Clear Bothell database
        print(f"\n🗑️  Clearing Bothell database...")
        bothell_cursor.execute("DELETE FROM products")
        
        # Insert all products into Bothell database
        print(f"\n📤 Inserting products into Bothell database...")
        
        # Prepare insert statement
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join([f'"{c}"' for c in columns])
        insert_sql = f"INSERT INTO products ({column_names}) VALUES ({placeholders})"
        
        # Insert in batches for better performance
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(all_products), batch_size):
            batch = all_products[i:i+batch_size]
            bothell_cursor.executemany(insert_sql, batch)
            bothell_conn.commit()
            total_inserted += len(batch)
            print(f"   Inserted {total_inserted}/{len(all_products)} products...")
        
        # Verify the sync
        bothell_cursor.execute("SELECT COUNT(*) FROM products")
        new_bothell_count = bothell_cursor.fetchone()[0]
        
        print(f"\n✅ Sync complete!")
        print(f"   Products in Bothell database (after): {new_bothell_count}")
        print(f"   Products synced: {total_inserted}")
        
        # Check prices
        main_cursor.execute("SELECT COUNT(*) FROM products WHERE \"Price\" IS NOT NULL AND \"Price\" != '' AND \"Price\" != '0'")
        main_prices = main_cursor.fetchone()[0]
        
        bothell_cursor.execute("SELECT COUNT(*) FROM products WHERE \"Price\" IS NOT NULL AND \"Price\" != '' AND \"Price\" != '0'")
        bothell_prices = bothell_cursor.fetchone()[0]
        
        print(f"\n💰 Price statistics:")
        print(f"   Main database products with prices: {main_prices}")
        print(f"   Bothell database products with prices: {bothell_prices}")
        
        if main_count == new_bothell_count:
            print(f"\n✅ SUCCESS: All products synced correctly!")
        else:
            print(f"\n⚠️  WARNING: Product count mismatch!")
        
        main_conn.close()
        bothell_conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_bothell_database()
