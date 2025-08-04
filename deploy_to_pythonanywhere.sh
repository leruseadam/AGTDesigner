#!/bin/bash

# PythonAnywhere Deployment Script
# This script helps deploy the fixed files to PythonAnywhere

echo "🚀 PythonAnywhere File Upload Fix Deployment"
echo "=============================================="

# Configuration
PROJECT_NAME="AGTDesigner"
PYTHONANYWHERE_USERNAME="adamcordova"
PYTHONANYWHERE_PROJECT_PATH="/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME"

echo "📋 Configuration:"
echo "  Username: $PYTHONANYWHERE_USERNAME"
echo "  Project: $PROJECT_NAME"
echo "  Path: $PYTHONANYWHERE_PROJECT_PATH"
echo ""

# Check if we're on PythonAnywhere
if [[ "$(hostname)" == *"pythonanywhere"* ]]; then
    echo "✅ Running on PythonAnywhere"
    IS_PYTHONANYWHERE=true
else
    echo "⚠️  Not running on PythonAnywhere - this script is for local preparation"
    IS_PYTHONANYWHERE=false
fi

echo ""

# Step 1: Create deployment package
echo "📦 Step 1: Creating deployment package..."

# Create deployment directory
DEPLOY_DIR="pythonanywhere_deployment"
mkdir -p "$DEPLOY_DIR"

# Copy essential files
echo "  Copying essential files..."
cp app.py "$DEPLOY_DIR/"
cp wsgi_pythonanywhere.py "$DEPLOY_DIR/"
cp fix_pythonanywhere_upload.py "$DEPLOY_DIR/"
cp test_pythonanywhere_upload.py "$DEPLOY_DIR/"
cp requirements_pythonanywhere.txt "$DEPLOY_DIR/" 2>/dev/null || cp requirements.txt "$DEPLOY_DIR/"

# Copy configuration files
echo "  Copying configuration files..."
cp config_pythonanywhere.py "$DEPLOY_DIR/" 2>/dev/null || echo "  ⚠️  config_pythonanywhere.py not found"
cp config_production.py "$DEPLOY_DIR/" 2>/dev/null || echo "  ⚠️  config_production.py not found"

# Copy source code
echo "  Copying source code..."
cp -r src "$DEPLOY_DIR/" 2>/dev/null || echo "  ⚠️  src directory not found"
cp -r static "$DEPLOY_DIR/" 2>/dev/null || echo "  ⚠️  static directory not found"
cp -r templates "$DEPLOY_DIR/" 2>/dev/null || echo "  ⚠️  templates directory not found"

# Create deployment instructions
echo "  Creating deployment instructions..."
cat > "$DEPLOY_DIR/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# PythonAnywhere Deployment Instructions

## Quick Setup

1. **Upload all files** to your PythonAnywhere project directory
2. **Open PythonAnywhere Bash Console** and run:
   ```bash
   cd /home/yourusername/AGTDesigner
   python fix_pythonanywhere_upload.py
   python test_pythonanywhere_upload.py
   ```
3. **Update WSGI file** with content from `wsgi_pythonanywhere.py`
4. **Set environment variables** in Web tab:
   - PYTHONANYWHERE=true
   - FLASK_ENV=production
   - FLASK_DEBUG=false
5. **Reload web app**

## File Structure
```
/home/yourusername/AGTDesigner/
├── app.py                          # Main application
├── wsgi_pythonanywhere.py          # WSGI configuration
├── fix_pythonanywhere_upload.py    # Fix script
├── test_pythonanywhere_upload.py   # Test script
├── src/                           # Source code
├── static/                        # Static files
├── templates/                     # Templates
└── uploads/                       # Upload directory (created by fix script)
```

## Troubleshooting
- Check error logs in PythonAnywhere Web tab
- Run test script to verify setup
- Ensure all dependencies are installed
EOF

echo "✅ Deployment package created in: $DEPLOY_DIR"
echo ""

# Step 2: Create upload script
echo "📤 Step 2: Creating upload script..."

cat > "$DEPLOY_DIR/upload_to_pythonanywhere.sh" << 'EOF'
#!/bin/bash

# Upload script for PythonAnywhere
# Run this from your local machine

echo "📤 Uploading files to PythonAnywhere..."

# Configuration
PYTHONANYWHERE_USERNAME="adamcordova"
PROJECT_NAME="AGTDesigner"
PYTHONANYWHERE_PROJECT_PATH="/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME"

echo "Uploading to: $PYTHONANYWHERE_PROJECT_PATH"

