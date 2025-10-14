#!/usr/bin/env python3
"""
Emergency PythonAnywhere Recovery Script
========================================
This script performs emergency recovery for PythonAnywhere when experiencing:
- Database corruption
- Disk quota exceeded errors
- High CPU usage
- Database locks

CRITICAL: This script will remove large files and recreate the database.
"""

import os
import sys
import shutil
import sqlite3
import time
from pathlib import Path

def emergency_cleanup():
    """Perform emergency cleanup to free disk space."""
    print("🚨 EMERGENCY CLEANUP INITIATED")
    print("=" * 50)
    
    total_freed = 0
    files_removed = 0
    
    # Remove all corrupted database files
    print("🗑️  Removing corrupted database files...")
    corrupted_patterns = [
        "uploads/product_database_AGT_Bothell.db.corrupted.*",
        "uploads/backups/*",
        "uploads/*.db-shm",
        "uploads/*.db-wal", 
        "uploads/*.db-journal",
        "*.zip",
        "uploads/*.zip"
    ]
    
    for pattern in corrupted_patterns:
        import glob
        files = glob.glob(pattern)
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_freed += size
                    files_removed += 1
                    print(f"   ✅ Removed: {file_path} ({size:,} bytes)")
            except Exception as e:
                print(f"   ❌ Error removing {file_path}: {e}")
    
    print(f"\n📊 Emergency Cleanup Results:")
    print(f"   Files removed: {files_removed}")
    print(f"   Space freed: {total_freed:,} bytes ({total_freed/1024/1024:.1f} MB)")
    
    return total_freed, files_removed

def create_minimal_database():
    """Create a minimal database with essential tables only."""
    print("\n🔧 Creating minimal database...")
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{int(time.time())}"
        try:
            shutil.move(db_path, backup_path)
            print(f"   📦 Backed up existing database to: {backup_path}")
        except Exception as e:
            print(f"   ⚠️  Could not backup existing database: {e}")
            os.remove(db_path)
    
    # Create new minimal database
    try:
        conn = sqlite3.connect(db_path)
        
        # Essential tables only
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ProductName TEXT,
                ProductType TEXT,
                Description TEXT,
                Price TEXT,
                Weight TEXT,
                Units TEXT,
                Lineage TEXT,
                ProductBrand TEXT,
                ProductStrain TEXT,
                Vendor TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS strains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                lineage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Essential indexes only
        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(ProductName)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name)")
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Minimal database created: {db_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating minimal database: {e}")
        return False

def disable_automatic_backups():
    """Disable automatic backups in the configuration."""
    print("\n⚙️  Disabling automatic backups...")
    
    # Create a configuration override
    config_content = '''# Emergency PythonAnywhere Configuration
# This disables all automatic backups to prevent disk quota issues

# Database settings
ENABLE_AUTOMATIC_BACKUPS = False
ENABLE_RELIABILITY_FEATURES = False
ENABLE_VECTORIZED_OPERATIONS = False
ENABLE_BATCH_OPERATIONS = False

# Backup settings
DATABASE_BACKUP_INTERVAL_HOURS = 999999  # Effectively disable
DATABASE_BACKUP_RETENTION_DAYS = 0      # Keep no backups
MAX_BACKUPS = 0                         # No backups

# Performance settings
MAX_CONNECTIONS = 2                     # Limit connections
BATCH_SIZE = 10                         # Small batch size
BACKUP_INTERVAL_WRITES = 999999        # Effectively disable

# Journal mode for PythonAnywhere
JOURNAL_MODE = "DELETE"                 # Use DELETE mode for PythonAnywhere
'''
    
    try:
        with open("pythonanywhere_emergency_config.py", "w") as f:
            f.write(config_content)
        print("   ✅ Emergency configuration created: pythonanywhere_emergency_config.py")
        return True
    except Exception as e:
        print(f"   ❌ Error creating emergency config: {e}")
        return False

def check_disk_usage():
    """Check current disk usage."""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        percent_used = (used / total) * 100
        
        print(f"\n📊 Disk Usage:")
        print(f"   Used: {used/1024/1024/1024:.1f} GB ({percent_used:.1f}%)")
        print(f"   Free: {free/1024/1024/1024:.1f} GB")
        
        if percent_used > 90:
            print("   🚨 CRITICAL: Disk usage > 90%")
            return False
        elif percent_used > 80:
            print("   ⚠️  WARNING: Disk usage > 80%")
            return False
        else:
            print("   ✅ Disk usage acceptable")
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking disk usage: {e}")
        return False

def main():
    """Main emergency recovery function."""
    print("🚨 PYTHONANYWHERE EMERGENCY RECOVERY")
    print("=" * 60)
    print("This script will:")
    print("1. Remove all large/corrupted files")
    print("2. Create a minimal database")
    print("3. Disable automatic backups")
    print("4. Check disk usage")
    print()
    
    # Step 1: Emergency cleanup
    freed_bytes, removed_files = emergency_cleanup()
    
    # Step 2: Check disk usage
    disk_ok = check_disk_usage()
    
    # Step 3: Create minimal database
    db_created = create_minimal_database()
    
    # Step 4: Disable automatic backups
    config_created = disable_automatic_backups()
    
    # Summary
    print("\n" + "=" * 60)
    print("🚨 EMERGENCY RECOVERY SUMMARY")
    print("=" * 60)
    print(f"✅ Files removed: {removed_files}")
    print(f"✅ Space freed: {freed_bytes/1024/1024:.1f} MB")
    print(f"✅ Disk usage: {'OK' if disk_ok else 'STILL HIGH'}")
    print(f"✅ Database created: {'YES' if db_created else 'NO'}")
    print(f"✅ Backup disabled: {'YES' if config_created else 'NO'}")
    
    if db_created and config_created:
        print("\n🎉 EMERGENCY RECOVERY COMPLETE!")
        print("   - Restart your Flask application")
        print("   - The system should now work without disk quota errors")
        print("   - Automatic backups are disabled")
        print("   - Database is minimal but functional")
    else:
        print("\n❌ EMERGENCY RECOVERY INCOMPLETE!")
        print("   - Some steps failed")
        print("   - Check the error messages above")
        print("   - Manual intervention may be required")
    
    return db_created and config_created

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
