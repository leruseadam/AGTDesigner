#!/bin/bash
# Upload fixed local database to PythonAnywhere

echo "================================================================================"
echo "UPLOAD FIXED DATABASE TO PYTHONANYWHERE"
echo "================================================================================"
echo ""

# Create zip of just the fixed database
echo "Creating zip of fixed database..."
cd uploads
zip -j database_fixed.zip product_database_AGT_Bothell.db
cd ..

echo "✓ Created database_fixed.zip ($(du -h uploads/database_fixed.zip | cut -f1))"
echo ""

echo "================================================================================"
echo "NEXT STEPS - UPLOAD TO PYTHONANYWHERE"
echo "================================================================================"
echo ""
echo "METHOD 1: Web Upload (Easiest)"
echo "--------------------------------------------------------------------------------"
echo "1. Go to PythonAnywhere Files tab"
echo "2. Navigate to: /home/adamcordova/AGTDesigner/uploads/"
echo "3. Click 'Upload a file'"
echo "4. Select: uploads/database_fixed.zip (from your Downloads)"
echo "5. In PythonAnywhere Bash console, run:"
echo "   cd ~/AGTDesigner/uploads"
echo "   rm product_database_AGT_Bothell.db*  # Remove corrupted files"
echo "   unzip database_fixed.zip"
echo "   rm database_fixed.zip"
echo ""
echo "METHOD 2: SCP Upload (Faster)"
echo "--------------------------------------------------------------------------------"
echo "From your local terminal:"
echo "   scp uploads/database_fixed.zip adamcordova@ssh.pythonanywhere.com:~/AGTDesigner/uploads/"
echo ""
echo "Then in PythonAnywhere Bash console:"
echo "   cd ~/AGTDesigner/uploads"
echo "   rm product_database_AGT_Bothell.db*"
echo "   unzip database_fixed.zip"
echo "   rm database_fixed.zip"
echo ""
echo "================================================================================"

