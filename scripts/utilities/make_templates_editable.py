#!/usr/bin/env python3
"""
Utility script to make Word templates editable by removing fixed table layout constraints.
This allows you to manually resize tables in Microsoft Word.

Usage:
    python scripts/utilities/make_templates_editable.py [template_path]
    
If no path is provided, it will update all templates in src/core/generation/templates/
"""

import sys
import os
from pathlib import Path
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def make_template_editable(template_path):
    """Remove fixed table layout and absolute widths to allow manual resizing in Word."""
    try:
        print(f"Processing: {template_path}")
        doc = Document(template_path)
        
        modified = False
        for table_idx, table in enumerate(doc.tables):
            table_modified = False
            
            # Get table properties
            tblPr = table._element.find(qn('w:tblPr'))
            if tblPr is not None:
                # 1. Remove fixed layout
                tblLayout = tblPr.find(qn('w:tblLayout'))
                if tblLayout is not None:
                    layout_type = tblLayout.get(qn('w:type'))
                    if layout_type == 'fixed':
                        # Remove fixed layout to allow autofit/resizing
                        tblLayout.getparent().remove(tblLayout)
                        table_modified = True
                        print(f"  ✓ Removed fixed layout from table {table_idx + 1}")
                
                # 2. Remove absolute width constraints (this is what prevents resizing!)
                tblW = tblPr.find(qn('w:tblW'))
                if tblW is not None:
                    width_type = tblW.get(qn('w:type'))
                    if width_type == 'dxa':  # Absolute width in twips
                        # Remove absolute width to allow resizing
                        tblW.getparent().remove(tblW)
                        table_modified = True
                        print(f"  ✓ Removed absolute width constraint from table {table_idx + 1}")
                
                # 3. Remove fixed column widths from grid
                tblGrid = table._element.find(qn('w:tblGrid'))
                if tblGrid is not None:
                    grid_cols = tblGrid.findall(qn('w:gridCol'))
                    for col in grid_cols:
                        if col.get(qn('w:w')):  # If column has fixed width
                            # Remove the width attribute
                            if qn('w:w') in col.attrib:
                                del col.attrib[qn('w:w')]
                            table_modified = True
                    if table_modified:
                        print(f"  ✓ Removed fixed column widths from table {table_idx + 1}")
            
            # 4. Remove fixed cell widths
            for row in table.rows:
                for cell in row.cells:
                    tcPr = cell._element.find(qn('w:tcPr'))
                    if tcPr is not None:
                        tcW = tcPr.find(qn('w:tcW'))
                        if tcW is not None:
                            width_type = tcW.get(qn('w:type'))
                            if width_type == 'dxa':  # Absolute width
                                tcW.getparent().remove(tcW)
                                table_modified = True
            
            # 5. Enable autofit to allow resizing
            table.autofit = True
            if hasattr(table, 'allow_autofit'):
                table.allow_autofit = True
            
            if table_modified:
                modified = True
        
        if modified:
            # Save the modified template
            doc.save(template_path)
            print(f"  ✓ Saved: {template_path}")
            return True
        else:
            print(f"  - No changes needed (already editable)")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {template_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process templates."""
    # Get template directory
    script_dir = Path(__file__).parent.parent.parent
    template_dir = script_dir / 'src' / 'core' / 'generation' / 'templates'
    
    if len(sys.argv) > 1:
        # Process specific template
        template_path = Path(sys.argv[1])
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            sys.exit(1)
        make_template_editable(template_path)
    else:
        # Process all templates in the templates directory
        print(f"Making all templates editable in: {template_dir}")
        print()
        
        template_files = list(template_dir.glob('*.docx'))
        # Exclude temporary Word files (starting with ~$)
        template_files = [f for f in template_files if not f.name.startswith('~$')]
        
        if not template_files:
            print("No template files found!")
            sys.exit(1)
        
        modified_count = 0
        for template_file in template_files:
            if make_template_editable(template_file):
                modified_count += 1
            print()
        
        print(f"Completed! Modified {modified_count} out of {len(template_files)} templates.")
        print()
        print("You can now edit and resize tables in Microsoft Word.")
        print("Note: After editing, the templates will still work for label generation,")
        print("but tables may expand during generation if not properly sized.")

if __name__ == '__main__':
    main()

