# Fresh PythonAnywhere Deployment Guide

## 🚀 **Complete Fresh Start - Step by Step**

### **Step 1: Create New PythonAnywhere Account (Optional)**
If you want a completely fresh start:
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Create a new account with a different email
3. This gives you a completely clean environment

### **Step 2: Set Up New Web App**
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10** (or latest available)
5. Set your domain (e.g., `yourusername.pythonanywhere.com`)

### **Step 3: Clone Fresh Repository**
1. Go to **Consoles** tab
2. Start a **Bash console**
3. Run these commands:

```bash
# Navigate to home directory
cd ~

# Remove old directory if it exists
rm -rf AGTDesigner_old

# Clone fresh repository
git clone https://github.com/yourusername/AGTDesigner.git
cd AGTDesigner

# Verify you have latest code
git log --oneline -3
```

### **Step 4: Set Up Virtual Environment**
```bash
# Create new virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install additional dependencies if needed
pip install flask flask-cors pandas openpyxl python-docx
```

### **Step 5: Configure Web App**
1. Go to **Web** tab
2. Click on your web app
3. Set **Source code** to: `/home/yourusername/AGTDesigner`
4. Set **Working directory** to: `/home/yourusername/AGTDesigner`
5. Set **WSGI configuration file** to point to your app.py

### **Step 6: Update WSGI File**
Edit the WSGI file to point to your app:

```python
import sys
path = '/home/yourusername/AGTDesigner'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### **Step 7: Create Uploads Directory**
```bash
# Create uploads directory
mkdir -p uploads

# Set permissions
chmod 755 uploads
```

### **Step 8: Upload Default File**
1. Go to **Files** tab
2. Navigate to `/home/yourusername/AGTDesigner/uploads/`
3. Upload your `testFile.xlsx` or any Excel file
4. This will be the default file loaded on startup

### **Step 9: Restart Web App**
1. Go to **Web** tab
2. Click **Reload** button
3. Wait for restart to complete

### **Step 10: Test the Application**
1. Visit your web app URL
2. Check if it loads without errors
3. Verify that tags are populated
4. Test file upload functionality

## 🔧 **Troubleshooting**

### **If you get import errors:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install missing packages
pip install package_name
```

### **If you get permission errors:**
```bash
# Set proper permissions
chmod -R 755 ~/AGTDesigner
chmod 755 ~/AGTDesigner/uploads
```

### **If the web app won't start:**
1. Check the **Error log** in the Web tab
2. Verify all dependencies are installed
3. Make sure the WSGI file points to the correct path

## 📝 **Quick Commands for Fresh Start**

```bash
# Complete fresh setup (run in PythonAnywhere Bash console)
cd ~
rm -rf AGTDesigner_old
git clone https://github.com/yourusername/AGTDesigner.git
cd AGTDesigner
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install flask flask-cors pandas openpyxl python-docx
mkdir -p uploads
chmod 755 uploads
```

## 🎯 **Expected Result**

After following these steps, you should have:
- ✅ Clean, fresh environment
- ✅ Latest code from GitHub
- ✅ All dependencies installed
- ✅ Working web application
- ✅ Default file loaded on startup
- ✅ Tags populated and working 