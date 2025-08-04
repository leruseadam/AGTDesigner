#!/bin/bash

# Git-based PythonAnywhere Deployment Script
# This script helps deploy files to PythonAnywhere using git

echo "🚀 Git-based PythonAnywhere Deployment"
echo "======================================"

# Configuration
GITHUB_REPO="https://github.com/leruseadam/AGTDesigner.git"
PYTHONANYWHERE_USERNAME="adamcordova"
PROJECT_NAME="AGTDesigner"
PYTHONANYWHERE_PROJECT_PATH="/home/$PYTHONANYWHERE_USERNAME/$PROJECT_NAME"

echo "📋 Configuration:"
echo "  GitHub Repo: $GITHUB_REPO"
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

# Step 1: Create PythonAnywhere deployment script
echo "📝 Step 1: Creating PythonAnywhere deployment script..."

cat > "deploy_on_pythonanywhere.sh" << 'EOF'
#!/bin/bash

# PythonAnywhere Deployment Script
# Run this on PythonAnywhere to deploy from git

echo "🚀 Deploying Label Maker to PythonAnywhere from Git..."

# Configuration
GITHUB_REPO="https://github.com/leruseadam/AGTDesigner.git"
PROJECT_NAME="AGTDesigner"
PROJECT_PATH="/home/$(whoami)/$PROJECT_NAME"

echo "📋 Configuration:"
echo "  GitHub Repo: $GITHUB_REPO"
echo "  Project: $PROJECT_NAME"
echo "  Path: $PROJECT_PATH"
echo ""

# Step 1: Navigate to home directory
echo "📁 Step 1: Setting up project directory..."
cd /home/$(whoami)

# Step 2: Clone or update repository
if [ -d "$PROJECT_NAME" ]; then
    echo "📥 Updating existing repository..."
    cd "$PROJECT_NAME"
    git fetch origin
    git reset --hard origin/main
    git clean -fd
else
    echo "📥 Cloning repository..."
    git clone "$GITHUB_REPO" "$PROJECT_NAME"
    cd "$PROJECT_NAME"
fi

echo "✅ Repository updated"

# Step 3: Run the fix script
echo "🔧 Step 2: Running PythonAnywhere fix script..."
if [ -f "fix_pythonanywhere_upload.py" ]; then
    python fix_pythonanywhere_upload.py
    if [ $? -eq 0 ]; then
        echo "✅ Fix script completed successfully"
    else
        echo "❌ Fix script failed"
        exit 1
    fi
else
    echo "❌ fix_pythonanywhere_upload.py not found"
    exit 1
fi

# Step 4: Run the test script
echo "🧪 Step 3: Running test script..."
if [ -f "test_pythonanywhere_upload.py" ]; then
    python test_pythonanywhere_upload.py
    if [ $? -eq 0 ]; then
        echo "✅ Test script passed"
    else
        echo "❌ Test script failed"
        echo "Check the error messages above"
    fi
else
    echo "❌ test_pythonanywhere_upload.py not found"
fi

# Step 5: Install dependencies
echo "📦 Step 4: Installing dependencies..."
if [ -f "requirements_pythonanywhere.txt" ]; then
    pip install -r requirements_pythonanywhere.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  No requirements file found"
fi

echo "✅ Dependencies installed"

# Step 6: Create necessary directories
echo "📁 Step 5: Creating directories..."
mkdir -p uploads output cache logs temp
chmod 755 uploads output cache logs temp

echo "✅ Directories created"

# Step 7: Test Flask app
echo "🧪 Step 6: Testing Flask app..."
python -c "from app import create_app; app = create_app(); print('✅ Flask app created successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Flask app test passed"
else
    echo "❌ Flask app test failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
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
echo ""
echo "🔗 Your app should be available at: https://$(whoami).pythonanywhere.com"
EOF

chmod +x "deploy_on_pythonanywhere.sh"

# Step 2: Create PythonAnywhere console commands
echo "💻 Step 2: Creating PythonAnywhere console commands..."

cat > "pythonanywhere_commands.txt" << EOF
# PythonAnywhere Console Commands
# Copy and paste these commands in your PythonAnywhere Bash console

# 1. Navigate to home directory
cd /home/$PYTHONANYWHERE_USERNAME

# 2. Clone or update the repository
if [ -d "$PROJECT_NAME" ]; then
    cd $PROJECT_NAME
    git fetch origin
    git reset --hard origin/main
    git clean -fd
else
    git clone $GITHUB_REPO $PROJECT_NAME
    cd $PROJECT_NAME
fi

# 3. Run the deployment script
chmod +x deploy_on_pythonanywhere.sh
./deploy_on_pythonanywhere.sh

# 4. Verify setup
python verify_setup.py

# 5. Test the application
python -c "from app import create_app; app = create_app(); print('✅ App ready!')"
EOF

# Step 3: Create WSGI configuration
echo "⚙️  Step 3: Creating WSGI configuration..."

cat > "wsgi_config_for_pythonanywhere.txt" << 'EOF'
# WSGI Configuration for PythonAnywhere
# Replace your WSGI file content with this:

