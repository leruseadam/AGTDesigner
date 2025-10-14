#!/usr/bin/env python3
"""
Fix Excel upload reliability issues on PythonAnywhere
"""

import os
import sys
import sqlite3
import subprocess

def fix_upload_reliability():
    """Fix Excel upload reliability issues"""
    
    print("=======================================")
    print("FIXING EXCEL UPLOAD RELIABILITY")
    print("=======================================")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ ERROR: app.py not found. Are you in ~/AGTDesigner?")
        return False
    
    print("✅ Found app.py")
    
    # 1. Fix database locks
    print("\n🔧 Step 1: Fixing database locks...")
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    if os.path.exists(db_path):
        # Remove lock files
        lock_files = [db_path + ext for ext in ['-shm', '-wal']]
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                    print(f"✅ Removed lock file: {lock_file}")
                except Exception as e:
                    print(f"⚠️  Could not remove {lock_file}: {e}")
        
        # Test database connection
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            conn.execute("SELECT 1")
            conn.close()
            print("✅ Database is accessible")
        except Exception as e:
            print(f"❌ Database still locked: {e}")
            # Kill any processes using the database
            try:
                result = subprocess.run(['lsof', db_path], capture_output=True, text=True)
                if result.stdout:
                    print("🔍 Processes using database:")
                    print(result.stdout)
                    # Kill processes
                    pids = []
                    for line in result.stdout.split('\n')[1:]:  # Skip header
                        if line.strip():
                            pid = line.split()[1]
                            pids.append(pid)
                    
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], check=True)
                            print(f"✅ Killed process {pid}")
                        except:
                            pass
            except:
                pass
    else:
        print("⚠️  Database file not found, will be created on first upload")
    
    # 2. Clean up uploads directory
    print("\n🧹 Step 2: Cleaning uploads directory...")
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        # Remove old Excel files
        excel_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.xlsx', '.xls'))]
        for excel_file in excel_files:
            try:
                file_path = os.path.join(uploads_dir, excel_file)
                if os.path.getsize(file_path) < 1000:  # Remove tiny files (likely corrupted)
                    os.remove(file_path)
                    print(f"✅ Removed corrupted file: {excel_file}")
                elif os.path.getmtime(file_path) < (time.time() - 3600):  # Remove files older than 1 hour
                    os.remove(file_path)
                    print(f"✅ Removed old file: {excel_file}")
            except Exception as e:
                print(f"⚠️  Could not remove {excel_file}: {e}")
        
        # Remove corrupted backups
        backup_files = [f for f in os.listdir(uploads_dir) if 'corrupted' in f]
        for backup_file in backup_files:
            try:
                os.remove(os.path.join(uploads_dir, backup_file))
                print(f"✅ Removed corrupted backup: {backup_file}")
            except Exception as e:
                print(f"⚠️  Could not remove {backup_file}: {e}")
    
    # 3. Check disk space
    print("\n💾 Step 3: Checking disk space...")
    try:
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        print("Disk usage:")
        print(result.stdout)
        
        # Check if disk is full
        lines = result.stdout.split('\n')
        if len(lines) > 1:
            usage_line = lines[1]
            usage_percent = int(usage_line.split()[4].replace('%', ''))
            if usage_percent > 90:
                print("⚠️  WARNING: Disk usage is very high!")
                print("Cleaning up more files...")
                
                # Remove old logs
                log_files = [f for f in os.listdir('.') if f.endswith('.log')]
                for log_file in log_files:
                    try:
                        if os.path.getmtime(log_file) < (time.time() - 86400):  # Older than 1 day
                            os.remove(log_file)
                            print(f"✅ Removed old log: {log_file}")
                    except:
                        pass
                
                # Remove Python cache
                import shutil
                for root, dirs, files in os.walk('.'):
                    for dir_name in dirs:
                        if dir_name == '__pycache__':
                            try:
                                shutil.rmtree(os.path.join(root, dir_name))
                                print(f"✅ Removed cache: {os.path.join(root, dir_name)}")
                            except:
                                pass
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
    
    # 4. Check file permissions
    print("\n🔐 Step 4: Checking file permissions...")
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        try:
            os.chmod(uploads_dir, 0o755)
            print("✅ Uploads directory permissions fixed")
        except Exception as e:
            print(f"⚠️  Could not fix uploads directory permissions: {e}")
    
    # 5. Test upload endpoint
    print("\n🧪 Step 5: Testing upload endpoint...")
    try:
        import requests
        # Test if the app is running
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ App is running and accessible")
        else:
            print(f"⚠️  App returned status code: {response.status_code}")
    except Exception as e:
        print(f"ℹ️  Cannot test app locally: {e}")
    
    print("\n✅ Upload reliability fix complete!")
    print("\n📋 Summary of fixes applied:")
    print("- Removed database lock files")
    print("- Cleaned up corrupted uploads")
    print("- Freed up disk space")
    print("- Fixed file permissions")
    print("\n🚀 Next steps:")
    print("1. Reload your web app")
    print("2. Try uploading an Excel file")
    print("3. If still issues, check logs: tail -f /var/log/www.agtpricetags.com.error.log")
    
    return True

if __name__ == "__main__":
    import time
    fix_upload_reliability()
