#!/usr/bin/env python3
"""
Upload application fixes to PythonAnywhere
This script provides instructions for manually uploading the fixed files
"""

import os
import subprocess
from pathlib import Path

def main():
    print("🚀 AGT Label Maker - Upload Application Fixes to PythonAnywhere")
    print("=" * 70)
    print()
    
    print("The following files have been updated with database fixes:")
    print("✅ app.py - Fixed database fallback logic")
    print("✅ src/core/data/product_database.py - Fixed duplicate column errors")
    print()
    
    print("To update the live website (agtpricetags.com), you need to:")
    print("1. Log into your PythonAnywhere account")
    print("2. Go to the Files tab")
    print("3. Navigate to /home/adamcordova/AGTDesigner/")
    print("4. Upload the following files from pythonanywhere_deployment/:")
    print()
    
    # List files that need to be uploaded
    files_to_upload = [
        "app.py",
        "core/data/product_database.py",
        "core/data/excel_processor.py",
        "core/generation/template_processor.py",
        "core/generation/tag_generator.py",
        "core/generation/unified_font_sizing.py",
        "core/data/json_matcher.py",
        "core/data/ai_product_matcher.py",
        "core/data/session_manager.py",
        "core/data/database_notifier.py",
        "core/data/product_database_optimized.py",
        "core/formatting/markers.py",
        "core/generation/context_builders.py",
        "core/generation/docx_formatting.py",
        "core/generation/font_sizing.py",
        "core/generation/text_processing.py",
        "core/ui/components.py",
        "core/ui/lineage_editor.py",
        "core/ui/main_window.py",
        "core/ui/modern_theme.py",
        "core/ui/template_editor.py",
        "core/ui/theme.py",
        "core/utils/common.py",
        "core/utils/resource_utils.py",
        "static/js/main.js",
        "static/css/styles.css",
        "templates/index.html",
        "templates/base.html",
        "templates/lineage_editor.html",
        "templates/library_browser.html",
        "templates/generation-splash.html",
        "templates/splash.html",
        "templates/auto_upload.html",
        "templates/initialization_test.html",
        "templates/upload_test.html",
        "templates/test_drag_drop_debug.html",
        "templates/test_drag_drop_real_data.html",
        "templates/test_lineage_editor_ux.html",
        "templates/test_lineage_simple.html",
        "templates/test_reorder_debug.html",
        "wsgi.py"
    ]
    
    print("Files to upload:")
    for i, file in enumerate(files_to_upload, 1):
        print(f"{i:2d}. {file}")
    
    print()
    print("5. After uploading, restart the web app:")
    print("   - Go to the Web tab in PythonAnywhere")
    print("   - Click 'Reload' for your web app")
    print()
    print("6. Test the website at https://agtpricetags.com")
    print("   - The database statistics should now show proper numbers")
    print("   - Total Products: 10,285")
    print("   - Unique Vendors: 108")
    print("   - Unique Brands: 170")
    print("   - Product Types: 19")
    print()
    print("🔧 Alternative: Use SCP to upload files automatically")
    print("If you have SSH access to PythonAnywhere, you can use:")
    print()
    print("scp -r pythonanywhere_deployment/* adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/")
    print()
    print("⚠️  Note: Make sure to backup your current files before uploading!")

if __name__ == "__main__":
    main()
