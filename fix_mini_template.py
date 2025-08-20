#!/usr/bin/env python3
"""
Fix mini template by adding VendorInfo placeholder
"""

import zipfile
import os
import re
import shutil
from pathlib import Path

def fix_mini_template():
    """Add VendorInfo placeholder to mini template"""
    
    template_path = 'src/core/generation/templates/mini.docx'
    backup_path = 'src/core/generation/templates/mini.docx.backup'
    
    if not os.path.exists(template_path):
        print(f"❌ Mini template not found at: {template_path}")
        return False
    
    print(f"🔍 Found mini template at: {template_path}")
    
    # Create backup
    shutil.copy2(template_path, backup_path)
    print(f"✅ Created backup at: {backup_path}")
    
    try:
        # Read the template
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            if 'word/document.xml' not in zip_file.namelist():
                print("❌ Could not find document.xml in template")
                return False
            
            content = zip_file.read('word/document.xml').decode('utf-8')
            print(f"📖 Read {len(content)} characters from mini template")
            
            # Check if VendorInfo is already there
            if 'VendorInfo' in content:
                print("✅ VendorInfo placeholder already exists in mini template!")
                return True
            
            # Find where to insert VendorInfo (after ProductBrand, before Ratio_or_THC_CBD)
            pattern = r'(\{\{Label1\.ProductBrand\}\})(.*?)(\{\{Label1\.Ratio_or_THC_CBD\}\})'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                print("❌ Could not find the right location to insert VendorInfo")
                return False
            
            # Insert VendorInfo placeholder
            before = match.group(1)
            middle = match.group(2)
            after = match.group(3)
            
            # Add VendorInfo placeholder with proper spacing
            vendor_placeholder = '{{Label1.VendorInfo}}'
            if middle.strip():
                # If there's content between, add newline
                new_middle = middle + f'\n{vendor_placeholder}'
            else:
                # If no content between, just add the placeholder
                new_middle = f'\n{vendor_placeholder}\n'
            
            # Replace the content
            new_content = content.replace(
                f"{before}{middle}{after}",
                f"{before}{new_middle}{after}"
            )
            
            # Update the zip file
            with zipfile.ZipFile(template_path, 'w') as zip_file:
                # Copy all files except document.xml
                for item in zip_file.infolist():
                    if item.filename != 'word/document.xml':
                        zip_file.writestr(item, zip_file.read(item.filename))
                
                # Add the updated document.xml
                zip_file.writestr('word/document.xml', new_content.encode('utf-8'))
            
            print("✅ Successfully updated mini template with VendorInfo placeholder!")
            
            # Verify the update
            with zipfile.ZipFile(template_path, 'r') as zip_file:
                updated_content = zip_file.read('word/document.xml').decode('utf-8')
                if 'VendorInfo' in updated_content:
                    print("✅ Verification: VendorInfo placeholder found in updated template!")
                    return True
                else:
                    print("❌ Verification failed: VendorInfo placeholder not found after update")
                    return False
                    
    except Exception as e:
        print(f"❌ Error updating mini template: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Fix Mini Template - Add VendorInfo Placeholder")
    print("=" * 60)
    
    if fix_mini_template():
        print("\n🎉 Success! Mini template now has VendorInfo placeholder.")
        print("📝 Next steps:")
        print("   1. Test mini template generation")
        print("   2. Vendor information should now appear on mini labels")
        print("   3. Push the updated template to your repository")
    else:
        print("\n❌ Failed to fix mini template. Please check the errors above.")

if __name__ == "__main__":
    main()
