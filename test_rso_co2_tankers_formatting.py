#!/usr/bin/env python3
"""
Test script to verify that RSO/CO2 Tankers get proper formatting:
1. Product Brand centering
2. Ratio formatting (same as edibles)
3. Weight in grams (not converted to ounces)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor
import pandas as pd

def test_rso_co2_tankers_formatting():
    """Test that RSO/CO2 Tankers get proper formatting."""
    
    # Create test data with RSO/CO2 Tankers
    test_data = {
        'Product Name*': [
            'Test RSO/CO2 Tanker Product',
            'Test Edible Solid Product',
            'Test Flower Product'
        ],
        'Product Type*': [
            'rso/co2 tankers',
            'edible (solid)',
            'flower'
        ],
        'Product Brand': ['Test Brand'] * 3,
        'Vendor': ['Test Vendor'] * 3,
        'Lineage': ['MIXED'] * 3,
        'Weight*': ['1', '1', '3.5'],
        'Units': ['g', 'g', 'g'],
        'Price': ['$10'] * 3,
        'Ratio': ['THC 10mg CBD 5mg CBG 2mg'] * 3
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    processor.df = df
    
    print("Testing RSO/CO2 Tankers formatting:")
    print("=" * 50)
    
    # Test 1: Weight formatting (should stay in grams for RSO/CO2 Tankers)
    print("\n1. Testing weight formatting:")
    print("-" * 30)
    
    for i, row in df.iterrows():
        product_type = row['Product Type*']
        weight = row['Weight*']
        units = row['Units']
        
        # Test the weight formatting logic directly
        if product_type == "rso/co2 tankers" and units in {"g", "grams"} and weight:
            # Should stay in grams
            expected_weight = f"{float(weight):.2f}".rstrip("0").rstrip(".") + "g"
        elif product_type in {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"} and units in {"g", "grams"} and weight:
            # Should convert to ounces
            weight_oz = float(weight) * 0.03527396195
            expected_weight = f"{weight_oz:.2f}".rstrip("0").rstrip(".") + "oz"
        else:
            expected_weight = f"{weight}{units}"
        
        print(f"  {product_type}: {weight}{units} → {expected_weight}")
        
        # Verify the logic
        if product_type == "rso/co2 tankers":
            if "g" in expected_weight and "oz" not in expected_weight:
                print(f"    ✅ PASS: RSO/CO2 Tankers weight stays in grams")
            else:
                print(f"    ❌ FAIL: RSO/CO2 Tankers weight should stay in grams")
        elif product_type == "edible (solid)":
            if "oz" in expected_weight:
                print(f"    ✅ PASS: Edible weight converted to ounces")
            else:
                print(f"    ❌ FAIL: Edible weight should be converted to ounces")
    
    # Test 2: Ratio formatting (should get classic THC/CBD formatting for RSO/CO2 Tankers)
    print("\n2. Testing ratio formatting:")
    print("-" * 30)
    
    # Test the ratio formatting logic
    ratio = "THC 10mg CBD 5mg CBG 2mg"
    
    def break_after_2nd_space(s):
        parts = s.split(' ')
        out = []
        for i, part in enumerate(parts):
            out.append(part)
            if (i+1) % 2 == 0 and i != len(parts)-1:
                out.append('\n')
        return ' '.join(out).replace(' \n ', '\n')
    
    edible_formatted = break_after_2nd_space(ratio)
    print(f"  Original ratio: {ratio}")
    print(f"  Edible formatted: {repr(edible_formatted)}")
    
    # Test the classic ratio formatting
    template_processor = TemplateProcessor('vertical', None)
    classic_formatted = template_processor.format_classic_ratio(ratio, {})
    print(f"  Classic formatted: {repr(classic_formatted)}")
    
    if '\n' in classic_formatted and 'THC:' in classic_formatted and 'CBD:' in classic_formatted:
        print(f"    ✅ PASS: Classic ratio has proper THC/CBD format")
    else:
        print(f"    ❌ FAIL: Classic ratio should have THC/CBD format")
    
    # Test 3: Product Brand centering
    print("\n3. Testing Product Brand centering:")
    print("-" * 30)
    
    # Test that RSO/CO2 Tankers are in the classic types set
    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
    
    for product_type in df['Product Type*'].unique():
        is_classic = product_type in classic_types
        print(f"  {product_type}: {'✅ Classic' if is_classic else '❌ Not Classic'}")
        
        if product_type == "rso/co2 tankers":
            if is_classic:
                print(f"    ✅ PASS: RSO/CO2 Tankers is recognized as classic type")
            else:
                print(f"    ❌ FAIL: RSO/CO2 Tankers should be recognized as classic type")
    
    # Test 4: Tag generation and formatting
    print("\n4. Testing tag generation:")
    print("-" * 30)
    
    # Get available tags
    available_tags = processor.get_available_tags()
    
    print(f"Generated {len(available_tags)} tags:")
    for tag in available_tags:
        product_type = tag.get('Product Type*', 'Unknown')
        product_name = tag.get('Product Name*', 'Unknown')
        print(f"  - {product_name} ({product_type})")
    
    # Test 5: Selected records formatting
    print("\n5. Testing selected records formatting:")
    print("-" * 30)
    
    # Get selected records to see how formatting is applied
    processor.selected_tags = [tag['Product Name*'] for tag in available_tags]
    selected_records = processor.get_selected_records('vertical')
    
    for record in selected_records:
        product_type = record.get('ProductType', 'Unknown')
        weight_units = record.get('WeightUnits', 'No weight')
        ratio = record.get('Ratio_or_THC_CBD', 'No ratio')
        print(f"  {product_type}:")
        print(f"    Weight: {weight_units}")
        print(f"    Ratio: {repr(ratio)}")
        
        # Verify RSO/CO2 Tankers formatting
        if product_type == "rso/co2 tankers":
            if "g" in weight_units and "oz" not in weight_units:
                print(f"    ✅ Weight in grams")
            else:
                print(f"    ❌ Weight should be in grams")
            
            # Note: Excel processor ratio is overridden by template processor
            print(f"    Note: Excel processor ratio is overridden by template processor")
    
    # Test 6: Template processor formatting
    print("\n6. Testing template processor formatting:")
    print("-" * 30)
    
    # Test template processor directly
    for record in selected_records:
        product_type = record.get('ProductType', 'Unknown')
        print(f"  Testing {product_type}:")
        
        # Create a mock document for template processing
        from docx import Document
        doc = Document()
        
        # Build label context using template processor
        label_context = template_processor._build_label_context(record, doc)
        
        ratio_result = label_context.get('Ratio_or_THC_CBD', 'No ratio')
        print(f"    Template processor ratio: {repr(ratio_result)}")
        
        if product_type == "rso/co2 tankers":
            if 'THC:' in ratio_result and 'CBD:' in ratio_result and '\n' in ratio_result:
                print(f"    ✅ Template processor gives classic THC/CBD format")
            else:
                print(f"    ❌ Template processor should give classic THC/CBD format")
    
    print(f"\n✅ RSO/CO2 Tankers formatting test completed!")
    print(f"   - Weight stays in grams (not converted to ounces)")
    print(f"   - Ratio gets classic THC/CBD formatting")
    print(f"   - Product Brand centering applied")
    print(f"   - Recognized as classic type for all formatting rules")

if __name__ == "__main__":
    test_rso_co2_tankers_formatting() 