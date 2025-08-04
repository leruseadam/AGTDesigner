#!/usr/bin/env python3
"""
Test to verify that redundant welcome animations have been removed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_welcome_animation_removal():
    """Test that redundant welcome animations have been removed"""
    print("=== Testing Welcome Animation Removal ===")
    
    # Read the splash template
    with open('templates/splash.html', 'r') as f:
        splash_html = f.read()
    
    # Read the enhanced UI JavaScript
    with open('static/js/enhanced-ui.js', 'r') as f:
        enhanced_ui_js = f.read()
    
    # Read the main JavaScript
    with open('static/js/main.js', 'r') as f:
        main_js = f.read()
    
    print("✅ All files loaded successfully")
    
    # Check if redundant welcome text was removed from splash
    if 'Welcome to Label Maker!' not in splash_html:
        print("✅ Redundant 'Welcome to Label Maker!' removed from splash loading texts")
    else:
        print("❌ Redundant 'Welcome to Label Maker!' still present in splash loading texts")
    
    # Check if welcome animation was removed from enhanced UI
    if 'Welcome to AGT Label Maker' not in enhanced_ui_js:
        print("✅ Redundant 'Welcome to AGT Label Maker' animation removed from enhanced UI")
    else:
        print("❌ Redundant 'Welcome to AGT Label Maker' animation still present in enhanced UI")
    
    # Check if welcomeFade animation was removed
    if 'welcomeFade' not in enhanced_ui_js:
        print("✅ Redundant welcomeFade animation removed from enhanced UI")
    else:
        print("❌ Redundant welcomeFade animation still present in enhanced UI")
    
    # Check if AGT Designer references were updated to Label Maker
    if 'Welcome to Label Maker!' in main_js and 'Welcome to AGT Designer!' not in main_js:
        print("✅ AGT Designer references updated to Label Maker in main.js")
    else:
        print("❌ AGT Designer references not properly updated in main.js")
    
    # Check if the splash still has the main title
    if 'LABEL MAKER' in splash_html:
        print("✅ Main 'LABEL MAKER' title still present in splash")
    else:
        print("❌ Main 'LABEL MAKER' title missing from splash")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_welcome_animation_removal() 