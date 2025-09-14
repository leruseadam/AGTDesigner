#!/usr/bin/env python3
"""
Comprehensive PythonAnywhere Database Diagnosis
This script helps identify exactly why the database is still showing 0
"""

def main():
    print("🔍 PYTHONANYWHERE DATABASE DIAGNOSIS")
    print("=" * 50)
    print()
    print("The website is still showing 0. Let's diagnose step by step:")
    print()
    
    print("1️⃣ CHECK DATABASE FILE STATUS")
    print("   Run these commands on PythonAnywhere:")
    print("   ls -lh product_database.db")
    print("   file product_database.db")
    print("   sqlite3 product_database.db 'SELECT COUNT(*) FROM products;'")
    print()
    
    print("2️⃣ CHECK APP.PY FILE")
    print("   Run these commands on PythonAnywhere:")
    print("   ls -lh app.py")
    print("   head -20 app.py")
    print("   grep -n 'product_database.db' app.py")
    print()
    
    print("3️⃣ CHECK WEB APP STATUS")
    print("   Run these commands on PythonAnywhere:")
    print("   ps aux | grep python")
    print("   curl -s http://localhost:5000/api/database-stats")
    print()
    
    print("4️⃣ CHECK WEB APP LOGS")
    print("   - Go to PythonAnywhere Web tab")
    print("   - Click on your web app")
    print("   - Check 'Error log' for database errors")
    print()
    
    print("5️⃣ FORCE COMPLETE RESTART")
    print("   - Stop the web app completely")
    print("   - Wait 10 seconds")
    print("   - Start it again")
    print("   - Wait 30 seconds")
    print()
    
    print("6️⃣ ALTERNATIVE: CREATE NEW DATABASE")
    print("   If the database is still corrupted:")
    print("   sqlite3 product_database_new.db < /dev/null")
    print("   # Then we'll need to recreate the database")
    print()
    
    print("🚨 MOST LIKELY ISSUES:")
    print("=" * 25)
    print("1. Database file is still corrupted")
    print("2. Web app wasn't restarted after upload")
    print("3. App.py is looking for database in wrong location")
    print("4. PythonAnywhere file permissions issue")
    print("5. Web app configuration pointing to wrong directory")
    print()
    
    print("📞 IMMEDIATE ACTIONS:")
    print("=" * 20)
    print("1. Run the diagnostic commands above")
    print("2. Check web app logs for errors")
    print("3. Force restart the web app")
    print("4. If still not working, we may need to recreate the database")
    print()
    
    print("Please run the commands and share the output!")

if __name__ == "__main__":
    main()
