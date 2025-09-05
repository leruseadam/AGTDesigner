#!/usr/bin/env python3
"""
Script to add all necessary columns to the product database schema.
This ensures the database has all required columns for comprehensive product management.
"""

import pandas as pd
import os
from datetime import datetime

def create_comprehensive_schema():
    """Create a comprehensive product database schema with all necessary columns."""
    
    # Define all the necessary columns for a complete product database
    comprehensive_columns = [
        # Core Product Information
        'Product Name*', 'ProductName', 'Description',
        'Product Type*', 'Lineage', 'Product Brand', 'Vendor/Supplier*',
        
        # Weight and Quantity
        'Weight*', 'Weight Unit* (grams/gm or ounces/oz)', 'Units',
        'Quantity*', 'Quantity Received*', 'Quantity', 'qty',
        
        # Pricing
        'Price* (Tier Name for Bulk)', 'Price',
        
        # Compliance and Testing
        'DOH Compliant (Yes/No)', 'DOH',
        
        # Product Classification
        'Concentrate Type', 'Ratio',
        'Joint Ratio', 'JointRatio',
        'Product Strain',
        
        # THC/CBD Content (Critical for labeling)
        'THC Content', 'THC', 'THC %', 'THC_Percentage',
        'CBD Content', 'CBD', 'CBD %', 'CBD_Percentage',
        'THC_CBD', 'THC_CBD_Content', 'Cannabinoid_Content',
        'Total THC', 'Total CBD', 'Active THC', 'Active CBD',
        
        # Testing and Lab Information
        'Lab Test Date', 'Test Date', 'Testing Date',
        'Lab Name', 'Laboratory', 'Testing Lab',
        'Certificate of Analysis', 'COA', 'Test Results',
        'Batch Number', 'Lot Number', 'Production Date',
        'Expiration Date', 'Shelf Life',
        
        # Additional Product Details
        'Terpenes', 'Terpene Profile', 'Terpene Content',
        'Flavor Profile', 'Aroma', 'Taste',
        'Effects', 'Experience', 'High Type',
        'Medical Benefits', 'Therapeutic Effects',
        
        # Packaging and Storage
        'Package Size', 'Container Type', 'Packaging',
        'Storage Instructions', 'Storage Requirements',
        'Serving Size', 'Dosage Instructions',
        
        # Regulatory and Compliance
        'State Compliance', 'Local Compliance', 'County Compliance',
        'Testing Requirements', 'Compliance Notes',
        'Warning Labels', 'Required Disclaimers',
        
        # Inventory and Tracking
        'SKU', 'Product Code', 'Internal ID',
        'Category', 'Subcategory', 'Product Family',
        'Seasonal', 'Limited Edition', 'Discontinued',
        
        # Supplier and Sourcing
        'Supplier Contact', 'Supplier Email', 'Supplier Phone',
        'Country of Origin', 'Growing Method', 'Organic Status',
        'Certifications', 'Quality Grade', 'Premium Tier',
        
        # Marketing and Sales
        'Marketing Description', 'Sales Notes', 'Promotional Text',
        'Target Audience', 'Recommended Use', 'Usage Instructions',
        'Warnings', 'Side Effects', 'Contraindications'
    ]
    
    # Create a sample database with all columns
    sample_data = []
    for i in range(5):  # Create 5 sample products
        product = {}
        for col in comprehensive_columns:
            if col == 'Product Name*':
                product[col] = f'Sample Product {i+1}'
            elif col == 'Product Type*':
                product[col] = 'flower'
            elif col == 'Lineage':
                product[col] = 'HYBRID'
            elif col == 'Product Brand':
                product[col] = 'Sample Brand'
            elif col == 'Vendor/Supplier*':
                product[col] = 'Sample Vendor'
            elif col == 'Weight*':
                product[col] = '3.5'
            elif col == 'Weight Unit* (grams/gm or ounces/oz)':
                product[col] = 'grams'
            elif col == 'Price* (Tier Name for Bulk)':
                product[col] = 'Tier 1'
            elif col == 'DOH Compliant (Yes/No)':
                product[col] = 'Yes'
            elif col == 'Product Strain':
                product[col] = 'Sample Strain'
            elif col == 'Quantity*':
                product[col] = '100'
            elif col == 'THC Content':
                product[col] = '18.5'
            elif col == 'CBD Content':
                product[col] = '0.5'
            elif col == 'THC_CBD':
                product[col] = '18.5% THC / 0.5% CBD'
            elif col == 'Lab Test Date':
                product[col] = '2024-01-15'
            elif col == 'Lab Name':
                product[col] = 'Sample Lab'
            elif col == 'Batch Number':
                product[col] = f'BATCH-{i+1:03d}'
            elif col == 'Production Date':
                product[col] = '2024-01-01'
            elif col == 'Expiration Date':
                product[col] = '2025-01-01'
            elif col == 'Terpenes':
                product[col] = 'Myrcene, Limonene, Pinene'
            elif col == 'Flavor Profile':
                product[col] = 'Earthy, Citrus, Pine'
            elif col == 'Effects':
                product[col] = 'Relaxing, Uplifting'
            elif col == 'Package Size':
                product[col] = '3.5g'
            elif col == 'SKU':
                product[col] = f'SKU-{i+1:03d}'
            elif col == 'Category':
                product[col] = 'Flower'
            elif col == 'Growing Method':
                product[col] = 'Indoor'
            elif col == 'Organic Status':
                product[col] = 'Organic'
            else:
                product[col] = ''  # Empty for optional fields
        
        sample_data.append(product)
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to Excel file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'comprehensive_product_database_{timestamp}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Products', index=False)
        
        # Create a schema sheet
        schema_df = pd.DataFrame({
            'Column Name': comprehensive_columns,
            'Required': ['Yes' if '*' in col else 'No' for col in comprehensive_columns],
            'Data Type': ['Text' if 'Date' not in col and '%' not in col else 'Date/Number' for col in comprehensive_columns],
            'Description': [
                'Core product identifier' if 'Product Name' in col else
                'Product category classification' if 'Product Type' in col else
                'Cannabis lineage/type' if 'Lineage' in col else
                'Brand name' if 'Brand' in col else
                'Supplier information' if 'Vendor' in col else
                'Product weight' if 'Weight' in col and '*' in col else
                'Weight measurement unit' if 'Unit' in col else
                'Product quantity' if 'Quantity' in col else
                'Pricing information' if 'Price' in col else
                'DOH compliance status' if 'DOH' in col else
                'Concentrate classification' if 'Concentrate' in col else
                'THC/CBD ratio information' if 'Ratio' in col else
                'Joint-specific ratio' if 'Joint' in col else
                'Strain name' if 'Strain' in col else
                'THC content percentage' if 'THC' in col and 'CBD' not in col else
                'CBD content percentage' if 'CBD' in col and 'THC' not in col else
                'Combined THC/CBD content' if 'THC_CBD' in col else
                'Laboratory testing date' if 'Test Date' in col else
                'Testing laboratory name' if 'Lab Name' in col else
                'Certificate of Analysis' if 'COA' in col else
                'Batch identification' if 'Batch' in col else
                'Production date' if 'Production' in col else
                'Expiration date' if 'Expiration' in col else
                'Terpene information' if 'Terpene' in col else
                'Flavor characteristics' if 'Flavor' in col else
                'Product effects' if 'Effects' in col else
                'Packaging details' if 'Package' in col else
                'Storage requirements' if 'Storage' in col else
                'Compliance information' if 'Compliance' in col else
                'Inventory tracking' if 'SKU' in col or 'Code' in col else
                'Product categorization' if 'Category' in col else
                'Growing methodology' if 'Growing' in col else
                'Organic certification' if 'Organic' in col else
                'Marketing information' if 'Marketing' in col else
                'Usage instructions' if 'Usage' in col else
                'Safety warnings' if 'Warning' in col else
                'General product information' for col in comprehensive_columns
            ]
        })
        
        schema_df.to_excel(writer, sheet_name='Schema', index=False)
    
    print(f"✅ Comprehensive product database created: {filename}")
    print(f"📊 Total columns: {len(comprehensive_columns)}")
    print(f"📝 Sample products: {len(sample_data)}")
    
    # Print column categories
    print("\n📋 Column Categories:")
    categories = {
        'Core Product Information': [col for col in comprehensive_columns[:8]],
        'Weight and Quantity': [col for col in comprehensive_columns[8:12]],
        'Pricing': [col for col in comprehensive_columns[12:14]],
        'Compliance and Testing': [col for col in comprehensive_columns[14:16]],
        'Product Classification': [col for col in comprehensive_columns[16:21]],
        'THC/CBD Content': [col for col in comprehensive_columns[21:29]],
        'Testing and Lab Information': [col for col in comprehensive_columns[29:37]],
        'Additional Product Details': [col for col in comprehensive_columns[37:45]],
        'Packaging and Storage': [col for col in comprehensive_columns[45:53]],
        'Regulatory and Compliance': [col for col in comprehensive_columns[53:61]],
        'Inventory and Tracking': [col for col in comprehensive_columns[61:69]],
        'Supplier and Sourcing': [col for col in comprehensive_columns[69:77]],
        'Marketing and Sales': [col for col in comprehensive_columns[77:85]]
    }
    
    for category, cols in categories.items():
        print(f"  • {category}: {len(cols)} columns")
    
    return filename

