#!/usr/bin/env python3
"""
Live debug script to generate an actual template and check font sizes in the output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_live_template_generation():
    """Generate an actual template and check the font sizes in the output."""
    
    print("=== LIVE TEMPLATE GENERATION DEBUG ===")
    print()
    
    try:
        from src.core.generation.template_processor import TemplateProcessor
        from src.core.generation.tag_generator import TagGenerator
        from src.core.generation.unified_font_sizing import get_font_size_by_marker
        from docx import Document
        from docx.shared import Pt
        
        print("✅ All imports successful")
        print()
        
        # Test data
        test_data = {
            "Ratio_or_THC_CBD": "THC: 15.2% | CBD: 0.8%",
            "ProductName": "Test Product",
            "ProductStrain": "Test Strain",
            "ProductBrand": "Test Brand",
            "Price": "$25.00",
            "Lineage": "Test Lineage",
            "DOH": "{{Label1.DOH}}"
        }
        
        print("📊 Test data:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        print()
        
        # Test tag generation
        print("1. Testing tag generation:")
        tag_generator = TagGenerator()
        label_data = tag_generator.generate_label_data(test_data)
        
        print("   Generated label data:")
        for key, value in label_data.items():
            if key == "Ratio_or_THC_CBD":
                print(f"   {key}: {value}")
        print()
        
        # Test font sizing directly
        print("2. Testing unified font sizing directly:")
        thc_cbd_content = test_data["Ratio_or_THC_CBD"]
        
        # Test with different marker types
        markers_to_test = ["THC_CBD", "RATIO_OR_THC_CBD", "Ratio_or_THC_CBD"]
        
        for marker in markers_to_test:
            font_size = get_font_size_by_marker(thc_cbd_content, marker, "horizontal")
            print(f"   {marker}: {font_size.pt}pt")
        
        print()
        
        # Test template processor
        print("3. Testing template processor:")
        template_processor = TemplateProcessor("horizontal", scale_factor=1.0)
        
        # Check if the processor has the correct font sizing method
        if hasattr(template_processor, '_get_template_specific_font_size'):
            font_size = template_processor._get_template_specific_font_size(thc_cbd_content, "THC_CBD")
            print(f"   Template processor font size: {font_size.pt}pt")
        else:
            print("   ❌ Template processor missing _get_template_specific_font_size method")
        
        print()
        
        # Generate actual template
        print("4. Generating actual template:")
        try:
            # Create a simple test template
            doc = Document()
            paragraph = doc.add_paragraph()
            
            # Add the THC/CBD content with markers
            thc_cbd_text = label_data["Ratio_or_THC_CBD"]
            print(f"   Adding text: {thc_cbd_text}")
            
            # Process the paragraph with the template processor
            template_processor._process_paragraph_for_marker_template_specific(paragraph, "THC_CBD")
            
            print(f"   ✅ Template generated successfully")
            print(f"   📄 Paragraph has {len(paragraph.runs)} runs")
            
            # Check font sizes in the generated content
            print("   📊 Font sizes in generated content:")
            for i, run in enumerate(paragraph.runs):
                if run.font.size:
                    print(f"      Run {i+1}: {run.font.size.pt}pt - '{run.text[:30]}...'")
                else:
                    print(f"      Run {i+1}: No font size - '{run.text[:30]}...'")
            
            # Save the test document
            output_path = "debug_thc_cbd_output.docx"
            doc.save(output_path)
            print(f"   💾 Test document saved to: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Error generating template: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Check if there are any hardcoded font sizes in the code
        print("5. Checking for any hardcoded font sizes:")
        
        # Check unified_font_sizing.py for any 7.5pt values
        from src.core.generation.unified_font_sizing import FONT_SIZING_CONFIG
        
        found_7pt5 = []
        for field_type, configs in FONT_SIZING_CONFIG.items():
            for template_type, thresholds in configs.items():
                for threshold, size in thresholds:
                    if size == 7.5:
                        found_7pt5.append(f"{field_type}.{template_type}")
        
        if found_7pt5:
            print(f"   ⚠️  Found 7.5pt in: {', '.join(found_7pt5)}")
        else:
            print("   ✅ No 7.5pt found in unified font sizing config")
        
        print()
        print("=== DEBUG COMPLETE ===")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_live_template_generation()
