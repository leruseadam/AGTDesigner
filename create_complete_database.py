#!/usr/bin/env python3
"""
Script to create a complete product database with all necessary columns properly populated.
This addresses the issue of having too many empty placeholder columns.
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import random

def create_complete_database():
    """Create a complete product database with all 104 columns properly populated."""
    
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
    
    # Sample data for realistic products
    sample_products = [
        {
            'Product Name*': 'Blue Dream',
            'ProductName': 'Blue Dream',
            'Description': 'A balanced hybrid with sweet berry aroma and uplifting effects',
            'Product Type*': 'flower',
            'Lineage': 'HYBRID',
            'Product Brand': 'Premium Cannabis Co',
            'Vendor/Supplier*': 'Blue Sky Farms',
            'Weight*': '3.5',
            'Weight Unit* (grams/gm or ounces/oz)': 'grams',
            'Units': 'grams',
            'Quantity*': '100',
            'Quantity Received*': '100',
            'Quantity': '100',
            'qty': '100',
            'Price* (Tier Name for Bulk)': 'Tier 1',
            'Price': '45.00',
            'DOH Compliant (Yes/No)': 'Yes',
            'DOH': 'Yes',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'JointRatio': 'N/A',
            'Product Strain': 'Blue Dream',
            'THC Content': '18.5',
            'THC': '18.5',
            'THC %': '18.5',
            'THC_Percentage': '18.5',
            'CBD Content': '0.5',
            'CBD': '0.5',
            'CBD %': '0.5',
            'CBD_Percentage': '0.5',
            'THC_CBD': '18.5% THC / 0.5% CBD',
            'THC_CBD_Content': '18.5% THC / 0.5% CBD',
            'Cannabinoid_Content': '19.0%',
            'Total THC': '18.5',
            'Total CBD': '0.5',
            'Active THC': '18.5',
            'Active CBD': '0.5',
            'Lab Test Date': '2024-08-15',
            'Test Date': '2024-08-15',
            'Testing Date': '2024-08-15',
            'Lab Name': 'Green Leaf Labs',
            'Laboratory': 'Green Leaf Labs',
            'Testing Lab': 'Green Leaf Labs',
            'Certificate of Analysis': 'COA-2024-0815-001',
            'COA': 'COA-2024-0815-001',
            'Test Results': 'Passed',
            'Batch Number': 'BATCH-2024-0815-001',
            'Lot Number': 'LOT-2024-0815-001',
            'Production Date': '2024-08-01',
            'Expiration Date': '2025-08-01',
            'Shelf Life': '12 months',
            'Terpenes': 'Myrcene, Limonene, Pinene',
            'Terpene Profile': 'Myrcene: 0.8%, Limonene: 0.6%, Pinene: 0.4%',
            'Terpene Content': '1.8%',
            'Flavor Profile': 'Sweet, Berry, Citrus',
            'Aroma': 'Sweet berry with citrus undertones',
            'Taste': 'Smooth, sweet berry flavor',
            'Effects': 'Uplifting, Creative, Focused',
            'Experience': 'Balanced high with clear-headed euphoria',
            'High Type': 'Hybrid',
            'Medical Benefits': 'Stress relief, mood enhancement, pain management',
            'Therapeutic Effects': 'Anti-anxiety, anti-inflammatory',
            'Package Size': '3.5g',
            'Container Type': 'Glass jar',
            'Packaging': 'Child-resistant glass jar with tamper seal',
            'Storage Instructions': 'Store in cool, dark place',
            'Storage Requirements': 'Temperature: 60-70°F, Humidity: 58-62%',
            'Serving Size': '0.1g',
            'Dosage Instructions': 'Start with small amounts, wait 15 minutes',
            'State Compliance': 'CA Compliant',
            'Local Compliance': 'Local regulations followed',
            'County Compliance': 'County compliant',
            'Testing Requirements': 'Full panel testing completed',
            'Compliance Notes': 'All testing requirements met',
            'Warning Labels': 'For adults 21+, Keep out of reach of children',
            'Required Disclaimers': 'This product has not been evaluated by FDA',
            'SKU': 'BD-3.5G-001',
            'Product Code': 'BD001',
            'Internal ID': 'INT-001',
            'Category': 'Flower',
            'Subcategory': 'Hybrid',
            'Product Family': 'Premium Flower',
            'Seasonal': 'Year-round',
            'Limited Edition': 'No',
            'Discontinued': 'No',
            'Supplier Contact': 'John Smith',
            'Supplier Email': 'john@blueskyfarms.com',
            'Supplier Phone': '(555) 123-4567',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic',
            'Certifications': 'USDA Organic, Clean Green Certified',
            'Quality Grade': 'Premium',
            'Premium Tier': 'Tier 1',
            'Marketing Description': 'Premium Blue Dream hybrid with exceptional quality',
            'Sales Notes': 'High demand, premium pricing justified',
            'Promotional Text': 'Experience the legendary Blue Dream',
            'Target Audience': 'Adult cannabis consumers 21+',
            'Recommended Use': 'Evening use for relaxation and creativity',
            'Usage Instructions': 'Grind and consume as preferred method',
            'Warnings': 'May cause drowsiness, do not drive under influence',
            'Side Effects': 'Dry mouth, dry eyes, increased appetite',
            'Contraindications': 'Not recommended for pregnant women'
        },
        {
            'Product Name*': 'Gelato',
            'ProductName': 'Gelato',
            'Description': 'A sweet and potent hybrid with dessert-like aroma',
            'Product Type*': 'flower',
            'Lineage': 'HYBRID',
            'Product Brand': 'Premium Cannabis Co',
            'Vendor/Supplier*': 'Green Valley Farms',
            'Weight*': '7.0',
            'Weight Unit* (grams/gm or ounces/oz)': 'grams',
            'Units': 'grams',
            'Quantity*': '50',
            'Quantity Received*': '50',
            'Quantity': '50',
            'qty': '50',
            'Price* (Tier Name for Bulk)': 'Tier 1',
            'Price': '85.00',
            'DOH Compliant (Yes/No)': 'Yes',
            'DOH': 'Yes',
            'Concentrate Type': 'flower',
            'Ratio': 'N/A',
            'Joint Ratio': 'N/A',
            'JointRatio': 'N/A',
            'Product Strain': 'Gelato',
            'THC Content': '22.0',
            'THC': '22.0',
            'THC %': '22.0',
            'THC_Percentage': '22.0',
            'CBD Content': '0.3',
            'CBD': '0.3',
            'CBD %': '0.3',
            'CBD_Percentage': '0.3',
            'THC_CBD': '22.0% THC / 0.3% CBD',
            'THC_CBD_Content': '22.0% THC / 0.3% CBD',
            'Cannabinoid_Content': '22.3%',
            'Total THC': '22.0',
            'Total CBD': '0.3',
            'Active THC': '22.0',
            'Active CBD': '0.3',
            'Lab Test Date': '2024-08-18',
            'Test Date': '2024-08-18',
            'Testing Date': '2024-08-18',
            'Lab Name': 'Cannabis Testing Lab',
            'Laboratory': 'Cannabis Testing Lab',
            'Testing Lab': 'Cannabis Testing Lab',
            'Certificate of Analysis': 'COA-2024-0818-002',
            'COA': 'COA-2024-0818-002',
            'Test Results': 'Passed',
            'Batch Number': 'BATCH-2024-0818-002',
            'Lot Number': 'LOT-2024-0818-002',
            'Production Date': '2024-08-05',
            'Expiration Date': '2025-08-05',
            'Shelf Life': '12 months',
            'Terpenes': 'Linalool, Caryophyllene, Limonene',
            'Terpene Profile': 'Linalool: 1.2%, Caryophyllene: 0.8%, Limonene: 0.5%',
            'Terpene Content': '2.5%',
            'Flavor Profile': 'Sweet, Creamy, Citrus',
            'Aroma': 'Sweet dessert with citrus notes',
            'Taste': 'Rich, creamy gelato flavor',
            'Effects': 'Euphoric, Relaxing, Happy',
            'Experience': 'Strong euphoria with body relaxation',
            'High Type': 'Hybrid',
            'Medical Benefits': 'Pain relief, stress reduction, mood elevation',
            'Therapeutic Effects': 'Analgesic, anxiolytic, antidepressant',
            'Package Size': '7g',
            'Container Type': 'Glass jar',
            'Packaging': 'Child-resistant glass jar with tamper seal',
            'Storage Instructions': 'Store in cool, dark place',
            'Storage Requirements': 'Temperature: 60-70°F, Humidity: 58-62%',
            'Serving Size': '0.1g',
            'Dosage Instructions': 'Start with small amounts, wait 15 minutes',
            'State Compliance': 'CA Compliant',
            'Local Compliance': 'Local regulations followed',
            'County Compliance': 'County compliant',
            'Testing Requirements': 'Full panel testing completed',
            'Compliance Notes': 'All testing requirements met',
            'Warning Labels': 'For adults 21+, Keep out of reach of children',
            'Required Disclaimers': 'This product has not been evaluated by FDA',
            'SKU': 'GL-7G-002',
            'Product Code': 'GL002',
            'Internal ID': 'INT-002',
            'Category': 'Flower',
            'Subcategory': 'Hybrid',
            'Product Family': 'Premium Flower',
            'Seasonal': 'Year-round',
            'Limited Edition': 'No',
            'Discontinued': 'No',
            'Supplier Contact': 'Sarah Johnson',
            'Supplier Email': 'sarah@greenvalleyfarms.com',
            'Supplier Phone': '(555) 987-6543',
            'Country of Origin': 'USA',
            'Growing Method': 'Indoor',
            'Organic Status': 'Organic',
            'Certifications': 'USDA Organic, Clean Green Certified',
            'Quality Grade': 'Premium',
            'Premium Tier': 'Tier 1',
            'Marketing Description': 'Premium Gelato hybrid with exceptional potency',
            'Sales Notes': 'High potency, premium pricing justified',
            'Promotional Text': 'Experience the sweet sensation of Gelato',
            'Target Audience': 'Adult cannabis consumers 21+',
            'Recommended Use': 'Evening use for relaxation and euphoria',
            'Usage Instructions': 'Grind and consume as preferred method',
            'Warnings': 'High THC content, start with small amounts',
            'Side Effects': 'Dry mouth, dry eyes, increased appetite',
            'Contraindications': 'Not recommended for novice users'
        },
        {
            'Product Name*': 'CBD Relief Tincture',
            'ProductName': 'CBD Relief Tincture',
            'Description': 'Full-spectrum CBD tincture for pain relief and relaxation',
            'Product Type*': 'tincture',
            'Lineage': 'CBD',
            'Product Brand': 'Wellness Solutions',
            'Vendor/Supplier*': 'CBD Wellness Co',
            'Weight*': '30',
            'Weight Unit* (grams/gm or ounces/oz)': 'ml',
            'Units': 'ml',
            'Quantity*': '75',
            'Quantity Received*': '75',
            'Quantity': '75',
            'qty': '75',
            'Price* (Tier Name for Bulk)': 'Tier 2',
            'Price': '65.00',
            'DOH Compliant (Yes/No)': 'Yes',
            'DOH': 'Yes',
            'Concentrate Type': 'tincture',
            'Ratio': '30:1 CBD:THC',
            'Joint Ratio': 'N/A',
            'JointRatio': 'N/A',
            'Product Strain': 'CBD Hemp',
            'THC Content': '0.3',
            'THC': '0.3',
            'THC %': '0.3',
            'THC_Percentage': '0.3',
            'CBD Content': '900',
            'CBD': '900',
            'CBD %': '900',
            'CBD_Percentage': '900',
            'THC_CBD': '0.3% THC / 900mg CBD',
            'THC_CBD_Content': '0.3% THC / 900mg CBD',
            'Cannabinoid_Content': '900.3mg',
            'Total THC': '0.3',
            'Total CBD': '900',
            'Active THC': '0.3',
            'Active CBD': '900',
            'Lab Test Date': '2024-08-20',
            'Test Date': '2024-08-20',
            'Testing Date': '2024-08-20',
            'Lab Name': 'Hemp Testing Lab',
            'Laboratory': 'Hemp Testing Lab',
            'Testing Lab': 'Hemp Testing Lab',
            'Certificate of Analysis': 'COA-2024-0820-003',
            'COA': 'COA-2024-0820-003',
            'Test Results': 'Passed',
            'Batch Number': 'BATCH-2024-0820-003',
            'Lot Number': 'LOT-2024-0820-003',
            'Production Date': '2024-08-10',
            'Expiration Date': '2026-08-10',
            'Shelf Life': '24 months',
            'Terpenes': 'Myrcene, Beta-Caryophyllene, Linalool',
            'Terpene Profile': 'Myrcene: 0.5%, Beta-Caryophyllene: 0.4%, Linalool: 0.3%',
            'Terpene Content': '1.2%',
            'Flavor Profile': 'Natural, Herbal, Mint',
            'Aroma': 'Natural hemp with mint undertones',
            'Taste': 'Smooth, natural hemp flavor',
            'Effects': 'Calming, Pain Relief, Relaxation',
            'Experience': 'Gentle relaxation without psychoactive effects',
            'High Type': 'Non-psychoactive',
            'Medical Benefits': 'Pain relief, anxiety reduction, sleep aid',
            'Therapeutic Effects': 'Analgesic, anxiolytic, sedative',
            'Package Size': '30ml',
            'Container Type': 'Glass dropper bottle',
            'Packaging': 'Child-resistant glass bottle with dropper',
            'Storage Instructions': 'Store in cool, dark place',
            'Storage Requirements': 'Temperature: 60-70°F, avoid direct sunlight',
            'Serving Size': '1ml',
            'Dosage Instructions': 'Start with 0.5ml, increase as needed',
            'State Compliance': 'CA Compliant',
            'Local Compliance': 'Local regulations followed',
            'County Compliance': 'County compliant',
            'Testing Requirements': 'Full panel testing completed',
            'Compliance Notes': 'All testing requirements met',
            'Warning Labels': 'For adults 21+, Keep out of reach of children',
            'Required Disclaimers': 'This product has not been evaluated by FDA',
            'SKU': 'CBD-TINCT-30ML-003',
            'Product Code': 'CBD003',
            'Internal ID': 'INT-003',
            'Category': 'Tincture',
            'Subcategory': 'CBD',
            'Product Family': 'Wellness Products',
            'Seasonal': 'Year-round',
            'Limited Edition': 'No',
            'Discontinued': 'No',
            'Supplier Contact': 'Mike Davis',
            'Supplier Email': 'mike@cbdwellnessco.com',
            'Supplier Phone': '(555) 456-7890',
            'Country of Origin': 'USA',
            'Growing Method': 'Outdoor',
            'Organic Status': 'Organic',
            'Certifications': 'USDA Organic, Non-GMO Project',
            'Quality Grade': 'Premium',
            'Premium Tier': 'Tier 2',
            'Marketing Description': 'Premium CBD tincture for natural relief',
            'Sales Notes': 'Growing market, competitive pricing',
            'Promotional Text': 'Natural relief without the high',
            'Target Audience': 'Adults seeking natural wellness solutions',
            'Recommended Use': 'Daily use for wellness support',
            'Usage Instructions': 'Place under tongue, hold for 30 seconds',
            'Warnings': 'Consult healthcare provider if pregnant or nursing',
            'Side Effects': 'Generally well-tolerated, rare drowsiness',
            'Contraindications': 'Consult doctor if taking medications'
        }
    ]
    
    # Create DataFrame with all columns
    df = pd.DataFrame(sample_products)
    
    # Ensure all columns exist (fill missing ones with empty strings)
    for col in comprehensive_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns to match the comprehensive list
    df = df[comprehensive_columns]
    
    # Save to Excel file with proper formatting
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'AGT_Complete_Product_Database_{timestamp}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Write the main products sheet
        df.to_excel(writer, sheet_name='Products', index=False)
        
        # Create a schema documentation sheet
        schema_data = []
        for col in comprehensive_columns:
            required = 'Yes' if '*' in col else 'No'
            data_type = 'Text'
            if 'Date' in col:
                data_type = 'Date'
            elif any(x in col for x in ['THC', 'CBD', 'Weight', 'Price', 'Quantity']):
                data_type = 'Number'
            elif col in ['DOH Compliant (Yes/No)', 'Organic Status']:
                data_type = 'Yes/No'
            
            description = get_column_description(col)
            schema_data.append([col, required, data_type, description])
        
        schema_df = pd.DataFrame(schema_data, columns=['Column Name', 'Required', 'Data Type', 'Description'])
        schema_df.to_excel(writer, sheet_name='Schema', index=False)
        
        # Create a sample data sheet
        sample_df = pd.DataFrame({
            'Column Name': comprehensive_columns,
            'Sample Value': [
                'Blue Dream' if 'Product Name' in col else
                'flower' if 'Product Type' in col else
                'HYBRID' if 'Lineage' in col else
                'Premium Cannabis Co' if 'Brand' in col else
                'Blue Sky Farms' if 'Vendor' in col else
                '3.5' if 'Weight' in col and '*' in col else
                'grams' if 'Unit' in col else
                '100' if 'Quantity' in col and '*' in col else
                'Tier 1' if 'Price' in col and 'Tier' in col else
                '45.00' if 'Price' in col and 'Tier' not in col else
                'Yes' if 'DOH' in col else
                '18.5' if 'THC' in col and 'CBD' not in col else
                '0.5' if 'CBD' in col and 'THC' not in col else
                '18.5% THC / 0.5% CBD' if 'THC_CBD' in col else
                '2024-08-15' if 'Date' in col else
                'Green Leaf Labs' if 'Lab' in col else
                'COA-2024-0815-001' if 'COA' in col else
                'BATCH-2024-0815-001' if 'Batch' in col else
                'Myrcene, Limonene, Pinene' if 'Terpene' in col else
                'Sweet, Berry, Citrus' if 'Flavor' in col else
                'Uplifting, Creative' if 'Effects' in col else
                '3.5g' if 'Package' in col else
                'Glass jar' if 'Container' in col else
                'Store in cool, dark place' if 'Storage' in col else
                'CA Compliant' if 'Compliance' in col else
                'BD-3.5G-001' if 'SKU' in col else
                'Flower' if 'Category' in col else
                'John Smith' if 'Contact' in col else
                'USA' if 'Origin' in col else
                'Indoor' if 'Growing' in col else
                'Organic' if 'Organic' in col else
                'Premium quality product' if 'Marketing' in col else
                'Evening use recommended' if 'Recommended' in col else
                'Start with small amounts' if 'Usage' in col else
                'May cause drowsiness' if 'Warning' in col else
                'Dry mouth, dry eyes' if 'Side Effects' in col else
                'Consult doctor if pregnant' if 'Contraindications' in col else
                'Sample data for reference' for col in comprehensive_columns
            ]
        })
        sample_df.to_excel(writer, sheet_name='Sample Data', index=False)
    
    print(f"✅ Complete product database created: {filename}")
    print(f"📊 Total columns: {len(comprehensive_columns)}")
    print(f"📝 Sample products: {len(sample_products)}")
    print(f"📋 Sheets created: Products, Schema, Sample Data")
    
    return filename

def get_column_description(column_name):
    """Get a description for each column."""
    descriptions = {
        'Product Name*': 'Core product identifier (required)',
        'ProductName': 'Alternative product name field',
        'Description': 'Detailed product description',
        'Product Type*': 'Product category classification (required)',
        'Lineage': 'Cannabis lineage/type (SATIVA/INDICA/HYBRID/CBD)',
        'Product Brand': 'Brand name of the product',
        'Vendor/Supplier*': 'Supplier information (required)',
        'Weight*': 'Product weight (required)',
        'Weight Unit* (grams/gm or ounces/oz)': 'Weight measurement unit (required)',
        'Units': 'Alternative weight unit field',
        'Quantity*': 'Product quantity (required)',
        'Quantity Received*': 'Quantity received from supplier',
        'Quantity': 'Alternative quantity field',
        'qty': 'Abbreviated quantity field',
        'Price* (Tier Name for Bulk)': 'Pricing tier for bulk orders (required)',
        'Price': 'Product price',
        'DOH Compliant (Yes/No)': 'DOH compliance status (required)',
        'DOH': 'Alternative DOH compliance field',
        'Concentrate Type': 'Type of concentrate (if applicable)',
        'Ratio': 'THC/CBD ratio information',
        'Joint Ratio': 'Joint-specific ratio information',
        'JointRatio': 'Alternative joint ratio field',
        'Product Strain': 'Specific strain name',
        'THC Content': 'THC content percentage',
        'THC': 'Alternative THC content field',
        'THC %': 'THC percentage field',
        'THC_Percentage': 'Alternative THC percentage field',
        'CBD Content': 'CBD content percentage',
        'CBD': 'Alternative CBD content field',
        'CBD %': 'CBD percentage field',
        'CBD_Percentage': 'Alternative CBD percentage field',
        'THC_CBD': 'Combined THC/CBD content display',
        'THC_CBD_Content': 'Alternative combined content field',
        'Cannabinoid_Content': 'Total cannabinoid content',
        'Total THC': 'Total THC content (including THCA)',
        'Total CBD': 'Total CBD content (including CBDA)',
        'Active THC': 'Active THC content (decarboxylated)',
        'Active CBD': 'Active CBD content (decarboxylated)',
        'Lab Test Date': 'Date of laboratory testing',
        'Test Date': 'Alternative test date field',
        'Testing Date': 'Alternative testing date field',
        'Lab Name': 'Name of testing laboratory',
        'Laboratory': 'Alternative laboratory field',
        'Testing Lab': 'Alternative testing lab field',
        'Certificate of Analysis': 'COA document reference',
        'COA': 'Alternative COA field',
        'Test Results': 'Laboratory test results',
        'Batch Number': 'Production batch identification',
        'Lot Number': 'Lot identification number',
        'Production Date': 'Date of production',
        'Expiration Date': 'Product expiration date',
        'Shelf Life': 'Product shelf life duration',
        'Terpenes': 'Terpene profile information',
        'Terpene Profile': 'Detailed terpene analysis',
        'Terpene Content': 'Total terpene content',
        'Flavor Profile': 'Product flavor characteristics',
        'Aroma': 'Product aroma description',
        'Taste': 'Product taste description',
        'Effects': 'Product effects description',
        'Experience': 'User experience description',
        'High Type': 'Type of high/effect',
        'Medical Benefits': 'Medical benefit claims',
        'Therapeutic Effects': 'Therapeutic effect descriptions',
        'Package Size': 'Product package size',
        'Container Type': 'Type of container',
        'Packaging': 'Packaging description',
        'Storage Instructions': 'Storage instructions',
        'Storage Requirements': 'Specific storage requirements',
        'Serving Size': 'Recommended serving size',
        'Dosage Instructions': 'Dosage instructions',
        'State Compliance': 'State compliance status',
        'Local Compliance': 'Local compliance status',
        'County Compliance': 'County compliance status',
        'Testing Requirements': 'Testing requirements',
        'Compliance Notes': 'Compliance notes and comments',
        'Warning Labels': 'Required warning labels',
        'Required Disclaimers': 'Required legal disclaimers',
        'SKU': 'Stock keeping unit',
        'Product Code': 'Internal product code',
        'Internal ID': 'Internal identification number',
        'Category': 'Product category',
        'Subcategory': 'Product subcategory',
        'Product Family': 'Product family grouping',
        'Seasonal': 'Seasonal availability',
        'Limited Edition': 'Limited edition status',
        'Discontinued': 'Discontinued product status',
        'Supplier Contact': 'Supplier contact person',
        'Supplier Email': 'Supplier email address',
        'Supplier Phone': 'Supplier phone number',
        'Country of Origin': 'Country of origin',
        'Growing Method': 'Growing method used',
        'Organic Status': 'Organic certification status',
        'Certifications': 'Product certifications',
        'Quality Grade': 'Product quality grade',
        'Premium Tier': 'Premium tier classification',
        'Marketing Description': 'Marketing description',
        'Sales Notes': 'Sales team notes',
        'Promotional Text': 'Promotional text content',
        'Target Audience': 'Target audience description',
        'Recommended Use': 'Recommended usage',
        'Usage Instructions': 'Detailed usage instructions',
        'Warnings': 'Product warnings',
        'Side Effects': 'Potential side effects',
        'Contraindications': 'Medical contraindications'
    }
    
    return descriptions.get(column_name, 'Product information field')

if __name__ == "__main__":
    print("🚀 Creating Complete Product Database")
    print("=" * 60)
    
    # Create the complete database
    filename = create_complete_database()
    
    print("\n🎯 Database Features:")
    print("  • 104 comprehensive columns (no more empty placeholders!)")
    print("  • 3 sample products with realistic data")
    print("  • Proper column headers and descriptions")
    print("  • Schema documentation sheet")
    print("  • Sample data reference sheet")
    
    print(f"\n📁 File saved as: {filename}")
    print("\n💡 Next Steps:")
    print("1. Open the Excel file and review all columns")
    print("2. Import this database into your Label Maker application")
    print("3. Add your actual product data to the appropriate columns")
    print("4. Use the Schema sheet to understand each column's purpose")
    print("5. The Sample Data sheet shows example values for reference")
