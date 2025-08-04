#!/bin/bash

# Quick PythonAnywhere Deployment Script
# Run this directly on PythonAnywhere

echo "🚀 Quick PythonAnywhere Deployment for Label Maker"

# Navigate to home directory
cd ~

# Clone or update repository
if [ -d "AGTDesigner" ]; then
    echo "📦 Updating existing repository..."
    cd AGTDesigner
    git pull origin main
else
    echo "📦 Cloning repository..."
    git clone https://github.com/leruseadam/AGTDesigner.git
    cd AGTDesigner
fi

# Remove old virtual environment
if [ -d "venv_pythonanywhere" ]; then
    echo "🗑️ Removing old virtual environment..."
    rm -rf venv_pythonanywhere
fi

# Create new virtual environment
echo "🐍 Creating virtual environment..."
python3.11 -m venv venv_pythonanywhere
source venv_pythonanywhere/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt
pip install flask-caching python-dotenv gunicorn

# Test application
echo "🧪 Testing application..."
python -c "from app import create_app; print('✅ Application ready!')"

# Create WSGI file
echo "🔧 Creating WSGI configuration..."
cat > wsgi.py << 'EOF'
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = os.path.join(project_dir, 'venv_pythonanywhere', 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
EOF

echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create a new web app (Manual configuration)"
echo "3. Set source code to: /home/$(whoami)/AGTDesigner"
echo "4. Set working directory to: /home/$(whoami)/AGTDesigner"
echo "5. Set WSGI file to: /var/www/$(whoami)_pythonanywhere_com_wsgi.py"
echo "6. Set virtual environment to: /home/$(whoami)/AGTDesigner/venv_pythonanywhere"
echo "7. Copy the content of wsgi.py to your WSGI file"
echo "8. Click 'Reload' to start the application"
echo ""
echo "🔗 Your app will be at: https://$(whoami).pythonanywhere.com" 