#!/usr/bin/env python3
"""
Script to run on PythonAnywhere to extract the database zip file
Upload this script along with your zip file to PythonAnywhere
"""
import zipfile
import os
import sys
from pathlib import Path

def unzip_database(zip_filename=None):
    """Extract database zip file on PythonAnywhere"""
    
    # Get the current directory
    current_dir = Path.cwd()
    
    # Find zip file if not specified
    if not zip_filename:
        zip_files = list(current_dir.glob("database_backup_*.zip"))
        if not zip_files:
            print("Error: No database_backup_*.zip file found in current directory")
            print("Available files:")
            for f in current_dir.iterdir():
                print(f"  - {f.name}")
            sys.exit(1)
        
        # Use the most recent one
        zip_filename = sorted(zip_files)[-1].name
    
    zip_path = current_dir / zip_filename
    
    if not zip_path.exists():
        print(f"Error: {zip_filename} not found!")
        sys.exit(1)
    
    print(f"Extracting: {zip_filename}")
    print(f"Location: {zip_path}")
    print()
    
    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # List contents
        print("Contents:")
        for info in zipf.infolist():
            print(f"  {info.filename} ({info.file_size / 1024 / 1024:.2f} MB)")
        
        print("\nExtracting...")
        zipf.extractall(current_dir)
    
    print("\n✓ Extraction complete!")
    
    # Verify the uploads directory
    uploads_dir = current_dir / "uploads"
    if uploads_dir.exists():
        print(f"\nVerifying uploads directory:")
        print(f"  Location: {uploads_dir}")
        
        # Count database files
        db_files = list(uploads_dir.glob("*.db"))
        print(f"  Database files: {len(db_files)}")
        for db in db_files:
            size = db.stat().st_size / 1024 / 1024
            print(f"    - {db.name} ({size:.2f} MB)")
    
    print("\n" + "="*60)
    print("DATABASE RESTORED SUCCESSFULLY!")
    print("="*60)
    print(f"\nYou can now delete the zip file if desired:")
    print(f"  rm {zip_filename}")

if __name__ == "__main__":
    # Get zip filename from command line if provided
    zip_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        unzip_database(zip_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

