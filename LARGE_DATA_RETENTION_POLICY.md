# Large Data Retention Policy

## Problem
Large data files (database backups, zip archives, temporary files) were accumulating and causing disk quota issues on PythonAnywhere.

## Solution: Automatic Cleanup Policy

### 1. Database Backups
- **Auto backups**: Keep only last 3 days
- **Emergency backups**: Keep only last 1 day  
- **Corrupted backups**: Remove immediately

### 2. Temporary Files
- **SQLite files** (.db-shm, .db-wal, .db-journal): Remove immediately
- **Old corrupted backups**: Remove immediately

### 3. Archive Files
- **Zip files**: Keep for 7 days maximum
- **Large zip files** (>50MB): Keep for 3 days maximum

### 4. Implementation
- **Automatic cleanup script**: `cleanup_large_files.py`
- **Run daily**: Via cron job or manual execution
- **Disk monitoring**: Alert when usage > 80%

## Usage

### Manual Cleanup
```bash
python cleanup_large_files.py
```

### Automatic Cleanup (Cron Job)
Add to crontab for daily cleanup at 2 AM:
```bash
0 2 * * * cd /path/to/project && python cleanup_large_files.py
```

## Benefits
- ✅ **Prevents disk quota exceeded errors**
- ✅ **Maintains optimal disk usage**
- ✅ **Keeps only necessary recent backups**
- ✅ **Automatically removes temporary files**
- ✅ **Configurable retention periods**

## Configuration
Edit `cleanup_large_files.py` to adjust retention periods:
- `max_age_days`: Number of days to keep files
- `pattern`: File pattern to match
- `description`: Human-readable description

## Monitoring
The script provides:
- **Disk usage before/after**
- **Files removed count**
- **Space freed in MB**
- **Detailed cleanup log**

This ensures the project stays within PythonAnywhere's disk limits while maintaining necessary backups.
