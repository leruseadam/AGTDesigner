#!/usr/bin/env python3
"""
Simple database test script to verify database functionality.
Run this to test if the database is working properly.
"""

import os
import sys
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database():
    """Test the database functionality."""
    try:
        logger.info("=== DATABASE TEST START ===")
        
        # Test 1: Import ProductDatabase
        logger.info("Testing ProductDatabase import...")
        from src.core.data.product_database import ProductDatabase
        logger.info("✅ ProductDatabase imported successfully")
        
        # Test 2: Create database instance
        logger.info("Testing database creation...")
        db_path = os.path.join(os.getcwd(), 'uploads', 'test_database.db')
        db = ProductDatabase(db_path)
        logger.info(f"✅ Database instance created at: {db_path}")
        
        # Test 3: Initialize database
        logger.info("Testing database initialization...")
        db.init_database()
        logger.info("✅ Database initialized successfully")
        
        # Test 4: Check if database file exists
        logger.info("Testing database file creation...")
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            logger.info(f"✅ Database file created, size: {db_size} bytes")
        else:
            logger.error(f"❌ Database file not created at {db_path}")
            return False
        
        # Test 5: Test basic database operations
        logger.info("Testing basic database operations...")
        
        # Test strain addition
        strain_id = db.add_or_update_strain("Test Strain", "HYBRID")
        logger.info(f"✅ Strain added with ID: {strain_id}")
        
        # Test product addition
        product_data = {
            'ProductName': 'Test Product',
            'Product Type*': 'Flower',
            'Lineage': 'HYBRID',
            'Vendor': 'Test Vendor',
            'Product Brand': 'Test Brand',
            'Description': 'Test Description',
            'Weight*': '1g',
            'Units': 'grams',
            'Price': '10.00',
            'Product Strain': 'Test Strain'
        }
        
        product_id = db.add_or_update_product(product_data)
        logger.info(f"✅ Product added with ID: {product_id}")
        
        # Test 6: Test data retrieval
        logger.info("Testing data retrieval...")
        strain_info = db.get_strain_info("Test Strain")
        if strain_info:
            logger.info(f"✅ Strain info retrieved: {strain_info}")
        else:
            logger.warning("⚠️  Strain info not retrieved")
        
        # Test 7: Test statistics
        logger.info("Testing database statistics...")
        stats = db.get_strain_statistics()
        logger.info(f"✅ Database statistics: {stats}")
        
        # Test 8: Test Excel data storage (with sample data)
        logger.info("Testing Excel data storage...")
        import pandas as pd
        
        # Create sample DataFrame
        sample_data = {
            'Product Name*': ['Sample Product 1', 'Sample Product 2'],
            'Product Type*': ['Flower', 'Concentrate'],
            'Lineage': ['HYBRID', 'INDICA'],
            'Vendor': ['Sample Vendor', 'Sample Vendor'],
            'Product Brand': ['Sample Brand', 'Sample Brand'],
            'Description': ['Sample Description 1', 'Sample Description 2'],
            'Weight*': ['1g', '0.5g'],
            'Units': ['grams', 'grams'],
            'Price': ['15.00', '25.00'],
            'Product Strain': ['Sample Strain 1', 'Sample Strain 2']
        }
        
        df = pd.DataFrame(sample_data)
        storage_result = db.store_excel_data(df, 'test_sample.xlsx')
        logger.info(f"✅ Excel data storage test completed: {storage_result}")
        
        logger.info("=== DATABASE TEST COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🎉 Database test PASSED! The database is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Database test FAILED! There are issues with the database.")
        sys.exit(1)
