#!/usr/bin/env python3
"""
Repair corrupted SQLite database on PythonAnywhere
Run this BEFORE cleanup to fix integrity issues

Usage:
  python3 pythonanywhere_repair_database.py [--store STORE_NAME]
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import argparse

def find_database_path(store_name="AGT_Bothell"):
    """Find the database file for the specified store"""
    possible_paths = [
        f"uploads/product_database_{store_name}.db",
        f"product_database_{store_name}.db",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') and store_name in file:
                return os.path.join(root, file)
    
    return None

def repair_database(db_path):
    """
    Repair corrupted SQLite database by dumping and reimporting
    """
    
    print("=" * 60)
    print("PYTHONANYWHERE DATABASE REPAIR")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Get initial database info
    db_size_mb = os.path.getsize(db_path) / 1024 / 1024
    print(f"📊 Database size: {db_size_mb:.2f} MB")
    
    try:
        # Check current integrity
        print("\n🔍 Checking database integrity...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA integrity_check;")
        results = cursor.fetchall()
        
        is_corrupt = False
        for result in results:
            if result[0] != "ok":
                is_corrupt = True
                print(f"⚠️  {result[0]}")
        
        if not is_corrupt:
            print("✅ Database is already healthy - no repair needed!")
            conn.close()
            return True
        
        print(f"\n🔧 Database corruption detected - starting repair process...")
        
        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_path}.backup_before_repair_{timestamp}"
        print(f"\n📁 Creating backup: {backup_path}")
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created")
        
        # Get product count before repair
        try:
            cursor.execute("SELECT COUNT(*) FROM products")
            initial_count = cursor.fetchone()[0]
            print(f"\n📦 Products in corrupted database: {initial_count:,}")
        except:
            print(f"\n⚠️  Could not count products in corrupted database")
            initial_count = "unknown"
        
        conn.close()
        
        # Create temporary database path
        temp_db = f"{db_path}.temp_repair_{timestamp}"
        dump_file = f"{db_path}.dump_{timestamp}.sql"
        
        print(f"\n🔄 Step 1: Dumping database to SQL file...")
        print(f"   This may take a few minutes for large databases...")
        
        # Try Python iterdump first (more reliable for corrupted DBs)
        try:
            print(f"   Using Python iterdump method...")
            with open(dump_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            
            if os.path.exists(dump_file):
                dump_size_mb = os.path.getsize(dump_file) / 1024 / 1024
                print(f"✅ Database dumped to SQL ({dump_size_mb:.2f} MB)")
            else:
                raise Exception("Dump file not created")
                
        except Exception as e:
            print(f"⚠️  Python iterdump failed: {e}")
            print(f"   Trying sqlite3 command line method...")
            
            # Fallback to sqlite3 command
            dump_cmd = f'sqlite3 "{db_path}" .dump > "{dump_file}"'
            result = os.system(dump_cmd)
            
            if result != 0 or not os.path.exists(dump_file):
                print(f"❌ Failed to dump database with both methods")
                return False
            
            dump_size_mb = os.path.getsize(dump_file) / 1024 / 1024
            print(f"✅ Database dumped to SQL ({dump_size_mb:.2f} MB)")
        
        # Fix duplicate IDs in the dump file
        print(f"\n🔄 Step 2: Fixing duplicate IDs in dump file...")
        cleaned_dump = f"{dump_file}.cleaned"
        
        with open(dump_file, 'r', encoding='utf-8', errors='ignore') as f_in:
            with open(cleaned_dump, 'w', encoding='utf-8') as f_out:
                in_strains_inserts = False
                strains_ids_seen = set()
                lines_cleaned = 0
                lines_skipped = 0
                
                for line in f_in:
                    # Detect if we're in strains table INSERT statements
                    if 'INSERT INTO "strains"' in line or 'INSERT INTO strains' in line:
                        in_strains_inserts = True
                        # Try to extract the ID from the INSERT statement
                        # Format: INSERT INTO "strains" VALUES(id,...)
                        try:
                            if 'VALUES(' in line:
                                values_part = line.split('VALUES(')[1]
                                id_str = values_part.split(',')[0].strip()
                                strain_id = int(id_str)
                                
                                if strain_id in strains_ids_seen:
                                    # Skip this duplicate
                                    lines_skipped += 1
                                    continue
                                else:
                                    strains_ids_seen.add(strain_id)
                        except:
                            pass  # If we can't parse, keep the line
                    elif in_strains_inserts and not line.strip().startswith('INSERT'):
                        # We've moved past strains inserts
                        in_strains_inserts = False
                        strains_ids_seen.clear()
                    
                    f_out.write(line)
                    lines_cleaned += 1
        
        if lines_skipped > 0:
            print(f"✅ Removed {lines_skipped} duplicate strain entries")
        
        # Use the cleaned dump
        print(f"✅ Database dumped to SQL ({dump_size_mb:.2f} MB)")
        
        # Fix duplicate IDs in the dump file
        print(f"\n🔄 Step 2: Fixing duplicate IDs in dump file...")
        cleaned_dump = f"{dump_file}.cleaned"
        
        with open(dump_file, 'r', encoding='utf-8', errors='ignore') as f_in:
            with open(cleaned_dump, 'w', encoding='utf-8') as f_out:
                in_strains_inserts = False
                strains_ids_seen = set()
                lines_cleaned = 0
                lines_skipped = 0
                
                for line in f_in:
                    # Detect if we're in strains table INSERT statements
                    if 'INSERT INTO "strains"' in line or 'INSERT INTO strains' in line:
                        in_strains_inserts = True
                        # Try to extract the ID from the INSERT statement
                        # Format: INSERT INTO "strains" VALUES(id,...)
                        try:
                            if 'VALUES(' in line:
                                values_part = line.split('VALUES(')[1]
                                id_str = values_part.split(',')[0].strip()
                                strain_id = int(id_str)
                                
                                if strain_id in strains_ids_seen:
                                    # Skip this duplicate
                                    lines_skipped += 1
                                    continue
                                else:
                                    strains_ids_seen.add(strain_id)
                        except:
                            pass  # If we can't parse, keep the line
                    elif in_strains_inserts and not line.strip().startswith('INSERT'):
                        # We've moved past strains inserts
                        in_strains_inserts = False
                        strains_ids_seen.clear()
                    
                    f_out.write(line)
                    lines_cleaned += 1
        
        if lines_skipped > 0:
            print(f"✅ Removed {lines_skipped} duplicate strain entries")
        
        # Use the cleaned dump
        os.replace(cleaned_dump, dump_file)
        
        print(f"\n🔄 Step 3: Creating new database from cleaned dump...")
        print(f"   This may take a few minutes...")
        
        # Import the cleaned dump into a new database
        import_cmd = f'sqlite3 "{temp_db}" < "{dump_file}"'
        result = os.system(import_cmd)
        
        if result != 0:
            print(f"⚠️  Import completed with warnings (likely due to duplicate constraints)")
            print(f"   Continuing with verification...")
        
        if not os.path.exists(temp_db):
            print(f"❌ Failed to create new database")
            # Clean up
            if os.path.exists(dump_file):
                os.remove(dump_file)
            return False
        
        print(f"✅ New database created from dump")
        
        # Verify the new database
        print(f"\n🔍 Verifying repaired database...")
        conn_new = sqlite3.connect(temp_db)
        cursor_new = conn_new.cursor()
        
        # Check integrity
        cursor_new.execute("PRAGMA integrity_check;")
        new_results = cursor_new.fetchall()
        
        new_is_ok = all(result[0] == "ok" for result in new_results)
        
        if not new_is_ok:
            print(f"❌ Repaired database still has integrity issues:")
            for result in new_results:
                if result[0] != "ok":
                    print(f"   {result[0]}")
            conn_new.close()
            return False
        
        print(f"✅ Repaired database integrity: OK")
        
        # Get product count in repaired database (if table exists)
        try:
            cursor_new.execute("SELECT COUNT(*) FROM products")
            final_count = cursor_new.fetchone()[0]
            print(f"📦 Products in repaired database: {final_count:,}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Could not verify product count: {e}")
            print(f"   Checking available tables...")
            cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor_new.fetchall()
            if tables:
                print(f"   Available tables: {', '.join([t[0] for t in tables])}")
            else:
                print(f"   ❌ No tables found in repaired database!")
                conn_new.close()
                return False
        
        conn_new.close()
        
        # Replace original with repaired
        print(f"\n🔄 Step 4: Replacing corrupted database with repaired version...")
        
        # Create another backup of the corrupted file
        corrupted_backup = f"{db_path}.corrupted_{timestamp}"
        shutil.copy2(db_path, corrupted_backup)
        
        # Replace with repaired
        shutil.move(temp_db, db_path)
        
        print(f"✅ Database replaced with repaired version")
        
        # Clean up dump file
        if os.path.exists(dump_file):
            os.remove(dump_file)
            print(f"✅ Cleaned up temporary dump file")
        
        # Final verification
        print(f"\n🔍 Final verification...")
        conn_final = sqlite3.connect(db_path)
        cursor_final = conn_final.cursor()
        
        cursor_final.execute("PRAGMA integrity_check;")
        final_results = cursor_final.fetchall()
        
        if all(result[0] == "ok" for result in final_results):
            print(f"✅ Final integrity check: PASSED")
        else:
            print(f"⚠️  Final integrity check has warnings:")
            for result in final_results:
                print(f"   {result[0]}")
        
        # Optimize the database
        print(f"\n🧹 Optimizing repaired database...")
        cursor_final.execute("VACUUM;")
        cursor_final.execute("ANALYZE;")
        conn_final.commit()
        
        new_size_mb = os.path.getsize(db_path) / 1024 / 1024
        print(f"✅ Database optimized")
        
        conn_final.close()
        
        # Summary
        print("\n" + "=" * 60)
        print("REPAIR SUMMARY")
        print("=" * 60)
        print(f"Original size:       {db_size_mb:.2f} MB")
        print(f"Repaired size:       {new_size_mb:.2f} MB")
        print(f"Products before:     {initial_count if isinstance(initial_count, int) else 'unknown'}")
        print(f"Products after:      {final_count:,}")
        print(f"\nBackup files created:")
        print(f"  - {backup_path}")
        print(f"  - {corrupted_backup}")
        print(f"\n✅ Database repair completed successfully!")
        print(f"\n💡 You can now run the duplicate cleanup script:")
        print(f"   python3 pythonanywhere_cleanup_duplicates.py --dry-run")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during repair: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temp files
        if 'temp_db' in locals() and os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except:
                pass
        if 'dump_file' in locals() and os.path.exists(dump_file):
            try:
                os.remove(dump_file)
            except:
                pass
        
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Repair corrupted SQLite database on PythonAnywhere',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
This script repairs database corruption by:
1. Creating a backup of the corrupted database
2. Dumping the database to SQL format
3. Creating a new database from the SQL dump
4. Verifying the new database integrity
5. Replacing the corrupted database with the repaired version

Examples:
  # Repair Bothell store database
  python3 pythonanywhere_repair_database.py
  
  # Repair specific store
  python3 pythonanywhere_repair_database.py --store AGT_Issaquah
        '''
    )
    
    parser.add_argument('--store', default='AGT_Bothell',
                       help='Store name (default: AGT_Bothell)')
    
    args = parser.parse_args()
    
    # Find database
    db_path = find_database_path(args.store)
    
    if not db_path:
        print(f"❌ Could not find database for store: {args.store}")
        print(f"\nSearched in:")
        print(f"  - uploads/product_database_{args.store}.db")
        print(f"  - product_database_{args.store}.db")
        print(f"  - Current directory and subdirectories")
        sys.exit(1)
    
    # Run repair
    success = repair_database(db_path)
    
    if success:
        print(f"\n✅ Repair completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Repair failed")
        print(f"\n💡 You can restore from backup if needed:")
        print(f"   The original database was backed up before repair")
        sys.exit(1)

if __name__ == "__main__":
    main()
