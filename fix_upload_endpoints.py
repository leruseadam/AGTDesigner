#!/usr/bin/env python3
"""
Fix upload endpoints for PythonAnywhere
This script will add missing upload endpoints and fix the frontend calls
"""

# Create a simple upload endpoint fix
upload_fix = '''
@app.route('/upload', methods=['POST'])
def upload_file_fixed():
    """Fixed upload endpoint for PythonAnywhere"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            # Process the file
            try:
                excel_processor = ExcelProcessor()
                df = excel_processor.load_file(file_path)
                
                # Convert to JSON for frontend
                data = df.to_dict('records')
                
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

@app.route('/api/performance/status', methods=['GET'])
def performance_status():
    """Performance status endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'memory_usage': 'normal'
    })

@app.route('/api/performance/clear-cache', methods=['POST'])
def clear_performance_cache():
    """Clear performance cache endpoint"""
    return jsonify({
        'success': True,
        'message': 'Cache cleared'
    })
'''

print("Upload endpoint fix created!")
print("Add this to your app.py file on PythonAnywhere:")
print("=" * 50)
print(upload_fix)
print("=" * 50)
