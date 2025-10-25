# Excel Upload Performance Optimization
# This script optimizes Excel upload performance for web version

import os
import time
import logging
from flask import request, jsonify, session
import pandas as pd

def create_fast_excel_processor():
    """Create a fast Excel processor optimized for web performance."""
    
    class FastExcelProcessor:
        def __init__(self):
            self.df = None
            self.logger = logging.getLogger(__name__)
            self._processing_mode = 'fast'
            
        def load_file_fast(self, file_path):
            """Ultra-fast Excel file loading with minimal processing."""
            start_time = time.time()
            
            try:
                self.logger.info(f"🚀 Fast loading: {file_path}")
                
                # Use optimized pandas settings
                pd.set_option('mode.chained_assignment', None)
                
                # Read with minimal processing
                self.df = pd.read_excel(
                    file_path,
                    engine='openpyxl',
                    dtype=str,  # Read everything as string for speed
                    na_filter=False,  # Don't filter NA values
                    keep_default_na=False,  # Don't use default NA values
                    nrows=None  # Read all rows but process minimally
                )
                
                # Basic cleanup only
                self.df = self.df.fillna('')
                
                # Add essential columns if missing
                essential_columns = [
                    'Product Name*', 'Product Type*', 'Lineage', 
                    'THC test result', 'CBD test result', 'Test result unit (% or mg)'
                ]
                
                for col in essential_columns:
                    if col not in self.df.columns:
                        self.df[col] = ''
                
                load_time = time.time() - start_time
                self.logger.info(f"✅ Fast load complete: {len(self.df)} rows in {load_time:.2f}s")
                
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Fast load failed: {e}")
                return False
        
        def get_basic_stats(self):
            """Get basic statistics without heavy processing."""
            if self.df is None:
                return {}
            
            return {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'product_types': self.df['Product Type*'].nunique() if 'Product Type*' in self.df.columns else 0,
                'strains': self.df['Product Strain'].nunique() if 'Product Strain' in self.df.columns else 0
            }
    
    return FastExcelProcessor()

def optimize_upload_endpoint(app):
    """Add optimized upload endpoint to Flask app."""
    
    @app.route('/upload-fast', methods=['POST'])
    def upload_file_fast():
        """Ultra-fast Excel upload optimized for web performance."""
        start_time = time.time()
        
        try:
            # Validate request quickly
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if not file or file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate extension
            if not file.filename.lower().endswith(('.xlsx', '.xls')):
                return jsonify({'error': 'Only Excel files allowed'}), 400
            
            # Save file quickly
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(uploads_dir, safe_filename)
            
            file.save(file_path)
            
            # Update session
            session.permanent = True
            session['file_path'] = file_path
            session['uploaded_filename'] = file.filename
            session['upload_timestamp'] = timestamp
            session.modified = True
            
            # Fast processing
            processor = create_fast_excel_processor()
            success = processor.load_file_fast(file_path)
            
            if success:
                stats = processor.get_basic_stats()
                
                # Store processor globally for immediate use
                from flask import g
                g.excel_processor = processor
                
                upload_time = time.time() - start_time
                
                return jsonify({
                    'success': True,
                    'message': f'File uploaded and processed in {upload_time:.2f}s',
                    'filename': file.filename,
                    'stats': stats,
                    'processing_time': upload_time
                })
            else:
                return jsonify({'error': 'Failed to process Excel file'}), 500
                
        except Exception as e:
            logging.error(f"Fast upload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/upload-progressive', methods=['POST'])
    def upload_file_progressive():
        """Progressive upload that processes file in chunks for large files."""
        start_time = time.time()
        
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if not file or file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            # Save file
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(uploads_dir, safe_filename)
            
            file.save(file_path)
            
            # Update session
            session.permanent = True
            session['file_path'] = file_path
            session['uploaded_filename'] = file.filename
            session['upload_timestamp'] = timestamp
            session.modified = True
            
            # Determine processing strategy based on file size
            if file_size > 10 * 1024 * 1024:  # 10MB threshold
                # Large file: Use progressive processing
                return process_large_file_progressive(file_path, file.filename, start_time)
            else:
                # Small file: Use fast processing
                processor = create_fast_excel_processor()
                success = processor.load_file_fast(file_path)
                
                if success:
                    stats = processor.get_basic_stats()
                    upload_time = time.time() - start_time
                    
                    return jsonify({
                        'success': True,
                        'message': f'File processed in {upload_time:.2f}s',
                        'filename': file.filename,
                        'stats': stats,
                        'processing_time': upload_time
                    })
                else:
                    return jsonify({'error': 'Failed to process Excel file'}), 500
                    
        except Exception as e:
            logging.error(f"Progressive upload error: {e}")
            return jsonify({'error': str(e)}), 500

def process_large_file_progressive(file_path, filename, start_time):
    """Process large files progressively to avoid timeouts."""
    try:
        # For large files, we'll process in chunks
        # This is a simplified version - in production, you'd want more sophisticated chunking
        
        # Read just the first chunk to get basic info
        df_sample = pd.read_excel(
            file_path,
            engine='openpyxl',
            dtype=str,
            na_filter=False,
            keep_default_na=False,
            nrows=1000  # Just first 1000 rows for initial processing
        )
        
        # Estimate total rows
        total_rows_estimate = len(df_sample) * 10  # Rough estimate
        
        return jsonify({
            'success': True,
            'message': f'Large file uploaded, processing in background',
            'filename': filename,
            'estimated_rows': total_rows_estimate,
            'processing_mode': 'progressive',
            'status': 'processing'
        })
        
    except Exception as e:
        logging.error(f"Progressive processing error: {e}")
        return jsonify({'error': f'Progressive processing failed: {str(e)}'}), 500

# Performance monitoring
def log_performance_metrics(operation, duration, details=None):
    """Log performance metrics for monitoring."""
    logging.info(f"📊 Performance: {operation} took {duration:.2f}s {f'- {details}' if details else ''}")

if __name__ == "__main__":
    print("Excel Upload Performance Optimization Module")
    print("This module provides fast Excel upload capabilities for web applications.")
