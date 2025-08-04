#!/usr/bin/env python3
"""
Test script to mimic ExcelProcessor operations and find duplicate indices issue
"""

import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import EXCLUDED_PRODUCT_TYPES, EXCLUDED_PRODUCT_PATTERNS

def test_excel_processor_mimic():
    """Test that mimics ExcelProcessor operations to find duplicate indices issue"""
    
    print("Testing ExcelProcessor Operations Mimic")
    print("=" * 60)
    
    # Find the test file
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return False
    
    # Find the most recent Excel file
    excel_files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.xlsx') and 'A Greener Today' in file:
            file_path = os.path.join(uploads_dir, file)
            mtime = os.path.getmtime(file_path)
            excel_files.append((file_path, mtime))
    
    if not excel_files:
        print("❌ No Excel files found in uploads directory")
        return False
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x[1], reverse=True)
    test_file = excel_files[0][0]
    print(f"✅ Found test file: {test_file}")
    
    try:
        print(f"🔄 Reading file with pandas...")
        
        # Read the file like ExcelProcessor does
        dtype_dict = {
            "Product Type*": "string",
            "Lineage": "string",
            "Product Brand": "string",
            "Vendor": "string",
            "Weight Unit* (grams/gm or ounces/oz)": "string",
            "Product Name*": "string"
        }
        
        df = pd.read_excel(test_file, engine='openpyxl', dtype=dtype_dict)
        
        print(f"✅ File read successfully")
        print(f"📊 Initial DataFrame shape: {df.shape}")
        print(f"📊 Initial has duplicate indices: {df.index.duplicated().any()}")
        
        # Step 1: Remove duplicates and reset index
        print(f"\n🔄 Step 1: Remove duplicates and reset index...")
        initial_count = len(df)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        final_count = len(df)
        print(f"📊 After drop_duplicates: has duplicate indices: {df.index.duplicated().any()}")
        
        # Step 2: Assign to self.df (simulate ExcelProcessor)
        print(f"\n🔄 Step 2: Assign to self.df...")
        self_df = df
        self_df.reset_index(drop=True, inplace=True)
        print(f"📊 After assignment: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 3: Trim product names
        print(f"\n🔄 Step 3: Trim product names...")
        if "ProductName" in self_df.columns:
            self_df["Product Name*"] = self_df["ProductName"].str.lstrip()
        print(f"📊 After trimming: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 4: Ensure required columns exist
        print(f"\n🔄 Step 4: Ensure required columns exist...")
        for col in ["Product Type*", "Lineage", "Product Brand"]:
            if col not in self_df.columns:
                self_df[col] = "Unknown"
        print(f"📊 After ensuring columns: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 5: Determine product name column
        print(f"\n🔄 Step 5: Determine product name column...")
        product_name_col = 'Product Name*'
        if product_name_col not in self_df.columns:
            product_name_col = 'ProductName' if 'ProductName' in self_df.columns else None
        print(f"📊 Product name column: {product_name_col}")
        print(f"📊 After determining column: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 6: Exclude sample rows and deactivated products
        print(f"\n🔄 Step 6: Exclude sample rows...")
        initial_count = len(self_df)
        excluded_by_type = self_df[self_df["Product Type*"].isin(EXCLUDED_PRODUCT_TYPES)]
        self_df = self_df[~self_df["Product Type*"].isin(EXCLUDED_PRODUCT_TYPES)]
        self_df.reset_index(drop=True, inplace=True)
        print(f"📊 After excluding by type: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 7: Exclude products with excluded patterns
        print(f"\n🔄 Step 7: Exclude products with patterns...")
        for pattern in EXCLUDED_PRODUCT_PATTERNS:
            pattern_mask = self_df["Product Name*"].str.contains(pattern, case=False, na=False)
            excluded_by_pattern = self_df[pattern_mask]
            self_df = self_df[~pattern_mask]
            if len(excluded_by_pattern) > 0:
                print(f"📊 Excluded {len(excluded_by_pattern)} products containing pattern '{pattern}'")
        
        self_df.reset_index(drop=True, inplace=True)
        print(f"📊 After excluding patterns: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 8: Rename columns
        print(f"\n🔄 Step 8: Rename columns...")
        self_df.rename(columns={
            "Product Name*": "ProductName",
            "Weight Unit* (grams/gm or ounces/oz)": "Units",
            "Price* (Tier Name for Bulk)": "Price",
            "Vendor/Supplier*": "Vendor",
            "DOH Compliant (Yes/No)": "DOH",
            "Concentrate Type": "Ratio"
        }, inplace=True)
        print(f"📊 After renaming: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 9: Update product_name_col after renaming
        print(f"\n🔄 Step 9: Update product_name_col...")
        if product_name_col == 'Product Name*':
            product_name_col = 'ProductName'
        print(f"📊 Updated product name column: {product_name_col}")
        print(f"📊 After updating column: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 10: Normalize units
        print(f"\n🔄 Step 10: Normalize units...")
        if "Units" in self_df.columns:
            self_df["Units"] = self_df["Units"].str.lower().replace(
                {"ounces": "oz", "grams": "g"}, regex=True
            )
        print(f"📊 After normalizing units: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 11: Standardize Lineage
        print(f"\n🔄 Step 11: Standardize Lineage...")
        self_df.reset_index(drop=True, inplace=True)
        if "Lineage" in self_df.columns:
            print("📊 Starting lineage standardization process...")
            # First, standardize existing values
            self_df["Lineage"] = (
                self_df["Lineage"]
                .str.lower()
                .replace({
                    "indica_hybrid": "HYBRID/INDICA",
                    "sativa_hybrid": "HYBRID/SATIVA",
                    "sativa": "SATIVA",
                    "hybrid": "HYBRID",
                    "indica": "INDICA",
                    "cbd": "CBD"
                })
                .str.upper()
            )
        print(f"📊 After lineage standardization: has duplicate indices: {self_df.index.duplicated().any()}")
        
        # Step 12: Build Description and Ratio columns (this is where it fails)
        print(f"\n🔄 Step 12: Build Description and Ratio columns...")
        self_df.reset_index(drop=True, inplace=True)
        
        def get_description(name):
            if pd.isna(name) or name == "":
                return ""
            name = str(name).strip()
            if " - " in name:
                # Take all parts before the last hyphen
                return name.rsplit(' - ', 1)[0].strip()
            return name.strip()
        
        # Ensure Product Name* is string type before applying
        if product_name_col:
            # Reset index to avoid duplicate labels before applying operations
            self_df.reset_index(drop=True, inplace=True)
            self_df[product_name_col] = self_df[product_name_col].astype(str)
            print(f"📊 Before apply: has duplicate indices: {self_df.index.duplicated().any()}")
            
            # This is the operation that's failing
            self_df["Description"] = self_df[product_name_col].apply(get_description)
            print(f"📊 After apply: has duplicate indices: {self_df.index.duplicated().any()}")
            
            if self_df.index.duplicated().any():
                print(f"❌ Duplicate indices found after apply operation!")
                print(f"📊 Duplicate indices: {self_df.index[self_df.index.duplicated()].tolist()}")
                return False
            else:
                print(f"✅ No duplicate indices after apply operation")
        
        return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_excel_processor_mimic()
    
    if success:
        print("\n🎉 ExcelProcessor mimic test passed!")
        print("✅ No duplicate indices created during operations")
    else:
        print("\n❌ ExcelProcessor mimic test failed")
        print("⚠️  Duplicate indices were created during operations")
    
    print("=" * 60) 