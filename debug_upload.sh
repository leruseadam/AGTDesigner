#!/bin/bash
# Debug upload issues
echo "Debugging upload issues..."

echo "Checking if app.py exists and is readable..."
if [ -f "/home/adamcordova/AGTDesigner/app.py" ]; then
    echo "✅ app.py exists"
    echo "File size: $(wc -c < /home/adamcordova/AGTDesigner/app.py) bytes"
    echo "First 10 lines:"
    head -10 /home/adamcordova/AGTDesigner/app.py
else
    echo "❌ app.py does not exist"
fi

echo ""
echo "Checking Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py 2>&1

echo ""
echo "Checking for upload endpoint..."
grep -n "def upload_file" /home/adamcordova/AGTDesigner/app.py

echo ""
echo "Checking for @app.route upload..."
grep -n "@app.route.*upload" /home/adamcordova/AGTDesigner/app.py

echo ""
echo "Checking uploads directory..."
if [ -d "/home/adamcordova/AGTDesigner/uploads" ]; then
    echo "✅ uploads directory exists"
    ls -la /home/adamcordova/AGTDesigner/uploads/
else
    echo "❌ uploads directory does not exist"
fi

echo ""
echo "Testing basic Python import..."
python3 -c "
import sys
sys.path.insert(0, '/home/adamcordova/AGTDesigner')
try:
    from app import app
    print('✅ App imports successfully')
    print('App routes:')
    for rule in app.url_map.iter_rules():
        print(f'  {rule.rule} -> {rule.endpoint}')
except Exception as e:
    print(f'❌ App import failed: {e}')
"

echo ""
echo "Debug complete!"
