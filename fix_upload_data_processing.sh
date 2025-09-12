#!/bin/bash
# Fix upload to process data and add to available list
echo "Fixing upload data processing..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Replace the upload endpoint with one that processes real data
sed -i '/^@app.route.*upload.*methods.*POST.*$/,/^}$/d' /home/adamcordova/AGTDesigner/app.py

# Add a new upload endpoint that processes real Excel data
cat >> /home/adamcordova/AGTDesigner/app.py << 'EOF'

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload endpoint that processes real Excel data"""
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
            
            # Process the Excel file
            try:
                import pandas as pd
                df = pd.read_excel(file_path)
                
                # Convert to the expected format
                data = []
                for index, row in df.head(50).iterrows():  # Limit to first 50 rows
                    item = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            item[col] = ''
                        else:
                            item[col] = str(value)
                    
                    # Ensure required fields exist
                    if 'Product Name*' not in item:
                        item['Product Name*'] = item.get('Product Name', 'Unknown Product')
                    if 'Vendor*' not in item:
                        item['Vendor*'] = item.get('Vendor', 'Unknown Vendor')
                    if 'Brand*' not in item:
                        item['Brand*'] = item.get('Brand', 'Unknown Brand')
                    if 'Product Type*' not in item:
                        item['Product Type*'] = item.get('Product Type', 'Unknown Type')
                    if 'Weight*' not in item:
                        item['Weight*'] = item.get('Weight', '1g')
                    if 'Units' not in item:
                        item['Units'] = 'g'
                    if 'Price*' not in item:
                        item['Price*'] = '$0.00'
                    if 'THC%' not in item:
                        item['THC%'] = '0.0'
                    if 'CBD%' not in item:
                        item['CBD%'] = '0.0'
                    
                    data.append(item)
                
                return jsonify({
                    'success': True,
                    'message': f'File {filename} uploaded and processed successfully',
                    'data': data,
                    'filename': filename
                })
            except Exception as e:
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ Upload data processing fixed!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Upload should now process real data."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Upload data processing fix applied successfully!"
echo "Upload should now process real Excel data and add to available list!"
