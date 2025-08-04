#!/usr/bin/env python3
"""
Comprehensive Lineage Persistence Test
Tests all aspects of the lineage database persistence system.
"""

import sys
import os
import sqlite3
import time
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and basic functionality."""
    print("=== Testing Database Connection ===")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        print("✅ Database connection successful")
        return db
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_lineage_persistence_flag():
    """Test that lineage persistence is always enabled."""
    print("\n=== Testing Lineage Persistence Flag ===")
    try:
        from src.core.data.excel_processor import ENABLE_LINEAGE_PERSISTENCE
        if ENABLE_LINEAGE_PERSISTENCE:
            print("✅ Lineage persistence is enabled")
            return True
        else:
            print("❌ Lineage persistence is disabled")
            return False
    except Exception as e:
        print(f"❌ Error checking lineage persistence flag: {e}")
        return False

def test_database_structure():
    """Test database table structure."""
    print("\n=== Testing Database Structure ===")
    try:
        conn = sqlite3.connect('product_database.db')
        cursor = conn.cursor()
        
        # Check if required tables exist
        tables = ['strains', 'products', 'lineage_history', 'strain_brand_lineage']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
                return False
        
        # Check if required columns exist in strains table
        cursor.execute("PRAGMA table_info(strains)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['strain_name', 'canonical_lineage', 'sovereign_lineage']
        for col in required_columns:
            if col in columns:
                print(f"✅ Column '{col}' exists in strains table")
            else:
                print(f"❌ Column '{col}' missing from strains table")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error testing database structure: {e}")
        return False

def test_lineage_data_integrity():
    """Test lineage data integrity."""
    print("\n=== Testing Lineage Data Integrity ===")
    try:
        conn = sqlite3.connect('product_database.db')
        cursor = conn.cursor()
        
        # Check for strains with both canonical and sovereign lineage
        cursor.execute("""
            SELECT COUNT(*) FROM strains 
            WHERE canonical_lineage IS NOT NULL 
            AND canonical_lineage != '' 
            AND sovereign_lineage IS NOT NULL 
            AND sovereign_lineage != ''
        """)
        count = cursor.fetchone()[0]
        print(f"✅ {count} strains have both canonical and sovereign lineage")
        
        # Check for strains with only canonical lineage
        cursor.execute("""
            SELECT COUNT(*) FROM strains 
            WHERE canonical_lineage IS NOT NULL 
            AND canonical_lineage != '' 
            AND (sovereign_lineage IS NULL OR sovereign_lineage = '')
        """)
        count = cursor.fetchone()[0]
        print(f"✅ {count} strains have only canonical lineage")
        
        # Check for strains with only sovereign lineage
        cursor.execute("""
            SELECT COUNT(*) FROM strains 
            WHERE sovereign_lineage IS NOT NULL 
            AND sovereign_lineage != '' 
            AND (canonical_lineage IS NULL OR canonical_lineage = '')
        """)
        count = cursor.fetchone()[0]
        print(f"✅ {count} strains have only sovereign lineage")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error testing lineage data integrity: {e}")
        return False

def test_recent_activity():
    """Test recent lineage activity."""
    print("\n=== Testing Recent Activity ===")
    try:
        conn = sqlite3.connect('product_database.db')
        cursor = conn.cursor()
        
        # Check recent lineage changes
        cursor.execute("""
            SELECT COUNT(*) FROM lineage_history 
            WHERE change_date >= datetime('now', '-24 hours')
        """)
        recent_changes = cursor.fetchone()[0]
        print(f"✅ {recent_changes} lineage changes in last 24 hours")
        
        # Check recent strain updates
        cursor.execute("""
            SELECT COUNT(*) FROM strains 
            WHERE updated_at >= datetime('now', '-24 hours')
        """)
        recent_updates = cursor.fetchone()[0]
        print(f"✅ {recent_updates} strain updates in last 24 hours")
        
        # Check for any strains with conflicting lineage
        cursor.execute("""
            SELECT COUNT(*) FROM strains 
            WHERE canonical_lineage != sovereign_lineage 
            AND canonical_lineage IS NOT NULL 
            AND sovereign_lineage IS NOT NULL 
            AND canonical_lineage != '' 
            AND sovereign_lineage != ''
        """)
        conflicts = cursor.fetchone()[0]
        if conflicts == 0:
            print("✅ No lineage conflicts detected")
        else:
            print(f"⚠️  {conflicts} strains have conflicting canonical vs sovereign lineage")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error testing recent activity: {e}")
        return False

def test_lineage_persistence_functionality():
    """Test the lineage persistence functionality."""
    print("\n=== Testing Lineage Persistence Functionality ===")
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create a test processor
        processor = ExcelProcessor()
        
        # Test the ensure_lineage_persistence method
        result = processor.ensure_lineage_persistence()
        
        if isinstance(result, dict) and 'message' in result:
            print(f"✅ Lineage persistence method works: {result['message']}")
            return True
        else:
            print(f"❌ Unexpected result from lineage persistence: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing lineage persistence functionality: {e}")
        return False

def test_database_notifier():
    """Test database notifier functionality."""
    print("\n=== Testing Database Notifier ===")
    try:
        from src.core.data.database_notifier import get_database_notifier
        
        notifier = get_database_notifier()
        if notifier:
            print("✅ Database notifier initialized successfully")
            return True
        else:
            print("❌ Database notifier initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database notifier: {e}")
        return False

def test_session_manager():
    """Test session manager functionality."""
    print("\n=== Testing Session Manager ===")
    try:
        from src.core.data.session_manager import get_session_manager
        
        manager = get_session_manager()
        if manager:
            print("✅ Session manager initialized successfully")
            
            # Test session stats
            stats = manager.get_session_stats()
            if isinstance(stats, dict):
                print(f"✅ Session stats available: {stats.get('active_sessions', 0)} active sessions")
                return True
            else:
                print("❌ Session stats not available")
                return False
        else:
            print("❌ Session manager initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session manager: {e}")
        return False

def main():
    """Run all lineage persistence tests."""
    print("🧪 Starting Comprehensive Lineage Persistence Tests")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Lineage Persistence Flag", test_lineage_persistence_flag),
        ("Database Structure", test_database_structure),
        ("Lineage Data Integrity", test_lineage_data_integrity),
        ("Recent Activity", test_recent_activity),
        ("Lineage Persistence Functionality", test_lineage_persistence_functionality),
        ("Database Notifier", test_database_notifier),
        ("Session Manager", test_session_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Lineage persistence system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the lineage persistence implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 