#!/usr/bin/env python3
"""
Patch docxcompose to replace pkg_resources with importlib.metadata
This fixes the deprecation warning until an official release is available.
"""
import os
import sys

def find_docxcompose_properties():
    """Find the installed docxcompose/properties.py file"""
    try:
        import docxcompose
        docxcompose_path = os.path.dirname(docxcompose.__file__)
        properties_file = os.path.join(docxcompose_path, 'properties.py')
        if os.path.exists(properties_file):
            return properties_file
    except ImportError:
        pass
    return None

def patch_properties_file(filepath):
    """Replace pkg_resources with importlib.metadata"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'importlib.metadata' in content or 'importlib_metadata' in content:
        print("✓ File already patched")
        return False
    
    # Replace pkg_resources import with importlib.metadata
    old_import = "import pkg_resources"
    
    # Try importlib.metadata (Python 3.8+)
    try:
        import importlib.metadata
        new_import = "from importlib import metadata as importlib_metadata"
        print("Using importlib.metadata (Python 3.8+)")
    except ImportError:
        # Fallback to importlib_metadata package
        new_import = "import importlib_metadata"
        print("Using importlib_metadata package (requires: pip install importlib-metadata)")
    
    # Replace the import
    new_content = content.replace(old_import, new_import)
    
    # Replace pkg_resources.get_distribution usage
    new_content = new_content.replace(
        "pkg_resources.get_distribution('docxcompose').version",
        "importlib_metadata.version('docxcompose')"
    )
    
    # Backup original file
    backup_file = filepath + '.backup'
    if not os.path.exists(backup_file):
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✓ Backup created: {backup_file}")
    
    # Write patched content
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Patched: {filepath}")
    return True

def main():
    properties_file = find_docxcompose_properties()
    
    if not properties_file:
        print("✗ Could not find docxcompose installation")
        sys.exit(1)
    
    print(f"Found docxcompose properties file: {properties_file}")
    
    if patch_properties_file(properties_file):
        print("\n✓ Successfully patched docxcompose!")
        print("The pkg_resources deprecation warning should now be resolved.")
    else:
        print("\nNo changes needed.")

if __name__ == "__main__":
    main()

