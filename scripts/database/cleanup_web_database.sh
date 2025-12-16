#!/bin/bash
# Database cleanup script for PythonAnywhere production
# Run this script ON PYTHONANYWHERE via SSH

set -e

echo "======================================="
echo "DATABASE CLEANUP FOR WEB VERSION"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd ~/AGTDesigner

echo -e "${BLUE}Current database status:${NC}"
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    DB_SIZE=$(stat -c%s "uploads/product_database_AGT_Bothell.db")
    echo "Database file size: $DB_SIZE bytes"
    echo "Database file age: $(stat -c %y uploads/product_database_AGT_Bothell.db)"
else
    echo -e "${RED}No database file found!${NC}"
fi

echo ""
echo -e "${YELLOW}1. Stopping web application...${NC}"
# Stop any running processes
pkill -f "python.*app.py" 2>/dev/null || true
sleep 3
echo -e "${GREEN}✓ Web app stopped${NC}"

echo ""
echo -e "${YELLOW}2. Creating database backup...${NC}"
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    BACKUP_NAME="uploads/product_database_AGT_Bothell.db.backup_$(date +%Y%m%d_%H%M%S)"
    cp uploads/product_database_AGT_Bothell.db "$BACKUP_NAME"
    echo -e "${GREEN}✓ Database backed up to: $BACKUP_NAME${NC}"
else
    echo -e "${YELLOW}⚠ No database to backup${NC}"
fi

echo ""
echo -e "${YELLOW}3. Cleaning up database lock files...${NC}"
rm -f uploads/*.db-shm 2>/dev/null || true
rm -f uploads/*.db-wal 2>/dev/null || true
echo -e "${GREEN}✓ Lock files removed${NC}"

echo ""
echo -e "${YELLOW}4. Cleaning up old database backups...${NC}"
# Remove old backup files (keep only last 3)
ls -t uploads/product_database_AGT_Bothell.db.backup* 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
echo -e "${GREEN}✓ Old backups cleaned${NC}"

echo ""
echo -e "${YELLOW}5. Cleaning up corrupted database files...${NC}"
rm -f uploads/*.db.corrupted.* 2>/dev/null || true
rm -f uploads/*.db.backup_before_* 2>/dev/null || true
rm -rf uploads/old_corrupted_backups 2>/dev/null || true
echo -e "${GREEN}✓ Corrupted files removed${NC}"

echo ""
echo -e "${YELLOW}6. Cleaning up sessions...${NC}"
# Clean old sessions (older than 1 day)
find sessions/ -type f -mtime +1 -delete 2>/dev/null || true
echo -e "${GREEN}✓ Old sessions cleaned${NC}"

echo ""
echo -e "${YELLOW}7. Cleaning up logs...${NC}"
# Clean old log files
find . -name "*.log" -mtime +1 -delete 2>/dev/null || true
echo -e "${GREEN}✓ Old logs cleaned${NC}"

echo ""
echo -e "${YELLOW}8. Cleaning up Python cache...${NC}"
# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleaned${NC}"

echo ""
echo -e "${YELLOW}9. Checking database integrity...${NC}"
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    # Check database integrity
    INTEGRITY_CHECK=$(sqlite3 uploads/product_database_AGT_Bothell.db "PRAGMA integrity_check;" 2>/dev/null || echo "error")
    if [ "$INTEGRITY_CHECK" = "ok" ]; then
        echo -e "${GREEN}✓ Database integrity check passed${NC}"
        
        # Get product count
        PRODUCT_COUNT=$(sqlite3 uploads/product_database_AGT_Bothell.db "SELECT COUNT(*) FROM products;" 2>/dev/null || echo "0")
        echo -e "${GREEN}✓ Database contains $PRODUCT_COUNT products${NC}"
    else
        echo -e "${RED}⚠ Database integrity check failed: $INTEGRITY_CHECK${NC}"
        echo -e "${YELLOW}Consider recreating the database...${NC}"
    fi
else
    echo -e "${RED}⚠ No database file found to check${NC}"
fi

echo ""
echo -e "${YELLOW}10. Setting proper permissions...${NC}"
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    chmod 666 uploads/product_database_AGT_Bothell.db
    echo -e "${GREEN}✓ Database permissions set${NC}"
fi

echo ""
echo -e "${YELLOW}11. Checking disk usage...${NC}"
echo "Current disk usage:"
du -sh ~/AGTDesigner
df -h ~

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}DATABASE CLEANUP COMPLETE!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload www.agtpricetags.com'"
echo "3. Test the application"
echo ""
echo "If you need to recreate the database:"
echo "  python3 create_fresh_database.py"
echo ""
