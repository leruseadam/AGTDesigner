#!/bin/bash
echo "=========================================================================="
echo "EXCEL UPLOAD DIAGNOSIS - PYTHONANYWHERE"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "❌ Error: Project directory not found"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# Check database status
echo "🔍 Checking database status..."
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "✅ Database file exists"
    DB_SIZE=$(du -h uploads/product_database_AGT_Bothell.db | cut -f1)
    echo "📊 Database size: $DB_SIZE"
    
    # Check database integrity
    python3 -c "
import sqlite3
import sys

try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
    cursor = conn.cursor()
    
    # Check integrity
    cursor.execute('PRAGMA integrity_check')
    result = cursor.fetchone()
    
    if result[0] == 'ok':
        print('✅ Database integrity: OK')
    else:
        print(f'❌ Database integrity issues: {result[0]}')
        sys.exit(1)
    
    # Count products
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    print(f'📦 Total products in database: {product_count}')
    
    # Check for recent uploads
    cursor.execute('SELECT COUNT(*) FROM products WHERE \"Source\" LIKE \"%Excel%\"')
    excel_products = cursor.fetchone()[0]
    print(f'📊 Products from Excel uploads: {excel_products}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Database check failed: {e}')
    sys.exit(1)
"
else
    echo "❌ Database file not found"
fi

echo ""

# Check uploads directory
echo "🔍 Checking uploads directory..."
ls -la uploads/ | head -10

echo ""

# Check for Excel files
echo "🔍 Checking for Excel files..."
find uploads/ -name "*.xlsx" -o -name "*.xls" | head -5

echo ""

# Check Python environment
echo "🔍 Checking Python environment..."
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import pandas as pd
    print(f'✅ Pandas version: {pd.__version__}')
except ImportError:
    print('❌ Pandas not available')

try:
    import openpyxl
    print(f'✅ Openpyxl version: {openpyxl.__version__}')
except ImportError:
    print('❌ Openpyxl not available')

try:
    import sqlite3
    print('✅ SQLite3 available')
except ImportError:
    print('❌ SQLite3 not available')
"

echo ""

# Test Excel processing
echo "🔍 Testing Excel processing capability..."
python3 -c "
import pandas as pd
import os

# Find an Excel file to test with
excel_files = []
for f in os.listdir('uploads/'):
    if f.endswith(('.xlsx', '.xls')):
        excel_files.append(f'uploads/{f}')

if excel_files:
    test_file = excel_files[0]
    print(f'Testing with: {test_file}')
    
    try:
        # Test basic read
        df = pd.read_excel(test_file, nrows=5, engine='openpyxl')
        print(f'✅ Excel read test: {len(df)} rows')
        print(f'Columns: {list(df.columns)[:5]}...')
        
        # Test database storage
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase('uploads/product_database_AGT_Bothell.db')
        db.init_database()
        print('✅ Database connection test: OK')
        
    except Exception as e:
        print(f'❌ Excel processing test failed: {e}')
else:
    print('❌ No Excel files found for testing')
"

echo ""
echo "=========================================================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================================================="
