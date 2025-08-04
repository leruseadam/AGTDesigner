# PythonAnywhere Fix Instructions

## 🚨 **Current Issue**
The production server at `https://www.agtpricetags.com` is not loading any data because there are no Excel files in the uploads directory.

**Error**: `expected str, bytes or os.PathLike object, not NoneType`

## ✅ **Solution Options**

### **Option 1: Quick Fix (Recommended)**
1. **Go to PythonAnywhere Console**
   - Log into [PythonAnywhere.com](https://www.pythonanywhere.com)
   - Go to **Consoles** tab
   - Start a new **Bash console**

2. **Run the Upload Script**
   ```bash
   cd ~/AGTDesigner
   python pythonanywhere_upload_script.py
   ```

3. **Restart Web App**
   - Go to **Web** tab
   - Click **Reload** on your web app

### **Option 2: Manual File Upload**
1. **Go to PythonAnywhere Files**
   - Log into [PythonAnywhere.com](https://www.pythonanywhere.com)
   - Go to **Files** tab
   - Navigate to `~/AGTDesigner/uploads/`

2. **Upload File**
   - Click **Upload a file**
   - Upload: `A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx`
   - Or upload: `testFile.xlsx`

3. **Restart Web App**
   - Go to **Web** tab
   - Click **Reload**

### **Option 3: Web Interface Upload**
1. **Go to the Website**
   - Visit [https://www.agtpricetags.com](https://www.agtpricetags.com)

2. **Upload File**
   - Click **Choose File**
   - Select: `A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx`
   - Click **Upload**

## 🔧 **Verification Steps**

After implementing any solution:

1. **Test API Endpoints**
   ```bash
   curl https://www.agtpricetags.com/api/status
   curl https://www.agtpricetags.com/api/initial-data
   ```

2. **Check Expected Response**
   - `/api/status` should show `"data_loaded": true`
   - `/api/initial-data` should return JSON with data

3. **Test Web Interface**
   - Visit [https://www.agtpricetags.com](https://www.agtpricetags.com)
   - Should load without JavaScript errors
   - Should display available tags and filters

## 📁 **File Locations**

**Local Development:**
- `uploads/A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx`
- `uploads/testFile.xlsx`

**PythonAnywhere Production:**
- `/home/adamcordova/AGTDesigner/uploads/`
- Should contain at least one Excel file

## 🐛 **Troubleshooting**

### **If files still don't load:**
1. Check file permissions on PythonAnywhere
2. Verify the uploads directory exists
3. Ensure pandas is installed: `pip install pandas openpyxl`
4. Check PythonAnywhere logs for errors

### **If web app won't restart:**
1. Check PythonAnywhere quotas
2. Verify all dependencies are installed
3. Check for syntax errors in the code

## 📞 **Support**

If issues persist:
1. Check PythonAnywhere error logs
2. Verify the `get_default_upload_file()` function is working
3. Test with a minimal Excel file first

## 🎯 **Expected Result**

After successful implementation:
- ✅ API endpoints return data
- ✅ Web interface loads without errors
- ✅ Tags and filters are populated
- ✅ File upload functionality works
- ✅ Label generation works correctly 