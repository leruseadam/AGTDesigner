#!/usr/bin/env python3
"""
Test script to verify the double template duplication fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor
import pandas as pd
from io import BytesIO

def test_double_template_fix():
    """Test that the double template no longer duplicates product names."""
    print("🧪 Testing Double Template Duplication Fix")
    print("=" * 50)
    
    # Create test data that would cause duplication
    test_data = {
        'Product Name*': [
            'Afghani Kush Wax -1g',
            'Blue Dream Wax -1g', 
            'Bruce Banner Wax -1g',
            'Lemon Jealousy Wax -1g',
            'Memory Loss Wax -1g',
            'Birthday Cake -14g'
        ],
        'Product Type*': [
            'concentrate',
            'concentrate',
            'concentrate', 
            'concentrate',
            'concentrate',
            'flower'
        ],
        'Product Brand': [
            'Test Brand 1',
            'Test Brand 2',
            'Test Brand 3',
            'Test Brand 4', 
            'Test Brand 5',
            'Test Brand 6'
        ],
        'Price': ['$12', '$12', '$12', '$12', '$12', '$100'],
        'Weight*': [1, 1, 1, 1, 1, 14],
        'Units': ['g', 'g', 'g', 'g', 'g', 'g'],
        'DOH': ['YES', 'YES', 'YES', 'YES', 'YES', 'YES'],
        'Lineage': ['INDICA', 'SATIVA', 'HYBRID/SATIVA', 'SATIVA', 'SATIVA', 'HYBRID'],
        'Product Strain': ['Afghani Kush', 'Blue Dream', 'Bruce Banner', 'Lemon Jealousy', 'Memory Loss', 'Birthday Cake'],
        'Ratio': ['THC: 66.73% CBD: -0.17%', 'THC: 65.12% CBD: 0.08%', 'THC: 68.45% CBD: 0.12%', 'THC: 67.89% CBD: 0.05%', 'THC: 66.21% CBD: 0.09%', 'THC: 24.95% CBD: 0.05%']
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Save to temporary Excel file
    temp_file = 'test_double_template_data.xlsx'
    df.to_excel(temp_file, index=False)
    
    try:
        # Process with Excel processor
        processor = ExcelProcessor()
        success = processor.load_file(temp_file)
        
        if not success:
            print("❌ Failed to load test file")
            return False
            
        print("✅ Excel file loaded successfully")
        
        # Get processed records
        records = processor.get_available_tags()
        
        print(f"\n📊 Processed {len(records)} records:")
        for i, record in enumerate(records[:3]):  # Show first 3
            print(f"  Record {i+1}:")
            print(f"    Description: '{record.get('Description', 'N/A')}'")
            print(f"    WeightUnits: '{record.get('WeightUnits', 'N/A')}'")
            print(f"    ProductName: '{record.get('ProductName', 'N/A')}'")
            print()
        
        # Test double template generation
        template_processor = TemplateProcessor('double', {}, 1.0)
        
        # Process the records
        result = template_processor.process_records(records)
        
        if result:
            print("✅ Double template generation successful")
            
            # Check if the result contains the expected content
            if hasattr(result, 'tables'):
                for table in result.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            text = cell.text.strip()
                            if text:
                                print(f"  Cell content: '{text}'")
                                
                                # Check for duplication
                                if 'Wax Wax' in text or 'Cake Cake' in text:
                                    print(f"❌ Found duplication in: '{text}'")
                                    return False
                                elif 'Wax -1g' in text or 'Cake -14g' in text:
                                    print(f"✅ No duplication found in: '{text}'")
            
            print("✅ Double template duplication fix verified!")
            return True
        else:
            print("❌ Double template generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    success = test_double_template_fix()
    if success:
        print("\n🎉 All tests passed! Double template duplication is fixed.")
    else:
        print("\n💥 Tests failed. Double template duplication still exists.")
    sys.exit(0 if success else 1) 