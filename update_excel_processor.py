#!/usr/bin/env python3
"""
Script to update the ExcelProcessor with comprehensive column definitions.
This ensures all necessary columns are recognized and processed correctly.
"""

import re
import os

def update_excel_processor_columns():
    """Update the ExcelProcessor with comprehensive column definitions."""
    
    excel_processor_file = 'src/core/data/excel_processor.py'
    
    if not os.path.exists(excel_processor_file):
        print(f"❌ ExcelProcessor file not found: {excel_processor_file}")
        return False
    
    # Read the current file
    with open(excel_processor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the comprehensive columns list
    comprehensive_columns = '''            # Keep all columns but ensure required ones exist
            required_columns = [
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
            ]'''
    
    # Find and replace the first required_columns definition
    pattern = r'# Keep all columns but ensure required ones exist\s+required_columns = \[.*?\]'
    
    if re.search(pattern, content, re.DOTALL):
        # Replace the existing definition
        updated_content = re.sub(pattern, comprehensive_columns, content, flags=re.DOTALL)
        
        # Write the updated content back
        with open(excel_processor_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated ExcelProcessor with comprehensive columns")
        print(f"📊 Total columns now supported: 104")
        return True
    else:
        print("❌ Could not find the required_columns definition to replace")
        return False

def add_column_processing_functions():
    """Add functions to process the new comprehensive columns."""
    
    excel_processor_file = 'src/core/data/excel_processor.py'
    
    if not os.path.exists(excel_processor_file):
        print(f"❌ ExcelProcessor file not found: {excel_processor_file}")
        return False
    
    # Read the current file
    with open(excel_processor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the new processing functions
    new_functions = '''
    def process_thc_cbd_columns(self, df):
        """Process and standardize THC/CBD content columns."""
        try:
            # Standardize THC content
            thc_columns = ['THC Content', 'THC', 'THC %', 'THC_Percentage']
            for col in thc_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace('%', '').str.strip()
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Standardize CBD content
            cbd_columns = ['CBD Content', 'CBD', 'CBD %', 'CBD_Percentage']
            for col in cbd_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace('%', '').str.strip()
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Create combined THC_CBD column if not exists
            if 'THC_CBD' not in df.columns:
                df['THC_CBD'] = ''
            
            # Populate combined column
            for idx, row in df.iterrows():
                thc_val = None
                cbd_val = None
                
                # Find THC value
                for col in thc_columns:
                    if col in df.columns and pd.notna(row[col]):
                        thc_val = row[col]
                        break
                
                # Find CBD value
                for col in cbd_columns:
                    if col in df.columns and pd.notna(row[col]):
                        cbd_val = row[col]
                        break
                
                # Format combined value
                if thc_val is not None and cbd_val is not None:
                    df.at[idx, 'THC_CBD'] = f"{thc_val}% THC / {cbd_val}% CBD"
                elif thc_val is not None:
                    df.at[idx, 'THC_CBD'] = f"{thc_val}% THC"
                elif cbd_val is not None:
                    df.at[idx, 'THC_CBD'] = f"{cbd_val}% CBD"
            
            self.logger.info("THC/CBD columns processed and standardized")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing THC/CBD columns: {e}")
            return df
    
    def process_testing_columns(self, df):
        """Process testing and lab information columns."""
        try:
            # Standardize date columns
            date_columns = ['Lab Test Date', 'Test Date', 'Testing Date', 'Production Date', 'Expiration Date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Ensure batch/lot number columns exist
            if 'Batch Number' not in df.columns:
                df['Batch Number'] = ''
            if 'Lot Number' not in df.columns:
                df['Lot Number'] = ''
            
            self.logger.info("Testing columns processed")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing testing columns: {e}")
            return df
    
    def process_product_details_columns(self, df):
        """Process additional product detail columns."""
        try:
            # Ensure terpene columns exist
            if 'Terpenes' not in df.columns:
                df['Terpenes'] = ''
            if 'Terpene Profile' not in df.columns:
                df['Terpene Profile'] = ''
            
            # Ensure effects columns exist
            if 'Effects' not in df.columns:
                df['Effects'] = ''
            if 'Experience' not in df.columns:
                df['Experience'] = ''
            
            # Ensure flavor columns exist
            if 'Flavor Profile' not in df.columns:
                df['Flavor Profile'] = ''
            if 'Aroma' not in df.columns:
                df['Aroma'] = ''
            
            self.logger.info("Product detail columns processed")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing product detail columns: {e}")
            return df
    
    def process_inventory_columns(self, df):
        """Process inventory and tracking columns."""
        try:
            # Ensure SKU and tracking columns exist
            if 'SKU' not in df.columns:
                df['SKU'] = ''
            if 'Product Code' not in df.columns:
                df['Product Code'] = ''
            if 'Internal ID' not in df.columns:
                df['Internal ID'] = ''
            
            # Ensure category columns exist
            if 'Category' not in df.columns:
                df['Category'] = ''
            if 'Subcategory' not in df.columns:
                df['Subcategory'] = ''
            
            self.logger.info("Inventory columns processed")
            return df
            
        except Exception as e:
            self.logger.error(f"Error processing inventory columns: {e}")
            return df'''
    
    # Find a good place to insert the new functions (after the existing methods)
    if 'def process_thc_cbd_columns(self, df):' not in content:
        # Insert after the last method in the class
        insert_pattern = r'(def __init__\(self.*?\):.*?)(\n\s*def|\n\s*class|\n\s*$)'
        match = re.search(insert_pattern, content, re.DOTALL)
        
        if match:
            # Insert the new functions
            updated_content = content.replace(match.group(1), match.group(1) + new_functions)
            
            # Write the updated content back
            with open(excel_processor_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Added new column processing functions to ExcelProcessor")
            return True
        else:
            print("❌ Could not find a suitable location to insert new functions")
            return False
    else:
        print("✅ Column processing functions already exist")
        return True

def main():
    """Main function to update the ExcelProcessor."""
    print("🔧 Updating ExcelProcessor with Comprehensive Columns")
    print("=" * 60)
    
    # Update the required columns list
    success1 = update_excel_processor_columns()
    
    print("\n" + "=" * 60)
    
    # Add new processing functions
    success2 = add_column_processing_functions()
    
    print("\n" + "=" * 60)
    
    if success1 and success2:
        print("🎉 ExcelProcessor successfully updated!")
        print("\n📋 What was added:")
        print("  • 104 comprehensive product database columns")
        print("  • THC/CBD content processing functions")
        print("  • Testing and lab information processing")
        print("  • Product detail processing functions")
        print("  • Inventory and tracking column support")
        print("\n🚀 Next steps:")
        print("1. Restart your Label Maker application")
        print("2. Import the comprehensive database template")
        print("3. Test the new columns with your products")
    else:
        print("❌ Some updates failed. Check the error messages above.")

if __name__ == "__main__":
    main()
