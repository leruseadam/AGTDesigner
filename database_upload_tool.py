#!/usr/bin/env python3
"""
Database Upload Tool - Alternative approach
Compresses and uploads database in chunks to bypass file size restrictions
"""

import sqlite3
import requests
import gzip
import base64
import os
import sys
import json
from typing import Dict, List, Any
import time

class DatabaseUploader:
    def __init__(self, local_db_path: str, web_base_url: str):
        self.local_db_path = local_db_path
        self.web_base_url = web_base_url.rstrip('/')
        self.session = requests.Session()
        self.chunk_size = 1024 * 1024  # 1MB chunks
        
    def compress_database(self) -> str:
        """Compress the database file"""
        print(f"Compressing database {self.local_db_path}...")
        
        with open(self.local_db_path, 'rb') as f_in:
            with gzip.open('database_compressed.db.gz', 'wb') as f_out:
                f_out.write(f_in.read())
        
        compressed_size = os.path.getsize('database_compressed.db.gz')
        original_size = os.path.getsize(self.local_db_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Compressed: {original_size:,} bytes -> {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
        return 'database_compressed.db.gz'
    
    def split_file(self, file_path: str) -> List[str]:
        """Split compressed file into chunks"""
        print(f"Splitting {file_path} into chunks...")
        
        chunk_files = []
        with open(file_path, 'rb') as f:
            chunk_num = 0
            while True:
                chunk_data = f.read(self.chunk_size)
                if not chunk_data:
                    break
                
                chunk_file = f"database_chunk_{chunk_num}.gz"
                with open(chunk_file, 'wb') as chunk_f:
                    chunk_f.write(chunk_data)
                
                chunk_files.append(chunk_file)
                chunk_num += 1
        
        print(f"Created {len(chunk_files)} chunks")
        return chunk_files
    
    def upload_chunk(self, chunk_file: str, chunk_num: int, total_chunks: int) -> bool:
        """Upload a single chunk"""
        try:
            with open(chunk_file, 'rb') as f:
                chunk_data = f.read()
            
            # Encode chunk as base64 for JSON transport
            encoded_data = base64.b64encode(chunk_data).decode('utf-8')
            
            payload = {
                'chunk_data': encoded_data,
                'chunk_num': chunk_num,
                'total_chunks': total_chunks,
                'is_last': chunk_num == total_chunks - 1
            }
            
            print(f"Uploading chunk {chunk_num + 1}/{total_chunks}...")
            response = self.session.post(
                f"{self.web_base_url}/api/upload-database-chunk",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                print(f"✓ Chunk {chunk_num + 1} uploaded successfully")
                return True
            else:
                print(f"✗ Error uploading chunk {chunk_num + 1}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error uploading chunk {chunk_num + 1}: {e}")
            return False
    
    def upload_database(self) -> bool:
        """Upload the complete database"""
        print("Starting database upload...")
        
        # Compress database
        compressed_file = self.compress_database()
        
        # Split into chunks
        chunk_files = self.split_file(compressed_file)
        
        # Upload chunks
        success_count = 0
        for i, chunk_file in enumerate(chunk_files):
            if self.upload_chunk(chunk_file, i, len(chunk_files)):
                success_count += 1
            time.sleep(0.5)  # Small delay between chunks
        
        # Cleanup chunk files
        for chunk_file in chunk_files:
            try:
                os.remove(chunk_file)
            except:
                pass
        
        try:
            os.remove(compressed_file)
        except:
            pass
        
        success = success_count == len(chunk_files)
        if success:
            print(f"✓ Database uploaded successfully ({success_count}/{len(chunk_files)} chunks)")
        else:
            print(f"✗ Database upload failed ({success_count}/{len(chunk_files)} chunks succeeded)")
        
        return success
    
    def verify_upload(self) -> bool:
        """Verify the upload was successful"""
        print("Verifying upload...")
        
        try:
            response = self.session.get(f"{self.web_base_url}/api/database-stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"Web database stats: {stats}")
                
                # Check if we have products
                if stats.get('stats', {}).get('total_products', 0) > 0:
                    print("✓ Database upload verified successfully")
                    return True
                else:
                    print("✗ Database appears empty after upload")
                    return False
            else:
                print(f"✗ Error verifying upload: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error verifying upload: {e}")
            return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python database_upload_tool.py <local_db_path> <web_base_url>")
        print("Example: python database_upload_tool.py uploads/product_database.db https://your-app.pythonanywhere.com")
        sys.exit(1)
    
    local_db_path = sys.argv[1]
    web_base_url = sys.argv[2]
    
    if not os.path.exists(local_db_path):
        print(f"Error: Local database file not found: {local_db_path}")
        sys.exit(1)
    
    uploader = DatabaseUploader(local_db_path, web_base_url)
    
    if uploader.upload_database():
        uploader.verify_upload()
    else:
        print("Upload failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
