#!/bin/bash

# PythonAnywhere File Loading Test Script
# This script runs comprehensive tests to diagnose Excel file loading issues on PythonAnywhere

echo "=== PythonAnywhere File Loading Test ==="
echo "Starting comprehensive file loading diagnostics..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the test script
echo "Running PythonAnywhere file loading test..."
python3 test_pythonanywhere_file_loading.py

echo ""
echo "=== Test Results ==="
echo "Check the following files for detailed results:"
echo "- pythonanywhere_test.log (detailed test log)"
echo "- logs/ (application logs)"
echo ""

# Show recent log entries
if [ -f "pythonanywhere_test.log" ]; then
    echo "Recent test log entries:"
    echo "========================"
    tail -20 pythonanywhere_test.log
    echo ""
fi

echo "=== Next Steps ==="
echo "1. Review the test results above"
echo "2. Check the log files for specific error messages"
echo "3. If files are found, try uploading them through the web interface"
echo "4. If no files are found, the test script should have generated a test file"
echo "5. Check the uploads/ directory for available files"
echo ""

# List files in uploads directory
if [ -d "uploads" ]; then
    echo "Files in uploads directory:"
    ls -la uploads/
    echo ""
fi

echo "Test completed. If you see any errors, please share the log files for further assistance." 