#!/usr/bin/env python3
"""
Web Database Recovery Script
============================
This script helps restore your web database when it has been reset or is empty.
"""

import os
import sqlite3
import shutil
from datetime import datetime

def check_database_status(db_path):
    """Check the status and content of a database"""
    if not os.path.exists(db_path):
        return {"exists": False, "products": 0, "size": 0}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get product count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        # Get file size
        file_size = os.path.getsize(db_path)
        
        conn.close()
        
        return {
            "exists": True, 
            "products": product_count, 
            "size": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2)
        }
    except Exception as e:
        return {"exists": True, "products": 0, "size": 0, "error": str(e)}

def backup_database(source_path, backup_dir="database_backups"):
    """Create a backup of the database"""
    if not os.path.exists(source_path):
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"product_database_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(source_path, backup_path)
    return backup_path

def restore_database_from_local():
    """Restore database from local copies"""
    print("🔍 Checking available local databases...")
    print("=" * 50)
    
    # Local database options
    local_databases = [
        "uploads/product_database_AGT_Bothell.db",
        "uploads/product_database.db", 
        "uploads/product_database_optimized.db",
        "uploads/product_database_pythonanywhere.db"
    ]
    
    best_database = None
    max_products = 0
    
    for db_path in local_databases:
        status = check_database_status(db_path)
        
        if status["exists"]:
            print(f"📁 {db_path}")
            print(f"   Products: {status['products']:,}")
            print(f"   Size: {status['size_mb']} MB")
            
            if status["products"] > max_products:
                max_products = status["products"]
                best_database = db_path
            
            if "error" in status:
                print(f"   ⚠️  Error: {status['error']}")
        else:
            print(f"❌ {db_path} - Not found")
        print()
    
    if best_database:
        print(f"🎯 Best database found: {best_database}")
        print(f"   Contains {max_products:,} products")
        return best_database, max_products
    else:
        print("❌ No valid databases found locally")
        return None, 0

def create_database_deployment_package():
    """Create a database package ready for web deployment"""
    print("📦 Creating database deployment package...")
    
    # Find the best local database
    best_db, product_count = restore_database_from_local()
    
    if not best_db:
        print("❌ No database available for deployment")
        return False
    
    # Create deployment directory
    deploy_dir = "web_database_restore"
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Copy the best database as the main database
    main_db_path = os.path.join(deploy_dir, "product_database_AGT_Bothell.db")
    shutil.copy2(best_db, main_db_path)
    
    print(f"✅ Copied {best_db} to {main_db_path}")
    print(f"✅ Database ready with {product_count:,} products")
    
    # Create deployment script
    deployment_script = f"""#!/bin/bash

# Web Database Restore Script
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🔄 Restoring AGT Label Maker Database"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from your AGT Label Maker directory"
    exit 1
fi

# Backup existing database if it exists
if [ -f "uploads/product_database_AGT_Bothell.db" ]; then
    echo "💾 Backing up existing database..."
    cp uploads/product_database_AGT_Bothell.db uploads/product_database_AGT_Bothell_backup_$(date +%Y%m%d_%H%M%S).db
fi

# Copy the restored database
echo "📥 Copying restored database..."
cp product_database_AGT_Bothell.db uploads/

# Verify the restoration
echo "🧪 Verifying database restoration..."
python3 -c "
import sqlite3
conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]
print(f'✅ Database restored with {{count:,}} products')
conn.close()
"

echo "🎉 Database restoration complete!"
echo "📋 You can now restart your web application"
"""
    
    script_path = os.path.join(deploy_dir, "restore_database.sh")
    with open(script_path, "w") as f:
        f.write(deployment_script)
    
    os.chmod(script_path, 0o755)
    
    # Create instructions
    instructions = f"""# Web Database Restore Instructions

## What Happened
Your web database was reset and is now empty or missing products.

## What's in This Package
- `product_database_AGT_Bothell.db` - Complete database with {product_count:,} products
- `restore_database.sh` - Automated restoration script
- `README.md` - These instructions

## Quick Restore (Choose One Method)

### Method 1: Upload Database File (Simplest)
1. Upload `product_database_AGT_Bothell.db` to your web server's `uploads/` directory
2. Restart your web application
3. Done! Your database is restored

### Method 2: Use Git (If using Git deployment)
1. Run this from your local repository:
   ```bash
   git add uploads/product_database_AGT_Bothell.db
   git commit -m "Restore database with {product_count:,} products"
   git push origin main
   ```
2. On your web server:
   ```bash
   git pull origin main
   ```
3. Restart your web application

### Method 3: Use the Restore Script
1. Upload both files to your web server
2. Run: `./restore_database.sh`
3. Restart your web application

## Verification
After restoration, your web app should show:
- {product_count:,} total products
- All product types (Flower, Concentrate, Edible, etc.)
- Concentrate products should show weights correctly

## Prevention
To prevent this in the future:
1. Regular database backups
2. Use Git to track database changes
3. Keep local copies as backup

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Database source: {best_db}
Products: {product_count:,}
"""
    
    readme_path = os.path.join(deploy_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(instructions)
    
    print(f"📋 Created deployment package in '{deploy_dir}/'")
    print(f"📄 Instructions in '{readme_path}'")
    
    return True

def main():
    """Main restoration workflow"""
    print("🚨 AGT Label Maker - Web Database Recovery")
    print("=" * 45)
    print()
    
    # Check current directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from your AGT Label Maker directory")
        return False
    
    print("🔍 Current situation analysis...")
    
    # Check web deployment database status
    web_db_path = "uploads/product_database_AGT_Bothell.db"
    web_status = check_database_status(web_db_path)
    
    print(f"📊 Web database status:")
    print(f"   Path: {web_db_path}")
    print(f"   Products: {web_status.get('products', 0):,}")
    print(f"   Size: {web_status.get('size_mb', 0)} MB")
    print()
    
    if web_status.get("products", 0) < 1000:  # Assume it should have more than 1000 products
        print("🚨 Web database appears to be empty or incomplete!")
        print("💡 Let's restore it from your local copies...")
        print()
        
        # Create restoration package
        if create_database_deployment_package():
            print()
            print("🎉 Database restoration package created successfully!")
            print("📁 Check the 'web_database_restore' directory for files to upload")
            print()
            print("📋 Quick next steps:")
            print("1. Upload 'product_database_AGT_Bothell.db' to your web server's uploads/ directory")
            print("2. Restart your web application")
            print("3. Verify that products are showing correctly")
            return True
        else:
            print("❌ Failed to create restoration package")
            return False
    else:
        print("✅ Web database appears to be working correctly")
        print("💡 If you're still having issues, the problem might be elsewhere")
        return True

if __name__ == "__main__":
    main()