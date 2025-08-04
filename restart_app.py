#!/usr/bin/env python3
"""
Restart App Script
Kills any existing Flask processes and starts fresh
"""

import os
import sys
import subprocess
import signal
import time

def kill_flask_processes():
    """Kill any existing Flask processes."""
    
    print("🔧 Killing any existing Flask processes...")
    
    try:
        # Kill processes on port 5001
        subprocess.run(['pkill', '-f', 'python.*app.py'], check=False)
        subprocess.run(['pkill', '-f', 'flask'], check=False)
        
        # Wait a moment for processes to terminate
        time.sleep(2)
        
        print("✅ Killed existing Flask processes")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not kill processes: {e}")
        return False

def start_app():
    """Start the app on port 5002."""
    
    print("🚀 Starting Label Maker App on port 5002...")
    
    # Set environment variables
    os.environ['FLASK_PORT'] = '5002'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # Import and run the app
        from app import LabelMakerApp
        
        label_maker = LabelMakerApp()
        label_maker.run()
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False

if __name__ == "__main__":
    # Kill existing processes
    kill_flask_processes()
    
    # Start the app
    start_app() 