#!/bin/bash
echo "=========================================================================="
echo "PYTHONANYWHERE DATABASE HEALTH CHECK & REPAIR"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "❌ Error: Project directory not found"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# Check if database exists
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "❌ Error: Database not found at uploads/product_database_AGT_Bothell.db"
    echo "🔍 Looking for database files..."
    find . -name "*.db" -type f 2>/dev/null
    exit 1
fi

echo "✅ Database found: uploads/product_database_AGT_Bothell.db"
echo ""

# Check database size
DB_SIZE=$(du -h uploads/product_database_AGT_Bothell.db | cut -f1)
echo "📊 Database size: $DB_SIZE"
echo ""

# Check database integrity
echo "🔍 Checking database integrity..."
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
    
    # Check for weight issues
    cursor.execute('''
        SELECT COUNT(*) FROM products 
        WHERE \"Weight*\" IS NULL OR \"Units\" IS NULL 
        OR \"Weight*\" = \"\" OR \"Units\" = \"\"
    ''')
    missing_weight_count = cursor.fetchone()[0]
    
    if missing_weight_count > 0:
        print(f'⚠️  Products with missing weights/units: {missing_weight_count}')
    else:
        print('✅ All products have weights and units')
    
    # Check Constellation Moonshots specifically
    cursor.execute('''
        SELECT COUNT(*) FROM products 
        WHERE \"Product Name*\" LIKE \"%Moonshot%\" 
        AND \"Product Brand\" = \"Constellation Cannabis\"
    ''')
    moonshot_count = cursor.fetchone()[0]
    print(f'🌙 Constellation Moonshots found: {moonshot_count}')
    
    if moonshot_count > 0:
        cursor.execute('''
            SELECT COUNT(*) FROM products 
            WHERE \"Product Name*\" LIKE \"%Moonshot%\" 
            AND \"Product Brand\" = \"Constellation Cannabis\"
            AND \"Weight*\" = \"1.7\" AND \"Units\" = \"oz\"
        ''')
        correct_moonshots = cursor.fetchone()[0]
        
        if correct_moonshots == moonshot_count:
            print('✅ All Moonshots have correct weights (1.7 oz)')
        else:
            print(f'⚠️  {moonshot_count - correct_moonshots} Moonshots need weight correction')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Database check failed: {e}')
    sys.exit(1)
"

echo ""
echo "🔧 Running database repairs..."

# Run weight fixes
echo "1️⃣ Fixing Constellation Moonshot weights..."
python3 fix_database_weights.py moonshots

echo ""
echo "2️⃣ Running general weight audit..."
python3 fix_database_weights.py audit

echo ""
echo "=========================================================================="
echo "✅ DATABASE CHECK & REPAIR COMPLETE!"
echo "=========================================================================="
echo ""
echo "📋 Next steps:"
echo "   1. Go to PythonAnywhere 'Web' tab"
echo "   2. Click the big green 'Reload' button"
echo "   3. Test your application"
echo ""
echo "🔍 To verify fixes, run:"
echo "   python3 -c \"import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); cursor = conn.cursor(); cursor.execute('SELECT \\\"Product Name*\\\", \\\"Weight*\\\", \\\"Units\\\" FROM products WHERE \\\"Product Name*\\\" LIKE \\\"%Moonshot%\\\" AND \\\"Product Brand\\\" = \\\"Constellation Cannabis\\\" ORDER BY \\\"Product Name*\\\"'); [print(f'{row[0]}: {row[1]} {row[2]}') for row in cursor.fetchall()]; conn.close()\""
echo ""
