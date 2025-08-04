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
