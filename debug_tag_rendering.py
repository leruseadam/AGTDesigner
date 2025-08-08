#!/usr/bin/env python3
"""
Debug script to test tag rendering and identify display issues
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from core.data.excel_processor import ExcelProcessor, get_default_upload_file

def test_tag_rendering():
    """Test tag rendering to identify display issues"""
    print("=== Testing Tag Rendering ===")
    
    # Initialize processor
    processor = ExcelProcessor()
    
    # Try to load default file
    default_file = get_default_upload_file()
    if default_file and os.path.exists(default_file):
        print(f"Loading default file: {default_file}")
        try:
            processor.load_file(default_file)
            print(f"✅ File loaded successfully: {len(processor.df)} records")
            
            # Get all available tags
            all_tags = processor.get_available_tags()
            print(f"✅ Total available tags: {len(all_tags)}")
            
            # Check for specific tag that was being cut off
            rainbow_belt_tags = [tag for tag in all_tags if 'Rainbow Belt' in str(tag.get('Product Name*', ''))]
            print(f"✅ Rainbow Belt tags found: {len(rainbow_belt_tags)}")
            
            if rainbow_belt_tags:
                print("Sample Rainbow Belt tags:")
                for i, tag in enumerate(rainbow_belt_tags[:5]):
                    print(f"  {i+1}. {tag.get('Product Name*', 'N/A')}")
            
            # Check if there are tags after Rainbow Belt alphabetically
            product_names = [str(tag.get('Product Name*', '')).lower() for tag in all_tags]
            rainbow_belt_index = -1
            
            for i, name in enumerate(product_names):
                if 'rainbow belt' in name:
                    rainbow_belt_index = i
                    break
            
            if rainbow_belt_index >= 0:
                tags_after_rainbow = product_names[rainbow_belt_index + 1:]
                print(f"✅ Tags after Rainbow Belt alphabetically: {len(tags_after_rainbow)}")
                
                if tags_after_rainbow:
                    print("Sample tags after Rainbow Belt:")
                    for i, name in enumerate(tags_after_rainbow[:10]):
                        print(f"  {i+1}. {name}")
            
            # Test filter options
            filter_options = processor.get_dynamic_filter_options({})
            print(f"✅ Filter options generated:")
            for filter_type, options in filter_options.items():
                print(f"  {filter_type}: {len(options)} options")
            
            print("\n✅ Tag rendering test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    else:
        print("❌ No default file found")
        return False

if __name__ == "__main__":
    success = test_tag_rendering()
    sys.exit(0 if success else 1) 