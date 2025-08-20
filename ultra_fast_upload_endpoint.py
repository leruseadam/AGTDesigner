@app.route('/upload-ultra-fast', methods=['POST'])
def upload_file_ultra_fast():
    """Ultra-fast file upload with minimal processing"""
    try:
        start_time = time.time()
        logging.info("=== ULTRA-FAST UPLOAD START ===")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files are allowed'}), 400
        
        # Ensure upload folder exists
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file with timestamp
        timestamp = int(time.time())
        safe_filename = f"ultra_fast_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_folder, safe_filename)
        
        # Save file
        file.save(file_path)
        save_time = time.time() - start_time
        
        # Load file with ultra-fast method
        try:
            excel_processor = get_excel_processor()
            
            # Force PythonAnywhere mode
            if hasattr(excel_processor, 'enable_pythonanywhere_mode'):
                excel_processor.enable_pythonanywhere_mode(True)
            
            # Use the fastest loading method available
            if hasattr(excel_processor, 'pythonanywhere_fast_load'):
                success = excel_processor.pythonanywhere_fast_load(file_path)
                method_used = 'pythonanywhere_fast_load'
            elif hasattr(excel_processor, 'fast_load'):
                success = excel_processor.fast_load(file_path)
                method_used = 'fast_load'
            else:
                # Fallback to regular load with optimizations
                success = excel_processor.load_file(file_path)
                method_used = 'load_file'
            
            if success:
                # Store file path in session
                session['file_path'] = file_path
                session['selected_tags'] = []
                
                total_time = time.time() - start_time
                
                logging.info(f"Ultra-fast upload completed in {total_time:.3f}s using {method_used}")
                
                return jsonify({
                    'message': 'File uploaded and loaded successfully',
                    'filename': file.filename,
                    'status': 'ready',
                    'upload_time': f"{save_time:.3f}s",
                    'total_time': f"{total_time:.3f}s",
                    'method_used': method_used,
                    'performance': 'ultra_fast'
                })
            else:
                logging.error(f"Failed to load file: {file_path}")
                return jsonify({'error': 'Failed to load file data'}), 500
                
        except Exception as load_error:
            logging.error(f"Error loading file: {load_error}")
            return jsonify({'error': f'Error loading file: {str(load_error)}'}), 500
            
    except Exception as e:
        logging.error(f"Ultra-fast upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500
