#!/usr/bin/env python3
"""
Test to verify that Classic Type Lineage values are properly left-justified.
"""

import pandas as pd
import sys
import os
import tempfile
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor

def test_classic_lineage_alignment():
    """Test that Classic Type Lineage values are left-justified."""
    
    # Create test data with classic and non-classic types
    test_data = [
        {
            'Product Name*': 'Blue Dream Flower',
            'Product Type*': 'flower',  # Classic type
            'Description': 'High-quality Blue Dream flower',
            'Lineage': 'HYBRID',
            'Expected Alignment': 'LEFT'
        },
        {
            'Product Name*': 'CBD Gummies',
            'Product Type*': 'edible (solid)',  # Non-classic type
            'Description': 'CBD gummies for relaxation',
            'Lineage': 'CBD',
            'Expected Alignment': 'CENTER'
        },
        {
            'Product Name*': 'OG Kush Pre-roll',
            'Product Type*': 'pre-roll',  # Classic type
            'Description': 'OG Kush pre-roll',
            'Lineage': 'INDICA',
            'Expected Alignment': 'LEFT'
        },
        {
            'Product Name*': 'CBD Tincture',
            'Product Type*': 'tincture',  # Non-classic type
            'Description': 'CBD tincture for wellness',
            'Lineage': 'CBD',
            'Expected Alignment': 'CENTER'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Add required columns
    df['Product Brand'] = 'Test Brand'
    df['Vendor'] = 'Test Vendor'
    df['Product Strain'] = ''
    df['Ratio'] = ''
    df['Price'] = '10.00'
    df['Weight*'] = '1.0'
    df['Units'] = 'oz'
    
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        temp_file_path = tmp_file.name
    
    try:
        # Create ExcelProcessor instance and load the file
        processor = ExcelProcessor()
        success = processor.load_file(temp_file_path)
        
        if not success:
            print("❌ Failed to load file")
            return False
        
        # Get all available tags and select them
        available_tags = processor.get_available_tags()
        if available_tags:
            # Debug: print the structure of available_tags
            print(f"Available tags structure: {type(available_tags)}")
            if available_tags:
                print(f"First tag: {available_tags[0]}")
            
            # Try different ways to get tag names
            if isinstance(available_tags[0], dict) and 'displayName' in available_tags[0]:
                tag_names = [tag['displayName'] for tag in available_tags]
            elif isinstance(available_tags[0], dict) and 'name' in available_tags[0]:
                tag_names = [tag['name'] for tag in available_tags]
            elif isinstance(available_tags[0], str):
                tag_names = available_tags
            else:
                # Fallback: use the tags directly
                tag_names = available_tags
            
            processor.select_tags(tag_names)
        
        # Get the processed records
        records = processor.get_selected_records('vertical')
        
        if not records:
            print("❌ No records found")
            return False
        
        # Create TemplateProcessor and generate a document
        template_processor = TemplateProcessor('vertical', {}, 1.0)
        doc = template_processor.process_records(records)
        
        if not doc:
            print("❌ Failed to generate document")
            return False
        
        # Check the alignment of Lineage text in the document
        results = []
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text.strip()
                        # Look for lineage values
                        lineage_values = ['HYBRID', 'INDICA', 'SATIVA', 'CBD', 'MIXED']
                        if any(lineage in text.upper() for lineage in lineage_values):
                            # Find the corresponding test data
                            for test_item in test_data:
                                if test_item['Lineage'] in text:
                                    actual_alignment = paragraph.alignment
                                    expected_alignment = test_item['Expected Alignment']
                                    
                                    # Convert alignment to string for comparison
                                    if actual_alignment == WD_ALIGN_PARAGRAPH.LEFT:
                                        actual_alignment_str = 'LEFT'
                                    elif actual_alignment == WD_ALIGN_PARAGRAPH.CENTER:
                                        actual_alignment_str = 'CENTER'
                                    else:
                                        actual_alignment_str = 'OTHER'
                                    
                                    result = {
                                        'Product': test_item['Product Name*'],
                                        'Type': test_item['Product Type*'],
                                        'Lineage': test_item['Lineage'],
                                        'Expected': expected_alignment,
                                        'Actual': actual_alignment_str,
                                        'Correct': actual_alignment_str == expected_alignment
                                    }
                                    results.append(result)
                                    
                                    status = "✅ PASS" if actual_alignment_str == expected_alignment else "❌ FAIL"
                                    print(f"{status} | {test_item['Product Name*']} | {test_item['Product Type*']} | Lineage: {test_item['Lineage']} | Expected: {expected_alignment} | Actual: {actual_alignment_str}")
        
        # Summary
        if results:
            correct_count = sum(1 for r in results if r['Correct'])
            total_count = len(results)
            
            print(f"\n=== Summary ===")
            print(f"Total tests: {total_count}")
            print(f"Passed: {correct_count}")
            print(f"Failed: {total_count - correct_count}")
            print(f"Success rate: {correct_count/total_count*100:.1f}%")
            
            if correct_count == total_count:
                print("🎉 All tests passed! Classic Type Lineage values are properly left-justified.")
            else:
                print("⚠️  Some tests failed. The alignment fix needs more work.")
            
            return correct_count == total_count
        else:
            print("❌ No lineage values found in the generated document")
            return False
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    success = test_classic_lineage_alignment()
    sys.exit(0 if success else 1) 