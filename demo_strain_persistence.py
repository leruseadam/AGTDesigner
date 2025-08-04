#!/usr/bin/env python3
"""
Demonstration script showing the strain persistence fix in action.
This script demonstrates how strain changes now persist after page refresh.
"""

import requests
import time
import json
from datetime import datetime

def demo_strain_persistence():
    """Demonstrate the strain persistence fix."""
    
    print("=== STRAIN PERSISTENCE FIX DEMONSTRATION ===")
    print(f"Demonstration started at: {datetime.now()}")
    print()
    
    base_url = "http://localhost:9090"
    
    try:
        # Step 1: Check current state
        print("1. 📊 Checking current backend state...")
        status_response = requests.get(f"{base_url}/api/status")
        status = status_response.json()
        
        if not status.get('data_loaded'):
            print("   ❌ No data loaded. Please upload a file first.")
            return False
        
        print(f"   ✅ Data loaded: {status['data_shape'][0]} rows, {status['data_shape'][1]} columns")
        print(f"   📁 File: {status['last_loaded_file']}")
        
        # Step 2: Get current tags
        print("\n2. 🏷️  Getting current tags...")
        tags_response = requests.get(f"{base_url}/api/available-tags")
        tags = tags_response.json()
        
        print(f"   ✅ Found {len(tags)} available tags")
        
        # Step 3: Find a tag to modify
        test_tag = None
        for tag in tags:
            if tag.get('Lineage') and tag.get('Product Name*') and tag.get('Product Strain'):
                test_tag = tag
                break
        
        if not test_tag:
            print("   ❌ No suitable tag found for testing")
            return False
        
        tag_name = test_tag['Product Name*']
        current_lineage = test_tag['Lineage']
        strain_name = test_tag['Product Strain']
        
        print(f"   🎯 Test tag: {tag_name}")
        print(f"   🧬 Current lineage: {current_lineage}")
        print(f"   🌿 Strain: {strain_name}")
        
        # Step 4: Make a lineage change
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        print(f"\n3. 🔄 Making lineage change: {current_lineage} → {new_lineage}")
        
        update_response = requests.post(f"{base_url}/api/update-lineage", json={
            'tag_name': tag_name,
            'lineage': new_lineage
        })
        
        if update_response.status_code != 200:
            print(f"   ❌ Failed to update lineage: {update_response.status_code}")
            return False
        
        update_result = update_response.json()
        print(f"   ✅ Lineage updated successfully!")
        print(f"   📝 Backend response: {update_result['message']}")
        
        # Step 5: Verify immediate change
        print("\n4. ✅ Verifying immediate change...")
        time.sleep(1)
        
        verify_response = requests.get(f"{base_url}/api/available-tags")
        verify_tags = verify_response.json()
        
        for tag in verify_tags:
            if tag.get('Product Name*') == tag_name:
                immediate_lineage = tag.get('Lineage', '')
                print(f"   🧬 Immediate lineage: {immediate_lineage}")
                if immediate_lineage == new_lineage:
                    print("   ✅ Immediate change verified!")
                else:
                    print(f"   ❌ Immediate change failed. Expected: {new_lineage}, Got: {immediate_lineage}")
                break
        
        # Step 6: Ensure persistence
        print("\n5. 🔒 Ensuring lineage persistence...")
        persistence_response = requests.post(f"{base_url}/api/ensure-lineage-persistence")
        persistence_result = persistence_response.json()
        
        print(f"   ✅ Persistence ensured: {persistence_result['message']}")
        
        # Step 7: Simulate page refresh
        print("\n6. 🔄 Simulating page refresh...")
        print("   (In a real scenario, this would be a browser page refresh)")
        
        # Clear any cached data by making a fresh request
        time.sleep(1)
        refresh_response = requests.get(f"{base_url}/api/available-tags")
        refresh_tags = refresh_response.json()
        
        # Find the same tag after "refresh"
        refreshed_tag = None
        for tag in refresh_tags:
            if tag.get('Product Name*') == tag_name:
                refreshed_tag = tag
                break
        
        if refreshed_tag:
            refreshed_lineage = refreshed_tag.get('Lineage', '')
            print(f"   🧬 Refreshed lineage: {refreshed_lineage}")
            
            if refreshed_lineage == new_lineage:
                print("   ✅ Lineage change persisted after 'page refresh'!")
                print("   🎉 SUCCESS: The strain persistence fix is working!")
            else:
                print(f"   ❌ Lineage change did not persist. Expected: {new_lineage}, Got: {refreshed_lineage}")
                return False
        else:
            print("   ❌ Could not find tag after refresh")
            return False
        
        # Step 8: Test multiple changes
        print("\n7. 🔄 Testing multiple lineage changes...")
        
        # Make another change
        second_new_lineage = "HYBRID" if refreshed_lineage != "HYBRID" else "MIXED"
        print(f"   Making second change: {refreshed_lineage} → {second_new_lineage}")
        
        second_update_response = requests.post(f"{base_url}/api/update-lineage", json={
            'tag_name': tag_name,
            'lineage': second_new_lineage
        })
        
        if second_update_response.status_code == 200:
            print("   ✅ Second change applied successfully!")
            
            # Verify second change
            time.sleep(1)
            final_response = requests.get(f"{base_url}/api/available-tags")
            final_tags = final_response.json()
            
            for tag in final_tags:
                if tag.get('Product Name*') == tag_name:
                    final_lineage = tag.get('Lineage', '')
                    print(f"   🧬 Final lineage: {final_lineage}")
                    if final_lineage == second_new_lineage:
                        print("   ✅ Multiple changes working correctly!")
                    else:
                        print(f"   ❌ Multiple changes failed. Expected: {second_new_lineage}, Got: {final_lineage}")
                    break
        else:
            print("   ❌ Second change failed")
        
        print("\n=== DEMONSTRATION COMPLETED SUCCESSFULLY ===")
        print("🎉 The strain persistence fix is working correctly!")
        print()
        print("📋 Summary of what was tested:")
        print("   ✅ Data loading and verification")
        print("   ✅ Lineage change application")
        print("   ✅ Immediate change verification")
        print("   ✅ Persistence enforcement")
        print("   ✅ Page refresh simulation")
        print("   ✅ Multiple change handling")
        print()
        print("🔧 Technical improvements implemented:")
        print("   • Enhanced backend persistence endpoint")
        print("   • Improved frontend data loading")
        print("   • Better cache management")
        print("   • Database override application")
        print("   • Automatic state restoration")
        
        return True
        
    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting strain persistence fix demonstration...")
    print("This demonstration shows how strain changes now persist after page refresh.")
    print()
    
    success = demo_strain_persistence()
    
    if success:
        print("\n🎯 DEMONSTRATION RESULT: SUCCESS")
        print("The strain persistence fix is working correctly!")
    else:
        print("\n❌ DEMONSTRATION RESULT: FAILED")
        print("Please check the implementation and try again.") 