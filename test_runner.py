#!/usr/bin/env python3
"""
Test file to verify different ways of running Python code in VS Code.
"""

import sys
import os

def main():
    print("=== Python Runner Test ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
    print(f"Workspace folder: {os.path.basename(os.getcwd())}")
    print("=== Test completed successfully! ===")

if __name__ == "__main__":
    main() 