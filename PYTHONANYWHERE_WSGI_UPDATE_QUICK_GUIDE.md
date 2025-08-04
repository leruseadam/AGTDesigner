# PythonAnywhere WSGI Update - Quick Guide

## 🚨 Current Issue
Your PythonAnywhere WSGI configuration is still pointing to:
```
/var/www/www_agtpricetags_com_wsgi.py
```

## ✅ Solution
Change it to point to the optimized WSGI file:
```
/home/adamcordova/AGTDesigner/wsgi_pythonanywhere.py
```

## 📋 Steps to Fix

### 1. Update WSGI Configuration Path
1. **Log into PythonAnywhere**
2. **Go to 'Web' tab**
3. **Click on your web app** (www.agtpricetags.com)
4. **Scroll to 'Code' section**
5. **Find 'WSGI configuration file' field**
6. **Change from:** `/var/www/www_agtpricetags_com_wsgi.py`
7. **Change to:** `/home/adamcordova/AGTDesigner/wsgi_pythonanywhere.py`
8. **Click 'Save'**

### 2. Ensure WSGI File Exists
1. **Go to 'Files' tab**
2. **Navigate to:** `/home/adamcordova/AGTDesigner/`
3. **Check if `wsgi_pythonanywhere.py` exists**
4. **If not, upload it from your local project**

### 3. Reload Web App
1. **Go back to 'Web' tab**
2. **Click 'Reload' button**
3. **Wait for reload to complete**

## 🎯 Expected Results
- **Startup time:** Under 10 seconds (vs 58 seconds before)
- **Log messages:**
  - "Lazy loading enabled - not loading default file during startup"
  - "Default file loading disabled for testing/performance optimization"
  - "WSGI application loaded successfully with performance optimizations"

## 🔧 If Issues Occur
1. **Check error logs** in PythonAnywhere dashboard
2. **Verify file path** is correct
3. **Ensure all files are uploaded** to the correct location
4. **Check file permissions** on the WSGI file

## 📞 Need Help?
- Check the full `WSGI_PERFORMANCE_OPTIMIZATION_GUIDE.md` for detailed instructions
- Run `python deploy_wsgi_optimization.py` for step-by-step guidance 