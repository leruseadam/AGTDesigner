#!/usr/bin/env python3
"""
Comprehensive test to verify double template cell corruption fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_records(count):
    """Create test records for testing."""
    base_records = [
        {
            'ProductName': 'HUSTLER\'S AMBITION Cheesecake - 14g',
            'Description': 'HUSTLER\'S AMBITION Cheesecake - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 24.95% CBD: 0.05%',
            'ProductStrain': 'Cheesecake',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Churros - 14g',
            'Description': 'HUSTLER\'S AMBITION Churros - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 19.0% CBD: 0.03%',
            'ProductStrain': 'Churros',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Jelly Donuts - 14g',
            'Description': 'HUSTLER\'S AMBITION Jelly Donuts - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 18.57% CBD: 0.05%',
            'ProductStrain': 'Jelly Donuts',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Gelato - 14g',
            'Description': 'HUSTLER\'S AMBITION Gelato - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 25.0% CBD: 0%',
            'ProductStrain': 'Gelato',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Blueberry - 14g',
            'Description': 'HUSTLER\'S AMBITION Blueberry - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 22.5% CBD: 1.2%',
            'ProductStrain': 'Blueberry',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Strawberry - 14g',
            'Description': 'HUSTLER\'S AMBITION Strawberry - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 21.8% CBD: 0.8%',
            'ProductStrain': 'Strawberry',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Vanilla - 14g',
            'Description': 'HUSTLER\'S AMBITION Vanilla - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 23.1% CBD: 0.9%',
            'ProductStrain': 'Vanilla',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Chocolate - 14g',
            'Description': 'HUSTLER\'S AMBITION Chocolate - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 20.5% CBD: 1.5%',
            'ProductStrain': 'Chocolate',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Mint - 14g',
            'Description': 'HUSTLER\'S AMBITION Mint - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 24.2% CBD: 0.7%',
            'ProductStrain': 'Mint',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Caramel - 14g',
            'Description': 'HUSTLER\'S AMBITION Caramel - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 19.8% CBD: 1.1%',
            'ProductStrain': 'Caramel',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Coffee - 14g',
            'Description': 'HUSTLER\'S AMBITION Coffee - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 26.3% CBD: 0.4%',
            'ProductStrain': 'Coffee',
            'DOH': 'DOH'
        },
        {
            'ProductName': 'HUSTLER\'S AMBITION Orange - 14g',
            'Description': 'HUSTLER\'S AMBITION Orange - 14g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$100',
            'Lineage': 'HYBRID',
            'Ratio_or_THC_CBD': 'THC: 18.9% CBD: 1.3%',
            'ProductStrain': 'Orange',
            'DOH': 'DOH'
        }
    ]
    
    return base_records[:count]

def analyze_document(doc, expected_records):
    """Analyze the generated document for correctness."""
    print(f"\nAnalyzing document with {expected_records} expected records:")
    print("-" * 50)
    
    if not doc.tables:
        print("❌ No tables found in document")
        return False
    
    table = doc.tables[0]
    total_cells = len(table.rows) * len(table.columns)
    print(f"Table structure: {len(table.rows)} rows x {len(table.columns)} columns = {total_cells} cells")
    
    filled_cells = 0
    empty_cells = 0
    corrupted_cells = 0
    
    for row_idx, row in enumerate(table.rows):
        for col_idx, cell in enumerate(row.cells):
            cell_text = cell.text.strip()
            cell_num = row_idx * len(table.columns) + col_idx + 1
            
            if cell_num <= expected_records:
                # This cell should be filled
                if cell_text and 'HUSTLER\'S AMBITION' in cell_text:
                    filled_cells += 1
                    print(f"  ✓ Cell {cell_num}: Filled correctly")
                elif 'Label' in cell_text:
                    corrupted_cells += 1
                    print(f"  ❌ Cell {cell_num}: Contains unprocessed placeholder")
                else:
                    corrupted_cells += 1
                    print(f"  ❌ Cell {cell_num}: Empty when it should be filled")
            else:
                # This cell should be empty
                if not cell_text or cell_text == "":
                    empty_cells += 1
                    print(f"  ✓ Cell {cell_num}: Correctly empty")
                elif 'Label' in cell_text:
                    corrupted_cells += 1
                    print(f"  ❌ Cell {cell_num}: Contains unprocessed placeholder")
                else:
                    empty_cells += 1
                    print(f"  ✓ Cell {cell_num}: Empty (acceptable)")
    
    print(f"\nSummary:")
    print(f"  Filled cells: {filled_cells}/{expected_records}")
    print(f"  Empty cells: {empty_cells}/{total_cells - expected_records}")
    print(f"  Corrupted cells: {corrupted_cells}")
    
    success = filled_cells == expected_records and corrupted_cells == 0
    if success:
        print("✅ Document analysis: PASSED")
    else:
        print("❌ Document analysis: FAILED")
    
    return success

def test_double_template_with_various_records():
    """Test double template with different numbers of records."""
    print("Double Template Cell Corruption Fix Verification")
    print("=" * 60)
    
    test_cases = [1, 4, 8, 12]  # Test with 1, 4, 8, and 12 records
    
    all_passed = True
    
    for record_count in test_cases:
        print(f"\n{'='*20} Testing with {record_count} records {'='*20}")
        
        try:
            # Create test records
            test_records = create_test_records(record_count)
            
            # Create template processor
            processor = TemplateProcessor('double', {}, 1.0)
            
            # Process records
            result_doc = processor.process_records(test_records)
            
            if result_doc:
                # Save test document
                filename = f"double_template_test_{record_count}_records.docx"
                result_doc.save(filename)
                print(f"✓ Document saved as: {filename}")
                
                # Analyze the document
                success = analyze_document(result_doc, record_count)
                if not success:
                    all_passed = False
            else:
                print(f"❌ Failed to generate document for {record_count} records")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {record_count} records: {e}")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! Double template cell corruption fix is working correctly.")
    else:
        print("❌ Some tests failed. Double template still has issues.")
    
    return all_passed

def test_edge_cases():
    """Test edge cases that might cause issues."""
    print(f"\n{'='*20} Testing Edge Cases {'='*20}")
    
    edge_cases = [
        {
            'name': 'Empty records list',
            'records': [],
            'expected': 0
        },
        {
            'name': 'Single record with special characters',
            'records': [{
                'ProductName': 'Test & Product (Special) - 14g',
                'Description': 'Test & Product (Special) - 14g',
                'ProductBrand': 'Test & Brand',
                'Price': '$99.99',
                'Lineage': 'HYBRID/INDICA',
                'Ratio_or_THC_CBD': 'THC: 25.5% CBD: 1.2%',
                'ProductStrain': 'Test Strain',
                'DOH': 'DOH'
            }],
            'expected': 1
        },
        {
            'name': 'Records with missing fields',
            'records': [{
                'ProductName': 'Incomplete Product',
                'Description': 'Incomplete Product',
                'ProductBrand': 'Incomplete Brand',
                'Price': '',
                'Lineage': '',
                'Ratio_or_THC_CBD': '',
                'ProductStrain': '',
                'DOH': ''
            }],
            'expected': 1
        }
    ]
    
    all_edge_passed = True
    
    for case in edge_cases:
        print(f"\nTesting: {case['name']}")
        try:
            processor = TemplateProcessor('double', {}, 1.0)
            result_doc = processor.process_records(case['records'])
            
            if result_doc:
                filename = f"edge_case_{case['name'].replace(' ', '_').lower()}.docx"
                result_doc.save(filename)
                print(f"✓ Edge case document saved: {filename}")
                
                success = analyze_document(result_doc, case['expected'])
                if not success:
                    all_edge_passed = False
            else:
                print(f"❌ Edge case failed: {case['name']}")
                all_edge_passed = False
                
        except Exception as e:
            print(f"❌ Edge case error: {case['name']} - {e}")
            all_edge_passed = False
    
    if all_edge_passed:
        print("✅ All edge cases passed!")
    else:
        print("❌ Some edge cases failed!")
    
    return all_edge_passed

if __name__ == "__main__":
    # Run main tests
    main_tests_passed = test_double_template_with_various_records()
    
    # Run edge case tests
    edge_tests_passed = test_edge_cases()
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY:")
    print(f"Main tests: {'✅ PASSED' if main_tests_passed else '❌ FAILED'}")
    print(f"Edge cases: {'✅ PASSED' if edge_tests_passed else '❌ FAILED'}")
    
    if main_tests_passed and edge_tests_passed:
        print("🎉 DOUBLE TEMPLATE CELL CORRUPTION FIX VERIFICATION COMPLETE!")
        print("The fix is working correctly for all test cases.")
    else:
        print("⚠️  Some issues remain with the double template.") 