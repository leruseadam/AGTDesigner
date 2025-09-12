#!/bin/bash
# PythonAnywhere Deployment Script
# Run this on PythonAnywhere after uploading the files

echo "🚀 Deploying LabelMaker to PythonAnywhere..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3.10 install --user -r requirements.txt

# Create sessions directory
echo "📁 Creating sessions directory..."
mkdir -p sessions

# Set permissions
echo "🔐 Setting file permissions..."
chmod 755 app.py
chmod 644 product_database.db
chmod -R 755 static/
chmod -R 755 templates/
chmod -R 755 src/

# Verify deployment
echo "🔍 Verifying deployment..."
if [ -f "app.py" ] && [ -f "product_database.db" ] && [ -d "src" ] && [ -d "static" ] && [ -d "templates" ]; then
    echo "✅ All essential files present"
else
    echo "❌ Missing essential files"
    exit 1
fi

echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Go to Web tab in PythonAnywhere dashboard"
echo "2. Add new web app → Manual configuration"
echo "3. Python 3.10"
echo "4. Source code: /home/yourusername/pythonanywhere_deployment/"
echo "5. WSGI file: /home/yourusername/pythonanywhere_deployment/app.py"
echo "6. Click Reload to start the app"
