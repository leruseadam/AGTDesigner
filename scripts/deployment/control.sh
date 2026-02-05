#!/bin/bash

# Ultra-simple Label Maker control script
# Usage: ./control.sh [start|stop|restart]

APP_DIR="/Users/adamcordova/Desktop/labelMaker_ QR copy final"
PORT=8001

case "$1" in
    start)
        echo "Starting Label Maker..."
        cd "$APP_DIR"
        # Kill anything on the port first
        lsof -ti:$PORT | xargs kill -9 2>/dev/null
        # Start the app
        nohup python app.py > app.log 2>&1 &
        echo "App started! Check http://127.0.0.1:$PORT"
        ;;
    stop)
        echo "Stopping Label Maker..."
        # Kill by port
        lsof -ti:$PORT | xargs kill -9 2>/dev/null
        # Kill by process name
        pkill -f "python.*app.py" 2>/dev/null
        # Remove lock files
        rm -f /tmp/labelmaker*
        echo "App stopped!"
        ;;
    restart)
        echo "Restarting Label Maker..."
        $0 stop
        sleep 2
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start the app"
        echo "  $0 stop     # Stop the app"
        echo "  $0 restart  # Restart the app"
        ;;
esac
