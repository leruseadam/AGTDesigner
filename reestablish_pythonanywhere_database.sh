#!/bin/bash
echo "=========================================================================="
echo "PYTHONANYWHERE DATABASE REESTABLISHMENT"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "❌ Error: Project directory not found"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# Create backup of current database (even if corrupted)
echo "💾 Creating backup of current database..."
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell.db.backup_corrupted_$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created: uploads/product_database_AGT_Bothell.db.backup_corrupted_$(date +%Y%m%d_%H%M%S)"
else
    echo "ℹ️  No existing database found to backup"
fi
echo ""

# Remove all database files to start fresh
echo "🗑️  Removing corrupted database files..."
rm -f uploads/product_database_AGT_Bothell.db
rm -f uploads/product_database_AGT_Bothell.db-wal
rm -f uploads/product_database_AGT_Bothell.db-shm
rm -f uploads/product_database.db
rm -f uploads/product_database.db-wal
rm -f uploads/product_database.db-shm
echo "✅ All database files removed"
echo ""

# Check if we have Excel files to rebuild from
echo "🔍 Looking for Excel files to rebuild database from..."
if [ -f "uploads/A Greener Today - Bothell_inventory_10-12-2025  6_37 AM.xlsx" ]; then
    EXCEL_FILE="uploads/A Greener Today - Bothell_inventory_10-12-2025  6_37 AM.xlsx"
    echo "✅ Found Excel file: $EXCEL_FILE"
elif [ -f "uploads/product_database/product_database.xlsx" ]; then
    EXCEL_FILE="uploads/product_database/product_database.xlsx"
    echo "✅ Found Excel file: $EXCEL_FILE"
else
    echo "⚠️  No Excel file found. Will create empty database."
    EXCEL_FILE=""
fi
echo ""

# Create new database using Python script
echo "🔧 Creating new database..."
python3 << 'PYTHONEOF'
import sqlite3
import os
from datetime import datetime

# Database path
db_path = 'uploads/product_database_AGT_Bothell.db'

print("Creating new database...")

# Create the database file
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        "Product Name*" TEXT,
        "ProductName" TEXT,
        "Description" TEXT,
        "Product Type*" TEXT,
        "Product Brand" TEXT,
        "Product Strain" TEXT,
        "Lineage" TEXT,
        "Vendor" TEXT,
        "Vendor/Supplier*" TEXT,
        "Price" TEXT,
        "Weight*" TEXT,
        "Weight" TEXT,
        "Units" TEXT,
        "Quantity*" TEXT,
        "Quantity" TEXT,
        "THC test result" REAL,
        "CBD test result" REAL,
        "Test result unit (% or mg)" TEXT,
        "State" TEXT DEFAULT 'active',
        "Is Sample? (yes/no)" TEXT DEFAULT 'no',
        "Is MJ product?(yes/no)" TEXT DEFAULT 'yes',
        "Discountable? (yes/no)" TEXT DEFAULT 'yes',
        "Room*" TEXT DEFAULT 'Default',
        "Medical Only (Yes/No)" TEXT DEFAULT 'No',
        "DOH" TEXT DEFAULT 'YES',
        "DOH Compliant (Yes/No)" TEXT DEFAULT 'Yes',
        "Source" TEXT DEFAULT 'Excel Upload',
        "created_at" TEXT DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create strains table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        strain_name TEXT UNIQUE,
        lineage TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create indexes for better performance
cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_name ON products("Product Name*")')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_brand ON products("Product Brand")')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor ON products("Vendor")')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_strain_name ON strains(strain_name)')

conn.commit()
conn.close()

print(f"✅ New database created: {db_path}")
PYTHONEOF

echo ""

# Verify database creation
echo "🔍 Verifying new database..."
python3 -c "
import sqlite3
import os

db_path = 'uploads/product_database_AGT_Bothell.db'

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute('PRAGMA integrity_check')
        result = cursor.fetchone()
        
        if result[0] == 'ok':
            print('✅ Database integrity: OK')
        else:
            print(f'❌ Database integrity issues: {result[0]}')
            exit(1)
        
        # Count tables
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
        tables = cursor.fetchall()
        print(f'📊 Tables created: {len(tables)}')
        
        # Check products table
        cursor.execute('SELECT COUNT(*) FROM products')
        product_count = cursor.fetchone()[0]
        print(f'📦 Products in database: {product_count}')
        
        conn.close()
        print('✅ Database verification successful!')
        
    except Exception as e:
        print(f'❌ Database verification failed: {e}')
        exit(1)
else:
    print(f'❌ Database file not found: {db_path}')
    exit(1)
"

echo ""
echo "🔧 Database reestablished successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Upload your Excel file through the web interface to populate the database"
echo "   2. Or run: python3 -c \"from src.core.data.excel_processor import ExcelProcessor; ep = ExcelProcessor(); ep.process_file('$EXCEL_FILE')\""
echo "   3. Go to PythonAnywhere 'Web' tab and click 'Reload'"
echo ""
echo "=========================================================================="
echo "✅ DATABASE REESTABLISHMENT COMPLETE!"
echo "=========================================================================="
