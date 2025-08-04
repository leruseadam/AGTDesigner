#!/usr/bin/env python3
"""
Script to help deploy a default file to the production server.
This script will help you identify and prepare a default file for deployment.
"""

import os
import shutil
from pathlib import Path

def list_available_files():
    """List all available Excel files that could be used as defaults."""
    uploads_dir = Path("uploads")
    excel_files = []
    
    if uploads_dir.exists():
        for file in uploads_dir.glob("*.xlsx"):
            file_size = file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            excel_files.append({
                'name': file.name,
                'path': str(file),
                'size_mb': round(file_size_mb, 2),
                'is_default': file.name.startswith("A Greener Today")
            })
    
    return excel_files

def suggest_default_file(files):
    """Suggest the best default file based on naming and size."""
    # Prefer "A Greener Today" files
    greener_files = [f for f in files if f['is_default']]
    if greener_files:
        # Sort by size (prefer smaller files for faster loading)
        greener_files.sort(key=lambda x: x['size_mb'])
        return greener_files[0]
    
    # Fallback to any Excel file
    if files:
        files.sort(key=lambda x: x['size_mb'])
        return files[0]
    
    return None

def create_deployment_instructions(default_file):
    """Create deployment instructions for the selected file."""
    instructions = f"""
# Deployment Instructions for Default File

## Selected File: {default_file['name']}
- Size: {default_file['size_mb']} MB
- Path: {default_file['path']}

## Option 1: Manual Upload (Recommended)
1. Go to https://www.agtpricetags.com
2. Click the upload button
3. Select the file: {default_file['name']}
4. The application will load the data and API endpoints will work

## Option 2: Server Deployment
If you want the file to be available by default:

1. **Upload to PythonAnywhere:**
   - Log into your PythonAnywhere account
   - Go to the Files tab
   - Navigate to your project directory
   - Create an 'uploads' folder if it doesn't exist
   - Upload the file: {default_file['name']}

2. **Or use the PythonAnywhere console:**
   ```bash
   # In your PythonAnywhere console
   cd /home/yourusername/yourproject
   mkdir -p uploads
   # Upload the file via the Files interface
   ```

3. **Restart your web app** after uploading the file

## Option 3: Include in Git Repository
If you want the file to be part of your deployment:

1. Copy the file to your project:
   ```bash
   cp "{default_file['path']}" uploads/default_inventory.xlsx
   ```

2. Add to git (if the file is not sensitive):
   ```bash
   git add uploads/default_inventory.xlsx
   git commit -m "Add default inventory file"
   git push
   ```

3. Modify the get_default_upload_file() function to look for this specific file

## Testing
After deployment, test the API endpoints:
- https://www.agtpricetags.com/api/status
- https://www.agtpricetags.com/api/available-tags
- https://www.agtpricetags.com/api/selected-tags

## Notes
- The file size ({default_file['size_mb']} MB) is reasonable for web loading
- Make sure the file contains the expected columns (Product Name*, Vendor, etc.)
- Consider if this data should be publicly accessible
"""
    return instructions

def main():
    print("=== Default File Deployment Helper ===\n")
    
    # List available files
    files = list_available_files()
    
    if not files:
        print("❌ No Excel files found in uploads directory")
        print("Please add an Excel file to the uploads/ directory first.")
        return
    
    print(f"Found {len(files)} Excel file(s):")
    for i, file in enumerate(files, 1):
        default_indicator = " (DEFAULT)" if file['is_default'] else ""
        print(f"{i}. {file['name']} - {file['size_mb']} MB{default_indicator}")
    
    print()
    
    # Suggest default file
    suggested = suggest_default_file(files)
    if suggested:
        print(f"✅ Suggested default file: {suggested['name']}")
        print(f"   Size: {suggested['size_mb']} MB")
        print(f"   Path: {suggested['path']}")
        
        # Create deployment instructions
        instructions = create_deployment_instructions(suggested)
        
        # Save instructions to file
        with open("DEPLOYMENT_INSTRUCTIONS.md", "w") as f:
            f.write(instructions)
        
        print(f"\n📝 Deployment instructions saved to: DEPLOYMENT_INSTRUCTIONS.md")
        print("\n=== Quick Fix ===")
        print("The fastest solution is to:")
        print("1. Go to https://www.agtpricetags.com")
        print("2. Upload the file: " + suggested['name'])
        print("3. The API errors should be resolved immediately")
        
    else:
        print("❌ No suitable default file found")

if __name__ == "__main__":
    main() 