# Database Migration Guide

This guide explains how to replace the web version database with your local database containing 7,870 products.

## Overview

Your local database (250MB) compresses to 25MB (90% reduction), making it feasible to upload via the web interface.

## Prerequisites

1. Local database with 7,870 products at `uploads/product_database.db`
2. Web application running with the new import API endpoints
3. Python environment with required packages

## Method 1: Chunked Upload (Recommended)

### Step 1: Deploy Updated Web App
First, push the updated app.py with the new import endpoints to your web server:

```bash
git add app.py
git commit -m "Add database import/export API endpoints for migration"
git push origin main
```

### Step 2: Run the Upload Tool
Use the chunked upload tool to transfer your database:

```bash
python database_upload_tool.py uploads/product_database.db https://your-app.pythonanywhere.com
```

This will:
- Compress your 250MB database to 25MB
- Split it into 3 chunks of ~10MB each
- Upload each chunk via API
- Reconstruct the database on the web server

## Method 2: API-Based Migration

If you prefer to migrate data via API calls:

```bash
python database_migration_tool.py uploads/product_database.db https://your-app.pythonanywhere.com
```

This will:
- Export all products and strains from local database
- Clear the web database
- Import strains first, then products
- Verify the migration was successful

## Method 3: Direct File Transfer (If you have SSH access)

If you have SSH access to your web server:

```bash
# Compress the database
gzip -c uploads/product_database.db > product_database.db.gz

# Upload via SCP (replace with your server details)
scp product_database.db.gz username@your-server:/path/to/your/app/uploads/

# SSH into server and decompress
ssh username@your-server
cd /path/to/your/app/uploads/
gunzip product_database.db.gz
mv product_database.db product_database.db
```

## Verification

After migration, verify the database was replaced successfully:

1. Check the web app's database stats: `https://your-app.pythonanywhere.com/api/database-stats`
2. Look for 7,870 products and 934 strains
3. Test uploading a new Excel file to ensure it works

## Troubleshooting

### If upload fails:
- Check web server logs for errors
- Ensure the web app is running the updated version
- Try the API-based migration method instead

### If database appears empty:
- Check if the migration completed successfully
- Look for error messages in the web server logs
- Try the direct file transfer method

### If performance is slow:
- The web server may need time to process the large database
- Check server resources and memory usage
- Consider restarting the web application

## Files Created

- `database_upload_tool.py` - Chunked upload tool
- `database_migration_tool.py` - API-based migration tool
- `test_compression.py` - Test compression ratio
- Updated `app.py` with import/export API endpoints

## API Endpoints Added

- `POST /api/clear-database` - Clear the database
- `POST /api/import-strains` - Import strains
- `POST /api/import-products` - Import products
- `POST /api/upload-database-chunk` - Upload database chunks

## Success Criteria

After successful migration:
- Web database shows 7,870 products
- Web database shows 934 strains
- File uploads work normally
- No duplicate column warnings
- Fast upload performance
