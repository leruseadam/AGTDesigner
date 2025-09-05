#!/usr/bin/env python3
"""
Test script to verify JSON parsing and deduplication logic.
This script tests the raw JSON processing to see why only 27 items are processed instead of 40.
"""

import requests
import json
import re
from collections import defaultdict

def test_json_parsing():
    """Test the JSON parsing and deduplication logic."""
    
    # Test URL from the WCIA Transfer Schema
    test_url = "https://api-trace.getbamboo.com/shared/manifests/json/hbtAmylgpfg29trznzzxqt5zgzbs9vdfmv7v355npf3xcz5qjfkAksdznrywAy5yhfdxg56rlb3A576w4rA2q8rs3n829zkAjbfw45b5hjy2m5dpk15gkn6wpf1wkncqmnbvq8kkmrjvcpj8"
    
    print("🧪 Testing JSON Parsing and Deduplication")
    print("=" * 60)
    
    try:
        print(f"🔗 Fetching JSON from: {test_url}")
        
        # Fetch the JSON data
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(test_url, headers=headers, timeout=60)
        response.raise_for_status()
        payload = response.json()
        
        print("✅ JSON fetched successfully!")
        
        # Handle both list and dictionary payloads
        if isinstance(payload, list):
            items = payload
            global_vendor = ""
        elif isinstance(payload, dict):
            items = payload.get("inventory_transfer_items", [])
            global_vendor = payload.get("from_license_name", "")
            print(f"📋 Global vendor: {global_vendor}")
        else:
            print(f"❌ Unexpected payload type: {type(payload)}")
            return False
        
        print(f"📊 Raw JSON data:")
        print(f"   - Total items in JSON: {len(items)}")
        
        if not items:
            print("❌ No inventory transfer items found in JSON")
            return False
        
        # Show first few items for reference
        print(f"\n🏷️  Sample items:")
        for i, item in enumerate(items[:3]):
            if isinstance(item, dict):
                product_name = item.get("product_name", "Unknown")
                vendor = item.get("vendor", "Unknown")
                weight = item.get("unit_weight", "Unknown")
                strain = item.get("strain_name", "Unknown")
                inventory_type = item.get("inventory_type", "Unknown")
                print(f"   {i+1}. {product_name}")
                print(f"      Vendor: {vendor}, Weight: {weight}, Strain: {strain}, Type: {inventory_type}")
        
        # Test the deduplication logic
        print(f"\n🔍 Testing deduplication logic...")
        
        seen_items = set()
        unique_items = []
        duplicate_count = 0
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            # Create a more specific unique key that includes distinguishing attributes
            product_name = str(item.get("product_name", "")).strip().lower()
            vendor = global_vendor if global_vendor else str(item.get("vendor", "")).strip().lower()
            weight = str(item.get("unit_weight", "")).strip().lower()
            strain = str(item.get("strain_name", "")).strip().lower()
            inventory_type = str(item.get("inventory_type", "")).strip().lower()
            
            if not product_name:
                continue
                
            # Create a unique identifier that includes distinguishing attributes
            item_key = f"{product_name}|{vendor}|{weight}|{strain}|{inventory_type}"
            
            if item_key in seen_items:
                duplicate_count += 1
                print(f"   🔄 Duplicate item #{duplicate_count}: {product_name}")
                print(f"      Key: {item_key}")
                continue
                
            seen_items.add(item_key)
            unique_items.append(item)
        
        duplicate_percentage = (duplicate_count / len(items)) * 100 if len(items) > 0 else 0
        print(f"\n📊 Deduplication results:")
        print(f"   - Original items: {len(items)}")
        print(f"   - Unique items after deduplication: {len(unique_items)}")
        print(f"   - Duplicates removed: {duplicate_count} ({duplicate_percentage:.1f}%)")
        
        # Expected: 40 items from the WCIA Transfer Schema
        expected_count = 40
        if len(unique_items) == expected_count:
            print(f"🎉 SUCCESS: All {expected_count} items processed correctly!")
        else:
            print(f"⚠️  WARNING: Expected {expected_count} items, but got {len(unique_items)}")
            print(f"   - This explains why only {len(unique_items)} tags are generated")
            
            # Analyze what might be causing the reduction
            if duplicate_count > 0:
                print(f"   - {duplicate_count} items were considered duplicates and removed")
                print(f"   - The deduplication logic may be too aggressive")
                
                # Show some examples of what was considered duplicate
                print(f"\n🔍 Duplicate analysis:")
                duplicate_examples = []
                seen_keys = set()
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                        
                    product_name = str(item.get("product_name", "")).strip().lower()
                    vendor = global_vendor if global_vendor else str(item.get("vendor", ""), "").strip().lower()
                    weight = str(item.get("unit_weight", "")).strip().lower()
                    strain = str(item.get("strain_name", "")).strip().lower()
                    inventory_type = str(item.get("inventory_type", "")).strip().lower()
                    
                    if not product_name:
                        continue
                        
                    item_key = f"{product_name}|{vendor}|{weight}|{strain}|{inventory_type}"
                    
                    if item_key in seen_keys:
                        duplicate_examples.append({
                            'product_name': product_name,
                            'vendor': vendor,
                            'weight': weight,
                            'strain': strain,
                            'inventory_type': inventory_type,
                            'key': item_key
                        })
                    else:
                        seen_keys.add(item_key)
                
                if duplicate_examples:
                    print(f"   - Sample duplicates:")
                    for i, dup in enumerate(duplicate_examples[:5]):  # Show first 5
                        print(f"     {i+1}. {dup['product_name']}")
                        print(f"        Key: {dup['key']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_parsing()
    exit(0 if success else 1)
