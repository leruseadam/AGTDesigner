#!/bin/bash
# Deploy tag loading race condition fix to PythonAnywhere

echo "🚀 Deploying tag loading fix to PythonAnywhere..."
echo ""
echo "Run these commands on PythonAnywhere bash console:"
echo ""
echo "cd ~/AGTDesigner"
echo "git pull origin main"
echo "touch /var/www/leruseadam_pythonanywhere_com_wsgi.py"
echo ""
echo "Then reload your web app in the PythonAnywhere Web tab"
echo ""
echo "✅ The fix will:"
echo "   - Ensure TagManager from main.js fully loads before initialization"
echo "   - Eliminate the race condition causing intermittent tag failures"
echo "   - Tags should load 100% reliably after deployment"

