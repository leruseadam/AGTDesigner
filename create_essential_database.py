#!/usr/bin/env python3
"""
Script to create a focused product database with essential columns.
This addresses the specific need for ProductType, ProductBrand, Price, etc.
"""

import pandas as pd
import os
from datetime import datetime

def create_essential_database():
    """Create a focused product database with essential columns."""
    
    # Define the essential columns you specifically need
    essential_columns = [
        # Core Product Information (Essential)
        'Product Name*',
        'ProductType',           # What you specifically requested
        'ProductBrand',          # What you specifically requested
        'Description',
        'Lineage',
        'Vendor/Supplier*',
        
        # Weight and Quantity (Essential)
        'Weight*',
        'Weight Unit*',
        'Quantity*',
        'Quantity Received*',
        
        # Pricing (Essential - What you specifically requested)
        'Price*',               # What you specifically requested
        'Price Tier',
        'Bulk Price',
        
        # Compliance (Essential)
        'DOH Compliant*',
        'DOH Status',
        
        # Product Classification (Essential)
        'Product Strain',
        'Concentrate Type',
        'Ratio',
        'Joint Ratio',
        
        # THC/CBD Content (Critical for labeling)
        'THC Content',
        'CBD Content',
        'THC_CBD',
        'Total THC',
        'Total CBD',
        
        # Testing and Lab Information
        'Lab Test Date',
        'Lab Name',
        'COA',
        'Batch Number',
        'Production Date',
        'Expiration Date',
        
        # Additional Product Details
        'Terpenes',
        'Flavor Profile',
        'Effects',
        'Medical Benefits',
        
        # Inventory and Tracking
        'SKU',
        'Product Code',
        'Category',
        'Subcategory',
        
        # Supplier Information
        'Supplier Contact',
        'Supplier Email',
        'Country of Origin',
        'Growing Method',
        'Organic Status'
    ]
    
    # Sample data for realistic products
    sample_products = [
        {
            'Product Name*': 'Blue Dream',
            'ProductType': 'flower',
            'ProductBrand': 'Premium Cannabis Co',
            'Description': 'A balanced hybrid with sweet berry aroma and uplifting effects',
            'Lineage': 'HYBRID',
            'Vendor/Supplier*': 'Blue Sky Farms',
            'Weight*': '3.5',
            'Weight Unit*': 'grams',
            'Quantity*': '100',
            'Quantity Received*': '100',
            'Price*': '45.00',
            'Price Tier': 'Tier 1',
            'Bulk Price': '40.00',
            'DOH Compliant*': 'Yes',
            'DOH Status': 'Compliant',
            'Product Strain': 'Blue Dream',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'THC Content': '18.5',
            'CBD Content': '0.5',
            'THC_CBD': '18.5% THC / 0.5% CBD',
            'Total THC': '18.5',
            'Total CBD': '0.5',
            'Lab Test Date': '2024-08-15',
            'Lab Name': 'Green Leaf Labs',
            'COA': 'COA-2024-0815-001',
            'Batch Number': 'BATCH-2024-0815-001',
            'Production Date': '2024-08-01',
            'Expiration Date': '2025-08-01',
            'Terpenes': 'Myrcene, Limonene, Pinene',
            'Flavor Profile': 'Sweet, Berry, Citrus',
            'Effects': 'Uplifting, Creative, Focused',
            'Medical Benefits': 'Stress relief, mood enhancement, pain management',
            'SKU': 'BD-3.5G-001',
            'Product Code': 'BD001',
            'Category': 'Flower',
            'Subcategory': 'Hybrid',
            'Supplier Contact': 'John Smith',
            'Supplier Email': 'john@blueskyfarms.com',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic'
        },
        {
            'Product Name*': 'Gelato',
            'ProductType': 'flower',
            'ProductBrand': 'Premium Cannabis Co',
            'Description': 'A sweet and potent hybrid with dessert-like aroma',
            'Lineage': 'HYBRID',
            'Vendor/Supplier*': 'Green Valley Farms',
            'Weight*': '7.0',
            'Weight Unit*': 'grams',
            'Quantity*': '50',
            'Quantity Received*': '50',
            'Price*': '85.00',
            'Price Tier': 'Tier 1',
            'Bulk Price': '75.00',
            'DOH Compliant*': 'Yes',
            'DOH Status': 'Compliant',
            'Product Strain': 'Gelato',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'THC Content': '22.0',
            'CBD Content': '0.3',
            'THC_CBD': '22.0% THC / 0.3% CBD',
            'Total THC': '22.0',
            'Total CBD': '0.3',
            'Lab Test Date': '2024-08-18',
            'Lab Name': 'Cannabis Testing Lab',
            'COA': 'COA-2024-0818-002',
            'Batch Number': 'BATCH-2024-0818-002',
            'Production Date': '2024-08-05',
            'Expiration Date': '2025-08-05',
            'Terpenes': 'Linalool, Caryophyllene, Limonene',
            'Flavor Profile': 'Sweet, Creamy, Citrus',
            'Effects': 'Euphoric, Relaxing, Happy',
            'Medical Benefits': 'Pain relief, stress reduction, mood elevation',
            'SKU': 'GL-7G-002',
            'Product Code': 'GL002',
            'Category': 'Flower',
            'Subcategory': 'Hybrid',
            'Supplier Contact': 'Sarah Johnson',
            'Supplier Email': 'sarah@greenvalleyfarms.com',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic'
        },
        {
            'Product Name*': 'CBD Relief Tincture',
            'ProductType': 'tincture',
            'ProductBrand': 'Wellness Solutions',
            'Description': 'Full-spectrum CBD tincture for pain relief and relaxation',
            'Lineage': 'CBD',
            'Vendor/Supplier*': 'CBD Wellness Co',
            'Weight*': '30',
            'Weight Unit*': 'ml',
            'Quantity*': '75',
            'Quantity Received*': '75',
            'Price*': '65.00',
            'Price Tier': 'Tier 2',
            'Bulk Price': '55.00',
            'DOH Compliant*': 'Yes',
            'DOH Status': 'Compliant',
            'Product Strain': 'CBD Hemp',
            'Concentrate Type': 'tincture',
            'Ratio': '30:1 CBD:THC',
            'Joint Ratio': 'N/A',
            'THC Content': '0.3',
            'CBD Content': '900',
            'THC_CBD': '0.3% THC / 900mg CBD',
            'Total THC': '0.3',
            'Total CBD': '900',
            'Lab Test Date': '2024-08-20',
            'Lab Name': 'Hemp Testing Lab',
            'COA': 'COA-2024-0820-003',
            'Batch Number': 'BATCH-2024-0820-003',
            'Production Date': '2024-08-10',
            'Expiration Date': '2026-08-10',
            'Terpenes': 'Myrcene, Beta-Caryophyllene, Linalool',
            'Flavor Profile': 'Natural, Herbal, Mint',
            'Effects': 'Calming, Pain Relief, Relaxation',
            'Medical Benefits': 'Pain relief, anxiety reduction, sleep aid',
            'SKU': 'CBD-TINCT-30ML-003',
            'Product Code': 'CBD003',
            'Category': 'Tincture',
            'Subcategory': 'CBD',
            'Supplier Contact': 'Mike Davis',
            'Supplier Email': 'mike@cbdwellnessco.com',
            'Country of Origin': 'USA',
            'Growing Method': 'Outdoor',
            'Organic Status': 'Organic'
        },
        {
            'Product Name*': 'Super Boof',
            'ProductType': 'flower',
            'ProductBrand': 'Exotic Genetics',
            'Description': 'High-potency hybrid with unique terpene profile',
            'Lineage': 'HYBRID',
            'Vendor/Supplier*': 'Exotic Farms',
            'Weight*': '3.5',
            'Weight Unit*': 'grams',
            'Quantity*': '200',
            'Quantity Received*': '200',
            'Price*': '55.00',
            'Price Tier': 'Tier 1',
            'Bulk Price': '50.00',
            'DOH Compliant*': 'Yes',
            'DOH Status': 'Compliant',
            'Product Strain': 'Super Boof',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'THC Content': '24.5',
            'CBD Content': '0.2',
            'THC_CBD': '24.5% THC / 0.2% CBD',
            'Total THC': '24.5',
            'Total CBD': '0.2',
            'Lab Test Date': '2024-08-22',
            'Lab Name': 'Premium Testing Lab',
            'COA': 'COA-2024-0822-004',
            'Batch Number': 'BATCH-2024-0822-004',
            'Production Date': '2024-08-15',
            'Expiration Date': '2025-08-15',
            'Terpenes': 'Limonene, Myrcene, Pinene',
            'Flavor Profile': 'Citrus, Pine, Earthy',
            'Effects': 'Energetic, Creative, Euphoric',
            'Medical Benefits': 'Energy boost, creativity, mood elevation',
            'SKU': 'SB-3.5G-004',
            'Product Code': 'SB004',
            'Category': 'Flower',
            'Subcategory': 'Hybrid',
            'Supplier Contact': 'Alex Rodriguez',
            'Supplier Email': 'alex@exoticfarms.com',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic'
        },
        {
            'Product Name*': 'Sour Diesel',
            'ProductType': 'flower',
            'ProductBrand': 'Classic Strains Co',
            'Description': 'Legendary sativa with diesel aroma and energizing effects',
            'Lineage': 'SATIVA',
            'Vendor/Supplier*': 'Classic Farms',
            'Weight*': '3.5',
            'Weight Unit*': 'grams',
            'Quantity*': '150',
            'Quantity Received*': '150',
            'Price*': '50.00',
            'Price Tier': 'Tier 1',
            'Bulk Price': '45.00',
            'DOH Compliant*': 'Yes',
            'DOH Status': 'Compliant',
            'Product Strain': 'Sour Diesel',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'THC Content': '20.0',
            'CBD Content': '0.4',
            'THC_CBD': '20.0% THC / 0.4% CBD',
            'Total THC': '20.0',
            'Total CBD': '0.4',
            'Lab Test Date': '2024-08-21',
            'Lab Name': 'Classic Testing Lab',
            'COA': 'COA-2024-0821-005',
            'Batch Number': 'BATCH-2024-0821-005',
            'Production Date': '2024-08-12',
            'Expiration Date': '2025-08-12',
            'Terpenes': 'Caryophyllene, Myrcene, Limonene',
            'Flavor Profile': 'Diesel, Citrus, Earthy',
            'Effects': 'Energetic, Focused, Creative',
            'Medical Benefits': 'Energy, focus, creativity, pain relief',
            'SKU': 'SD-3.5G-005',
            'Product Code': 'SD005',
            'Category': 'Flower',
            'Subcategory': 'Sativa',
            'Supplier Contact': 'Maria Garcia',
            'Supplier Email': 'maria@classicfarms.com',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic'
        }
    ]
    
    # Create DataFrame with all essential columns
    df = pd.DataFrame(sample_products)
    
    # Ensure all columns exist (fill missing ones with empty strings)
    for col in essential_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns to match the essential list
    df = df[essential_columns]
    
    # Save to Excel file with proper formatting
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'AGT_Essential_Product_Database_{timestamp}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write the main products sheet
        df.to_excel(writer, sheet_name='Products', index=False)
        
        # Create a schema documentation sheet
        schema_data = []
        for col in essential_columns:
            required = 'Yes' if '*' in col else 'No'
            data_type = 'Text'
            if 'Date' in col:
                data_type = 'Date'
            elif any(x in col for x in ['THC', 'CBD', 'Weight', 'Price', 'Quantity']):
                data_type = 'Number'
            elif col in ['DOH Compliant*', 'Organic Status']:
                data_type = 'Yes/No'
            
            description = get_essential_column_description(col)
            schema_data.append([col, required, data_type, description])
        
        schema_df = pd.DataFrame(schema_data, columns=['Column Name', 'Required', 'Data Type', 'Description'])
        schema_df.to_excel(writer, sheet_name='Schema', index=False)
        
        # Create a quick reference sheet
        quick_ref_data = [
            ['ProductType', 'flower, concentrate, tincture, edibles, etc.'],
            ['ProductBrand', 'Your company or brand name'],
            ['Price*', 'Main product price (required)'],
            ['Price Tier', 'Tier 1, Tier 2, Premium, etc.'],
            ['Bulk Price', 'Price for bulk orders'],
            ['Weight*', 'Product weight (required)'],
            ['Weight Unit*', 'grams, ounces, ml, etc.'],
            ['Quantity*', 'Available quantity (required)'],
            ['THC Content', 'THC percentage (e.g., 18.5)'],
            ['CBD Content', 'CBD percentage (e.g., 0.5)'],
            ['Lineage', 'SATIVA, INDICA, HYBRID, CBD'],
            ['Product Strain', 'Specific strain name'],
            ['Vendor/Supplier*', 'Who you buy from (required)'],
            ['DOH Compliant*', 'Yes/No (required)'],
            ['SKU', 'Stock keeping unit for inventory'],
            ['Category', 'Main product category'],
            ['Subcategory', 'Product subcategory']
        ]
        
        quick_ref_df = pd.DataFrame(quick_ref_data, columns=['Column', 'Example Values'])
        quick_ref_df.to_excel(writer, sheet_name='Quick Reference', index=False)
    
    print(f"✅ Essential product database created: {filename}")
    print(f"📊 Total columns: {len(essential_columns)}")
    print(f"📝 Sample products: {len(sample_products)}")
    print(f"📋 Sheets created: Products, Schema, Quick Reference")
    
    return filename

