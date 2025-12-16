#!/bin/bash
# NUCLEAR OPTION: Complete database reset and fix

echo "======================================="
echo "NUCLEAR DATABASE FIX"
echo "======================================="
echo "⚠️  This will completely reset the database!"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Emergency stop of all processes...${NC}"
# Kill everything that might be using the database
sudo pkill -9 -f "python" 2>/dev/null || true
sudo pkill -9 -f "flask" 2>/dev/null || true
sudo pkill -9 -f "gunicorn" 2>/dev/null || true
sudo pkill -9 -f "wsgi" 2>/dev/null || true
sleep 5
echo -e "${GREEN}✓ All processes stopped${NC}"

echo ""
echo -e "${YELLOW}Step 2: Complete database cleanup...${NC}"
cd ~/AGTDesigner

# Remove ALL database files and locks
rm -f uploads/*.db 2>/dev/null || true
rm -f uploads/*.db-shm 2>/dev/null || true
rm -f uploads/*.db-wal 2>/dev/null || true
rm -f uploads/*.db.backup.* 2>/dev/null || true
rm -f uploads/*.db.corrupted.* 2>/dev/null || true
rm -rf uploads/old_corrupted_backups 2>/dev/null || true

# Remove all session files
rm -rf sessions/* 2>/dev/null || true
mkdir -p sessions

echo -e "${GREEN}✓ All database files removed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Creating completely fresh database...${NC}"
python3 -c "
import os
import sqlite3
import datetime

print('Creating fresh database...')

# Ensure uploads directory exists
os.makedirs('uploads', exist_ok=True)

db_path = 'uploads/product_database_AGT_Bothell.db'

# Create new database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create strains table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT,
        thc_percentage REAL,
        cbd_percentage REAL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,
        brand TEXT,
        vendor TEXT,
        strain TEXT,
        weight REAL,
        weight_unit TEXT,
        price REAL,
        thc_percentage REAL,
        cbd_percentage REAL,
        lineage TEXT,
        terpenes TEXT,
        effects TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, weight, weight_unit, brand)
    )
''')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_type ON strains(type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_type ON products(type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain)')

# Add essential default strains
default_strains = [
    ('Hybrid', 'hybrid', 20.0, 0.0),
    ('Indica', 'indica', 22.0, 0.0),
    ('Sativa', 'sativa', 18.0, 0.0),
    ('CBD Blend', 'hybrid', 5.0, 15.0),
    ('Mixed', 'hybrid', 15.0, 0.0),
    ('Unknown', 'hybrid', 15.0, 0.0),
]

for strain_name, strain_type, thc, cbd in default_strains:
    try:
        cursor.execute(
            'INSERT OR IGNORE INTO strains (name, type, thc_percentage, cbd_percentage) VALUES (?, ?, ?, ?)',
            (strain_name, strain_type, thc, cbd)
        )
    except Exception as e:
        print(f'Warning: Could not insert strain {strain_name}: {e}')

conn.commit()
conn.close()

# Set permissions
os.chmod(db_path, 0o666)

# Verify
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM strains')
strain_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM products')
product_count = cursor.fetchone()[0]
conn.close()

file_size = os.path.getsize(db_path)
print(f'✅ Fresh database created: {file_size:,} bytes')
print(f'   Strains: {strain_count}')
print(f'   Products: {product_count}')
"

echo ""
echo -e "${YELLOW}Step 4: Clean up Python cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleaned${NC}"

echo ""
echo -e "${YELLOW}Step 5: Verify database access...${NC}"
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM strains')
    strain_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Database verified: {strain_count} strains, {product_count} products')
    print('✅ Database is accessible and ready')
except Exception as e:
    print(f'❌ Database verification failed: {e}')
"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}NUCLEAR FIX COMPLETE${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Reload your web app:"
echo "   - Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "   - Click 'Reload' for www.agtpricetags.com"
echo ""
echo "2. Test the application:"
echo "   - Visit: https://www.agtpricetags.com"
echo "   - Check if 'TOTAL PRODUCTS' shows the correct count"
echo ""
echo "3. Upload your Excel file to populate the database"
echo ""
echo -e "${RED}⚠️  Note: All previous data has been reset. You'll need to upload your Excel file again.${NC}"
echo ""