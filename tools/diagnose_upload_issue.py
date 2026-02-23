#!/usr/bin/env python3
"""
Diagnostic tool to check upload and session state
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_upload_folder():
    """Check if upload folder exists and what files are in it"""
    from app import app

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    print(f"\n📁 Upload folder: {upload_folder}")
    print(f"   Absolute path: {os.path.abspath(upload_folder)}")
    print(f"   Exists: {os.path.exists(upload_folder)}")

    if os.path.exists(upload_folder):
        files = os.listdir(upload_folder)
        print(f"   Files: {len(files)}")
        for f in sorted(files)[-10:]:  # Show last 10 files
            full_path = os.path.join(upload_folder, f)
            size = os.path.getsize(full_path)
            print(f"     - {f} ({size:,} bytes)")
    else:
        print("   ⚠️  Upload folder does not exist!")

def check_excel_processor():
    """Check global Excel processor state"""
    from app import _excel_processor

    print(f"\n📊 Excel Processor:")
    print(f"   Instance: {_excel_processor}")

    if _excel_processor:
        has_df = hasattr(_excel_processor, 'df') and _excel_processor.df is not None
        print(f"   Has DataFrame: {has_df}")
        if has_df:
            print(f"   Rows: {len(_excel_processor.df)}")
            print(f"   Columns: {list(_excel_processor.df.columns)[:5]}...")

        if hasattr(_excel_processor, '_last_loaded_file'):
            print(f"   Last loaded file: {_excel_processor._last_loaded_file}")
            if _excel_processor._last_loaded_file:
                exists = os.path.exists(_excel_processor._last_loaded_file)
                print(f"   File exists: {exists}")
    else:
        print("   ⚠️  No Excel processor initialized!")

def check_session_config():
    """Check Flask session configuration"""
    from app import app

    print(f"\n🔧 Session Configuration:")
    print(f"   SESSION_TYPE: {app.config.get('SESSION_TYPE', 'not set')}")
    print(f"   SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT', 'not set')}")
    print(f"   SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER', 'not set')}")
    print(f"   SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE', 'not set')}")
    print(f"   SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE', 'not set')}")
    print(f"   SECRET_KEY: {'set' if app.config.get('SECRET_KEY') else 'NOT SET ⚠️'}")

def simulate_available_tags_check():
    """Simulate what /api/available-tags does to check for Excel data"""
    from app import app
    from flask import session

    print(f"\n🔍 Simulating /api/available-tags logic:")

    # Create app context
    with app.test_request_context():
        session_file_path = session.get('file_path', '')
        print(f"   session['file_path']: {session_file_path or '(empty)'}")

        if session_file_path:
            file_exists = os.path.exists(session_file_path)
            print(f"   File exists on disk: {file_exists}")
            has_excel_data = file_exists and session_file_path
            print(f"   has_excel_data: {has_excel_data}")
        else:
            print(f"   ⚠️  No file_path in session!")
            print(f"   This will cause 'No Excel file uploaded' message")

if __name__ == '__main__':
    print("=" * 60)
    print("UPLOAD DIAGNOSTIC TOOL")
    print("=" * 60)

    try:
        check_upload_folder()
        check_excel_processor()
        check_session_config()
        simulate_available_tags_check()

        print("\n" + "=" * 60)
        print("DIAGNOSIS COMPLETE")
        print("=" * 60)

        print("\n💡 Common Issues:")
        print("   1. Upload folder doesn't exist → create it")
        print("   2. File uploaded but session not maintained → check SECRET_KEY")
        print("   3. Background processing not complete → file not in processor yet")
        print("   4. Session file_path points to deleted file → clear session")

    except Exception as e:
        print(f"\n❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
