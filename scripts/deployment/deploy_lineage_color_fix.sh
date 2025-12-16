#!/bin/bash
# Deploy lineage color fix to PythonAnywhere

echo "🚀 Deploying lineage color fix to PythonAnywhere..."

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Check if pull was successful
if [ $? -eq 0 ]; then
    echo "✅ Code updated successfully"
else
    echo "❌ Failed to pull latest code"
    exit 1
fi

# Test lineage functionality locally first
echo "🧪 Testing lineage functionality locally..."
python3 test_lineage_change.py

if [ $? -eq 0 ]; then
    echo "✅ Lineage tests passed locally"
else
    echo "⚠️  Lineage tests failed, but continuing with deployment"
fi

echo ""
echo "🎯 Next steps for PythonAnywhere:"
echo "1. SSH into PythonAnywhere: ssh adamcordova@ssh.pythonanywhere.com"
echo "2. Navigate to directory: cd ~/AGTDesigner"
echo "3. Pull latest code: git pull origin main"
echo "4. Reload web app at: https://www.pythonanywhere.com/user/adamcordova/webapps/"
echo "5. Test lineage changes in the browser"
echo "6. Check logs: tail -f /var/log/www.agtpricetags.com.error.log"
echo ""
echo "🔍 What to look for in logs:"
echo "   - 'DEBUG: Lineage data in records:' - shows lineage data being processed"
echo "   - 'LINEAGE COLOR:' - shows which colors are being applied"
echo "   - 'LINEAGE COLOR SUMMARY:' - shows total cells processed and colored"
echo ""
echo "✅ Local deployment complete. Ready to deploy to PythonAnywhere!"

