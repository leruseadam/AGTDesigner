#!/usr/bin/env python3
"""
Upload Database in Chunks via Web Interface
Splits the database into smaller chunks and uploads them via web interface
"""

import os
import sys
import requests
import base64
import json
from pathlib import Path
from datetime import datetime

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks

def split_database_file(db_path, chunk_size=CHUNK_SIZE):
    """Split database file into chunks."""
    print(f"Splitting {db_path} into {chunk_size // (1024*1024)}MB chunks...")
    
    chunks = []
    with open(db_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            
            chunk_file = f"database_chunk_{chunk_num}.bin"
            with open(chunk_file, 'wb') as chunk_f:
                chunk_f.write(chunk_data)
            
            chunks.append(chunk_file)
            chunk_num += 1
    
    print(f"Created {len(chunks)} chunks")
    return chunks

def upload_chunk_via_web(chunk_path, chunk_num, total_chunks):
    """Upload a single chunk via web interface."""
    try:
        print(f"Uploading chunk {chunk_num + 1}/{total_chunks}...")
        
        with open(chunk_path, 'rb') as f:
            files = {'file': (chunk_path.name, f, 'application/octet-stream')}
            
            # Use a special endpoint for database chunks
            response = requests.post(
                f"{PYTHONANYWHERE_URL}/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                print(f"✅ Chunk {chunk_num + 1} uploaded successfully!")
                return True
            else:
                print(f"❌ Chunk {chunk_num + 1} upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error uploading chunk {chunk_num + 1}: {e}")
        return False

def upload_database_metadata(chunks_info):
    """Upload metadata about the chunks."""
    try:
        metadata = {
            'type': 'database_chunks',
            'total_chunks': len(chunks_info),
            'chunks': chunks_info,
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{PYTHONANYWHERE_URL}/api/upload-metadata",
            json=metadata,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Database metadata uploaded successfully!")
            return True
        else:
            print(f"❌ Metadata upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading metadata: {e}")
        return False

def check_web_status():
    """Check if the web application is accessible."""
    try:
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/initial-data", timeout=10)
        if response.status_code == 200:
            print("✅ Web application is accessible")
            return True
        else:
            print(f"❌ Web application returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to web application: {e}")
        return False

def cleanup_chunks(chunk_files):
    """Clean up chunk files."""
    print("Cleaning up chunk files...")
    for chunk_file in chunk_files:
        try:
            os.remove(chunk_file)
        except:
            pass
    print("✅ Cleanup completed")

def main():
    """Main function."""
    print("Database Chunk Upload via Web Interface")
    print("=" * 45)
    
    # Check web status
    if not check_web_status():
        print("❌ Cannot connect to the web application. Please check the URL and try again.")
        return
    
    # Find database file
    db_path = Path("product_database.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    file_size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"Database size: {file_size_mb:.1f} MB")
    
    # Split into chunks
    chunk_files = split_database_file(db_path)
    
    # Upload chunks
    success_count = 0
    chunks_info = []
    
    for i, chunk_file in enumerate(chunk_files):
        if upload_chunk_via_web(chunk_file, i, len(chunk_files)):
            success_count += 1
            chunks_info.append({
                'chunk_num': i,
                'filename': chunk_file,
                'size': os.path.getsize(chunk_file)
            })
    
    # Upload metadata
    if success_count == len(chunk_files):
        upload_database_metadata(chunks_info)
        print(f"\n🎉 Database upload completed successfully!")
        print(f"Uploaded {success_count}/{len(chunk_files)} chunks")
        print("The web application should now have the database data.")
    else:
        print(f"\n⚠️  Partial upload: {success_count}/{len(chunk_files)} chunks succeeded")
        print("Some chunks failed to upload. You may need to retry.")
    
    # Cleanup
    cleanup_chunks(chunk_files)

if __name__ == "__main__":
    main()
