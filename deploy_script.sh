#!/bin/bash
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
