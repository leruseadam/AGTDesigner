#!/bin/bash
# Automatic cleanup script for large data files
# Run this script daily to prevent disk quota issues

# Set the project directory
PROJECT_DIR="/Users/adamcordova/Desktop/labelMaker_ QR copy final"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Run the cleanup script
echo "🧹 Starting daily cleanup at $(date)"
python cleanup_large_files.py

# Check disk usage
echo "📊 Current disk usage:"
du -sh .

# Log the cleanup
echo "✅ Daily cleanup completed at $(date)" >> cleanup.log
