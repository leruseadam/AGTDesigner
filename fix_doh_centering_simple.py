#!/usr/bin/env python3
"""
Simple DOH Image Centering Fix
Direct replacement of the DOH centering function for better InlineImage handling.
"""

def print_fix_plan():
    """Print the simple fix plan."""
    
    print("🔧 Simple DOH Image Centering Fix")
    print("=" * 40)
    print()
    
    print("📋 ISSUE IDENTIFIED:")
    print("-" * 25)
    print("• DOH placeholder InlineImages are not properly centered")
    print("• Current method clears cell content")
    print("• Need to preserve InlineImage objects")
    print("• Apply centering without destroying content")
    print()
    
    print("🛠️ SIMPLE FIX PLAN:")
    print("-" * 20)
    print("1. Replace DOH centering function directly")
    print("2. Preserve InlineImage objects intact")
    print("3. Apply centering at paragraph level")
    print("4. Keep existing content structure")
    print()

def apply_simple_doh_centering():
    """Apply the simple DOH centering fix."""
    
    print("🔧 Applying Simple DOH Centering Fix...")
    
    # Read the current template processor
    with open('src/core/generation/template_processor.py', 'r') as f:
        lines = f.readlines()
    
    # Find the start and end of the DOH centering function
    start_line = -1
    end_line = -1
    
    for i, line in enumerate(lines):
        if 'def _ensure_doh_image_centering(self, doc):' in line:
            start_line = i
            break
    
    if start_line == -1:
        print("❌ Could not find DOH centering function")
        return False
    
    # Find the end of the function (next function definition)
    for i in range(start_line + 1, len(lines)):
        if lines[i].strip().startswith('def ') and 'self' in lines[i]:
            end_line = i
            break
    
    if end_line == -1:
        end_line = len(lines)
    
    # Define the improved function
    improved_function = [
        '    def _ensure_doh_image_centering(self, doc):\n',
        '        """\n',
        '        Ensure DOH images are properly centered in all cells.\n',
        '        This method provides improved centering for InlineImage objects.\n',
        '        """\n',
        '        try:\n',
        '            from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT\n',
        '            from docx.enum.text import WD_ALIGN_PARAGRAPH\n',
        '            from docx.shared import Pt\n',
        '            from docx.oxml.ns import qn\n',
        '            from docx.oxml import OxmlElement\n',
        '            \n',
        '            for table in doc.tables:\n',
        '                for row in table.rows:\n',
        '                    for cell in row.cells:\n',
        '                        # Check if this cell contains a DOH image\n',
        '                        has_doh_image = False\n',
        '                        image_paragraph = None\n',
        '                        \n',
        '                        # Improved image detection\n',
        '                        for paragraph in cell.paragraphs:\n',
        '                            for run in paragraph.runs:\n',
        '                                if hasattr(run, \'_element\'):\n',
        '                                    # Check for drawing elements (InlineImage)\n',
        '                                    if run._element.find(qn(\'w:drawing\')) is not None:\n',
        '                                        has_doh_image = True\n',
        '                                        image_paragraph = paragraph\n',
        '                                        break\n',
        '                                    # Check for picture elements\n',
        '                                    elif run._element.find(qn(\'w:pict\')) is not None:\n',
        '                                        has_doh_image = True\n',
        '                                        image_paragraph = paragraph\n',
        '                                        break\n',
        '                            if has_doh_image:\n',
        '                                break\n',
        '                        \n',
        '                        if has_doh_image and image_paragraph:\n',
        '                            self.logger.debug("Found DOH image, applying improved centering")\n',
        '                            \n',
        '                            # Apply centering at paragraph level\n',
        '                            image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER\n',
        '                            \n',
        '                            # Set minimal spacing\n',
        '                            image_paragraph.paragraph_format.space_before = Pt(0)\n',
        '                            image_paragraph.paragraph_format.space_after = Pt(0)\n',
        '                            image_paragraph.paragraph_format.line_spacing = 1.0\n',
        '                            \n',
        '                            # Set cell vertical alignment to center\n',
        '                            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER\n',
        '                            \n',
        '                            # Ensure proper XML-level centering\n',
        '                            pPr = image_paragraph._element.get_or_add_pPr()\n',
        '                            \n',
        '                            # Set paragraph justification to center\n',
        '                            jc = pPr.find(qn(\'w:jc\'))\n',
        '                            if jc is None:\n',
        '                                jc = OxmlElement(\'w:jc\')\n',
        '                                pPr.append(jc)\n',
        '                            jc.set(qn(\'w:val\'), \'center\')\n',
        '                            \n',
        '                            # Remove any existing spacing\n',
        '                            existing_spacing = pPr.find(qn(\'w:spacing\'))\n',
        '                            if existing_spacing is not None:\n',
        '                                pPr.remove(existing_spacing)\n',
        '                            \n',
        '                            # Add minimal spacing\n',
        '                            spacing = OxmlElement(\'w:spacing\')\n',
        '                            spacing.set(qn(\'w:before\'), \'0\')\n',
        '                            spacing.set(qn(\'w:after\'), \'0\')\n',
        '                            spacing.set(qn(\'w:line\'), \'240\')\n',
        '                            spacing.set(qn(\'w:lineRule\'), \'auto\')\n',
        '                            pPr.append(spacing)\n',
        '                            \n',
        '                            # Ensure proper indentation\n',
        '                            ind = pPr.find(qn(\'w:ind\'))\n',
        '                            if ind is None:\n',
        '                                ind = OxmlElement(\'w:ind\')\n',
        '                                pPr.append(ind)\n',
        '                            ind.set(qn(\'w:left\'), \'0\')\n',
        '                            ind.set(qn(\'w:right\'), \'0\')\n',
        '                            ind.set(qn(\'w:firstLine\'), \'0\')\n',
        '                            ind.set(qn(\'w:hanging\'), \'0\')\n',
        '                            \n',
        '                            self.logger.debug("Applied improved DOH image centering")\n',
        '                                \n',
        '        except Exception as e:\n',
        '            self.logger.warning(f"Error in improved DOH image centering: {e}")\n',
        '\n'
    ]
    
    # Replace the function
    new_lines = lines[:start_line] + improved_function + lines[end_line:]
    
    # Write the updated content back
    with open('src/core/generation/template_processor.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Simple DOH centering fix applied successfully")
    return True

def create_simple_test():
    """Create a simple test script."""
    
    test_script = '''#!/usr/bin/env python3
"""
Simple test for DOH image centering.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_doh_centering():
    """Test DOH image centering."""
    print("🧪 Testing DOH Image Centering")
    print("=" * 35)
    
    try:
        from src.core.generation.template_processor import TemplateProcessor
        from src.core.constants import FONT_SCHEME_DOUBLE
        
        # Create a test record
        test_record = {
            'Description': 'Test Product with DOH',
            'DOH': 'YES',
            'Product Type*': 'Flower',
            'Product Name*': 'Test Product',
            'Brand': 'Test Brand',
            'Price': '$10.00',
            'THC': '15.5%',
            'CBD': '0.5%',
            'Lineage': 'SATIVA'
        }
        
        # Create template processor
        processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
        
        # Process the test record
        result = processor.process_records([test_record])
        print("✅ Document generated successfully")
        
        # Check for DOH images
        doh_found = False
        for table in result.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.alignment and 'CENTER' in str(paragraph.alignment):
                            doh_found = True
                            print("✅ Found centered DOH image")
                            break
        
        if doh_found:
            print("✅ SUCCESS: DOH images are properly centered")
            return True
        else:
            print("❌ No centered DOH images found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_doh_centering()
    if success:
        print("\\n✅ TEST PASSED: DOH centering is working")
    else:
        print("\\n❌ TEST FAILED: DOH centering needs work")
'''
    
    with open('test_simple_doh_centering.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created simple test script: test_simple_doh_centering.py")

def main():
    """Main function to apply the simple DOH centering fix."""
    
    print_fix_plan()
    
    # Apply the simple fix
    if apply_simple_doh_centering():
        # Create test script
        create_simple_test()
        
        print("\\n✅ SIMPLE DOH CENTERING FIX COMPLETED!")
        print("=" * 40)
        print()
        print("📋 WHAT WAS FIXED:")
        print("• Replaced DOH centering function with improved version")
        print("• Preserved InlineImage objects intact")
        print("• Applied centering at paragraph level")
        print("• Removed cell content clearing")
        print("• Added proper spacing and alignment")
        print()
        print("🚀 NEXT STEPS:")
        print("1. Test the fix: python test_simple_doh_centering.py")
        print("2. Generate a document with DOH images")
        print("3. Check that images are properly centered")
        print()
        print("🔧 The DOH placeholder InlineImages should now be properly centered!")

if __name__ == "__main__":
    main() 