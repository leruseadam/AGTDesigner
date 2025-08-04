#!/usr/bin/env python3
"""
Script to fix duplicate labels issue in ExcelProcessor
"""

import re

def fix_duplicate_labels():
    """Fix the duplicate labels issue in excel_processor.py"""
    
    file_path = "src/core/data/excel_processor.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace the first occurrence (in fast_load_file method)
    pattern1 = r'(# Remove duplicates\n\s+initial_count = len\(df\)\n\s+df\.drop_duplicates\(inplace=True\)\n\s+final_count = len\(df\))'
    replacement1 = r'# Remove duplicates and reset index to avoid duplicate labels\n            initial_count = len(df)\n            df.drop_duplicates(inplace=True)\n            df.reset_index(drop=True, inplace=True)  # Reset index to avoid duplicate labels\n            final_count = len(df)'
    
    # Replace the second occurrence (in load_file method)
    pattern2 = r'(# Remove duplicates\n\s+initial_count = len\(df\)\n\s+df\.drop_duplicates\(inplace=True\)\n\s+final_count = len\(df\))'
    replacement2 = r'# Remove duplicates and reset index to avoid duplicate labels\n            initial_count = len(df)\n            df.drop_duplicates(inplace=True)\n            df.reset_index(drop=True, inplace=True)  # Reset index to avoid duplicate labels\n            final_count = len(df)'
    
    # Apply the first replacement
    content = re.sub(pattern1, replacement1, content, count=1)
    
    # Apply the second replacement
    content = re.sub(pattern2, replacement2, content, count=1)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed duplicate labels issue in ExcelProcessor")

if __name__ == "__main__":
    fix_duplicate_labels() 