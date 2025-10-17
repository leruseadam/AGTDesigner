"""
Ultra-fast Excel processing with streaming, chunking, and parallel processing.
Optimized for large files and maximum performance.
"""

import pandas as pd
import numpy as np
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Iterator, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
from pathlib import Path
import gc
import io

from src.core.utils.performance_cache import excel_cached, EXCEL_CACHE
from src.core.utils.performance_monitor import performance_timer
from src.core.utils.lazy_loader import register_lazy, get_lazy

logger = logging.getLogger(__name__)

class StreamingExcelProcessor:
    """Streaming Excel processor for large files."""
    
    def __init__(self, chunk_size: int = 1000, max_workers: int = None):
        self.chunk_size = chunk_size
        self.max_workers = max_workers or min(mp.cpu_count(), 4)
        self._processing_stats = {
            'chunks_processed': 0,
            'rows_processed': 0,
            'processing_time': 0.0,
            'memory_usage': 0.0
        }
    
    @performance_timer('excel_streaming_load')
    def load_file_streaming(self, file_path: str, 
                          process_chunk: Callable[[pd.DataFrame], Any] = None) -> Iterator[Any]:
        """
        Load Excel file in streaming chunks.
        
        Args:
            file_path: Path to Excel file
            process_chunk: Function to process each chunk
            
        Yields:
            Processed chunk results
        """
        logger.info(f"Starting streaming load of {file_path}")
        start_time = time.time()
        
        try:
            # Read Excel file in chunks
            excel_file = pd.ExcelFile(file_path)
            sheet_name = excel_file.sheet_names[0]  # Use first sheet
            
            # Get total rows for progress tracking
            total_rows = len(pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)) + 1
            
            chunk_count = 0
            for chunk_start in range(0, total_rows, self.chunk_size):
                chunk_end = min(chunk_start + self.chunk_size, total_rows)
                
                # Read chunk
                chunk = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_name,
                    skiprows=chunk_start,
                    nrows=self.chunk_size,
                    dtype=str,  # Read as strings for speed
                    na_filter=False
                )
                
                if chunk.empty:
                    break
                
                chunk_count += 1
                
                # Process chunk if callback provided
                if process_chunk:
                    try:
                        result = process_chunk(chunk)
                        yield result
                    except Exception as e:
                        logger.error(f"Chunk processing failed: {e}")
                        yield None
                else:
                    yield chunk
                
                # Update stats
                self._processing_stats['chunks_processed'] += 1
                self._processing_stats['rows_processed'] += len(chunk)
                
                # Memory management
                if chunk_count % 10 == 0:
                    gc.collect()
                
                # Log progress
                if chunk_count % 100 == 0:
                    progress = (chunk_end / total_rows) * 100
                    logger.info(f"Streaming progress: {progress:.1f}% ({chunk_count} chunks)")
            
            self._processing_stats['processing_time'] = time.time() - start_time
            logger.info(f"Streaming load completed: {chunk_count} chunks, {self._processing_stats['rows_processed']} rows")
            
        except Exception as e:
            logger.error(f"Streaming load failed: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self._processing_stats.copy()

class ParallelExcelProcessor:
    """Parallel Excel processor using multiprocessing."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(mp.cpu_count(), 4)
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._processing_stats = {
            'files_processed': 0,
            'total_rows': 0,
            'parallel_processing_time': 0.0
        }
    
    @performance_timer('excel_parallel_processing')
    def process_files_parallel(self, file_paths: List[str], 
                             process_func: Callable[[str], Any]) -> List[Any]:
        """
        Process multiple Excel files in parallel.
        
        Args:
            file_paths: List of Excel file paths
            process_func: Function to process each file
            
        Returns:
            List of processing results
        """
        logger.info(f"Starting parallel processing of {len(file_paths)} files")
        start_time = time.time()
        
        # Submit all files for parallel processing
        futures = []
        for file_path in file_paths:
            future = self._executor.submit(process_func, file_path)
            futures.append(future)
        
        # Collect results
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                self._processing_stats['files_processed'] += 1
            except Exception as e:
                logger.error(f"Parallel processing failed: {e}")
                results.append(None)
        
        self._processing_stats['parallel_processing_time'] = time.time() - start_time
        logger.info(f"Parallel processing completed: {len(results)} results")
        
        return results
    
    def shutdown(self):
        """Shutdown parallel processor."""
        self._executor.shutdown(wait=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self._processing_stats.copy()

class UltraFastExcelProcessor:
    """Ultra-fast Excel processor with all optimizations."""
    
    def __init__(self, chunk_size: int = 1000, max_workers: int = None, 
                 enable_caching: bool = True):
        self.chunk_size = chunk_size
        self.max_workers = max_workers or min(mp.cpu_count(), 4)
        self.enable_caching = enable_caching
        
        self.streaming_processor = StreamingExcelProcessor(chunk_size, max_workers)
        self.parallel_processor = ParallelExcelProcessor(max_workers)
        
        # Performance optimizations
        self._optimized_dtypes = {
            'Product Name*': 'category',
            'Product Brand': 'category',
            'Product Type*': 'category',
            'Weight*': 'string',
            'Units': 'category',
            'Price*': 'string',
            'THC Content': 'string',
            'CBD Content': 'string',
            'Vendor/Supplier*': 'category',
            'Barcode*': 'string'
        }
        
        # Cache for processed data
        self._processed_cache = {}
        
        logger.info(f"Ultra-fast Excel processor initialized with {self.max_workers} workers")
    
    @excel_cached(ttl=3600)  # Cache for 1 hour
    def load_file_ultra_fast(self, file_path: str, 
                           sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Ultra-fast Excel file loading with optimizations.
        
        Args:
            file_path: Path to Excel file
            sample_size: Optional sample size for quick preview
            
        Returns:
            Optimized DataFrame
        """
        logger.info(f"Ultra-fast loading: {file_path}")
        start_time = time.time()
        
        try:
            # Use optimized loading parameters
            df = pd.read_excel(
                file_path,
                dtype=self._optimized_dtypes,
                na_filter=False,
                engine='openpyxl',
                nrows=sample_size
            )
            
            # Optimize DataFrame memory usage
            df = self._optimize_dataframe(df)
            
            load_time = time.time() - start_time
            logger.info(f"Ultra-fast load completed in {load_time:.3f}s: {len(df)} rows")
            
            return df
            
        except Exception as e:
            logger.error(f"Ultra-fast load failed: {e}")
            # Fallback to regular loading
            return pd.read_excel(file_path, nrows=sample_size)
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame for memory and performance."""
        try:
            # Convert object columns to category if beneficial
            for col in df.select_dtypes(include=['object']).columns:
                if col in self._optimized_dtypes:
                    continue
                
                # Convert to category if low cardinality
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
            
            # Optimize numeric columns
            for col in df.select_dtypes(include=['int64']).columns:
                if df[col].min() >= 0 and df[col].max() < 255:
                    df[col] = df[col].astype('uint8')
                elif df[col].min() >= -128 and df[col].max() < 127:
                    df[col] = df[col].astype('int8')
                elif df[col].min() >= 0 and df[col].max() < 65535:
                    df[col] = df[col].astype('uint16')
                elif df[col].min() >= -32768 and df[col].max() < 32767:
                    df[col] = df[col].astype('int16')
            
            return df
            
        except Exception as e:
            logger.warning(f"DataFrame optimization failed: {e}")
            return df
    
    def process_large_file_streaming(self, file_path: str, 
                                   process_func: Callable[[pd.DataFrame], Any],
                                   batch_size: int = None) -> List[Any]:
        """
        Process large Excel file using streaming.
        
        Args:
            file_path: Path to Excel file
            process_func: Function to process each chunk
            batch_size: Optional batch size override
            
        Returns:
            List of processing results
        """
        if batch_size:
            self.streaming_processor.chunk_size = batch_size
        
        results = []
        for chunk_result in self.streaming_processor.load_file_streaming(file_path, process_func):
            if chunk_result is not None:
                results.append(chunk_result)
        
        return results
    
    def process_multiple_files_parallel(self, file_paths: List[str],
                                      process_func: Callable[[str], Any]) -> List[Any]:
        """
        Process multiple Excel files in parallel.
        
        Args:
            file_paths: List of Excel file paths
            process_func: Function to process each file
            
        Returns:
            List of processing results
        """
        return self.parallel_processor.process_files_parallel(file_paths, process_func)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get Excel file information without loading full content."""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            # Get sheet info
            sheet_info = {}
            for sheet_name in excel_file.sheet_names:
                # Read just the header
                df_sample = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
                sheet_info[sheet_name] = {
                    'columns': list(df_sample.columns),
                    'column_count': len(df_sample.columns)
                }
            
            # Get file size
            file_size = Path(file_path).stat().st_size
            
            return {
                'file_path': file_path,
                'file_size_mb': file_size / (1024 * 1024),
                'sheet_names': excel_file.sheet_names,
                'sheet_info': sheet_info,
                'total_sheets': len(excel_file.sheet_names)
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {'error': str(e)}
    
    def validate_file_format(self, file_path: str) -> Dict[str, Any]:
        """Validate Excel file format and structure."""
        try:
            excel_file = pd.ExcelFile(file_path)
            
            # Check for required sheets/columns
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'file_info': self.get_file_info(file_path)
            }
            
            # Check first sheet
            if excel_file.sheet_names:
                first_sheet = excel_file.sheet_names[0]
                df_sample = pd.read_excel(file_path, sheet_name=first_sheet, nrows=5)
                
                # Check for required columns
                required_columns = ['Product Name*', 'Product Brand', 'Product Type*']
                missing_columns = [col for col in required_columns if col not in df_sample.columns]
                
                if missing_columns:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Missing required columns: {missing_columns}")
                
                # Check for empty file
                if len(df_sample) == 0:
                    validation_result['warnings'].append("File appears to be empty")
                
            else:
                validation_result['valid'] = False
                validation_result['errors'].append("No sheets found in Excel file")
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"File validation failed: {str(e)}"],
                'warnings': [],
                'file_info': {}
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        return {
            'streaming': self.streaming_processor.get_stats(),
            'parallel': self.parallel_processor.get_stats(),
            'cache_stats': EXCEL_CACHE.get_stats() if self.enable_caching else {},
            'memory_usage': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),
            'vms_mb': memory_info.vms / (1024 * 1024),
            'percent': process.memory_percent()
        }
    
    def clear_cache(self):
        """Clear processing cache."""
        if self.enable_caching:
            EXCEL_CACHE.clear()
        self._processed_cache.clear()
        gc.collect()
        logger.info("Processing cache cleared")
    
    def shutdown(self):
        """Shutdown processor and cleanup resources."""
        self.parallel_processor.shutdown()
        self.clear_cache()
        logger.info("Ultra-fast Excel processor shutdown")

# Global ultra-fast processor
_ultra_fast_processor = None
_processor_lock = threading.Lock()

def get_ultra_fast_processor() -> UltraFastExcelProcessor:
    """Get or create global ultra-fast Excel processor."""
    global _ultra_fast_processor
    
    if _ultra_fast_processor is None:
        with _processor_lock:
            if _ultra_fast_processor is None:
                _ultra_fast_processor = UltraFastExcelProcessor()
                logger.info("Global ultra-fast Excel processor created")
    
    return _ultra_fast_processor

def clear_excel_cache():
    """Clear Excel processing cache."""
    processor = get_ultra_fast_processor()
    processor.clear_cache()

# Lazy-loaded processor for better startup performance
def _create_ultra_fast_processor() -> UltraFastExcelProcessor:
    """Create ultra-fast Excel processor (lazy loaded)."""
    return UltraFastExcelProcessor()

register_lazy('ultra_fast_excel_processor', _create_ultra_fast_processor, background=True)

def get_lazy_excel_processor() -> UltraFastExcelProcessor:
    """Get lazy-loaded Excel processor."""
    return get_lazy('ultra_fast_excel_processor')
