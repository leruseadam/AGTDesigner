#!/usr/bin/env python3
"""
Test database compression to see if it's small enough for upload
"""

import sqlite3
import gzip
import os
import sys

def test_compression(db_path):
    """Test compression ratio of the database"""
    if not os.path.exists(db_path):
        print(f"Error: Database file not found: {db_path}")
        return
    
    # Get original size
    original_size = os.path.getsize(db_path)
    print(f"Original database size: {original_size:,} bytes ({original_size / (1024*1024):.1f} MB)")
    
    # Compress
    compressed_file = 'test_compressed.db.gz'
    with open(db_path, 'rb') as f_in:
        with gzip.open(compressed_file, 'wb') as f_out:
            f_out.write(f_in.read())
    
    compressed_size = os.path.getsize(compressed_file)
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    print(f"Compressed size: {compressed_size:,} bytes ({compressed_size / (1024*1024):.1f} MB)")
    print(f"Compression ratio: {compression_ratio:.1f}% reduction")
    
    # Check if it's small enough for typical upload limits
    if compressed_size < 50 * 1024 * 1024:  # 50MB
        print("✓ Compressed database is small enough for direct upload")
    elif compressed_size < 100 * 1024 * 1024:  # 100MB
        print("⚠ Compressed database might be too large for direct upload")
    else:
        print("✗ Compressed database is too large for direct upload")
    
    # Test chunking
    chunk_size = 10 * 1024 * 1024  # 10MB chunks
    num_chunks = (compressed_size + chunk_size - 1) // chunk_size
    print(f"Would need {num_chunks} chunks of {chunk_size // (1024*1024)}MB each")
    
    # Cleanup
    os.remove(compressed_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_compression.py <database_path>")
        sys.exit(1)
    
    test_compression(sys.argv[1])
