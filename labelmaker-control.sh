#!/bin/bash

# Bulletproof Label Maker Control Script
# This script WILL work - guaranteed!

APP_DIR="/Users/adamcordova/Desktop/labelMaker_ QR copy final"
PORT=8001

# Function to kill everything
kill_all() {
    echo "🔫 Killing all Label Maker processes..."
    
    # Kill by port
    PORT_PIDS=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$PORT_PIDS" ]; then
        echo "Killing processes on port $PORT: $PORT_PIDS"
        echo "$PORT_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    # Kill by process name
    APP_PIDS=$(pgrep -f "python.*app.py" 2>/dev/null)
    if [ ! -z "$APP_PIDS" ]; then
        echo "Killing app.py processes: $APP_PIDS"
        echo "$APP_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    # Kill any python processes in the app directory
    PYTHON_PIDS=$(ps aux | grep python | grep "$APP_DIR" | awk '{print $2}' 2>/dev/null)
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "Killing Python processes in app directory: $PYTHON_PIDS"
        echo "$PYTHON_PIDS" | xargs kill -9 2>/dev/null
    fi
    
    # Remove all lock files
    rm -f /tmp/labelmaker* 2>/dev/null
    rm -f "$APP_DIR"/*.lock 2>/dev/null
    
    echo "✅ All processes killed!"
}

# Function to start the app
start_app() {
    echo "🚀 Starting Label Maker..."
    
    # First, kill everything
    kill_all
    sleep 1
    
    # Change to app directory
    cd "$APP_DIR" || {
        echo "❌ Cannot change to directory: $APP_DIR"
        exit 1
    }
    
    # Start the app
    echo "Starting Flask app..."
    nohup python app.py > app.log 2>&1 &
    APP_PID=$!
    
    # Wait a moment and check if it started
    sleep 3
    
    # Check if the port is being used
    if lsof -i :$PORT >/dev/null 2>&1; then
        echo "✅ App started successfully!"
        echo "🌐 Available at: http://127.0.0.1:$PORT"
        echo "📝 Logs: $APP_DIR/app.log"
        echo "🆔 Process ID: $APP_PID"
    else
        echo "❌ App failed to start. Check logs: $APP_DIR/app.log"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo "📊 Label Maker Status:"
    echo "======================"
    
    # Check if port is in use
    PORT_PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "✅ App is running on port $PORT (PID: $PORT_PID)"
        echo "🌐 URL: http://127.0.0.1:$PORT"
        
        # Show recent logs
        if [ -f "$APP_DIR/app.log" ]; then
            echo ""
            echo "📝 Recent logs:"
            tail -5 "$APP_DIR/app.log"
        fi
    else
        echo "❌ App is not running"
        
        # Check for any Python processes
        PYTHON_COUNT=$(ps aux | grep python | grep -v grep | wc -l)
        if [ $PYTHON_COUNT -gt 0 ]; then
            echo "⚠️  Found $PYTHON_COUNT Python processes running (not Label Maker)"
        fi
    fi
}

# Main script
case "${1:-help}" in
    start)
        start_app
        ;;
    stop)
        echo "🛑 Stopping Label Maker..."
        kill_all
        echo "✅ App stopped!"
        ;;
    restart)
        echo "🔄 Restarting Label Maker..."
        kill_all
        sleep 2
        start_app
        ;;
    status)
        show_status
        ;;
    kill)
        kill_all
        ;;
    *)
        echo "🎯 Label Maker Control Script"
        echo "============================"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the Label Maker app"
        echo "  stop     - Stop the Label Maker app"
        echo "  restart  - Restart the Label Maker app"
        echo "  status   - Show app status"
        echo "  kill     - Force kill all processes"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 stop"
        echo "  $0 restart"
        echo "  $0 status"
        echo ""
        echo "💡 This script will ALWAYS work - it kills everything first!"
        ;;
esac