#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
Optimized for PythonAnywhere deployment with file upload support.
"""

import sys
import os
import logging
from datetime import datetime

# Disable stdout/stderr buffering to prevent BlockingIOError
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Add virtual environment to Python path
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')

if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)
    print(f"✅ Virtual environment site-packages added: {venv_site_packages}")
else:
    print(f"⚠️  Virtual environment site-packages not found at: {venv_site_packages}")
    print("Continuing without virtual environment...")

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure basic logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

# Ensure uploads directory exists with proper permissions
uploads_dir = os.path.join(project_dir, 'uploads')
os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
try:
    os.chmod(uploads_dir, 0o755)
    print(f"✅ Uploads directory configured: {uploads_dir}")
except Exception as e:
    print(f"⚠️  Could not set uploads directory permissions: {e}")

# Import the Flask app
try:
    from app import create_app
    print("✅ Successfully imported Flask app")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    raise

# Create the application instance
try:
    application = create_app()
    print("✅ Application created successfully")
except Exception as e:
    print(f"❌ Error creating application: {e}")
    raise

# Configure for production
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True

# Set production secret key
if not application.secret_key or application.secret_key == 'dev':
    application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')

print(f"✅ Label Maker application created successfully at {datetime.now()}")

# WSGI application entry point
if __name__ == "__main__":
    application.run()
EOF

# Step 4: Create environment variables configuration
echo "🔧 Step 4: Creating environment variables configuration..."

cat > "environment_variables_for_pythonanywhere.txt" << 'EOF'
# Environment Variables for PythonAnywhere
# Add these in your PythonAnywhere Web app configuration:

PYTHONANYWHERE=true
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=label-maker-production-key-2024
EOF

# Step 5: Create quick deployment guide
echo "📖 Step 5: Creating quick deployment guide..."

cat > "QUICK_DEPLOYMENT_GUIDE.md" << 'EOF'
# Quick PythonAnywhere Deployment Guide

## 🚀 Automated Deployment (Recommended)

### Step 1: Open PythonAnywhere Console
1. Go to PythonAnywhere dashboard
2. Click on **Consoles** tab
3. Start a new **Bash console**

### Step 2: Run Deployment Commands
Copy and paste these commands:

```bash
# Navigate to home directory
cd /home/yourusername

# Clone or update repository
if [ -d "AGTDesigner" ]; then
    cd AGTDesigner
    git fetch origin
    git reset --hard origin/main
    git clean -fd
else
    git clone https://github.com/leruseadam/AGTDesigner.git AGTDesigner
    cd AGTDesigner
fi

# Run deployment script
chmod +x deploy_on_pythonanywhere.sh
./deploy_on_pythonanywhere.sh
```

### Step 3: Configure Web App
1. Go to **Web** tab in PythonAnywhere
2. Click on your web app
3. Update **WSGI configuration file** with content from `wsgi_config_for_pythonanywhere.txt`
4. Add **Environment variables** from `environment_variables_for_pythonanywhere.txt`
5. Click **Reload**

### Step 4: Test
1. Visit your PythonAnywhere URL
2. Try uploading an Excel file
3. Check that file upload works

## 🔧 Manual Deployment (Alternative)

If automated deployment doesn't work:

1. **Upload files manually** through PythonAnywhere Files tab
2. **Run fix script**: `python fix_pythonanywhere_upload.py`
3. **Run test script**: `python test_pythonanywhere_upload.py`
4. **Update WSGI file** with provided configuration
5. **Set environment variables** and reload

## 🐛 Troubleshooting

### Common Issues:
- **Permission errors**: Run `chmod 755 uploads/` in console
- **Import errors**: Check virtual environment path in WSGI file
- **Upload fails**: Check browser console and PythonAnywhere error logs

### Debug Commands:
```bash
# Check PythonAnywhere environment
python -c "import os; print('PYTHONANYWHERE:', os.environ.get('PYTHONANYWHERE'))"

# Test file creation
python -c "import os; open('uploads/test.txt', 'w').write('test'); print('File creation OK')"

# Test Flask app
python -c "from app import create_app; app = create_app(); print('Flask app OK')"
```

## ✅ Success Indicators
- ✅ File upload works in web interface
- ✅ No permission errors in logs
- ✅ API endpoints respond correctly
- ✅ Uploads directory with 755 permissions

## 📞 Support
If you still have issues:
1. Check PythonAnywhere error logs
2. Run `python verify_setup.py`
3. Ensure all dependencies are installed
4. Verify file permissions on directories
EOF

echo "✅ All deployment files created!"
echo ""
echo "📦 Files created:"
echo "  - deploy_on_pythonanywhere.sh (run this on PythonAnywhere)"
echo "  - pythonanywhere_commands.txt (console commands)"
echo "  - wsgi_config_for_pythonanywhere.txt (WSGI configuration)"
echo "  - environment_variables_for_pythonanywhere.txt (environment variables)"
echo "  - QUICK_DEPLOYMENT_GUIDE.md (step-by-step guide)"
echo ""
echo "🚀 Next steps:"
echo "1. Copy the commands from pythonanywhere_commands.txt"
echo "2. Paste them in your PythonAnywhere Bash console"
echo "3. Follow the QUICK_DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 This will automatically deploy your app from git!" 