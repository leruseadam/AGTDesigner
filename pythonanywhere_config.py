# PythonAnywhere Emergency Configuration
# This configuration disables all features that can cause disk quota issues

import os

# Check if running on PythonAnywhere
IS_PYTHONANYWHERE = os.environ.get('PYTHONANYWHERE_DOMAIN') is not None

if IS_PYTHONANYWHERE:
    print("🐍 PythonAnywhere detected - enabling emergency mode")
    
    # Database settings - DISABLED FOR PYTHONANYWHERE
    ENABLE_AUTOMATIC_BACKUPS = False
    ENABLE_RELIABILITY_FEATURES = False
    ENABLE_VECTORIZED_OPERATIONS = False
    ENABLE_BATCH_OPERATIONS = False
    
    # Backup settings - DISABLED FOR PYTHONANYWHERE
    DATABASE_BACKUP_INTERVAL_HOURS = 999999  # Effectively disable
    DATABASE_BACKUP_RETENTION_DAYS = 0      # Keep no backups
    MAX_BACKUPS = 0                         # No backups
    
    # Performance settings - OPTIMIZED FOR PYTHONANYWHERE
    MAX_CONNECTIONS = 2                     # Limit connections
    BATCH_SIZE = 10                         # Small batch size
    BACKUP_INTERVAL_WRITES = 999999        # Effectively disable
    
    # Journal mode for PythonAnywhere
    JOURNAL_MODE = "DELETE"                 # Use DELETE mode for PythonAnywhere
    
    # Disable all logging to files
    ENABLE_FILE_LOGGING = False
    
    # Disable temporary file creation
    ENABLE_TEMP_FILES = False
    
    print("✅ PythonAnywhere emergency mode enabled")
    print("   - Automatic backups: DISABLED")
    print("   - Reliability features: DISABLED") 
    print("   - File logging: DISABLED")
    print("   - Max connections: 2")
    print("   - Journal mode: DELETE")
    
else:
    print("🖥️  Local development detected - using normal configuration")
    
    # Normal configuration for local development
    ENABLE_AUTOMATIC_BACKUPS = True
    ENABLE_RELIABILITY_FEATURES = True
    ENABLE_VECTORIZED_OPERATIONS = True
    ENABLE_BATCH_OPERATIONS = True
    
    DATABASE_BACKUP_INTERVAL_HOURS = 7200  # 2 hours
    DATABASE_BACKUP_RETENTION_DAYS = 3     # 3 days
    MAX_BACKUPS = 3                        # 3 backups
    
    MAX_CONNECTIONS = 5
    BATCH_SIZE = 50
    BACKUP_INTERVAL_WRITES = 200
    
    JOURNAL_MODE = "WAL"
    ENABLE_FILE_LOGGING = True
    ENABLE_TEMP_FILES = True
