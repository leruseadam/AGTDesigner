#!/usr/bin/env python3
"""
Single Instance App Starter
This script ensures only one instance of the Flask app runs at a time
"""

import os
import sys
import subprocess
import time
import signal

def kill_existing_processes():
    """Kill any existing Flask processes on common ports"""
    ports = [8001, 8002, 5000, 5001, 5002]
    
    for port in ports:
        try:
            # Find processes using the port
            result = subprocess.run(f"lsof -ti tcp:{port}", shell=True, capture_output=True, text=True)
            pids = [pid.strip() for pid in result.stdout.strip().splitlines() if pid.strip()]
            
            if pids:
                print(f"🔄 Killing existing processes on port {port}: {pids}")
                subprocess.run(f"kill -9 {' '.join(pids)}", shell=True)
                time.sleep(1)
        except Exception as e:
            print(f"⚠️  Error checking port {port}: {e}")

def main():
    print("🚀 Starting AGT Label Maker (Single Instance)")
    print("🛡️  Ensuring no multiple restarts...")
    
    # Kill any existing processes
    kill_existing_processes()
    
    # Set environment variables to prevent multiple restarts
    os.environ['DEVELOPMENT_MODE'] = 'false'  # Disable development mode
    os.environ['DISABLE_STARTUP_FILE_LOADING'] = '1'  # Speed up startup
    
    print("✅ Environment configured for single instance")
    print("🌐 Starting app on http://127.0.0.1:8001")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start the app
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
