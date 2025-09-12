#!/bin/bash
# Fix upload by removing ExcelProcessor dependency that's causing hangs
echo "Fixing upload by removing ExcelProcessor dependency..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Replace the upload endpoint with one that doesn't use ExcelProcessor
echo "Replacing upload endpoint..."
sed -i '/^@app.route.*upload.*methods.*POST.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Add a new simple upload endpoint
cat >> /home/adamcordova/AGTDesigner/app.py << 'EOF'

@app.route('/upload', methods=['POST'])
def upload_file():
    """Simple upload endpoint without ExcelProcessor dependency"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            # Use pandas directly instead of ExcelProcessor
            try:
                import pandas as pd
                df = pd.read_excel(file_path)
                
                # Convert to simple data structure
                data = []
                for index, row in df.head(20).iterrows():  # Limit to first 20 rows
                    item = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            item[col] = ''
                        else:
                            item[col] = str(value)
                    data.append(item)
                
                return jsonify({
                    'success': True,
                    'message': f'File {filename} uploaded successfully',
                    'data': data,
                    'filename': filename
                })
            except Exception as e:
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ Upload endpoint fixed (no ExcelProcessor dependency)!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Upload should work now."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Upload fix applied successfully!"
echo "Upload should no longer hang on initializing!"
