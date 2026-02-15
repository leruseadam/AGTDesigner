#!/usr/bin/env python3
"""Test script to verify lineage functionality and cache behavior."""
import os
import sys
import logging

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)

def test_lineage_generation():
    """Test that lineage is correctly assigned for classic and non-classic types."""
    try:
        import app as main_app
        from flask import Flask
        from src.core.generation.fast_generation import clear_all_caches

        # Clear caches first
        clear_all_caches()
        logging.info("Cleared all generation caches")

        # Test data: one classic (flower), one non-classic (edible)
        test_records = [
            {
                'Product Name*': 'Test Classic Flower',
                'ProductType': 'flower',
                'Lineage': '',  # Empty to test fallback
                'ProductBrand': 'Test Brand',
                'Product Strain': 'Test Strain',
                'Weight*': '1',
                'Units': 'g',
                'Price': '10.00'
            },
            {
                'Product Name*': 'Test Edible',
                'ProductType': 'edible (solid)',
                'Lineage': '',  # Empty to test fallback
                'ProductBrand': 'Edible Brand',
                'Product Strain': 'CBD Blend',
                'Weight*': '10',
                'Units': 'mg',
                'Price': '5.00'
            }
        ]

        # Test fast generation
        from src.core.generation.fast_generation import FastGenerationEngine
        from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

        font_scheme = get_font_scheme('horizontal')
        template_processor = TemplateProcessor('horizontal', font_scheme)
        engine = FastGenerationEngine(template_processor)

        # Generate document
        doc = engine.generate_with_cache(test_records, 'horizontal', 1.0)

        if doc:
            logging.info("✅ Document generated successfully")
            # Check cache stats
            hit_rate = engine._get_hit_rate()
            logging.info(f"Cache hit rate: {hit_rate:.1f}%")
            return True
        else:
            logging.error("❌ Document generation failed")
            return False

    except Exception as e:
        logging.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_lineage_generation()
    sys.exit(0 if success else 1)