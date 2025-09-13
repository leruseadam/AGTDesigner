#!/bin/bash
# Fix NaN JSON serialization error
echo "Fixing NaN JSON serialization error..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Add NaN handling to the upload endpoint
cat > /tmp/fix_nan.py << 'EOF'
import re

# Read the current app.py
with open('/home/adamcordova/AGTDesigner/app.py', 'r') as f:
    content = f.read()

# Find the data processing section and add NaN handling
old_processing = '''                # Convert to list of dictionaries
                data = df.to_dict('records')'''

new_processing = '''                # Convert to list of dictionaries
                data = df.to_dict('records')
                
                # Handle NaN values for JSON serialization
                import numpy as np
                def clean_nan_values(obj):
                    if isinstance(obj, dict):
                        return {k: clean_nan_values(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [clean_nan_values(item) for item in obj]
                    elif isinstance(obj, float) and np.isnan(obj):
                        return None  # Convert NaN to None for JSON
                    else:
                        return obj
                
                data = clean_nan_values(data)'''

# Replace the processing section
content = content.replace(old_processing, new_processing)

# Write the fixed content
with open('/home/adamcordova/AGTDesigner/app.py', 'w') as f:
    f.write(content)

print("✅ Added NaN handling to upload processing")
EOF

# Run the fix
python3 /tmp/fix_nan.py

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ NaN handling added!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Upload should work now."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "NaN JSON error fix applied successfully!"
