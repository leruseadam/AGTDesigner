#!/usr/bin/env python3

import os
import sys
from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def update_template_dimensions(template_path, template_type):
    """Update template file dimensions to 3.4 x 2.4 inches"""
    print(f"Updating {template_path}...")
    
    # Load the document
    doc = Document(template_path)
    
    # Update each table in the document
    for table in doc.tables:
        print(f"  Found table with {len(table.rows)} rows and {len(table.columns)} columns")
        
        # Set table width based on template type
        if template_type == 'horizontal':
            # Horizontal: 3 columns of 3.4/3 = 1.133 inches each = 3.4 inches total
            total_width = 3.4
            col_width = total_width / 3  # 1.133 inches per column
        elif template_type == 'vertical':
            # Vertical: 3 columns of 2.4/3 = 0.8 inches each = 2.4 inches total
            total_width = 2.4
            col_width = total_width / 3  # 0.8 inches per column
        else:
            # Default to horizontal dimensions
            total_width = 3.4
            col_width = total_width / 3
        
        # Set row height
        row_height = 2.4  # 2.4 inches for all templates
        
        # Update table grid
        tblGrid = table._element.find(qn('w:tblGrid'))
        if tblGrid is not None:
            # Remove existing grid
            tblGrid.getparent().remove(tblGrid)
        
        # Create new grid with correct dimensions
        tblGrid = OxmlElement('w:tblGrid')
        for _ in range(len(table.columns)):
            gridCol = OxmlElement('w:gridCol')
            gridCol.set(qn('w:w'), str(int(col_width * 1440)))  # Convert to twips
            tblGrid.append(gridCol)
        table._element.insert(0, tblGrid)
        
        # Update row heights
        for row in table.rows:
            row.height = Inches(row_height)
            row.height_rule = 1  # WD_ROW_HEIGHT_RULE.EXACTLY
        
        # Update cell widths
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                tcW = tcPr.find(qn('w:tcW'))
                if tcW is None:
                    tcW = OxmlElement('w:tcW')
                    tcPr.append(tcW)
                tcW.set(qn('w:w'), str(int(col_width * 1440)))
                tcW.set(qn('w:type'), 'dxa')
        
        print(f"  Updated table: {len(table.columns)} columns × {len(table.rows)} rows")
        print(f"  Column width: {col_width:.3f} inches")
        print(f"  Row height: {row_height:.3f} inches")
        print(f"  Total width: {total_width:.3f} inches")
    
    # Save the updated document
    doc.save(template_path)
    print(f"  Saved updated template: {template_path}")

def main():
    template_dir = "src/core/generation/templates"
    
    # Define which templates to update and their types
    templates_to_update = [
        ("horizontal.docx", "horizontal"),
        ("vertical.docx", "vertical"),
        ("mini.docx", "mini"),
        ("double.docx", "double"),
        ("InventorySlips.docx", "inventory")
    ]
    
    print("Updating template dimensions to 3.4 x 2.4 inches...")
    print("=" * 50)
    
    for filename, template_type in templates_to_update:
        template_path = os.path.join(template_dir, filename)
        if os.path.exists(template_path):
            try:
                update_template_dimensions(template_path, template_type)
            except Exception as e:
                print(f"Error updating {filename}: {e}")
        else:
            print(f"Template not found: {template_path}")
    
    print("\nTemplate update completed!")

if __name__ == "__main__":
    main() 