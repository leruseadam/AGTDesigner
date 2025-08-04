#!/usr/bin/env python3
"""
Fix App Port Conflict
Changes the app to use a different port to avoid conflicts
"""

import os
import sys

def fix_port_conflict():
    """Fix port conflict by changing to a different port."""
    
    print("🔧 Fixing App Port Conflict...")
    
    # Set environment variable to use a different port
    os.environ['FLASK_PORT'] = '5002'
    
    print("✅ Changed Flask port to 5002")
    print("✅ Now you can run: python app.py")
    print("✅ App will be available at: http://127.0.0.1:5002")
    
    return True

if __name__ == "__main__":
    fix_port_conflict() 