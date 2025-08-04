# PythonAnywhere Quick Fix - Missing Dependencies

## 🚨 **URGENT: Missing flask_cors Error**

Your PythonAnywhere deployment is failing because `flask_cors` is not installed. Here's how to fix it:

## 🔧 **Quick Fix (5 minutes)**

### **Option 1: Automated Fix (Recommended)**

1. **Log into PythonAnywhere**
2. **Open a Bash Console**
3. **Run this command:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/leruseadam/AGTDesigner/main/fix_pythonanywhere_missing_deps.sh | bash
   ```

### **Option 2: Manual Fix**

1. **Open PythonAnywhere Bash Console**
2. **Navigate to your project:**
   ```bash
   cd ~/AGTDesigner
   ```

3. **Activate virtual environment:**
   ```bash
   source venv_pythonanywhere/bin/activate
   ```

4. **Install missing dependencies:**
   ```bash
   pip install flask-cors
   pip install flask-caching
   pip install python-dotenv
   pip install gunicorn
   pip install werkzeug
   pip install jinja2
   pip install pandas
   pip install numpy
   pip install openpyxl
   pip install python-docx
   pip install pillow
   pip install docxtpl
   ```

5. **Test the application:**
   ```bash
   python -c "from flask_cors import CORS; from app import create_app; print('✅ Fixed!')"
   ```

6. **Reload your web app in PythonAnywhere Web tab**

## 🎯 **What This Fixes**

- ✅ **flask_cors**: CORS support for web requests
- ✅ **flask_caching**: Performance optimization
- ✅ **python-dotenv**: Environment variable support
- ✅ **gunicorn**: Production web server
- ✅ **All other missing dependencies**

## 📋 **Verification Steps**

After running the fix:

1. **Check PythonAnywhere Web tab**
2. **Click "Reload"**
3. **Check error logs** - should be clean now
4. **Visit your website** - should work!

## 🚀 **If Still Having Issues**

1. **Check virtual environment path** in PythonAnywhere Web tab
2. **Verify it's set to**: `/home/adamcordova/AGTDesigner/venv_pythonanywhere`
3. **Make sure WSGI file points to correct app import**

## 📞 **Emergency Commands**

If you need to manually install just the critical missing package:

```bash
cd ~/AGTDesigner
source venv_pythonanywhere/bin/activate
pip install flask-cors
```

---

**🎉 This should fix your PythonAnywhere deployment immediately!** 