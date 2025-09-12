#!/usr/bin/env python3
"""
Fix THC calculation in Excel processor
"""

import re

def fix_thc_calculation():
    """Fix the THC calculation in the Excel processor."""
    
    file_path = 'src/core/data/excel_processor.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the THC calculation to use THCA instead of THC Content
    # Replace 'THC Content' with 'THCA' in the THC calculation
    content = content.replace("str(record.get('THC Content', '')).strip()", "str(record.get('THCA', '')).strip()")
    
    # Also fix the comment
    content = content.replace("# Use THC Content as test result", "# Use THCA as test result")
    content = content.replace("# Use THC Content as fallback", "# Use THCA as fallback")
    
    # Write the file back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed THC calculation in Excel processor")

if __name__ == "__main__":
    fix_thc_calculation()
