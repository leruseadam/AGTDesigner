#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "Activating virtual environment (venv)..."
    source venv/bin/activate
else
    echo "Error: No virtual environment found. Please create one with: python -m venv .venv"
    exit 1
fi

echo "Starting Flask app on port 5001..."
FLASK_PORT=5001 python app.py 