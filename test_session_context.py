#!/usr/bin/env python3
"""
Test script to verify session ExcelProcessor works within Flask context.
"""

from app import app, get_session_excel_processor

def test_session_excel_processor():
    """Test session ExcelProcessor within Flask application context."""
    print("Testing session ExcelProcessor with Flask context...")
    
    with app.app_context():
        try:
            session_proc = get_session_excel_processor()
            print(f"Session processor: {session_proc is not None}")
            print(f"Has df: {hasattr(session_proc, 'df')}")
            print(f"df is None: {session_proc.df is None}")
            print(f"Has selected_tags: {hasattr(session_proc, 'selected_tags')}")
            print("✅ Session ExcelProcessor test passed!")
            return True
        except Exception as e:
            print(f"❌ Session ExcelProcessor test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_session_excel_processor() 