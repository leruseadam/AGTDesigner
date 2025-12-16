#!/usr/bin/env python3
"""
Test script to verify Flask context fixes for get_client_ip, get_current_store_name, and get_excel_processor.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_outside_context():
    """Test functions when called outside Flask request/application context."""
    print("=" * 60)
    print("Testing functions OUTSIDE Flask context")
    print("=" * 60)
    
    # Import the functions
    from app import get_client_ip, get_current_store_name, get_excel_processor
    
    # Test get_client_ip outside context
    print("\n1. Testing get_client_ip() outside context...")
    try:
        result = get_client_ip()
        assert result is None, f"Expected None, got {result}"
        print("   ✅ get_client_ip() correctly returns None outside context")
    except Exception as e:
        print(f"   ❌ get_client_ip() failed: {e}")
        return False
    
    # Test get_current_store_name outside context (with fallback)
    print("\n2. Testing get_current_store_name(allow_fallback=True) outside context...")
    try:
        result = get_current_store_name(allow_fallback=True)
        assert result == 'AGT_Bothell', f"Expected 'AGT_Bothell', got {result}"
        print(f"   ✅ get_current_store_name() correctly returns fallback: {result}")
    except Exception as e:
        print(f"   ❌ get_current_store_name() with fallback failed: {e}")
        return False
    
    # Test get_current_store_name outside context (without fallback)
    print("\n3. Testing get_current_store_name(allow_fallback=False) outside context...")
    try:
        result = get_current_store_name(allow_fallback=False)
        assert result is None, f"Expected None, got {result}"
        print("   ✅ get_current_store_name() correctly returns None without fallback")
    except Exception as e:
        print(f"   ❌ get_current_store_name() without fallback failed: {e}")
        return False
    
    # Test get_excel_processor outside context
    print("\n4. Testing get_excel_processor() outside context...")
    try:
        result = get_excel_processor()
        # Should not crash, but may return None or a processor
        print(f"   ✅ get_excel_processor() completed without error (returned: {type(result).__name__})")
    except Exception as e:
        print(f"   ❌ get_excel_processor() failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_inside_context():
    """Test functions when called inside Flask application context."""
    print("\n" + "=" * 60)
    print("Testing functions INSIDE Flask context")
    print("=" * 60)
    
    from app import app, get_client_ip, get_current_store_name, get_excel_processor
    
    with app.app_context():
        print("\n1. Testing get_client_ip() inside application context (no request)...")
        try:
            result = get_client_ip()
            # Should return None since there's no request context
            assert result is None, f"Expected None (no request context), got {result}"
            print("   ✅ get_client_ip() correctly returns None (no request context)")
        except Exception as e:
            print(f"   ❌ get_client_ip() failed: {e}")
            return False
        
        print("\n2. Testing get_current_store_name() inside application context...")
        try:
            result = get_current_store_name(allow_fallback=True)
            # Should return fallback since there's no request context
            assert result == 'AGT_Bothell', f"Expected 'AGT_Bothell', got {result}"
            print(f"   ✅ get_current_store_name() correctly returns fallback: {result}")
        except Exception as e:
            print(f"   ❌ get_current_store_name() failed: {e}")
            return False
        
        print("\n3. Testing get_excel_processor() inside application context...")
        try:
            result = get_excel_processor()
            print(f"   ✅ get_excel_processor() completed without error (returned: {type(result).__name__})")
        except Exception as e:
            print(f"   ❌ get_excel_processor() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("FLASK CONTEXT FIX TEST SUITE")
    print("=" * 60)
    
    success = True
    
    # Test outside context
    if not test_outside_context():
        success = False
    
    # Test inside context
    if not test_inside_context():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
