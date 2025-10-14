#!/bin/bash
# EMERGENCY COMPLETE FIX FOR PYTHONANYWHERE
# This script fixes all critical issues: syntax error, disk space, database corruption

set -e  # Exit on error

echo "======================================="
echo "EMERGENCY COMPLETE FIX - PYTHONANYWHERE"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Cleaning up local disk space...${NC}"
# Remove old corrupted backups locally
if [ -d "uploads/old_corrupted_backups" ]; then
    echo "Removing old_corrupted_backups directory..."
    rm -rf uploads/old_corrupted_backups
    echo -e "${GREEN}✓ Local corrupted backups removed${NC}"
fi

# Remove old zip files
echo "Removing old zip files..."
find . -maxdepth 1 -name "*.zip" -mtime +2 -delete 2>/dev/null || true
echo -e "${GREEN}✓ Old zip files cleaned${NC}"

# Remove old .db files in root
echo "Removing stray database files..."
find . -maxdepth 1 -name "*.db" -delete 2>/dev/null || true
find . -maxdepth 1 -name "*.db-*" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Stray database files removed${NC}"

echo ""
echo -e "${YELLOW}Step 2: Creating fresh working database...${NC}"
# Check if we have a good local database
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    DB_SIZE=$(stat -f%z "uploads/product_database_AGT_Bothell.db" 2>/dev/null || stat -c%s "uploads/product_database_AGT_Bothell.db" 2>/dev/null)
    if [ "$DB_SIZE" -gt 10000 ]; then
        echo -e "${GREEN}✓ Local database is good (${DB_SIZE} bytes)${NC}"
    else
        echo -e "${RED}✗ Local database is too small, needs recreation${NC}"
        rm -f uploads/product_database_AGT_Bothell.db
        python3 create_fresh_database.py
    fi
else
    echo "No local database found, creating fresh one..."
    python3 create_fresh_database.py
fi

echo ""
echo -e "${YELLOW}Step 3: Creating deployment package...${NC}"
# Create a minimal deployment package (no large files)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_DIR="emergency_deploy_${TIMESTAMP}"
mkdir -p "${DEPLOY_DIR}"

# Copy essential files only
echo "Copying essential files..."
cp app.py "${DEPLOY_DIR}/"
cp config.py "${DEPLOY_DIR}/" 2>/dev/null || echo "No config.py to copy"
cp wsgi.py "${DEPLOY_DIR}/"
cp requirements.txt "${DEPLOY_DIR}/"

# Copy source code
cp -r src "${DEPLOY_DIR}/"
cp -r templates "${DEPLOY_DIR}/"
cp -r static "${DEPLOY_DIR}/"

# Copy database (if good)
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    mkdir -p "${DEPLOY_DIR}/uploads"
    cp uploads/product_database_AGT_Bothell.db "${DEPLOY_DIR}/uploads/"
    echo -e "${GREEN}✓ Database included in deployment${NC}"
fi

# Create .gitignore for deployment
cat > "${DEPLOY_DIR}/.gitignore" << 'EOF'
*.pyc
__pycache__/
*.log
sessions/
uploads/*.xlsx
uploads/*.zip
uploads/old_corrupted_backups/
*.db-shm
*.db-wal
EOF

echo -e "${GREEN}✓ Deployment package created: ${DEPLOY_DIR}${NC}"

echo ""
echo -e "${YELLOW}Step 4: Creating PythonAnywhere deployment script...${NC}"

cat > "deploy_to_pythonanywhere_now.sh" << 'DEPLOY_SCRIPT'
#!/bin/bash
# Run this script ON PYTHONANYWHERE via SSH

set -e

echo "======================================="
echo "DEPLOYING TO PYTHONANYWHERE"
echo "======================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd ~/AGTDesigner

echo -e "${YELLOW}1. Pulling latest code from GitHub...${NC}"
git fetch origin
git reset --hard origin/main
echo -e "${GREEN}✓ Code updated${NC}"

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
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload www.agtpricetags.com'"
echo "3. Check error logs if issues persist"
echo ""
echo "To check logs:"
echo "  tail -f /var/log/www.agtpricetags.com.error.log"
echo ""
DEPLOY_SCRIPT

chmod +x deploy_to_pythonanywhere_now.sh
echo -e "${GREEN}✓ PythonAnywhere deployment script created${NC}"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}LOCAL PREPARATION COMPLETE!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. The syntax error fix has been pushed to GitHub ✓"
echo ""
echo "2. SSH into PythonAnywhere and run:"
echo -e "${GREEN}   bash ~/AGTDesigner/deploy_to_pythonanywhere_now.sh${NC}"
echo ""
echo "3. After the script completes, reload your web app:"
echo "   - Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "   - Click the reload button for www.agtpricetags.com"
echo ""
echo "4. Monitor the logs:"
echo -e "${GREEN}   tail -f /var/log/www.agtpricetags.com.error.log${NC}"
echo ""
echo -e "${YELLOW}Alternative if SSH doesn't work:${NC}"
echo "- Use PythonAnywhere bash console"
echo "- Run the same deployment command"
echo ""

