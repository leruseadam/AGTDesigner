import sqlite3
import os
from pathlib import Path
import re

def fix_price_formatting():
    """Fix price formatting in the database (remove extra dollar signs)."""
    
    # Find the database file
    current_dir = Path(__file__).parent
    db_path = current_dir / 'uploads' / 'product_database.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"📊 Fixing price formatting in: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check products with double dollar signs
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE "Price" LIKE '$$%'
        """)
        double_dollar_count = cursor.fetchone()[0]
        
        if double_dollar_count == 0:
            print("✅ No double dollar signs found in prices")
            conn.close()
            return
        
        print(f"\n⚠️  Found {double_dollar_count} products with double dollar signs")
        
        # Get some examples
        cursor.execute("""
            SELECT "Product Name*", "Price"
            FROM products 
            WHERE "Price" LIKE '$$%'
            LIMIT 10
        """)
        
        examples = cursor.fetchall()
        print(f"\n🔍 Examples:")
        for name, price in examples:
            print(f"  {name[:50]}: {price}")
        
        # Ask for confirmation
        response = input(f"\n❓ Fix {double_dollar_count} prices? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Cancelled")
            conn.close()
            return
        
        # Update prices to remove extra dollar signs
        cursor.execute("""
            UPDATE products 
            SET "Price" = REPLACE("Price", '$$', '$')
            WHERE "Price" LIKE '$$%'
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Fixed {updated_count} prices")
        
        # Verify the fix
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE "Price" LIKE '$$%'
        """)
        remaining = cursor.fetchone()[0]
        
        if remaining == 0:
            print("✅ All double dollar signs fixed!")
        else:
            print(f"⚠️  {remaining} products still have double dollar signs")
        
        # Show some updated prices
        cursor.execute("""
            SELECT "Product Name*", "Price"
            FROM products 
            LIMIT 10
        """)
        
        updated_examples = cursor.fetchall()
        print(f"\n📋 Sample updated prices:")
        for name, price in updated_examples:
            print(f"  {name[:50]}: {price}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_price_formatting()
