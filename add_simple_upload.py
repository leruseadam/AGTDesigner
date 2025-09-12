#!/usr/bin/env python3
"""
Add a simple, reliable upload endpoint for PythonAnywhere
"""

import os

def add_simple_upload_endpoint():
    """Add a simple upload endpoint that won't get stuck"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if simple upload already exists
    if 'def upload_file_simple_pythonanywhere' in content:
        print("✅ Simple upload endpoint already exists")
        return True
    
    # Add the simple upload endpoint before the existing upload-simple route
    simple_upload_code = '''
@app.route('/upload-pythonanywhere', methods=['POST'])
def upload_file_simple_pythonanywhere():
    """Ultra-simple upload endpoint specifically for PythonAnywhere - no background processing"""
    try:
        logging.info("=== PYTHONANYWHERE UPLOAD START ===")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files are allowed'}), 400
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(file.filename)
        
        # Save file temporarily
        temp_path = os.path.join(tempfile.gettempdir(), f"upload_{sanitized_filename}")
        file.save(temp_path)
        
        # Process immediately (no background processing)
        try:
            from src.core.data.excel_processor import ExcelProcessor
            processor = ExcelProcessor()
            
            # Load file with full method (not fast_load_file)
            success = processor.load_file(temp_path)
            
            if not success or processor.df is None or processor.df.empty:
                return jsonify({'error': 'Failed to process file'}), 400
            
            # Store in global processor
            global excel_processor
            excel_processor = processor
            
            # Update session
            session['file_path'] = temp_path
            session['selected_tags'] = []
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': sanitized_filename,
                'rows': len(processor.df),
                'status': 'ready'
            })
            
        except Exception as process_error:
            logging.error(f"Processing error: {process_error}")
            return jsonify({'error': f'Processing failed: {str(process_error)}'}), 500
            
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

'''
    
    # Find the location to insert the new endpoint (before upload-simple)
    insert_location = content.find('@app.route(\'/upload-simple\', methods=[\'POST\'])')
    
    if insert_location == -1:
        print("❌ Could not find insertion point for simple upload endpoint")
        return False
    
    # Insert the new code
    new_content = content[:insert_location] + simple_upload_code + content[insert_location:]
    
    # Write the updated file
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Added simple PythonAnywhere upload endpoint")
    return True

if __name__ == "__main__":
    add_simple_upload_endpoint()
