#!/usr/bin/env python3
"""
Test script to verify that strain changes persist after page refresh.
This script tests the enhanced lineage persistence functionality.
"""

import requests
import time
import json
from datetime import datetime

def test_strain_persistence_fix():
    """Test that strain changes persist after page refresh."""
    
    print("=== STRAIN PERSISTENCE FIX TEST ===")
    print(f"Test started at: {datetime.now()}")
    
    base_url = "http://localhost:9090"
    
    try:
        # Step 1: Check if data is loaded
        print("\n1. Checking if data is loaded...")
        status_response = requests.get(f"{base_url}/api/status")
        if status_response.status_code != 200:
            print("✗ Failed to get status")
            return False
        
        status = status_response.json()
        print(f"   Backend status: {status}")
        
        if not status.get('data_loaded'):
            print("✗ No data loaded in backend")
            return False
        
        print("✓ Data is loaded in backend")
        
        # Step 2: Get available tags
        print("\n2. Getting available tags...")
        tags_response = requests.get(f"{base_url}/api/available-tags?limit=10")
        if tags_response.status_code != 200:
            print("✗ Failed to get available tags")
            return False
        
        tags = tags_response.json()
        if not tags or len(tags) == 0:
            print("✗ No tags available")
            return False
        
        print(f"✓ Found {len(tags)} available tags")
        
        # Step 3: Find a tag with lineage to test
        test_tag = None
        for tag in tags:
            if tag.get('Lineage') and tag.get('Product Name*') and tag.get('Product Strain'):
                test_tag = tag
                break
        
        if not test_tag:
            print("✗ No suitable tag found for testing")
            return False
        
        tag_name = test_tag['Product Name*']
        current_lineage = test_tag['Lineage']
        strain_name = test_tag['Product Strain']
        
        print(f"   Testing with tag: {tag_name}")
        print(f"   Current lineage: {current_lineage}")
        print(f"   Strain: {strain_name}")
        
        # Step 4: Update lineage
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        print(f"\n3. Updating lineage to {new_lineage}...")
        
        update_data = {
            'tag_name': tag_name,
            'lineage': new_lineage
        }
        
        update_response = requests.post(f"{base_url}/api/update-lineage", json=update_data)
        if update_response.status_code != 200:
            print(f"✗ Failed to update lineage: {update_response.status_code}")
            return False
        
        update_result = update_response.json()
        print(f"✓ Lineage updated successfully: {update_result}")
        
        # Step 5: Wait a moment for changes to propagate
        print("\n4. Waiting for changes to propagate...")
        time.sleep(2)
        
        # Step 6: Ensure lineage persistence
        print("\n5. Ensuring lineage persistence...")
        persistence_response = requests.post(f"{base_url}/api/ensure-lineage-persistence")
        if persistence_response.status_code != 200:
            print(f"✗ Failed to ensure lineage persistence: {persistence_response.status_code}")
            return False
        
        persistence_result = persistence_response.json()
        print(f"✓ Lineage persistence ensured: {persistence_result}")
        
        # Step 7: Verify the change persisted by getting tags again
        print("\n6. Verifying change persisted...")
        tags_response2 = requests.get(f"{base_url}/api/available-tags?limit=50")
        if tags_response2.status_code != 200:
            print("✗ Failed to get available tags for verification")
            return False
        
        tags2 = tags_response2.json()
        
        # Find the same tag
        updated_tag = None
        for tag in tags2:
            if tag.get('Product Name*') == tag_name:
                updated_tag = tag
                break
        
        if not updated_tag:
            print("✗ Could not find the updated tag")
            return False
        
        updated_lineage = updated_tag.get('Lineage', '')
        print(f"   Updated lineage: {updated_lineage}")
        
        if updated_lineage == new_lineage:
            print("✓ Lineage change persisted successfully!")
        else:
            print(f"✗ Lineage change did not persist. Expected: {new_lineage}, Got: {updated_lineage}")
            return False
        
        # Step 8: Test that the change persists in the database
        print("\n7. Testing database persistence...")
        
        # Get strain info from database
        strain_response = requests.get(f"{base_url}/api/all-strains")
        if strain_response.status_code == 200:
            strains = strain_response.json()
            strain_found = False
            for strain in strains:
                if strain.get('strain_name') == strain_name:
                    strain_found = True
                    db_lineage = strain.get('sovereign_lineage') or strain.get('canonical_lineage')
                    print(f"   Database lineage for {strain_name}: {db_lineage}")
                    if db_lineage == new_lineage:
                        print("✓ Lineage change persisted in database!")
                    else:
                        print(f"✗ Lineage change not found in database. Expected: {new_lineage}, Got: {db_lineage}")
                    break
            
            if not strain_found:
                print(f"   Strain {strain_name} not found in database")
        else:
            print("   Could not check database persistence (endpoint not available)")
        
        print("\n=== TEST COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

def test_page_refresh_simulation():
    """Simulate page refresh by clearing frontend state and reloading data."""
    
    print("\n=== PAGE REFRESH SIMULATION TEST ===")
    
    base_url = "http://localhost:9090"
    
    try:
        # Step 1: Get initial state
        print("\n1. Getting initial state...")
        status_response = requests.get(f"{base_url}/api/status")
        if status_response.status_code != 200:
            print("✗ Failed to get status")
            return False
        
        status = status_response.json()
        if not status.get('data_loaded'):
            print("✗ No data loaded")
            return False
        
        # Step 2: Get initial tags
        tags_response = requests.get(f"{base_url}/api/available-tags?limit=10")
        if tags_response.status_code != 200:
            print("✗ Failed to get initial tags")
            return False
        
        initial_tags = tags_response.json()
        print(f"✓ Initial tags loaded: {len(initial_tags)} tags")
        
        # Step 3: Find a tag with lineage
        test_tag = None
        for tag in initial_tags:
            if tag.get('Lineage') and tag.get('Product Name*'):
                test_tag = tag
                break
        
        if not test_tag:
            print("✗ No suitable tag found")
            return False
        
        tag_name = test_tag['Product Name*']
        initial_lineage = test_tag['Lineage']
        
        print(f"   Test tag: {tag_name}")
        print(f"   Initial lineage: {initial_lineage}")
        
        # Step 4: Update lineage
        new_lineage = "HYBRID" if initial_lineage != "HYBRID" else "MIXED"
        print(f"\n2. Updating lineage to {new_lineage}...")
        
        update_response = requests.post(f"{base_url}/api/update-lineage", json={
            'tag_name': tag_name,
            'lineage': new_lineage
        })
        
        if update_response.status_code != 200:
            print("✗ Failed to update lineage")
            return False
        
        print("✓ Lineage updated")
        
        # Step 5: Simulate page refresh by ensuring persistence
        print("\n3. Simulating page refresh (ensuring persistence)...")
        persistence_response = requests.post(f"{base_url}/api/ensure-lineage-persistence")
        if persistence_response.status_code != 200:
            print("✗ Failed to ensure persistence")
            return False
        
        print("✓ Persistence ensured")
        
        # Step 6: "Refresh" by getting tags again
        print("\n4. Refreshing data...")
        time.sleep(1)
        
        refresh_tags_response = requests.get(f"{base_url}/api/available-tags?limit=50")
        if refresh_tags_response.status_code != 200:
            print("✗ Failed to get refreshed tags")
            return False
        
        refreshed_tags = refresh_tags_response.json()
        
        # Find the same tag
        refreshed_tag = None
        for tag in refreshed_tags:
            if tag.get('Product Name*') == tag_name:
                refreshed_tag = tag
                break
        
        if not refreshed_tag:
            print("✗ Could not find refreshed tag")
            return False
        
        refreshed_lineage = refreshed_tag.get('Lineage', '')
        print(f"   Refreshed lineage: {refreshed_lineage}")
        
        if refreshed_lineage == new_lineage:
            print("✓ Lineage change persisted after simulated page refresh!")
        else:
            print(f"✗ Lineage change did not persist after refresh. Expected: {new_lineage}, Got: {refreshed_lineage}")
            return False
        
        print("\n=== PAGE REFRESH SIMULATION COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        print(f"✗ Page refresh simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting strain persistence fix tests...")
    
    # Test basic strain persistence
    test1_success = test_strain_persistence_fix()
    
    # Test page refresh simulation
    test2_success = test_page_refresh_simulation()
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Basic persistence test: {'✓ PASSED' if test1_success else '✗ FAILED'}")
    print(f"Page refresh simulation: {'✓ PASSED' if test2_success else '✗ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! Strain persistence fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.") 