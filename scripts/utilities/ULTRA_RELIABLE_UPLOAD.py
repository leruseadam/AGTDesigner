@app.route('/upload-ultra-reliable', methods=['POST'])
def upload_ultra_reliable():
    """Ultra-reliable Excel upload with comprehensive error handling and optimization."""
    try:
        logging.info("=== ULTRA-RELIABLE UPLOAD START ===")
        start_time = time.time()
        
        # 1. VALIDATION PHASE - Fast validation before any heavy processing
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files are allowed'}), 400
        
        # 2. FILE SIZE ANALYSIS - Determine processing strategy
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        logging.info(f"📁 File: {file.filename}, Size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)")
        
        # Prevent oversized files
        max_size = 200 * 1024 * 1024  # 200MB limit
        if file_size > max_size:
            return jsonify({'error': f'File too large. Maximum size is {max_size/(1024*1024):.0f} MB'}), 400
        
        if file_size == 0:
            return jsonify({'error': 'Empty file uploaded'}), 400
        
        # 3. QUICK PREVIEW - Estimate processing complexity
        estimated_rows = 1000
        processing_strategy = "immediate"
        
        try:
            import pandas as pd
            # Quick preview with minimal processing
            preview_df = pd.read_excel(file, nrows=50, engine='openpyxl', dtype=str, na_filter=False)
            if len(preview_df) > 0:
                # Estimate total rows based on file size and preview
                estimated_rows = max(50, int(file_size / (file_size / len(preview_df)) * 1.1))
                
                # Determine processing strategy based on complexity
                if estimated_rows > 10000 or file_size > 50 * 1024 * 1024:  # 50MB
                    processing_strategy = "background_chunked"
                elif estimated_rows > 3000 or file_size > 10 * 1024 * 1024:  # 10MB
                    processing_strategy = "background_simple"
                else:
                    processing_strategy = "immediate"
                
                logging.info(f"📊 Estimated rows: {estimated_rows:,}, Strategy: {processing_strategy}")
            
            file.seek(0)  # Reset after preview
            
        except Exception as preview_error:
            logging.warning(f"Preview failed, using default strategy: {preview_error}")
            processing_strategy = "background_simple"
        
        # 4. FILE SAVING - Always save first for reliability
        sanitized_filename = sanitize_filename(file.filename)
        if not sanitized_filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, sanitized_filename)
        
        # Remove existing file if present
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Removed existing file: {sanitized_filename}")
            except Exception as e:
                logging.warning(f"Could not remove existing file: {e}")
        
        # Save file with error handling
        try:
            file.save(file_path)
            save_time = time.time() - start_time
            logging.info(f"✅ File saved successfully in {save_time:.2f}s")
        except Exception as save_error:
            logging.error(f"File save failed: {save_error}")
            return jsonify({'error': 'Failed to save file. Please try again.'}), 500
        
        # 5. SESSION PERSISTENCE - Always set session data first
        session.permanent = True
        session['uploaded_file_path'] = file_path
        session['uploaded_filename'] = sanitized_filename
        session['file_path'] = file_path  # For compatibility
        session.modified = True
        
        # Clear processing status
        update_processing_status(file.filename, 'processing')
        
        # 6. PROCESSING STRATEGY EXECUTION
        if processing_strategy == "immediate":
            # Small files - process immediately with timeout protection
            logging.info(f"⚡ Processing immediately (small file: {estimated_rows:,} rows)")
            
            try:
                from src.core.data.excel_processor import ExcelProcessor
                processor = ExcelProcessor()
                
                # Use fast loading for small files
                success = processor.fast_load_file(file_path) if hasattr(processor, 'fast_load_file') else processor.load_file(file_path)
                
                if success:
                    global _excel_processor
                    with excel_processor_lock:
                        _excel_processor = processor
                        _excel_processor._last_loaded_file = file_path
                    
                    row_count = len(processor.df) if hasattr(processor, 'df') and processor.df is not None else 0
                    upload_time = time.time() - start_time
                    
                    update_processing_status(file.filename, 'ready')
                    logging.info(f"✅ Immediate processing complete: {row_count} rows in {upload_time:.2f}s")
                    
                    return jsonify({
                        'success': True,
                        'filename': sanitized_filename,
                        'message': f'File processed successfully ({row_count:,} rows)',
                        'processing': False,
                        'rows_processed': row_count,
                        'upload_time': upload_time,
                        'strategy': 'immediate'
                    })
                else:
                    return jsonify({'error': 'Failed to process file'}), 500
                    
            except Exception as process_error:
                logging.error(f"Immediate processing failed: {process_error}")
                # Fallback to background processing
                processing_strategy = "background_simple"
        
        if processing_strategy in ["background_simple", "background_chunked"]:
            # Medium/Large files - background processing
            logging.info(f"🚀 Using background processing ({processing_strategy})")
            
            # Start background processing thread
            import threading
            
            def background_excel_processing():
                try:
                    logging.info(f"[BG] Starting {processing_strategy} for {sanitized_filename}")
                    
                    from src.core.data.excel_processor import ExcelProcessor
                    processor = ExcelProcessor()
                    
                    # Choose processing method based on strategy
                    if processing_strategy == "background_chunked":
                        # Use minimal processing for very large files
                        success = processor.minimal_load_file(file_path) if hasattr(processor, 'minimal_load_file') else processor.load_file(file_path)
                    else:
                        # Use regular processing for medium files
                        success = processor.load_file(file_path)
                    
                    if success:
                        global _excel_processor
                        with excel_processor_lock:
                            _excel_processor = processor
                            _excel_processor._last_loaded_file = file_path
                        
                        row_count = len(processor.df) if hasattr(processor, 'df') and processor.df is not None else 0
                        update_processing_status(file.filename, 'ready')
                        logging.info(f"[BG] Background processing complete: {row_count} rows")
                    else:
                        update_processing_status(file.filename, 'error: Processing failed')
                        logging.error(f"[BG] Background processing failed for {sanitized_filename}")
                        
                except Exception as bg_error:
                    logging.error(f"[BG] Background processing error: {bg_error}")
                    update_processing_status(file.filename, f'error: {str(bg_error)}')
            
            # Start background thread with error handling
            try:
                thread = threading.Thread(target=background_excel_processing, daemon=True)
                thread.start()
                logging.info(f"✅ Background thread started for {sanitized_filename}")
            except Exception as thread_error:
                logging.error(f"Failed to start background thread: {thread_error}")
                return jsonify({'error': 'Failed to start processing'}), 500
            
            upload_time = time.time() - start_time
            return jsonify({
                'success': True,
                'filename': sanitized_filename,
                'message': f'File uploaded, processing in background ({processing_strategy})',
                'processing': True,
                'estimated_rows': estimated_rows,
                'upload_time': upload_time,
                'strategy': processing_strategy
            })
        
        # Fallback response (shouldn't reach here)
        upload_time = time.time() - start_time
        return jsonify({
            'success': True,
            'filename': sanitized_filename,
            'message': 'File uploaded successfully',
            'upload_time': upload_time,
            'strategy': 'fallback'
        })
        
    except Exception as e:
        logging.error(f"Ultra-reliable upload failed: {e}")
        logging.error(f"Upload error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Upload failed. Please try again.'}), 500
