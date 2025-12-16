#!/usr/bin/env python3
"""
DIAGNOSTIC: Check if 49 matches become 18 valid records
This will help us determine if it's a matching vs validation issue
"""

import os
import sys
import re

def analyze_matching_vs_validation():
    """Analyze if the issue is in matching or validation phase."""
    
    print("=" * 60)
    print("MATCHING vs VALIDATION ANALYSIS")
    print("=" * 60)
    
    # Read the app.py file to find validation logic
    app_path = "app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ app.py not found")
        return
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
        
        print("🔍 SEARCHING FOR VALIDATION LOGIC...")
        
        # Look for the validation section
        validation_patterns = [
            r'valid_selected_tags = \[\]',
            r'normalized_tags.*=',
            r'CRITICAL FIX:.*JSON matched session',
            r'Found.*tags in database',
            r'get_products_by_names'
        ]
        
        found_patterns = []
        for pattern in validation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                found_patterns.append(pattern)
                print(f"✅ Found pattern: {pattern}")
        
        if not found_patterns:
            print("❌ Could not find validation logic patterns")
            return
        
        # Look for the specific validation code
        validation_section = re.search(
            r'# Try to validate tags against database.*?valid_selected_tags = normalized_tags',
            content, 
            re.DOTALL
        )
        
        if validation_section:
            print("\n🔍 FOUND VALIDATION SECTION:")
            print("=" * 40)
            validation_code = validation_section.group(0)
            lines = validation_code.split('\n')
            for i, line in enumerate(lines[:20]):  # Show first 20 lines
                print(f"{i+1:2d}: {line}")
            if len(lines) > 20:
                print(f"... ({len(lines) - 20} more lines)")
        
        # Check for any database validation limits
        db_validation_patterns = [
            r'get_products_by_names.*\(',
            r'db_records.*=',
            r'found_names.*=',
            r'len\(.*found_names',
            r'len\(.*valid_selected_tags'
        ]
        
        print("\n🔍 DATABASE VALIDATION PATTERNS:")
        for pattern in db_validation_patterns:
            matches = re.findall(rf'.*{pattern}.*', content, re.IGNORECASE)
            if matches:
                print(f"✅ {pattern}:")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"    {match.strip()}")
        
        # Look for any limits in database queries
        database_files = [
            "src/core/data/product_database.py",
            "src/core/data/excel_processor.py"
        ]
        
        print("\n🔍 CHECKING DATABASE FILES FOR LIMITS...")
        for db_file in database_files:
            if os.path.exists(db_file):
                with open(db_file, 'r') as f:
                    db_content = f.read()
                
                # Look for LIMIT clauses or array slicing
                limit_patterns = [
                    r'LIMIT\s+\d+',
                    r'\.limit\(\d+\)',
                    r'\[\s*:\s*\d+\s*\]',
                    r'\.head\(\d+\)',
                    r'\.iloc\[.*:\d+.*\]'
                ]
                
                found_limits = []
                for pattern in limit_patterns:
                    matches = re.findall(pattern, db_content, re.IGNORECASE)
                    if matches:
                        found_limits.extend(matches)
                
                if found_limits:
                    print(f"⚠️  FOUND LIMITS in {db_file}:")
                    for limit in found_limits:
                        print(f"    {limit}")
                else:
                    print(f"✅ No limits found in {db_file}")
            else:
                print(f"❌ {db_file} not found")
        
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        
        print("""
🔍 WHAT TO CHECK:

1. JSON MATCHING PHASE:
   ✅ 49 matches found from JSON data
   ✅ All matches filtered to vendor 'CERES'

2. VALIDATION PHASE (Potential issue):
   ❓ Are all 49 JSON matches being validated correctly?
   ❓ Is get_products_by_names() returning only 18 records?
   ❓ Are there any limits in the database query?

3. DATABASE LOOKUP:
   ❓ Does the database actually contain all 49 products?
   ❓ Are product names matching exactly between JSON and DB?

🚀 NEXT DIAGNOSTIC STEPS:

1. Add logging to see how many records get_products_by_names() returns
2. Check if the database actually has all 49 products
3. Verify product name matching between JSON and database

🎯 LIKELY ISSUE:
The 49 JSON matches are found, but only 18 of them exist in the 
database, so only 18 valid records are returned for label generation.
        """)
        
    except Exception as e:
        print(f"❌ Error analyzing files: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_matching_vs_validation()