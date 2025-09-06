#!/usr/bin/env python3
"""
Create a small test database for upload
"""

import sqlite3
import os

def create_test_database():
    """Create a small test database with sample data"""
    db_file = 'test_database.db'
    
    # Remove existing test database
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Create new database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create tables with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            strain_id INTEGER,
            product_type TEXT NOT NULL,
            vendor TEXT,
            brand TEXT,
            description TEXT,
            weight TEXT,
            units TEXT,
            price TEXT,
            lineage TEXT,
            first_seen_date TEXT NOT NULL,
            last_seen_date TEXT NOT NULL,
            total_occurrences INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (strain_id) REFERENCES strains (id),
            UNIQUE(product_name, vendor, brand)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strain_name TEXT UNIQUE NOT NULL,
            normalized_name TEXT NOT NULL,
            canonical_lineage TEXT,
            first_seen_date TEXT NOT NULL,
            last_seen_date TEXT NOT NULL,
            total_occurrences INTEGER DEFAULT 1,
            lineage_confidence REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Create lineage_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lineage_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strain_id INTEGER,
            old_lineage TEXT,
            new_lineage TEXT,
            change_date TEXT NOT NULL,
            change_reason TEXT,
            FOREIGN KEY (strain_id) REFERENCES strains (id)
        )
    ''')
    
    # Create strain_brand_lineage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strain_brand_lineage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strain_id INTEGER,
            brand TEXT,
            lineage TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (strain_id) REFERENCES strains (id)
        )
    ''')
    
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # Insert sample strains first
    strains = [
        ('Blue Dream', 'blue dream', 'Blueberry x Haze', now, now, 1, 0.9, now, now),
        ('OG Kush', 'og kush', 'Chemdawg x Hindu Kush', now, now, 1, 0.95, now, now),
        ('Sour Diesel', 'sour diesel', 'Chemdawg x Super Skunk', now, now, 1, 0.85, now, now),
        ('Girl Scout Cookies', 'girl scout cookies', 'OG Kush x Durban Poison', now, now, 1, 0.9, now, now),
        ('White Widow', 'white widow', 'Brazilian Sativa x South Indian Indica', now, now, 1, 0.88, now, now)
    ]
    
    cursor.executemany('''
        INSERT INTO strains (strain_name, normalized_name, canonical_lineage, first_seen_date, last_seen_date, total_occurrences, lineage_confidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', strains)
    
    # Get strain IDs for products
    cursor.execute('SELECT id, strain_name FROM strains')
    strain_data = cursor.fetchall()
    strain_map = {name: id for id, name in strain_data}
    
    # Insert sample products
    products = [
        ('Blue Dream Flower', 'blue dream flower', strain_map['Blue Dream'], 'Flower', 'Green Valley', 'Green Valley', 'Classic hybrid strain', '3.5g', 'grams', '45.00', 'Blueberry x Haze', now, now, 1, now, now),
        ('OG Kush Pre-roll', 'og kush pre-roll', strain_map['OG Kush'], 'Pre-roll', 'Mountain High', 'Mountain High', 'Popular indica strain', '1g', 'grams', '12.00', 'Chemdawg x Hindu Kush', now, now, 1, now, now),
        ('Sour Diesel Vape', 'sour diesel vape', strain_map['Sour Diesel'], 'Vape Cartridge', 'City Lights', 'City Lights', 'Energizing sativa', '0.5g', 'grams', '60.00', 'Chemdawg x Super Skunk', now, now, 1, now, now),
        ('GSC Edible', 'gsc edible', strain_map['Girl Scout Cookies'], 'Edible', 'Cookie Co', 'Cookie Co', 'Sweet hybrid strain', '100mg', 'mg', '25.00', 'OG Kush x Durban Poison', now, now, 1, now, now),
        ('White Widow Concentrate', 'white widow concentrate', strain_map['White Widow'], 'Concentrate', 'White Label', 'White Label', 'Balanced hybrid', '1g', 'grams', '80.00', 'Brazilian Sativa x South Indian Indica', now, now, 1, now, now)
    ]
    
    cursor.executemany('''
        INSERT INTO products (product_name, normalized_name, strain_id, product_type, vendor, brand, description, weight, units, price, lineage, first_seen_date, last_seen_date, total_occurrences, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    # Check file size
    file_size = os.path.getsize(db_file)
    print(f"✅ Test database created: {db_file}")
    print(f"📊 File size: {file_size / 1024:.1f} KB")
    
    return db_file

if __name__ == "__main__":
    create_test_database()
