#!/usr/bin/env python3
"""
Simple startup script for the Label Maker app.
This script disables startup file loading to prevent hanging during initialization.
"""

import os
import sys

def main():
    print("🚀 Starting Label Maker App...")
    print("📝 Disabling startup file loading for faster startup...")
    
    # Set environment variable to disable startup file loading
    os.environ['DISABLE_STARTUP_FILE_LOADING'] = 'true'
    
    # Import and run the app
    try:
        from app import LabelMakerApp
        app = LabelMakerApp()
        
        print("✅ App initialized successfully!")
        print("🌐 Starting server on http://localhost:5001")
        print("📁 Note: You'll need to upload a file after the app starts")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 