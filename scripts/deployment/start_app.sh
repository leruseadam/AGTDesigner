#!/bin/bash
# Startup script for AGT Designer application
# Avoids port 5000 which is used by macOS AirPlay/Control Center

echo "======================================"
echo "AGT Designer - Starting Application"
echo "======================================"

# Navigate to the application directory
cd "$(dirname "$0")"

# Check if port 5001 is available
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5001 is already in use. Attempting to free it..."
    pkill -f "python.*app.py"
    sleep 2
fi

# Kill any remaining Flask processes
pkill -f "python.*app" 2>/dev/null || true
sleep 1

# Start the application on port 5001
echo "🚀 Starting Flask on port 5001..."
export FLASK_PORT=5001
python app.py &

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo "✅ Server is running!"
    echo ""
    echo "======================================"
    echo "🌐 Access the application at:"
    echo "   http://localhost:5001"
    echo "======================================"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Keep the script running
    tail -f flask.log 2>/dev/null
else
    echo "❌ Server failed to start"
    echo "Check flask.log for errors"
    exit 1
fi

