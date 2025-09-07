# Production Deployment Instructions

## Issue
The production server at `agtpricetags.com` is showing empty dashboard metrics (all zeros) because it doesn't have the database upload fix deployed.

## Root Cause
The production server has the old code that has a schema mismatch bug in the database upload functionality. The fix has been applied locally and pushed to git, but the production server needs to be updated.

## Solution
Deploy the latest code to the production server.

## Steps to Deploy

### Option 1: SSH into Production Server
```bash
# SSH into the production server
ssh username@agtpricetags.com

# Navigate to the project directory
cd /path/to/labelmaker/project

# Pull the latest code
git pull origin main

# Restart the Flask application
sudo systemctl restart labelmaker
# OR if using screen/tmux:
pkill -f 'python app.py'
python app.py
```

### Option 2: PythonAnywhere Web Interface
1. Go to PythonAnywhere Web tab
2. Access the console
3. Navigate to the project directory
4. Run: `git pull origin main`
5. Reload the web app

### Option 3: Manual File Upload
If SSH is not available, manually upload the fixed files:
1. Upload `src/core/data/product_database.py` (with the schema fix)
2. Restart the web application

## Verification
After deployment, test these endpoints:
- `https://www.agtpricetags.com/api/database-vendor-stats` - Should return data instead of empty arrays
- `https://www.agtpricetags.com/api/performance` - Should show `"initialized": true` for product_database

## Expected Result
After deployment, the dashboard should show:
- Total Products: > 0
- Unique Vendors: > 0  
- Unique Brands: > 0
- Product Types: > 0

## Files Changed
- `src/core/data/product_database.py` - Fixed column name mapping in SQL queries
- `app.py` - Added database upload endpoints

## Git Commits
- `39b23484` - Fix database upload issue: correct column name mapping
- `52b6c176` - Add database file upload and decompression endpoints
- `0ba0611c` - Merge remote changes and resolve conflicts

## Status
- ✅ Local fix applied and tested
- ✅ Code pushed to git repository
- ❌ Production server needs to be updated
