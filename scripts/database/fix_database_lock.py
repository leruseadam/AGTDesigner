#!/usr/bin/env python3
"""
Fix database lock issue on PythonAnywhere
"""
import sqlite3
import os
import time

def fix_database_lock():
    """Fix database lock issues"""
    print("🔧 Fixing database lock issues...")
    
    # Common database paths
    db_paths = [
        "uploads/product_database_AGT_Bothell.db",
        "uploads/product_database.db",
        "product_database_AGT_Bothell.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"📁 Found database: {db_path}")
            
            try:
                # Try to connect and run a simple query
                conn = sqlite3.connect(db_path, timeout=10.0)
                cursor = conn.cursor()
                
                # Test query
                cursor.execute("SELECT COUNT(*) FROM products LIMIT 1")
                count = cursor.fetchone()[0]
                print(f"✅ Database accessible: {count} products")
                
                # Close connection properly
                conn.close()
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    print(f"🔒 Database locked: {db_path}")
                    print("💡 Solution: Restart the web app on PythonAnywhere")
                    return False
                else:
                    print(f"❌ Database error: {e}")
                    return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
    
    print("✅ Database lock check complete")
    return True

if __name__ == "__main__":
    fix_database_lock()
