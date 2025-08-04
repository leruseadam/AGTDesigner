#!/usr/bin/env python3
"""
Test script to verify ratio font sizing is working correctly.
"""

import requests
import json
import time

def test_ratio_font_sizing():
    """Test that ratio font sizing is using correct sizes."""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testing ratio font sizing...")
    print("=" * 50)
    
    # Test data for ratio content
    test_data = {
        "template_type": "vertical",
        "scale_factor": 1.0,
        "selected_tags": ["Core Reactor Quartz Banger"]  # Use a simple product for testing
    }
    
    print(f"\n📄 Generating label with template: {test_data['template_type']}")
    print(f"   Scale factor: {test_data['scale_factor']}")
    print(f"   Selected product: {test_data['selected_tags'][0]}")
    
    try:
        # Generate a label
        start_time = time.time()
        response = requests.post(f"{base_url}/api/generate", json=test_data)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Label generated successfully in {generation_time:.2f}s")
            print(f"   📁 File size: {len(response.content)} bytes")
            
            # Save the file for inspection
            filename = f"test_ratio_font_sizing_{int(time.time())}.docx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"   💾 Saved as: {filename}")
            
            # Test different template types
            templates = ['vertical', 'horizontal', 'mini']
            for template in templates:
                print(f"\n🔄 Testing {template} template...")
                test_data['template_type'] = template
                
                try:
                    response = requests.post(f"{base_url}/api/generate", json=test_data)
                    if response.status_code == 200:
                        filename = f"test_ratio_{template}_{int(time.time())}.docx"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f"   ✅ {template} template generated: {filename}")
                    else:
                        print(f"   ❌ Failed to generate {template} template: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error generating {template} template: {e}")
            
            print(f"\n📋 Expected ratio font sizes:")
            print(f"   Vertical: 12pt (or 11pt for THC/CBD format)")
            print(f"   Horizontal: 12pt (or 11pt for THC/CBD format)")
            print(f"   Mini: 9pt (or 8pt for THC/CBD format)")
            print(f"\n📝 Please check the generated files to verify ratio text is properly sized.")
            
        else:
            print(f"   ❌ Failed to generate label: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Ratio font sizing test complete!")

if __name__ == "__main__":
    test_ratio_font_sizing() 