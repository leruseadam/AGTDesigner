#!/bin/bash
# PythonAnywhere Emergency Fix Script
# Run this script to fix the current database corruption and disk quota issues

echo "🚨 PYTHONANYWHERE EMERGENCY FIX"
echo "================================"

# Step 1: Remove all corrupted database files
echo "🗑️  Step 1: Removing corrupted database files..."
rm -f uploads/product_database_AGT_Bothell.db.corrupted.*
rm -f uploads/backups/*
rm -f uploads/*.db-shm uploads/*.db-wal uploads/*.db-journal
rm -f *.zip
rm -f uploads/*.zip

# Step 2: Check disk usage
echo "📊 Step 2: Checking disk usage..."
du -sh .

# Step 3: Create minimal database
echo "🔧 Step 3: Creating minimal database..."
python3 -c "
import sqlite3
import os

# Remove existing database
db_path = 'uploads/product_database_AGT_Bothell.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print('Removed existing database')

# Create new minimal database
conn = sqlite3.connect(db_path)

# Essential tables only
conn.execute('''
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
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS strains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        lineage TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Essential indexes only
conn.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(ProductName)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name)')

conn.commit()
conn.close()
print('✅ Minimal database created successfully')
"

# Step 4: Check final disk usage
echo "📊 Step 4: Final disk usage check..."
du -sh .

echo "✅ EMERGENCY FIX COMPLETE!"
echo "   - All corrupted files removed"
echo "   - Minimal database created"
echo "   - Ready to restart Flask application"
