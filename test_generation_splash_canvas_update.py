#!/usr/bin/env python3
"""
Test to verify that generation splash canvas animation has been updated to match opening splash style
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_generation_splash_canvas_update():
    """Test that generation splash canvas animation has been updated to match opening splash style"""
    print("=== Testing Generation Splash Canvas Update ===")
    
    # Read the main JavaScript file
    with open('static/js/main.js', 'r') as f:
        main_js = f.read()
    
    print("✅ Main JavaScript file loaded successfully")
    
    # Check if canvas animation has been updated to use teal/blue theme
    canvas_checks = [
        {
            'name': 'Canvas Background Gradient',
            'old': 'rgba(30, 20, 40, 0.95)',
            'new': 'rgba(22, 33, 62, 0.95)'
        },
        {
            'name': 'Canvas Background Gradient End',
            'old': 'rgba(50, 30, 70, 0.95)',
            'new': 'rgba(15, 52, 96, 0.95)'
        },
        {
            'name': 'Canvas Animated Elements',
            'old': 'rgba(160, 132, 232,',
            'new': 'rgba(0, 212, 170,'
        },
        {
            'name': 'Canvas Title Color',
            'old': '#a084e8',
            'new': '#00d4aa'
        },
        {
            'name': 'Canvas Border Color',
            'old': '#a084e8',
            'new': '#00d4aa'
        },
        {
            'name': 'Canvas Progress Bar',
            'old': '#667eea',
            'new': '#00d4aa'
        },
        {
            'name': 'Canvas Progress Bar End',
            'old': '#764ba2',
            'new': '#0099cc'
        }
    ]
    
    all_updated = True
    
    for check in canvas_checks:
        old_found = check['old'] in main_js
        new_found = check['new'] in main_js
        
        if not old_found and new_found:
            print(f"✅ {check['name']}: Updated to teal/blue theme")
        elif old_found and not new_found:
            print(f"❌ {check['name']}: Still using old purple theme")
            all_updated = False
        elif old_found and new_found:
            print(f"⚠️  {check['name']}: Both old and new found (may be in different contexts)")
        else:
            print(f"❌ {check['name']}: Neither old nor new found")
            all_updated = False
    
    # Check if fallback text-based splash has been updated
    if 'rgba(22, 33, 62, 0.95)' in main_js and 'rgba(30, 20, 40, 0.95)' not in main_js:
        print("✅ Fallback text-based splash: Updated to teal/blue theme")
    else:
        print("❌ Fallback text-based splash: Still using old purple theme")
        all_updated = False
    
    # Check if fallback progress bar has been updated
    if 'linear-gradient(90deg, #00d4aa, #0099cc)' in main_js and 'linear-gradient(90deg, #667eea, #764ba2)' not in main_js:
        print("✅ Fallback progress bar: Updated to teal/blue theme")
    else:
        print("❌ Fallback progress bar: Still using old purple theme")
        all_updated = False
    
    if all_updated:
        print("\n🎉 SUCCESS: Generation splash canvas animation updated to match opening splash style!")
    else:
        print("\n❌ FAILURE: Generation splash canvas animation still using old purple theme")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_generation_splash_canvas_update() 