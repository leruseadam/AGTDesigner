#!/bin/bash
# Script to fix database weights on PythonAnywhere
# Run this in a Bash console on PythonAnywhere

echo "=========================================================================="
echo "PYTHONANYWHERE DATABASE WEIGHT FIX"
echo "=========================================================================="
echo ""

# Navigate to project directory
cd ~/AGTDesigner || { echo "Error: Project directory not found"; exit 1; }

echo "Current directory: $(pwd)"
echo ""

# Check if database exists
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "❌ Error: Database not found at uploads/product_database_AGT_Bothell.db"
    exit 1
fi

echo "✓ Database found"
echo ""

# Run the fix script
echo "Running Constellation Moonshot weight normalization..."
echo ""

python3 fix_database_weights.py moonshots

echo ""
echo "=========================================================================="
echo "COMPLETE!"
echo "=========================================================================="
echo ""
echo "To verify the fix, run:"
echo "  python3 -c \"import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); cursor = conn.cursor(); cursor.execute('SELECT \\\"Product Name*\\\", \\\"Weight*\\\", \\\"Units\\\" FROM products WHERE \\\"Product Name*\\\" LIKE \\\"%Moonshot%\\\" AND \\\"Product Brand\\\" = \\\"Constellation Cannabis\\\" ORDER BY \\\"Product Name*\\\"'); [print(f'{row[0]}: {row[1]} {row[2]}') for row in cursor.fetchall()]; conn.close()\""
echo ""
echo "After fixing, remember to reload your web app!"

