#!/bin/bash

# Reliable App Startup Script
# This script ensures the Flask app starts reliably by handling port conflicts

echo "🚀 Starting AGT Label Maker Application..."

# Function to kill processes on a port
kill_port() {
    local port=$1
    echo "🔍 Checking port $port..."
    
    # Find processes using the port
    local pids=$(lsof -ti tcp:$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "⚠️  Found processes on port $port: $pids"
        echo "🔄 Killing processes..."
        
        # Kill processes with retry logic
        for attempt in 1 2 3; do
            kill -9 $pids 2>/dev/null
            sleep 1
            
            # Check if still running
            local remaining=$(lsof -ti tcp:$port 2>/dev/null)
            if [ -z "$remaining" ]; then
                echo "✅ Successfully freed port $port"
                return 0
            else
                echo "⚠️  Attempt $attempt: Still processes on port $port"
            fi
        done
        
        echo "❌ Could not fully free port $port"
        return 1
    else
        echo "✅ Port $port is already free"
        return 0
    fi
}

# Try to free port 8001
if kill_port 8001; then
    echo "🎯 Starting app on port 8001..."
    python app.py
else
    echo "🔄 Port 8001 busy, trying port 8002..."
    if kill_port 8002; then
        echo "🎯 Starting app on port 8002..."
        FLASK_PORT=8002 python app.py
    else
        echo "❌ Both ports 8001 and 8002 are busy"
        echo "Please manually kill processes and try again:"
        echo "  lsof -i :8001"
        echo "  lsof -i :8002"
        echo "  kill -9 <PID>"
        exit 1
    fi
fi
