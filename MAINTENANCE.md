# Label Maker Maintenance Guide

This guide helps you maintain and troubleshoot the Label Maker application.

## Quick Commands

### Check System Health
```bash
python monitor_system.py
```
This will check:
- Disk space
- Application status
- Running processes
- Large files

### Clean Up Disk Space
```bash
python cleanup_disk.py
```
This will:
- Truncate large log files
- Remove old upload files (keeps 10 most recent)
- Clean up temporary files
- Remove cache directories

### Restart Application
```bash
# Stop the application
pkill -f "python app.py"

# Start the application
python app.py
```

## Common Issues and Solutions

### 1. "Site Not Available" Error

**Cause:** Usually due to low disk space or application crash

**Solution:**
1. Run system monitor: `python monitor_system.py`
2. If disk space is low: `python cleanup_disk.py`
3. Restart application: `python app.py`

### 2. Database Export Not Working

**Cause:** Missing global variables or disk space issues

**Solution:**
1. Check if application is running: `python monitor_system.py`
2. If not running, restart: `python app.py`
3. Try the export again

### 3. Slow Performance

**Cause:** Large log files or too many upload files

**Solution:**
1. Run cleanup: `python cleanup_disk.py`
2. Check for large files: `python monitor_system.py`

## Disk Space Management

The application requires at least 2GB of free disk space to operate properly. When disk space gets low:

1. **Automatic Protection:** The application will automatically:
   - Check disk space before uploads
   - Perform emergency cleanup if needed
   - Prevent operations that could cause crashes

2. **Manual Cleanup:** Run `python cleanup_disk.py` to:
   - Clear large log files
   - Remove old upload files
   - Clean temporary files

## Monitoring

### Regular Checks
Run `python monitor_system.py` periodically to:
- Monitor disk space usage
- Verify application is running
- Check for large files
- Get recommendations

### Log Files
- `app.log` - Main application log
- `logs/label_maker.log` - Application-specific logs

## File Structure

```
labelMaker/
├── app.py              # Main application
├── cleanup_disk.py     # Disk cleanup utility
├── monitor_system.py   # System monitoring
├── uploads/            # Uploaded Excel files
├── logs/               # Log files
├── product_database.db # Product database
└── app.log            # Main log file
```

## Troubleshooting

### Application Won't Start
1. Check disk space: `df -h .`
2. Check for errors: `tail -50 app.log`
3. Restart: `python app.py`

### Upload Issues
1. Check disk space: `python monitor_system.py`
2. Verify file format (must be .xlsx)
3. Check file size (max 20MB)

### Database Issues
1. Check if database file exists: `ls -la *.db`
2. Restart application: `python app.py`
3. Try database export to test

## Performance Tips

1. **Regular Cleanup:** Run `python cleanup_disk.py` weekly
2. **Monitor Logs:** Keep log files under 1MB
3. **Limit Uploads:** Keep only recent upload files
4. **Check Disk Space:** Monitor regularly with `python monitor_system.py`

## Emergency Procedures

### If Application Crashes
1. Check disk space: `df -h .`
2. Clean up if needed: `python cleanup_disk.py`
3. Restart: `python app.py`
4. Verify: `python monitor_system.py`

### If Disk is Full
1. Run emergency cleanup: `python cleanup_disk.py`
2. Move large files to external storage
3. Delete unnecessary files
4. Restart application: `python app.py` 