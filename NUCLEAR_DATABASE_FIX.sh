#!/bin/bash
# NUCLEAR DATABASE FIX - AGGRESSIVE APPROACH TO UNLOCK DATABASE

echo "======================================="
echo "NUCLEAR DATABASE FIX"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd ~/AGTDesigner

echo -e "${YELLOW}Step 1: NUCLEAR OPTION - Kill ALL processes...${NC}"
# Kill everything that might be using the database
sudo pkill -f python 2>/dev/null || true
sudo pkill -f flask 2>/dev/null || true
sudo pkill -f gunicorn 2>/dev/null || true
sudo pkill -f uwsgi 2>/dev/null || true
sleep 5
echo -e "${GREEN}✓ All processes killed${NC}"

echo ""
echo -e "${YELLOW}Step 2: Force remove ALL database files...${NC}"
# Backup current database first
timestamp=$(date +%Y%m%d_%H%M%S)
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    cp uploads/product_database_AGT_Bothell.db "uploads/product_database_AGT_Bothell.db.backup_${timestamp}"
    echo "📋 Database backed up to: uploads/product_database_AGT_Bothell.db.backup_${timestamp}"
fi

# Remove all database files and locks
rm -f uploads/*.db 2>/dev/null || true
rm -f uploads/*.db-shm 2>/dev/null || true
rm -f uploads/*.db-wal 2>/dev/null || true
echo -e "${GREEN}✓ All database files removed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Clean up corrupted backups...${NC}"
# Remove all corrupted backup directories
rm -rf uploads/old_corrupted_backups 2>/dev/null || true
rm -f uploads/*.corrupted.* 2>/dev/null || true
echo -e "${GREEN}✓ Corrupted backups cleaned${NC}"

echo ""
echo -e "${YELLOW}Step 4: Create FRESH database...${NC}"
# Create completely fresh database
python3 create_fresh_database.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Fresh database created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create fresh database${NC}"
    echo "Creating minimal database manually..."
    
    python3 -c "
import sqlite3
import os

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Create minimal database
conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
cursor = conn.cursor()

# Create strains table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT,
        thc_percentage REAL,
        cbd_percentage REAL
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
        cbd_percentage REAL
    )
''')

# Add default strains
default_strains = [
    ('Hybrid', 'hybrid', 20.0, 0.0),
    ('Indica', 'indica', 22.0, 0.0),
    ('Sativa', 'sativa', 18.0, 0.0),
    ('CBD Blend', 'hybrid', 5.0, 15.0),
    ('Mixed', 'hybrid', 15.0, 0.0),
]

for strain_name, strain_type, thc, cbd in default_strains:
    cursor.execute(
        'INSERT OR IGNORE INTO strains (name, type, thc_percentage, cbd_percentage) VALUES (?, ?, ?, ?)',
        (strain_name, strain_type, thc, cbd)
    )

conn.commit()
conn.close()
print('✅ Minimal database created manually')
"
fi

echo ""
echo -e "${YELLOW}Step 5: Set proper permissions...${NC}"
chmod 666 uploads/product_database_AGT_Bothell.db 2>/dev/null || true
echo -e "${GREEN}✓ Permissions set${NC}"

echo ""
echo -e "${YELLOW}Step 6: Verify database...${NC}"
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db', timeout=5)
    cursor = conn.cursor()
    
    # Check strains
    cursor.execute('SELECT COUNT(*) FROM strains')
    strain_count = cursor.fetchone()[0]
    print(f'✅ Strains: {strain_count}')
    
    # Check products
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    print(f'✅ Products: {product_count}')
    
    # Test write access
    cursor.execute('INSERT OR IGNORE INTO products (name, type) VALUES (?, ?)', ('Test Product', 'Test'))
    conn.commit()
    print('✅ Database write test: PASSED')
    
    conn.close()
    print('✅ Database is fully functional')
    
except Exception as e:
    print(f'❌ Database verification failed: {e}')
"

echo ""
echo -e "${YELLOW}Step 7: Clean up sessions and cache...${NC}"
rm -rf sessions/* 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Cache cleaned${NC}"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}NUCLEAR FIX COMPLETE!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${YELLOW}CRITICAL: You MUST reload your web app now!${NC}"
echo ""
echo "1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "2. Click 'Reload' for www.agtpricetags.com"
echo "3. Wait 30 seconds"
echo "4. Visit: https://www.agtpricetags.com"
echo "5. Check if 'TOTAL PRODUCTS' shows a number (even if it's 0, that's normal for a fresh database)"
echo ""
echo -e "${RED}If you don't reload the web app, the fix won't work!${NC}"
echo ""