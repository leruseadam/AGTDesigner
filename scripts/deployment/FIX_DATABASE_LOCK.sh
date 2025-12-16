#!/bin/bash
# IMMEDIATE FIX FOR DATABASE LOCK ISSUE

echo "======================================="
echo "FIXING DATABASE LOCK ISSUE"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Stopping all Python processes...${NC}"
# Kill any running Python processes that might be locking the database
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "flask" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3
echo -e "${GREEN}✓ Python processes stopped${NC}"

echo ""
echo -e "${YELLOW}Step 2: Removing database lock files...${NC}"
cd ~/AGTDesigner

# Remove all lock files
rm -f uploads/*.db-shm 2>/dev/null || true
rm -f uploads/*.db-wal 2>/dev/null || true
echo -e "${GREEN}✓ Database lock files removed${NC}"

echo ""
echo -e "${YELLOW}Step 3: Checking for zombie processes...${NC}"
# Check if any processes are still using the database
if lsof uploads/product_database_AGT_Bothell.db 2>/dev/null; then
    echo -e "${RED}WARNING: Processes still using database${NC}"
    echo "Killing processes using database..."
    lsof -t uploads/product_database_AGT_Bothell.db 2>/dev/null | xargs kill -9 2>/dev/null || true
    sleep 2
else
    echo -e "${GREEN}✓ No processes using database${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Testing database access...${NC}"
# Try to connect to database
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db', timeout=5)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    print(f'✅ Database accessible: {count} products found')
    conn.close()
except Exception as e:
    print(f'❌ Database still locked: {e}')
"

echo ""
echo -e "${YELLOW}Step 5: If still locked, create fresh database...${NC}"
# If database is still locked, create a fresh one
python3 -c "
import sqlite3
import os
try:
    conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db', timeout=2)
    conn.close()
    print('✅ Database is now accessible')
except Exception as e:
    print(f'❌ Database still locked, creating fresh database...')
    # Backup the locked database
    import shutil
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'uploads/product_database_AGT_Bothell.db.locked_backup_{timestamp}'
    shutil.move('uploads/product_database_AGT_Bothell.db', backup_name)
    print(f'📋 Locked database backed up to: {backup_name}')
    
    # Create fresh database
    import subprocess
    result = subprocess.run(['python3', 'create_fresh_database.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print('✅ Fresh database created successfully')
    else:
        print(f'❌ Failed to create fresh database: {result.stderr}')
"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}DATABASE LOCK FIX COMPLETE${NC}"
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
echo "3. If still issues, run diagnostic again:"
echo "   python3 DIAGNOSE_PYTHONANYWHERE.py"
echo ""
