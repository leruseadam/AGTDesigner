#!/usr/bin/env python3
"""
Auto Upload Web Interface Launcher

This script starts the auto-upload web interface and opens it in your default browser.
"""

import subprocess
import time
import webbrowser
import sys
import os

def main():
    print("🚀 Starting Auto Upload Web Interface...")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        'auto_upload_web_interface.py',
        'enhanced_auto_upload_noninteractive.py',
        'templates/auto_upload.html'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files found")
    
    try:
        # Start the web interface in the background
        print("🌐 Starting web server on port 5002...")
        process = subprocess.Popen([
            sys.executable, 'auto_upload_web_interface.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if server is running
        try:
            import requests
            response = requests.get('http://localhost:5002', timeout=5)
            if response.status_code == 200:
                print("✅ Web server is running!")
            else:
                print("⚠️  Server responded with unexpected status code")
        except Exception as e:
            print(f"⚠️  Could not verify server status: {e}")
        
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:5002')
        
        print("\n🎉 Auto Upload Web Interface is ready!")
        print("📱 Open your browser to: http://localhost:5002")
        print("🔄 Auto-upload will trigger automatically when you visit the page")
        print("\n💡 Press Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 