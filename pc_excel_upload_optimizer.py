/**
 * PC Excel Upload Optimizer - Backend chunked processing
 * Handles large Excel files efficiently for PC users
 */

import pandas as pd
import os
import time
import logging
from typing import Dict, Any, Optional
from flask import request, jsonify
import tempfile
import shutil

class PCExcelUploadOptimizer:
    """Optimized Excel processing for PC users with chunked uploads"""
    
    def __init__(self):
        self.chunk_storage = {}
        self.processing_status = {}
        self.max_chunk_size = 1000  # rows per chunk
        self.max_file_size = 100 * 1024 * 1024  # 100MB limit
        
    def handle_chunk_upload(self, chunk_data: bytes, chunk_index: int, total_chunks: int, 
                           filename: str, session_id: str) -> Dict[str, Any]:
        """Handle individual chunk upload"""
        try:
            start_time = time.time()
            
            # Validate chunk
            if not chunk_data or len(chunk_data) == 0:
                return {'success': False, 'error': 'Empty chunk received'}
            
            # Initialize session storage if needed
            if session_id not in self.chunk_storage:
                self.chunk_storage[session_id] = {
                    'chunks': {},
                    'total_chunks': total_chunks,
                    'filename': filename,
                    'start_time': time.time(),
                    'uploaded_chunks': 0
                }
            
            session_data = self.chunk_storage[session_id]
            
            # Store chunk
            session_data['chunks'][chunk_index] = chunk_data
            session_data['uploaded_chunks'] += 1
            
            # Check if all chunks received
            if session_data['uploaded_chunks'] == total_chunks:
                return self._process_complete_file(session_id)
            
            # Return success for partial upload
            elapsed = time.time() - start_time
            progress = (session_data['uploaded_chunks'] / total_chunks) * 100
            
            return {
                'success': True,
                'message': f'Chunk {chunk_index + 1}/{total_chunks} uploaded',
                'progress': progress,
                'elapsed_time': elapsed,
                'remaining_chunks': total_chunks - session_data['uploaded_chunks']
            }
            
        except Exception as e:
            logging.error(f"Chunk upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_complete_file(self, session_id: str) -> Dict[str, Any]:
        """Process complete file after all chunks received"""
        try:
            session_data = self.chunk_storage[session_id]
            
            # Reassemble file
            temp_file_path = self._reassemble_file(session_data)
            
            if not temp_file_path:
                return {'success': False, 'error': 'Failed to reassemble file'}
            
            # Process Excel file
            result = self._process_excel_file(temp_file_path, session_data['filename'])
            
            # Cleanup
            self._cleanup_session(session_id)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return result
            
        except Exception as e:
            logging.error(f"Complete file processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _reassemble_file(self, session_data: Dict[str, Any]) -> Optional[str]:
        """Reassemble chunks into complete file"""
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
            
            with os.fdopen(temp_fd, 'wb') as temp_file:
                # Write chunks in order
                for i in range(session_data['total_chunks']):
                    if i in session_data['chunks']:
                        temp_file.write(session_data['chunks'][i])
                    else:
                        logging.error(f"Missing chunk {i}")
                        return None
            
            return temp_path
            
        except Exception as e:
            logging.error(f"File reassembly error: {e}")
            return None
    
    def _process_excel_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process Excel file with PC optimizations"""
        try:
            start_time = time.time()
            
            # Quick file validation
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {'success': False, 'error': 'Empty file'}
            
            if file_size > self.max_file_size:
                return {'success': False, 'error': f'File too large ({file_size / 1024 / 1024:.1f}MB)'}
            
            logging.info(f"🚀 PC EXCEL PROCESSING: {filename} ({file_size:,} bytes)")
            
            # Estimate rows for processing strategy
            estimated_rows = self._estimate_row_count(file_path)
            
            # Choose processing strategy based on size
            if estimated_rows > 10000:
                result = self._process_large_file_chunked(file_path, estimated_rows)
            elif estimated_rows > 1000:
                result = self._process_medium_file_optimized(file_path)
            else:
                result = self._process_small_file_fast(file_path)
            
            # Add processing metrics
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            result['file_size'] = file_size
            result['estimated_rows'] = estimated_rows
            
            logging.info(f"✅ PC EXCEL PROCESSING COMPLETE: {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            logging.error(f"Excel processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _estimate_row_count(self, file_path: str) -> int:
        """Estimate row count without loading full file"""
        try:
            # Read first 100 rows to estimate
            sample_df = pd.read_excel(file_path, nrows=100, engine='openpyxl')
            
            if sample_df.empty:
                return 0
            
            # Estimate based on file size and sample
            file_size = os.path.getsize(file_path)
            sample_size = len(sample_df)
            
            # Rough estimation: each row is approximately 200 bytes
            estimated_rows = int(file_size / 200)
            
            # Cap at reasonable limit
            return min(estimated_rows, 100000)
            
        except Exception as e:
            logging.warning(f"Row estimation failed: {e}")
            return 1000  # Default estimate
    
    def _process_small_file_fast(self, file_path: str) -> Dict[str, Any]:
        """Process small files (<1000 rows) with maximum speed"""
        try:
            # Load entire file at once
            df = pd.read_excel(
                file_path,
                engine='openpyxl',
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )
            
            if df.empty:
                return {'success': False, 'error': 'No data found in file'}
            
            # Apply minimal processing
            df = self._apply_minimal_processing(df)
            
            # Update global processor
            self._update_global_processor(df)
            
            return {
                'success': True,
                'message': f'Small file processed successfully',
                'rows_processed': len(df),
                'processing_type': 'small_file_fast'
            }
            
        except Exception as e:
            logging.error(f"Small file processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_medium_file_optimized(self, file_path: str) -> Dict[str, Any]:
        """Process medium files (1000-10000 rows) with optimizations"""
        try:
            # Load with optimizations
            df = pd.read_excel(
                file_path,
                engine='openpyxl',
                dtype=str,
                na_filter=False,
                keep_default_na=False,
                nrows=50000  # Limit for safety
            )
            
            if df.empty:
                return {'success': False, 'error': 'No data found in file'}
            
            # Apply optimized processing
            df = self._apply_optimized_processing(df)
            
            # Update global processor
            self._update_global_processor(df)
            
            return {
                'success': True,
                'message': f'Medium file processed successfully',
                'rows_processed': len(df),
                'processing_type': 'medium_file_optimized'
            }
            
        except Exception as e:
            logging.error(f"Medium file processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_large_file_chunked(self, file_path: str, estimated_rows: int) -> Dict[str, Any]:
        """Process large files (>10000 rows) in chunks"""
        try:
            chunk_size = self.max_chunk_size
            all_chunks = []
            processed_rows = 0
            
            logging.info(f"📦 Processing large file in chunks: {estimated_rows:,} rows")
            
            # Process file in chunks
            for chunk_start in range(0, estimated_rows, chunk_size):
                try:
                    # Read chunk
                    chunk_df = pd.read_excel(
                        file_path,
                        skiprows=chunk_start,
                        nrows=chunk_size,
                        engine='openpyxl',
                        dtype=str,
                        na_filter=False,
                        keep_default_na=False
                    )
                    
                    if chunk_df.empty:
                        break
                    
                    # Process chunk
                    processed_chunk = self._apply_chunk_processing(chunk_df)
                    all_chunks.append(processed_chunk)
                    processed_rows += len(processed_chunk)
                    
                    # Progress logging
                    progress = (processed_rows / estimated_rows) * 100
                    logging.info(f"📊 Chunk progress: {progress:.1f}% ({processed_rows:,}/{estimated_rows:,} rows)")
                    
                except Exception as chunk_error:
                    logging.warning(f"Chunk processing failed: {chunk_error}")
                    continue
            
            if not all_chunks:
                return {'success': False, 'error': 'No chunks processed successfully'}
            
            # Combine chunks
            df = pd.concat(all_chunks, ignore_index=True)
            
            # Final processing
            df = self._apply_final_processing(df)
            
            # Update global processor
            self._update_global_processor(df)
            
            return {
                'success': True,
                'message': f'Large file processed successfully in chunks',
                'rows_processed': len(df),
                'chunks_processed': len(all_chunks),
                'processing_type': 'large_file_chunked'
            }
            
        except Exception as e:
            logging.error(f"Large file processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _apply_minimal_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply minimal processing for speed"""
        # Only essential processing
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.drop_duplicates()  # Remove duplicates
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def _apply_optimized_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply optimized processing for medium files"""
        # Remove empty rows and duplicates
        df = df.dropna(how='all')
        df = df.drop_duplicates()
        df.reset_index(drop=True, inplace=True)
        
        # Basic data cleaning
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def _apply_chunk_processing(self, chunk_df: pd.DataFrame) -> pd.DataFrame:
        """Process individual chunk"""
        # Remove empty rows
        chunk_df = chunk_df.dropna(how='all')
        
        # Basic cleaning
        for col in chunk_df.columns:
            if chunk_df[col].dtype == 'object':
                chunk_df[col] = chunk_df[col].astype(str).str.strip()
        
        return chunk_df
    
    def _apply_final_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply final processing after combining chunks"""
        # Remove duplicates that might have been created during chunking
        df = df.drop_duplicates()
        df.reset_index(drop=True, inplace=True)
        
        return df
    
    def _update_global_processor(self, df: pd.DataFrame):
        """Update global Excel processor with processed data"""
        try:
            # Import here to avoid circular imports
            from src.core.data.excel_processor import ExcelProcessor
            
            # Create or update global processor
            global _excel_processor
            if '_excel_processor' not in globals():
                _excel_processor = ExcelProcessor()
            
            _excel_processor.df = df
            _excel_processor._cache_dropdown_values()
            
            logging.info(f"✅ Global processor updated with {len(df)} rows")
            
        except Exception as e:
            logging.error(f"Failed to update global processor: {e}")
    
    def _cleanup_session(self, session_id: str):
        """Clean up session data"""
        try:
            if session_id in self.chunk_storage:
                del self.chunk_storage[session_id]
            logging.info(f"Session {session_id} cleaned up")
        except Exception as e:
            logging.warning(f"Session cleanup failed: {e}")
    
    def get_upload_status(self, session_id: str) -> Dict[str, Any]:
        """Get upload status for a session"""
        if session_id not in self.chunk_storage:
            return {'success': False, 'error': 'Session not found'}
        
        session_data = self.chunk_storage[session_id]
        
        return {
            'success': True,
            'uploaded_chunks': session_data['uploaded_chunks'],
            'total_chunks': session_data['total_chunks'],
            'progress': (session_data['uploaded_chunks'] / session_data['total_chunks']) * 100,
            'filename': session_data['filename']
        }

# Global instance
pc_excel_optimizer = PCExcelUploadOptimizer()
