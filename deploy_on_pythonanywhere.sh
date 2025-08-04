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
