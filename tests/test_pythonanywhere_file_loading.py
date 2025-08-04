#!/usr/bin/env python3
"""
Test script for PythonAnywhere Excel file loading issues.
This script helps diagnose and fix common problems with file loading on PythonAnywhere.
"""

import os
import sys
import logging
import traceback
import time
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pythonanywhere_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_environment():
    """Test the PythonAnywhere environment."""
    logger.info("=== Testing PythonAnywhere Environment ===")
    
    # Check if we're on PythonAnywhere
    pythonanywhere_indicators = [
        'PYTHONANYWHERE_SITE' in os.environ,
        'PYTHONANYWHERE_DOMAIN' in os.environ,
        os.path.exists('/var/log/pythonanywhere'),
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    ]
    
    is_pythonanywhere = any(pythonanywhere_indicators)
    logger.info(f"PythonAnywhere detected: {is_pythonanywhere}")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        logger.info(f"Total memory: {memory.total / (1024**3):.2f} GB")
        logger.info(f"Available memory: {memory.available / (1024**3):.2f} GB")
        logger.info(f"Memory usage: {memory.percent:.1f}%")
    except ImportError:
        logger.warning("psutil not available for memory monitoring")
    
    # Check disk space
    try:
        disk = psutil.disk_usage('/')
        logger.info(f"Disk space: {disk.free / (1024**3):.2f} GB free")
    except:
        logger.warning("Could not check disk space")
    
    return is_pythonanywhere

def test_file_paths():
    """Test file path accessibility."""
    logger.info("=== Testing File Paths ===")
    
    paths_to_test = [
        os.getcwd(),
        os.path.join(os.getcwd(), 'uploads'),
        os.path.expanduser('~'),
        os.path.join(os.path.expanduser('~'), 'Downloads'),
    ]
    
    for path in paths_to_test:
        exists = os.path.exists(path)
        readable = os.access(path, os.R_OK) if exists else False
        writable = os.access(path, os.W_OK) if exists else False
        logger.info(f"Path: {path}")
        logger.info(f"  Exists: {exists}")
        logger.info(f"  Readable: {readable}")
        logger.info(f"  Writable: {writable}")
        
        if exists and readable:
            try:
                files = os.listdir(path)
                logger.info(f"  Files: {len(files)} items")
                # Show first few files
                for file in files[:5]:
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        logger.info(f"    {file}: {size} bytes")
            except Exception as e:
                logger.error(f"  Error listing directory: {e}")

def test_excel_libraries():
    """Test Excel library availability and functionality."""
    logger.info("=== Testing Excel Libraries ===")
    
    libraries = ['pandas', 'openpyxl', 'xlrd']
    
    for lib in libraries:
        try:
            module = __import__(lib)
            version = getattr(module, '__version__', 'unknown')
            logger.info(f"{lib}: {version} - OK")
        except ImportError as e:
            logger.error(f"{lib}: Not available - {e}")
    
    # Test pandas Excel reading
    try:
        import pandas as pd
        logger.info(f"Pandas version: {pd.__version__}")
        
        # Test if pandas can read Excel files
        logger.info("Testing pandas Excel reading capability...")
        
        # Create a small test Excel file
        test_data = {
            'Product Name*': ['Test Product 1', 'Test Product 2'],
            'Product Type*': ['Flower', 'Concentrate'],
            'Weight*': [3.5, 1.0],
            'Units': ['g', 'g']
        }
        
        test_df = pd.DataFrame(test_data)
        test_file = 'test_excel_reading.xlsx'
        
        # Write test file
        test_df.to_excel(test_file, index=False, engine='openpyxl')
        logger.info(f"Created test file: {test_file}")
        
        # Read test file with different engines
        engines = ['openpyxl', 'xlrd']
        for engine in engines:
            try:
                df = pd.read_excel(test_file, engine=engine)
                logger.info(f"Successfully read with {engine}: {len(df)} rows")
            except Exception as e:
                logger.error(f"Failed to read with {engine}: {e}")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            
    except Exception as e:
        logger.error(f"Error testing pandas Excel functionality: {e}")

