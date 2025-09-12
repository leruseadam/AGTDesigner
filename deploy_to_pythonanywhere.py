#!/usr/bin/env python3
"""
Deployment script for PythonAnywhere
This script ensures a clean deployment that matches the local version exactly
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_deployment_package():
    """Create a clean deployment package"""
    print("🚀 Creating deployment package for PythonAnywhere...")
    
    # Create deployment directory
    deploy_dir = "pythonanywhere_deployment"
    if os.path.exists(deploy_dir):
        run_command(f"rm -rf {deploy_dir}", "Cleaning existing deployment directory")
    
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Files and directories to include
    include_items = [
        "app.py",
        "requirements.txt",
        "src/",
        "static/",
        "templates/",
        "product_database.db",
        "AGT_Complete_Product_Database_20250822_020841.xlsx",
        "AGT_Essential_Product_Database_20250822_022042.xlsx",
        "comprehensive_product_database_20250822_020149.xlsx",
        "comprehensive_product_database_with_pricing.xlsx",
        "README.md"
    ]
    
    # Copy files
    for item in include_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                run_command(f"cp -r {item} {deploy_dir}/", f"Copying directory {item}")
            else:
                run_command(f"cp {item} {deploy_dir}/", f"Copying file {item}")
        else:
            print(f"⚠️  Warning: {item} not found, skipping")
    
    # Create .gitignore for deployment
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
    
    with open(f"{deploy_dir}/.gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create deployment README
    readme_content = """# PythonAnywhere Deployment

This is a clean deployment package for PythonAnywhere.

## Setup Instructions

1. Upload all files to your PythonAnywhere account
2. Install dependencies: `pip3.10 install --user -r requirements.txt`
3. Set up the web app to point to app.py
4. The database is included and ready to use

## Files Included

- app.py (main application)
- requirements.txt (dependencies)
- src/ (source code)
- static/ (static files)
- templates/ (HTML templates)
- product_database.db (SQLite database)
- Excel database files
- README.md (this file)

## Database

The SQLite database is included and contains all product data.
No additional database setup is required.

## Notes

- Sessions directory will be created automatically
- All temporary files are excluded
- This deployment matches the local version exactly
"""
    
    with open(f"{deploy_dir}/README.md", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Deployment package created in {deploy_dir}/")
    return deploy_dir

def create_zip_package(deploy_dir):
    """Create a zip file for easy upload"""
    zip_name = "labelmaker_pythonanywhere.zip"
    
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    run_command(f"cd {deploy_dir} && zip -r ../{zip_name} .", "Creating zip package")
    
    if os.path.exists(zip_name):
        print(f"✅ Zip package created: {zip_name}")
        return zip_name
    else:
        print("❌ Failed to create zip package")
        return None

def verify_deployment(deploy_dir):
    """Verify the deployment package"""
    print("🔍 Verifying deployment package...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "src/core/data/product_database.py",
        "product_database.db",
        "static/js/main.js",
        "templates/index.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(deploy_dir, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Main deployment function"""
    print("🚀 PythonAnywhere Deployment Script")
    print("=" * 50)
    
    # Create deployment package
    deploy_dir = create_deployment_package()
    if not deploy_dir:
        print("❌ Failed to create deployment package")
        return
    
    # Verify deployment
    if not verify_deployment(deploy_dir):
        print("❌ Deployment verification failed")
        return
    
    # Create zip package
    zip_file = create_zip_package(deploy_dir)
    if not zip_file:
        print("❌ Failed to create zip package")
        return
    
    print("\n🎉 Deployment package ready!")
    print(f"📁 Directory: {deploy_dir}/")
    print(f"📦 Zip file: {zip_file}")
    print("\n📋 Next steps:")
    print("1. Upload the zip file to PythonAnywhere")
    print("2. Extract it in your home directory")
    print("3. Install dependencies: pip3.10 install --user -r requirements.txt")
    print("4. Set up web app to point to app.py")
    print("5. Start the application")

if __name__ == "__main__":
    main()
