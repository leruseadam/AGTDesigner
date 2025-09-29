# PythonAnywhere Deployment Guide

## 🚀 Complete Deployment Instructions

This guide will help you deploy the Label Maker application to PythonAnywhere with the large database (500MB).

### Prerequisites

- PythonAnywhere **Hacker plan** (required for 500MB database)
- PythonAnywhere account with console access
- GitHub repository access

---

## Step 1: Prepare Local Files

### 1.1 Database Preparation ✅
The database has been prepared and compressed:
- **Original size**: 499.8 MB
- **Compressed size**: 29.2 MB (94.1% compression)
- **Products**: 7,853
- **Strains**: 2,556

Files ready for upload:
- `uploads/product_database_pythonanywhere.db.gz` (29.2 MB)

### 1.2 Application Files ✅
All application files are ready:
- `app.py` (main Flask application)
- `wsgi_pythonanywhere_optimized.py` (WSGI configuration)
- `requirements.txt` (dependencies)
- `deploy_pythonanywhere_complete.sh` (deployment script)

---

## Step 2: Deploy to PythonAnywhere

### 2.1 Upload Code to PythonAnywhere

**Option A: Using Git (Recommended)**
```bash
# In PythonAnywhere console
cd ~/AGTDesigner
git pull origin main
```

**Option B: Manual Upload**
1. Go to PythonAnywhere Files tab
2. Navigate to `/home/adamcordova/AGTDesigner/`
3. Upload all application files

### 2.2 Run Deployment Script

```bash
# In PythonAnywhere console
cd ~/AGTDesigner
chmod +x deploy_pythonanywhere_complete.sh
./deploy_pythonanywhere_complete.sh
```

This script will:
- ✅ Install all Python dependencies
- ✅ Create required directories
- ✅ Set up WSGI configuration
- ✅ Test application import
- ✅ Prepare for web app configuration

---

## Step 3: Upload Database

### 3.1 Upload Compressed Database

1. **Go to PythonAnywhere Files tab**
2. **Navigate to**: `/home/adamcordova/AGTDesigner/uploads/`
3. **Upload**: `product_database_pythonanywhere.db.gz` (29.2 MB)

### 3.2 Extract Database

```bash
# In PythonAnywhere console
cd ~/AGTDesigner/uploads
gunzip product_database_pythonanywhere.db.gz
mv product_database_pythonanywhere.db product_database.db
```

### 3.3 Test Database

```bash
# Test database connection
python3.11 -c "
import sqlite3
conn = sqlite3.connect('uploads/product_database.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products')
print(f'Products: {cursor.fetchone()[0]:,}')
cursor.execute('SELECT COUNT(*) FROM strains')
print(f'Strains: {cursor.fetchone()[0]:,}')
conn.close()
print('✅ Database test successful')
"
```

Expected output:
```
Products: 7,853
Strains: 2,556
✅ Database test successful
```

---

## Step 4: Configure Web App

### 4.1 Create Web App

1. **Go to PythonAnywhere Web tab**
2. **Click**: "Add a new web app"
3. **Choose**: "Manual configuration"
4. **Select**: **Python 3.11**
5. **Don't use**: framework template

### 4.2 Configure WSGI File

1. **Click on**: WSGI configuration file link
2. **Replace contents** with:

```python
#!/usr/bin/env python3.11
"""
PythonAnywhere WSGI configuration for Label Maker application
Optimized for production deployment with large database
"""

import os
import sys
import logging
import site

# Configure the project directory
project_dir = '/home/adamcordova/AGTDesigner'

# Add project to Python path
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Add user site-packages for --user installed packages
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure minimal logging for production
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(message)s'
)

# Suppress verbose logging from libraries
for logger_name in ['werkzeug', 'urllib3', 'requests', 'pandas', 'openpyxl', 'docxcompose']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

try:
    # Import the Flask application
    from app import app as application
    
    # Production configuration
    application.config.update(
        DEBUG=False,
        TESTING=False,
        TEMPLATES_AUTO_RELOAD=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year cache for static files
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max file size
        SECRET_KEY=os.environ.get('SECRET_KEY', 'production-secret-key-change-me'),
    )
    
    print("✅ WSGI application loaded successfully")
    print(f"📁 Project directory: {project_dir}")
    print(f"🐍 Python version: {sys.version}")
    
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    raise
except Exception as e:
    print(f"❌ Error configuring Flask app: {e}")
    raise

# For direct execution
if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=5000)
```

### 4.3 Configure Static Files

1. **Scroll down** to "Static files" section
2. **Add mapping**:
   - **URL**: `/static/`
   - **Directory**: `/home/adamcordova/AGTDesigner/static/`

---

## Step 5: Final Configuration

### 5.1 Reload Web App

1. **Click**: "Reload" button in Web tab
2. **Wait**: 30-60 seconds for reload to complete

### 5.2 Test Application

1. **Visit**: `https://adamcordova.pythonanywhere.com`
2. **Check**: Application loads without errors
3. **Test**: Database functionality (JSON matching, etc.)

### 5.3 Monitor Logs

If there are issues:
1. **Go to**: Web tab → "Error log" link
2. **Check**: For any error messages
3. **Common issues**:
   - Missing dependencies
   - Database path issues
   - Memory limits

---

## Step 6: Performance Optimization

### 6.1 Memory Management

The application uses ~500MB database, so monitor memory usage:

```bash
# Check memory usage
free -h
```

### 6.2 Database Optimization

```bash
# Optimize database
python3.11 -c "
import sqlite3
conn = sqlite3.connect('uploads/product_database.db')
conn.execute('VACUUM')
conn.close()
print('✅ Database optimized')
"
```

---

## Troubleshooting

### Common Issues

**1. Application won't start**
- Check WSGI configuration
- Verify all dependencies installed
- Check error logs

**2. Database not found**
- Verify database path: `/home/adamcordova/AGTDesigner/uploads/product_database.db`
- Check file permissions
- Test database connection

**3. Memory issues**
- Upgrade to Hacker plan
- Monitor memory usage
- Consider database optimization

**4. Static files not loading**
- Verify static file mapping
- Check file permissions
- Ensure static directory exists

### Getting Help

1. **Check error logs** in PythonAnywhere Web tab
2. **Test components** individually:
   - Database connection
   - Application import
   - WSGI configuration
3. **Monitor resources** (memory, disk space)

---

## Success Checklist

- ✅ Code deployed to PythonAnywhere
- ✅ Dependencies installed
- ✅ Database uploaded and extracted
- ✅ WSGI configuration set
- ✅ Static files mapped
- ✅ Web app reloaded
- ✅ Application accessible
- ✅ Database functionality working
- ✅ JSON matching working
- ✅ Performance acceptable

---

## 🎉 Deployment Complete!

Your Label Maker application is now deployed to PythonAnywhere with:
- **7,853 products** in the database
- **2,556 strains** available
- **Full functionality** including JSON matching
- **Production-ready** configuration

**Access your application**: `https://adamcordova.pythonanywhere.com`