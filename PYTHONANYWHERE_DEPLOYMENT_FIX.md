# PythonAnywhere Deployment Fix - Timeout Issues

## Problem Identified

Your app works locally but times out on PythonAnywhere due to:

1. **Heavy Initialization on Startup** - Lines 1842-1843 in [app.py](app.py#L1842-L1843):
   ```python
   start_storage_cleanup_scheduler()
   start_daily_upload_cleanup_scheduler(run_hour=0, run_minute=0)
   ```
   These create background threads that may cause startup delays.

2. **Large App File** - app.py is 1.2MB and 24,120 lines - extremely large for a web app
   - Takes significant time to parse and load
   - PythonAnywhere has strict 120-second timeout for WSGI startup

3. **Missing requirements.txt** - No requirements.txt in root directory
   - Dependencies may not be properly installed on PythonAnywhere

4. **WSGI Path Mismatch** - [wsgi.py](wsgi.py#L12) points to `/home/adamcordova/AGTDesigner`
   - May not match your actual PythonAnywhere directory

## Critical Fixes Required

### Fix 1: Update WSGI Configuration Path

Edit [wsgi.py](wsgi.py) line 12 to match your actual PythonAnywhere path:

```python
# Current (line 12):
project_dir = '/home/adamcordova/AGTDesigner'

# Change to your actual path (check in PythonAnywhere Files tab):
project_dir = '/home/YOUR_USERNAME/YOUR_PROJECT_FOLDER'
```

**To find your correct path:**
1. Go to PythonAnywhere Dashboard → Files
2. Navigate to where app.py is located
3. Copy that full path

### Fix 2: Disable Background Schedulers on PythonAnywhere

The background cleanup threads are causing startup delays. Edit [app.py](app.py#L1842-L1843):

**Current code (lines 1842-1843):**
```python
start_storage_cleanup_scheduler()
start_daily_upload_cleanup_scheduler(run_hour=0, run_minute=0)
```

**Change to:**
```python
# Only start schedulers if not on PythonAnywhere (they cause timeout issues)
if not PYTHONANYWHERE_OPTIMIZATION:
    start_storage_cleanup_scheduler()
    start_daily_upload_cleanup_scheduler(run_hour=0, run_minute=0)
else:
    logging.info("Background schedulers disabled on PythonAnywhere to prevent startup timeout")
```

### Fix 3: Install Dependencies

1. Upload [requirements.txt](requirements.txt) to your PythonAnywhere project root (created for you)

2. Open a Bash console on PythonAnywhere and run:
```bash
cd /home/YOUR_USERNAME/YOUR_PROJECT_FOLDER
pip3 install --user -r requirements.txt
```

3. Wait for installation to complete (may take 5-10 minutes)

### Fix 4: Optimize WSGI Startup

Your [wsgi.py](wsgi.py) already has good optimizations, but ensure these environment variables are set:

```python
# These should already be in wsgi.py (lines 33-37):
os.environ['FORCE_FAST_LOAD'] = 'True'
os.environ['DISABLE_STARTUP_FILE_LOADING'] = 'True'
os.environ['MAX_MEMORY_MB'] = '450'
```

✅ These are already set in your wsgi.py - good!

### Fix 5: Reload Web App

After making changes:

1. Go to PythonAnywhere Dashboard → Web
2. Click **"Reload YOUR_USERNAME.pythonanywhere.com"** button
3. Check error log for any issues (link on Web tab)

## Deployment Checklist

- [ ] Fix wsgi.py path (line 12) to match actual project directory
- [ ] Disable background schedulers in app.py (lines 1842-1843)
- [ ] Upload requirements.txt to project root
- [ ] Install dependencies via Bash console
- [ ] Reload web app on PythonAnywhere
- [ ] Check error log for any remaining issues
- [ ] Test the website - should load without timeout

## Expected Results

After fixes:
- ✅ App loads within 30-60 seconds (well under 120s timeout)
- ✅ No startup thread delays
- ✅ All dependencies properly installed
- ✅ Background cleanup disabled (can run manually if needed)

## Troubleshooting

### Still Getting Timeout?

1. **Check error log** (Web tab → error log link):
   - Look for import errors (missing dependencies)
   - Check for path errors (wsgi.py pointing to wrong directory)

2. **Verify Python path**:
   ```bash
   which python3
   pip3 list | grep -i flask
   ```

3. **Test import manually**:
   ```bash
   cd /home/YOUR_USERNAME/YOUR_PROJECT_FOLDER
   python3 -c "from app import app; print('Success!')"
   ```
   If this times out or errors, the issue is in app.py initialization.

### Import Errors?

If you see `ModuleNotFoundError` in error log:

```bash
pip3 install --user PACKAGE_NAME
```

Common missing packages:
- `pip3 install --user Flask Flask-CORS Flask-Session Flask-Compress`
- `pip3 install --user pandas numpy openpyxl python-docx`
- `pip3 install --user docxtpl qrcode Pillow`

### Wrong Python Version?

PythonAnywhere Web tab → Source code section:
- Change Python version to 3.10 or 3.11
- Reload web app

## Performance Notes

Your app is optimized for PythonAnywhere but the size is concerning:
- **app.py: 1.2MB, 24,120 lines** - This is extremely large
- Consider refactoring into smaller modules in the future
- Current fix: disable heavy startup operations

## PythonAnywhere-Specific Limitations

Free/Basic tier:
- ⚠️ 120-second WSGI timeout (your main issue)
- ⚠️ 1 worker only (line 12 in [gunicorn_config.py](gunicorn_config.py))
- ⚠️ 512MB memory limit
- ⚠️ No always-on tasks (background schedulers won't persist anyway)

Your app already accounts for these - good optimization!

## Quick Fix Script

Run this on PythonAnywhere Bash console:

```bash
#!/bin/bash
# Quick deployment fix script

cd ~  # Go to home
PROJECT_DIR=$(find . -name "app.py" -type f | head -1 | xargs dirname)
cd "$PROJECT_DIR"

echo "Found project at: $PROJECT_DIR"

# Install dependencies
echo "Installing dependencies..."
pip3 install --user -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Edit wsgi.py line 12: project_dir = '$PROJECT_DIR'"
echo "2. Edit app.py lines 1842-1843: wrap schedulers in 'if not PYTHONANYWHERE_OPTIMIZATION:'"
echo "3. Go to Web tab and click Reload"
```

## Support

If still having issues, check:
1. PythonAnywhere error log (Web tab)
2. PythonAnywhere server log (Web tab)
3. Your actual project path matches wsgi.py
4. All dependencies installed successfully

The timeout is almost certainly due to the background scheduler threads starting on line 1842-1843. Disabling those on PythonAnywhere should fix the issue immediately.
