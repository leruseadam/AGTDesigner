"""
Optimized upload route for ultra-fast file uploads
Replaces the slow upload process with a streamlined version
"""

import os
import time
import logging
import threading
from flask import request, jsonify, session, current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

def create_optimized_upload_route():
    """Create an optimized upload route that returns immediately"""
    
    def optimized_upload_file():
        """Ultra-fast file upload with immediate response"""
        try:
            start_time = time.time()
            logger.info("=== OPTIMIZED UPLOAD START ===")
            
            # Quick validation
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith('.xlsx'):
                return jsonify({'error': 'Only .xlsx files are allowed'}), 400
            
            # Quick file size check
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                return jsonify({'error': f'File too large. Maximum size is {current_app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.1f} MB'}), 400
            
            # Sanitize filename
            sanitized_filename = secure_filename(file.filename)
            
            # Save file quickly
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            temp_path = os.path.join(upload_folder, sanitized_filename)
            
            save_start = time.time()
            file.save(temp_path)
            save_time = time.time() - save_start
            
            logger.info(f"File saved in {save_time:.3f}s: {temp_path}")
            
            # Mark as processing
            from app import update_processing_status
            update_processing_status(file.filename, 'processing')
            
            # Start ultra-fast background processing
            thread = threading.Thread(
                target=ultra_fast_background_processing,
                args=(file.filename, temp_path)
            )
            thread.daemon = True
            thread.start()
            
            # Store in session for immediate access
            session['file_path'] = temp_path
            session['selected_tags'] = []
            
            # Return immediately
            upload_time = time.time() - start_time
            logger.info(f"Optimized upload completed in {upload_time:.3f}s")
            
            return jsonify({
                'message': 'File uploaded, processing in background',
                'filename': sanitized_filename,
                'upload_time': f"{upload_time:.3f}s",
                'processing_status': 'background',
                'performance': 'ultra_fast'
            })
            
        except Exception as e:
            logger.error(f"Optimized upload error: {str(e)}")
            return jsonify({'error': 'Upload failed. Please try again.'}), 500
    
    return optimized_upload_file

def ultra_fast_background_processing(filename: str, temp_path: str):
    """Ultra-optimized background processing with minimal overhead"""
    try:
        logger.info(f"[FAST-BG] Starting ultra-fast processing: {filename}")
        start_time = time.time()
        
        # Step 1: Quick file validation
        if not os.path.exists(temp_path):
            from app import update_processing_status
            update_processing_status(filename, 'error: File not found')
            return
        
        # Step 2: Create ExcelProcessor with fast loading
        from src.core.data.excel_processor import ExcelProcessor
        processor = ExcelProcessor()
        
        # Disable heavy processing for speed
        if hasattr(processor, 'enable_product_db_integration'):
            processor.enable_product_db_integration(False)
        
        # Step 3: Use fast loading mode
        logger.info(f"[FAST-BG] Loading file with fast mode: {temp_path}")
        load_start = time.time()
        
        # Use the fast_load_file method
        success = processor.fast_load_file(temp_path)
        load_time = time.time() - load_start
        
        logger.info(f"[FAST-BG] Fast load completed in {load_time:.3f}s, success: {success}")
        
        if not success or processor.df is None or processor.df.empty:
            from app import update_processing_status
            update_processing_status(filename, 'error: Failed to load file data')
            return
        
        # Step 4: Minimal additional processing
        logger.info(f"[FAST-BG] Applying minimal additional processing to {len(processor.df)} rows")
        process_start = time.time()
        
        # Only do essential additional processing
        apply_essential_processing(processor.df)
        
        logger.info(f"[FAST-BG] Essential processing completed in {time.time() - process_start:.3f}s")
        
        # Step 5: Update global processor (skip database storage for speed)
        update_global_processor_fast(processor, temp_path)
        
        # Step 6: Mark as ready
        from app import update_processing_status
        update_processing_status(filename, 'ready')
        
        total_time = time.time() - start_time
        logger.info(f"[FAST-BG] Ultra-fast processing completed in {total_time:.3f}s")
        
    except Exception as e:
        logger.error(f"[FAST-BG] Processing error: {str(e)}")
        from app import update_processing_status
        update_processing_status(filename, f'error: {str(e)}')

def apply_essential_processing(df):
    """Apply only the most essential data processing for speed"""
    try:
        logger.info("[FAST-BG] Applying essential processing...")
        
        # Only do the most critical processing that's needed for the UI
        import pandas as pd
        
        # Basic string operations
        if 'Product Name*' in df.columns:
            df['Product Name*'] = df['Product Name*'].astype(str).str.strip()
        
        if 'Description' in df.columns:
            df['Description'] = df['Description'].astype(str).str.strip()
        
        # Basic lineage standardization (minimal)
        if 'Lineage' in df.columns:
            df['Lineage'] = df['Lineage'].astype(str).str.strip().str.upper()
            # Quick lineage fixes
            df['Lineage'] = df['Lineage'].replace({
                'INDICA_HYBRID': 'HYBRID/INDICA',
                'SATIVA_HYBRID': 'HYBRID/SATIVA',
                'SATIVA': 'SATIVA',
                'HYBRID': 'HYBRID',
                'INDICA': 'INDICA',
                'CBD': 'CBD'
            })
            
            # Set empty to HYBRID
            empty_mask = (df['Lineage'] == '') | (df['Lineage'] == 'NAN')
            df.loc[empty_mask, 'Lineage'] = 'HYBRID'
        
        # Basic product strain processing
        if 'Product Strain' in df.columns:
            df['Product Strain'] = df['Product Strain'].astype(str).str.strip()
            empty_strain = (df['Product Strain'] == '') | (df['Product Strain'] == 'NAN')
            df.loc[empty_strain, 'Product Strain'] = 'Mixed'
        
        # Basic ratio processing
        if 'Ratio' in df.columns:
            df['Ratio'] = df['Ratio'].astype(str).str.strip()
            empty_ratio = (df['Ratio'] == '') | (df['Ratio'] == 'NAN')
            df.loc[empty_ratio, 'Ratio'] = 'THC:|BR|CBD:'
        
        # Ensure ProductName column exists for UI
        if 'Product Name*' in df.columns and 'ProductName' not in df.columns:
            df['ProductName'] = df['Product Name*']
        
        logger.info("[FAST-BG] Essential processing completed")
        
    except Exception as e:
        logger.error(f"Essential processing error: {str(e)}")

def update_global_processor_fast(processor, temp_path: str):
    """Update the global processor with minimal overhead"""
    try:
        # Import here to avoid circular imports
        from app import _excel_processor, excel_processor_lock
        
        with excel_processor_lock:
            # Clear old processor efficiently
            if _excel_processor is not None:
                if hasattr(_excel_processor, 'df'):
                    del _excel_processor.df
                if hasattr(_excel_processor, 'selected_tags'):
                    _excel_processor.selected_tags = []
            
            # Set new processor
            _excel_processor = processor
            _excel_processor._last_loaded_file = temp_path
            
            logger.info(f"[FAST-BG] Global processor updated with {len(processor.df)} rows")
            
    except Exception as e:
        logger.error(f"Error updating global processor: {str(e)}")
