#!/bin/bash

# AGT Label Maker - Process Management Script
# This script provides reliable start/stop/restart functionality

APP_NAME="labelmaker"
APP_DIR="/Users/adamcordova/Desktop/labelMaker_ QR copy final"
APP_FILE="app.py"
LOCK_FILE="/tmp/labelmaker_app.lock"
PID_FILE="/tmp/labelmaker_app.pid"
LOG_FILE="$APP_DIR/app.log"
PORT=8001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if app is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$PID_FILE" "$LOCK_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to get PID from port
get_pid_from_port() {
    lsof -ti:$PORT 2>/dev/null
}

# Function to kill process by PID
kill_process() {
    local pid=$1
    local force=${2:-false}
    
    if [ "$force" = true ]; then
        print_warning "Force killing process $pid..."
        kill -9 "$pid" 2>/dev/null
    else
        print_status "Gracefully stopping process $pid..."
        kill -TERM "$pid" 2>/dev/null
        
        # Wait up to 10 seconds for graceful shutdown
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # If still running, force kill
        if ps -p "$pid" > /dev/null 2>&1; then
            print_warning "Process didn't stop gracefully, force killing..."
            kill -9 "$pid" 2>/dev/null
        fi
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    rm -f "$LOCK_FILE" "$PID_FILE"
    
    # Kill any remaining processes on the port
    local port_pid=$(get_pid_from_port)
    if [ ! -z "$port_pid" ]; then
        print_warning "Found process $port_pid still using port $PORT, killing..."
        kill_process "$port_pid" true
    fi
    
    # Kill any python processes with app.py
    local app_pids=$(pgrep -f "python.*app.py" 2>/dev/null)
    if [ ! -z "$app_pids" ]; then
        print_warning "Found additional app.py processes: $app_pids"
        echo "$app_pids" | xargs kill -9 2>/dev/null
    fi
    
    print_success "Cleanup complete"
}

# Function to start the app
start_app() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_warning "App is already running with PID $pid"
        return 1
    fi
    
    print_status "Starting $APP_NAME..."
    
    # Change to app directory
    cd "$APP_DIR" || {
        print_error "Cannot change to directory $APP_DIR"
        exit 1
    }
    
    # Cleanup any stale files
    cleanup
    
    # Start the app in background
    nohup python "$APP_FILE" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        print_success "App started successfully with PID $pid"
        print_status "App is available at: http://127.0.0.1:$PORT"
        print_status "Logs are being written to: $LOG_FILE"
        print_status "Use './manage.sh stop' to stop the app"
    else
        print_error "Failed to start app. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop the app
stop_app() {
    if ! is_running; then
        print_warning "App is not running"
        # Still try to cleanup
        cleanup
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping $APP_NAME (PID: $pid)..."
    
    kill_process "$pid"
    
    # Cleanup
    cleanup
    
    print_success "App stopped successfully"
}

# Function to restart the app
restart_app() {
    print_status "Restarting $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_success "App is running with PID $pid"
        print_status "Port: $PORT"
        print_status "Log file: $LOG_FILE"
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            print_status "Recent logs:"
            tail -5 "$LOG_FILE"
        fi
    else
        print_warning "App is not running"
        
        # Check if something is using the port
        local port_pid=$(get_pid_from_port)
        if [ ! -z "$port_pid" ]; then
            print_warning "Port $PORT is being used by process $port_pid"
        fi
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        print_status "Showing logs from $LOG_FILE:"
        tail -f "$LOG_FILE"
    else
        print_error "Log file not found: $LOG_FILE"
    fi
}

# Function to show help
show_help() {
    echo "AGT Label Maker - Process Management Script"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs|cleanup|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the Flask application"
    echo "  stop     - Stop the Flask application gracefully"
    echo "  restart  - Restart the Flask application"
    echo "  status   - Show application status"
    echo "  logs     - Show and follow application logs"
    echo "  cleanup  - Force cleanup of all processes and files"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the app"
    echo "  $0 stop      # Stop the app"
    echo "  $0 restart   # Restart the app"
    echo "  $0 status    # Check if app is running"
    echo "  $0 logs      # View live logs"
}

# Main script logic
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
