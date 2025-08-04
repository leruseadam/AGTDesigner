#!/usr/bin/env python3
"""
Test script to verify that classic types now use database lineage instead of Excel lineage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import CLASSIC_TYPES
from docx import Document
import tempfile
import os

def test_classic_lineage_fix():
    """Test that classic types now use database lineage instead of Excel lineage."""
    print("Testing Classic Type Lineage Fix")
    
    # Test with a classic type (concentrate) that has "HUSTLER'S AMBITION" in Excel lineage
    # but should use the strain's canonical lineage from the database
    classic_record = {
        'ProductName': 'Acapulco Gold Wax',
        'Product Brand': 'HUSTLER\'S AMBITION',  # This should NOT be used for classic types
        'Product Strain': 'Acapulco Gold',  # This should be used to get canonical lineage
        'Product Type*': 'concentrate',  # Classic type
        'Lineage': 'HUSTLER\'S AMBITION',  # This should be ignored for classic types
        'Price': '$12',
        'THC': '71.66%',
        'CBD': '',
        'Description': 'Acapulco Gold Wax -1g',
        'WeightUnits': '1g'
    }
    
    print("1. Testing classic type lineage processing:")
    print(f"   Product: {classic_record['ProductName']}")
    print(f"   Product Type: {classic_record['Product Type*']} (classic)")
    print(f"   Product Strain: {classic_record['Product Strain']}")
    print(f"   Excel Lineage: '{classic_record['Lineage']}' (should be ignored)")
    print(f"   Product Brand: '{classic_record['Product Brand']}' (should be ignored)")
    
    # Process the test record
    tp = TemplateProcessor('double', {})
    documents = tp.process_records([classic_record])
    
    if not documents:
        print("✗ No documents generated")
        return False
    
    # Save the document to a temporary file
    doc = documents[0] if isinstance(documents, list) else documents
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_file.name)
    temp_file.close()
    
    print(f"\n2. Document saved to: {temp_file.name}")
    
    # Check if "HUSTLER'S AMBITION" is present in the document
    print("\n3. Checking document content:")
    found_hustlers_ambition = False
    found_strain_lineage = False
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    text = paragraph.text
                    print(f"   Cell text: '{text.strip()}'")
                    
                    if 'HUSTLER\'S AMBITION' in text:
                        found_hustlers_ambition = True
                        print(f"   ✗ Found 'HUSTLER\'S AMBITION' in: '{text.strip()}'")
                    
                    # Look for strain lineage (should be from database)
                    if 'ACAPULCO GOLD' in text or 'SATIVA' in text or 'INDICA' in text or 'HYBRID' in text:
                        found_strain_lineage = True
                        print(f"   ✓ Found strain lineage in: '{text.strip()}'")
    
    print(f"\n4. Results:")
    print(f"   Found 'HUSTLER\'S AMBITION': {found_hustlers_ambition}")
    print(f"   Found strain lineage: {found_strain_lineage}")
    
    if not found_hustlers_ambition and found_strain_lineage:
        print("✓ SUCCESS: Classic type now uses database lineage instead of Excel lineage")
        return True
    elif found_hustlers_ambition:
        print("✗ ERROR: 'HUSTLER'S AMBITION' is still being inserted (should use database lineage)")
        return False
    else:
        print("✗ ERROR: No lineage found in document")
        return False

if __name__ == "__main__":
    success = test_classic_lineage_fix()
    if success:
        print("\n✅ Classic type lineage fix is working correctly!")
    else:
        print("\n❌ Classic type lineage fix needs more work.")
    
    # Clean up
    try:
        os.unlink(temp_file.name)
    except:
        pass 