#!/usr/bin/env python3
"""
Reliable App Startup Script
This script ensures the Flask app starts reliably by handling port conflicts
"""

import subprocess
import sys
import time
import os

def kill_port(port):
    """Kill processes on a specific port with retry logic"""
    print(f"🔍 Checking port {port}...")
    
    try:
        # Find processes using the port
        result = subprocess.run(f"lsof -ti tcp:{port}", shell=True, capture_output=True, text=True)
        pids = [pid.strip() for pid in result.stdout.strip().splitlines() if pid.strip()]
        
        if not pids:
            print(f"✅ Port {port} is already free")
            return True
        
        print(f"⚠️  Found processes on port {port}: {pids}")
        print("🔄 Killing processes...")
        
        # Kill processes with retry logic
        for attempt in range(3):
            subprocess.run(f"kill -9 {' '.join(pids)}", shell=True)
            time.sleep(1)
            
            # Check if still running
            result = subprocess.run(f"lsof -ti tcp:{port}", shell=True, capture_output=True, text=True)
            remaining = [pid.strip() for pid in result.stdout.strip().splitlines() if pid.strip()]
            
            if not remaining:
                print(f"✅ Successfully freed port {port}")
                return True
            else:
                print(f"⚠️  Attempt {attempt + 1}: Still processes on port {port}")
        
        print(f"❌ Could not fully free port {port}")
        return False
        
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False

def main():
    print("🚀 Starting AGT Label Maker Application...")
    
    # Try to free port 8001
    if kill_port(8001):
        print("🎯 Starting app on port 8001...")
        os.system("python app.py")
    else:
        print("🔄 Port 8001 busy, trying port 8002...")
        if kill_port(8002):
            print("🎯 Starting app on port 8002...")
            os.environ['FLASK_PORT'] = '8002'
            os.system("python app.py")
        else:
            print("❌ Both ports 8001 and 8002 are busy")
            print("Please manually kill processes and try again:")
            print("  lsof -i :8001")
            print("  lsof -i :8002")
            print("  kill -9 <PID>")
            sys.exit(1)

if __name__ == "__main__":
    main()
