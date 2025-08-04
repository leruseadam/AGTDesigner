#!/usr/bin/env python3
"""
Diagnostic script to check PythonAnywhere default file loading
"""

import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_pythonanywhere_environment():
    """Check if we're running on PythonAnywhere and get environment info."""
    print("=== PythonAnywhere Environment Check ===")
    
    # Check for PythonAnywhere indicators
    pythonanywhere_indicators = [
        'PYTHONANYWHERE_SITE' in os.environ,
        'PYTHONANYWHERE_DOMAIN' in os.environ,
        os.path.exists('/var/log/pythonanywhere'),
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', ''),
        os.path.exists("/home/adamcordova"),
        "pythonanywhere" in os.getcwd().lower()
    ]
    
    is_pythonanywhere = any(pythonanywhere_indicators)
    print(f"Running on PythonAnywhere: {is_pythonanywhere}")
    
    # Environment variables
    print(f"Current working directory: {os.getcwd()}")
    print(f"User home directory: {os.path.expanduser('~')}")
    print(f"PYTHONANYWHERE_SITE: {os.environ.get('PYTHONANYWHERE_SITE', 'Not set')}")
    print(f"PYTHONANYWHERE_DOMAIN: {os.environ.get('PYTHONANYWHERE_DOMAIN', 'Not set')}")
    print(f"HTTP_HOST: {os.environ.get('HTTP_HOST', 'Not set')}")
    
    return is_pythonanywhere

def check_file_locations():
    """Check all possible file locations for AGT files."""
    print("\n=== File Location Check ===")
    
    current_dir = os.getcwd()
    home_dir = os.path.expanduser('~')
    
    # Define all possible search locations
    search_locations = [
        os.path.join(current_dir, "uploads"),
        os.path.join(home_dir, "Downloads"),
        "/home/adamcordova/uploads",
        "/home/adamcordova/AGTDesigner/uploads",
        "/home/adamcordova/AGTDesigner/AGTDesigner/uploads",
        "/home/adamcordova/Downloads",
        "/home/adamcordova/AGTDesigner",
        "/home/adamcordova/AGTDesigner/AGTDesigner",
    ]
    
    agt_files = []
    
    for location in search_locations:
        print(f"\nChecking location: {location}")
        if os.path.exists(location):
            print(f"  ✓ Location exists")
            try:
                files = os.listdir(location)
                print(f"  Files in directory: {len(files)}")
                
                # Look for AGT files
                agt_files_in_location = []
                for filename in files:
                    if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                        file_path = os.path.join(location, filename)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            file_size = os.path.getsize(file_path)
                            agt_files_in_location.append((file_path, filename, mod_time, file_size))
                            print(f"    ✓ Found AGT file: {filename}")
                            print(f"      Size: {file_size:,} bytes")
                            print(f"      Modified: {mod_time}")
                
                agt_files.extend(agt_files_in_location)
                
            except Exception as e:
                print(f"  ✗ Error reading directory: {e}")
        else:
            print(f"  ✗ Location does not exist")
    
    return agt_files

def check_file_permissions():
    """Check file permissions for found AGT files."""
    print("\n=== File Permissions Check ===")
    
    agt_files = check_file_locations()
    
    if not agt_files:
        print("No AGT files found!")
        return []
    
    print(f"\nFound {len(agt_files)} AGT files:")
    
    for file_path, filename, mod_time, file_size in agt_files:
        print(f"\nFile: {filename}")
        print(f"  Path: {file_path}")
        print(f"  Size: {file_size:,} bytes")
        print(f"  Modified: {mod_time}")
        
        # Check permissions
        try:
            stat_info = os.stat(file_path)
            print(f"  Readable: {os.access(file_path, os.R_OK)}")
            print(f"  Writable: {os.access(file_path, os.W_OK)}")
            print(f"  Executable: {os.access(file_path, os.X_OK)}")
            print(f"  Owner: {stat_info.st_uid}")
            print(f"  Group: {stat_info.st_gid}")
        except Exception as e:
            print(f"  ✗ Error checking permissions: {e}")
    
    return agt_files

def test_file_loading():
    """Test loading the most recent AGT file."""
    print("\n=== File Loading Test ===")
    
    agt_files = check_file_permissions()
    
    if not agt_files:
        print("No AGT files found to test!")
        return
    
    # Sort by modification time (most recent first)
    agt_files.sort(key=lambda x: x[2], reverse=True)
    most_recent_file = agt_files[0]
    
    print(f"\nTesting loading of most recent file: {most_recent_file[1]}")
    
    try:
        # Try to import and test ExcelProcessor
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        from core.data.excel_processor import ExcelProcessor
        
        processor = ExcelProcessor()
        success = processor.load_file(most_recent_file[0])
        
        if success:
            print(f"✓ File loaded successfully!")
            print(f"  DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
            if processor.df is not None:
                print(f"  Columns: {list(processor.df.columns)}")
                print(f"  Sample data:")
                print(processor.df.head(3))
        else:
            print(f"✗ File loading failed!")
            
    except Exception as e:
        print(f"✗ Error testing file loading: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main diagnostic function."""
    print("PythonAnywhere Default File Loading Diagnostic")
    print("=" * 50)
    
    # Check environment
    is_pythonanywhere = check_pythonanywhere_environment()
    
    # Check file locations and permissions
    agt_files = check_file_permissions()
    
    # Test file loading
    test_file_loading()
    
    # Summary
    print("\n=== Summary ===")
    print(f"Running on PythonAnywhere: {is_pythonanywhere}")
    print(f"AGT files found: {len(agt_files)}")
    
    if agt_files:
        most_recent = max(agt_files, key=lambda x: x[2])
        print(f"Most recent file: {most_recent[1]}")
        print(f"Most recent file path: {most_recent[0]}")
    else:
        print("No AGT files found in any location!")

if __name__ == "__main__":
    main() 