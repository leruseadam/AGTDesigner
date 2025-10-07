#!/bin/bash

# Local Preparation Script for PythonAnywhere Deployment
# ======================================================
# Run this locally to prepare files for PythonAnywhere deployment

echo "🚀 AGT Label Maker - Local Preparation for PythonAnywhere"
echo "======================================================="
echo "Preparing deployment for commit: af1ec360 - Add JointRatio handling for pre-rolls in database processing"
echo ""

# Check current git status
echo "📊 Current Repository Status:"
echo "- Current commit: $(git log -1 --oneline)"
echo "- Current branch: $(git branch --show-current)"
echo "- Repository URL: $(git remote get-url origin)"
echo ""

# Verify we're on the right commit
CURRENT_COMMIT=$(git log -1 --format="%h")
if [ "$CURRENT_COMMIT" = "af1ec36" ]; then
    echo "✅ Confirmed: Currently on commit af1ec360 (JointRatio handling)"
else
    echo "⚠️ Warning: Not on commit af1ec360. Current: $CURRENT_COMMIT"
    echo "Resetting to af1ec360..."
    git reset --hard af1ec360
    echo "✅ Reset to commit af1ec360"
fi

# Create PythonAnywhere deployment commands
echo ""
echo "📋 PythonAnywhere Deployment Commands"
echo "====================================="
echo ""
echo "Copy and paste these commands into your PythonAnywhere Bash console:"
echo ""
echo "# Step 1: Clone/Update Repository"
echo "cd ~"
echo "if [ -d 'AGTDesigner' ]; then"
echo "    cd AGTDesigner"
echo "    git fetch origin"
echo "    git reset --hard af1ec360"
echo "    echo '✅ Updated to commit af1ec360'"
echo "else"
echo "    git clone https://github.com/leruseadam/AGTDesigner.git"
echo "    cd AGTDesigner"
echo "    git reset --hard af1ec360"
echo "    echo '✅ Cloned and reset to commit af1ec360'"
echo "fi"
echo ""
echo "# Step 2: Install Dependencies"
echo "pip3.11 install --user Flask==2.3.3 Werkzeug==2.3.7 Flask-CORS==4.0.0 Flask-Caching==2.1.0"
echo "pip3.11 install --user pandas==2.1.4 openpyxl==3.1.2 xlrd==2.0.1"
echo "pip3.11 install --user python-docx==0.8.11 docxtpl==0.16.7 docxcompose==1.4.0 lxml==4.9.3"
echo "pip3.11 install --user Pillow==10.1.0 python-dateutil==2.8.2 pytz==2023.3"
echo "pip3.11 install --user jellyfish==1.2.0 requests>=2.32.0 fuzzywuzzy>=0.18.0 python-Levenshtein>=0.27.0"
echo ""
echo "# Step 3: Create Directories"
echo "mkdir -p uploads output cache sessions logs temp"
echo "chmod 755 uploads output cache sessions logs temp"
echo ""
echo "# Step 4: Create WSGI File"
echo "cat > wsgi.py << 'EOF'"
echo "#!/usr/bin/env python3"
echo "import os"
echo "import sys"
echo "import logging"
echo ""
echo "# Project directory"
echo "project_dir = '/home/{}/AGTDesigner'.format(os.environ.get('USER', 'yourusername'))"
echo ""
echo "# Add to Python path"
echo "if project_dir not in sys.path:"
echo "    sys.path.insert(0, project_dir)"
echo ""
echo "# Environment variables"
echo "os.environ['PYTHONANYWHERE_SITE'] = 'True'"
echo "os.environ['FLASK_ENV'] = 'production'"
echo "os.environ['FLASK_DEBUG'] = 'False'"
echo ""
echo "# Configure logging"
echo "logging.basicConfig(level=logging.ERROR)"
echo "for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas']:"
echo "    logging.getLogger(logger_name).setLevel(logging.ERROR)"
echo ""
echo "try:"
echo "    from app import app as application"
echo "    application.config.update("
echo "        DEBUG=False,"
echo "        TESTING=False,"
echo "        TEMPLATES_AUTO_RELOAD=False,"
echo "        SEND_FILE_MAX_AGE_DEFAULT=31536000,"
echo "        MAX_CONTENT_LENGTH=50 * 1024 * 1024,"
echo "    )"
echo "    print('WSGI application loaded successfully')"
echo "except Exception as e:"
echo "    print(f'Error: {e}')"
echo "    raise"
echo "EOF"
echo ""
echo "# Step 5: Test Installation"
echo "python3 -c \"import app; print('✅ App imports successfully')\""
echo ""
echo "# Step 6: Display Status"
echo "echo '🎉 JointRatio Deployment Complete!'"
echo "echo '=================================='"
echo "echo 'Repository: /home/\$USER/AGTDesigner'"
echo "echo 'WSGI file: /home/\$USER/AGTDesigner/wsgi.py'"
echo "echo 'Commit: af1ec360 - Add JointRatio handling for pre-rolls in database processing'"
echo ""
echo "echo '📋 Next: Configure Web App in PythonAnywhere Web tab'"
echo "echo '1. Source code: /home/\$USER/AGTDesigner'"
echo "echo '2. WSGI file: /home/\$USER/AGTDesigner/wsgi.py'"
echo "echo '3. Static files: /home/\$USER/AGTDesigner/static/'"
echo "echo '4. Reload web app'"
echo ""

