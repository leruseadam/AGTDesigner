#!/usr/bin/env python3
"""
Upload database to PythonAnywhere using their API
"""
import os
import sys
import requests
from pathlib import Path

# PythonAnywhere API configuration
API_USERNAME = "adamcordova"
API_URL = f"https://www.pythonanywhere.com/api/v0/user/{API_USERNAME}/files/path"

def get_api_token():
    """Get API token from environment or prompt user"""
    token = os.environ.get('PYTHONANYWHERE_API_TOKEN')
    if not token:
        print("=" * 60)
        print("⚠️  PythonAnywhere API Token Required")
        print("=" * 60)
        print("To upload files via API, you need your API token:")
        print("1. Go to https://www.pythonanywhere.com/user/adamcordova/")
        print("2. Click on 'API Token' tab")
        print("3. Copy your API token")
        print()
        token = input("Enter your PythonAnywhere API token: ").strip()
        
        if not token:
            print("❌ No API token provided")
            return None
    
    return token

def upload_file(token, local_path, remote_path):
    """Upload a file to PythonAnywhere using the API"""
    
    if not os.path.exists(local_path):
        print(f"❌ Local file not found: {local_path}")
        return False
    
    # Get file size
    file_size = os.path.getsize(local_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📤 Uploading {os.path.basename(local_path)} ({file_size_mb:.1f} MB)...")
    print(f"   Local:  {local_path}")
    print(f"   Remote: {remote_path}")
    
    # Prepare headers
    headers = {
        'Authorization': f'Token {token}'
    }
    
    # Upload file
    url = f"{API_URL}{remote_path}"
    
    try:
        with open(local_path, 'rb') as f:
            response = requests.post(
                url,
                files={'content': f},
                headers=headers,
                timeout=300  # 5 minute timeout for large files
            )
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Upload successful!")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Upload timed out. The file may be too large.")
        print("   Try using the manual upload method instead.")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def extract_and_deploy_commands(remote_path):
    """Return commands to extract and deploy the database on PythonAnywhere"""
    
    commands = f"""
# Run these commands in your PythonAnywhere Bash console:

cd ~/AGTDesigner/uploads

# Extract the compressed database
gunzip -f product_database_AGT_Bothell.db.gz

# Verify the database
python3.11 -c "
import sqlite3
conn = sqlite3.connect('product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products')
print(f'✅ Products in database: {{cursor.fetchone()[0]:,}}')
conn.close()
"

# Make sure the database is readable
chmod 644 product_database_AGT_Bothell.db

# Reload your web app
# Go to PythonAnywhere Web tab and click 'Reload'
"""
    return commands

def main():
    """Main upload function"""
    
    print("🚀 Push Database to PythonAnywhere")
    print("=" * 60)
    
    # Database file to upload
    local_db = "uploads/product_database_AGT_Bothell.db.gz"
    remote_db = "/home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db.gz"
    
    if not os.path.exists(local_db):
        print(f"❌ Database file not found: {local_db}")
        print("   Creating compressed database...")
        
        # Try to compress the uncompressed version
        uncompressed = "uploads/product_database_AGT_Bothell.db"
        if os.path.exists(uncompressed):
            import gzip
            import shutil
            print(f"📦 Compressing {uncompressed}...")
            with open(uncompressed, 'rb') as f_in:
                with gzip.open(local_db, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"✅ Created {local_db}")
        else:
            print(f"❌ Could not find uncompressed database: {uncompressed}")
            return False
    
    # Get file info
    file_size = os.path.getsize(local_db)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📊 Database file: {local_db}")
    print(f"   Size: {file_size_mb:.1f} MB")
    print()
    
    # Check if file is too large for API upload
    if file_size_mb > 100:
        print("⚠️  File is quite large (>100MB)")
        print("   API upload may be slow or fail.")
        print()
        print("📋 MANUAL UPLOAD INSTRUCTIONS (Recommended)")
        print("=" * 60)
        print("1. Go to: https://www.pythonanywhere.com/user/adamcordova/files/")
        print("2. Navigate to: /home/adamcordova/AGTDesigner/uploads/")
        print("3. Click 'Upload a file'")
        print(f"4. Select: {os.path.abspath(local_db)}")
        print("5. Wait for upload to complete")
        print()
        print(extract_and_deploy_commands(remote_db))
        
        choice = input("Try API upload anyway? (y/N): ").strip().lower()
        if choice != 'y':
            print("✅ Use manual upload instructions above")
            return True
    
    # Get API token
    token = get_api_token()
    if not token:
        print("❌ Cannot proceed without API token")
        return False
    
    # Upload the file
    print()
    success = upload_file(token, local_db, remote_db)
    
    if success:
        print()
        print("=" * 60)
        print("✅ Upload Complete!")
        print("=" * 60)
        print(extract_and_deploy_commands(remote_db))
    else:
        print()
        print("=" * 60)
        print("❌ API Upload Failed - Use Manual Upload Instead")
        print("=" * 60)
        print("1. Go to: https://www.pythonanywhere.com/user/adamcordova/files/")
        print("2. Navigate to: /home/adamcordova/AGTDesigner/uploads/")
        print("3. Click 'Upload a file'")
        print(f"4. Select: {os.path.abspath(local_db)}")
        print("5. Wait for upload to complete")
        print()
        print(extract_and_deploy_commands(remote_db))
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

