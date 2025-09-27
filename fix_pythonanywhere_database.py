#!/usr/bin/env python3.11
"""
Fix corrupted database files on PythonAnywhere
Removes invalid database files and initializes fresh ones
"""

import os
import sqlite3
import shutil
from pathlib import Path

class DatabaseFixer:
    def __init__(self):
        self.project_dir = "/home/adamcordova/AGTDesigner"
        self.fixed_databases = []
        self.issues_found = []

    def print_header(self, title):
        print(f"\n{'='*50}")
        print(f"🔧 {title}")
        print(f"{'='*50}")

    def find_database_files(self):
        """Find all potential database files"""
        db_patterns = ['*.db', '*database*', '*.sqlite', '*.sqlite3']
        database_files = []
        
        for pattern in db_patterns:
            for db_file in Path(self.project_dir).rglob(pattern):
                if db_file.is_file():
                    database_files.append(str(db_file))
        
        return database_files

    def test_database_integrity(self, db_path):
        """Test if database file is valid"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            return True, len(tables)
        except sqlite3.DatabaseError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def backup_corrupted_file(self, db_path):
        """Backup corrupted database file"""
        backup_path = f"{db_path}.corrupted_backup"
        try:
            shutil.move(db_path, backup_path)
            print(f"   📦 Backed up corrupted file to: {backup_path}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to backup file: {e}")
            return False

    def fix_databases(self):
        """Fix all corrupted database files"""
        self.print_header("DATABASE CORRUPTION FIX")
        
        database_files = self.find_database_files()
        
        if not database_files:
            print("📋 No database files found")
            return
        
        print(f"🔍 Found {len(database_files)} database files:")
        
        for db_path in database_files:
            db_size = os.path.getsize(db_path)
            print(f"\n📄 Checking: {db_path}")
            print(f"   Size: {db_size:,} bytes")
            
            is_valid, result = self.test_database_integrity(db_path)
            
            if is_valid:
                print(f"   ✅ Valid database ({result} tables)")
                continue
            
            print(f"   ❌ Corrupted: {result}")
            self.issues_found.append(f"Corrupted database: {db_path}")
            
            # Backup corrupted file
            if self.backup_corrupted_file(db_path):
                self.fixed_databases.append(db_path)
                print(f"   🔧 Removed corrupted database file")

    def initialize_fresh_database(self):
        """Initialize a fresh database"""
        self.print_header("FRESH DATABASE INITIALIZATION")
        
        # Create the main database path
        main_db_path = os.path.join(self.project_dir, "product_database.db")
        
        try:
            # Create a fresh SQLite database
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            
            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT,
                    category TEXT,
                    price REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create strains table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT,
                    thc_percentage REAL,
                    cbd_percentage REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert sample data
            sample_products = [
                ("Sample Product", "Test Brand", "Accessories", 19.99, "Test product for initialization"),
                ("Dabber Tool", "AGT", "Tools", 15.00, "Standard dabber tool"),
                ("Glass Pipe", "Generic", "Smoking", 25.99, "Basic glass pipe"),
                ("Grinder", "Premium", "Accessories", 35.00, "4-piece herb grinder")
            ]
            
            cursor.executemany('''
                INSERT INTO products (name, brand, category, price, description)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_products)
            
            sample_strains = [
                ("Blue Dream", "Hybrid", 18.5, 0.5, "Popular balanced hybrid strain"),
                ("OG Kush", "Indica", 20.0, 0.3, "Classic indica-dominant strain")
            ]
            
            cursor.executemany('''
                INSERT INTO strains (name, type, thc_percentage, cbd_percentage, description)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_strains)
            
            conn.commit()
            conn.close()
            
            # Verify the new database
            is_valid, table_count = self.test_database_integrity(main_db_path)
            if is_valid:
                print(f"✅ Fresh database created successfully!")
                print(f"   📍 Location: {main_db_path}")
                print(f"   📊 Tables: {table_count}")
                print(f"   📦 Sample data: {len(sample_products)} products, {len(sample_strains)} strains")
            else:
                print(f"❌ Failed to create valid database: {table_count}")
                
        except Exception as e:
            print(f"❌ Error creating fresh database: {e}")
            return False
        
        return True

    def generate_report(self):
        """Generate fix report"""
        self.print_header("REPAIR REPORT")
        
        print(f"🔍 Issues found: {len(self.issues_found)}")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 Databases fixed: {len(self.fixed_databases)}")
        for i, db in enumerate(self.fixed_databases, 1):
            print(f"   {i}. {db}")
        
        print(f"\n🎯 NEXT STEPS:")
        print("="*20)
        print("1. 🔄 Reload your PythonAnywhere web app")
        print("2. 🧪 Test the application functionality")
        print("3. 📊 Upload your product data if needed")
        print("4. ✅ Switch to optimized WSGI once confirmed working:")
        print("   /home/adamcordova/AGTDesigner/wsgi_ultra_optimized.py")

    def run_fix(self):
        """Run complete database fix"""
        print("🚨 PythonAnywhere Database Corruption Fix")
        print("==========================================")
        
        # Change to project directory
        if os.path.exists(self.project_dir):
            os.chdir(self.project_dir)
        else:
            print(f"❌ Project directory not found: {self.project_dir}")
            return False
        
        self.fix_databases()
        
        # Always initialize fresh database (even if no corruption found)
        self.initialize_fresh_database()
        
        self.generate_report()
        return True

if __name__ == "__main__":
    fixer = DatabaseFixer()
    fixer.run_fix()