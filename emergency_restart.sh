#!/bin/bash
"""
Emergency restart script for PythonAnywhere
"""

echo "Emergency restart script for PythonAnywhere"
echo "=========================================="

# Stop the current web app
echo "Stopping web app..."
cd /home/adamcordova/AGTDesigner

# Clear any stuck processes
pkill -f "python.*app.py" || true
pkill -f "uwsgi" || true

# Clear log files
echo "Clearing log files..."
rm -f /home/adamcordova/pythonanywhere.log
rm -f /home/adamcordova/AGTDesigner/pythonanywhere.log
rm -f /home/adamcordova/AGTDesigner/logs/*.log

# Clear cache
echo "Clearing cache..."
rm -rf /home/adamcordova/AGTDesigner/__pycache__
rm -rf /home/adamcordova/AGTDesigner/src/__pycache__
find /home/adamcordova/AGTDesigner -name "*.pyc" -delete

# Clear session data
echo "Clearing session data..."
rm -f /home/adamcordova/AGTDesigner/session_*

# Restart the web app
echo "Restarting web app..."
echo "Please go to PythonAnywhere Web tab and click 'Reload'"

echo "Emergency restart complete!"
echo "Check the web app status in PythonAnywhere Web tab"
