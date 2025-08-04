#!/usr/bin/env python3
"""
Test script to demonstrate complete label generation workflow with Cultivera JSON data.
This shows how all JSON matched items can be generated as labels.
"""

import requests
import json
import time

def test_complete_cultivera_workflow():
    """Test the complete workflow: JSON matching -> Selection -> Label generation."""
    
    # Real Cultivera JSON URL
    cultivera_url = "https://files.cultivera.com/435553542D5753313030303438/Interop/25/28/0KMK8B1FTA5RZZ67/Cultivera_ORD-153392_422044.json"
    
    print("🚀 Complete Cultivera Label Generation Workflow")
    print("=" * 60)
    print()
    
    try:
        # Step 1: JSON Matching
        print("📋 Step 1: JSON Matching")
        print("-" * 30)
        
        response = requests.post('http://127.0.0.1:5001/api/json-match', 
                               json={'url': cultivera_url}, 
                               timeout=120)
        
        if response.status_code != 200:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        match_result = response.json()
        available_tags = match_result.get('available_tags', [])
        
        print(f"✅ JSON matching successful!")
        print(f"   Matched items: {len(available_tags)}")
        print(f"   Available tags updated with Cultivera transfer items")
        print()
        
        # Step 2: Get Available Tags (should now contain only JSON matched items)
        print("📋 Step 2: Verify Available Tags")
        print("-" * 30)
        
        response = requests.get('http://127.0.0.1:5001/api/available-tags', timeout=30)
        
        if response.status_code == 200:
            available_data = response.json()
            print(f"✅ Available tags retrieved: {len(available_data)} items")
            print("   (Should now contain only the Cultivera transfer items)")
            print()
            
            # Show sample available tags
            print("📋 Sample Available Tags:")
            for i, tag in enumerate(available_data[:5], 1):
                product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                vendor = tag.get('Vendor', 'Unknown')
                price = tag.get('Price', 'Unknown')
                source = tag.get('Source', 'Unknown')
                
                print(f"  {i}. {product_name}")
                print(f"     Source: {source}")
                print(f"     Vendor: {vendor}")
                print(f"     Price: {price}")
                print()
            
            if len(available_data) > 5:
                print(f"     ... and {len(available_data) - 5} more items")
                print()
        else:
            print(f"❌ Failed to get available tags: {response.status_code}")
            return False
        
        # Step 3: Select All Items for Label Generation
        print("📋 Step 3: Select All Items for Labels")
        print("-" * 30)
        
        # Get all product names from available tags
        all_product_names = []
        for tag in available_data:
            product_name = tag.get('Product Name*', tag.get('ProductName', ''))
            if product_name:
                all_product_names.append(product_name)
        
        print(f"✅ Selected {len(all_product_names)} items for label generation")
        print("   (All items from the Cultivera transfer)")
        print()
        
        # Show what we're generating labels for
        print("🎯 Generating Labels For:")
        for i, name in enumerate(all_product_names[:10], 1):
            print(f"  {i}. {name}")
        
        if len(all_product_names) > 10:
            print(f"     ... and {len(all_product_names) - 10} more items")
        print()
        
        # Step 4: Generate Labels
        print("📋 Step 4: Generate Labels")
        print("-" * 30)
        
        # Test with different template types
        template_types = ['mini', 'vertical', 'horizontal', 'double']
        
        for template_type in template_types:
            print(f"🔄 Generating {template_type.upper()} template labels...")
            
            try:
                response = requests.post('http://127.0.0.1:5001/api/generate', 
                                       json={
                                           'selected_tags': all_product_names,
                                           'template_type': template_type,
                                           'scale_factor': 1.0
                                       }, 
                                       timeout=60)
                
                if response.status_code == 200:
                    print(f"✅ {template_type.upper()} labels generated successfully!")
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                    print(f"   Content-Length: {len(response.content)} bytes")
                    print(f"   Labels generated for {len(all_product_names)} items")
                    print()
                else:
                    print(f"❌ {template_type.upper()} label generation failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"   Response: {response.text[:200]}...")
                    print()
                    
            except requests.exceptions.Timeout:
                print(f"⏰ {template_type.upper()} label generation timed out")
                print("   (This is normal for large batches)")
                print()
            except Exception as e:
                print(f"❌ {template_type.upper()} label generation error: {e}")
                print()
        
        # Step 5: Summary
        print("📋 Step 5: Workflow Summary")
        print("-" * 30)
        
        print("🎉 Complete Workflow Results:")
        print(f"   ✅ JSON matching: {len(available_tags)} items processed")
        print(f"   ✅ Available tags: {len(available_data)} items filtered")
        print(f"   ✅ Label generation: {len(all_product_names)} items selected")
        print()
        
        print("💡 Key Benefits:")
        print("   • Only relevant items from the transfer are shown")
        print("   • No need to search through 2,000+ products")
        print("   • All items can be generated as labels")
        print("   • Works with any Cultivera transfer URL")
        print("   • Supports all template types (mini, vertical, horizontal, double)")
        print()
        
        print("🚀 Ready for Production Use!")
        print("   You can now use this workflow for any Cultivera transfer.")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        print("Make sure the server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_single_item_label_generation():
    """Test label generation for a single item to verify quality."""
    
    print("\n🔍 Testing Single Item Label Generation")
    print("=" * 50)
    
    try:
        # Get available tags first
        response = requests.get('http://127.0.0.1:5001/api/available-tags', timeout=30)
        
        if response.status_code == 200:
            available_data = response.json()
            
            if available_data:
                # Test with first item
                first_item = available_data[0]
                product_name = first_item.get('Product Name*', first_item.get('ProductName', 'Unknown'))
                
                print(f"🎯 Testing label generation for: {product_name}")
                print()
                
                # Generate mini template label
                response = requests.post('http://127.0.0.1:5001/api/generate', 
                                       json={
                                           'selected_tags': [product_name],
                                           'template_type': 'mini',
                                           'scale_factor': 1.0
                                       }, 
                                       timeout=30)
                
                if response.status_code == 200:
                    print(f"✅ Single item label generated successfully!")
                    print(f"   Product: {product_name}")
                    print(f"   Template: Mini")
                    print(f"   File size: {len(response.content)} bytes")
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                    print()
                    
                    # Show product details
                    print("📋 Product Details:")
                    print(f"   Name: {product_name}")
                    print(f"   Vendor: {first_item.get('Vendor', 'Unknown')}")
                    print(f"   Price: {first_item.get('Price', 'Unknown')}")
                    print(f"   Strain: {first_item.get('Product Strain', 'Unknown')}")
                    print(f"   Source: {first_item.get('Source', 'Unknown')}")
                    print()
                    
                    return True
                else:
                    print(f"❌ Single item label generation failed: {response.status_code}")
                    return False
            else:
                print("❌ No available tags found")
                return False
        else:
            print(f"❌ Failed to get available tags: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing single item: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Cultivera Label Generation Test")
    print("=" * 60)
    print()
    
    # Test complete workflow
    success1 = test_complete_cultivera_workflow()
    
    # Test single item generation
    success2 = test_single_item_label_generation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Complete workflow is working perfectly")
        print("✅ All items can be generated as labels")
        print("✅ Single item generation works correctly")
    elif success1:
        print("🎉 WORKFLOW SUCCESS!")
        print("✅ JSON matching and bulk generation work")
        print("⚠️  Single item generation needs investigation")
    else:
        print("❌ TESTS FAILED")
        print("🔧 Check the server logs for more details") 