def test_file_loading():
    """Test actual file loading with the ExcelProcessor."""
    logger.info("=== Testing File Loading ===")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        
        # Get default file
        default_file = get_default_upload_file()
        if default_file:
            logger.info(f"Found default file: {default_file}")
            
            # Test file properties
            if os.path.exists(default_file):
                size = os.path.getsize(default_file)
                mtime = os.path.getmtime(default_file)
                logger.info(f"File size: {size} bytes ({size / (1024*1024):.2f} MB)")
                logger.info(f"Last modified: {time.ctime(mtime)}")
                
                # Test loading with ExcelProcessor
                excel_processor = ExcelProcessor()
                
                start_time = time.time()
                success = excel_processor.load_file(default_file)
                load_time = time.time() - start_time
                
                logger.info(f"Load success: {success}")
                logger.info(f"Load time: {load_time:.2f} seconds")
                
                if success and excel_processor.df is not None:
                    logger.info(f"Loaded {len(excel_processor.df)} rows")
                    logger.info(f"Columns: {list(excel_processor.df.columns)}")
                    
                    # Test memory usage
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_info = process.memory_info()
                        logger.info(f"Memory usage after load: {memory_info.rss / (1024*1024):.2f} MB")
                    except ImportError:
                        pass
                else:
                    logger.error("File loading failed")
            else:
                logger.error(f"Default file does not exist: {default_file}")
        else:
            logger.warning("No default file found")
            
            # Look for any Excel files in common locations
            search_paths = [
                os.path.join(os.getcwd(), 'uploads'),
                os.path.join(os.path.expanduser('~'), 'Downloads'),
                os.getcwd()
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    logger.info(f"Searching for Excel files in: {search_path}")
                    try:
                        for file in os.listdir(search_path):
                            if file.lower().endswith(('.xlsx', '.xls')):
                                file_path = os.path.join(search_path, file)
                                size = os.path.getsize(file_path)
                                logger.info(f"Found Excel file: {file} ({size} bytes)")
                    except Exception as e:
                        logger.error(f"Error searching {search_path}: {e}")
                        
    except Exception as e:
        logger.error(f"Error testing file loading: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def test_upload_directory():
    """Test upload directory functionality."""
    logger.info("=== Testing Upload Directory ===")
    
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir, exist_ok=True)
            logger.info(f"Created upload directory: {upload_dir}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            return
    
    # Test permissions
    readable = os.access(upload_dir, os.R_OK)
    writable = os.access(upload_dir, os.W_OK)
    logger.info(f"Upload directory permissions - Readable: {readable}, Writable: {writable}")
    
    # List existing files
    try:
        files = os.listdir(upload_dir)
        logger.info(f"Upload directory contains {len(files)} files")
        for file in files:
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                logger.info(f"  {file}: {size} bytes")
    except Exception as e:
        logger.error(f"Error listing upload directory: {e}")

def generate_test_excel():
    """Generate a test Excel file for testing."""
    logger.info("=== Generating Test Excel File ===")
    
    try:
        import pandas as pd
        
        # Create test data similar to "A Greener Today" format
        test_data = {
            'Product Name*': [
                'Blue Dream - 22% THC',
                'OG Kush - 18% THC',
                'CBD Tincture - 500mg CBD',
                'Pre-Roll - 1g - 20% THC',
                'Concentrate - 1g - 85% THC'
            ],
            'Product Type*': [
                'Flower',
                'Flower', 
                'Tincture',
                'Pre-Roll',
                'Concentrate'
            ],
            'Weight*': [3.5, 3.5, 30, 1, 1],
            'Weight Unit* (grams/gm or ounces/oz)': ['g', 'g', 'ml', 'g', 'g'],
            'Lineage': ['HYBRID', 'INDICA', 'CBD', 'HYBRID', 'HYBRID'],
            'Product Brand': ['Test Brand', 'Test Brand', 'Test Brand', 'Test Brand', 'Test Brand'],
            'Vendor': ['Test Vendor', 'Test Vendor', 'Test Vendor', 'Test Vendor', 'Test Vendor'],
            'Product Strain': ['Blue Dream', 'OG Kush', 'CBD Blend', 'Mixed', 'Mixed'],
            'Price* (Tier Name for Bulk)': ['$45', '$50', '$35', '$15', '$60'],
            'Quantity*': [10, 10, 5, 20, 5]
        }
        
        df = pd.DataFrame(test_data)
        test_file = os.path.join(os.getcwd(), 'uploads', 'Test_A_Greener_Today.xlsx')
        
        # Ensure uploads directory exists
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        # Write test file
        df.to_excel(test_file, index=False, engine='openpyxl')
        logger.info(f"Generated test file: {test_file}")
        logger.info(f"File size: {os.path.getsize(test_file)} bytes")
        
        return test_file
        
    except Exception as e:
        logger.error(f"Error generating test Excel file: {e}")
        return None

def main():
    """Run all tests."""
    logger.info("Starting PythonAnywhere file loading tests...")
    
    # Run tests
    test_environment()
    test_file_paths()
    test_excel_libraries()
    test_upload_directory()
    
    # Generate test file if no files found
    test_file = generate_test_excel()
    
    # Test file loading
    test_file_loading()
    
    logger.info("=== Test Summary ===")
    logger.info("Tests completed. Check the log file 'pythonanywhere_test.log' for detailed results.")
    
    if test_file and os.path.exists(test_file):
        logger.info(f"Test file available: {test_file}")
        logger.info("You can use this file to test the application.")

if __name__ == "__main__":
    main() 