#!/usr/bin/env python3
"""
Fix THC/CBD column names in Excel processor
"""

import re

def fix_thc_cbd_columns():
    """Fix the column names in the Excel processor to match the actual Excel data."""
    
    file_path = 'src/core/data/excel_processor.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the CBD column references
    # Replace 'CBD Content' with 'CBDA' and 'CBD test result'
    content = content.replace("str(record.get('CBD Content', '')).strip()", "str(record.get('CBDA', '')).strip()")
    
    # Also fix the comment
    content = content.replace("# Use CBD Content as test result", "# Use CBDA as content")
    content = content.replace("# Use CBD Content as fallback", "# Use CBDA as content")
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed THC/CBD column names in Excel processor")

if __name__ == "__main__":
    fix_thc_cbd_columns()
