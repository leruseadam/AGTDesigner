#!/bin/bash

# Quick Fix for PythonAnywhere - Pull Latest Changes and Test
# Run this on PythonAnywhere to get the config.py fix

set -e

echo "🚀 Quick Fix for PythonAnywhere"
echo "==============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Step 1: Navigate to project
print_info "Step 1: Navigating to project..."
cd ~/AGTDesigner
print_success "Current directory: $(pwd)"

# Step 2: Pull latest changes
print_info "Step 2: Pulling latest changes..."
git pull origin main
print_success "Latest changes pulled"

# Step 3: Activate virtual environment
print_info "Step 3: Activating virtual environment..."
source venv_pythonanywhere/bin/activate
print_success "Virtual environment activated"

# Step 4: Test the fix
print_info "Step 4: Testing the fix..."
python -c "
try:
    from flask import Flask
    from flask_cors import CORS
    from flask_caching import Cache
    from app import create_app
    print('✅ All imports successful!')
    print('✅ Config module fix applied!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Other error: {e}')
    exit(1)
"
print_success "Application test passed!"

# Step 5: Test application creation
print_info "Step 5: Testing application creation..."
python -c "
try:
    from app import create_app
    app = create_app()
    print('✅ Application created successfully!')
except Exception as e:
    print(f'❌ Application creation error: {e}')
    exit(1)
"
print_success "Application creation test passed!"

print_info "🎉 Fix applied successfully!"
print_info "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload'"
echo "3. Your application should now work!"
echo ""
echo "The config.py module has been added and the import error should be resolved! 🚀" 