def update_existing_database():
    """Update an existing database to include missing columns."""
    
    # Check if there's an existing database file
    data_dir = 'data'
    if os.path.exists(data_dir):
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]
        if excel_files:
            print(f"📁 Found existing database files: {excel_files}")
            
            # Load the first Excel file
            file_path = os.path.join(data_dir, excel_files[0])
            try:
                df = pd.read_excel(file_path)
                print(f"✅ Loaded existing database: {len(df)} rows, {len(df.columns)} columns")
                
                # Get the comprehensive column list
                comprehensive_columns = [
                    # Core Product Information
                    'Product Name*', 'ProductName', 'Description',
                    'Product Type*', 'Lineage', 'Product Brand', 'Vendor/Supplier*',
                    
                    # Weight and Quantity
                    'Weight*', 'Weight Unit* (grams/gm or ounces/oz)', 'Units',
                    'Quantity*', 'Quantity Received*', 'Quantity', 'qty',
                    
                    # Pricing
                    'Price* (Tier Name for Bulk)', 'Price',
                    
                    # Compliance and Testing
                    'DOH Compliant (Yes/No)', 'DOH',
                    
                    # Product Classification
                    'Concentrate Type', 'Ratio',
                    'Joint Ratio', 'JointRatio',
                    'Product Strain',
                    
                    # THC/CBD Content (Critical for labeling)
                    'THC Content', 'THC', 'THC %', 'THC_Percentage',
                    'CBD Content', 'CBD', 'CBD %', 'CBD_Percentage',
                    'THC_CBD', 'THC_CBD_Content', 'Cannabinoid_Content',
                    'Total THC', 'Total CBD', 'Active THC', 'Active CBD',
                    
                    # Testing and Lab Information
                    'Lab Test Date', 'Test Date', 'Testing Date',
                    'Lab Name', 'Laboratory', 'Testing Lab',
                    'Certificate of Analysis', 'COA', 'Test Results',
                    'Batch Number', 'Lot Number', 'Production Date',
                    'Expiration Date', 'Shelf Life',
                    
                    # Additional Product Details
                    'Terpenes', 'Terpene Profile', 'Terpene Content',
                    'Flavor Profile', 'Aroma', 'Taste',
                    'Effects', 'Experience', 'High Type',
                    'Medical Benefits', 'Therapeutic Effects',
                    
                    # Packaging and Storage
                    'Package Size', 'Container Type', 'Packaging',
                    'Storage Instructions', 'Storage Requirements',
                    'Serving Size', 'Dosage Instructions',
                    
                    # Regulatory and Compliance
                    'State Compliance', 'Local Compliance', 'County Compliance',
                    'Testing Requirements', 'Compliance Notes',
                    'Warning Labels', 'Required Disclaimers',
                    
                    # Inventory and Tracking
                    'SKU', 'Product Code', 'Internal ID',
                    'Category', 'Subcategory', 'Product Family',
                    'Seasonal', 'Limited Edition', 'Discontinued',
                    
                    # Supplier and Sourcing
                    'Supplier Contact', 'Supplier Email', 'Supplier Phone',
                    'Country of Origin', 'Growing Method', 'Organic Status',
                    'Certifications', 'Quality Grade', 'Premium Tier',
                    
                    # Marketing and Sales
                    'Marketing Description', 'Sales Notes', 'Promotional Text',
                    'Target Audience', 'Recommended Use', 'Usage Instructions',
                    'Warnings', 'Side Effects', 'Contraindications'
                ]
                
                # Add missing columns
                missing_columns = [col for col in comprehensive_columns if col not in df.columns]
                if missing_columns:
                    print(f"🔧 Adding {len(missing_columns)} missing columns...")
                    for col in missing_columns:
                        df[col] = ''  # Initialize with empty values
                    
                    # Save updated database
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    updated_filename = f'updated_database_{timestamp}.xlsx'
                    df.to_excel(updated_filename, index=False)
                    print(f"✅ Updated database saved: {updated_filename}")
                    print(f"📊 New total columns: {len(df.columns)}")
                else:
                    print("✅ Database already has all necessary columns!")
                
            except Exception as e:
                print(f"❌ Error updating existing database: {e}")
        else:
            print("📁 No existing database files found in data directory")
    else:
        print("📁 No data directory found")

if __name__ == "__main__":
    print("🚀 Product Database Column Enhancement Tool")
    print("=" * 50)
    
    # Create comprehensive schema
    filename = create_comprehensive_schema()
    
    print("\n" + "=" * 50)
    
    # Update existing database if available
    update_existing_database()
    
    print("\n🎯 Next Steps:")
    print("1. Use the comprehensive database template for new products")
    print("2. Import existing data into the new schema")
    print("3. Update your ExcelProcessor to recognize all columns")
    print("4. Test the database with the Label Maker application")
