#!/usr/bin/env python3

import sys
import os
sys.path.append('.')
from app import process_file_chunked
import threading
import time

print("=== Testing Simple Upload ===")

# Test with a simple file
filename = "test_export.xlsx"
filepath = "uploads/test_export.xlsx"

print(f"File exists: {os.path.exists(filepath)}")

# Start background processing
print("Starting background processing...")
thread = threading.Thread(target=process_file_chunked, args=(filename, filepath))
thread.daemon = True
thread.start()

print("Background thread started, waiting...")

# Wait and check status
for i in range(15):
    time.sleep(1)
    print(f"Waiting... {i+1}/15")
    
    # Check if thread is still alive
    if not thread.is_alive():
        print("Thread finished!")
        break

print("Test completed")
