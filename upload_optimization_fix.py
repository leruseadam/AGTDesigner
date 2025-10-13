#!/usr/bin/env python3
"""
Upload Optimization Fix - Prevents Excel hanging during processing
"""

# Add this to your upload endpoint to prevent hanging:

def optimized_upload_processing(file_path, filename):
    """Optimized Excel processing that prevents hanging"""
    try:
        logging.info(f"🚀 OPTIMIZED PROCESSING: {filename}")
        
        # Step 1: Quick file validation
        file_size = os.path.getsize(file_path)
        logging.info(f"📁 File size: {file_size:,} bytes")
        
        if file_size == 0:
            return {"success": False, "error": "Empty file"}
        
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return {"success": False, "error": "File too large (>100MB)"}
        
        # Step 2: Quick preview to estimate rows
        import pandas as pd
        try:
            preview_df = pd.read_excel(file_path, nrows=100, engine='openpyxl')
            estimated_rows = max(100, int(file_size / (file_size / len(preview_df)) * 1.2))
            logging.info(f"📊 Estimated rows: {estimated_rows:,}")
        except Exception as e:
            logging.warning(f"Preview failed: {e}")
            estimated_rows = 1000
        
        # Step 3: Choose processing strategy based on size
        if estimated_rows > 5000:
            # Large file - process in background with chunking
            return process_large_file_chunked(file_path, filename, estimated_rows)
        elif estimated_rows > 1000:
            # Medium file - process with timeout protection
            return process_medium_file_with_timeout(file_path, filename)
        else:
            # Small file - process normally
            return process_small_file_normal(file_path, filename)
            
    except Exception as e:
        logging.error(f"❌ Optimized processing failed: {e}")
        return {"success": False, "error": str(e)}

def process_large_file_chunked(file_path, filename, estimated_rows):
    """Process large files in chunks to prevent hanging"""
    try:
        logging.info(f"📦 CHUNKED PROCESSING: {filename} (~{estimated_rows:,} rows)")
        
        # Import Excel processor
        from src.core.data.excel_processor import ExcelProcessor
        processor = ExcelProcessor()
        
        # Process in chunks
        chunk_size = 1000
        all_chunks = []
        processed_rows = 0
        
        for chunk_start in range(0, estimated_rows, chunk_size):
            try:
                # Read chunk
                chunk_df = pd.read_excel(
                    file_path,
                    skiprows=chunk_start,
                    nrows=chunk_size,
                    engine='openpyxl',
                    dtype=str,
                    na_filter=False
                )
                
                if chunk_df.empty:
                    break
                
                all_chunks.append(chunk_df)
                processed_rows += len(chunk_df)
                
                logging.info(f"📦 Chunk processed: {len(chunk_df)} rows (total: {processed_rows:,})")
                
                # Small delay to prevent overwhelming
                time.sleep(0.05)
                
            except Exception as chunk_error:
                logging.warning(f"Chunk failed: {chunk_error}")
                continue
        
        # Combine chunks
        if all_chunks:
            processor.df = pd.concat(all_chunks, ignore_index=True)
            
            # Update global processor
            global _excel_processor
            with excel_processor_lock:
                _excel_processor = processor
                _excel_processor._last_loaded_file = file_path
            
            logging.info(f"✅ Large file processed: {len(processor.df)} rows")
            
            return {
                "success": True,
                "method": "chunked",
                "rows_processed": len(processor.df),
                "chunks_processed": len(all_chunks)
            }
        else:
            return {"success": False, "error": "No chunks could be processed"}
            
    except Exception as e:
        logging.error(f"❌ Chunked processing failed: {e}")
        return {"success": False, "error": str(e)}

def process_medium_file_with_timeout(file_path, filename):
    """Process medium files with timeout protection"""
    try:
        logging.info(f"⏱️ TIMEOUT-PROTECTED PROCESSING: {filename}")
        
        import signal
        from src.core.data.excel_processor import ExcelProcessor
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Processing timeout")
        
        # Set 20-second timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(20)
        
        try:
            processor = ExcelProcessor()
            success = processor.load_file(file_path)
            signal.alarm(0)  # Cancel timeout
            
            if success:
                global _excel_processor
                with excel_processor_lock:
                    _excel_processor = processor
                    _excel_processor._last_loaded_file = file_path
                
                row_count = len(processor.df) if hasattr(processor, 'df') and processor.df is not None else 0
                logging.info(f"✅ Medium file processed: {row_count} rows")
                
                return {
                    "success": True,
                    "method": "timeout_protected",
                    "rows_processed": row_count
                }
            else:
                signal.alarm(0)
                return {"success": False, "error": "File processing failed"}
                
        except TimeoutError:
            signal.alarm(0)
            logging.warning("Processing timeout, switching to chunked mode...")
            return process_large_file_chunked(file_path, filename, 5000)
            
    except Exception as e:
        logging.error(f"❌ Timeout-protected processing failed: {e}")
        return {"success": False, "error": str(e)}

def process_small_file_normal(file_path, filename):
    """Process small files normally"""
    try:
        logging.info(f"⚡ NORMAL PROCESSING: {filename}")
        
        from src.core.data.excel_processor import ExcelProcessor
        processor = ExcelProcessor()
        
        success = processor.load_file(file_path)
        if success:
            global _excel_processor
            with excel_processor_lock:
                _excel_processor = processor
                _excel_processor._last_loaded_file = file_path
            
            row_count = len(processor.df) if hasattr(processor, 'df') and processor.df is not None else 0
            logging.info(f"✅ Small file processed: {row_count} rows")
            
            return {
                "success": True,
                "method": "normal",
                "rows_processed": row_count
            }
        else:
            return {"success": False, "error": "File processing failed"}
            
    except Exception as e:
        logging.error(f"❌ Normal processing failed: {e}")
        return {"success": False, "error": str(e)}

# Usage in your upload endpoint:
def upload_with_optimization():
    """Example of how to use the optimized processing in your upload endpoint"""
    
    # ... existing upload code ...
    
    # After saving the file, use optimized processing:
    result = optimized_upload_processing(file_path, filename)
    
    if result["success"]:
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'File processed successfully ({result["rows_processed"]} rows)',
            'processing': False,
            'method': result["method"]
        })
    else:
        return jsonify({'error': result["error"]}), 500
