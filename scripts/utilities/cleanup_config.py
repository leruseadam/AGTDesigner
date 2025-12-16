# Large Data Cleanup Configuration
# Adjust these settings to control data retention

# Database Backup Settings
DATABASE_BACKUP_RETENTION_DAYS = 3  # Keep database backups for 3 days
DATABASE_BACKUP_MAX_COUNT = 3       # Maximum number of database backups
DATABASE_BACKUP_INTERVAL_HOURS = 2  # Create backup every 2 hours

# Emergency Backup Settings  
EMERGENCY_BACKUP_RETENTION_DAYS = 1  # Keep emergency backups for 1 day
EMERGENCY_BACKUP_MAX_COUNT = 2       # Maximum number of emergency backups

# Temporary File Settings
TEMP_FILE_RETENTION_HOURS = 0       # Remove temp files immediately
SQLITE_TEMP_FILES_RETENTION_HOURS = 0  # Remove SQLite temp files immediately

# Archive File Settings
ZIP_FILE_RETENTION_DAYS = 7         # Keep zip files for 7 days
LARGE_ZIP_RETENTION_DAYS = 3        # Keep large zip files (>50MB) for 3 days

# Corrupted File Settings
CORRUPTED_BACKUP_RETENTION_HOURS = 0  # Remove corrupted backups immediately

# Disk Usage Monitoring
DISK_USAGE_WARNING_THRESHOLD = 80   # Warn when disk usage > 80%
DISK_USAGE_CRITICAL_THRESHOLD = 90  # Critical when disk usage > 90%

# Cleanup Schedule
CLEANUP_SCHEDULE_HOUR = 2           # Run cleanup at 2 AM daily
CLEANUP_SCHEDULE_MINUTE = 0         # Run cleanup at 2:00 AM

# File Size Limits
LARGE_FILE_THRESHOLD_MB = 50        # Files larger than 50MB are considered "large"
MAX_SINGLE_FILE_SIZE_MB = 500       # Files larger than 500MB trigger immediate cleanup

# Logging Settings
CLEANUP_LOG_RETENTION_DAYS = 30     # Keep cleanup logs for 30 days
VERBOSE_CLEANUP_LOGGING = True      # Enable detailed cleanup logging
