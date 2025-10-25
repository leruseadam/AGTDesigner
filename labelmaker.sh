#!/bin/bash

# Simple Label Maker Management Script
# Usage: ./labelmaker.sh [start|stop|restart|status]

APP_DIR="/Users/adamcordova/Desktop/labelMaker_ QR copy final"
APP_FILE="app.py"
PID_FILE="/tmp/labelmaker.pid"
LOG_FILE="$APP_DIR/app.log"
PORT=8001

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if app is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Start the app
start() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        warning "App is already running with PID $pid"
        return 1
    fi
    
    log "Starting Label Maker..."
    cd "$APP_DIR" || { error "Cannot change to $APP_DIR"; exit 1; }
    
    # Kill any existing processes on port
    local port_pid=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$port_pid" ]; then
        warning "Killing existing process $port_pid on port $PORT"
        kill -9 "$port_pid" 2>/dev/null
    fi
    
    # Start the app
    nohup python "$APP_FILE" > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        log "App started successfully with PID $pid"
        log "Available at: http://127.0.0.1:$PORT"
        log "Logs: $LOG_FILE"
    else
        error "Failed to start app"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the app
stop() {
    if ! is_running; then
        warning "App is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    log "Stopping app (PID: $pid)..."
    
    # Try graceful shutdown first
    kill -TERM "$pid" 2>/dev/null
    
    # Wait up to 5 seconds
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 5 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        warning "Force killing process..."
        kill -9 "$pid" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    log "App stopped"
}

# Restart the app
restart() {
    log "Restarting app..."
    stop
    sleep 1
    start
}

# Show status
status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        log "App is running with PID $pid"
        log "Port: $PORT"
        log "Log file: $LOG_FILE"
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            echo ""
            log "Recent logs:"
            tail -3 "$LOG_FILE"
        fi
    else
        warning "App is not running"
        
        # Check port
        local port_pid=$(lsof -ti:$PORT 2>/dev/null)
        if [ ! -z "$port_pid" ]; then
            warning "Port $PORT is used by process $port_pid"
        fi
    fi
}

# Show help
help() {
    echo "Label Maker Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the Flask app"
    echo "  stop     - Stop the Flask app"
    echo "  restart  - Restart the Flask app"
    echo "  status   - Show app status"
    echo "  help     - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 restart"
    echo "  $0 status"
}

# Main
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
