#!/bin/bash

# PythonAnywhere Deployment Script - JointRatio Handling Version
# =============================================================
# This script deploys the current state (commit af1ec360) to PythonAnywhere
# Run this script in a PythonAnywhere Bash console

echo "🚀 AGT Label Maker - PythonAnywhere Deployment (JointRatio Version)"
echo "=================================================================="
echo "Deploying commit: af1ec360 - Add JointRatio handling for pre-rolls in database processing"
echo ""

# Check if we're in PythonAnywhere
if [ ! -f "/home/$USER/.bashrc" ]; then
    echo "❌ This script should be run in a PythonAnywhere Bash console"
    exit 1
fi

# Step 1: Clone or update the repository
echo "📥 Step 1: Setting up repository..."
if [ -d "AGTDesigner" ]; then
    echo "🔄 Repository exists, updating to JointRatio commit..."
    cd AGTDesigner
    git fetch origin
    git reset --hard af1ec360
    echo "✅ Reset to commit af1ec360"
else
    echo "📦 Cloning repository..."
    git clone https://github.com/leruseadam/AGTDesigner.git
    cd AGTDesigner
    git reset --hard af1ec360
    echo "✅ Cloned and reset to commit af1ec360"
fi

# Step 2: Install dependencies
echo "📦 Step 2: Installing dependencies..."
pip3.11 install --user Flask==2.3.3 Werkzeug==2.3.7 Flask-CORS==4.0.0 Flask-Caching==2.1.0
pip3.11 install --user pandas==2.1.4 openpyxl==3.1.2 xlrd==2.0.1
pip3.11 install --user python-docx==0.8.11 docxtpl==0.16.7 docxcompose==1.4.0 lxml==4.9.3
pip3.11 install --user Pillow==10.1.0 python-dateutil==2.8.2 pytz==2023.3
pip3.11 install --user jellyfish==1.2.0 requests>=2.32.0 fuzzywuzzy>=0.18.0 python-Levenshtein>=0.27.0

# Step 3: Create required directories
echo "📁 Step 3: Creating required directories..."
mkdir -p uploads output cache sessions logs temp
chmod 755 uploads output cache sessions logs temp

# Step 4: Test the installation
echo "🧪 Step 4: Testing installation..."
if python3 -c "import app; print('✅ App imports successfully')"; then
    echo "✅ Application test passed"
else
    echo "❌ Application test failed"
    exit 1
fi

# Step 5: Create WSGI file
echo "⚙️ Step 5: Creating WSGI configuration..."
cat > wsgi.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import logging

# Project directory
project_dir = '/home/{}/AGTDesigner'.format(os.environ.get('USER', 'yourusername'))

# Add to Python path
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Environment variables
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure logging
logging.basicConfig(level=logging.ERROR)
for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

try:
    from app import app as application
    application.config.update(
        DEBUG=False,
        TESTING=False,
        TEMPLATES_AUTO_RELOAD=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,
    )
    print("WSGI application loaded successfully")
except Exception as e:
    print(f"Error: {e}")
    raise
EOF

echo "✅ WSGI file created"

# Step 6: Display deployment information
echo ""
echo "🎉 JointRatio Deployment Complete!"
echo "=================================="
echo ""
echo "📊 Deployment Status:"
echo "- Repository: https://github.com/leruseadam/AGTDesigner"
echo "- Commit: af1ec360 - Add JointRatio handling for pre-rolls in database processing"
echo "- Location: /home/$USER/AGTDesigner"
echo "- WSGI file: /home/$USER/AGTDesigner/wsgi.py"
echo ""
echo "📋 Next Steps in PythonAnywhere Web Tab:"
echo "1. Go to Web tab in your PythonAnywhere dashboard"
echo "2. Create a new web app (or edit existing):"
echo "   - Choose 'Manual configuration'"
echo "   - Select Python 3.11"
echo "3. Set source code: /home/$USER/AGTDesigner"
echo "4. Set WSGI file: /home/$USER/AGTDesigner/wsgi.py"
echo "5. Configure static files:"
echo "   - URL: /static/"
echo "   - Directory: /home/$USER/AGTDesigner/static/"
echo "6. Reload your web app"
echo ""
echo "🔧 JointRatio Features Included:"
echo "- Pre-roll joint ratio handling in database processing"
echo "- Enhanced product weight calculations"
echo "- Improved database integration"
echo ""
echo "🔄 For future updates:"
echo "cd AGTDesigner && git pull origin main && pip3.11 install --user -r requirements.txt"
echo "Then reload your web app in the Web tab"
echo ""
echo "✅ Ready for PythonAnywhere deployment with JointRatio handling!"
