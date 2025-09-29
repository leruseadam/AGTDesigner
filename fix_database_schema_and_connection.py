#!/usr/bin/env python3
"""
Fix Database Schema and Connection Issues
Adds missing columns and ensures correct PostgreSQL connection
"""

import os
import sys
import psycopg2
from psycopg2 import sql

def set_environment_variables():
    """Set environment variables like the WSGI file does"""
    
    print("🔧 Setting Environment Variables...")
    print("=" * 40)
    
    # Set the environment variables (same as WSGI file)
    os.environ['DB_HOST'] = 'adamcordova-4822.postgres.pythonanywhere-services.com'
    os.environ['DB_NAME'] = 'postgres'
    os.environ['DB_USER'] = 'super'
    os.environ['DB_PASSWORD'] = '193154life'
    os.environ['DB_PORT'] = '14822'
    
    print("✅ Environment variables set")

def fix_database_schema():
    """Fix database schema by adding missing columns"""
    
    print("\n🔧 Fixing Database Schema...")
    print("=" * 35)
    
    # Database connection parameters
    db_config = {
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD'],
        'port': os.environ['DB_PORT']
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Check current table structure
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            ORDER BY column_name
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"📋 Current products table has {len(existing_columns)} columns")
        
        # Required columns that might be missing
        required_columns = [
            'Product Name*',
            'Product Brand',
            'Vendor/Supplier*',
            'Product Type*',
            'Description',
            'Weight*',
            'Units',
            'Price',
            'Quantity*',
            'Product Strain',
            'Lineage',
            'THC test result',
            'CBD test result',
            'Room*',
            'State',
            'DOH',
            'first_seen_date',
            'last_seen_date',
            'normalized_name'
        ]
        
        missing_columns = []
        for column in required_columns:
            if column not in existing_columns:
                missing_columns.append(column)
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            print("🔧 Adding missing columns...")
            
            for column in missing_columns:
                try:
                    # Add column with appropriate data type
                    if column in ['Product Name*', 'Product Brand', 'Vendor/Supplier*', 'Product Type*', 'Description', 'Product Strain', 'Lineage', 'Room*', 'State', 'normalized_name']:
                        cur.execute(f'ALTER TABLE products ADD COLUMN "{column}" TEXT')
                    elif column in ['Weight*', 'Price', 'Quantity*', 'THC test result', 'CBD test result']:
                        cur.execute(f'ALTER TABLE products ADD COLUMN "{column}" NUMERIC')
                    elif column in ['Units', 'DOH']:
                        cur.execute(f'ALTER TABLE products ADD COLUMN "{column}" TEXT')
                    elif column in ['first_seen_date', 'last_seen_date']:
                        cur.execute(f'ALTER TABLE products ADD COLUMN "{column}" TIMESTAMP')
                    else:
                        cur.execute(f'ALTER TABLE products ADD COLUMN "{column}" TEXT')
                    
                    print(f"✅ Added column: {column}")
                except Exception as e:
                    print(f"❌ Error adding column {column}: {e}")
        else:
            print("✅ All required columns exist")
        
        # Check for other potential issues
        print("\n🔍 Checking for other potential issues...")
        
        # Test basic queries
        cur.execute("SELECT COUNT(*) FROM products;")
        product_count = cur.fetchone()[0]
        print(f"📊 Total products in database: {product_count}")
        
        cur.execute("SELECT COUNT(*) FROM strains;")
        strain_count = cur.fetchone()[0]
        print(f"🌿 Total strains in database: {strain_count}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Database schema check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        return False

def test_database_connection():
    """Test database connection with correct configuration"""
    
    print("\n🔗 Testing Database Connection...")
    print("=" * 35)
    
    try:
        import psycopg2
        from src.core.data.product_database import get_database_config
        
        config = get_database_config()
        
        # Check if it's using the correct host
        if config['host'] == 'localhost':
            print("❌ Database config is still using localhost")
            print("💡 Environment variables may not be loaded in the app")
            return False
        elif 'pythonanywhere' in config['host']:
            print("✅ Database config is using PythonAnywhere PostgreSQL")
        else:
            print(f"⚠️ Database host is: {config['host']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        
        print(f"✅ Database connection successful!")
        print(f"📊 Found {count} products in database")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_app_functionality():
    """Test app functionality with fixed database"""
    
    print("\n🧪 Testing App Functionality...")
    print("=" * 35)
    
    try:
        sys.path.insert(0, os.getcwd())
        from app import app
        
        print("✅ App imported successfully")
        
        if hasattr(app, 'route'):
            print("✅ App is a valid Flask application")
            
            # Test database stats endpoint
            with app.test_client() as client:
                try:
                    response = client.get('/api/database-stats')
                    print(f"✅ App responds to database-stats (status: {response.status_code})")
                    
                    if response.status_code == 200:
                        data = response.get_json()
                        if 'total_products' in data and data['total_products'] > 0:
                            print(f"📊 Database stats show: {data['total_products']} products")
                            return True
                        else:
                            print("⚠️ Database stats show 0 products")
                            return False
                    else:
                        print(f"⚠️ Database stats returned status {response.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"❌ App doesn't respond to database-stats: {e}")
                    return False
        else:
            print("❌ App is not a valid Flask application")
            return False
            
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("🚀 Fix Database Schema and Connection Issues")
    print("=" * 50)
    
    # Set environment variables
    set_environment_variables()
    
    # Fix database schema
    schema_ok = fix_database_schema()
    
    # Test database connection
    connection_ok = test_database_connection()
    
    # Test app functionality
    app_ok = test_app_functionality()
    
    print("\n📊 Fix Summary:")
    print("=" * 20)
    print(f"Database Schema: {'✅' if schema_ok else '❌'}")
    print(f"Database Connection: {'✅' if connection_ok else '❌'}")
    print(f"App Functionality: {'✅' if app_ok else '❌'}")
    
    print("\n💡 Next Steps:")
    if schema_ok and connection_ok and app_ok:
        print("🎉 Database issues fixed!")
        print("1. Go to PythonAnywhere Web tab")
        print("2. Click Reload button")
        print("3. Wait 60 seconds")
        print("4. Refresh your web app")
        print("5. Database should now show real data!")
    else:
        print("⚠️ Some issues remain")
        if not schema_ok:
            print("- Database schema issues")
        if not connection_ok:
            print("- Database connection issues")
        if not app_ok:
            print("- App functionality issues")

if __name__ == "__main__":
    main()
