#!/bin/bash

echo "🔄 FORCING COMPLETE REFRESH..."
echo ""

# Kill any existing Flask processes
echo "1️⃣  Stopping any running Flask servers..."
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# Touch the CSS file to update its timestamp
echo "2️⃣  Updating CSS file timestamp..."
touch static/css/styles.css

# Add a unique timestamp to the CSS file as a comment
echo "/* Cache bust: $(date +%s) */" >> static/css/styles.css

echo "3️⃣  Starting server on port 8001..."
python app.py &
SERVER_PID=$!
sleep 3

echo ""
echo "✅ Server started! (PID: $SERVER_PID)"
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  NOW DO THIS IN YOUR BROWSER:                        ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  1. Close ALL browser tabs with localhost:8001       ║"
echo "║  2. Open INCOGNITO/PRIVATE window (Cmd+Shift+N)      ║"
echo "║  3. Go to: http://localhost:8001                      ║"
echo "║                                                       ║"
echo "║  The buttons WILL be purple in incognito!            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""

# Keep the script running
wait $SERVER_PID

