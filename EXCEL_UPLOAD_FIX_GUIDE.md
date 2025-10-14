# 🔧 Excel Upload Reliability Fix

## The Problem
Excel files don't upload sometimes until you refresh multiple times. This is caused by:

1. **Database locks** from previous uploads
2. **Corrupted upload files** in the uploads directory
3. **Disk space issues** on PythonAnywhere
4. **File permission problems**
5. **Multiple upload endpoints** causing conflicts

## 🚀 Quick Fix

### Method 1: Run the Fix Script
```bash
ssh adamcordova@ssh.pythonanywhere.com
cd ~/AGTDesigner
python3 FIX_EXCEL_UPLOAD_RELIABILITY.py
```

### Method 2: Manual Fix
```bash
ssh adamcordova@ssh.pythonanywhere.com
cd ~/AGTDesigner

# 1. Remove database locks
rm -f uploads/product_database_AGT_Bothell.db-shm
rm -f uploads/product_database_AGT_Bothell.db-wal

# 2. Clean up old uploads
find uploads/ -name "*.xlsx" -mtime +1 -delete
find uploads/ -name "*.xls" -mtime +1 -delete

# 3. Remove corrupted backups
rm -f uploads/*corrupted*

# 4. Check disk space
df -h

# 5. Kill any stuck processes
pkill -f python
```

## 🔄 Reload Web App
After running the fix:
1. Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/
2. Click **"Reload"** for www.agtpricetags.com
3. Wait 30 seconds

## 🎯 Test Upload
1. Visit: https://www.agtpricetags.com
2. Try uploading an Excel file
3. Should work on first try now

## 🚨 If Still Having Issues

### Check Logs
```bash
tail -f /var/log/www.agtpricetags.com.error.log
```

### Common Error Messages
- **"database is locked"** → Run the fix script
- **"File too large"** → Check file size (should be under 200MB)
- **"No file uploaded"** → Browser cache issue, try incognito mode
- **"Upload failed"** → Disk space issue, run cleanup

### Alternative Upload Methods
If the main upload still fails:
1. **Try smaller Excel files** (under 50MB)
2. **Use incognito/private browsing**
3. **Clear browser cache** (Ctrl+F5)
4. **Try different browser**

## 🔍 Root Causes

### Database Lock Issues
- Previous uploads leave database locks
- Multiple upload attempts create conflicts
- PythonAnywhere has limited resources

### File System Issues
- Old Excel files accumulate in uploads/
- Corrupted files block new uploads
- Disk space fills up over time

### Browser Issues
- Cached upload states cause conflicts
- Multiple tabs trying to upload simultaneously
- Network timeouts on large files

## ✅ Prevention

### Regular Maintenance
```bash
# Run this weekly to prevent issues
cd ~/AGTDesigner
python3 FIX_EXCEL_UPLOAD_RELIABILITY.py
```

### Best Practices
1. **Close other tabs** before uploading
2. **Wait for upload to complete** before refreshing
3. **Use smaller Excel files** when possible
4. **Don't upload multiple files simultaneously**

## 🚀 Expected Results

After applying the fix:
- ✅ **Uploads work on first try**
- ✅ **No more refresh requirements**
- ✅ **Faster upload processing**
- ✅ **No database lock errors**
- ✅ **Cleaner uploads directory**

**Run the fix script to resolve upload reliability issues!** 📁