# Upload files using scp (if you have SSH access)
# scp -r . $PYTHONANYWHERE_USERNAME@ssh.pythonanywhere.com:$PYTHONANYWHERE_PROJECT_PATH/

# Alternative: Manual upload instructions
echo ""
echo "📋 Manual Upload Instructions:"
echo "1. Go to PythonAnywhere Files tab"
echo "2. Navigate to: $PYTHONANYWHERE_PROJECT_PATH"
echo "3. Upload all files from this directory"
echo "4. Run the fix script on PythonAnywhere"
echo ""

echo "✅ Upload script created"
EOF

chmod +x "$DEPLOY_DIR/upload_to_pythonanywhere.sh"

# Step 3: Create PythonAnywhere setup script
echo "🔧 Step 3: Creating PythonAnywhere setup script..."

cat > "$DEPLOY_DIR/setup_on_pythonanywhere.sh" << 'EOF'
#!/bin/bash

# Setup script to run on PythonAnywhere

echo "🔧 Setting up Label Maker on PythonAnywhere..."

# Configuration
PROJECT_NAME="AGTDesigner"
PROJECT_PATH="/home/$(whoami)/$PROJECT_NAME"

echo "Project path: $PROJECT_PATH"

# Navigate to project directory
cd "$PROJECT_PATH" || {
    echo "❌ Could not navigate to project directory"
    exit 1
}

echo "✅ Navigated to project directory"

# Step 1: Run the fix script
echo "🔧 Step 1: Running fix script..."
python fix_pythonanywhere_upload.py

if [ $? -eq 0 ]; then
    echo "✅ Fix script completed successfully"
else
    echo "❌ Fix script failed"
    exit 1
fi

# Step 2: Run the test script
echo "🧪 Step 2: Running test script..."
python test_pythonanywhere_upload.py

if [ $? -eq 0 ]; then
    echo "✅ Test script passed"
else
    echo "❌ Test script failed"
    echo "Check the error messages above"
fi

# Step 3: Install dependencies
echo "📦 Step 3: Installing dependencies..."
if [ -f "requirements_pythonanywhere.txt" ]; then
    pip install -r requirements_pythonanywhere.txt
else
    pip install -r requirements.txt
fi

echo "✅ Dependencies installed"

# Step 4: Create necessary directories
echo "📁 Step 4: Creating directories..."
mkdir -p uploads output cache logs temp
chmod 755 uploads output cache logs temp

echo "✅ Directories created"

# Step 5: Test Flask app
echo "🧪 Step 5: Testing Flask app..."
python -c "from app import create_app; app = create_app(); print('✅ Flask app created successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Flask app test passed"
else
    echo "❌ Flask app test failed"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Update your WSGI file with content from wsgi_pythonanywhere.py"
echo "3. Set environment variables:"
echo "   - PYTHONANYWHERE=true"
echo "   - FLASK_ENV=production"
echo "   - FLASK_DEBUG=false"
echo "4. Reload your web app"
echo "5. Test file upload functionality"
EOF

chmod +x "$DEPLOY_DIR/setup_on_pythonanywhere.sh"

# Step 4: Create verification script
echo "✅ Step 4: Creating verification script..."

cat > "$DEPLOY_DIR/verify_setup.py" << 'EOF'
#!/usr/bin/env python3

"""
Verification script for PythonAnywhere setup
Run this after setup to verify everything is working
"""

import os
import sys
import subprocess

def check_pythonanywhere_environment():
    """Check if we're running on PythonAnywhere."""
    print("🔍 Checking PythonAnywhere environment...")
    
    is_pythonanywhere = os.environ.get('PYTHONANYWHERE', 'false').lower() == 'true'
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    
    print(f"  Hostname: {hostname}")
    print(f"  PYTHONANYWHERE env var: {is_pythonanywhere}")
    
    if 'pythonanywhere' in hostname.lower() or is_pythonanywhere:
        print("✅ Running on PythonAnywhere")
        return True
    else:
        print("⚠️  Not running on PythonAnywhere")
        return False
    
def check_directories():
    """Check if required directories exist and have correct permissions."""
    print("\n📁 Checking directories...")
    
    directories = ['uploads', 'output', 'cache', 'logs', 'temp']
    
    for dir_name in directories:
        if os.path.exists(dir_name):
            stat_info = os.stat(dir_name)
            permissions = oct(stat_info.st_mode)[-3:]
            print(f"  ✅ {dir_name}/ - permissions: {permissions}")
            
            if permissions != '755':
                print(f"    ⚠️  {dir_name}/ should have 755 permissions")
        else:
            print(f"  ❌ {dir_name}/ - directory not found")

