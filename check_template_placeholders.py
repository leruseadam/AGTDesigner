#!/usr/bin/env python3
"""
Check what placeholders are in the double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from docx import Document
import re

def check_template_placeholders():
    """Check what placeholders are in the double template."""
    print("🔍 Checking Double Template Placeholders")
    print("=" * 40)
    
    template_path = "src/core/generation/templates/double.docx"
    print(f"Template path: {template_path}")
    print()
    
    if not os.path.exists(template_path):
        print(f"❌ ERROR: Template file not found: {template_path}")
        return
    
    # Load the template document
    doc = Document(template_path)
    
    # Find all placeholders in the document
    placeholders = set()
    
    print("📋 Searching for placeholders...")
    
    # Check tables
    for table_idx, table in enumerate(doc.tables):
        print(f"  Table {table_idx + 1}:")
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                if cell_text:
                    print(f"    Cell [{row_idx},{cell_idx}]: '{cell_text}'")
                    
                    # Find placeholders in this cell
                    placeholder_matches = re.findall(r'\{\{.*?\}\}', cell_text)
                    for match in placeholder_matches:
                        placeholders.add(match)
                        print(f"      → Found placeholder: {match}")
    
    # Check paragraphs outside tables
    for para_idx, paragraph in enumerate(doc.paragraphs):
        para_text = paragraph.text.strip()
        if para_text:
            print(f"  Paragraph {para_idx + 1}: '{para_text}'")
            
            # Find placeholders in this paragraph
            placeholder_matches = re.findall(r'\{\{.*?\}\}', para_text)
            for match in placeholder_matches:
                placeholders.add(match)
                print(f"    → Found placeholder: {match}")
    
    print(f"\n📊 Summary:")
    print(f"  Total unique placeholders found: {len(placeholders)}")
    print()
    
    if placeholders:
        print("📋 All placeholders found:")
        for placeholder in sorted(placeholders):
            print(f"  • {placeholder}")
    else:
        print("❌ No placeholders found in template!")
    
    # Check specifically for DOH-related placeholders
    doh_placeholders = [p for p in placeholders if 'DOH' in p]
    print(f"\n🔍 DOH-related placeholders: {len(doh_placeholders)}")
    for placeholder in doh_placeholders:
        print(f"  • {placeholder}")

if __name__ == "__main__":
    check_template_placeholders() 