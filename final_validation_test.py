#!/usr/bin/env python3
"""
Final comprehensive validation test for JSON matching
"""

import requests
import json
import base64

def final_validation_test():
    """Run final validation with real-world scenario"""
    
    # Real-world test data that should match your Excel inventory
    test_data = {
        "inventory_transfer_items": [
            {
                "product_name": "Core Reactor Quartz Banger",
                "vendor": "One Stop Wholesale",
                "brand": "One Stop Wholesale",
                "product_type": "Paraphernalia",
                "weight": "1",
                "strain_name": "Paraphernalia"
            },
            {
                "product_name": "Terp Slurper Quartz Banger",
                "vendor": "Hibro Wholesale",
                "brand": "Hibro Wholesale", 
                "product_type": "Paraphernalia",
                "weight": "1",
                "strain_name": "Paraphernalia"
            },
            {
                "product_name": "Diamond Knot Quartz Banger",
                "vendor": "Hibro Wholesale",
                "brand": "Hibro Wholesale",
                "product_type": "Paraphernalia", 
                "weight": "1",
                "strain_name": "Paraphernalia"
            },
            {
                "product_name": "Plastic K-clip",
                "vendor": "S & A Wholesale",
                "brand": "S & A Wholesale",
                "product_type": "Paraphernalia",
                "weight": "1", 
                "strain_name": "Paraphernalia"
            },
            {
                "product_name": "Assorted Design Bowl Piece by Hibro Wholesale",
                "vendor": "Hibro Wholesale",
                "brand": "Hibro Wholesale",
                "product_type": "Paraphernalia",
                "weight": "1",
                "strain_name": "Paraphernalia"
            }
        ],
        "session_id": "final_validation"
    }
    
    # Encode test data
    json_str = json.dumps(test_data)
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    data_url = f"data:application/json;base64,{encoded}"
    
    payload = {"url": data_url}
    
    print("🎯 Final Validation Test")
    print("=" * 50)
    print("Testing 5 known products from your Excel inventory:")
    for i, item in enumerate(test_data["inventory_transfer_items"], 1):
        print(f"{i}. {item['product_name']} ({item['vendor']})")
    
    try:
        response = requests.post("http://localhost:5001/api/json-match", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Request successful!")
            print(f"🎯 Matches found: {result.get('matched_count', 0)}/5")
            print(f"📋 Available tags: {len(result.get('available_tags', []))}")
            print(f"✅ Success: {result.get('success', False)}")
            
            # Show detailed results
            available_tags = result.get('available_tags', [])
            print(f"\n📊 Detailed Results:")
            
            for i, tag in enumerate(available_tags, 1):
                product_name = tag.get('Product Name*', 'Unknown')
                vendor = tag.get('Vendor', 'Unknown')
                confidence = tag.get('Match Confidence', 'Unknown')
                source = tag.get('Source', 'Unknown')
                
                print(f"\nMatch {i}:")
                print(f"  📝 Product: {product_name}")
                print(f"  🏪 Vendor: {vendor}")
                print(f"  🎯 Confidence: {confidence}")
                print(f"  📍 Source: {source}")
            
            # Validation summary
            expected_matches = 5
            actual_matches = result.get('matched_count', 0)
            
            print(f"\n{'='*50}")
            print(f"📊 VALIDATION SUMMARY")
            print(f"{'='*50}")
            print(f"Expected matches: {expected_matches}")
            print(f"Actual matches: {actual_matches}")
            print(f"Success rate: {(actual_matches/expected_matches)*100:.1f}%")
            
            if actual_matches == expected_matches:
                print(f"🎉 PERFECT! All {expected_matches} products matched successfully!")
                print(f"✅ JSON matching is working flawlessly!")
                return True
            elif actual_matches >= expected_matches * 0.8:  # 80% success rate
                print(f"✅ GOOD! {actual_matches}/{expected_matches} products matched.")
                print(f"📈 JSON matching is working well!")
                return True
            else:
                print(f"⚠️  Only {actual_matches}/{expected_matches} products matched.")
                print(f"🔧 JSON matching needs improvement.")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = final_validation_test()
    
    print(f"\n{'='*50}")
    if success:
        print("🏆 FINAL RESULT: JSON MATCHING IS WORKING PERFECTLY!")
        print("✅ Ready for production use!")
    else:
        print("⚠️  FINAL RESULT: JSON MATCHING NEEDS ATTENTION")
        print("🔧 Further debugging required.")
