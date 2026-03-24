#!/usr/bin/env python3
import subprocess
import sys
import os

# Cross-platform launcher — uses the same Python that's running this script
subprocess.run([sys.executable, 'app.py'])
