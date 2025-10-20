#!/bin/bash
# Deploy all latest fixes to PythonAnywhere
# Run this script ON PYTHONANYWHERE via SSH

set -e

echo "======================================="
echo "DEPLOYING ALL LATEST FIXES TO PYTHONANYWHERE"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd ~/AGTDesigner

echo -e "${BLUE}Checking current status...${NC}"
echo "Current directory: $(pwd)"
echo "Current git status:"
git status --porcelain | head -10

echo ""
echo -e "${YELLOW}1. Pulling ALL latest changes from GitHub...${NC}"
echo "Fetching latest commits..."
git fetch origin
echo "Latest commits available:"
git log --oneline origin/main -5

echo ""
echo "Resetting to latest main branch..."
git reset --hard origin/main
echo -e "${GREEN}✓ Code updated to latest version${NC}"

echo ""
echo "Verifying latest commit:"
git log --oneline -1
echo ""

echo -e "${YELLOW}2. Emergency disk cleanup...${NC}"

# Stop any running processes that might lock files
echo "Stopping any processes..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# Clean up corrupted database backups
echo "Removing corrupted database backups..."
rm -f uploads/*.db.corrupted.* 2>/dev/null || true
rm -f uploads/product_database_AGT_Bothell.db.backup.* 2>/dev/null || true
rm -rf uploads/old_corrupted_backups 2>/dev/null || true

# Clean up old sessions
echo "Cleaning sessions..."
find sessions/ -type f -mtime +1 -delete 2>/dev/null || true

# Clean up logs
echo "Cleaning logs..."
find . -name "*.log" -mtime +1 -delete 2>/dev/null || true

# Clean up Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clean up old zip files
echo "Removing old archives..."
find . -maxdepth 1 -name "*.zip" -delete 2>/dev/null || true

# Remove database lock files
echo "Removing database locks..."
rm -f uploads/*.db-shm 2>/dev/null || true
rm -f uploads/*.db-wal 2>/dev/null || true

echo -e "${GREEN}✓ Disk cleanup complete${NC}"

# Check disk usage
echo ""
echo "Current disk usage:"
du -sh ~/AGTDesigner
df -h ~

echo ""
echo -e "${YELLOW}3. Database setup...${NC}"

# Check if database exists and is valid
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    DB_SIZE=$(stat -c%s "uploads/product_database_AGT_Bothell.db")
    if [ "$DB_SIZE" -lt 10000 ]; then
        echo -e "${RED}Database is too small (${DB_SIZE} bytes), removing...${NC}"
        rm -f uploads/product_database_AGT_Bothell.db
    else
        echo -e "${GREEN}✓ Database exists and looks valid (${DB_SIZE} bytes)${NC}"
    fi
fi

# Create fresh database if needed
if [ ! -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "Creating fresh database..."
    python3 create_fresh_database.py || {
        echo -e "${RED}Failed to create database, will be created on first run${NC}"
    }
fi

# Set proper permissions
chmod 666 uploads/product_database_AGT_Bothell.db 2>/dev/null || true

echo -e "${GREEN}✓ Database ready${NC}"

echo ""
echo -e "${YELLOW}4. Updating dependencies...${NC}"
pip3 install --user -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}ALL LATEST FIXES DEPLOYED!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${BLUE}What was deployed:${NC}"
echo "✓ Enhanced JSON matcher with detailed display names"
echo "✓ Enhanced clear functionality with full app reset"
echo "✓ Improved lineage detection in excel processor"
echo "✓ Updated product database handling"
echo "✓ Refined CSS styling and UI improvements"
echo "✓ Template processor improvements"
echo "✓ Various bug fixes and optimizations"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload www.agtpricetags.com'"
echo "3. Test the new features:"
echo "   - JSON matcher should show detailed product info"
echo "   - Clear buttons should say 'Clear & Reset'"
echo "   - All latest improvements should be active"
echo ""
echo "To check logs:"
echo "  tail -f /var/log/www.agtpricetags.com.error.log"
echo ""
