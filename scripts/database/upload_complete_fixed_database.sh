#!/bin/bash

echo "================================================================================"
echo "CREATING COMPLETE FIXED DATABASE PACKAGE FOR PYTHONANYWHERE"
echo "================================================================================"
echo ""

# Check if database exists
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "❌ Error: Database not found at uploads/product_database_AGT_Bothell.db"
    exit 1
fi

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create zip file
echo "Creating database zip file..."
cd uploads
zip -9 product_database_AGT_Bothell_complete_${TIMESTAMP}.zip product_database_AGT_Bothell.db
cd ..

echo ""
echo "✅ Database package created!"
echo ""
echo "================================================================================"
echo "UPLOAD TO PYTHONANYWHERE - INSTRUCTIONS"
echo "================================================================================"
echo ""
echo "1. BACKUP THE CORRUPTED DATABASE (just in case):"
echo "   ssh adamcordova@ssh.pythonanywhere.com"
echo "   cd ~/AGTDesigner/uploads"
echo "   mv product_database_AGT_Bothell.db product_database_AGT_Bothell_corrupted_backup.db"
echo ""
echo "2. UPLOAD THE FIXED DATABASE:"
echo ""
echo "   Option A - Using scp (recommended):"
echo "   ---------------------------------------------------------------------"
echo "   scp uploads/product_database_AGT_Bothell_complete_${TIMESTAMP}.zip \\"
echo "       adamcordova@ssh.pythonanywhere.com:~/AGTDesigner/uploads/"
echo ""
echo "   Then on PythonAnywhere:"
echo "   ssh adamcordova@ssh.pythonanywhere.com"
echo "   cd ~/AGTDesigner/uploads"
echo "   unzip -o product_database_AGT_Bothell_complete_${TIMESTAMP}.zip"
echo "   rm product_database_AGT_Bothell_complete_${TIMESTAMP}.zip"
echo ""
echo "   Option B - Using PythonAnywhere web interface:"
echo "   ---------------------------------------------------------------------"
echo "   1. Go to: https://www.pythonanywhere.com/user/adamcordova/files/home/adamcordova/AGTDesigner/uploads"
echo "   2. Delete the corrupted product_database_AGT_Bothell.db"
echo "   3. Upload: uploads/product_database_AGT_Bothell_complete_${TIMESTAMP}.zip"
echo "   4. Click on the zip file and extract it"
echo ""
echo "3. VERIFY THE DATABASE:"
echo "   cd ~/AGTDesigner"
echo "   python3 -c \"import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); print('Database OK:', conn.execute('SELECT COUNT(*) FROM products').fetchone()[0], 'products'); conn.close()\""
echo ""
echo "4. RELOAD YOUR WEB APP:"
echo "   Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/#tab_id_adamcordova_pythonanywhere_com"
echo "   Click the green 'Reload' button"
echo ""
echo "================================================================================"
echo ""
echo "Database package location:"
echo "  $(pwd)/uploads/product_database_AGT_Bothell_complete_${TIMESTAMP}.zip"
echo ""
echo "================================================================================"

