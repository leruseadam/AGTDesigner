#!/usr/bin/env python3
"""
Diagnostic script to check PythonAnywhere database status
Run this ON PYTHONANYWHERE to see what's happening
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def check_database_status():
    """Check the current database status"""
    
    print("=" * 50)
    print("PYTHONANYWHERE DATABASE DIAGNOSTIC")
    print("=" * 50)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if we're in the right place
    if not os.path.exists("app.py"):
        print("❌ ERROR: app.py not found. Are you in ~/AGTDesigner?")
        return False
    
    print("✅ Found app.py")
    
    # Check uploads directory
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ ERROR: uploads directory not found")
        return False
    
    print("✅ Found uploads directory")
    
    # Check database file
    db_path = os.path.join(uploads_dir, "product_database_AGT_Bothell.db")
    
    if not os.path.exists(db_path):
        print("❌ ERROR: Database file not found")
        return False
    
    # Get file size
    file_size = os.path.getsize(db_path)
    print(f"✅ Database file exists: {file_size:,} bytes")
    
    if file_size < 10000:
        print("❌ WARNING: Database file is too small (likely corrupted)")
        return False
    
    # Check permissions
    import stat
    file_stat = os.stat(db_path)
    permissions = stat.filemode(file_stat.st_mode)
    print(f"📋 Database permissions: {permissions}")
    
    # Try to connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Database connection successful")
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        # Check strains table
        if ('strains',) in tables:
            cursor.execute("SELECT COUNT(*) FROM strains")
            strain_count = cursor.fetchone()[0]
            print(f"📊 Strains count: {strain_count}")
            
            # Show sample strains
            cursor.execute("SELECT name, type FROM strains LIMIT 5")
            sample_strains = cursor.fetchall()
            print(f"📋 Sample strains: {sample_strains}")
        
        # Check products table
        if ('products',) in tables:
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            print(f"📊 Products count: {product_count}")
            
            # Show sample products
            cursor.execute("SELECT name, type FROM products LIMIT 5")
            sample_products = cursor.fetchall()
            print(f"📋 Sample products: {sample_products}")
        
        # Check for corruption
        try:
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            if result == "ok":
                print("✅ Database integrity check: PASSED")
            else:
                print(f"❌ Database integrity check: FAILED - {result}")
        except Exception as e:
            print(f"❌ Database integrity check failed: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to database: {e}")
        return False
    
    # Check for lock files
    lock_files = []
    for ext in ['-shm', '-wal']:
        lock_file = db_path + ext
        if os.path.exists(lock_file):
            lock_files.append(lock_file)
    
    if lock_files:
        print(f"⚠️  WARNING: Database lock files found: {lock_files}")
    else:
        print("✅ No database lock files found")
    
    # Check disk space
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        print(f"💾 Disk usage:\n{result.stdout}")
    except Exception as e:
        print(f"Could not check disk usage: {e}")
    
    print("=" * 50)
    return True

def check_app_status():
    """Check if the app is running and accessible"""
    
    print("\n" + "=" * 50)
    print("APPLICATION STATUS CHECK")
    print("=" * 50)
    
    # Check if there are any Python processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python' in line and 'app.py' in line]
        
        if python_processes:
            print("🔄 Found running Python app processes:")
            for proc in python_processes:
                print(f"  {proc}")
        else:
            print("ℹ️  No Python app processes found running")
    except Exception as e:
        print(f"Could not check processes: {e}")
    
    # Check recent logs
    log_files = [
        "/var/log/www.agtpricetags.com.error.log",
        "flask.log",
        "app.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📋 Recent errors from {log_file}:")
            try:
                result = subprocess.run(['tail', '-10', log_file], capture_output=True, text=True)
                if result.stdout.strip():
                    print(result.stdout)
                else:
                    print("  (No recent errors)")
            except Exception as e:
                print(f"  Could not read log: {e}")
            break

if __name__ == "__main__":
    print("Starting PythonAnywhere diagnostic...")
    
    success = check_database_status()
    check_app_status()
    
    if success:
        print("\n✅ DIAGNOSTIC COMPLETE - Database appears functional")
        print("If you're still seeing '0 TOTAL PRODUCTS', the issue might be:")
        print("1. Frontend JavaScript not updating")
        print("2. Cached data in browser")
        print("3. API endpoint not working")
        print("\nTry: Hard refresh browser (Ctrl+F5) or clear cache")
    else:
        print("\n❌ DIAGNOSTIC COMPLETE - Database issues found")
        print("Run the deployment script again or create fresh database")
    
    sys.exit(0 if success else 1)
