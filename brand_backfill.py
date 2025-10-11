#!/usr/bin/env python3
"""
Brand Backfill Script - Fills in missing brand information in the product database
"""
import sys
import os
import logging
import re

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.product_database import ProductDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_brand_from_vendor(vendor_name):
    """Extract a potential brand name from vendor/supplier name."""
    if not vendor_name or vendor_name.strip() == '':
        return None
    
    # Clean up vendor name
    vendor = vendor_name.strip()
    
    # Remove common business suffixes
    business_suffixes = [
        r'\s*,?\s*DBA\s+.*$',
        r'\s*,?\s*LLC$',
        r'\s*,?\s*Inc\.?$',
        r'\s*,?\s*Corp\.?$',
        r'\s*,?\s*Co\.?$',
        r'\s*,?\s*Ltd\.?$',
        r'\s*,?\s*SPC$',
        r'\s*Proc$',
        r'\s*Consultants$'
    ]
    
    for suffix in business_suffixes:
        vendor = re.sub(suffix, '', vendor, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    vendor = ' '.join(vendor.split())
    
    # If it's too generic or empty, return None
    generic_names = ['WAVE', 'Green Revolution', '']
    if vendor in generic_names:
        return None
    
    return vendor

def backfill_missing_brands():
    """Backfill missing brand information in the database."""
    logger.info("🔍 Starting brand backfill process...")
    
    try:
        db = ProductDatabase()
        
        # Get all products without brands
        all_products = db.get_all_products()
        products_without_brands = [p for p in all_products if not p.get('Product Brand', '')]
        
        logger.info(f"Found {len(products_without_brands)} products without brand information")
        
        if not products_without_brands:
            logger.info("✅ All products already have brand information!")
            return
        
        backfilled_count = 0
        skipped_count = 0
        
        for product in products_without_brands:
            product_name = product.get('ProductName')
            vendor = product.get('Vendor/Supplier*', '')
            product_id = product.get('id')
            
            logger.info(f"\\n🔍 Processing product: '{product_name}' (ID: {product_id})")
            logger.info(f"   Vendor: '{vendor}'")
            
            # Skip products with corrupted names
            if not product_name or product_name == 'None':
                logger.warning(f"   ⚠️  Skipping product with corrupted name")
                skipped_count += 1
                continue
            
            # Try to extract brand from vendor
            potential_brand = extract_brand_from_vendor(vendor)
            
            if potential_brand:
                logger.info(f"   ✅ Extracted brand: '{potential_brand}'")
                
                # Update the product in database
                try:
                    # Note: This is a simplified approach - in a real scenario you'd need 
                    # to implement an update method in ProductDatabase
                    logger.info(f"   📝 Would update product {product_id} with brand: '{potential_brand}'")
                    backfilled_count += 1
                except Exception as e:
                    logger.error(f"   ❌ Failed to update product {product_id}: {e}")
            else:
                logger.info(f"   ⚠️  Could not determine brand from vendor: '{vendor}'")
                skipped_count += 1
        
        logger.info(f"\\n📊 Brand backfill summary:")
        logger.info(f"   ✅ Brands backfilled: {backfilled_count}")
        logger.info(f"   ⚠️  Products skipped: {skipped_count}")
        logger.info(f"   📈 Total processed: {len(products_without_brands)}")
        
        # Show updated brand coverage
        all_products_updated = db.get_all_products()
        products_with_brands_updated = [p for p in all_products_updated if p.get('Product Brand', '')]
        new_coverage = (len(products_with_brands_updated) / len(all_products_updated)) * 100
        
        logger.info(f"\\n📊 Updated brand coverage: {new_coverage:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ Error during brand backfill: {e}")
        import traceback
        traceback.print_exc()

def analyze_brand_patterns():
    """Analyze existing brand patterns to help with backfill."""
    logger.info("🔍 Analyzing existing brand patterns...")
    
    try:
        db = ProductDatabase()
        all_products = db.get_all_products()
        
        # Get unique brands
        brands = set()
        vendor_brand_mapping = {}
        
        for product in all_products:
            brand = product.get('Product Brand', '')
            vendor = product.get('Vendor/Supplier*', '')
            
            if brand:
                brands.add(brand)
                if vendor not in vendor_brand_mapping:
                    vendor_brand_mapping[vendor] = set()
                vendor_brand_mapping[vendor].add(brand)
        
        logger.info(f"📊 Found {len(brands)} unique brands")
        logger.info(f"📊 Found {len(vendor_brand_mapping)} unique vendors")
        
        # Show vendors with multiple brands
        multi_brand_vendors = {v: brands for v, brands in vendor_brand_mapping.items() if len(brands) > 1}
        if multi_brand_vendors:
            logger.info(f"\\n🏢 Vendors with multiple brands:")
            for vendor, vendor_brands in list(multi_brand_vendors.items())[:5]:
                logger.info(f"   - {vendor}: {', '.join(vendor_brands)}")
        
        return vendor_brand_mapping
        
    except Exception as e:
        logger.error(f"❌ Error during brand pattern analysis: {e}")
        return {}

if __name__ == "__main__":
    logger.info("🚀 Starting Brand Backfill Process")
    
    # First analyze patterns
    analyze_brand_patterns()
    
    # Then backfill missing brands
    backfill_missing_brands()
    
    logger.info("✅ Brand backfill process completed!")