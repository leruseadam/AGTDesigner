# PythonAnywhere Deployment Guide - Large Database Solution
# =======================================================

## 🚀 Updated Deployment Instructions

### Step 1: Deploy Your Code
Copy and paste these commands into your PythonAnywhere Bash console:

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner

# Reset to the JointRatio commit
git reset --hard af1ec360

# Install dependencies
pip3.11 install --user Flask==2.3.3 Werkzeug==2.3.7 Flask-CORS==4.0.0 Flask-Caching==2.1.0
pip3.11 install --user pandas==2.1.4 openpyxl==3.1.2 xlrd==2.0.1
pip3.11 install --user python-docx==0.8.11 docxtpl==0.16.7 docxcompose==1.4.0 lxml==4.9.3
pip3.11 install --user Pillow==10.1.0 python-dateutil==2.8.2 pytz==2023.3
pip3.11 install --user jellyfish==1.2.0 requests>=2.32.0 fuzzywuzzy>=0.18.0 python-Levenshtein>=0.27.0

# Create required directories
mkdir -p uploads output cache sessions logs temp
chmod 755 uploads output cache sessions logs temp

# Create WSGI file
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

# Test the installation
python3 -c "import app; print('✅ App imports successfully')"

echo "🎉 Code deployment complete!"
```

### Step 2: Upload Compressed Database (Optional)
If you want your full database with 5,201 products:

1. **Download the compressed file**: `product_database_compressed.sql.gz` (0.3MB)
2. **Upload to PythonAnywhere**:
   - Go to **Files** tab
   - Navigate to `/home/yourusername/AGTDesigner/uploads/`
   - Upload `product_database_compressed.sql.gz`

3. **Restore the database**:
```bash
cd ~/AGTDesigner
python3 restore_database_pythonanywhere.py
```

### Step 3: Configure Web App
1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.11**
5. Set **Source code**: `/home/yourusername/AGTDesigner`
6. Set **WSGI file**: `/home/yourusername/AGTDesigner/wsgi.py`

### Step 4: Configure Static Files
Add static file mapping:
- **URL**: `/static/`
- **Directory**: `/home/yourusername/AGTDesigner/static/`

### Step 5: Reload and Test
1. Click **"Reload"** in Web tab
2. Visit: `https://yourusername.pythonanywhere.com`

## 🎯 What You'll Have:

### ✅ **With Default Sample File** (Always Works):
- 5 sample products
- All functionality working
- JointRatio handling
- File upload capability
- Label generation

### ✅ **With Full Database** (If Uploaded):
- 5,201 products
- 1,358 products with JointRatio
- Complete product database
- All advanced features

## 🔧 Troubleshooting:

### If Database Upload Fails:
```bash
# Use the sample database instead
cd ~/AGTDesigner
python3 restore_database_pythonanywhere.py
```

### If App Won't Start:
```bash
# Check error logs
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Test import
python3 -c "from app import app; print('OK')"
```

### If Static Files Don't Load:
- Check static file mapping in Web tab
- Ensure `/static/` URL points to correct directory
- Reload web app after changes

## 💡 Pro Tips:

1. **Start Simple**: Use default sample file first
2. **Test Gradually**: Upload small Excel files first
3. **Monitor Logs**: Check error logs for issues
4. **Backup**: Keep local version as backup

## 📊 File Sizes:
- **Compressed Database**: 0.3MB (uploadable)
- **Default Sample File**: 6KB (included)
- **Application Code**: ~50MB (via git clone)

Your application will work perfectly with either the sample file or the full database!