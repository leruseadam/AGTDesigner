#!/usr/bin/env python3
"""
Production runner for Label Maker application.
This script runs the app in production mode without hot reloading.
"""

import os
import sys
import logging

# Set production environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Configure logging for production
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the application in production mode."""
    try:
        # Temporarily set development mode to False
        import config
        original_dev_mode = config.Config.DEVELOPMENT_MODE
        config.Config.DEVELOPMENT_MODE = False
        
        # Import and run the app
        from app import LabelMakerApp
        
        print("🚀 Starting Label Maker in PRODUCTION mode...")
        print("⚡ Optimized for performance")
        print("🔒 Debug mode disabled")
        print("📦 Static file caching enabled")
        print("-" * 50)
        
        app = LabelMakerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Production server stopped by user")
    except Exception as e:
        print(f"❌ Error starting production server: {e}")
        sys.exit(1)
    finally:
        # Restore original development mode setting
        if 'config' in locals():
            config.Config.DEVELOPMENT_MODE = original_dev_mode

if __name__ == '__main__':
    main() 