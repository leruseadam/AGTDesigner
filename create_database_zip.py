#!/usr/bin/env python3
"""
Script to create a zip archive of database files for uploading to PythonAnywhere
"""
import zipfile
import os
from pathlib import Path
from datetime import datetime

def create_database_zip():
    """Create a zip file of all database-related files"""
    
    # Define the base directory
    base_dir = Path(__file__).parent
    uploads_dir = base_dir / "uploads"
    
    # Create timestamp for the zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"database_backup_{timestamp}.zip"
    zip_path = base_dir / zip_filename
    
    # Files and directories to include
    files_to_zip = []
    
    # Add all .db, .db-shm, .db-wal files
    for ext in ['*.db', '*.db-shm', '*.db-wal']:
        files_to_zip.extend(uploads_dir.glob(ext))
    
    # Add product_database directory
    product_db_dir = uploads_dir / "product_database"
    if product_db_dir.exists():
        for file in product_db_dir.rglob("*"):
            if file.is_file():
                files_to_zip.append(file)
    
    # Add strain_data directory
    strain_data_dir = uploads_dir / "strain_data"
    if strain_data_dir.exists():
        for file in strain_data_dir.rglob("*"):
            if file.is_file():
                files_to_zip.append(file)
    
    # Create the zip file
    print(f"Creating zip file: {zip_filename}")
    print(f"Files to include:")
    
    total_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            # Calculate relative path from base directory
            rel_path = file_path.relative_to(base_dir)
            file_size = file_path.stat().st_size
            total_size += file_size
            
            print(f"  + {rel_path} ({file_size / 1024 / 1024:.2f} MB)")
            zipf.write(file_path, rel_path)
    
    zip_size = zip_path.stat().st_size
    compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
    
    print(f"\n✓ Zip file created successfully!")
    print(f"  Location: {zip_path}")
    print(f"  Original size: {total_size / 1024 / 1024:.2f} MB")
    print(f"  Compressed size: {zip_size / 1024 / 1024:.2f} MB")
    print(f"  Compression: {compression_ratio:.1f}%")
    
    return zip_path

if __name__ == "__main__":
    try:
        zip_path = create_database_zip()
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("\n1. Upload to PythonAnywhere:")
        print("   a. Go to https://www.pythonanywhere.com")
        print("   b. Navigate to Files tab")
        print("   c. Upload this zip file")
        print("\n2. Extract on PythonAnywhere (in Bash console):")
        print(f"   cd ~/your-project-directory")
        print(f"   unzip {zip_path.name}")
        print("\n3. Verify extraction:")
        print("   ls -lh uploads/")
        print("\n4. Remove zip file (optional):")
        print(f"   rm {zip_path.name}")
        
    except Exception as e:
        print(f"Error creating zip file: {e}")
        raise

