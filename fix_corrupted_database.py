#!/usr/bin/env python3
"""
Fix corrupted SQLite database by exporting and reimporting data.
"""

import sqlite3
import os
import shutil
from pathlib import Path
from datetime import datetime

def fix_corrupted_database(db_path):
    """
    Attempt to recover a corrupted SQLite database.
    
    Method 1: Try to dump and restore
    Method 2: Try PRAGMA integrity_check and recover what we can
    """
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print("="*80)
    print("DATABASE CORRUPTION REPAIR")
    print("="*80)
    print(f"Database: {db_path}")
    print()
    
    # Create backup first
    backup_path = db_path.parent / f"{db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"Creating backup: {backup_path.name}")
    try:
        shutil.copy2(db_path, backup_path)
        print("✓ Backup created")
    except Exception as e:
        print(f"⚠ Warning: Could not create backup: {e}")
    print()
    
    # Method 1: Try to dump and restore
    print("Method 1: Dump and Restore")
    print("-" * 80)
    
    dump_file = db_path.parent / f"{db_path.stem}_dump.sql"
    recovered_db = db_path.parent / f"{db_path.stem}_recovered.db"
    
    try:
        # Try to dump the database
        print("Attempting to dump database...")
        conn = sqlite3.connect(db_path)
        
        with open(dump_file, 'w') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        conn.close()
        print(f"✓ Database dumped to {dump_file.name}")
        
        # Create new database from dump
        print("Restoring from dump...")
        if recovered_db.exists():
            recovered_db.unlink()
        
        new_conn = sqlite3.connect(recovered_db)
        with open(dump_file, 'r') as f:
            new_conn.executescript(f.read())
        new_conn.close()
        
        print(f"✓ Recovered database created: {recovered_db.name}")
        print()
        
        # Verify the recovered database
        print("Verifying recovered database...")
        verify_conn = sqlite3.connect(recovered_db)
        cursor = verify_conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        
        verify_conn.close()
        
        print(f"✓ Products: {product_count}")
        print(f"✓ Strains: {strain_count}")
        print()
        
        # Replace old database with recovered one
        print("Replacing corrupted database with recovered version...")
        db_path.unlink()
        shutil.move(recovered_db, db_path)
        
        # Clean up dump file
        dump_file.unlink()
        
        print("="*80)
        print("✅ DATABASE SUCCESSFULLY RECOVERED!")
        print("="*80)
        print()
        print(f"Original (corrupted): {backup_path.name}")
        print(f"Recovered: {db_path.name}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        print()
        
        # Method 2: Try to recover what we can
        print("Method 2: Partial Recovery")
        print("-" * 80)
        
        try:
            print("Attempting to recover readable data...")
            
            old_conn = sqlite3.connect(db_path)
            old_cursor = old_conn.cursor()
            
            # Create new database
            if recovered_db.exists():
                recovered_db.unlink()
            
            new_conn = sqlite3.connect(recovered_db)
            new_cursor = new_conn.cursor()
            
            # Get schema
            print("Copying database schema...")
            old_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            tables = old_cursor.fetchall()
            
            for table_sql in tables:
                if table_sql[0]:
                    new_cursor.execute(table_sql[0])
            
            new_conn.commit()
            print("✓ Schema copied")
            
            # Try to copy data table by table
            old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in old_cursor.fetchall()]
            
            recovered_tables = []
            failed_tables = []
            
            for table_name in table_names:
                try:
                    print(f"Recovering {table_name}...")
                    old_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = old_cursor.fetchall()
                    
                    if rows:
                        # Get column count
                        col_count = len(rows[0])
                        placeholders = ','.join(['?' for _ in range(col_count)])
                        
                        new_cursor.executemany(
                            f"INSERT INTO {table_name} VALUES ({placeholders})",
                            rows
                        )
                        new_conn.commit()
                        recovered_tables.append((table_name, len(rows)))
                        print(f"  ✓ Recovered {len(rows)} rows")
                    else:
                        print(f"  ⚠ No data in {table_name}")
                        
                except Exception as table_error:
                    failed_tables.append((table_name, str(table_error)))
                    print(f"  ✗ Failed: {table_error}")
            
            old_conn.close()
            new_conn.close()
            
            print()
            print("Recovery Summary:")
            print(f"  Recovered: {len(recovered_tables)} tables")
            for table, count in recovered_tables:
                print(f"    • {table}: {count} rows")
            
            if failed_tables:
                print(f"  Failed: {len(failed_tables)} tables")
                for table, error in failed_tables:
                    print(f"    • {table}: {error}")
            
            if recovered_tables:
                print()
                print("Replacing corrupted database with partially recovered version...")
                db_path.unlink()
                shutil.move(recovered_db, db_path)
                
                print("="*80)
                print("⚠ DATABASE PARTIALLY RECOVERED")
                print("="*80)
                print()
                print("Some data was recovered. You may need to:")
                print("  1. Re-upload your latest Excel file")
                print("  2. Check for missing products")
                print()
                return True
            else:
                print()
                print("❌ Could not recover any data")
                return False
                
        except Exception as e2:
            print(f"❌ Method 2 also failed: {e2}")
            print()
            print("="*80)
            print("RECOVERY FAILED")
            print("="*80)
            print()
            print("Options:")
            print("  1. Restore from backup if you have one")
            print("  2. Delete the database and re-upload your Excel file")
            print()
            return False

if __name__ == "__main__":
    import sys
    
    # Default to AGT Bothell database
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "uploads/product_database_AGT_Bothell.db"
    
    print()
    success = fix_corrupted_database(db_path)
    
    if success:
        print("Next steps:")
        print("  1. Run: python3 fix_all_weights.py")
        print("  2. Reload your web app")
    else:
        print("If recovery failed, you can:")
        print("  1. Delete the corrupted database:")
        print(f"     rm {db_path}")
        print("  2. Upload your latest Excel file through the web interface")
        print("     This will recreate the database")
    print()

