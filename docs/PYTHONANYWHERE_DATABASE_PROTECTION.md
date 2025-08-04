# 🛡️ PythonAnywhere Database Protection Guide

## Overview
This guide provides comprehensive strategies to keep your database safe from Git changes when deploying to PythonAnywhere.

## ✅ Current Protection (Already Active)

Your `.gitignore` file already includes excellent database protection:
```gitignore
# Database files
*.db
*.db-shm
*.db-wal
*.sqlite
*.sqlite3
```

**This means all SQLite database files are automatically excluded from Git tracking.**

## 🚀 Additional Protection Strategies

### 1. **Environment-Specific Database Paths**

Configure your database to use different paths for different environments:

```python
# In your database configuration
import os

def get_database_path():
    """Get database path based on environment."""
    if os.environ.get('PYTHONANYWHERE_SITE'):
        # PythonAnywhere: Use user's home directory
        return os.path.expanduser('~/databases/product_database.db')
    else:
        # Local development: Use project directory
        return 'product_database.db'
```

### 2. **Database Backup Strategy**

Create a backup system that runs before Git operations:

```bash
#!/bin/bash
# backup_database.sh
echo "Creating database backup before Git operations..."

# Create backup directory if it doesn't exist
mkdir -p ~/database_backups

# Backup current database with timestamp
cp ~/labelmaker/product_database.db ~/database_backups/product_database_$(date +%Y%m%d_%H%M%S).db

echo "Database backed up successfully!"
```

### 3. **Git Hooks for Database Protection**

Create a pre-commit hook to prevent accidental database commits:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Check if any database files are being committed
if git diff --cached --name-only | grep -E '\.(db|sqlite|sqlite3)$'; then
    echo "❌ ERROR: Database files detected in commit!"
    echo "Database files are protected and should not be committed."
    echo "Please remove database files from your commit."
    exit 1
fi

echo "✅ Database protection check passed"
exit 0
```

### 4. **PythonAnywhere-Specific Configuration**

Update your database configuration for PythonAnywhere:

```python
# config_pythonanywhere.py
import os

class PythonAnywhereConfig:
    # Database settings for PythonAnywhere
    DATABASE_PATH = os.path.expanduser('~/databases/product_database.db')
    DATABASE_BACKUP_PATH = os.path.expanduser('~/database_backups/')
    
    # Ensure database directory exists
    @staticmethod
    def ensure_database_directory():
        db_dir = os.path.dirname(PythonAnywhereConfig.DATABASE_PATH)
        os.makedirs(db_dir, exist_ok=True)
        return db_dir
```

### 5. **Deployment Scripts with Database Protection**

Create deployment scripts that handle database safety:

```bash
#!/bin/bash
# deploy_to_pythonanywhere.sh

echo "🚀 Deploying to PythonAnywhere with database protection..."

# Step 1: Backup existing database
echo "📦 Creating database backup..."
mkdir -p ~/database_backups
if [ -f ~/labelmaker/product_database.db ]; then
    cp ~/labelmaker/product_database.db ~/database_backups/product_database_backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ Database backed up"
else
    echo "ℹ️  No existing database found"
fi

# Step 2: Pull latest code (database files are ignored by .gitignore)
echo "📥 Pulling latest code..."
cd ~/labelmaker
git pull origin main

# Step 3: Restore database if needed
echo "🔄 Checking database status..."
if [ ! -f product_database.db ] && [ -f ~/database_backups/product_database_backup_*.db ]; then
    echo "📋 Restoring database from backup..."
    cp ~/database_backups/product_database_backup_*.db product_database.db
    echo "✅ Database restored"
fi

echo "🎉 Deployment complete with database protection!"
```

### 6. **Database Monitoring Script**

Create a script to monitor database integrity:

```python
#!/usr/bin/env python3
# monitor_database.py

import os
import sqlite3
import logging
from datetime import datetime

def check_database_integrity(db_path):
    """Check database integrity and create backup if needed."""
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == "ok":
            print(f"✅ Database integrity check passed: {db_path}")
            return True
        else:
            print(f"❌ Database integrity check failed: {result[0]}")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def create_database_backup(db_path):
    """Create a timestamped backup of the database."""
    if not os.path.exists(db_path):
        print(f"ℹ️  Database not found: {db_path}")
        return
    
    backup_dir = os.path.expanduser('~/database_backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'product_database_backup_{timestamp}.db')
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    db_path = os.path.expanduser('~/labelmaker/product_database.db')
    
    print("🔍 Checking database integrity...")
    if check_database_integrity(db_path):
        print("📦 Creating backup...")
        create_database_backup(db_path)
    else:
        print("⚠️  Database integrity check failed - manual intervention required")
```

## 🛠️ Implementation Steps

### 1. **Set Up Database Directory Structure**
```bash
# On PythonAnywhere
mkdir -p ~/databases
mkdir -p ~/database_backups
chmod 755 ~/databases ~/database_backups
```

### 2. **Update Database Configuration**
```python
# In your database initialization code
def get_database_path():
    if os.environ.get('PYTHONANYWHERE_SITE'):
        db_path = os.path.expanduser('~/databases/product_database.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return db_path
    return 'product_database.db'
```

### 3. **Create Protection Scripts**
```bash
# Make scripts executable
chmod +x backup_database.sh
chmod +x deploy_to_pythonanywhere.sh
chmod +x monitor_database.py
```

### 4. **Set Up Git Hooks**
```bash
# Make pre-commit hook executable
chmod +x .git/hooks/pre-commit
```

## 🔍 Verification Commands

### Check Current Database Protection
```bash
# Verify database files are ignored
git status --ignored | grep -E '\.(db|sqlite|sqlite3)$'

# Check if database files are tracked
git ls-files | grep -E '\.(db|sqlite|sqlite3)$'
```

### Test Database Integrity
```bash
# Run database integrity check
python3 monitor_database.py

# Check database size and location
ls -la ~/labelmaker/product_database.db
ls -la ~/databases/product_database.db
```

## 🚨 Emergency Recovery

If you accidentally commit a database file:

```bash
# Remove from Git tracking (but keep the file)
git rm --cached product_database.db

# Commit the removal
git commit -m "Remove database file from tracking"

# Push the change
git push origin main
```

## 📋 Best Practices Summary

1. **✅ Already Protected**: Your `.gitignore` excludes all database files
2. **🔄 Use Environment-Specific Paths**: Different paths for local vs PythonAnywhere
3. **📦 Regular Backups**: Automated backup system before deployments
4. **🔒 Git Hooks**: Prevent accidental database commits
5. **🔍 Monitoring**: Regular integrity checks and monitoring
6. **📚 Documentation**: Keep track of database locations and backup procedures

## 🎯 Benefits

- **Data Safety**: Database files are never accidentally committed
- **Environment Isolation**: Different database paths for different environments
- **Easy Recovery**: Automated backup and restore procedures
- **Deployment Safety**: Protected deployments with database preservation
- **Monitoring**: Proactive database health monitoring

Your database is now fully protected from Git changes while maintaining easy deployment and backup procedures! 