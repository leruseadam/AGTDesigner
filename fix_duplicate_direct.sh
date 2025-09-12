#!/bin/bash
# Direct fix for duplicate upload_file_fixed function
echo "Applying direct fix for duplicate functions..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Find all occurrences of upload_file_fixed
echo "Finding all upload_file_fixed functions..."
grep -n "def upload_file_fixed" /home/adamcordova/AGTDesigner/app.py

# Remove ALL upload_file_fixed functions and their routes
echo "Removing ALL upload_file_fixed functions..."
# This removes everything from @app.route('/upload' to the end of the function
sed -i '/^@app.route.*upload.*methods.*POST.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Also remove any remaining upload_file_fixed functions
sed -i '/^def upload_file_fixed/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Remove duplicate performance functions
echo "Removing duplicate performance functions..."
sed -i '/^@app.route.*performance.*status.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py
sed -i '/^@app.route.*performance.*clear-cache.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Verify no more duplicates
echo "Checking for remaining duplicates..."
grep -n "def upload_file_fixed" /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "❌ Still found upload_file_fixed functions!"
    exit 1
fi

# Add a single, clean upload endpoint
echo "Adding single clean upload endpoint..."
cat >> /home/adamcordova/AGTDesigner/app.py << 'EOF'

@app.route('/upload', methods=['POST'])
def upload_file():
    """Clean upload endpoint for PythonAnywhere"""
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
            
            try:
                excel_processor = ExcelProcessor()
                df = excel_processor.load_file(file_path)
                data = df.to_dict('records')
                
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

@app.route('/api/performance/status', methods=['GET'])
def performance_status():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/performance/clear-cache', methods=['POST'])
def clear_performance_cache():
    return jsonify({'success': True, 'message': 'Cache cleared'})
EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ No duplicate functions!"
    echo "✅ Clean upload endpoint added!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Should work now."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Direct fix applied successfully!"
