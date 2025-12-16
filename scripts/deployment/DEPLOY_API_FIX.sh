#!/bin/bash
# Deploy API Generation Endpoint Fix to PythonAnywhere

echo "🚀 Deploying API Generation Endpoint Fix..."
echo ""

# Step 1: Commit changes
echo "📦 Step 1: Committing changes to git..."
git add app.py
git add src/core/generation/parallel_tag_generator.py
git add API_GENERATION_ENDPOINT_FIX.md
git commit -m "Fix API generation endpoints - add /api/generate fallback and fix multiprocessing for PythonAnywhere"
echo "✅ Changes committed"
echo ""

# Step 2: Push to GitHub
echo "📤 Step 2: Pushing to GitHub..."
git push origin main
if [ $? -eq 0 ]; then
    echo "✅ Changes pushed to GitHub"
else
    echo "❌ Failed to push. Please check your git configuration."
    exit 1
fi
echo ""

# Step 3: Instructions for PythonAnywhere
echo "============================================"
echo "📋 NEXT STEPS - Run on PythonAnywhere:"
echo "============================================"
echo ""
echo "1. Go to https://www.pythonanywhere.com"
echo "2. Click 'Consoles' tab"
echo "3. Start a Bash console"
echo "4. Run these commands:"
echo ""
echo "   cd /home/YOUR_USERNAME/your-app-directory"
echo "   git pull origin main"
echo "   # Then go to Web tab and click 'Reload' button"
echo ""
echo "============================================"
echo "✅ Local deployment complete!"
echo "============================================"
echo ""
echo "After reloading on PythonAnywhere, test at:"
echo "https://www.agtpricetags.com"
echo ""

