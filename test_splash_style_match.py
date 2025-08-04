#!/usr/bin/env python3
"""
Test to verify that generation splash style matches opening splash style
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_splash_style_match():
    """Test that generation splash style matches opening splash style"""
    print("=== Testing Splash Style Match ===")
    
    # Read the opening splash template
    with open('templates/splash.html', 'r') as f:
        opening_splash = f.read()
    
    # Read the generation splash template
    with open('templates/generation-splash.html', 'r') as f:
        generation_splash = f.read()
    
    # Read the main index template to check the modal styles
    with open('templates/index.html', 'r') as f:
        index_template = f.read()
    
    # Read the generation splash JavaScript
    with open('static/js/generation-splash.js', 'r') as f:
        generation_splash_js = f.read()
    
    print("✅ All splash files loaded successfully")
    
    # Check key style elements
    style_checks = [
        {
            'name': 'Background Gradient',
            'opening': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
            'generation': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
        },
        {
            'name': 'Container Background',
            'opening': 'rgba(22, 33, 62, 0.95)',
            'generation': 'rgba(22, 33, 62, 0.95)'
        },
        {
            'name': 'Border Color',
            'opening': 'rgba(0, 212, 170, 0.2)',
            'generation': 'rgba(0, 212, 170, 0.2)'
        },
        {
            'name': 'Logo Gradient',
            'opening': 'linear-gradient(135deg, #00d4aa, #0099cc)',
            'generation': 'linear-gradient(135deg, #00d4aa, #0099cc)'
        },
        {
            'name': 'Border Radius',
            'opening': 'border-radius: 24px',
            'generation': 'border-radius: 24px'
        }
    ]
    
    all_matched = True
    
    for check in style_checks:
        opening_found = check['opening'] in opening_splash
        generation_found = check['generation'] in generation_splash
        js_found = check['generation'] in generation_splash_js
        
        if opening_found and (generation_found or js_found):
            print(f"✅ {check['name']}: Matches")
        else:
            print(f"❌ {check['name']}: Does not match")
            print(f"   Opening splash: {opening_found}")
            print(f"   Generation splash: {generation_found}")
            print(f"   Generation JS: {js_found}")
            all_matched = False
    
    # Check if the modal overlay in index.html has been updated
    if 'rgba(22, 33, 62, 0.95)' in index_template and 'rgba(0, 212, 170, 0.2)' in index_template:
        print("✅ Modal overlay styles: Updated to match opening splash")
    else:
        print("❌ Modal overlay styles: Still using old purple theme")
        all_matched = False
    
    if all_matched:
        print("\n🎉 SUCCESS: Generation splash style matches opening splash style!")
    else:
        print("\n❌ FAILURE: Generation splash style does not match opening splash style")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_splash_style_match() 