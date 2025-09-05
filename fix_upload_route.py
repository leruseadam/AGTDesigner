#!/usr/bin/env python3
"""
Fix the broken upload-fast route in app.py
"""

import re

def fix_upload_route():
    # Read the file
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the broken upload-fast route section
    pattern = r'@app\.route\('/upload-fast', methods=\['POST'\]\).*?@app\.route\('/upload-test'\)'
    
    # Create the fixed upload-fast function
    fixed_function = '''@app.route('/upload-fast', methods=['POST'])
def upload_file_fast():
    """Ultra-fast file upload endpoint with minimal processing for maximum speed"""
    try:
        logging.info("=== ULTRA-FAST UPLOAD REQUEST START ===")
        start_time = time.time()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.lower().endswith('.xlsx'):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(file.filename)
        if not sanitized_filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Check file size (minimal check)
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large'}), 400
        
        # Save file
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        temp_path = os.path.join(upload_folder, sanitized_filename)
        
        file.save(temp_path)
        
        # Set processing status
        update_processing_status(file.filename, 'processing')
        
        # Start background processing
        thread = threading.Thread(target=process_excel_background, args=(file.filename, temp_path))
        thread.daemon = True
        thread.start()
        
        # Ultra-fast response
        upload_time = time.time() - start_time
        logging.info(f"[FAST-UPLOAD] Completed in {upload_time:.3f}s")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': sanitized_filename,
            'upload_time': f"{upload_time:.3f}s",
            'performance': 'ultra_fast'
        })
        
    except Exception as e:
        logging.error(f"Fast upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/upload-test')'''
    
    # Replace the broken section
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, fixed_function, content, flags=re.DOTALL)
        
        # Write the fixed content back
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Fixed upload-fast route successfully!")
        return True
    else:
        print("❌ Could not find the broken upload-fast route pattern")
        return False

if __name__ == "__main__":
    fix_upload_route()
