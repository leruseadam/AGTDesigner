#!/usr/bin/env python3
"""
Performance test script to measure loading time improvements
"""

import time
import sys
import os
from functools import wraps

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def timing_decorator(func_name=None):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                name = func_name or func.__name__
                if elapsed > 0.1:  # Log slow operations
                    print(f"⏱️  {name}: {elapsed:.3f}s")
                else:
                    print(f"✅ {name}: {elapsed:.3f}s")
        return wrapper
    return decorator

@timing_decorator("Import ExcelProcessor")
def import_excel_processor():
    """Time the import of ExcelProcessor."""
    from src.core.data.excel_processor import ExcelProcessor
    return ExcelProcessor

@timing_decorator("Create ExcelProcessor instance")
def create_excel_processor():
    """Time the creation of ExcelProcessor instance."""
    from src.core.data.excel_processor import ExcelProcessor
    return ExcelProcessor()

@timing_decorator("Load default file (OPTIMIZED)")
def load_default_file_optimized():
    """Time loading the default Excel file with optimizations."""
    from src.core.data.excel_processor import get_default_upload_file, ExcelProcessor
    
    excel_processor = ExcelProcessor()
    default_file = get_default_upload_file()
    if default_file:
        return excel_processor.load_file(default_file)
    return False

def main():
    """Main performance test function."""
    print("🚀 Testing performance optimizations...")
    print("=" * 50)
    
    # Test module imports
    print("\n📦 Testing module imports:")
    import_excel_processor()
    
    print("\n🔧 Testing instance creation:")
    create_excel_processor()
    
    print("\n📁 Testing optimized file loading:")
    load_default_file_optimized()
    
    print("\n" + "=" * 50)
    print("✅ Performance test complete!")
    print("\n💡 Expected improvements:")
    print("   - File loading should be much faster (under 5 seconds)")
    print("   - Strain similarity processing is disabled by default")
    print("   - Memory usage should be optimized")

if __name__ == "__main__":
    main() 