# Create a simple deployment file for easy copying
cat > pythonanywhere_commands.txt << 'EOF'
# PythonAnywhere Deployment Commands
# Copy and paste these into your PythonAnywhere Bash console

# Step 1: Clone/Update Repository
cd ~
if [ -d 'AGTDesigner' ]; then
    cd AGTDesigner
    git fetch origin
    git reset --hard af1ec360
    echo '✅ Updated to commit af1ec360'
else
    git clone https://github.com/leruseadam/AGTDesigner.git
    cd AGTDesigner
    git reset --hard af1ec360
    echo '✅ Cloned and reset to commit af1ec360'
fi

# Step 2: Install Dependencies
pip3.11 install --user Flask==2.3.3 Werkzeug==2.3.7 Flask-CORS==4.0.0 Flask-Caching==2.1.0
pip3.11 install --user pandas==2.1.4 openpyxl==3.1.2 xlrd==2.0.1
pip3.11 install --user python-docx==0.8.11 docxtpl==0.16.7 docxcompose==1.4.0 lxml==4.9.3
pip3.11 install --user Pillow==10.1.0 python-dateutil==2.8.2 pytz==2023.3
pip3.11 install --user jellyfish==1.2.0 requests>=2.32.0 fuzzywuzzy>=0.18.0 python-Levenshtein>=0.27.0

# Step 3: Create Directories
mkdir -p uploads output cache sessions logs temp
chmod 755 uploads output cache sessions logs temp

# Step 4: Create WSGI File
cat > wsgi.py << 'WSGIEOF'
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
WSGIEOF

# Step 5: Test Installation
python3 -c "import app; print('✅ App imports successfully')"

# Step 6: Display Status
echo '🎉 JointRatio Deployment Complete!'
echo '=================================='
echo 'Repository: /home/$USER/AGTDesigner'
echo 'WSGI file: /home/$USER/AGTDesigner/wsgi.py'
echo 'Commit: af1ec360 - Add JointRatio handling for pre-rolls in database processing'
echo ''
echo '📋 Next: Configure Web App in PythonAnywhere Web tab'
echo '1. Source code: /home/$USER/AGTDesigner'
echo '2. WSGI file: /home/$USER/AGTDesigner/wsgi.py'
echo '3. Static files: /home/$USER/AGTDesigner/static/'
echo '4. Reload web app'
EOF

echo ""
echo "✅ Created pythonanywhere_commands.txt with all deployment commands"
echo ""
echo "📋 Next Steps:"
echo "1. Open pythonanywhere_commands.txt"
echo "2. Copy all the commands"
echo "3. Paste them into your PythonAnywhere Bash console"
echo "4. Configure your Web app in the PythonAnywhere Web tab"
echo ""
echo "🎯 Your deployment will include:"
echo "- Commit af1ec360: Add JointRatio handling for pre-rolls in database processing"
echo "- All required dependencies"
echo "- Proper WSGI configuration"
echo "- JointRatio functionality for pre-roll processing"
echo ""
echo "✅ Ready for PythonAnywhere deployment!"
