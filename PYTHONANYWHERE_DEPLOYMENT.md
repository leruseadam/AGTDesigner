# 🚀 PythonAnywhere Deployment Guide

This guide will help you deploy your LabelMaker application to PythonAnywhere with **ZERO differences** from your local version.

## 📦 Deployment Package Ready

Your deployment package is ready:
- **Directory**: `pythonanywhere_deployment/`
- **Zip file**: `labelmaker_pythonanywhere.zip`
- **Deployment script**: `pythonanywhere_deploy.sh`

## 🎯 Quick Deployment (3 Steps)

### Step 1: Upload Files
**Option A: Using Zip File (Recommended)**
1. Go to PythonAnywhere dashboard
2. Open Files tab
3. Upload `labelmaker_pythonanywhere.zip`
4. Extract it in your home directory

**Option B: Using Git (Alternative)**
```bash
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner
```

### Step 2: Install Dependencies
```bash
pip3.10 install --user -r requirements.txt
```

### Step 3: Configure Web App
1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.10**
5. Set source code path to your app directory
6. Set WSGI file to: `/home/yourusername/pythonanywhere_deployment/app.py`
7. Click **"Reload"** to start the app

## ✅ What's Included

### Core Files
- ✅ `app.py` - Main Flask application
- ✅ `requirements.txt` - Python dependencies
- ✅ `product_database.db` - SQLite database (262MB with all your data)

### Source Code
- ✅ `src/` - Complete source code directory
- ✅ `src/core/data/product_database.py` - Database handler
- ✅ `src/core/data/excel_processor.py` - Excel processing
- ✅ `src/core/data/json_matcher.py` - JSON matching
- ✅ `src/core/generation/` - Template generation

### Static Files
- ✅ `static/` - CSS, JavaScript, images
- ✅ `static/js/main.js` - Main JavaScript
- ✅ `static/css/styles.css` - Styling

### Templates
- ✅ `templates/` - HTML templates
- ✅ `templates/index.html` - Main interface

### Database Files
- ✅ `AGT_Complete_Product_Database_20250822_020841.xlsx`
- ✅ `AGT_Essential_Product_Database_20250822_022042.xlsx`
- ✅ `comprehensive_product_database_20250822_020149.xlsx`
- ✅ `comprehensive_product_database_with_pricing.xlsx`

## 🔧 Detailed Setup Instructions

### 1. File Upload
```bash
# If using zip file
unzip labelmaker_pythonanywhere.zip
cd pythonanywhere_deployment

# If using git
git clone https://github.com/leruseadam/AGTDesigner.git
cd AGTDesigner
```

### 2. Dependencies Installation
```bash
pip3.10 install --user -r requirements.txt
```

### 3. Web App Configuration
1. **Source code**: `/home/yourusername/pythonanywhere_deployment/`
2. **WSGI file**: `/home/yourusername/pythonanywhere_deployment/app.py`
3. **Python version**: 3.10
4. **Static files**: Will be served automatically from `static/`

### 4. Database Setup
- ✅ **No setup required** - SQLite database is included
- ✅ **All data preserved** - 262MB of product data
- ✅ **Cost column removed** - As per your recent changes

## 🐛 Troubleshooting

### Common Issues & Solutions

**1. Import Errors**
```bash
# Check Python version
python3.10 --version

# Reinstall dependencies
pip3.10 install --user -r requirements.txt
```

**2. Database Errors**
```bash
# Check database file exists
ls -la product_database.db

# Check file permissions
chmod 644 product_database.db
```

**3. Static Files Not Loading**
- Verify `static/` directory exists
- Check web app configuration
- Ensure static files are in correct location

**4. App Not Starting**
- Check error logs in Web tab
- Verify all files are present
- Check file permissions

### File Structure Verification
Your deployed app should have:
```
/home/yourusername/pythonanywhere_deployment/
├── app.py                          ✅ Main application
├── requirements.txt                ✅ Dependencies
├── product_database.db             ✅ Database (262MB)
├── src/
│   └── core/
│       └── data/
│           └── product_database.py ✅ Database handler
├── static/
│   └── js/
│       └── main.js                 ✅ JavaScript
├── templates/
│   └── index.html                  ✅ Main template
└── [Excel database files]          ✅ Product data
```

## 🎉 Success Verification

After deployment, verify:
- [ ] App loads without errors
- [ ] Database queries work
- [ ] Static files load properly
- [ ] Templates render correctly
- [ ] All functionality works as expected

## 📞 Support

If you encounter issues:
1. Check PythonAnywhere error logs
2. Verify file permissions
3. Ensure all dependencies are installed
4. Check that database file is present and accessible

## 🚀 Ready to Deploy!

Your deployment package is complete and ready. The app will work **exactly** as it does on your local machine with **zero differences**.

**Next step**: Upload `labelmaker_pythonanywhere.zip` to PythonAnywhere and follow the setup steps above.
