# EMERGENCY PYTHONANYWHERE RECOVERY PLAN

## Critical Issues Detected
1. **Database corruption**: "Database integrity check failed: row 1 missing from index sqlite_autoindex_strains_1"
2. **Disk quota exceeded**: "[Errno 122] Disk quota exceeded"
3. **High CPU usage**: 80-100% CPU usage
4. **Database locks**: Continuous "database is locked" errors
5. **Empty database files**: "Database file is empty"

## Immediate Actions Required

### 1. Disable Automatic Backups (CRITICAL)
The system is trying to create backups but hitting disk quota limits, causing more corruption.

### 2. Emergency Cleanup
Remove all large files immediately to free up disk space.

### 3. Minimal Database Mode
Switch to a minimal database configuration that doesn't create large backups.

### 4. Database Recreation
Create a fresh, minimal database without corruption.

## Recovery Steps

### Step 1: Emergency Cleanup
```bash
# Remove all corrupted database files
rm -f uploads/product_database_AGT_Bothell.db.corrupted.*
rm -f uploads/backups/*
rm -f uploads/*.db-shm uploads/*.db-wal uploads/*.db-journal

# Remove large zip files
rm -f *.zip
rm -f uploads/*.zip

# Check disk usage
du -sh .
```

### Step 2: Disable Automatic Backups
Modify the database configuration to disable automatic backups completely.

### Step 3: Create Minimal Database
Create a new, minimal database with essential tables only.

### Step 4: Restart Application
Restart the Flask application with the new minimal database.

## Prevention Measures
1. **No automatic backups** on PythonAnywhere
2. **Minimal database schema** with only essential tables
3. **Aggressive cleanup** of temporary files
4. **Disk usage monitoring** with automatic cleanup

## Files to Modify
- `src/core/data/product_database.py` - Disable backups
- `src/core/data/database_reliability.py` - Disable reliability features
- `app.py` - Add emergency mode detection

## Expected Results
- ✅ No more disk quota exceeded errors
- ✅ No more database corruption
- ✅ Reduced CPU usage
- ✅ Functional application with minimal database
