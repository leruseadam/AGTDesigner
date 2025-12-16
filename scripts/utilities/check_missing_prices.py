import sqlite3
import os
from pathlib import Path

def check_missing_prices():
    """Check the database for products with missing prices."""
    
    # Find the database file
    current_dir = Path(__file__).parent
    db_path = current_dir / 'uploads' / 'product_database.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        # Try to find any database files
        uploads_dir = current_dir / 'uploads'
        if uploads_dir.exists():
            db_files = list(uploads_dir.glob('product_database*.db'))
            if db_files:
                print(f"\nFound database files:")
                for db_file in db_files:
                    print(f"  - {db_file}")
                    db_path = db_file
            else:
                print("No database files found in uploads directory")
                return
        else:
            return
    
    print(f"📊 Checking database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"\n📦 Total products in database: {total_products}")
        
        # Check products with missing prices
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE "Price" IS NULL 
               OR "Price" = '' 
               OR "Price" = 'nan'
               OR "Price" = '0'
               OR "Price" = '0.0'
               OR "Price" = '0.00'
        """)
        missing_prices_count = cursor.fetchone()[0]
        
        print(f"⚠️  Products with missing or zero prices: {missing_prices_count}")
        
        if missing_prices_count > 0:
            # Get sample products with missing prices
            cursor.execute("""
                SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Price"
                FROM products 
                WHERE "Price" IS NULL 
                   OR "Price" = '' 
                   OR "Price" = 'nan'
                   OR "Price" = '0'
                   OR "Price" = '0.0'
                   OR "Price" = '0.00'
                LIMIT 20
            """)
            
            missing_price_products = cursor.fetchall()
            
            print(f"\n🔍 Sample products with missing prices (showing first 20):")
            print("-" * 100)
            print(f"{'Product Name':<40} {'Type':<20} {'Brand':<25} {'Price':<10}")
            print("-" * 100)
            
            for product in missing_price_products:
                name, ptype, vendor, brand, price = product
                name = str(name)[:38] if name else 'N/A'
                ptype = str(ptype)[:18] if ptype else 'N/A'
                brand = str(brand)[:23] if brand else 'N/A'
                price_str = str(price)[:8] if price else 'NULL'
                print(f"{name:<40} {ptype:<20} {brand:<25} {price_str:<10}")
        
        # Check products with valid prices
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE "Price" IS NOT NULL 
              AND "Price" != '' 
              AND "Price" != 'nan'
              AND "Price" != '0'
              AND "Price" != '0.0'
              AND "Price" != '0.00'
        """)
        valid_prices_count = cursor.fetchone()[0]
        
        print(f"\n✅ Products with valid prices: {valid_prices_count}")
        
        # Show price distribution
        print(f"\n💰 Price distribution:")
        cursor.execute("""
            SELECT "Price", COUNT(*) as count
            FROM products 
            WHERE "Price" IS NOT NULL 
              AND "Price" != '' 
              AND "Price" != 'nan'
              AND "Price" != '0'
            GROUP BY "Price"
            ORDER BY count DESC
            LIMIT 15
        """)
        
        price_dist = cursor.fetchall()
        for price, count in price_dist:
            print(f"  {price}: {count} products")
        
        # Check how many products had prices set by default vs have real prices
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN "Price" = '0.00' THEN 1 ELSE 0 END) as zero_prices,
                SUM(CASE WHEN "Price" = '0.0' THEN 1 ELSE 0 END) as zero_prices_1,
                SUM(CASE WHEN "Price" = '0' THEN 1 ELSE 0 END) as zero_prices_2,
                SUM(CASE WHEN "Price" IS NULL OR "Price" = '' THEN 1 ELSE 0 END) as null_prices
            FROM products
        """)
        
        zero_stats = cursor.fetchone()
        zero_total = sum(zero_stats)
        
        if zero_total > 0:
            print(f"\n⚠️  Products with default/zero prices: {zero_total}")
            print(f"   - '0.00': {zero_stats[0]}")
            print(f"   - '0.0': {zero_stats[1]}")
            print(f"   - '0': {zero_stats[2]}")
            print(f"   - NULL/empty: {zero_stats[3]}")
        
        conn.close()
        
        print(f"\n{'='*100}")
        if missing_prices_count > 0:
            print(f"⚠️  SUMMARY: {missing_prices_count} products need price data")
            print(f"   Percentage: {(missing_prices_count/total_products)*100:.1f}%")
        else:
            print("✅ All products have valid prices!")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_missing_prices()
