#!/usr/bin/env python3
"""
Diagnose memory usage issues in the application
"""

import os
import sys
import sqlite3
import json
from pathlib import Path

def get_database_size(db_path):
    """Get database file size"""
    if os.path.exists(db_path):
        return os.path.getsize(db_path)
    return 0

def count_products(db_path):
    """Count products in database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Error counting products: {e}")
        return 0

def estimate_product_memory(count):
    """Estimate memory usage for products (rough estimate: ~2KB per product)"""
    return count * 2 * 1024  # 2KB per product estimate

def check_cache_files():
    """Check cache directory size"""
    cache_dir = Path("uploads/cache")
    if not cache_dir.exists():
        return 0, 0
    
    total_size = 0
    file_count = 0
    for file in cache_dir.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
            file_count += 1
    
    return total_size, file_count

def check_session_files():
    """Check session directory size"""
    session_dir = Path("sessions")
    if not session_dir.exists():
        return 0, 0
    
    total_size = 0
    file_count = 0
    for file in session_dir.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
            file_count += 1
    
    return total_size, file_count

def main():
    print("=" * 80)
    print("MEMORY USAGE DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Check database files
    print("📊 DATABASE FILES:")
    print("-" * 80)
    
    db_files = []
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for file in uploads_dir.glob("*.db"):
            if not file.name.endswith(('-shm', '-wal')):
                db_files.append(file)
    
    total_db_size = 0
    total_products = 0
    
    for db_file in db_files:
        size = get_database_size(str(db_file))
        count = count_products(str(db_file))
        size_mb = size / (1024 * 1024)
        estimated_memory = estimate_product_memory(count) / (1024 * 1024)
        
        total_db_size += size
        total_products += count
        
        print(f"  {db_file.name}:")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Products: {count:,}")
        print(f"    Estimated in-memory size: {estimated_memory:.2f} MB")
        print()
    
    print(f"  TOTAL: {total_db_size / (1024 * 1024):.2f} MB on disk, {total_products:,} products")
    print(f"  Estimated in-memory: {estimate_product_memory(total_products) / (1024 * 1024):.2f} MB")
    print()
    
    # Check cache files
    print("💾 CACHE FILES:")
    print("-" * 80)
    cache_size, cache_count = check_cache_files()
    cache_mb = cache_size / (1024 * 1024)
    print(f"  Total cache size: {cache_mb:.2f} MB ({cache_count} files)")
    print()
    
    # Check session files
    print("📝 SESSION FILES:")
    print("-" * 80)
    session_size, session_count = check_session_files()
    session_mb = session_size / (1024 * 1024)
    print(f"  Total session size: {session_mb:.2f} MB ({session_count} files)")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    estimated_total = (estimate_product_memory(total_products) / (1024 * 1024)) + cache_mb + session_mb
    print(f"  Estimated total in-memory usage: {estimated_total:.2f} MB")
    print()
    
    # Recommendations
    print("🔍 RECOMMENDATIONS:")
    print("-" * 80)
    
    if total_products > 10000:
        print(f"  ⚠️  Large product count ({total_products:,}) - consider pagination")
        print(f"     Current: Loading all {total_products:,} products into memory")
        print(f"     Recommendation: Load products in batches of 1000-5000")
    
    if estimate_product_memory(total_products) > 500 * 1024 * 1024:  # > 500MB
        print(f"  ⚠️  High estimated product memory ({estimate_product_memory(total_products) / (1024 * 1024):.2f} MB)")
        print(f"     Recommendation: Reduce cache TTL or implement pagination")
    
    if cache_mb > 100:
        print(f"  ⚠️  Large cache size ({cache_mb:.2f} MB)")
        print(f"     Recommendation: Clear old cache files or reduce cache TTL")
    
    if session_mb > 50:
        print(f"  ⚠️  Large session size ({session_mb:.2f} MB)")
        print(f"     Recommendation: Clean up old session files")
    
    print()
    print("💡 MEMORY OPTIMIZATION SUGGESTIONS:")
    print("-" * 80)
    print("  1. Implement pagination for get_all_products() calls")
    print("  2. Reduce cache TTL from 1 hour to 15-30 minutes")
    print("  3. Clear old cache entries periodically")
    print("  4. Use lazy loading for product data")
    print("  5. Consider using database queries instead of loading all products")
    print("  6. Clear Excel dataframes from memory after processing")
    print()

if __name__ == "__main__":
    main()

