#!/usr/bin/env python3
"""
Script to check the template content and see how fields are arranged.
"""

from docx import Document

def check_template():
    doc = Document('src/core/generation/templates/double.docx')
    print("Template content:")
    
    for i, row in enumerate(doc.tables[0].rows):
        print(f"Row {i}:")
        for j, cell in enumerate(row.cells):
            print(f"  Cell {j}: \"{cell.text}\"")

if __name__ == "__main__":
    check_template()
