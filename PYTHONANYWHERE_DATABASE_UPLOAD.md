# PythonAnywhere Database Upload Guide

This guide explains how to upload your large database files to PythonAnywhere using zip compression.

## Quick Start (Recommended Method)

### Step 1: Create Zip File Locally

```bash
# Run the zip creation script
python3 create_database_zip.py
```

This will create a file named `database_backup_YYYYMMDD_HHMMSS.zip` in your project directory.

### Step 2: Upload to PythonAnywhere

**Option A: Web Interface (Easiest)**

1. Go to https://www.pythonanywhere.com and log in
2. Click on the **Files** tab
3. Navigate to your project directory (e.g., `/home/yourusername/your-project/`)
4. Click the **Upload a file** button
5. Select your `database_backup_*.zip` file
6. Wait for upload to complete

**Option B: Command Line (Faster for large files)**

```bash
# From your local machine
scp database_backup_*.zip yourusername@ssh.pythonanywhere.com:~/your-project/
```

### Step 3: Extract on PythonAnywhere

1. Open a **Bash console** on PythonAnywhere (Console tab → Bash)
2. Navigate to your project:
   ```bash
   cd ~/your-project/
   ```

3. **Option A: Use the Python script (recommended)**
   ```bash
   # Upload unzip_on_pythonanywhere.py first, then run:
   python3 unzip_on_pythonanywhere.py
   ```

4. **Option B: Manual unzip**
   ```bash
   unzip database_backup_*.zip
   ```

5. Verify extraction:
   ```bash
   ls -lh uploads/
   ls -lh uploads/*.db
   ```

6. Clean up (optional):
   ```bash
   rm database_backup_*.zip
   ```

---

## Alternative Methods

### Method 2: Direct Upload via rsync (Best for updates)

If you need to sync database updates regularly:

```bash
# First time setup - create .pyanywhererc with your credentials
rsync -avz --progress \
  uploads/*.db* \
  yourusername@ssh.pythonanywhere.com:~/your-project/uploads/
```

### Method 3: Git LFS (For version control)

If your database should be version controlled:

```bash
# Install Git LFS
git lfs install

# Track database files
git lfs track "uploads/*.db"
git lfs track "uploads/*.db-shm"
git lfs track "uploads/*.db-wal"

# Commit and push
git add .gitattributes
git add uploads/
git commit -m "Add database files with LFS"
git push

# On PythonAnywhere
git lfs pull
```

### Method 4: Using PythonAnywhere API (Automated)

For automated uploads, use the PythonAnywhere API:

```python
import requests

api_token = 'your_api_token'
username = 'yourusername'

# Upload file
with open('database_backup.zip', 'rb') as f:
    response = requests.post(
        f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path/home/{username}/your-project/database_backup.zip',
        files={'content': f},
        headers={'Authorization': f'Token {api_token}'}
    )
```

---

## Important Notes

### SQLite Database Considerations

Your SQLite databases have three files:
- `.db` - Main database file
- `.db-shm` - Shared memory file (can be deleted before upload)
- `.db-wal` - Write-ahead log file (can be deleted before upload)

**Before zipping, consider closing the database properly:**

```python
# In your app or a script:
import sqlite3

# Close all connections
conn = sqlite3.connect('uploads/product_database.db')
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.close()
```

This will merge the WAL file back into the main database, reducing upload size.

### File Size Limits

- **PythonAnywhere Free**: 512 MB disk space total
- **PythonAnywhere Paid**: Check your plan limits
- **Web upload limit**: ~100 MB (use SCP/rsync for larger files)

### Compression Tips

The zip script uses `ZIP_DEFLATED` for maximum compression. SQLite databases typically compress well (30-50% reduction).

---

## Troubleshooting

### Upload Fails or Times Out

Try splitting into multiple zip files:

```python
# Modify create_database_zip.py to create separate archives
# Archive 1: Just the main databases
# Archive 2: Excel files and other data
```

### Database Locked Error on PythonAnywhere

Make sure to:
1. Stop your web app before extracting
2. Close all database connections
3. Restart web app after extraction

### Permission Issues

After extracting, set correct permissions:

```bash
chmod 644 uploads/*.db
chmod 755 uploads/
```

### Verify Database Integrity

After upload and extraction:

```bash
# On PythonAnywhere
python3 << EOF
import sqlite3
conn = sqlite3.connect('uploads/product_database.db')
conn.execute('PRAGMA integrity_check')
print('Database OK!')
conn.close()
EOF
```

---

## Automation Script for Regular Updates

Create a script for regular database syncs:

```bash
#!/bin/bash
# sync_database.sh

echo "Creating database backup..."
python3 create_database_zip.py

echo "Uploading to PythonAnywhere..."
scp database_backup_*.zip yourusername@ssh.pythonanywhere.com:~/your-project/

echo "Extracting on server..."
ssh yourusername@ssh.pythonanywhere.com << 'EOF'
cd ~/your-project
python3 unzip_on_pythonanywhere.py
rm database_backup_*.zip
EOF

echo "Cleaning up local zip..."
rm database_backup_*.zip

echo "✓ Database sync complete!"
```

---

## Security Considerations

1. **Never commit database files to public Git repos**
2. **Use environment variables for sensitive data**
3. **Backup before uploading** (PythonAnywhere doesn't auto-backup free tier)
4. **Use HTTPS only** when accessing PythonAnywhere
5. **Rotate API tokens regularly** if using API method

---

## Need Help?

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Support: help@pythonanywhere.com

