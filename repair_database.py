#!/usr/bin/env python3
"""
SQLite Database Repair Script
Repairs corrupted SQLite databases used by the label maker application.

Usage:
    python repair_database.py [database_path]
    
If no path is provided, it will attempt to find and repair all databases in the data directory.
"""

import sqlite3
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse


def check_database_integrity(db_path):
    """Check if a database is corrupted."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        # Run integrity check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'ok':
            return True, "Database integrity check passed"
        else:
            return False, f"Database integrity check failed: {result[0] if result else 'Unknown error'}"
    except sqlite3.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def repair_database_dump_restore(db_path, backup_path=None):
    """Attempt to repair database using dump and restore method."""
    db_path = Path(db_path)
    
    if not db_path.exists():
        return False, f"Database file does not exist: {db_path}"
    
    # Create backup if not provided
    if backup_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = db_path.parent / f"{db_path.stem}_corrupted_backup_{timestamp}.db"
    
    backup_path = Path(backup_path)
    
    print(f"📦 Creating backup: {backup_path.name}")
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created successfully")
    except Exception as e:
        return False, f"Failed to create backup: {e}"
    
    # Method 1: Dump and restore
    print("🔧 Method 1: Attempting dump and restore...")
    dump_file = db_path.parent / f"{db_path.stem}_dump.sql"
    recovered_db = db_path.parent / f"{db_path.stem}_recovered.db"
    
    try:
        # Try to dump the database
        print("  → Dumping database...")
        old_conn = sqlite3.connect(str(db_path))
        with open(dump_file, 'w', encoding='utf-8') as f:
            for line in old_conn.iterdump():
                f.write(f"{line}\n")
        old_conn.close()
        print("  ✅ Dump completed")
        
        # Create new database from dump
        print("  → Restoring from dump...")
        if recovered_db.exists():
            recovered_db.unlink()
        
        new_conn = sqlite3.connect(str(recovered_db))
        with open(dump_file, 'r', encoding='utf-8') as f:
            new_conn.executescript(f.read())
        new_conn.close()
        print("  ✅ Restore completed")
        
        # Verify recovered database
        print("  → Verifying recovered database...")
        verify_conn = sqlite3.connect(str(recovered_db))
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        verify_conn.close()
        
        if integrity_result and integrity_result[0] == 'ok' and table_count > 0:
            print(f"  ✅ Recovered database verified ({table_count} tables)")
            
            # Replace corrupted database with recovered one
            db_path.unlink()
            recovered_db.rename(db_path)
            dump_file.unlink()
            
            print(f"✅ Database successfully repaired!")
            return True, f"Database repaired successfully. Backup saved as: {backup_path.name}"
        else:
            print(f"  ❌ Recovered database verification failed")
            recovered_db.unlink()
            dump_file.unlink()
            return False, "Recovered database failed verification"
            
    except sqlite3.DatabaseError as e:
        print(f"  ❌ Dump/restore failed: {e}")
        if dump_file.exists():
            dump_file.unlink()
        if recovered_db.exists():
            recovered_db.unlink()
        return False, f"Dump/restore method failed: {e}"
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        if dump_file.exists():
            dump_file.unlink()
        if recovered_db.exists():
            recovered_db.unlink()
        return False, f"Unexpected error: {e}"


def repair_database_vacuum(db_path, backup_path=None):
    """Attempt to repair database using VACUUM method."""
    db_path = Path(db_path)
    
    if not db_path.exists():
        return False, f"Database file does not exist: {db_path}"
    
    # Create backup if not provided
    if backup_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = db_path.parent / f"{db_path.stem}_corrupted_backup_{timestamp}.db"
    
    backup_path = Path(backup_path)
    
    print(f"📦 Creating backup: {backup_path.name}")
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created successfully")
    except Exception as e:
        return False, f"Failed to create backup: {e}"
    
    # Method 2: VACUUM
    print("🔧 Method 2: Attempting VACUUM repair...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Try to run VACUUM
        print("  → Running VACUUM...")
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()
        print("  ✅ VACUUM completed")
        
        # Verify database
        print("  → Verifying database...")
        verify_conn = sqlite3.connect(str(db_path))
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        verify_conn.close()
        
        if integrity_result and integrity_result[0] == 'ok':
            print(f"  ✅ Database verified after VACUUM")
            return True, f"Database repaired using VACUUM. Backup saved as: {backup_path.name}"
        else:
            return False, "Database still corrupted after VACUUM"
            
    except sqlite3.DatabaseError as e:
        print(f"  ❌ VACUUM failed: {e}")
        return False, f"VACUUM method failed: {e}"
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False, f"Unexpected error: {e}"


def repair_database(db_path, methods=['dump_restore', 'vacuum']):
    """Attempt to repair a corrupted database using multiple methods."""
    db_path = Path(db_path)
    
    print(f"\n{'='*60}")
    print(f"🔍 Repairing database: {db_path.name}")
    print(f"{'='*60}\n")
    
    # Check current integrity
    print("📋 Checking database integrity...")
    is_ok, message = check_database_integrity(db_path)
    if is_ok:
        print(f"✅ {message}")
        print("✅ Database is healthy - no repair needed!")
        return True, "Database is healthy"
    else:
        print(f"⚠️  {message}")
        print("🔧 Starting repair process...\n")
    
    # Try repair methods in order
    for method in methods:
        if method == 'dump_restore':
            success, message = repair_database_dump_restore(db_path)
            if success:
                return True, message
        elif method == 'vacuum':
            success, message = repair_database_vacuum(db_path)
            if success:
                return True, message
    
    return False, "All repair methods failed"


def find_databases(data_dir=None, recursive=False):
    """Find all SQLite databases in the data directory."""
    databases = []
    
    if data_dir is None:
        # Try to find data directory - search more locations
        script_dir = Path(__file__).parent
        possible_dirs = [
            script_dir / 'data',
            script_dir / 'src' / 'core' / 'data',
            script_dir / 'src' / 'data',
            script_dir / 'core' / 'data',
            Path.home() / '.labelmaker' / 'data',
            Path('/tmp'),
            Path('/var/tmp'),
        ]
        
        # Also search recursively from script directory
        if recursive:
            print("🔍 Searching recursively for databases...")
            for root_dir in [script_dir, Path.home()]:
                if root_dir.exists():
                    databases.extend(root_dir.rglob('*.db'))
                    # Limit search depth to avoid scanning entire filesystem
                    if len(databases) > 0:
                        break
        
        # Try specific directories
        for dir_path in possible_dirs:
            if dir_path.exists():
                if recursive:
                    databases.extend(dir_path.rglob('*.db'))
                else:
                    databases.extend(dir_path.glob('*.db'))
        
        # Remove duplicates and sort
        databases = sorted(set(databases), key=lambda p: str(p))
        return databases
    
    # Search specified directory
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []
    
    if recursive:
        databases = list(data_dir.rglob('*.db'))
    else:
        databases = list(data_dir.glob('*.db'))
    
    return databases


def main():
    parser = argparse.ArgumentParser(description='Repair corrupted SQLite databases')
    parser.add_argument('database', nargs='?', help='Path to database file (optional)')
    parser.add_argument('--data-dir', help='Data directory to search for databases')
    parser.add_argument('--method', choices=['dump_restore', 'vacuum', 'all'], 
                       default='all', help='Repair method to use')
    parser.add_argument('--check-only', action='store_true', 
                       help='Only check integrity, do not repair')
    parser.add_argument('--find', action='store_true',
                       help='Find and list all databases without repairing')
    parser.add_argument('--recursive', action='store_true',
                       help='Search recursively for databases')
    
    args = parser.parse_args()
    
    methods = []
    if args.method == 'all':
        methods = ['dump_restore', 'vacuum']
    else:
        methods = [args.method]
    
    databases_to_repair = []
    
    if args.database:
        # Repair specific database
        databases_to_repair = [Path(args.database)]
    else:
        # Find all databases
        print("🔍 Searching for databases...")
        databases = find_databases(args.data_dir, recursive=args.recursive or args.find)
        if not databases:
            print("❌ No databases found.")
            print("\n💡 Try:")
            print("  1. python repair_database.py --find --recursive")
            print("  2. python repair_database.py /path/to/database.db")
            print("  3. python repair_database.py --data-dir /path/to/data/directory")
            sys.exit(1)
        
        if args.find:
            # Just list databases
            print(f"\n✅ Found {len(databases)} database(s):\n")
            for db in databases:
                size = db.stat().st_size / (1024 * 1024)  # Size in MB
                is_ok, message = check_database_integrity(db)
                status = "✅ OK" if is_ok else "❌ CORRUPTED"
                print(f"  {status}  {db} ({size:.2f} MB)")
            print()
            sys.exit(0)
        
        databases_to_repair = databases
        print(f"✅ Found {len(databases)} database(s)\n")
    
    # Process each database
    repaired_count = 0
    failed_count = 0
    
    for db_path in databases_to_repair:
        if not db_path.exists():
            print(f"❌ Database not found: {db_path}")
            failed_count += 1
            continue
        
        if args.check_only:
            # Only check integrity
            is_ok, message = check_database_integrity(db_path)
            if is_ok:
                print(f"✅ {db_path.name}: {message}")
            else:
                print(f"❌ {db_path.name}: {message}")
                failed_count += 1
        else:
            # Attempt repair
            success, message = repair_database(db_path, methods)
            if success:
                print(f"\n✅ SUCCESS: {message}\n")
                repaired_count += 1
            else:
                print(f"\n❌ FAILED: {message}\n")
                failed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Summary:")
    if args.check_only:
        healthy = len(databases_to_repair) - failed_count
        print(f"  ✅ Healthy: {healthy}")
        print(f"  ❌ Corrupted: {failed_count}")
    else:
        print(f"  ✅ Repaired: {repaired_count}")
        print(f"  ❌ Failed: {failed_count}")
    print(f"{'='*60}\n")
    
    if failed_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
