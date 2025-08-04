#!/usr/bin/env python3
"""
Development runner for Label Maker application.
This script ensures the app runs in development mode with hot reloading enabled.
"""

import os
import sys
import logging

# Set development environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Configure logging for development
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the application in development mode."""
    try:
        # Import and run the app
        from app import LabelMakerApp
        
        print("🚀 Starting Label Maker in DEVELOPMENT mode...")
        print("📝 Hot reloading enabled - changes will auto-refresh")
        print("🔧 Debug mode enabled")
        print("📁 Watching for file changes...")
        print("-" * 50)
        
        app = LabelMakerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Development server stopped by user")
    except Exception as e:
        print(f"❌ Error starting development server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 