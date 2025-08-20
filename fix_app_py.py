#!/usr/bin/env python3
"""
Fix app.py syntax error script
Removes duplicate import math statements that are causing the syntax error
"""

import os
import re

def fix_app_py():
    """Fix the syntax error in app.py"""
    
    # Path to app.py
    app_path = "app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ app.py not found at: {app_path}")
        return False
    
    print(f"🔍 Found app.py at: {app_path}")
    
    # Read the file
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False
    
    print(f"📖 Read {len(content)} characters from app.py")
    
    # Check if the problematic duplicate imports exist
    if '                import math' not in content:
        print("✅ No duplicate import math statements found - app.py is already fixed!")
        return True
    
    print("🔧 Fixing duplicate import math statements...")
    
    # Fix: Remove duplicate import math statements
    content = content.replace('                import math\n                def clean_dict', '                # Clean the tags data\n                def clean_dict')
    
    # Write the fixed content back
    try:
        # Create backup first
        backup_path = app_path + '.backup_fixed'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created backup at: {backup_path}")
        
        # Write fixed content
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed app.py successfully!")
        
        # Verify the fix
        if '                import math' not in content:
            print("✅ Duplicate import math statements have been removed!")
            return True
        else:
            print("❌ Fix may not have worked completely")
            return False
            
    except Exception as e:
        print(f"❌ Error writing fixed app.py: {e}")
        return False

def main():
    print("🔧 Fix app.py Syntax Error Script")
    print("=" * 40)
    
    if fix_app_py():
        print("\n🎉 Success! Your app.py has been fixed.")
        print("📝 Next steps:")
        print("   1. Test the syntax: python -m py_compile app.py")
        print("   2. Try running: python app.py")
        print("   3. Reload your PythonAnywhere web app")
    else:
        print("\n❌ Failed to fix app.py. Please check the errors above.")

if __name__ == "__main__":
    main()
