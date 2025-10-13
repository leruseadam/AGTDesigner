#!/usr/bin/env python3
"""
FAST EXCEL UPLOAD - Optimized Excel processing to prevent hanging
"""

import pandas as pd
import os
import time
import logging
from typing import Optional, Dict, Any

class FastExcelProcessor:
    """Ultra-fast Excel processor that prevents hanging during upload"""
    
    def __init__(self):
        self.df = None
        self.processing_status = "idle"
        self.progress = 0
        self.max_rows_per_batch = 1000
        
    def process_excel_fast(self, file_path: str) -> Dict[str, Any]:
        """Process Excel file in chunks to prevent hanging"""
        try:
            logging.info(f"🚀 FAST PROCESSING: Starting {os.path.basename(file_path)}")
            start_time = time.time()
            
            # Step 1: Quick file validation
            if not os.path.exists(file_path):
                return {"success": False, "error": "File not found"}
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {"success": False, "error": "Empty file"}
            
            logging.info(f"📁 File size: {file_size:,} bytes")
            
            # Step 2: Quick preview (first 100 rows)
            try:
                preview_df = pd.read_excel(file_path, nrows=100, engine='openpyxl')
                total_columns = len(preview_df.columns)
                logging.info(f"📊 Preview: {len(preview_df)} rows, {total_columns} columns")
                
                # Check if file has expected structure
                expected_columns = ['Description', 'Product Brand', 'Price', 'Lineage']
                missing_columns = [col for col in expected_columns if col not in preview_df.columns]
                if missing_columns:
                    logging.warning(f"⚠️ Missing columns: {missing_columns}")
                
            except Exception as e:
                logging.error(f"❌ Preview failed: {e}")
                return {"success": False, "error": f"File preview failed: {e}"}
            
            # Step 3: Estimate total rows (without loading full file)
            estimated_rows = self._estimate_row_count(file_path)
            logging.info(f"📈 Estimated rows: {estimated_rows:,}")
            
            # Step 4: Process in chunks if large file
            if estimated_rows > 2000:
                return self._process_large_file_chunked(file_path, estimated_rows)
            else:
                return self._process_small_file_fast(file_path)
                
        except Exception as e:
            logging.error(f"❌ Fast processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _estimate_row_count(self, file_path: str) -> int:
        """Estimate row count without loading full file"""
        try:
            # Read first 1000 rows to get column structure
            sample_df = pd.read_excel(file_path, nrows=1000, engine='openpyxl')
            
            # Estimate based on file size and sample
            file_size = os.path.getsize(file_path)
            sample_size = len(sample_df)
            
            # Rough estimation: assume consistent row size
            estimated_rows = int((file_size / (file_size / sample_size)) * 1.2)  # 20% buffer
            
            return max(sample_size, estimated_rows)
            
        except Exception as e:
            logging.warning(f"Row estimation failed: {e}")
            return 1000  # Default estimate
    
    def _process_small_file_fast(self, file_path: str) -> Dict[str, Any]:
        """Process small files (< 2000 rows) quickly"""
        try:
            logging.info("⚡ Processing small file with full load...")
            
            # Load with optimizations
            df = pd.read_excel(
                file_path, 
                engine='openpyxl',
                dtype=str,  # Read as strings for speed
                na_filter=False,  # Don't convert to NaN
                keep_default_na=False
            )
            
            self.df = df
            processing_time = time.time() - start_time
            
            logging.info(f"✅ Small file processed: {len(df)} rows in {processing_time:.2f}s")
            
            return {
                "success": True,
                "rows_processed": len(df),
                "processing_time": processing_time,
                "method": "full_load"
            }
            
        except Exception as e:
            logging.error(f"❌ Small file processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_large_file_chunked(self, file_path: str, estimated_rows: int) -> Dict[str, Any]:
        """Process large files in chunks to prevent hanging"""
        try:
            logging.info(f"📦 Processing large file in chunks (estimated {estimated_rows:,} rows)...")
            
            chunk_size = self.max_rows_per_batch
            all_chunks = []
            processed_rows = 0
            chunk_count = 0
            
            # Process file in chunks
            for chunk_start in range(0, estimated_rows, chunk_size):
                chunk_count += 1
                logging.info(f"📦 Processing chunk {chunk_count} (rows {chunk_start}-{chunk_start + chunk_size})")
                
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
                        logging.info(f"📦 Chunk {chunk_count} is empty, stopping")
                        break
                    
                    all_chunks.append(chunk_df)
                    processed_rows += len(chunk_df)
                    
                    # Progress update
                    progress = min(100, (processed_rows / estimated_rows) * 100)
                    logging.info(f"📊 Progress: {progress:.1f}% ({processed_rows:,}/{estimated_rows:,} rows)")
                    
                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)
                    
                except Exception as chunk_error:
                    logging.warning(f"⚠️ Chunk {chunk_count} failed: {chunk_error}")
                    continue
            
            # Combine chunks
            if all_chunks:
                logging.info("🔗 Combining chunks...")
                self.df = pd.concat(all_chunks, ignore_index=True)
                
                processing_time = time.time() - start_time
                logging.info(f"✅ Large file processed: {len(self.df)} rows in {processing_time:.2f}s")
                
                return {
                    "success": True,
                    "rows_processed": len(self.df),
                    "processing_time": processing_time,
                    "method": "chunked_processing",
                    "chunks_processed": chunk_count
                }
            else:
                return {"success": False, "error": "No chunks could be processed"}
                
        except Exception as e:
            logging.error(f"❌ Large file processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            "status": self.processing_status,
            "progress": self.progress,
            "has_data": self.df is not None and not self.df.empty,
            "row_count": len(self.df) if self.df is not None else 0
        }

# Usage example
def optimize_excel_upload():
    """Example of how to use the fast Excel processor"""
    
    processor = FastExcelProcessor()
    
    # Process file
    result = processor.process_excel_fast("/path/to/excel/file.xlsx")
    
    if result["success"]:
        print(f"✅ Success: {result['rows_processed']} rows processed in {result['processing_time']:.2f}s")
        print(f"Method: {result['method']}")
    else:
        print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    optimize_excel_upload()
