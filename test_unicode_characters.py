#!/usr/bin/env python3
"""
Test script to identify Unicode characters being added to template output.
This will help find what's causing the blue dots (•) in the labels.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_unicode_characters():
    """Test what Unicode characters are being added to template output."""
    
    print("=== UNICODE CHARACTER TEST ===\n")
    
    try:
        # Import the necessary modules
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
        
        print("✅ Successfully imported required modules")
        
        # Get the default file
        default_file = get_default_upload_file()
        if not default_file:
            print("❌ No default file found")
            return
        
        print(f"📁 Using default file: {default_file}")
        
        # Load the data
        processor = ExcelProcessor()
        success = processor.load_file(default_file)
        
        if not success or processor.df is None or processor.df.empty:
            print("❌ No data loaded")
            return
        
        print(f"✅ Loaded {len(processor.df)} records\n")
        
        # Test with a specific record
        test_record = processor.df.iloc[0]
        print(f"🔍 Testing with record: {test_record.get('ProductName', 'Unknown')}")
        
        # Create a template processor
        template_processor = TemplateProcessor(
            template_type="double",
            font_scheme=get_font_scheme("double")
        )
        
        # Convert the record to a dictionary
        record_dict = test_record.to_dict()
        
        # Test the context building
        print(f"🔧 Testing context building...")
        
        try:
            # Create a mock document for testing
            from docx import Document
            doc = Document()
            
            # Test the context building
            label_context = template_processor._build_label_context(record_dict, doc)
            
            # Check specific fields for Unicode characters
            fields_to_check = ['DescAndWeight', 'ProductBrand', 'Lineage', 'ProductStrain']
            
            for field in fields_to_check:
                if field in label_context:
                    value = label_context[field]
                    print(f"\n📋 {field}:")
                    print(f"   Raw value: {repr(value)}")
                    
                    # Check for specific Unicode characters
                    unicode_chars = []
                    for char in value:
                        if ord(char) > 127:  # Non-ASCII characters
                            unicode_chars.append(f"U+{ord(char):04X} ({char})")
                    
                    if unicode_chars:
                        print(f"   Unicode characters found: {', '.join(unicode_chars)}")
                    else:
                        print(f"   No Unicode characters found")
                    
                    # Check for specific problematic characters
                    problematic_chars = {
                        '\u00A0': 'Non-breaking space',
                        '\u202F': 'Narrow no-break space', 
                        '\u00B0': 'Degree sign',
                        '\u2219': 'Bullet operator',
                        '\u2022': 'Bullet',
                        '\u00B7': 'Middle dot'
                    }
                    
                    for char, description in problematic_chars.items():
                        if char in value:
                            print(f"   ⚠️  Found {description}: {repr(char)}")
            
        except Exception as e:
            print(f"      ❌ Error testing context building: {e}")
        
        print("\n✅ Unicode character test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unicode_characters()
