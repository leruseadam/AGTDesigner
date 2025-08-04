#!/bin/bash

# Auto-activate virtual environment for labelMaker
# Usage: source activate_venv.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if .venv exists and activate it
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "Activating virtual environment..."
    source "$SCRIPT_DIR/.venv/bin/activate"
    echo "Virtual environment activated! You can now run: python app.py"
else
    echo "Error: .venv directory not found in $SCRIPT_DIR"
    echo "Please run: python -m venv .venv"
    exit 1
fi 