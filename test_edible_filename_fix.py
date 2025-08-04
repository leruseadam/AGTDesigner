#!/usr/bin/env python3
"""
Test script to verify that edibles use brand instead of lineage in filename generation.
"""

import requests
import json
import time

def test_edible_filename():
    """Test that edibles use brand instead of lineage in filename."""
    base_url = 'http://127.0.0.1:9090'
    
    print("🧪 Testing Edible Filename Generation")
    print("=" * 50)
    
    # Step 1: Get available tags
    print("\n1. Getting available tags...")
    
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            available_tags = response.json()
            print(f"✅ Got {len(available_tags)} available tags")
        else:
            print(f"❌ Failed to get available tags: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting available tags: {e}")
        return
    
    # Step 2: Find edible products
    print("\n2. Finding edible products...")
    
    edible_products = []
    for tag in available_tags:
        product_type = tag.get('Product Type*', '').lower()
        if 'edible' in product_type or product_type in ['tincture', 'topical', 'capsule']:
            edible_products.append(tag)
    
    print(f"✅ Found {len(edible_products)} edible products")
    
    if not edible_products:
        print("❌ No edible products found to test")
        return
    
    # Step 3: Select some edible products
    print("\n3. Selecting edible products for testing...")
    
    # Take first 5 edible products
    selected_edibles = edible_products[:5]
    selected_names = [tag['Product Name*'] for tag in selected_edibles]
    
    print(f"✅ Selected {len(selected_edibles)} edible products:")
    for name in selected_names:
        print(f"   - {name}")
    
    # Step 4: Generate labels and check filename
    print("\n4. Generating labels to check filename...")
    
    try:
        generate_data = {
            'selected_tags': selected_names,
            'template_type': 'horizontal'
        }
        
        response = requests.post(f'{base_url}/api/generate', json=generate_data)
        
        if response.status_code == 200:
            # Check the Content-Disposition header for filename
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"✅ Generation successful")
            print(f"📄 Content-Disposition: {content_disposition}")
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_start = content_disposition.find('filename=') + 9
                filename_end = content_disposition.find(';', filename_start)
                if filename_end == -1:
                    filename_end = len(content_disposition)
                filename = content_disposition[filename_start:filename_end].strip('"')
                
                print(f"📄 Generated filename: {filename}")
                
                # Check if filename contains brand instead of lineage
                if '_MIX_' in filename:
                    print("❌ Filename still contains lineage (MIX) instead of brand")
                    return False
                else:
                    print("✅ Filename appears to use brand instead of lineage")
                    return True
            else:
                print("❌ Could not extract filename from response")
                return False
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

def test_non_edible_filename():
    """Test that non-edibles still use lineage in filename."""
    base_url = 'http://127.0.0.1:9090'
    
    print("\n🧪 Testing Non-Edible Filename Generation")
    print("=" * 50)
    
    # Step 1: Get available tags
    print("\n1. Getting available tags...")
    
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            available_tags = response.json()
            print(f"✅ Got {len(available_tags)} available tags")
        else:
            print(f"❌ Failed to get available tags: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting available tags: {e}")
        return
    
    # Step 2: Find non-edible products
    print("\n2. Finding non-edible products...")
    
    non_edible_products = []
    for tag in available_tags:
        product_type = tag.get('Product Type*', '').lower()
        if 'edible' not in product_type and product_type not in ['tincture', 'topical', 'capsule']:
            non_edible_products.append(tag)
    
    print(f"✅ Found {len(non_edible_products)} non-edible products")
    
    if not non_edible_products:
        print("❌ No non-edible products found to test")
        return
    
    # Step 3: Select some non-edible products
    print("\n3. Selecting non-edible products for testing...")
    
    # Take first 5 non-edible products
    selected_non_edibles = non_edible_products[:5]
    selected_names = [tag['Product Name*'] for tag in selected_non_edibles]
    
    print(f"✅ Selected {len(selected_non_edibles)} non-edible products:")
    for name in selected_names:
        print(f"   - {name}")
    
    # Step 4: Generate labels and check filename
    print("\n4. Generating labels to check filename...")
    
    try:
        generate_data = {
            'selected_tags': selected_names,
            'template_type': 'horizontal'
        }
        
        response = requests.post(f'{base_url}/api/generate', json=generate_data)
        
        if response.status_code == 200:
            # Check the Content-Disposition header for filename
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"✅ Generation successful")
            print(f"📄 Content-Disposition: {content_disposition}")
            
            # Extract filename from Content-Disposition
            if 'filename=' in content_disposition:
                filename_start = content_disposition.find('filename=') + 9
                filename_end = content_disposition.find(';', filename_start)
                if filename_end == -1:
                    filename_end = len(content_disposition)
                filename = content_disposition[filename_start:filename_end].strip('"')
                
                print(f"📄 Generated filename: {filename}")
                
                # Check if filename contains lineage (should for non-edibles)
                if '_MIX_' in filename or '_S_' in filename or '_I_' in filename or '_H_' in filename:
                    print("✅ Filename correctly contains lineage for non-edibles")
                    return True
                else:
                    print("❌ Filename missing lineage for non-edibles")
                    return False
            else:
                print("❌ Could not extract filename from response")
                return False
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

if __name__ == "__main__":
    print("Testing Edible vs Non-Edible Filename Generation")
    print("=" * 60)
    
    # Test edible filename
    edible_result = test_edible_filename()
    
    # Test non-edible filename
    non_edible_result = test_non_edible_filename()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if edible_result and non_edible_result:
        print("✅ SUCCESS: Edibles use brand, non-edibles use lineage")
    elif edible_result:
        print("⚠️  PARTIAL: Edibles work, but non-edibles may have issues")
    elif non_edible_result:
        print("⚠️  PARTIAL: Non-edibles work, but edibles may have issues")
    else:
        print("❌ FAILED: Both edible and non-edible filename generation have issues") 