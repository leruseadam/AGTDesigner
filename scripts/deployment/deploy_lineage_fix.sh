#!/bin/bash
# Deploy lineage fix to PythonAnywhere
# Run this script ON PYTHONANYWHERE via SSH

set -e

echo "======================================="
echo "DEPLOYING LINEAGE FIX TO PYTHONANYWHERE"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd ~/AGTDesigner

echo -e "${BLUE}Current status...${NC}"
echo "Current directory: $(pwd)"
echo "Current git status:"
git status --porcelain | head -5

echo ""
echo -e "${YELLOW}1. Pulling latest lineage fix from GitHub...${NC}"
echo "Fetching latest commits..."
git fetch origin
echo "Latest commits available:"
git log --oneline origin/main -3

echo ""
echo "Resetting to latest main branch..."
git reset --hard origin/main
echo -e "${GREEN}✓ Code updated to latest version with lineage fix${NC}"

echo ""
echo "Verifying lineage fix commit:"
git log --oneline -1
echo ""

echo -e "${YELLOW}2. Checking database status...${NC}"
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    DB_SIZE=$(stat -c%s "uploads/product_database_AGT_Bothell.db")
    echo "Database file size: $DB_SIZE bytes"
    
    # Check if database has products
    PRODUCT_COUNT=$(sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;" 2>/dev/null || echo "0")
    echo "Products in database: $PRODUCT_COUNT"
    
    if [ "$PRODUCT_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  Database is empty - creating fresh database...${NC}"
        python3 create_fresh_database.py
        echo -e "${GREEN}✓ Fresh database created${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No database found - creating fresh database...${NC}"
    python3 create_fresh_database.py
    echo -e "${GREEN}✓ Fresh database created${NC}"
fi

echo ""
echo -e "${YELLOW}3. Testing lineage functionality...${NC}"
# Test if the lineage methods exist
python3 -c "
from src.core.data.product_database import ProductDatabase
db = ProductDatabase()
print('✓ ProductDatabase imported successfully')
print('✓ get_product_lineage method available:', hasattr(db, 'get_product_lineage'))
print('✓ update_product_lineage method available:', hasattr(db, 'update_product_lineage'))
"

echo ""
echo -e "${YELLOW}4. Cleaning up and setting permissions...${NC}"
# Remove lock files
rm -f uploads/*.db-shm uploads/*.db-wal 2>/dev/null || true

# Set proper permissions
chmod 666 uploads/product_database_AGT_Bothell.db 2>/dev/null || true

echo -e "${GREEN}✓ Permissions set${NC}"

echo ""
echo -e "${YELLOW}5. Checking Python dependencies...${NC}"
pip3 install --user -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}LINEAGE FIX DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${BLUE}What was deployed:${NC}"
echo "✓ Enhanced database lineage retrieval in DOCX generation"
echo "✓ Added get_product_lineage() method to ProductDatabase class"
echo "✓ Enhanced lineage update process to save directly to database"
echo "✓ Fixed lineage override logic to check database first"
echo "✓ Improved logging for lineage override process"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload www.agtpricetags.com'"
echo "3. Test lineage changes:"
echo "   - Change lineage in dropdown"
echo "   - Generate DOCX"
echo "   - Verify lineage appears in generated labels"
echo ""
echo "To check logs if issues persist:"
echo "  tail -f /var/log/www.agtpricetags.com.error.log"
echo ""
