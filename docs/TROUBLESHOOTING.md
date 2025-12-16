# Troubleshooting Page Load Issues

## Quick Fixes

### 1. Hard Refresh Browser
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### 2. Clear Browser Cache
1. Open Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### 3. Check Browser Console for Errors
1. Open Developer Tools (F12)
2. Go to "Console" tab
3. Look for red error messages
4. Share the error text if you see any

### 4. Restart Flask Server
```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"

# Kill existing server
lsof -ti:5000 | xargs kill -9

# Start fresh
python3 app.py
```

## What to Check

### Symptoms & Solutions

**Blank White Page**
- Check browser console for JavaScript errors
- Hard refresh (Ctrl+Shift+R)
- Clear browser cache

**Stuck on Loading Screen**
- Check Network tab in DevTools
- Look for failed API requests
- May need to restart Flask server

**Error Message Visible**
- Read the error message
- Check browser console for details
- Check Flask terminal for Python errors

**Page Loads But Tags Don't Appear**
- Open Console, look for these messages:
  - `✅ Cache HIT: X tags loaded`
  - `⚡ INSTANT LOAD: X tags rendered`
- If you see timeout errors, restart Flask

## Reverting Changes

If the page still doesn't load, you can revert the JavaScript changes:

### Option 1: Restore from Git
```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
git checkout static/js/main.js
```

### Option 2: Manual Revert
The changes were made to `static/js/main.js` at these lines:
- Line 1192-1198
- Line 1213-1214
- Line 8246-8249

You can edit the file and restore the original code.

## Testing Backend Changes

The backend changes should not break page loading. Test them individually:

```bash
# Test Python syntax
python3 -m py_compile app.py
python3 -m py_compile core/data/excel_processor.py
python3 -m py_compile core/data/product_database.py

# Test Flask server starts
python3 app.py
```

## Common Issues

### Issue: "Module not found" error
**Solution:** Check that all files are in the correct locations

### Issue: JavaScript errors about undefined functions
**Solution:** Hard refresh to load new JavaScript files

### Issue: 500 Internal Server Error
**Solution:** Check Flask terminal for Python traceback

### Issue: Timeouts or slow loading
**Solution:** The optimizations are working! Just need to wait for first load

## Emergency Rollback

If nothing works, restore the backup files:

```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"

# Restore from backup (if you have one)
cp static/js/main.js.backup static/js/main.js
cp app.py.backup app.py
cp core/data/excel_processor.py.backup core/data/excel_processor.py
cp core/data/product_database.py.backup core/data/product_database.py

# Restart server
pkill -f "python3 app.py"
python3 app.py
```

## Contact Information

If you continue having issues, please provide:
1. Screenshot of browser console errors
2. Flask terminal output
3. What symptoms you're seeing (blank page, error message, etc.)

---

**Most Common Fix:** Hard refresh (Ctrl+Shift+R) + Clear cache
