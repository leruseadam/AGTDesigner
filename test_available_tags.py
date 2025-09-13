#!/usr/bin/env python3

import requests
import json

print("=== Testing Available Tags API ===")

# Test the available-tags endpoint
try:
    response = requests.get("http://localhost:5002/api/available-tags")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test the initial-data endpoint for comparison
try:
    response = requests.get("http://localhost:5002/api/initial-data")
    print(f"\nInitial data status code: {response.status_code}")
    data = response.json()
    print(f"Initial data success: {data.get('success', False)}")
    print(f"Initial data count: {data.get('total_count', 0)}")
except Exception as e:
    print(f"Initial data error: {e}")
