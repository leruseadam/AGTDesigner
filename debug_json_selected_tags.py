#!/usr/bin/env python3
"""
Debug script to test JSON matching and selected tags functionality
"""

import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, get_session_excel_processor, get_session_json_matcher
from flask import session

def test_json_matching():
    """Test JSON matching functionality"""
    
    with app.app_context():
        # Initialize session
        session['session_id'] = 'test_session'
        
        # Get Excel processor
        excel_processor = get_session_excel_processor()
        print(f"Excel processor loaded: {excel_processor is not None}")
        print(f"Excel data shape: {excel_processor.df.shape if excel_processor.df is not None else 'None'}")
        
        # Get JSON matcher
        json_matcher = get_session_json_matcher()
        print(f"JSON matcher loaded: {json_matcher is not None}")
        
        # Test with local test file
        test_file_path = "test_products.json"
        if os.path.exists(test_file_path):
            print(f"Test file exists: {test_file_path}")
            
            # Read test data
            with open(test_file_path, 'r') as f:
                test_data = json.load(f)
            print(f"Test data contains {len(test_data)} products")
            
            # Test product database matching
            try:
                matched_products = json_matcher.fetch_and_match_with_product_db(f"file://{os.path.abspath(test_file_path)}")
                print(f"Product database matching found {len(matched_products)} products")
                
                # Check what the matched products look like
                if matched_products:
                    print("Sample matched product:")
                    print(json.dumps(matched_products[0], indent=2))
                    
                    # Test the selected tags logic
                    print("\nTesting selected tags logic:")
                    
                    # Simulate what the backend does
                    selected_tag_objects = matched_products.copy()
                    print(f"Selected tag objects: {len(selected_tag_objects)}")
                    
                    # Update session selected tags
                    session['selected_tags'] = []
                    excel_processor.selected_tags = []
                    
                    for tag in selected_tag_objects:
                        if isinstance(tag, dict):
                            # Store the full dictionary object in session
                            session['selected_tags'].append(tag)
                            # Store just the product name in ExcelProcessor's selected_tags
                            product_name = tag.get('Product Name*', '')
                            if product_name:
                                excel_processor.selected_tags.append(product_name)
                    
                    print(f"Session selected tags: {len(session['selected_tags'])}")
                    print(f"Excel processor selected tags: {len(excel_processor.selected_tags)}")
                    print(f"Sample session tag: {session['selected_tags'][0] if session['selected_tags'] else 'None'}")
                    print(f"Sample excel processor tag: {excel_processor.selected_tags[0] if excel_processor.selected_tags else 'None'}")
                    
            except Exception as e:
                print(f"Error in product database matching: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Test file not found: {test_file_path}")

if __name__ == "__main__":
    test_json_matching() 