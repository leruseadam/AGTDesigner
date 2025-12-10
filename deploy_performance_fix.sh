#!/bin/bash
# Deploy Performance-Optimized Version to PythonAnywhere
# This script ensures all performance fixes are active

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "🚀 Deploying Performance-Optimized Version to PythonAnywhere"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PYTHONANYWHERE_USER="adamcordova"
PROJECT_DIR="/home/${PYTHONANYWHERE_USER}/AGTDesigner"

echo "📋 Pre-deployment Checks"
echo "──────────────────────────────────────────────────────────"

# Check if wsgi.py has performance optimizations
if grep -q "FORCE_FAST_LOAD" wsgi.py; then
    echo -e "${GREEN}✅${NC} wsgi.py has performance optimizations"
else
    echo -e "${YELLOW}⚠️${NC}  wsgi.py missing performance optimizations - applying now..."
    python3 apply_pythonanywhere_performance_fix.py
fi

# Check if response_cache module exists
if [ -f "src/core/utils/response_cache.py" ]; then
    echo -e "${GREEN}✅${NC} Response cache module present"
else
    echo -e "${RED}❌${NC} Response cache module missing - caching will be disabled"
fi

# Check if app.py has fast_load enabled
if grep -q "fast_load = True  # Default to fast loading" app.py; then
    echo -e "${GREEN}✅${NC} Fast load mode enabled in app.py"
else
    echo -e "${YELLOW}⚠️${NC}  Fast load not defaulted - this may cause slow performance"
fi

echo ""
echo "📦 Files to Deploy"
echo "──────────────────────────────────────────────────────────"
echo "  - app.py (main application)"
echo "  - wsgi.py (WSGI configuration with performance settings)"
echo "  - config.py (Flask configuration)"
echo "  - src/core/utils/response_cache.py (caching module)"
echo "  - src/core/data/product_database.py (database module)"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

echo ""
echo "🔄 Deploying to PythonAnywhere..."
echo "──────────────────────────────────────────────────────────"

# Check if we have SSH access configured
if ! ssh ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com "echo test" 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  SSH not configured. Manual deployment required:${NC}"
    echo ""
    echo "1. Go to: https://www.pythonanywhere.com/user/${PYTHONANYWHERE_USER}/files/"
    echo "2. Upload the following files to ${PROJECT_DIR}:"
    echo "   - app.py"
    echo "   - wsgi.py"
    echo "   - config.py"
    echo "3. Upload to ${PROJECT_DIR}/src/core/utils/:"
    echo "   - src/core/utils/response_cache.py"
    echo "4. Upload to ${PROJECT_DIR}/src/core/data/:"
    echo "   - src/core/data/product_database.py"
    echo ""
    echo "5. Reload the web app from: https://www.pythonanywhere.com/user/${PYTHONANYWHERE_USER}/webapps/"
    echo ""
    echo "Or configure SSH access with:"
    echo "  ssh-keygen -t rsa -b 4096"
    echo "  cat ~/.ssh/id_rsa.pub"
    echo "  # Add the key to PythonAnywhere Account > SSH Keys"
    echo ""
    exit 1
fi

# Deploy via SSH
echo "Uploading files via SSH..."

# Create directories if they don't exist
ssh ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com "mkdir -p ${PROJECT_DIR}/src/core/utils ${PROJECT_DIR}/src/core/data"

# Upload main files
scp app.py ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com:${PROJECT_DIR}/
scp wsgi.py ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com:${PROJECT_DIR}/
scp config.py ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com:${PROJECT_DIR}/

# Upload modules
if [ -f "src/core/utils/response_cache.py" ]; then
    scp src/core/utils/response_cache.py ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com:${PROJECT_DIR}/src/core/utils/
fi

if [ -f "src/core/data/product_database.py" ]; then
    scp src/core/data/product_database.py ${PYTHONANYWHERE_USER}@ssh.pythonanywhere.com:${PROJECT_DIR}/src/core/data/
fi

echo -e "${GREEN}✅${NC} Files uploaded successfully"

echo ""
echo "🔄 Reloading web app..."
echo "──────────────────────────────────────────────────────────"

# Reload web app using PythonAnywhere API
# You'll need to set up an API token at: https://www.pythonanywhere.com/user/${PYTHONANYWHERE_USER}/account/#api_token
if [ -n "$PYTHONANYWHERE_API_TOKEN" ]; then
    curl -X POST \
        -H "Authorization: Token $PYTHONANYWHERE_API_TOKEN" \
        https://www.pythonanywhere.com/api/v0/user/${PYTHONANYWHERE_USER}/webapps/adamcordova.pythonanywhere.com/reload/ \
        2>/dev/null
    echo -e "${GREEN}✅${NC} Web app reloaded via API"
else
    echo -e "${YELLOW}⚠️${NC}  Manual reload required:"
    echo "   Go to: https://www.pythonanywhere.com/user/${PYTHONANYWHERE_USER}/webapps/"
    echo "   Click the 'Reload' button for your web app"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Next Steps:"
echo ""
echo "1. Wait 30 seconds for the app to fully restart"
echo ""
echo "2. Test performance:"
echo "   python3 test_pythonanywhere_performance.py https://${PYTHONANYWHERE_USER}.pythonanywhere.com"
echo ""
echo "3. Check logs for any errors:"
echo "   https://www.pythonanywhere.com/user/${PYTHONANYWHERE_USER}/files/var/log/"
echo ""
echo "4. Monitor app:"
echo "   - Open: https://${PYTHONANYWHERE_USER}.pythonanywhere.com"
echo "   - Check browser DevTools (F12) Network tab"
echo "   - Look for X-Cache: HIT headers (indicates caching is working)"
echo "   - Look for Content-Encoding: gzip (indicates compression is working)"
echo ""
echo "Expected Performance:"
echo "  • First tag load: 2-4 seconds (down from 15-30s)"
echo "  • Cached tag load: <0.5 seconds (down from 15-30s)"
echo "  • Page load: 1-2 seconds (down from 5-10s)"
echo ""
echo "═══════════════════════════════════════════════════════════"
