#!/usr/bin/env python3
"""
Script to upload default files to PythonAnywhere production server
"""

import os
import subprocess
import sys

def upload_file_to_pythonanywhere(local_file, remote_path):
    """Upload a file to PythonAnywhere using scp"""
    try:
        # Use scp to upload the file
        cmd = [
            'scp', 
            local_file, 
            f'adamcordova@ssh.pythonanywhere.com:{remote_path}'
        ]
        
        print(f"Uploading {os.path.basename(local_file)}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully uploaded {os.path.basename(local_file)}")
            return True
        else:
            print(f"❌ Failed to upload {os.path.basename(local_file)}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading {os.path.basename(local_file)}: {e}")
        return False

def main():
    print("🚀 UPLOADING DEFAULT FILES TO PYTHONANYWHERE")
    print("=" * 50)
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(current_dir, 'uploads')
    
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return
    
    # Find the most recent Excel file (excluding temp files)
    excel_files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.xlsx') and not file.startswith('~$'):
            file_path = os.path.join(uploads_dir, file)
            excel_files.append((file_path, os.path.getmtime(file_path)))
    
    if not excel_files:
        print("❌ No Excel files found in uploads directory")
        return
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📁 Found {len(excel_files)} Excel files in uploads directory")
    print("📋 Files to upload:")
    for i, (file_path, mtime) in enumerate(excel_files[:5]):  # Show top 5
        print(f"  {i+1}. {os.path.basename(file_path)}")
    
    # Upload the most recent file as the default
    default_file_path, _ = excel_files[0]
    remote_path = "~/AGTDesigner/uploads/"
    
    print(f"\n🎯 Uploading default file: {os.path.basename(default_file_path)}")
    
    # First, ensure the remote uploads directory exists
    print("📁 Creating remote uploads directory...")
    mkdir_cmd = [
        'ssh', 
        'adamcordova@ssh.pythonanywhere.com', 
        'mkdir -p ~/AGTDesigner/uploads'
    ]
    
    try:
        subprocess.run(mkdir_cmd, capture_output=True, text=True)
        print("✅ Remote uploads directory created/verified")
    except Exception as e:
        print(f"⚠️  Warning: Could not create remote directory: {e}")
    
    # Upload the default file
    success = upload_file_to_pythonanywhere(default_file_path, remote_path)
    
    if success:
        print("\n✅ UPLOAD COMPLETED!")
        print("\n🔄 Next steps:")
        print("1. Go to PythonAnywhere console")
        print("2. Run: touch /var/www/www_agtpricetags_com_wsgi.py")
        print("3. Test the app at: https://www.agtpricetags.com")
        print("\n📝 If you still have issues:")
        print("- Check PythonAnywhere error logs")
        print("- Verify the file was uploaded: ls -la ~/AGTDesigner/uploads/")
    else:
        print("\n❌ UPLOAD FAILED!")
        print("\n🔧 Manual upload instructions:")
        print("1. Go to PythonAnywhere Files tab")
        print("2. Navigate to ~/AGTDesigner/uploads/")
        print("3. Upload the file manually")
        print("4. Reload the web app")

if __name__ == "__main__":
    main() 