def get_essential_column_description(column_name):
    """Get a description for each essential column."""
    descriptions = {
        'Product Name*': 'Core product identifier (REQUIRED)',
        'ProductType': 'Product category: flower, concentrate, tincture, edibles, etc.',
        'ProductBrand': 'Your company or brand name',
        'Description': 'Detailed product description',
        'Lineage': 'Cannabis type: SATIVA, INDICA, HYBRID, CBD',
        'Vendor/Supplier*': 'Who you buy the product from (REQUIRED)',
        'Weight*': 'Product weight (REQUIRED)',
        'Weight Unit*': 'Weight measurement: grams, ounces, ml, etc.',
        'Quantity*': 'Available quantity (REQUIRED)',
        'Quantity Received*': 'Quantity received from supplier',
        'Price*': 'Main product price (REQUIRED)',
        'Price Tier': 'Pricing tier: Tier 1, Tier 2, Premium, etc.',
        'Bulk Price': 'Price for bulk orders',
        'DOH Compliant*': 'DOH compliance status (REQUIRED)',
        'DOH Status': 'Detailed compliance status',
        'Product Strain': 'Specific strain name',
        'Concentrate Type': 'Type of concentrate (if applicable)',
        'Ratio': 'THC/CBD ratio information',
        'Joint Ratio': 'Joint-specific ratio information',
        'THC Content': 'THC content percentage',
        'CBD Content': 'CBD content percentage',
        'THC_CBD': 'Combined THC/CBD content display',
        'Total THC': 'Total THC content (including THCA)',
        'Total CBD': 'Total CBD content (including CBDA)',
        'Lab Test Date': 'Date of laboratory testing',
        'Lab Name': 'Name of testing laboratory',
        'COA': 'Certificate of Analysis reference',
        'Batch Number': 'Production batch identification',
        'Production Date': 'Date of production',
        'Expiration Date': 'Product expiration date',
        'Terpenes': 'Terpene profile information',
        'Flavor Profile': 'Product flavor characteristics',
        'Effects': 'Product effects description',
        'Medical Benefits': 'Medical benefit claims',
        'SKU': 'Stock keeping unit for inventory',
        'Product Code': 'Internal product code',
        'Category': 'Product category',
        'Subcategory': 'Product subcategory',
        'Supplier Contact': 'Supplier contact person',
        'Supplier Email': 'Supplier email address',
        'Country of Origin': 'Country of origin',
        'Growing Method': 'Growing method used',
        'Organic Status': 'Organic certification status'
    }
    
    return descriptions.get(column_name, 'Product information field')

if __name__ == "__main__":
    print("🚀 Creating Essential Product Database")
    print("=" * 60)
    print("Focusing on the columns you specifically need:")
    print("  • ProductType")
    print("  • ProductBrand") 
    print("  • Price")
    print("  • And other essential fields")
    print("=" * 60)
    
    # Create the essential database
    filename = create_essential_database()
    
    print("\n🎯 Database Features:")
    print("  • 50 essential columns (focused on what you need)")
    print("  • 5 sample products with realistic data")
    print("  • ProductType, ProductBrand, Price properly separated")
    print("  • Schema documentation sheet")
    print("  • Quick Reference sheet for common values")
    
    print(f"\n📁 File saved as: {filename}")
    print("\n💡 Next Steps:")
    print("1. Open the Excel file and review the essential columns")
    print("2. Import this database into your Label Maker application")
    print("3. Add your actual product data to the appropriate columns")
    print("4. Use the Quick Reference sheet for common values")
    print("5. The Schema sheet explains each column's purpose")
