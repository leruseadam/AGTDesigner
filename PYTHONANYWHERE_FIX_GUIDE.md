# PythonAnywhere Deployment Fix Guide

## The Problem
The web app was trying to connect to `localhost:5432` instead of the PythonAnywhere PostgreSQL database, causing "Connection refused" errors.

## The Solution

### 1. Updated WSGI File
I've created `wsgi_pythonanywhere_python311_fixed.py` with the following improvements:

- ✅ **Environment variables set FIRST** - Before any imports
- ✅ **Database connection test** - Verifies connection before app import
- ✅ **Better error handling** - Graceful fallback if database test fails
- ✅ **Debug output** - Shows environment variables for troubleshooting

### 2. Deployment Steps

#### Option A: Manual Upload (Recommended)
1. **Upload the fixed WSGI file:**
   - Go to PythonAnywhere Files tab
   - Navigate to `/var/www/www_agtpricetags_com_wsgi.py`
   - Replace the content with `wsgi_pythonanywhere_python311_fixed.py`

2. **Reload your web app:**
   - Go to PythonAnywhere Web tab
   - Click "Reload" button

#### Option B: Using PythonAnywhere Console
1. **Open PythonAnywhere Console**
2. **Run these commands:**
   ```bash
   cd /home/adamcordova/AGTDesigner
   cp wsgi_pythonanywhere_python311_fixed.py /var/www/www_agtpricetags_com_wsgi.py
   ```
3. **Reload your web app**

### 3. Verification

After deployment, check the error logs:
- Go to PythonAnywhere Web tab
- Click "Error log" link
- Look for these messages:
  - ✅ `DB_HOST: adamcordova-4822.postgres.pythonanywhere-services.com`
  - ✅ `Database connection successful! Products: XXXX`
  - ✅ `WSGI application loaded successfully`

### 4. Troubleshooting

If you still see connection errors:

1. **Check database credentials:**
   - Verify the PostgreSQL database is running
   - Confirm the credentials are correct
   - Check if the database has the `products` table

2. **Check environment variables:**
   - The error log should show the environment variables
   - If they show "NOT SET", the WSGI file wasn't updated properly

3. **Test database connection manually:**
   ```python
   import psycopg2
   conn = psycopg2.connect(
       host='adamcordova-4822.postgres.pythonanywhere-services.com',
       database='postgres',
       user='super',
       password='193154life',
       port='14822'
   )
   ```

### 5. Local Development

For local development, use:
```bash
python run_local.py
```

This will:
- Set local database environment variables
- Start the app on `http://localhost:5000`
- Use your local PostgreSQL database

## Expected Results

After deployment:
- ✅ No more "Connection refused" errors
- ✅ Database operations work correctly
- ✅ App loads without database connection issues
- ✅ Product database integration functions properly

## Files Created

1. `wsgi_pythonanywhere_python311_fixed.py` - Fixed WSGI file
2. `run_local.py` - Local development runner
3. `test_web_deployment.py` - Web deployment tester
4. `copy_wsgi_to_pythonanywhere.py` - WSGI file copier (for local testing)