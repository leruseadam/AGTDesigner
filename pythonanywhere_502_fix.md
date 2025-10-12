# Fix 502 Bad Gateway Error on PythonAnywhere

## Error Diagnosis
You're seeing these errors:
- `GET https://www.agtpricetags.com/api/initial-data 502 (Bad Gateway)`
- `GET https://www.agtpricetags.com/api/available-tags 502 (Bad Gateway)`

This means the Flask application is not running or crashing on startup.

## Solution Steps (In Order)

### Step 1: Check if Web App is Running
1. Go to https://www.pythonanywhere.com/user/adamcordova/webapps
2. Look for your web app (www.agtpricetags.com)
3. Check if it shows "Running" (green) or has any error messages

### Step 2: Reload the Web App (Most Common Fix)
1. Click the green **"Reload"** button at the top right
2. Wait 10-15 seconds
3. Try accessing https://www.agtpricetags.com again
4. Check browser console for errors

If this doesn't fix it, continue to Step 3.

### Step 3: Check Error Logs
1. On the Web tab, scroll down to "Log files"
2. Click on **"Error log"** (latest)
3. Look for Python errors at the bottom of the file
4. Common errors:
   - `ModuleNotFoundError`: Missing Python package
   - `FileNotFoundError`: Missing file (database, templates, etc.)
   - `SyntaxError`: Code syntax error
   - `ImportError`: Import problems

### Step 4: Verify File Paths
Check that these paths exist on PythonAnywhere:

```bash
/home/adamcordova/AGTDesigner/
/home/adamcordova/AGTDesigner/app.py
/home/adamcordova/AGTDesigner/uploads/
/home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db
/home/adamcordova/AGTDesigner/templates/
/home/adamcordova/AGTDesigner/static/
```

To check in PythonAnywhere console:
```bash
cd /home/adamcordova/AGTDesigner
ls -la
ls -la uploads/
ls -la uploads/product_database_AGT_Bothell.db
```

### Step 5: Check WSGI Configuration
1. On the Web tab, click "WSGI configuration file" link
2. Verify it contains:
   ```python
   project_dir = '/home/adamcordova/AGTDesigner'
   from app import app as application
   ```
3. Make sure the path matches where your files are actually located

### Step 6: Test Database Connection
Open a **Bash console** on PythonAnywhere and run:

```bash
cd /home/adamcordova/AGTDesigner
python3 -c "
import sqlite3
import os
db_path = '/home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db'
print(f'Database exists: {os.path.exists(db_path)}')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    print(f'Products in database: {count}')
    conn.close()
"
```

### Step 7: Test App Import
In PythonAnywhere Bash console:

```bash
cd /home/adamcordova/AGTDesigner
python3 -c "from app import app; print('✅ App imported successfully')"
```

If you see errors, they'll tell you what's wrong.

### Step 8: Check Python Version
In PythonAnywhere:
1. Go to Web tab
2. Check "Python version" dropdown
3. Should be Python 3.8 or higher
4. If changed, click "Reload"

### Step 9: Install Missing Dependencies
If error logs show missing packages, open Bash console:

```bash
cd /home/adamcordova/AGTDesigner
pip3 install --user -r requirements.txt
```

Or install specific packages:
```bash
pip3 install --user flask flask-cors flask-session pandas openpyxl python-docx qrcode pillow
```

### Step 10: Check Static Files Configuration
On Web tab, verify Static files mapping:
- URL: `/static/`
- Directory: `/home/adamcordova/AGTDesigner/static`

## Quick Diagnostic Script

Create this file on PythonAnywhere as `check_app_health.py`:

```python
#!/usr/bin/env python3
import os
import sys

print("=== PythonAnywhere App Health Check ===\n")

# Check working directory
print(f"1. Current directory: {os.getcwd()}")

# Check if app.py exists
app_py = '/home/adamcordova/AGTDesigner/app.py'
print(f"2. app.py exists: {os.path.exists(app_py)}")

# Check database
db_path = '/home/adamcordova/AGTDesigner/uploads/product_database_AGT_Bothell.db'
print(f"3. Database exists: {os.path.exists(db_path)}")
if os.path.exists(db_path):
    print(f"   Database size: {os.path.getsize(db_path):,} bytes")

# Check uploads directory
uploads_dir = '/home/adamcordova/AGTDesigner/uploads'
if os.path.exists(uploads_dir):
    files = os.listdir(uploads_dir)
    print(f"4. Files in uploads/: {len(files)} files")
    db_files = [f for f in files if f.endswith('.db')]
    print(f"   Database files: {db_files}")

# Check templates
templates_dir = '/home/adamcordova/AGTDesigner/templates'
print(f"5. Templates directory exists: {os.path.exists(templates_dir)}")

# Check static
static_dir = '/home/adamcordova/AGTDesigner/static'
print(f"6. Static directory exists: {os.path.exists(static_dir)}")

# Try importing app
print("\n7. Testing app import...")
sys.path.insert(0, '/home/adamcordova/AGTDesigner')
try:
    from app import app
    print("   ✅ App imported successfully!")
except Exception as e:
    print(f"   ❌ Error importing app: {e}")

print("\n=== End Health Check ===")
```

Run it:
```bash
cd /home/adamcordova/AGTDesigner
python3 check_app_health.py
```

## Common Fixes

### Fix 1: Missing Database
If database is missing, upload it from your local machine:
1. Go to PythonAnywhere Files tab
2. Navigate to `/home/adamcordova/AGTDesigner/uploads/`
3. Upload `product_database_AGT_Bothell.db`
4. Reload web app

### Fix 2: Wrong Python Version
1. Web tab → Python version dropdown
2. Select Python 3.9 or 3.10
3. Reload web app

### Fix 3: Import Errors
Check error log for specific missing modules, then:
```bash
pip3 install --user [missing-module-name]
```

### Fix 4: Path Issues in WSGI
If files are in a different location, update WSGI file:
1. Find actual location: `find /home/adamcordova -name app.py`
2. Update `project_dir` in WSGI file
3. Save and reload

## After Each Fix
1. **Reload** the web app (green button)
2. Wait 10-15 seconds
3. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
4. Test the site

## Still Not Working?

If none of these work, please provide:
1. The **error log** (last 50 lines)
2. The **server log** (last 50 lines)  
3. Output from the health check script above

You can access logs from PythonAnywhere Web tab → Log files section.

## Emergency: Force Restart

If everything looks correct but it still doesn't work:
1. Web tab → Click "Reload" button
2. Wait 30 seconds
3. Go to Consoles tab
4. Kill any running consoles
5. Go back to Web tab and reload again

This forces PythonAnywhere to completely restart your application.

