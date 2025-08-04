#!/usr/bin/env python3
"""
PythonAnywhere File Loading Fix
Comprehensive solution for file access limitations on PythonAnywhere.
"""

import re

def print_fix_plan():
    """Print the comprehensive fix plan."""
    
    print("🔧 PythonAnywhere File Loading Fix")
    print("=" * 45)
    print()
    
    print("📋 ISSUE IDENTIFIED:")
    print("-" * 25)
    print("• PythonAnywhere cannot access user's download folder")
    print("• Local version can access /Users/adamcordova/Downloads")
    print("• PythonAnywhere restricted to /home/adamcordova/AGTDesigner")
    print("• Default file loading fails on PythonAnywhere")
    print()
    
    print("🛠️ COMPREHENSIVE FIX PLAN:")
    print("-" * 30)
    print("1. Detect PythonAnywhere environment")
    print("2. Modify file loading logic for PythonAnywhere")
    print("3. Use only project directory files")
    print("4. Provide clear error messages")
    print("5. Add file upload instructions")
    print()
    
    print("📁 PYTHONANYWHERE FILE STRATEGY:")
    print("-" * 35)
    print("• Only search in /home/adamcordova/AGTDesigner/uploads")
    print("• Skip Downloads folder entirely")
    print("• Provide clear upload instructions")
    print("• Handle missing files gracefully")
    print()

def fix_pythonanywhere_file_loading():
    """Apply the PythonAnywhere file loading fix."""
    
    print("🔧 Applying PythonAnywhere File Loading Fix...")
    print()
    
    # Read the current app.py file
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find and fix the get_default_upload_file function
    pattern = r'def get_default_upload_file\(\):.*?return None'
    replacement = '''def get_default_upload_file():
    """
    Get the default upload file path, with PythonAnywhere-specific handling.
    """
    import os
    
    # Check if running on PythonAnywhere
    is_pythonanywhere = os.environ.get('PYTHONANYWHERE_SITE', False) or 'pythonanywhere' in os.environ.get('PYTHONANYWHERE_DOMAIN', '').lower()
    
    if is_pythonanywhere:
        # PythonAnywhere: Only search in project directory
        current_dir = os.getcwd()
        uploads_dir = os.path.join(current_dir, 'uploads')
        
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir, exist_ok=True)
            return None
        
        # Search for Excel files in uploads directory only
        excel_files = []
        for file in os.listdir(uploads_dir):
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
                file_path = os.path.join(uploads_dir, file)
                excel_files.append((file_path, os.path.getmtime(file_path)))
        
        if excel_files:
            # Return the most recent file
            latest_file = max(excel_files, key=lambda x: x[1])[0]
            return latest_file
        else:
            return None
    else:
        # Local development: Use original logic
        current_dir = os.getcwd()
        uploads_dir = os.path.join(current_dir, 'uploads')
        downloads_dir = os.path.expanduser('~/Downloads')
        
        # Search in uploads directory first
        if os.path.exists(uploads_dir):
            excel_files = []
            for file in os.listdir(uploads_dir):
                if file.endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
                    file_path = os.path.join(uploads_dir, file)
                    excel_files.append((file_path, os.path.getmtime(file_path)))
            
            if excel_files:
                return max(excel_files, key=lambda x: x[1])[0]
        
        # Fallback to Downloads directory (local only)
        if os.path.exists(downloads_dir):
            excel_files = []
            for file in os.listdir(downloads_dir):
                if file.endswith(('.xlsx', '.xls')) and not file.startswith('~$'):
                    file_path = os.path.join(downloads_dir, file)
                    excel_files.append((file_path, os.path.getmtime(file_path)))
            
            if excel_files:
                return max(excel_files, key=lambda x: x[1])[0]
    
    return None'''
    
    # Apply the fix
    if 'def get_default_upload_file():' in content:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print("✅ Updated get_default_upload_file function for PythonAnywhere")
    else:
        print("❌ Could not find get_default_upload_file function")
        return False
    
    # Add PythonAnywhere-specific error handling
    pattern = r'if default_file and os\.path\.exists\(default_file\):'
    replacement = '''if default_file and os.path.exists(default_file):
                logging.info(f"Attempting to load default file: {default_file}")
                success = excel_processor.load_file(default_file)
            else:
                # PythonAnywhere-specific handling
                if os.environ.get('PYTHONANYWHERE_SITE', False):
                    logging.warning("PythonAnywhere: No default file found in uploads directory")
                    logging.info("Please upload an Excel file using the file upload feature")
                    return jsonify({
                        'error': 'No default file found. Please upload an Excel file.',
                        'pythonanywhere': True,
                        'upload_required': True
                    }), 404
                else:
                    logging.warning("No default file found in uploads or downloads directory")'''
    
    if 'if default_file and os.path.exists(default_file):' in content:
        content = re.sub(pattern, replacement, content)
        print("✅ Added PythonAnywhere-specific error handling")
    else:
        print("❌ Could not find default file loading section")
        return False
    
    # Write the updated content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ PythonAnywhere file loading fix applied successfully!")
    return True

def create_pythonanywhere_guide():
    """Create a guide for PythonAnywhere file management."""
    
    guide_content = """# PythonAnywhere File Management Guide

## 🔍 **Understanding the Limitation**

PythonAnywhere cannot access your local Downloads folder or any files outside your project directory. This is a security feature of the platform.

## 📁 **Where PythonAnywhere Can Access Files**

- ✅ `/home/adamcordova/AGTDesigner/uploads/` (your project's uploads folder)
- ✅ Any files you upload through the web interface
- ❌ `/home/adamcordova/Downloads/` (cannot access)
- ❌ `/home/adamcordova/Desktop/` (cannot access)

## 🛠️ **How to Use Files on PythonAnywhere**

### **Option 1: Upload Through Web Interface**
1. Go to your app's main page
2. Use the file upload feature
3. Select your Excel file
4. The file will be stored in the uploads directory

### **Option 2: Upload via PythonAnywhere Files**
1. Go to PythonAnywhere dashboard
2. Click "Files" tab
3. Navigate to `/home/adamcordova/AGTDesigner/uploads/`
4. Upload your Excel file there

### **Option 3: Use Git (Recommended)**
1. Add your Excel file to your local project
2. Commit and push to GitHub
3. Pull on PythonAnywhere

## 🔧 **What the Fix Does**

- Detects when running on PythonAnywhere
- Only searches in the project's uploads directory
- Provides clear error messages when no files are found
- Guides users to upload files through the web interface

## 📋 **Best Practices**

1. **Always upload files through the web interface** for the best user experience
2. **Keep important files in your project directory** so they're available on PythonAnywhere
3. **Use the file upload feature** rather than relying on default file loading
4. **Check the uploads directory** if you need to verify file availability

## 🚨 **Troubleshooting**

If you see "No default file found" errors:
1. Upload a file through the web interface
2. Check that the file is in the uploads directory
3. Ensure the file is a valid Excel file (.xlsx or .xls)
4. Try refreshing the page after upload
"""
    
    with open('PYTHONANYWHERE_FILE_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print("✅ Created PythonAnywhere file management guide")

if __name__ == "__main__":
    print_fix_plan()
    
    if fix_pythonanywhere_file_loading():
        create_pythonanywhere_guide()
        print("\n🎉 PythonAnywhere file loading fix completed!")
        print("\n📋 Next Steps:")
        print("1. Test the fix locally")
        print("2. Commit and push the changes")
        print("3. Deploy to PythonAnywhere")
        print("4. Upload files through the web interface")
    else:
        print("\n❌ Fix failed. Please check the error messages above.") 