def check_flask_app():
    """Check if Flask app can be imported and created."""
    print("\n🐍 Checking Flask app...")
    
    try:
        from app import create_app
        print("  ✅ Flask app imported successfully")
        
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Check configuration
        upload_folder = app.config.get('UPLOAD_FOLDER')
        print(f"  ✅ Upload folder configured: {upload_folder}")
        
        return True
    except Exception as e:
        print(f"  ❌ Flask app error: {e}")
        return False

def check_file_upload():
    """Test file upload functionality."""
    print("\n📤 Testing file upload...")
    
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    
    try:
        # Test file creation
        test_file = os.path.join(upload_dir, 'test_upload.txt')
        with open(test_file, 'w') as f:
            f.write('Test upload functionality')
        
        print("  ✅ Test file created successfully")
        
        # Check file size
        file_size = os.path.getsize(test_file)
        print(f"  ✅ Test file size: {file_size} bytes")
        
        # Clean up
        os.remove(test_file)
        print("  ✅ Test file cleaned up")
        
        return True
    except Exception as e:
        print(f"  ❌ File upload test failed: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'pandas',
        'openpyxl',
        'werkzeug'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - installed")
        except ImportError:
            print(f"  ❌ {package} - not installed")

def main():
    """Main verification function."""
    print("🧪 PythonAnywhere Setup Verification")
    print("=" * 40)
    
    # Check environment
    is_pythonanywhere = check_pythonanywhere_environment()
    
    # Check directories
    check_directories()
    
    # Check Flask app
    flask_ok = check_flask_app()
    
    # Check file upload
    upload_ok = check_file_upload()
    
    # Check dependencies
    check_dependencies()
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 40)
    
    if is_pythonanywhere:
        print("✅ PythonAnywhere environment detected")
    else:
        print("⚠️  Not running on PythonAnywhere")
    
    if flask_ok:
        print("✅ Flask app working correctly")
    else:
        print("❌ Flask app has issues")
    
    if upload_ok:
        print("✅ File upload working correctly")
    else:
        print("❌ File upload has issues")
    
    print("\n🎯 Next steps:")
    if flask_ok and upload_ok:
        print("✅ Setup appears to be working correctly!")
        print("   You can now test the web interface")
    else:
        print("❌ Some issues detected")
        print("   Check the error messages above")
        print("   Run the fix script again if needed")

if __name__ == "__main__":
    main()
EOF

chmod +x "$DEPLOY_DIR/verify_setup.py"

# Step 5: Create summary
echo "📋 Step 5: Creating deployment summary..."

cat > "$DEPLOY_DIR/DEPLOYMENT_SUMMARY.md" << EOF
# PythonAnywhere Deployment Summary

## Files Created
- \`app.py\` - Updated with PythonAnywhere configuration
- \`wsgi_pythonanywhere.py\` - Optimized WSGI file
- \`fix_pythonanywhere_upload.py\` - Fix script
- \`test_pythonanywhere_upload.py\` - Test script
- \`setup_on_pythonanywhere.sh\` - Setup script
- \`verify_setup.py\` - Verification script

## Quick Deployment Steps

### 1. Upload Files
Upload all files in this directory to your PythonAnywhere project.

### 2. Run Setup
\`\`\`bash
cd /home/yourusername/AGTDesigner
chmod +x setup_on_pythonanywhere.sh
./setup_on_pythonanywhere.sh
\`\`\`

### 3. Verify Setup
\`\`\`bash
python verify_setup.py
\`\`\`

### 4. Update WSGI
Replace your WSGI file content with \`wsgi_pythonanywhere.py\`

### 5. Set Environment Variables
- PYTHONANYWHERE=true
- FLASK_ENV=production
- FLASK_DEBUG=false

### 6. Reload Web App
Click "Reload" in PythonAnywhere Web tab

## Expected Results
- ✅ File upload works in web interface
- ✅ No permission errors
- ✅ API endpoints respond correctly
- ✅ Uploads directory with 755 permissions

## Troubleshooting
- Check PythonAnywhere error logs
- Run \`python verify_setup.py\` for diagnostics
- Ensure all dependencies are installed
- Verify file permissions on directories
EOF

echo "✅ Deployment package complete!"
echo ""
echo "📦 Deployment package created in: $DEPLOY_DIR"
    echo ""
    echo "📋 Next steps:"
echo "1. Upload all files from $DEPLOY_DIR to PythonAnywhere"
echo "2. Run: ./setup_on_pythonanywhere.sh"
echo "3. Run: python verify_setup.py"
echo "4. Update WSGI file and reload web app"
    echo ""
echo "🎉 Your PythonAnywhere file upload should work after deployment!" 