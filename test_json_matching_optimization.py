#!/usr/bin/env python3
"""
Test script to verify JSON matching optimization with strain database integration
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

@timing_decorator("Import modules")
def import_modules():
    """Import required modules."""
    from src.core.data.excel_processor import ExcelProcessor
    from src.core.data.json_matcher import JSONMatcher
    from src.core.data.product_database import ProductDatabase
    return ExcelProcessor, JSONMatcher, ProductDatabase

@timing_decorator("Initialize ExcelProcessor")
def init_excel_processor():
    """Initialize ExcelProcessor with default file."""
    from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
    
    excel_processor = ExcelProcessor()
    default_file = get_default_upload_file()
    if default_file:
        success = excel_processor.load_file(default_file)
        print(f"Excel file loaded: {success}")
        return excel_processor
    return None

@timing_decorator("Test strain database")
def test_strain_database():
    """Test the strain database functionality."""
    from src.core.data.product_database import ProductDatabase
    
    product_db = ProductDatabase()
    
    # Test getting all strains
    all_strains = product_db.get_all_strains()
    print(f"Total strains in database: {len(all_strains)}")
    
    # Test getting strain lineage map
    lineage_map = product_db.get_strain_lineage_map()
    print(f"Strains with lineages: {len(lineage_map)}")
    
    # Show some sample strains
    sample_strains = list(all_strains)[:5]
    print(f"Sample strains: {sample_strains}")
    
    return product_db

@timing_decorator("Test JSONMatcher strain cache")
def test_json_matcher_strain_cache(excel_processor):
    """Test the JSONMatcher strain cache functionality."""
    from src.core.data.json_matcher import JSONMatcher
    
    json_matcher = JSONMatcher(excel_processor)
    
    # Test strain cache building
    json_matcher._build_strain_cache()
    
    # Test finding strains in text
    test_texts = [
        "Blue Dream Flower",
        "OG Kush Pre-Roll",
        "Sour Diesel Concentrate",
        "Unknown Product Name",
        "White Widow - Premium"
    ]
    
    for text in test_texts:
        found_strains = json_matcher._find_strains_in_text(text)
        print(f"'{text}' -> Found strains: {found_strains}")
    
    return json_matcher

@timing_decorator("Test optimized matching")
def test_optimized_matching(json_matcher):
    """Test the optimized matching with strain awareness."""
    
    # Create test JSON items
    test_items = [
        {"product_name": "Blue Dream Flower", "vendor": "Test Vendor"},
        {"product_name": "OG Kush Pre-Roll", "vendor": "Test Vendor"},
        {"product_name": "Unknown Product", "vendor": "Test Vendor"},
        {"product_name": "Sour Diesel Concentrate", "vendor": "Test Vendor"}
    ]
    
    # Create test cache items
    test_cache_items = [
        {
            "idx": "1",
            "original_name": "Blue Dream - Premium Flower",
            "norm": "blue dream premium flower",
            "key_terms": {"blue", "dream", "premium", "flower"},
            "vendor": "test vendor"
        },
        {
            "idx": "2", 
            "original_name": "OG Kush Pre-Roll",
            "norm": "og kush pre roll",
            "key_terms": {"og", "kush", "pre", "roll"},
            "vendor": "test vendor"
        }
    ]
    
    print("\nTesting optimized matching:")
    for item in test_items:
        best_score = 0.0
        best_match = None
        
        for cache_item in test_cache_items:
            score = json_matcher._calculate_match_score(item, cache_item)
            if score > best_score:
                best_score = score
                best_match = cache_item["original_name"]
        
        print(f"'{item['product_name']}' -> Best match: '{best_match}' (score: {best_score:.3f})")

def main():
    """Main test function."""
    print("🧪 Testing JSON matching optimization with strain database...")
    print("=" * 60)
    
    # Import modules
    print("\n📦 Importing modules:")
    import_modules()
    
    # Test strain database
    print("\n🗄️  Testing strain database:")
    product_db = test_strain_database()
    
    # Initialize ExcelProcessor
    print("\n📊 Initializing ExcelProcessor:")
    excel_processor = init_excel_processor()
    if not excel_processor:
        print("❌ Failed to initialize ExcelProcessor")
        return
    
    # Test JSONMatcher strain cache
    print("\n🔍 Testing JSONMatcher strain cache:")
    json_matcher = test_json_matcher_strain_cache(excel_processor)
    
    # Test optimized matching
    print("\n🎯 Testing optimized matching:")
    test_optimized_matching(json_matcher)
    
    print("\n" + "=" * 60)
    print("✅ JSON matching optimization test complete!")
    print("\n💡 Expected improvements:")
    print("   - Strain-aware matching for better accuracy")
    print("   - Faster lineage assignment using database")
    print("   - Better fallback tag creation with strain info")

if __name__ == "__main__":
    main() 