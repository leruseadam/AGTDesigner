#!/usr/bin/env python3
"""
Database Monitoring Script for PythonAnywhere
Checks database integrity and creates backups.
"""

import os
import sqlite3
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_pythonanywhere():
    """Check if running on PythonAnywhere."""
    return (
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    )

def find_database_files(project_dir):
    """Find all database files in the project directory."""
    database_files = []
    
    # Common database locations
    common_paths = [
        os.path.join(project_dir, 'product_database.db'),
        os.path.join(project_dir, 'src', 'core', 'data', 'product_database.db'),
        os.path.expanduser('~/databases/product_database.db'),
    ]
    
    # Check common paths
    for path in common_paths:
        if os.path.isfile(path):
            database_files.append(path)
    
    # Search for any .db, .sqlite, or .sqlite3 files
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                file_path = os.path.join(root, file)
                if file_path not in database_files:
                    database_files.append(file_path)
    
    return database_files

def check_database_integrity(db_path):
    """Check database integrity and return status."""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        # Get database info
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        
        # Get table count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Get total size
        file_size = os.path.getsize(db_path)
        
        if result[0] == "ok":
            logger.info(f"✅ Database integrity check passed: {db_path}")
            logger.info(f"   📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            logger.info(f"   📋 Tables: {len(tables)}")
            logger.info(f"   🔗 Database info: {db_info}")
            return True, {
                'status': 'ok',
                'size': file_size,
                'tables': len(tables),
                'db_info': db_info
            }
        else:
            logger.error(f"❌ Database integrity check failed: {result[0]}")
            return False, {
                'status': 'failed',
                'error': result[0],
                'size': file_size
            }
            
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False, {
            'status': 'error',
            'error': str(e)
        }
    finally:
        if 'conn' in locals():
            conn.close()

def create_database_backup(db_path):
    """Create a timestamped backup of the database."""
    if not os.path.exists(db_path):
        logger.warning(f"ℹ️  Database not found: {db_path}")
        return None
    
    # Create backup directory
    backup_dir = os.path.expanduser('~/database_backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.basename(db_path)
    name, ext = os.path.splitext(filename)
    backup_filename = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Create backup
        shutil.copy2(db_path, backup_path)
        
        # Verify backup
        if os.path.exists(backup_path):
            original_size = os.path.getsize(db_path)
            backup_size = os.path.getsize(backup_path)
            
            if original_size == backup_size:
                logger.info(f"✅ Database backed up to: {backup_path}")
                logger.info(f"   📊 Original: {original_size:,} bytes")
                logger.info(f"   📊 Backup: {backup_size:,} bytes")
                return backup_path
            else:
                logger.error(f"❌ Backup size mismatch: {original_size} vs {backup_size}")
                return None
        else:
            logger.error(f"❌ Backup file not created: {backup_path}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None

def cleanup_old_backups(backup_dir, keep_count=10):
    """Clean up old backup files, keeping only the most recent ones."""
    try:
        backup_files = []
        for ext in ['.db', '.sqlite', '.sqlite3']:
            backup_files.extend(Path(backup_dir).glob(f'*{ext}'))
        
        if len(backup_files) > keep_count:
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for old_backup in backup_files[keep_count:]:
                try:
                    old_backup.unlink()
                    logger.info(f"🗑️  Removed old backup: {old_backup}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to remove old backup {old_backup}: {e}")
                    
    except Exception as e:
        logger.warning(f"⚠️  Backup cleanup failed: {e}")

def get_database_stats(db_path):
    """Get detailed database statistics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        stats = {
            'tables': [],
            'total_records': 0,
            'file_size': os.path.getsize(db_path)
        }
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats['tables'].append({
                    'name': table_name,
                    'records': count
                })
                stats['total_records'] += count
            except Exception as e:
                logger.warning(f"⚠️  Could not get count for table {table_name}: {e}")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to monitor databases."""
    print("🔍 Database Monitoring Script")
    print("=" * 50)
    
    # Check environment
    if is_pythonanywhere():
        print("🌐 PythonAnywhere environment detected")
    else:
        print("💻 Local environment detected")
    
    # Get project directory
    project_dir = os.getcwd()
    print(f"📁 Project directory: {project_dir}")
    
    # Find database files
    print("\n🔍 Searching for database files...")
    database_files = find_database_files(project_dir)
    
    if not database_files:
        print("ℹ️  No database files found")
        return
    
    print(f"📦 Found {len(database_files)} database file(s):")
    for db_file in database_files:
        print(f"   📋 {db_file}")
    
    # Process each database
    all_healthy = True
    backup_dir = os.path.expanduser('~/database_backups')
    
    for db_path in database_files:
        print(f"\n🔍 Checking database: {db_path}")
        print("-" * 40)
        
        # Check integrity
        is_healthy, integrity_info = check_database_integrity(db_path)
        
        if not is_healthy:
            all_healthy = False
        
        # Create backup if healthy
        if is_healthy:
            backup_path = create_database_backup(db_path)
            if backup_path:
                print(f"📦 Backup created: {backup_path}")
            
            # Get detailed stats
            stats = get_database_stats(db_path)
            if stats:
                print(f"📊 Database statistics:")
                print(f"   📁 File size: {stats['file_size']:,} bytes ({stats['file_size']/1024/1024:.2f} MB)")
                print(f"   📋 Total tables: {len(stats['tables'])}")
                print(f"   📊 Total records: {stats['total_records']:,}")
                
                for table in stats['tables']:
                    print(f"      📋 {table['name']}: {table['records']:,} records")
        else:
            print(f"⚠️  Database integrity check failed - skipping backup")
    
    # Clean up old backups
    print(f"\n🧹 Cleaning up old backups...")
    cleanup_old_backups(backup_dir)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   📦 Databases checked: {len(database_files)}")
    print(f"   ✅ Healthy databases: {sum(1 for db in database_files if check_database_integrity(db)[0])}")
    print(f"   ❌ Unhealthy databases: {sum(1 for db in database_files if not check_database_integrity(db)[0])}")
    print(f"   📁 Backup directory: {backup_dir}")
    
    # Count backups
    backup_count = 0
    if os.path.exists(backup_dir):
        for ext in ['.db', '.sqlite', '.sqlite3']:
            backup_count += len(list(Path(backup_dir).glob(f'*{ext}')))
    
    print(f"   📦 Total backups: {backup_count}")
    
    if all_healthy:
        print(f"\n✅ All databases are healthy!")
        return 0
    else:
        print(f"\n⚠️  Some databases have issues - manual review recommended")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 