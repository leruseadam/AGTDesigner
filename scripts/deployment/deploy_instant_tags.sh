#!/bin/bash

# Tag Instant Load Fix - Quick Deploy Script
# This script helps test the instant tag loading improvements

echo "🚀 Deploying Tag Instant Load Fix..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this from the project root."
    exit 1
fi

# Check if main.js was modified
if [ -f "static/js/main.js" ]; then
    echo "✅ main.js found"
else
    echo "❌ Error: static/js/main.js not found"
    exit 1
fi

# Show what was changed
echo ""
echo "📝 Changes made to improve tag loading:"
echo "  1. ⚡ Instant cache rendering with requestAnimationFrame"
echo "  2. 🎯 Ultra-fast splash timeout (500ms instead of 2000ms)"
echo "  3. 🔄 Background loading of selected tags/filters"
echo "  4. 🛡️ Enhanced error handling for syntax errors"
echo "  5. 📊 Better console logging for debugging"
echo ""

# Test if Flask is running
echo "🔍 Checking if Flask is running..."
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Flask is running on localhost:5000"
    echo ""
    echo "📌 To test the fix:"
    echo "   1. Open Chrome DevTools (F12)"
    echo "   2. Go to Console tab"
    echo "   3. Refresh the page (Cmd+R or Ctrl+R)"
    echo "   4. Look for these messages:"
    echo "      - ⚡ INSTANT CACHE LOAD: X tags available"
    echo "      - ✅ INSTANT RENDER: X tags displayed from cache"
    echo "      - ✅ Tags ready: X items - hiding splash"
    echo ""
    echo "   Tags should appear in < 100ms if cached!"
    echo ""
else
    echo "⚠️  Flask is not running"
    echo ""
    echo "To start Flask:"
    echo "  python app.py"
    echo ""
fi

# Optional: Restart Flask if running
read -p "Would you like to restart Flask to load the changes? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Restarting Flask..."
    
    # Find Flask process and kill it
    FLASK_PID=$(ps aux | grep '[p]ython app.py' | awk '{print $2}')
    if [ ! -z "$FLASK_PID" ]; then
        echo "   Stopping Flask (PID: $FLASK_PID)..."
        kill $FLASK_PID
        sleep 2
    fi
    
    # Start Flask in background
    echo "   Starting Flask..."
    python app.py > flask.log 2>&1 &
    sleep 3
    
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo "✅ Flask restarted successfully!"
        echo "   Log file: flask.log"
    else
        echo "❌ Failed to restart Flask. Check flask.log for errors."
    fi
fi

echo ""
echo "✨ Deployment complete!"
echo ""
echo "📚 For more details, see TAG_INSTANT_LOAD_FIX.md"
