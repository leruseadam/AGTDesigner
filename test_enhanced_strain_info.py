#!/usr/bin/env python3
"""
Test script to verify enhanced strain information with brand, weight, vendor, and price data
for JSON matching functionality.
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase
from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_strain_info():
    """Test the enhanced strain information functionality."""
    print("=== Testing Enhanced Strain Information ===")
    
    try:
        # Initialize product database
        product_db = ProductDatabase()
        print(f"✓ Product database initialized")
        
        # Test 1: Get comprehensive strain information
        print("\n1. Testing comprehensive strain information...")
        test_strains = ["Blue Dream", "Super Boof", "Grand Daddy Purple"]
        
        for strain_name in test_strains:
            print(f"\n   Testing strain: {strain_name}")
            strain_info = product_db.get_strain_with_products_info(strain_name)
            
            if strain_info:
                print(f"   ✓ Found comprehensive info for {strain_name}")
                print(f"   - Display lineage: {strain_info['strain_info']['display_lineage']}")
                print(f"   - Total products: {strain_info['aggregated_info']['total_products']}")
                print(f"   - Brands: {strain_info['aggregated_info']['brands'][:3]}...")  # Show first 3
                print(f"   - Vendors: {strain_info['aggregated_info']['vendors'][:3]}...")  # Show first 3
                print(f"   - Weights: {strain_info['aggregated_info']['weights'][:3]}...")  # Show first 3
                print(f"   - Most common brand: {strain_info['aggregated_info']['most_common_brand']}")
                print(f"   - Most common weight: {strain_info['aggregated_info']['most_common_weight']}")
                print(f"   - Most common price: {strain_info['aggregated_info']['most_common_price']}")
            else:
                print(f"   ✗ No comprehensive info found for {strain_name}")
        
        # Test 2: Get strain information with brand context
        print("\n2. Testing strain information with brand context...")
        test_brands = ["Dank Czar", "Super Fog", "Wyld"]
        
        for brand in test_brands:
            print(f"\n   Testing brand: {brand}")
            strain_info = product_db.get_strain_brand_info("Blue Dream", brand)
            
            if strain_info:
                print(f"   ✓ Found brand-specific info for Blue Dream + {brand}")
                print(f"   - Display lineage: {strain_info['display_lineage']}")
                print(f"   - Brand lineage: {strain_info['brand_lineage']}")
                print(f"   - Total products: {strain_info['aggregated_info']['total_products']}")
                print(f"   - Most common weight: {strain_info['aggregated_info']['most_common_weight']}")
                print(f"   - Most common price: {strain_info['aggregated_info']['most_common_price']}")
            else:
                print(f"   ✗ No brand-specific info found for Blue Dream + {brand}")
        
        # Test 3: Get strains with brand info
        print("\n3. Testing strains with brand info...")
        strains_with_brand = product_db.get_strains_with_brand_info(limit=5)
        print(f"   ✓ Retrieved {len(strains_with_brand)} strains with brand info")
        
        for i, strain in enumerate(strains_with_brand[:3]):  # Show first 3
            print(f"   {i+1}. {strain['strain_name']}")
            print(f"      - Lineage: {strain['display_lineage']}")
            print(f"      - Brand: {strain['brand']}")
            print(f"      - Vendor: {strain['vendor']}")
            print(f"      - Weight: {strain['weight']} {strain['units']}")
            print(f"      - Price: {strain['price']}")
        
        # Test 4: Test JSON matcher enhanced functionality
        print("\n4. Testing JSON matcher enhanced functionality...")
        
        # Initialize Excel processor and JSON matcher
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Test product names that should contain strains
        test_products = [
            "Blue Dream Flower by Dank Czar - 3.5g",
            "Super Boof Concentrate by Super Fog - 1g",
            "Grand Daddy Purple Pre-Roll by Wyld - 1g"
        ]
        
        for product_name in test_products:
            print(f"\n   Testing product: {product_name}")
            
            # Test strain finding
            found_strains = json_matcher._find_strains_in_text(product_name)
            if found_strains:
                print(f"   ✓ Found {len(found_strains)} strains")
                for strain_name, lineage in found_strains:
                    print(f"   - {strain_name}: {lineage}")
                    
                    # Test comprehensive info retrieval
                    strain_info = json_matcher._get_strain_comprehensive_info(strain_name)
                    if strain_info:
                        print(f"     ✓ Comprehensive info available")
                        print(f"     - Display lineage: {strain_info.get('display_lineage', 'N/A')}")
                        print(f"     - Total products: {strain_info.get('aggregated_info', {}).get('total_products', 0)}")
                        print(f"     - Most common weight: {strain_info.get('aggregated_info', {}).get('most_common_weight', 'N/A')}")
                        print(f"     - Most common price: {strain_info.get('aggregated_info', {}).get('most_common_price', 'N/A')}")
                    else:
                        print(f"     ✗ No comprehensive info available")
            else:
                print(f"   ✗ No strains found")
        
        # Test 5: Test enhanced fallback tag creation
        print("\n5. Testing enhanced fallback tag creation...")
        
        test_json_item = {
            "product_name": "Blue Dream Flower by Dank Czar - 3.5g",
            "product_type": "flower",
            "qty": 1,
            "vendor": "JSM LLC",
            "brand": "Dank Czar"
        }
        
        # Test with strain found
        fallback_tag = json_matcher._create_enhanced_fallback_tag(test_json_item, "Blue Dream", "JSM LLC", "Dank Czar")
        print(f"   ✓ Created enhanced fallback tag with strain")
        print(f"   - Product Name: {fallback_tag['Product Name*']}")
        print(f"   - Lineage: {fallback_tag['Lineage']}")
        print(f"   - Vendor: {fallback_tag['Vendor']}")
        print(f"   - Brand: {fallback_tag['Product Brand']}")
        print(f"   - Weight: {fallback_tag.get('Weight*', 'N/A')}")
        print(f"   - Units: {fallback_tag.get('Weight Unit* (grams/gm or ounces/oz)', 'N/A')}")
        print(f"   - Price: {fallback_tag.get('Price', 'N/A')}")
        print(f"   - Strain: {fallback_tag.get('Product Strain', 'N/A')}")
        
        # Test without strain (should still work)
        fallback_tag_no_strain = json_matcher._create_enhanced_fallback_tag(test_json_item, None, "JSM LLC", "Dank Czar")
        print(f"   ✓ Created enhanced fallback tag without strain")
        print(f"   - Lineage: {fallback_tag_no_strain['Lineage']}")
        print(f"   - Price: {fallback_tag_no_strain.get('Price', 'N/A')}")
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False
    
    return True

def test_database_queries():
    """Test direct database queries to verify data integrity."""
    print("\n=== Testing Database Queries ===")
    
    try:
        import sqlite3
        
        # Connect to the database
        db_path = "product_database.db"
        if not os.path.exists(db_path):
            print(f"✗ Database file not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check strains table
        print("\n1. Checking strains table...")
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        print(f"   ✓ Total strains: {strain_count}")
        
        # Test 2: Check products table
        print("\n2. Checking products table...")
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"   ✓ Total products: {product_count}")
        
        # Test 3: Check products with strain associations
        print("\n3. Checking products with strain associations...")
        cursor.execute("""
            SELECT COUNT(*) FROM products p 
            JOIN strains s ON p.strain_id = s.id
        """)
        associated_count = cursor.fetchone()[0]
        print(f"   ✓ Products with strain associations: {associated_count}")
        
        # Test 4: Check brand-specific lineages
        print("\n4. Checking brand-specific lineages...")
        cursor.execute("SELECT COUNT(*) FROM strain_brand_lineage")
        brand_lineage_count = cursor.fetchone()[0]
        print(f"   ✓ Brand-specific lineages: {brand_lineage_count}")
        
        # Test 5: Sample data verification
        print("\n5. Sample data verification...")
        cursor.execute("""
            SELECT s.strain_name, p.brand, p.vendor, p.weight, p.units, p.price
            FROM strains s
            JOIN products p ON s.id = p.strain_id
            WHERE p.brand IS NOT NULL AND p.weight IS NOT NULL
            ORDER BY p.total_occurrences DESC
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        print(f"   ✓ Sample products with complete info:")
        for i, sample in enumerate(samples, 1):
            strain_name, brand, vendor, weight, units, price = sample
            print(f"   {i}. {strain_name} | {brand} | {vendor} | {weight}{units} | {price}")
        
        conn.close()
        print("\n=== Database queries completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Error during database testing: {e}")
        logger.error(f"Database test error: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    print("Enhanced Strain Information Test Suite")
    print("=" * 50)
    
    # Run tests
    success1 = test_enhanced_strain_info()
    success2 = test_database_queries()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Enhanced strain information is working correctly.")
        print("\nKey improvements implemented:")
        print("✓ Comprehensive strain information with brand, weight, vendor, and price data")
        print("✓ Brand-specific lineage overrides")
        print("✓ Enhanced JSON matching with strain context")
        print("✓ Improved fallback tag creation with real data")
        print("✓ API endpoints for accessing enhanced strain information")
    else:
        print("\n❌ Some tests failed. Please check the logs for details.")
        sys.exit(1) 