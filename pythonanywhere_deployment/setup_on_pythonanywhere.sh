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
