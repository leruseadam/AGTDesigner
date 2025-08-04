#!/usr/bin/env python3
"""
PythonAnywhere Upload Optimizer
Dramatically improves Excel upload performance on PythonAnywhere by implementing:
1. Chunked file reading for large files
2. Minimal processing during upload
3. Background processing for heavy operations
4. Memory optimization
5. Caching improvements
"""

import os
import sys
import time
import logging
import threading
import gc
from typing import Optional, Dict, Any
import pandas as pd
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PythonAnywhereUploadOptimizer:
    """Optimized upload processor specifically for PythonAnywhere environment."""
    
    def __init__(self):
        self.chunk_size = 1000  # Process 1000 rows at a time
        self.max_memory_mb = 100  # Limit memory usage to 100MB
        self.enable_background_processing = True
        self.cache_enabled = True
        self.processing_status = {}
        
    def optimize_for_pythonanywhere(self):
        """Apply PythonAnywhere-specific optimizations."""
        # Reduce pandas memory usage
        pd.options.mode.chained_assignment = None
        
        # Force garbage collection
        gc.collect()
        
        # Set pandas to use less memory
        pd.options.mode.use_inf_as_na = True
        
        logger.info("Applied PythonAnywhere optimizations")
    
    def chunked_read_excel(self, file_path: str) -> Optional[pd.DataFrame]:
        """Read Excel file in chunks to reduce memory usage."""
        try:
            logger.info(f"Starting chunked read of {file_path}")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"File size: {file_size_mb:.2f} MB")
            
            # For small files (< 5MB), read normally
            if file_size_mb < 5:
                logger.info("Small file detected, using normal read")
                return pd.read_excel(file_path, engine='openpyxl')
            
            # For large files, use chunked reading
            logger.info("Large file detected, using chunked reading")
            
            # Read only the first few rows to get column structure
            sample_df = pd.read_excel(file_path, engine='openpyxl', nrows=10)
            columns = sample_df.columns.tolist()
            
            # Read in chunks
            chunks = []
            chunk_count = 0
            
            for chunk in pd.read_excel(file_path, engine='openpyxl', chunksize=self.chunk_size):
                chunk_count += 1
                logger.info(f"Processing chunk {chunk_count} ({len(chunk)} rows)")
                
                # Apply minimal processing to chunk
                chunk = self.minimal_chunk_processing(chunk)
                chunks.append(chunk)
                
                # Force garbage collection every few chunks
                if chunk_count % 5 == 0:
                    gc.collect()
                
                # Check memory usage
                if self.check_memory_usage():
                    logger.warning("Memory usage high, forcing garbage collection")
                    gc.collect()
            
            # Combine chunks
            logger.info(f"Combining {len(chunks)} chunks")
            combined_df = pd.concat(chunks, ignore_index=True)
            
            # Final cleanup
            del chunks
            gc.collect()
            
            logger.info(f"Chunked read complete: {len(combined_df)} total rows")
            return combined_df
            
        except Exception as e:
            logger.error(f"Error in chunked read: {e}")
            return None
    
    def minimal_chunk_processing(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Apply minimal processing to a chunk to reduce processing time."""
        try:
            # Only do essential processing
            if len(chunk) == 0:
                return chunk
            
            # Handle duplicate columns
            chunk = self.handle_duplicate_columns(chunk)
            
            # Basic string cleaning for key columns
            string_columns = ['Product Name*', 'Product Type*', 'Lineage', 'Product Brand']
            for col in string_columns:
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(str).str.strip()
            
            # Remove obvious duplicates
            chunk.drop_duplicates(inplace=True)
            
            return chunk
            
        except Exception as e:
            logger.error(f"Error in minimal chunk processing: {e}")
            return chunk
    
    def handle_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle duplicate column names efficiently."""
        if df.columns.duplicated().any():
            # Get duplicate columns
            duplicated = df.columns[df.columns.duplicated()].unique()
            logger.info(f"Found duplicate columns: {duplicated}")
            
            # Keep only the first occurrence of each column
            df = df.loc[:, ~df.columns.duplicated()]
            
        return df
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is too high."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            if memory_mb > self.max_memory_mb:
                logger.warning(f"Memory usage high: {memory_mb:.1f} MB")
                return True
            return False
        except ImportError:
            # psutil not available, skip memory check
            return False
    
    def fast_upload_process(self, file_path: str) -> Dict[str, Any]:
        """Ultra-fast upload process optimized for PythonAnywhere."""
        start_time = time.time()
        
        try:
            # Apply optimizations
            self.optimize_for_pythonanywhere()
            
            # Update status
            self.processing_status[file_path] = 'reading'
            
            # Read file with chunked processing
            df = self.chunked_read_excel(file_path)
            
            if df is None or df.empty:
                return {
                    'success': False,
                    'error': 'Failed to read file or file is empty',
                    'processing_time': time.time() - start_time
                }
            
            # Update status
            self.processing_status[file_path] = 'processing'
            
            # Create minimal ExcelProcessor
            processor = ExcelProcessor()
            
            # Disable heavy features for faster processing
            processor.enable_product_db_integration(False)
            
            # Set the dataframe directly (skip file loading)
            processor.df = df
            
            # Minimal processing
            processor._cache_dropdown_values()
            
            # Store processor in global context (simplified)
            import flask
            if hasattr(flask, 'g'):
                flask.g.excel_processor = processor
            
            processing_time = time.time() - start_time
            
            logger.info(f"Fast upload completed in {processing_time:.2f} seconds")
            
            return {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns),
                'processing_time': processing_time,
                'memory_optimized': True
            }
            
        except Exception as e:
            logger.error(f"Error in fast upload process: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def background_processing(self, file_path: str):
        """Background processing for heavy operations."""
        try:
            logger.info(f"Starting background processing for {file_path}")
            
            # Update status
            self.processing_status[file_path] = 'background_processing'
            
            # Get the processor
            import flask
            if hasattr(flask, 'g') and hasattr(flask.g, 'excel_processor'):
                processor = flask.g.excel_processor
                
                # Enable product database integration in background
                processor.enable_product_db_integration(True)
                
                # Run heavy processing in background
                processor._schedule_product_db_integration()
                
                logger.info("Background processing completed")
                self.processing_status[file_path] = 'completed'
            else:
                logger.error("No processor found for background processing")
                
        except Exception as e:
            logger.error(f"Error in background processing: {e}")
            self.processing_status[file_path] = f'error: {str(e)}'

def create_optimized_upload_endpoint():
    """Create an optimized upload endpoint for PythonAnywhere."""
    
    optimizer = PythonAnywhereUploadOptimizer()
    
    def optimized_upload_handler(file_path: str):
        """Optimized upload handler."""
        
        # Start fast processing
        result = optimizer.fast_upload_process(file_path)
        
        if result['success']:
            # Start background processing if enabled
            if optimizer.enable_background_processing:
                thread = threading.Thread(
                    target=optimizer.background_processing,
                    args=(file_path,)
                )
                thread.daemon = True
                thread.start()
            
            return {
                'status': 'success',
                'message': 'File uploaded and processed successfully',
                'data': result
            }
        else:
            return {
                'status': 'error',
                'message': result['error'],
                'data': result
            }
    
    return optimized_upload_handler

# Performance monitoring
def monitor_performance():
    """Monitor system performance during uploads."""
    try:
        import psutil
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        logger.info(f"Performance - CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%")
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent
        }
    except ImportError:
        logger.warning("psutil not available, skipping performance monitoring")
        return None

if __name__ == "__main__":
    # Test the optimizer
    print("PythonAnywhere Upload Optimizer")
    print("=" * 40)
    
    optimizer = PythonAnywhereUploadOptimizer()
    
    # Test with a sample file if available
    test_file = "test_sample.xlsx"
    if os.path.exists(test_file):
        print(f"Testing with {test_file}")
        result = optimizer.fast_upload_process(test_file)
        print(f"Result: {result}")
    else:
        print("No test file found. Create a test_sample.xlsx file to test the optimizer.")
    
    # Monitor performance
    performance = monitor_performance()
    if performance:
        print(f"Performance: {performance}") 