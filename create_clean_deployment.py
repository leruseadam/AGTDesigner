#!/usr/bin/env python3
"""
Create a clean deployment package for PythonAnywhere
"""

import os
import subprocess
import shutil
from pathlib import Path

def create_clean_deployment():
    """Create a clean deployment package with only necessary files"""
    
    print("🚀 Creating clean PythonAnywhere deployment...")
    
    # Create deployment directory
    deploy_dir = "pythonanywhere_deployment"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    
    os.makedirs(deploy_dir)
    
    # Essential files to copy
    essential_files = [
        "app.py",
        "requirements.txt",
        "product_database.db"
    ]
    
    # Essential directories to copy
    essential_dirs = [
        "src",
        "static", 
        "templates"
    ]
    
    # Excel database files
    excel_files = [
        "AGT_Complete_Product_Database_20250822_020841.xlsx",
        "AGT_Essential_Product_Database_20250822_022042.xlsx",
        "comprehensive_product_database_20250822_020149.xlsx",
        "comprehensive_product_database_with_pricing.xlsx"
    ]
    
    # Copy essential files
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️  Warning: {file} not found")
    
    # Copy essential directories
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(deploy_dir, dir_name))
            print(f"✅ Copied directory {dir_name}")
        else:
            print(f"⚠️  Warning: {dir_name} not found")
    
    # Copy Excel files
    for file in excel_files:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️  Warning: {file} not found")
    
    # Create .gitignore
    gitignore_content = """# PythonAnywhere deployment
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Sessions (will be recreated)
sessions/

# Temporary files
*.tmp
*.temp
~$*

# OS files
.DS_Store
Thumbs.db
"""
    
    with open(os.path.join(deploy_dir, ".gitignore"), "w") as f:
        f.write(gitignore_content)
    
    # Create deployment README
    readme_content = """# LabelMaker - PythonAnywhere Deployment

This is a clean deployment package for PythonAnywhere.

## Quick Setup

1. Upload all files to your PythonAnywhere account
2. Install dependencies: `pip3.10 install --user -r requirements.txt`
3. Set up web app to point to `app.py`
4. The database is included and ready to use

## Files Included

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `src/` - Source code directory
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `product_database.db` - SQLite database with all product data
- Excel database files - Product data sources

## Database

The SQLite database (`product_database.db`) is included and contains all your product data.
No additional database setup is required.

## Web App Configuration

1. Go to Web tab in PythonAnywhere dashboard
2. Add new web app → Manual configuration
3. Python 3.10
4. Source code: `/home/yourusername/pythonanywhere_deployment/`
5. WSGI file: `/home/yourusername/pythonanywhere_deployment/app.py`

## Notes

- Sessions directory will be created automatically
- All temporary files are excluded
- This deployment matches your local version exactly
- No environment variables required
"""
    
    with open(os.path.join(deploy_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    print(f"\n✅ Clean deployment package created in {deploy_dir}/")
    
    # Verify essential files
    essential_checks = [
        "app.py",
        "requirements.txt", 
        "product_database.db",
        "src/core/data/product_database.py",
        "static/js/main.js",
        "templates/index.html"
    ]
    
    print("\n🔍 Verifying deployment...")
    all_good = True
    for check in essential_checks:
        check_path = os.path.join(deploy_dir, check)
        if os.path.exists(check_path):
            print(f"✅ {check}")
        else:
            print(f"❌ {check} - MISSING")
            all_good = False
    
    if all_good:
        print("\n🎉 Deployment package is ready!")
        
        # Create zip file
        zip_name = "labelmaker_pythonanywhere.zip"
        if os.path.exists(zip_name):
            os.remove(zip_name)
        
        print(f"📦 Creating zip file: {zip_name}")
        subprocess.run(f"cd {deploy_dir} && zip -r ../{zip_name} .", shell=True, check=True)
        
        if os.path.exists(zip_name):
            print(f"✅ Zip file created: {zip_name}")
        else:
            print("❌ Failed to create zip file")
    else:
        print("\n❌ Deployment verification failed")
    
    return deploy_dir

if __name__ == "__main__":
    create_clean_deployment()
