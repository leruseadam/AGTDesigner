#!/usr/bin/env python3
"""
Test script to demonstrate educated guessing functionality.
This script shows how the system can make educated guesses for new products
based on similar existing products in the database.
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.product_database import ProductDatabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_educated_guessing():
    """Test the educated guessing functionality with various product examples."""
    
    print("🧪 Testing Educated Guessing Functionality")
    print("=" * 50)
    
    try:
        # Initialize the product database
        product_db = ProductDatabase()
        product_db.init_database()
        
        # Test cases - products that might not exist in the database
        test_products = [
            {
                "name": "Glazed Apricots Live Resin Disposable Vape",
                "vendor": "Dank Czar",
                "brand": "Dank Czar",
                "description": "New apricot-flavored disposable vape"
            },
            {
                "name": "Wedding Cake Live Resin Disposable Vape", 
                "vendor": "Dank Czar",
                "brand": "Dank Czar",
                "description": "Existing wedding cake strain in disposable format"
            },
            {
                "name": "Blueberry Kush Flower 3.5g",
                "vendor": "Omega Labs",
                "brand": "Omega Labs", 
                "description": "Blueberry kush strain in flower format"
            },
            {
                "name": "Sour Diesel Pre-Roll 1g",
                "vendor": "Hustler's Ambition",
                "brand": "Hustler's Ambition",
                "description": "Sour diesel in pre-roll format"
            },
            {
                "name": "Lemon Haze Concentrate 1g",
                "vendor": "Airo Pro",
                "brand": "Airo Pro",
                "description": "Lemon haze in concentrate format"
            }
        ]
        
        print(f"Testing {len(test_products)} product examples...\n")
        
        for i, test_product in enumerate(test_products, 1):
            print(f"📦 Test {i}: {test_product['name']}")
            print(f"   Vendor: {test_product['vendor']}")
            print(f"   Brand: {test_product['brand']}")
            print(f"   Description: {test_product['description']}")
            
            # Try to make an educated guess
            educated_guess = product_db.make_educated_guess(
                test_product['name'], 
                test_product['vendor'], 
                test_product['brand']
            )
            
            if educated_guess:
                print(f"   ✅ EDUCATED GUESS FOUND:")
                print(f"      Product Type: {educated_guess.get('product_type', 'Unknown')}")
                print(f"      Strain: {educated_guess.get('strain_name', 'Unknown')}")
                print(f"      Lineage: {educated_guess.get('lineage', 'Unknown')}")
                print(f"      Weight: {educated_guess.get('weight', 'Unknown')} {educated_guess.get('units', 'Unknown')}")
                print(f"      Price: ${educated_guess.get('price', 'Unknown')}")
                print(f"      Confidence: {educated_guess.get('confidence', 'Unknown')}")
                print(f"      Description: {educated_guess.get('description', 'Unknown')}")
            else:
                print(f"   ❌ No educated guess available")
            
            print()
        
        print("🎯 Summary:")
        print("The educated guessing system works by:")
        print("1. Finding similar products in the database based on:")
        print("   - Similar product names and key terms")
        print("   - Same product types (flower, concentrate, vape, etc.)")
        print("   - Same strain names")
        print("2. Analyzing the properties of similar products")
        print("3. Inferring missing information using:")
        print("   - Median weights and prices from similar products")
        print("   - Most common product types, lineages, and strains")
        print("   - Pattern matching for weights and units")
        print("4. Providing confidence levels for the guesses")
        
        print("\n💡 Example Use Cases:")
        print("- New product variants (e.g., 'Glazed Apricots' based on existing 'Wedding Cake')")
        print("- Different formats of the same strain (e.g., flower vs concentrate)")
        print("- New brands with similar product types")
        print("- Products with slight name variations")
        
    except Exception as e:
        logger.error(f"Error testing educated guessing: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_educated_guessing()
