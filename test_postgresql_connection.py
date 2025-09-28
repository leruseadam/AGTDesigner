#!/usr/bin/env python3
"""
PostgreSQL Connection Test
Tests connection to your PostgreSQL database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    
    print("🧪 Testing PostgreSQL Connection...")
    print("=" * 40)
    
    # Update these with your actual connection details
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'labelmaker'),
        'user': os.getenv('DB_USER', 'labelmaker'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Port: {config['port']}")
    print()
    
    try:
        # Test connection
        conn = psycopg2.connect(**config)
        print("✅ Connection successful!")
        
        # Test query
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version['version']}")
        
        # Test database info
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()
        print(f"✅ Connected to database: {db_name['current_database']}")
        
        # Test table creation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Table creation test passed")
        
        # Test insert
        cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("test",))
        conn.commit()
        print("✅ Insert test passed")
        
        # Test select
        cursor.execute("SELECT * FROM test_table")
        results = cursor.fetchall()
        print(f"✅ Select test passed: {len(results)} rows")
        
        # Clean up
        cursor.execute("DROP TABLE test_table")
        conn.commit()
        print("✅ Cleanup test passed")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 All PostgreSQL tests passed!")
        print("✅ Your database is ready for migration")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Check your connection details:")
        print("   • Host: Is the server running?")
        print("   • Database: Does it exist?")
        print("   • User: Does the user exist?")
        print("   • Password: Is it correct?")
        print("   • Port: Is it open?")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🐘 PostgreSQL Connection Test")
    print("=" * 30)
    
    # Check if psycopg2 is installed
    try:
        import psycopg2
        print("✅ PostgreSQL client available")
    except ImportError:
        print("❌ PostgreSQL client not available")
        print("💡 Install with: pip install psycopg2-binary")
        exit(1)
    
    # Run test
    success = test_postgresql_connection()
    
    if success:
        print("\n🚀 Ready to migrate your data!")
        print("Run: python migrate_to_postgresql_agt.py")
    else:
        print("\n🔧 Fix connection issues first")
        print("Then run this test again")
