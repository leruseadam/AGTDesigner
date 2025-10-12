#!/bin/bash
echo "=========================================================================="
echo "PYTHONANYWHERE CORRUPTED DATABASE REPAIR"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "❌ Error: Project directory not found"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# Check if database exists
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "❌ Error: Database not found at uploads/product_database_AGT_Bothell.db"
    exit 1
fi

echo "✅ Database found: uploads/product_database_AGT_Bothell.db"
echo ""

# Check database size
DB_SIZE=$(du -h uploads/product_database_AGT_Bothell.db | cut -f1)
echo "📊 Database size: $DB_SIZE"
echo ""

# Create backup before repair
echo "💾 Creating backup..."
cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
echo ""

# Run corruption repair
echo "🔧 Running database corruption repair..."
python3 fix_corrupted_database.py uploads/product_database_AGT_Bothell.db

echo ""
echo "🔍 Verifying repair..."
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
    
    conn.close()
    print('✅ Database repair successful!')
    
except Exception as e:
    print(f'❌ Database repair failed: {e}')
    sys.exit(1)
"

echo ""
echo "🔧 Now running weight fixes..."
python3 fix_database_weights.py moonshots

echo ""
echo "=========================================================================="
echo "✅ DATABASE REPAIR COMPLETE!"
echo "=========================================================================="
echo ""
echo "📋 Next steps:"
echo "   1. Go to PythonAnywhere 'Web' tab"
echo "   2. Click the big green 'Reload' button"
echo "   3. Test your application"
echo ""
