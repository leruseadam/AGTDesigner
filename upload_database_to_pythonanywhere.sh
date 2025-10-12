#!/bin/bash
# Script to prepare database for PythonAnywhere upload

echo "================================================"
echo "Preparing Database for PythonAnywhere Upload"
echo "================================================"

cd "$(dirname "$0")"

DB_FILE="uploads/product_database_AGT_Bothell.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="database_for_pythonanywhere_${TIMESTAMP}.zip"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Error: Database not found at $DB_FILE"
    exit 1
fi

# Check database is valid
echo ""
echo "Checking database integrity..."
if sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -q "ok"; then
    echo "✓ Database integrity: OK"
else
    echo "❌ Database integrity check failed!"
    exit 1
fi

# Check for normalized_name column
echo "Checking schema..."
if sqlite3 "$DB_FILE" "PRAGMA table_info(strains);" | grep -q "normalized_name"; then
    echo "✓ normalized_name column: Present"
else
    echo "❌ Warning: normalized_name column missing!"
fi

# Get database size
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo "✓ Database size: $DB_SIZE"

# Create zip file
echo ""
echo "Creating zip file..."
if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
fi

cd uploads
zip -q "../${ZIP_NAME}" "product_database_AGT_Bothell.db"
cd ..

if [ -f "$ZIP_NAME" ]; then
    ZIP_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
    echo "✓ Created: $ZIP_NAME ($ZIP_SIZE)"
else
    echo "❌ Failed to create zip file"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ SUCCESS! Database ready for upload"
echo "================================================"
echo ""
echo "Zip file: $ZIP_NAME"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Files tab"
echo "2. Navigate to: /home/adamcordova/AGTDesigner"
echo "3. Click 'Upload a file' and select: $ZIP_NAME"
echo "4. In PythonAnywhere Bash console, run:"
echo ""
echo "   cd ~/AGTDesigner"
echo "   unzip -o ${ZIP_NAME}"
echo "   mv product_database_AGT_Bothell.db uploads/"
echo "   rm ${ZIP_NAME}"
echo ""
echo "5. Reload your web app"
echo ""
echo "Full instructions in: DATABASE_UPLOAD_TO_PYTHONANYWHERE.md"
echo "================================================"

