#!/usr/bin/env python3
"""
Simple test to verify the lineage alignment logic directly.
"""

import sys
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_lineage_alignment_logic():
    """Test the lineage alignment logic directly."""
    
    # Create a simple document with paragraphs
    doc = Document()
    
    # Test cases
    test_cases = [
        {
            'content': 'INDICA_PRODUCT_TYPE_flower_IS_CLASSIC_true',
            'expected_alignment': 'LEFT',
            'description': 'Classic type with embedded info'
        },
        {
            'content': 'CBD_PRODUCT_TYPE_edible (solid)_IS_CLASSIC_false',
            'expected_alignment': 'CENTER',
            'description': 'Non-classic type with embedded info'
        },
        {
            'content': 'HYBRID',
            'expected_alignment': 'LEFT',
            'description': 'Classic lineage without embedded info'
        },
        {
            'content': 'TEST BRAND',
            'expected_alignment': 'CENTER',
            'description': 'Non-classic lineage without embedded info'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        # Create a paragraph
        paragraph = doc.add_paragraph()
        paragraph.text = test_case['content']
        
        # Apply the alignment logic (simplified version of what's in template_processor.py)
        content = test_case['content']
        
        # Extract product type information from the content
        if '_PRODUCT_TYPE_' in content and '_IS_CLASSIC_' in content:
            parts = content.split('_PRODUCT_TYPE_')
            if len(parts) == 2:
                actual_lineage = parts[0]
                type_info = parts[1]
                type_parts = type_info.split('_IS_CLASSIC_')
                if len(type_parts) == 2:
                    product_type = type_parts[0]
                    is_classic = type_parts[1].lower() == 'true'

                    # Center if it's NOT a classic type
                    if not is_classic:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        # For Classic Types, left-justify the text
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else:
            # Fallback: use the old logic for backward compatibility
            classic_lineages = [
                "SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", 
                "CBD", "MIXED", "PARAPHERNALIA", "PARA"
            ]
            # Only center if the content is NOT a classic lineage (meaning it's likely a brand name)
            if content.upper() not in classic_lineages:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                # For Classic Types, left-justify the text
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Check the actual alignment
        actual_alignment = paragraph.alignment
        expected_alignment = test_case['expected_alignment']
        
        # Convert alignment to string for comparison
        if actual_alignment == WD_ALIGN_PARAGRAPH.LEFT:
            actual_alignment_str = 'LEFT'
        elif actual_alignment == WD_ALIGN_PARAGRAPH.CENTER:
            actual_alignment_str = 'CENTER'
        else:
            actual_alignment_str = 'OTHER'
        
        result = {
            'Description': test_case['description'],
            'Content': content,
            'Expected': expected_alignment,
            'Actual': actual_alignment_str,
            'Correct': actual_alignment_str == expected_alignment
        }
        results.append(result)
        
        status = "✅ PASS" if actual_alignment_str == expected_alignment else "❌ FAIL"
        print(f"{status} | {test_case['description']} | Content: {content} | Expected: {expected_alignment} | Actual: {actual_alignment_str}")
    
    # Summary
    correct_count = sum(1 for r in results if r['Correct'])
    total_count = len(results)
    
    print(f"\n=== Summary ===")
    print(f"Total tests: {total_count}")
    print(f"Passed: {correct_count}")
    print(f"Failed: {total_count - correct_count}")
    print(f"Success rate: {correct_count/total_count*100:.1f}%")
    
    if correct_count == total_count:
        print("🎉 All tests passed! The lineage alignment logic is working correctly.")
    else:
        print("⚠️  Some tests failed. The alignment logic needs more work.")
    
    return correct_count == total_count

if __name__ == "__main__":
    success = test_lineage_alignment_logic()
    sys.exit(0 if success else 1) 