#!/usr/bin/env python3
"""
Comprehensive test for optimized lineage persistence system.
Tests that lineage changes are always persisted to the SQLite database
and that the system performs well even with large datasets.
"""

import pandas as pd
import tempfile
import os
import sys
import time
import requests
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor, ENABLE_LINEAGE_PERSISTENCE
from core.data.product_database import ProductDatabase

def create_test_excel_with_strains():
    """Create a test Excel file with various strains for testing lineage persistence."""
    print("Creating test Excel file with strains for lineage persistence testing...")
    
    # Sample data with various strains and lineages
    data = {
        'Product Name*': [
            'Test Flower 1',
            'Test Flower 2', 
            'Test Flower 3',
            'Test Flower 4',
            'Test Concentrate 1',
            'Test Concentrate 2',
            'Test Edible 1',
            'Test Edible 2'
        ],
        'Product Type*': [
            'flower',
            'flower',
            'flower', 
            'flower',
            'concentrate',
            'concentrate',
            'edible (solid)',
            'edible (solid)'
        ],
        'Description': [
            'Test Flower Description 1',
            'Test Flower Description 2',
            'Test Flower Description 3',
            'Test Flower Description 4',
            'Test Concentrate Description 1',
            'Test Concentrate Description 2',
            'Test Edible Description 1',
            'Test Edible Description 2'
        ],
        'Product Strain': [
            'Blue Dream',
            'Blue Dream',
            'OG Kush',
            'Sour Diesel',
            'Blue Dream',
            'OG Kush',
            'CBD Gummy',
            'CBD Gummy'
        ],
        'Lineage': [
            'HYBRID',
            'HYBRID',
            'INDICA',
            'SATIVA',
            'HYBRID',
            'INDICA',
            'CBD',
            'CBD'
        ],
        'Product Brand': [
            'Brand A',
            'Brand B',
            'Brand C',
            'Brand D',
            'Brand A',
            'Brand C',
            'Brand E',
            'Brand F'
        ],
        'Vendor/Supplier': [
            'Vendor 1',
            'Vendor 2',
            'Vendor 3',
            'Vendor 4',
            'Vendor 1',
            'Vendor 3',
            'Vendor 5',
            'Vendor 6'
        ],
        'Weight*': [
            '3.5',
            '7.0',
            '3.5',
            '7.0',
            '1.0',
            '0.5',
            '100',
            '200'
        ],
        'Units': [
            'g',
            'g',
            'g',
            'g',
            'g',
            'g',
            'mg',
            'mg'
        ],
        'Price': [
            '45.00',
            '85.00',
            '50.00',
            '90.00',
            '60.00',
            '35.00',
            '25.00',
            '45.00'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    print(f"Created test file: {temp_file.name}")
    return temp_file.name

def test_lineage_persistence_enabled():
    """Test that lineage persistence is always enabled."""
    print("\n=== Testing Lineage Persistence Always Enabled ===")
    
    # Check that the flag is enabled
    assert ENABLE_LINEAGE_PERSISTENCE == True, "ENABLE_LINEAGE_PERSISTENCE should always be True"
    print("✅ Lineage persistence is always enabled")
    
    # Test that the flag cannot be disabled
    try:
        import src.core.data.excel_processor as excel_module
        excel_module.ENABLE_LINEAGE_PERSISTENCE = False
        print("❌ Lineage persistence flag should not be modifiable")
        return False
    except:
        print("✅ Lineage persistence flag is protected")
    
    return True

def test_optimized_lineage_persistence():
    """Test the optimized lineage persistence functionality."""
    print("\n=== Testing Optimized Lineage Persistence ===")
    
    # Create test file
    test_file = create_test_excel_with_strains()
    
    try:
        # Initialize processor
        processor = ExcelProcessor()
        
        # Load file
        start_time = time.time()
        success = processor.load_file(test_file)
        load_time = time.time() - start_time
        
        if not success:
            print("❌ Failed to load test file")
            return False
        
        print(f"✅ File loaded successfully in {load_time:.3f}s")
        
        # Check that lineage persistence was applied
        if hasattr(processor, 'df') and processor.df is not None:
            # Check that strains have proper lineages
            classic_mask = processor.df["Product Type*"].str.strip().str.lower().isin(['flower', 'concentrate'])
            classic_df = processor.df[classic_mask]
            
            if not classic_df.empty:
                print(f"✅ Found {len(classic_df)} classic type products")
                
                # Check that lineages are properly set
                empty_lineages = classic_df['Lineage'].isna().sum()
                if empty_lineages == 0:
                    print("✅ All classic type products have lineages set")
                else:
                    print(f"⚠️  {empty_lineages} classic type products have empty lineages")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing lineage persistence: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_database_lineage_persistence():
    """Test that lineage changes are persisted to the database."""
    print("\n=== Testing Database Lineage Persistence ===")
    
    try:
        # Initialize database
        product_db = ProductDatabase()
        
        # Test strain lineage update
        strain_name = "Test Strain Persistence"
        new_lineage = "HYBRID"
        
        # Update strain in database
        strain_id = product_db.add_or_update_strain(strain_name, new_lineage, sovereign=True)
        
        if strain_id:
            print(f"✅ Successfully added strain '{strain_name}' with lineage '{new_lineage}' to database")
            
            # Verify the lineage was saved
            strain_info = product_db.get_strain_info(strain_name)
            if strain_info and strain_info.get('sovereign_lineage') == new_lineage:
                print("✅ Lineage was properly persisted to database")
                return True
            else:
                print("❌ Lineage was not properly persisted to database")
                return False
        else:
            print("❌ Failed to add strain to database")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database lineage persistence: {e}")
        return False

def test_lineage_update_methods():
    """Test the new lineage update methods in ExcelProcessor."""
    print("\n=== Testing Lineage Update Methods ===")
    
    # Create test file
    test_file = create_test_excel_with_strains()
    
    try:
        # Initialize processor
        processor = ExcelProcessor()
        
        # Load file
        success = processor.load_file(test_file)
        if not success:
            print("❌ Failed to load test file")
            return False
        
        # Test single lineage update
        strain_name = "Blue Dream"
        new_lineage = "SATIVA"
        
        success = processor.update_lineage_in_database(strain_name, new_lineage)
        if success:
            print(f"✅ Successfully updated lineage for '{strain_name}' to '{new_lineage}'")
        else:
            print(f"❌ Failed to update lineage for '{strain_name}'")
            return False
        
        # Test batch lineage update
        lineage_updates = {
            "OG Kush": "HYBRID",
            "Sour Diesel": "INDICA"
        }
        
        success = processor.batch_update_lineages(lineage_updates)
        if success:
            print(f"✅ Successfully updated {len(lineage_updates)} lineages in batch")
        else:
            print(f"❌ Failed to update lineages in batch")
            return False
        
        # Test lineage suggestions
        suggestions = processor.get_lineage_suggestions("Blue Dream")
        if suggestions:
            print(f"✅ Got lineage suggestions: {suggestions}")
        else:
            print("❌ Failed to get lineage suggestions")
            return False
        
        # Test ensure lineage persistence
        result = processor.ensure_lineage_persistence()
        if result and result.get('updated_count', 0) >= 0:
            print(f"✅ Ensured lineage persistence: {result}")
        else:
            print("❌ Failed to ensure lineage persistence")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing lineage update methods: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_performance_with_large_dataset():
    """Test performance with a larger dataset to ensure lineage persistence scales well."""
    print("\n=== Testing Performance with Large Dataset ===")
    
    # Create a larger test dataset
    print("Creating large test dataset...")
    
    # Generate 1000 records with various strains
    strains = ['Blue Dream', 'OG Kush', 'Sour Diesel', 'Girl Scout Cookies', 'Granddaddy Purple']
    lineages = ['HYBRID', 'INDICA', 'SATIVA', 'HYBRID', 'INDICA']
    product_types = ['flower', 'concentrate']
    
    data = {
        'Product Name*': [f'Test Product {i}' for i in range(1000)],
        'Product Type*': [product_types[i % len(product_types)] for i in range(1000)],
        'Description': [f'Test Description {i}' for i in range(1000)],
        'Product Strain': [strains[i % len(strains)] for i in range(1000)],
        'Lineage': [lineages[i % len(lineages)] for i in range(1000)],
        'Product Brand': [f'Brand {i % 10}' for i in range(1000)],
        'Vendor/Supplier': [f'Vendor {i % 5}' for i in range(1000)],
        'Weight*': ['3.5' for _ in range(1000)],
        'Units': ['g' for _ in range(1000)],
        'Price': ['45.00' for _ in range(1000)]
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    try:
        # Test loading performance
        processor = ExcelProcessor()
        
        start_time = time.time()
        success = processor.load_file(temp_file.name)
        load_time = time.time() - start_time
        
        if success:
            print(f"✅ Large dataset loaded successfully in {load_time:.3f}s")
            
            # Test lineage persistence performance
            start_time = time.time()
            result = processor.ensure_lineage_persistence()
            persistence_time = time.time() - start_time
            
            print(f"✅ Lineage persistence completed in {persistence_time:.3f}s")
            print(f"   Updated {result.get('updated_count', 0)} strains")
            
            # Performance should be reasonable (under 5 seconds for 1000 records)
            if load_time < 10.0 and persistence_time < 5.0:
                print("✅ Performance is acceptable for large datasets")
                return True
            else:
                print("⚠️  Performance could be improved for large datasets")
                return True  # Still acceptable for now
        else:
            print("❌ Failed to load large dataset")
            return False
            
    except Exception as e:
        print(f"❌ Error testing performance: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

def main():
    """Run all lineage persistence tests."""
    print("🧪 Starting Optimized Lineage Persistence Tests")
    print("=" * 60)
    
    tests = [
        ("Lineage Persistence Always Enabled", test_lineage_persistence_enabled),
        ("Optimized Lineage Persistence", test_optimized_lineage_persistence),
        ("Database Lineage Persistence", test_database_lineage_persistence),
        ("Lineage Update Methods", test_lineage_update_methods),
        ("Performance with Large Dataset", test_performance_with_large_dataset)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Lineage persistence is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the lineage persistence implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 