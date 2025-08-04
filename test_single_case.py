#!/usr/bin/env python3
"""
Simple test for a specific case.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.unified_font_sizing import get_font_size
from docx.shared import Pt

def test_single_case():
    """Test a specific case with logging."""
    
    text = 'CONSTELLATION ABC'
    print(f"Testing: '{text}'")
    
    # Check word lengths
    words = text.split()
    word_lengths = [len(word) for word in words]
    long_words = [word for word in words if len(word) >= 8]
    
    print(f"Words: {words}")
    print(f"Word lengths: {word_lengths}")
    print(f"Long words (8+ chars): {long_words}")
    print(f"Number of long words: {len(long_words)}")
    
    # Test brand font sizing
    font_size = get_font_size(text, 'brand', 'double', 1.0)
    print(f"Brand font size: {font_size.pt}pt")
    
    # Check if our rule should trigger
    should_trigger = len(long_words) >= 2
    print(f"Should trigger our rule: {should_trigger}")

if __name__ == "__main__":
    test_single_case() 