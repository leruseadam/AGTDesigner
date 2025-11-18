"""
Optimized Excel File Processing with Chunking
Handles large Excel files efficiently using streaming and chunking
"""

import pandas as pd
import logging
from typing import Iterator, List, Dict, Any, Optional
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class OptimizedExcelProcessor:
    """
    Optimized Excel processor that handles large files efficiently
    Uses chunking and streaming to reduce memory usage
    """
    
    def __init__(self, chunk_size: int = 1000):
        """
        Initialize optimized processor
        
        Args:
            chunk_size: Number of rows to process at a time
        """
        self.chunk_size = chunk_size
        self.file_path = None
        self.total_rows = 0
        self.processed_rows = 0
    
    def read_excel_in_chunks(
        self, 
        file_path: str, 
        sheet_name: str = 0
    ) -> Iterator[pd.DataFrame]:
        """
        Read Excel file in chunks for memory-efficient processing
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet to read (default first sheet)
        
        Yields:
            DataFrame chunks
        """
        self.file_path = file_path
        
        try:
            # First, get total row count
            temp_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
            
            # Read in chunks
            excel_file = pd.ExcelFile(file_path)
            df = excel_file.parse(sheet_name)
            
            self.total_rows = len(df)
            
            # Split into chunks
            for start_idx in range(0, len(df), self.chunk_size):
                end_idx = min(start_idx + self.chunk_size, len(df))
                chunk = df.iloc[start_idx:end_idx].copy()
                
                # Optimize chunk data types
                chunk = self._optimize_datatypes(chunk)
                
                self.processed_rows = end_idx
                yield chunk
                
        except Exception as e:
            logger.error(f"Error reading Excel file in chunks: {e}")
            raise
    
    def _optimize_datatypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame data types to reduce memory usage
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with optimized data types
        """
        for col in df.columns:
            col_type = df[col].dtype
            
            # Convert object columns with few unique values to category
            if col_type == 'object':
                unique_ratio = len(df[col].unique()) / len(df[col])
                if unique_ratio < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
            
            # Optimize numeric columns
            elif np.issubdtype(col_type, np.integer):
                c_min = df[col].min()
                c_max = df[col].max()
                
                # Use smallest integer type that fits the data
                if c_min >= 0:
                    if c_max < 255:
                        df[col] = df[col].astype(np.uint8)
                    elif c_max < 65535:
                        df[col] = df[col].astype(np.uint16)
                    elif c_max < 4294967295:
                        df[col] = df[col].astype(np.uint32)
                else:
                    if c_min > -128 and c_max < 127:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > -32768 and c_max < 32767:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > -2147483648 and c_max < 2147483647:
                        df[col] = df[col].astype(np.int32)
            
            # Optimize float columns
            elif np.issubdtype(col_type, np.floating):
                df[col] = df[col].astype(np.float32)
        
        return df
    
    def process_excel_file(
        self,
        file_path: str,
        processor_func: callable,
        sheet_name: str = 0,
        progress_callback: Optional[callable] = None
    ) -> List[Any]:
        """
        Process Excel file in chunks and apply processing function
        
        Args:
            file_path: Path to Excel file
            processor_func: Function to apply to each chunk
            sheet_name: Sheet to read
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of processed results
        """
        results = []
        
        try:
            for chunk in self.read_excel_in_chunks(file_path, sheet_name):
                # Process chunk
                chunk_result = processor_func(chunk)
                results.extend(chunk_result if isinstance(chunk_result, list) else [chunk_result])
                
                # Report progress
                if progress_callback:
                    progress = (self.processed_rows / self.total_rows) * 100
                    progress_callback(progress, self.processed_rows, self.total_rows)
            
            logger.info(f"Processed {self.total_rows} rows in {len(results)} chunks")
            return results
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
    
    def parallel_process_chunks(
        self,
        file_path: str,
        processor_func: callable,
        max_workers: int = 4,
        sheet_name: str = 0
    ) -> List[Any]:
        """
        Process Excel chunks in parallel for better performance
        
        Args:
            file_path: Path to Excel file
            processor_func: Function to apply to each chunk
            max_workers: Maximum number of parallel workers
            sheet_name: Sheet to read
        
        Returns:
            List of processed results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        try:
            # Read file into chunks first
            chunks = list(self.read_excel_in_chunks(file_path, sheet_name))
            
            # Process chunks in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all chunks
                futures = {
                    executor.submit(processor_func, chunk): i 
                    for i, chunk in enumerate(chunks)
                }
                
                # Collect results as they complete
                for future in as_completed(futures):
                    chunk_idx = futures[future]
                    try:
                        result = future.result()
                        results.append((chunk_idx, result))
                    except Exception as e:
                        logger.error(f"Error processing chunk {chunk_idx}: {e}")
            
            # Sort results by original chunk order
            results.sort(key=lambda x: x[0])
            results = [r[1] for r in results]
            
            logger.info(f"Parallel processed {len(chunks)} chunks with {max_workers} workers")
            return results
            
        except Exception as e:
            logger.error(f"Error in parallel processing: {e}")
            raise
    
    def get_memory_usage(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Get memory usage statistics for DataFrame
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with memory usage statistics
        """
        memory_usage = df.memory_usage(deep=True)
        total_mb = memory_usage.sum() / (1024 * 1024)
        
        return {
            'total_mb': round(total_mb, 2),
            'per_column_mb': {
                col: round(mem / (1024 * 1024), 2) 
                for col, mem in memory_usage.items()
            },
            'rows': len(df),
            'columns': len(df.columns)
        }
    
    def optimize_full_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all optimizations to a full DataFrame
        
        Args:
            df: Input DataFrame
        
        Returns:
            Optimized DataFrame
        """
        logger.info(f"Optimizing DataFrame with {len(df)} rows, {len(df.columns)} columns")
        
        # Get initial memory usage
        initial_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Optimize data types
        df = self._optimize_datatypes(df)
        
        # Get final memory usage
        final_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        reduction = ((initial_memory - final_memory) / initial_memory) * 100
        
        logger.info(f"Final memory usage: {final_memory:.2f} MB")
        logger.info(f"Memory reduction: {reduction:.1f}%")
        
        return df


def fast_excel_read(
    file_path: str,
    sheet_name: str = 0,
    use_chunks: bool = True,
    chunk_size: int = 1000
) -> pd.DataFrame:
    """
    Fast Excel file reading with automatic optimization
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet to read
        use_chunks: Whether to use chunked reading
        chunk_size: Size of chunks if using chunked reading
    
    Returns:
        Optimized DataFrame
    """
    if use_chunks:
        processor = OptimizedExcelProcessor(chunk_size=chunk_size)
        chunks = []
        
        for chunk in processor.read_excel_in_chunks(file_path, sheet_name):
            chunks.append(chunk)
        
        df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        processor = OptimizedExcelProcessor()
        df = processor.optimize_full_dataframe(df)
    
    return df


def estimate_processing_time(file_path: str, rows_per_second: int = 1000) -> Dict[str, Any]:
    """
    Estimate processing time for an Excel file
    
    Args:
        file_path: Path to Excel file
        rows_per_second: Estimated processing speed
    
    Returns:
        Dictionary with time estimates
    """
    try:
        # Get row count without loading full file
        df = pd.read_excel(file_path, nrows=0)
        with pd.ExcelFile(file_path) as xls:
            df = xls.parse(0)
            total_rows = len(df)
        
        estimated_seconds = total_rows / rows_per_second
        
        return {
            'total_rows': total_rows,
            'estimated_seconds': round(estimated_seconds, 1),
            'estimated_minutes': round(estimated_seconds / 60, 1),
            'rows_per_second': rows_per_second
        }
    except Exception as e:
        logger.error(f"Error estimating processing time: {e}")
        return {
            'error': str(e)
        }

