#!/usr/bin/env python3
"""
Diagnostic script to check why products are missing from database after upload
"""
import sqlite3
import sys
import os

# Database path
DB_PATH = "/Users/adamcordova/Desktop/labelMaker_ QR copy final/uploads/product_database_AGT_Bothell.db"

def check_product(search_term):
    """Check if a product exists in the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Search for the product
    query = """
    SELECT "Product Name*", "Vendor/Supplier*", "Product Type*",
           Source, created_at, updated_at
    FROM products
    WHERE "Product Name*" LIKE ?
    ORDER BY created_at DESC
    LIMIT 10
    """

    cursor.execute(query, (f'%{search_term}%',))
    results = cursor.fetchall()

    print(f"\n🔍 Search results for '{search_term}':")
    print(f"Found {len(results)} matching products\n")

    if results:
        for row in results:
            print(f"Name: {row[0]}")
            print(f"Vendor: {row[1]}")
            print(f"Type: {row[2]}")
            print(f"Source: {row[3] or '(empty)'}")
            print(f"Created: {row[4]}")
            print(f"Updated: {row[5]}")
            print("-" * 80)
    else:
        print(f"❌ No products found matching '{search_term}'")

    conn.close()
    return len(results)

def check_recent_uploads():
    """Check the most recent uploads to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get most recent products
    query = """
    SELECT "Product Name*", "Vendor/Supplier*", created_at
    FROM products
    ORDER BY created_at DESC
    LIMIT 20
    """

    cursor.execute(query)
    results = cursor.fetchall()

    print("\n📋 20 Most Recently Added Products:")
    print("=" * 80)
    for i, row in enumerate(results, 1):
        print(f"{i}. {row[0]} ({row[1]}) - {row[2]}")

    conn.close()

def check_database_stats():
    """Get overall database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]

    # Products added today
    cursor.execute("SELECT COUNT(*) FROM products WHERE DATE(created_at) = DATE('now')")
    today = cursor.fetchone()[0]

    # Products updated today
    cursor.execute("SELECT COUNT(*) FROM products WHERE DATE(updated_at) = DATE('now')")
    updated_today = cursor.fetchone()[0]

    print("\n📊 Database Statistics:")
    print("=" * 80)
    print(f"Total products: {total}")
    print(f"Added today: {today}")
    print(f"Updated today: {updated_today}")

    conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("PRODUCT DATABASE DIAGNOSTIC TOOL")
    print("=" * 80)

    # Check database stats
    check_database_stats()

    # Check recent uploads
    check_recent_uploads()

    # Search for specific products
    search_terms = [
        "White Widow CBG",
        "Platinum Distillate Disposable",
        "Skagit Organics"
    ]

    for term in search_terms:
        check_product(term)

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
