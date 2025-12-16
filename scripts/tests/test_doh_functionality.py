#!/usr/bin/env python3
"""
Test script to verify DOH dropdown functionality affects DOCX output
"""
import sqlite3
import sys

def check_doh_values():
    """Check current DOH values in database"""
    # Use Bothell database
    db_path = "uploads/product_database_AGT_Bothell.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 80)
        print("DOH FUNCTIONALITY TEST")
        print("=" * 80)

        # Count products by DOH value
        cursor.execute("""
            SELECT DOH, COUNT(*) as count
            FROM products
            WHERE DOH IS NOT NULL AND DOH != ''
            GROUP BY DOH
            ORDER BY count DESC
        """)

        print("\n1. Current DOH value distribution:")
        print("-" * 40)
        for row in cursor.fetchall():
            doh_value, count = row
            print(f"   DOH='{doh_value}': {count} products")

        # Show sample products with different DOH values
        print("\n2. Sample products with DOH='Yes' (should include image):")
        print("-" * 40)
        cursor.execute("""
            SELECT "Product Name*"
            FROM products
            WHERE DOH = 'Yes'
            LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"   - {row[0]}")

        print("\n3. Sample products with DOH='No' (should NOT include image):")
        print("-" * 40)
        cursor.execute("""
            SELECT "Product Name*"
            FROM products
            WHERE DOH = 'No'
            LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"   - {row[0]}")

        # Check for new DOH values (DOH, THC, CBD)
        print("\n4. Products with new DOH values:")
        print("-" * 40)
        cursor.execute("""
            SELECT DOH, COUNT(*) as count
            FROM products
            WHERE DOH IN ('DOH', 'THC', 'CBD')
            GROUP BY DOH
        """)
        results = cursor.fetchall()
        if results:
            for row in results:
                doh_value, count = row
                print(f"   DOH='{doh_value}': {count} products")
        else:
            print("   No products with new DOH values (DOH/THC/CBD) yet")

        print("\n" + "=" * 80)
        print("EXPECTED BEHAVIOR:")
        print("=" * 80)
        print("When DOH dropdown is set to:")
        print("  • 'None' (stores as 'No')   → No .png image in DOCX")
        print("  • 'DOH'  (stores as 'DOH')  → Includes DOH.png in DOCX")
        print("  • 'THC'  (stores as 'THC')  → Includes HighTHC.png in DOCX")
        print("  • 'CBD'  (stores as 'CBD')  → Includes HighCBD.png in DOCX")
        print("  • 'Yes'  (legacy, stored)   → Includes DOH.png in DOCX")
        print("\n" + "=" * 80)
        print("\nTO TEST:")
        print("1. Open your app in browser")
        print("2. Select a product from the list")
        print("3. Change its DOH dropdown (e.g., from 'None' to 'DOH')")
        print("4. Generate a DOCX with that product")
        print("5. Check the logs for messages starting with '🔍 DOH' or '✅ DOH'")
        print("6. Verify the DOCX output matches the expected behavior above")
        print("=" * 80)

        conn.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_doh_values()
    sys.exit(0 if success else 1)
