#!/usr/bin/env python3
"""
Database Migration Tool
Exports data from local database and imports it to web version
"""

import sqlite3
import requests
import json
import os
import sys
from typing import Dict, List, Any
import time

class DatabaseMigrator:
    def __init__(self, local_db_path: str, web_base_url: str):
        self.local_db_path = local_db_path
        self.web_base_url = web_base_url.rstrip('/')
        self.session = requests.Session()
        
    def export_products(self, batch_size: int = 1000) -> List[Dict[str, Any]]:
        """Export products from local database in batches"""
        print(f"Exporting products from {self.local_db_path}...")
        
        conn = sqlite3.connect(self.local_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"Found {total_products} products to export")
        
        products = []
        offset = 0
        
        while offset < total_products:
            cursor.execute(f"""
                SELECT p.*, s.strain_name, s.canonical_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                LIMIT {batch_size} OFFSET {offset}
            """)
            
            batch = [dict(row) for row in cursor.fetchall()]
            products.extend(batch)
            offset += batch_size
            
            print(f"Exported {len(products)}/{total_products} products...")
        
        conn.close()
        return products
    
    def export_strains(self) -> List[Dict[str, Any]]:
        """Export strains from local database"""
        print(f"Exporting strains from {self.local_db_path}...")
        
        conn = sqlite3.connect(self.local_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM strains")
        strains = [dict(row) for row in cursor.fetchall()]
        
        print(f"Found {len(strains)} strains to export")
        conn.close()
        return strains
    
    def clear_web_database(self):
        """Clear the web database before import"""
        print("Clearing web database...")
        try:
            response = self.session.post(f"{self.web_base_url}/api/clear-database")
            if response.status_code == 200:
                print("Web database cleared successfully")
            else:
                print(f"Warning: Could not clear web database: {response.status_code}")
        except Exception as e:
            print(f"Warning: Could not clear web database: {e}")
    
    def import_strains(self, strains: List[Dict[str, Any]]):
        """Import strains to web database"""
        print(f"Importing {len(strains)} strains...")
        
        batch_size = 100
        for i in range(0, len(strains), batch_size):
            batch = strains[i:i + batch_size]
            
            try:
                response = self.session.post(
                    f"{self.web_base_url}/api/import-strains",
                    json={"strains": batch},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"Imported strains batch {i//batch_size + 1}/{(len(strains)-1)//batch_size + 1}")
                else:
                    print(f"Error importing strains batch: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Error importing strains batch: {e}")
            
            time.sleep(0.1)  # Small delay to avoid overwhelming the server
    
    def import_products(self, products: List[Dict[str, Any]]):
        """Import products to web database"""
        print(f"Importing {len(products)} products...")
        
        batch_size = 50  # Smaller batch size for products due to size
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            try:
                response = self.session.post(
                    f"{self.web_base_url}/api/import-products",
                    json={"products": batch},
                    timeout=60
                )
                
                if response.status_code == 200:
                    print(f"Imported products batch {i//batch_size + 1}/{(len(products)-1)//batch_size + 1}")
                else:
                    print(f"Error importing products batch: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Error importing products batch: {e}")
            
            time.sleep(0.2)  # Small delay to avoid overwhelming the server
    
    def verify_import(self):
        """Verify the import was successful"""
        print("Verifying import...")
        
        try:
            response = self.session.get(f"{self.web_base_url}/api/database-stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"Web database stats: {stats}")
                return stats
            else:
                print(f"Error getting database stats: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error verifying import: {e}")
            return None
    
    def migrate(self):
        """Perform the complete migration"""
        print("Starting database migration...")
        
        # Export data
        strains = self.export_strains()
        products = self.export_products()
        
        # Clear web database
        self.clear_web_database()
        
        # Import data
        self.import_strains(strains)
        self.import_products(products)
        
        # Verify
        self.verify_import()
        
        print("Migration completed!")

def main():
    if len(sys.argv) != 3:
        print("Usage: python database_migration_tool.py <local_db_path> <web_base_url>")
        print("Example: python database_migration_tool.py uploads/product_database.db https://your-app.pythonanywhere.com")
        sys.exit(1)
    
    local_db_path = sys.argv[1]
    web_base_url = sys.argv[2]
    
    if not os.path.exists(local_db_path):
        print(f"Error: Local database file not found: {local_db_path}")
        sys.exit(1)
    
    migrator = DatabaseMigrator(local_db_path, web_base_url)
    migrator.migrate()

if __name__ == "__main__":
    main()
