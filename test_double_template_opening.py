#!/usr/bin/env python3
"""
Test script to verify that the double template can be opened from the template folder.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from pathlib import Path

def test_double_template_opening():
    """Test that the double template can be opened successfully."""
    print("Testing Double Template Opening")
    print("=" * 40)
    
    try:
        # Create template processor for double template
        print("Creating TemplateProcessor for 'double' template...")
        processor = TemplateProcessor('double', {}, 1.0)
        
        # Get the template path
        template_path = processor._get_template_path()
        print(f"✓ Template path resolved: {template_path}")
        
        # Check if the file exists
        if template_path.exists():
            print(f"✓ Template file exists: {template_path}")
            
            # Check file size
            file_size = template_path.stat().st_size
            print(f"✓ Template file size: {file_size} bytes")
            
            # Try to open and read the file
            with open(template_path, 'rb') as f:
                content = f.read()
                print(f"✓ Template file can be read: {len(content)} bytes")
            
            # Check if the expanded template buffer is available
            if hasattr(processor, '_expanded_template_buffer'):
                buffer = processor._expanded_template_buffer
                if buffer:
                    print(f"✓ Expanded template buffer available: {len(buffer.getvalue())} bytes")
                else:
                    print("✗ Expanded template buffer is empty")
            else:
                print("✗ No expanded template buffer attribute found")
                
            return True
            
        else:
            print(f"✗ Template file does not exist: {template_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error opening double template: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_template_folder():
    """Check what's in the template folder."""
    print("\nChecking Template Folder Contents")
    print("=" * 40)
    
    template_dir = Path(__file__).parent / "src" / "core" / "generation" / "templates"
    
    if not template_dir.exists():
        print(f"✗ Template directory not found: {template_dir}")
        return
    
    print(f"✓ Template directory exists: {template_dir}")
    
    # List all files
    for item in template_dir.iterdir():
        if item.is_file():
            # Check if it's a .docx file
            if item.suffix.lower() == '.docx':
                # Check if it's not a temporary file
                if not item.name.startswith('~$') and not item.name.startswith('.'):
                    print(f"  📄 {item.name} ({item.stat().st_size} bytes)")
                else:
                    print(f"  🗑️  {item.name} (temp file)")
            else:
                print(f"  📁 {item.name}")

if __name__ == "__main__":
    print("Double Template Opening Test")
    print("=" * 50)
    
    # Check template folder first
    check_template_folder()
    
    print("\n" + "=" * 50)
    
    # Test template opening
    success = test_double_template_opening()
    
    if success:
        print("\n✅ Double template opened successfully!")
    else:
        print("\n❌ Failed to open double template") 