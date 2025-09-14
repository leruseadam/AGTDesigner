#!/usr/bin/env python3
"""
Fix Live Database - Step by Step Instructions
The database is showing 0 because the web app needs to be restarted after file uploads
"""

def main():
    print("🚨 FIX LIVE DATABASE - STEP BY STEP")
    print("=" * 50)
    print()
    print("The database is showing 0 because the web app needs to be restarted.")
    print("Here are the EXACT steps to fix it:")
    print()
    
    print("1️⃣ LOG INTO PYTHONANYWHERE")
    print("   - Go to https://www.pythonanywhere.com")
    print("   - Log in with your credentials")
    print()
    
    print("2️⃣ RESTART THE WEB APP")
    print("   - Click on the 'Web' tab")
    print("   - Find your web app (should be agtpricetags.com)")
    print("   - Click the 'Reload' button")
    print("   - Wait 30 seconds for it to restart")
    print()
    
    print("3️⃣ VERIFY FILES ARE UPLOADED")
    print("   - Click on the 'Files' tab")
    print("   - Navigate to /home/adamcordova/AGTDesigner/")
    print("   - Check these files exist:")
    print("     ✅ app.py (should be ~509KB)")
    print("     ✅ product_database.db (should be ~250MB)")
    print("     ✅ core/data/product_database.py")
    print()
    
    print("4️⃣ CHECK WEB APP LOGS (if still not working)")
    print("   - Go back to 'Web' tab")
    print("   - Click on your web app")
    print("   - Click 'Error log' to see any errors")
    print("   - Look for database-related errors")
    print()
    
    print("5️⃣ TEST THE WEBSITE")
    print("   - Go to https://agtpricetags.com")
    print("   - Should now show:")
    print("     ✅ Total Products: 10,285 (instead of 0)")
    print("     ✅ Unique Vendors: 108 (instead of 0)")
    print("     ✅ Unique Brands: 170 (instead of 0)")
    print("     ✅ Product Types: 19 (instead of 0)")
    print()
    
    print("🔧 IF STILL NOT WORKING:")
    print("=" * 30)
    print("The most common issues are:")
    print("1. Web app not restarted after file upload")
    print("2. Wrong directory path in web app configuration")
    print("3. Database file permissions")
    print("4. PythonAnywhere web app configuration")
    print()
    
    print("📞 EMERGENCY FIX:")
    print("=" * 20)
    print("If restarting doesn't work:")
    print("1. Stop the web app completely")
    print("2. Wait 10 seconds")
    print("3. Start it again")
    print("4. Wait 30 seconds")
    print("5. Test the website")
    print()
    
    print("✅ The files are already uploaded - just need to restart!")

if __name__ == "__main__":
    main()
