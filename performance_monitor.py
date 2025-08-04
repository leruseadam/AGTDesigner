#!/usr/bin/env python3
"""
Performance monitoring script to identify bottlenecks in app startup
"""

import time
import logging
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

@timing_decorator("Import excel_processor")
def import_excel_processor():
    """Time the import of excel_processor."""
    from src.core.data.excel_processor import ExcelProcessor
    return ExcelProcessor

@timing_decorator("Import product_database")
def import_product_database():
    """Time the import of product_database."""
    from src.core.data.product_database import ProductDatabase
    return ProductDatabase

@timing_decorator("Create ExcelProcessor instance")
def create_excel_processor():
    """Time the creation of ExcelProcessor instance."""
    from src.core.data.excel_processor import ExcelProcessor
    return ExcelProcessor()

@timing_decorator("Create ProductDatabase instance")
def create_product_database():
    """Time the creation of ProductDatabase instance."""
    from src.core.data.product_database import ProductDatabase
    return ProductDatabase()

@timing_decorator("Load default file")
def load_default_file():
    """Time loading the default Excel file."""
    from src.core.data.excel_processor import get_default_upload_file, ExcelProcessor
    
    excel_processor = ExcelProcessor()
    default_file = get_default_upload_file()
    if default_file:
        return excel_processor.load_file(default_file)
    return False

@timing_decorator("Import template_processor")
def import_template_processor():
    """Time the import of template_processor."""
    from src.core.generation.template_processor import TemplateProcessor
    return TemplateProcessor

@timing_decorator("Import all core modules")
def import_all_core_modules():
    """Time importing all core modules."""
    modules = [
        "src.core.data.excel_processor",
        "src.core.data.product_database", 
        "src.core.generation.template_processor",
        "src.core.generation.docx_formatting",
        "src.core.generation.font_sizing",
        "src.core.generation.text_processing",
        "src.core.formatting.markers"
    ]
    
    for module in modules:
        __import__(module)

def main():
    """Main performance monitoring function."""
    print("🚀 Starting performance monitoring...")
    print("=" * 50)
    
    # Test module imports
    print("\n📦 Testing module imports:")
    import_excel_processor()
    import_product_database()
    import_template_processor()
    
    print("\n🔧 Testing instance creation:")
    create_excel_processor()
    create_product_database()
    
    print("\n📁 Testing file loading:")
    load_default_file()
    
    print("\n📚 Testing all core modules:")
    import_all_core_modules()
    
    print("\n" + "=" * 50)
    print("✅ Performance monitoring complete!")

if __name__ == "__main__":
    main()
