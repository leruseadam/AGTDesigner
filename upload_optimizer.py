"""
Ultra-fast file upload optimizer for web version
Addresses performance bottlenecks in file upload process
"""

import os
import time
import logging
import threading
from typing import Optional, Dict, Any
import pandas as pd
from flask import current_app

logger = logging.getLogger(__name__)

class UploadOptimizer:
    """Optimizes file upload performance by reducing processing overhead"""
    
    def __init__(self):
        self.processing_status = {}
        self.optimization_enabled = True
        
    def create_fast_upload_endpoint(self):
        """Create an optimized upload endpoint that returns immediately"""
        
        def fast_upload_file():
            """Ultra-fast file upload with minimal processing"""
            try:
                start_time = time.time()
                logger.info("=== FAST UPLOAD REQUEST START ===")
                
                # Basic validation
                if 'file' not in request.files:
                    return jsonify({'error': 'No file uploaded'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not file.filename.lower().endswith('.xlsx'):
                    return jsonify({'error': 'Only .xlsx files are allowed'}), 400
                
                # Check file size quickly
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                    return jsonify({'error': f'File too large. Maximum size is {current_app.config["MAX_CONTENT_LENGTH"] / (1024*1024):.1f} MB'}), 400
                
                # Sanitize filename
                from werkzeug.utils import secure_filename
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
                self.update_processing_status(file.filename, 'processing')
                
                # Start ultra-fast background processing
                thread = threading.Thread(
                    target=self.ultra_fast_background_processing,
                    args=(file.filename, temp_path)
                )
                thread.daemon = True
                thread.start()
                
                # Store in session for immediate access
                session['file_path'] = temp_path
                session['selected_tags'] = []
                
                # Return immediately
                upload_time = time.time() - start_time
                logger.info(f"Fast upload completed in {upload_time:.3f}s")
                
                return jsonify({
                    'message': 'File uploaded, processing in background',
                    'filename': sanitized_filename,
                    'upload_time': f"{upload_time:.3f}s",
                    'processing_status': 'background',
                    'performance': 'ultra_fast'
                })
                
            except Exception as e:
                logger.error(f"Fast upload error: {str(e)}")
                return jsonify({'error': 'Upload failed. Please try again.'}), 500
        
        return fast_upload_file
    
    def ultra_fast_background_processing(self, filename: str, temp_path: str):
        """Ultra-optimized background processing with minimal overhead"""
        try:
            logger.info(f"[FAST-BG] Starting ultra-fast processing: {filename}")
            start_time = time.time()
            
            # Step 1: Quick file validation
            if not os.path.exists(temp_path):
                self.update_processing_status(filename, 'error: File not found')
                return
            
            # Step 2: Create minimal ExcelProcessor with fast loading
            from src.core.data.excel_processor import ExcelProcessor
            processor = ExcelProcessor()
            
            # Disable heavy processing for speed
            processor.enable_product_db_integration = False
            
            # Step 3: Use fast loading mode
            logger.info(f"[FAST-BG] Loading file with fast mode: {temp_path}")
            load_start = time.time()
            
            # Use the fast_load_file method if available
            if hasattr(processor, 'fast_load_file'):
                success = processor.fast_load_file(temp_path)
                logger.info(f"[FAST-BG] Fast load completed in {time.time() - load_start:.3f}s, success: {success}")
            else:
                # Fallback to regular load but with optimizations
                success = self.optimized_load_file(processor, temp_path)
                logger.info(f"[FAST-BG] Optimized load completed in {time.time() - load_start:.3f}s, success: {success}")
            
            if not success or processor.df is None or processor.df.empty:
                self.update_processing_status(filename, 'error: Failed to load file data')
                return
            
            # Step 4: Minimal data processing (only essential operations)
            logger.info(f"[FAST-BG] Applying minimal processing to {len(processor.df)} rows")
            process_start = time.time()
            
            # Only do essential processing
            self.apply_minimal_processing(processor.df)
            
            logger.info(f"[FAST-BG] Minimal processing completed in {time.time() - process_start:.3f}s")
            
            # Step 5: Update global processor (skip database storage for speed)
            self.update_global_processor(processor, temp_path)
            
            # Step 6: Mark as ready
            self.update_processing_status(filename, 'ready')
            
            total_time = time.time() - start_time
            logger.info(f"[FAST-BG] Ultra-fast processing completed in {total_time:.3f}s")
            
        except Exception as e:
            logger.error(f"[FAST-BG] Processing error: {str(e)}")
            self.update_processing_status(filename, f'error: {str(e)}')
    
    def optimized_load_file(self, processor, file_path: str) -> bool:
        """Optimized file loading with reduced processing"""
        try:
            # Quick validation
            if not os.path.exists(file_path):
                return False
            
            # Read with minimal processing
            df = pd.read_excel(
                file_path,
                engine='openpyxl',
                dtype=str,  # Read everything as string for speed
                na_filter=False,
                keep_default_na=False
            )
            
            if df.empty:
                return False
            
            # Basic cleanup only
            df = df.drop_duplicates().reset_index(drop=True)
            
            # Ensure required columns exist with defaults
            required_columns = {
                'Product Name*': 'Unknown',
                'Product Type*': 'Unknown', 
                'Lineage': 'HYBRID',
                'Product Brand': 'Unknown',
                'Vendor': 'Unknown',
                'Description': '',
                'Ratio': '',
                'Product Strain': 'Mixed'
            }
            
            for col, default in required_columns.items():
                if col not in df.columns:
                    df[col] = default
            
            # Basic product name processing
            if 'Product Name*' in df.columns:
                df['Product Name*'] = df['Product Name*'].astype(str).str.strip()
                df['Description'] = df['Product Name*']
            
            # Basic product type normalization
            if 'Product Type*' in df.columns:
                df['Product Type*'] = df['Product Type*'].astype(str).str.strip()
            
            # Basic lineage processing
            if 'Lineage' in df.columns:
                df['Lineage'] = df['Lineage'].astype(str).str.strip().str.upper()
                # Set empty lineage to HYBRID
                empty_mask = (df['Lineage'] == '') | (df['Lineage'] == 'NAN')
                df.loc[empty_mask, 'Lineage'] = 'HYBRID'
            
            # Set the processed DataFrame
            processor.df = df
            processor._last_loaded_file = file_path
            
            return True
            
        except Exception as e:
            logger.error(f"Optimized load error: {str(e)}")
            return False
    
    def apply_minimal_processing(self, df: pd.DataFrame):
        """Apply only essential data processing for speed"""
        try:
            # Only do the most critical processing
            logger.info("[FAST-BG] Applying minimal processing...")
            
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
            
            logger.info("[FAST-BG] Minimal processing completed")
            
        except Exception as e:
            logger.error(f"Minimal processing error: {str(e)}")
    
    def update_global_processor(self, processor, temp_path: str):
        """Update the global processor with minimal overhead"""
        try:
            # Import here to avoid circular imports
            from app import _excel_processor, excel_processor_lock
            
            with excel_processor_lock:
                # Clear old processor
                if _excel_processor is not None:
                    if hasattr(_excel_processor, 'df'):
                        del _excel_processor.df
                    _excel_processor.selected_tags = []
                
                # Set new processor
                _excel_processor = processor
                _excel_processor._last_loaded_file = temp_path
                
                logger.info(f"[FAST-BG] Global processor updated with {len(processor.df)} rows")
                
        except Exception as e:
            logger.error(f"Error updating global processor: {str(e)}")
    
    def update_processing_status(self, filename: str, status: str):
        """Update processing status"""
        self.processing_status[filename] = status
        logger.info(f"Processing status for {filename}: {status}")

# Create global optimizer instance
upload_optimizer = UploadOptimizer()

def get_fast_upload_endpoint():
    """Get the optimized upload endpoint"""
    return upload_optimizer.create_fast_upload_endpoint()
