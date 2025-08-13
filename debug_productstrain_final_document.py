#!/usr/bin/env python3
"""
Debug script to examine the final generated document and identify 
where ProductStrain content is appearing and why it might show ProductBrand values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from src.core.data.excel_processor import get_default_upload_file
from docx import Document
import pandas as pd

def debug_final_document():
    """Examine the final generated document to find ProductStrain issues."""
    
    print("🔍 Debugging Final Document Content")
    print("=" * 50)
    
    # Load the default Excel file
    default_file = get_default_upload_file()
    if not default_file or not os.path.exists(default_file):
        print("❌ No default Excel file found")
        return
    
    print(f"📁 Loading Excel file: {os.path.basename(default_file)}")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    success = excel_processor.load_file(default_file)
    
    if not success:
        print("❌ Failed to load Excel file")
        return
    
    df = excel_processor.df
    print(f"✅ Excel file loaded successfully")
    print(f"📊 Total records: {len(df)}")
    
    # Find a record with different ProductStrain and ProductBrand
    strain_col = 'Product Strain' if 'Product Strain' in df.columns else 'ProductStrain'
    brand_col = 'Product Brand' if 'Product Brand' in df.columns else 'ProductBrand'
    
    # Convert to string to avoid categorical comparison issues
    strain_values = df[strain_col].astype(str)
    brand_values = df[brand_col].astype(str)
    different_records = df[strain_values != brand_values].head(3)
    
    if len(different_records) == 0:
        print("❌ No records with different ProductStrain and ProductBrand found")
        return
    
    print(f"✅ Found {len(different_records)} records with different ProductStrain and ProductBrand")
    
    # Test with first record
    record = different_records.iloc[0]
    print(f"\n🧪 Testing with record:")
    print(f"  Product Type: {record.get('Product Type*', 'N/A')}")
    print(f"  Product Strain: {record.get(strain_col, 'N/A')}")
    print(f"  Product Brand: {record.get(brand_col, 'N/A')}")
    print(f"  Description: {record.get('Description', 'N/A')}")
    
    # Initialize template processor
    template_processor = TemplateProcessor('vertical', get_font_scheme('vertical'))
    
    # Generate the document
    print(f"\n📄 Generating document...")
    try:
        doc = template_processor.generate_labels([record])
        print("✅ Document generated successfully")
    except Exception as e:
        print(f"❌ Failed to generate document: {e}")
        return
    
    # Examine the document content
    print(f"\n🔍 Examining document content...")
    
    # Look for ProductStrain and ProductBrand content in each cell
    for table_idx, table in enumerate(doc.tables):
        print(f"\n📋 Table {table_idx + 1}:")
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cell_text = "".join([run.text for run in cell.paragraphs[0].runs])
                if cell_text.strip():
                    print(f"  Cell [{row_idx},{col_idx}]: '{cell_text}'")
                    
                    # Check if this cell contains ProductStrain content
                    if 'PRODUCTSTRAIN_START' in cell_text and 'PRODUCTSTRAIN_END' in cell_text:
                        print(f"    ✅ Contains ProductStrain markers")
                        # Extract the strain content
                        start_idx = cell_text.find('PRODUCTSTRAIN_START') + len('PRODUCTSTRAIN_START')
                        end_idx = cell_text.find('PRODUCTSTRAIN_END')
                        strain_content = cell_text[start_idx:end_idx]
                        print(f"    📝 Strain content: '{strain_content}'")
                        
                        # Check if this matches the expected strain
                        expected_strain = record.get(strain_col, '')
                        if strain_content == expected_strain:
                            print(f"    ✅ Strain content matches Excel data")
                        else:
                            print(f"    ❌ Strain content mismatch!")
                            print(f"      Expected: '{expected_strain}'")
                            print(f"      Found: '{strain_content}'")
                    
                    # Check if this cell contains ProductBrand content
                    if 'PRODUCTBRAND_CENTER_START' in cell_text and 'PRODUCTBRAND_CENTER_END' in cell_text:
                        print(f"    ✅ Contains ProductBrand markers")
                        # Extract the brand content
                        start_idx = cell_text.find('PRODUCTBRAND_CENTER_START') + len('PRODUCTBRAND_CENTER_START')
                        end_idx = cell_text.find('PRODUCTBRAND_CENTER_END')
                        brand_content = cell_text[start_idx:end_idx]
                        print(f"    📝 Brand content: '{brand_content}'")
                        
                        # Check if this matches the expected brand
                        expected_brand = record.get(brand_col, '')
                        if brand_content == expected_brand:
                            print(f"    ✅ Brand content matches Excel data")
                        else:
                            print(f"    ❌ Brand content mismatch!")
                            print(f"      Expected: '{expected_brand}'")
                            print(f"      Found: '{brand_content}'")
    
    # Save the document for manual inspection
    output_file = "debug_final_document_output.docx"
    doc.save(output_file)
    print(f"\n💾 Document saved as: {output_file}")
    print(f"  You can open this file to manually inspect the content")

if __name__ == "__main__":
    debug_final_document() 