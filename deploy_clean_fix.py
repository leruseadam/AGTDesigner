#!/usr/bin/env python3
"""
Deploy clean fix to PythonAnywhere
This script will upload the clean app.py file to resolve the merge conflict
"""

import os
import subprocess
import sys

def deploy_to_pythonanywhere():
    """Deploy the clean app.py to PythonAnywhere"""
    
    print("🚀 Starting deployment to PythonAnywhere...")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found in current directory")
        return False
    
    # Check for Git conflict markers in app.py
    with open("app.py", "r") as f:
        content = f.read()
        # Check for actual Git conflict markers (not comment lines)
        if "<<<<<<< HEAD" in content or ">>>>>>> " in content:
            print("❌ Error: Git conflict markers found in app.py")
            print("Please resolve conflicts before deploying")
            return False
        # Check for conflict separators that aren't in comments
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == "=======" and i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip()
                if prev_line.startswith("<<<<<<<") or next_line.startswith(">>>>>>>"):
                    print("❌ Error: Git conflict markers found in app.py")
                    print("Please resolve conflicts before deploying")
                    return False
    
    print("✅ Local app.py is clean (no conflict markers)")
    
    # Create a simple deployment script for PythonAnywhere
    deploy_script = """#!/bin/bash
# PythonAnywhere deployment script

echo "🔄 Updating PythonAnywhere deployment..."

# Navigate to the project directory
cd /home/adamcordova/AGTDesigner

# Pull the latest changes
echo "📥 Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main

# Verify the app.py file is clean
if grep -q "<<<<<<< HEAD" app.py; then
    echo "❌ Error: Git conflict markers still present in app.py"
    exit 1
fi

echo "✅ app.py is clean"

# Restart the web application
echo "🔄 Restarting web application..."
touch /var/www/www_agtpricetags_com_wsgi.py

echo "✅ Deployment complete!"
"""
    
    # Write the deployment script
    with open("deploy_script.sh", "w") as f:
        f.write(deploy_script)
    
    os.chmod("deploy_script.sh", 0o755)
    
    print("📝 Created deployment script: deploy_script.sh")
    print("📋 To deploy to PythonAnywhere, run this script on PythonAnywhere:")
    print("   bash deploy_script.sh")
    
    return True

if __name__ == "__main__":
    success = deploy_to_pythonanywhere()
    if success:
        print("\n✅ Deployment preparation complete!")
        print("🌐 Your PythonAnywhere site should be fixed after running the deployment script")
    else:
        print("\n❌ Deployment preparation failed")
        sys.exit(1)
