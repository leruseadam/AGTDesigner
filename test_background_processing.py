#!/usr/bin/env python3

import sys
import os
sys.path.append('.')
from app import process_file_chunked
import threading
import time

print("=== Testing Background Processing ===")

# Test with a simple file
filename = "test_export.xlsx"
filepath = "uploads/test_export.xlsx"

print(f"Starting background processing for {filename}")
print(f"File exists: {os.path.exists(filepath)}")

# Start background processing
thread = threading.Thread(target=process_file_chunked, args=(filename, filepath))
thread.daemon = True
thread.start()

print("Background thread started, waiting...")

# Wait and check status
for i in range(10):
    time.sleep(1)
    print(f"Waiting... {i+1}/10")
    
    # Check if thread is still alive
    if not thread.is_alive():
        print("Thread finished!")
        break

print("Test completed")
