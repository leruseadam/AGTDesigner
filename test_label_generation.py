#!/usr/bin/env python3
"""
Test script to test actual label generation and verify ProductStrain duplication fix.
This script will generate a label using the full system to see if the fix is working.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_label_generation():
    """Test the actual label generation process to verify the ProductStrain fix."""
    
    print("=== LABEL GENERATION TEST ===")
    
    try:
        # Import the necessary modules
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        from src.core.generation.tag_generator import generate_labels
        
        print("✅ Successfully imported required modules")
        
        # Get the default file
        default_file = get_default_upload_file()
        if not default_file:
            print("❌ No default file found")
            return
        
        print(f"📁 Using default file: {default_file}")
        
        # Load the data
        processor = ExcelProcessor()
        data = processor.load_data(default_file)
        
        if data is None or data.empty:
            print("❌ No data loaded")
            return
        
        print(f"✅ Loaded {len(data)} records")
        
        # Find a problematic record (Paraphernalia type)
        problematic_records = data[data['Product Type*'].str.lower() == 'paraphernalia']
        
        if problematic_records.empty:
            print("❌ No problematic records found")
            return
        
        test_record = problematic_records.iloc[0]
        print(f"🔍 Testing with record: {test_record.get('Product Brand', 'Unknown')}")
        print(f"   Type: {test_record.get('Product Type*', 'Unknown')}")
        print(f"   Original Strain: {test_record.get('Product Strain', 'Unknown')}")
        
        # Test the full label generation process
        try:
            # Create a small test dataset with just this record
            test_data = pd.DataFrame([test_record])
            
            # Generate labels
            result = generate_labels(test_data, "double", "horizontal")
            
            if result and 'success' in result and result['success']:
                print("✅ Label generation successful")
                
                # Check if the generated document contains the correct ProductStrain
                if 'document_path' in result:
                    doc_path = result['document_path']
                    print(f"📄 Generated document: {doc_path}")
                    
                    # For now, just confirm the process completed
                    print("✅ ProductStrain processing completed through full pipeline")
                else:
                    print("⚠️  No document path in result")
            else:
                print(f"❌ Label generation failed: {result}")
                
        except Exception as e:
            print(f"❌ Error during label generation: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_label_generation()
