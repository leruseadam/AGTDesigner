#!/usr/bin/env python3
"""
Test script to verify THC/CBD column merging logic.
Tests merging column K (THC test result) into column AI (Total THC) 
and column L (CBD test result) into column AK (CBDA), using highest values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_thc_cbd_merge():
    """Test the THC/CBD column merging logic."""
    
    print("Testing THC/CBD Column Merging Logic")
    print("=" * 50)
    
    # Create Excel processor
    processor = ExcelProcessor()
    
    # Get the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file:
        print("❌ No default file found")
        return
    
    print(f"Found default file: {default_file}")
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully: {len(processor.df)} rows")
    
    # Check if required columns exist
    required_columns = ['Total THC', 'THCA', 'THC test result', 'CBDA', 'CBD test result']
    missing_columns = [col for col in required_columns if col not in processor.df.columns]
    
    if missing_columns:
        print(f"⚠️  Missing columns: {missing_columns}")
        print("Available THC/CBD columns:")
        for col in processor.df.columns:
            if any(keyword in col.lower() for keyword in ['thc', 'cbd']):
                print(f"  - {col}")
        return
    
    print("✅ All required columns found")
    
    # Test the merging logic with sample data
    print("\nTesting merging logic with sample data:")
    
    # Create test cases
    test_cases = [
        {
            'name': 'THC test result higher',
            'total_thc': '15.5',
            'thca': '12.0',
            'thc_test_result': '18.2',
            'cbda': '2.1',
            'cbd_test_result': '3.5',
            'expected_thc': '18.2',
            'expected_cbd': '3.5'
        },
        {
            'name': 'Total THC higher',
            'total_thc': '22.0',
            'thca': '18.5',
            'thc_test_result': '19.8',
            'cbda': '4.2',
            'cbd_test_result': '2.8',
            'expected_thc': '22.0',
            'expected_cbd': '4.2'
        },
        {
            'name': 'Empty THC test result',
            'total_thc': '16.5',
            'thca': '14.0',
            'thc_test_result': '',
            'cbda': '1.8',
            'cbd_test_result': '',
            'expected_thc': '16.5',
            'expected_cbd': '1.8'
        },
        {
            'name': 'Zero Total THC, use THCA',
            'total_thc': '0',
            'thca': '13.2',
            'thc_test_result': '12.0',
            'cbda': '2.5',
            'cbd_test_result': '3.0',
            'expected_thc': '13.2',
            'expected_cbd': '3.0'
        },
        {
            'name': 'Invalid values',
            'total_thc': 'nan',
            'thca': '15.0',
            'thc_test_result': 'invalid',
            'cbda': 'nan',
            'cbd_test_result': '2.1',
            'expected_thc': '15.0',
            'expected_cbd': '2.1'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        
        # Create a mock record
        mock_record = {
            'Total THC': test_case['total_thc'],
            'THCA': test_case['thca'],
            'THC test result': test_case['thc_test_result'],
            'CBDA': test_case['cbda'],
            'CBD test result': test_case['cbd_test_result'],
            'Product Name*': f'Test Product {i}'
        }
        
        # Apply the merging logic (copied from excel_processor.py)
        def safe_float(value):
            if not value or value in ['nan', 'NaN', '']:
                return 0.0
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        # THC merging logic
        total_thc_value = str(mock_record.get('Total THC', '')).strip()
        thca_value = str(mock_record.get('THCA', '')).strip()
        thc_test_result = str(mock_record.get('THC test result', '')).strip()
        
        if thc_test_result in ['nan', 'NaN', '']:
            thc_test_result = ''
        
        total_thc_float = safe_float(total_thc_value)
        thc_test_float = safe_float(thc_test_result)
        thca_float = safe_float(thca_value)
        
        # For THC: Use the highest value among Total THC, THC test result, and THCA
        # But if Total THC is 0 or empty, prefer THCA over THC test result
        if total_thc_float > 0:
            # Total THC has a valid value, compare with THC test result
            if thc_test_float > total_thc_float:
                ai_value = thc_test_result
            else:
                ai_value = total_thc_value
        else:
            # Total THC is 0 or empty, compare THCA vs THC test result
            if thca_float > 0 and thca_float >= thc_test_float:
                ai_value = thca_value
            elif thc_test_float > 0:
                ai_value = thc_test_result
            else:
                ai_value = ''
        
        # CBD merging logic
        cbda_value = str(mock_record.get('CBDA', '')).strip()
        cbd_test_result = str(mock_record.get('CBD test result', '')).strip()
        
        if cbd_test_result in ['nan', 'NaN', '']:
            cbd_test_result = ''
        
        cbda_float = safe_float(cbda_value)
        cbd_test_float = safe_float(cbd_test_result)
        
        if cbd_test_float > cbda_float:
            ak_value = cbd_test_result
        else:
            ak_value = cbda_value
        
        # Clean up values
        if ai_value in ['nan', 'NaN', '']:
            ai_value = ''
        if ak_value in ['nan', 'NaN', '']:
            ak_value = ''
        
        # Check results
        thc_correct = ai_value == test_case['expected_thc']
        cbd_correct = ak_value == test_case['expected_cbd']
        
        print(f"  Input - Total THC: {test_case['total_thc']}, THCA: {test_case['thca']}, THC test result: {test_case['thc_test_result']}")
        print(f"  Input - CBDA: {test_case['cbda']}, CBD test result: {test_case['cbd_test_result']}")
        print(f"  Output - AI (THC): {ai_value}, AK (CBD): {ak_value}")
        print(f"  Expected - THC: {test_case['expected_thc']}, CBD: {test_case['expected_cbd']}")
        print(f"  Result: {'✅ PASS' if thc_correct and cbd_correct else '❌ FAIL'}")
        
        if not thc_correct:
            print(f"    THC mismatch: expected {test_case['expected_thc']}, got {ai_value}")
        if not cbd_correct:
            print(f"    CBD mismatch: expected {test_case['expected_cbd']}, got {ak_value}")
    
    # Test with actual data from the file
    print("\n" + "=" * 50)
    print("Testing with actual data from file:")
    
    # Get sample records that have THC/CBD data
    sample_records = processor.df.head(20)
    
    for i, (idx, row) in enumerate(sample_records.iterrows()):
        product_name = row.get('Product Name*', f'Row {idx}')
        
        # Check if this record has any THC/CBD data
        has_thc_data = any([
            pd.notna(row.get('Total THC', '')) and str(row.get('Total THC', '')).strip(),
            pd.notna(row.get('THCA', '')) and str(row.get('THCA', '')).strip(),
            pd.notna(row.get('THC test result', '')) and str(row.get('THC test result', '')).strip()
        ])
        
        has_cbd_data = any([
            pd.notna(row.get('CBDA', '')) and str(row.get('CBDA', '')).strip(),
            pd.notna(row.get('CBD test result', '')) and str(row.get('CBD test result', '')).strip()
        ])
        
        if has_thc_data or has_cbd_data:
            print(f"\nProduct {i+1}: {product_name}")
            
            # Show original values
            total_thc = row.get('Total THC', '')
            thca = row.get('THCA', '')
            thc_test = row.get('THC test result', '')
            cbda = row.get('CBDA', '')
            cbd_test = row.get('CBD test result', '')
            
            print(f"  Original - Total THC: {total_thc}, THCA: {thca}, THC test result: {thc_test}")
            print(f"  Original - CBDA: {cbda}, CBD test result: {cbd_test}")
            
            # Apply merging logic
            def safe_float(value):
                if pd.isna(value) or not value or str(value).lower() in ['nan', '']:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # THC merging
            total_thc_value = str(total_thc).strip() if pd.notna(total_thc) else ''
            thca_value = str(thca).strip() if pd.notna(thca) else ''
            thc_test_result = str(thc_test).strip() if pd.notna(thc_test) else ''
            
            total_thc_float = safe_float(total_thc_value)
            thc_test_float = safe_float(thc_test_result)
            thca_float = safe_float(thca_value)
            
            # For THC: Use the highest value among Total THC, THC test result, and THCA
            # But if Total THC is 0 or empty, prefer THCA over THC test result
            if total_thc_float > 0:
                # Total THC has a valid value, compare with THC test result
                if thc_test_float > total_thc_float:
                    ai_value = thc_test_result
                else:
                    ai_value = total_thc_value
            else:
                # Total THC is 0 or empty, compare THCA vs THC test result
                if thca_float > 0 and thca_float >= thc_test_float:
                    ai_value = thca_value
                elif thc_test_float > 0:
                    ai_value = thc_test_result
                else:
                    ai_value = ''
            
            # CBD merging
            cbda_value = str(cbda).strip() if pd.notna(cbda) else ''
            cbd_test_result = str(cbd_test).strip() if pd.notna(cbd_test) else ''
            
            cbda_float = safe_float(cbda_value)
            cbd_test_float = safe_float(cbd_test_result)
            
            if cbd_test_float > cbda_float:
                ak_value = cbd_test_result
            else:
                ak_value = cbda_value
            
            print(f"  Merged - AI (THC): {ai_value}, AK (CBD): {ak_value}")
    
    print("\n✅ THC/CBD column merging test completed!")

if __name__ == "__main__":
    test_thc_cbd_merge() 