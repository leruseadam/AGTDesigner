#!/usr/bin/env python3
"""
Test DOH update for Baker's Blend Kief
"""
import sqlite3

db_path = "uploads/product_database_AGT_Bothell.db"
product_name = "Baker's Blend Kief by Mt Baker Homegrown - 1g"

# Check current value
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("BEFORE UPDATE:")
print("=" * 80)
cursor.execute('SELECT "Product Name*", DOH FROM products WHERE "Product Name*" = ?', (product_name,))
result = cursor.fetchone()
print(f"Product: {result[0]}")
print(f"Current DOH: '{result[1]}'")

# Update to 'No'
print("\n" + "=" * 80)
print("UPDATING DOH to 'No'...")
print("=" * 80)
cursor.execute('UPDATE products SET DOH = ? WHERE "Product Name*" = ?', ('No', product_name))
conn.commit()
print("✅ Update committed")

# Verify update
print("\n" + "=" * 80)
print("AFTER UPDATE:")
print("=" * 80)
cursor.execute('SELECT "Product Name*", DOH FROM products WHERE "Product Name*" = ?', (product_name,))
result = cursor.fetchone()
print(f"Product: {result[0]}")
print(f"Current DOH: '{result[1]}'")

print("\n" + "=" * 80)
print("Now generate a DOCX with this product.")
print("The {Label1.DOH} placeholder should be BLANK (no image).")
print("=" * 80)

conn.close()
