#!/usr/bin/env python3
"""
Add the upload-fast route to app.py
"""

def add_upload_fast_route():
    # Read the file
    with open('app.py', 'r') as f:
        lines = f.readlines()
    
    # Find the line with def process_excel_background
    for i, line in enumerate(lines):
        if 'def process_excel_background' in line:
            # Insert the upload-fast route before this line
            upload_fast_route = [
                '\n',
                '@app.route(\'/upload-fast\', methods=[\'POST\'])\n',
                'def upload_file_fast():\n',
                '    """Ultra-fast file upload endpoint with minimal processing for maximum speed"""\n',
                '    try:\n',
                '        logging.info("=== ULTRA-FAST UPLOAD REQUEST START ===")\n',
                '        start_time = time.time()\n',
                '        \n',
                '        if \'file\' not in request.files:\n',
                '            return jsonify({\'error\': \'No file uploaded\'}), 400\n',
                '        \n',
                '        file = request.files[\'file\']\n',
                '        if file.filename == \'\' or not file.filename.lower().endswith(\'.xlsx\'):\n',
                '            return jsonify({\'error\': \'Invalid file\'}), 400\n',
                '        \n',
                '        # Sanitize filename\n',
                '        sanitized_filename = sanitize_filename(file.filename)\n',
                '        if not sanitized_filename:\n',
                '            return jsonify({\'error\': \'Invalid filename\'}), 400\n',
                '        \n',
                '        # Check file size (minimal check)\n',
                '        file.seek(0, 2)\n',
                '        file_size = file.tell()\n',
                '        file.seek(0)\n',
                '        \n',
                '        if file_size > app.config[\'MAX_CONTENT_LENGTH\']:\n',
                '            return jsonify({\'error\': \'File too large\'}), 400\n',
                '        \n',
                '        # Save file\n',
                '        upload_folder = app.config[\'UPLOAD_FOLDER\']\n',
                '        os.makedirs(upload_folder, exist_ok=True)\n',
                '        temp_path = os.path.join(upload_folder, sanitized_filename)\n',
                '        \n',
                '        file.save(temp_path)\n',
                '        \n',
                '        # Set processing status\n',
                '        update_processing_status(file.filename, \'processing\')\n',
                '        \n',
                '        # Start background processing\n',
                '        thread = threading.Thread(target=process_excel_background, args=(file.filename, temp_path))\n',
                '        thread.daemon = True\n',
                '        thread.start()\n',
                '        \n',
                '        # Ultra-fast response\n',
                '        upload_time = time.time() - start_time\n',
                '        logging.info(f"[FAST-UPLOAD] Completed in {upload_time:.3f}s")\n',
                '        \n',
                '        return jsonify({\n',
                '            \'success\': True,\n',
                '            \'message\': \'File uploaded successfully\',\n',
                '            \'filename\': sanitized_filename,\n',
                '            \'upload_time\': f"{upload_time:.3f}s",\n',
                '            \'performance\': \'ultra_fast\'\n',
                '        })\n',
                '        \n',
                '    except Exception as e:\n',
                '        logging.error(f"Fast upload error: {str(e)}")\n',
                '        return jsonify({\'error\': \'Upload failed\'}), 500\n',
                '\n'
            ]
            
            # Insert the route before the process_excel_background function
            lines[i:i] = upload_fast_route
            
            # Write the file back
            with open('app.py', 'w') as f:
                f.writelines(lines)
            
            print("✅ Added upload-fast route successfully!")
            return True
    
    print("❌ Could not find process_excel_background function")
    return False

if __name__ == "__main__":
    add_upload_fast_route()
