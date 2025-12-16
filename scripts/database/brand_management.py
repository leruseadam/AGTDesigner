#!/usr/bin/env python3
"""
Comprehensive Brand Management Script
- Cleans up corrupted records
- Ensures brand enrichment is working
- Provides brand statistics
"""
import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.product_database import ProductDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_database_health():
    """Analyze the health of the product database."""
    logger.info("🔍 Analyzing database health...")
    
    try:
        db = ProductDatabase()
        all_products = db.get_all_products()
        
        # Categorize products
        valid_products = []
        corrupted_products = []
        products_with_brands = []
        products_without_brands = []
        
        for product in all_products:
            product_name = product.get('ProductName')
            brand = product.get('Product Brand', '')
            
            # Check if product is corrupted
            if not product_name or product_name == 'None' or product_name.strip() == '':
                corrupted_products.append(product)
            else:
                valid_products.append(product)
                
                if brand and brand.strip():
                    products_with_brands.append(product)
                else:
                    products_without_brands.append(product)
        
        logger.info(f"📊 Database Health Report:")
        logger.info(f"   Total products: {len(all_products)}")
        logger.info(f"   ✅ Valid products: {len(valid_products)}")
        logger.info(f"   ❌ Corrupted products: {len(corrupted_products)}")
        logger.info(f"   🏷️  Valid products with brands: {len(products_with_brands)}")
        logger.info(f"   ⚠️  Valid products without brands: {len(products_without_brands)}")
        
        if len(valid_products) > 0:
            brand_coverage = (len(products_with_brands) / len(valid_products)) * 100
            logger.info(f"   📈 Brand coverage (valid products): {brand_coverage:.1f}%")
        
        # Show corrupted products
        if corrupted_products:
            logger.info(f"\\n❌ Corrupted products found:")
            for product in corrupted_products:
                product_id = product.get('id')
                vendor = product.get('Vendor/Supplier*', 'N/A')
                logger.info(f"   - ID: {product_id}, Vendor: {vendor}")
        
        # Show valid products without brands
        if products_without_brands:
            logger.info(f"\\n⚠️  Valid products without brands:")
            for product in products_without_brands[:5]:  # Show first 5
                product_name = product.get('ProductName')
                vendor = product.get('Vendor/Supplier*', 'N/A')
                logger.info(f"   - {product_name} (Vendor: {vendor})")
        
        return {
            'total': len(all_products),
            'valid': len(valid_products),
            'corrupted': len(corrupted_products),
            'with_brands': len(products_with_brands),
            'without_brands': len(products_without_brands),
            'brand_coverage': brand_coverage if len(valid_products) > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing database health: {e}")
        return None

def test_brand_enrichment():
    """Test the brand enrichment functionality in the template processor."""
    logger.info("🧪 Testing brand enrichment functionality...")
    
    try:
        from src.core.generation.template_processor import TemplateProcessor
        from docx import Document
        
        # Create a template processor
        processor = TemplateProcessor('vertical', {}, 1.0)
        
        # Test records with missing brands but real product names
        test_records = [
            {
                'ProductName': "Stone Thermal Chromatic Quartz Banger - Assorted",
                'Product Brand': "",
                'Product Type*': 'accessory',
                'Price': '45'
            },
            {
                'ProductName': "$8 Dab Straw by Mary Jane's Glass Productions",
                'Product Brand': "",
                'Product Type*': 'accessory', 
                'Price': '8'
            }
        ]
        
        doc = Document()
        enriched_count = 0
        
        for i, record in enumerate(test_records):
            original_brand = record.get('Product Brand', '')
            context = processor._build_label_context(record, doc)
            final_brand = context.get('ProductBrand', '')
            
            logger.info(f"\\n🧪 Test {i+1}: {record['ProductName'][:50]}...")
            logger.info(f"   Original brand: '{original_brand}'")
            logger.info(f"   Enriched brand: '{final_brand}'")
            
            if final_brand and final_brand != original_brand:
                enriched_count += 1
                logger.info(f"   ✅ Brand successfully enriched!")
            else:
                logger.info(f"   ⚠️  No brand enrichment occurred")
        
        logger.info(f"\\n🧪 Enrichment test results: {enriched_count}/{len(test_records)} brands enriched")
        return enriched_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error testing brand enrichment: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_brand_statistics():
    """Get comprehensive brand statistics."""
    logger.info("📊 Gathering brand statistics...")
    
    try:
        db = ProductDatabase()
        all_products = db.get_all_products()
        
        # Filter out corrupted products
        valid_products = [p for p in all_products if p.get('ProductName') and p.get('ProductName') != 'None']
        
        # Get brand information
        brands = {}
        vendors = set()
        
        for product in valid_products:
            brand = product.get('Product Brand', '')
            vendor = product.get('Vendor/Supplier*', '')
            
            if vendor:
                vendors.add(vendor)
            
            if brand:
                if brand not in brands:
                    brands[brand] = 0
                brands[brand] += 1
        
        # Sort brands by product count
        sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"📊 Brand Statistics:")
        logger.info(f"   Valid products: {len(valid_products)}")
        logger.info(f"   Unique brands: {len(brands)}")
        logger.info(f"   Unique vendors: {len(vendors)}")
        
        logger.info(f"\\n🏆 Top 10 brands by product count:")
        for brand, count in sorted_brands[:10]:
            logger.info(f"   - {brand}: {count} products")
        
        return {
            'valid_products': len(valid_products),
            'unique_brands': len(brands),
            'unique_vendors': len(vendors),
            'top_brands': sorted_brands[:10]
        }
        
    except Exception as e:
        logger.error(f"❌ Error gathering brand statistics: {e}")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starting Comprehensive Brand Management")
    
    # Analyze database health
    health = analyze_database_health()
    
    # Test brand enrichment functionality
    enrichment_works = test_brand_enrichment()
    
    # Get brand statistics
    stats = get_brand_statistics()
    
    # Summary
    logger.info(f"\\n📋 Summary:")
    if health:
        logger.info(f"   📊 Database: {health['valid']} valid products, {health['brand_coverage']:.1f}% brand coverage")
    if enrichment_works:
        logger.info(f"   ✅ Brand enrichment: Working correctly")
    else:
        logger.info(f"   ❌ Brand enrichment: Needs attention")
    if stats:
        logger.info(f"   🏷️  Brands: {stats['unique_brands']} unique brands across {stats['valid_products']} products")
    
    logger.info("\\n✅ Brand management analysis completed!")