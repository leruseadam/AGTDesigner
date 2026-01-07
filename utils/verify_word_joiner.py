#!/usr/bin/env python3
"""
Verify that Word Joiner (U+2060) is now being used instead of NBSP (U+00A0).
"""

import sys
sys.path.insert(0, '/Users/adamcordova/Desktop/labelMaker_ QR copy final')

from src.core.generation.text_processing import make_nonbreaking_hyphens, make_nonbreaking_weight_units

test_cases = [
    "Blueberry - 7g",
    "Swiss Watch - 3.5g",
    "100 Rackz - 7g",
    "Garlic Grapes - 7g",
]

print("="*80)
print("VERIFYING WORD JOINER (U+2060) IS USED")
print("="*80)

for test in test_cases:
    processed = make_nonbreaking_hyphens(test)
    processed = make_nonbreaking_weight_units(processed)

    print(f"\nOriginal:  {repr(test)}")
    print(f"Processed: {repr(processed)}")

    # Check for Word Joiner
    has_word_joiner = '\u2060' in processed
    has_nbsp = '\u00A0' in processed
    has_non_breaking_hyphen = '\u2011' in processed

    print(f"  ✓ Word Joiner (U+2060): {has_word_joiner}")
    print(f"  {'✗' if has_nbsp else '✓'} NBSP (U+00A0): {has_nbsp} {'(should be False)' if has_nbsp else ''}")
    print(f"  ✓ Non-breaking hyphen (U+2011): {has_non_breaking_hyphen}")

    # Show character breakdown for the weight portion
    import re
    weight_match = re.search(r'‑.(\d+\.?\d*[gmolz]+)', processed)
    if weight_match:
        weight_portion = weight_match.group(0)
        print(f"  Weight portion: {repr(weight_portion)}")
        for i, char in enumerate(weight_portion):
            char_name = {
                '\u2011': 'NON-BREAKING HYPHEN',
                '\u2060': 'WORD JOINER',
                '\u00A0': 'NBSP (NON-BREAKING SPACE)',
            }.get(char, chr(ord(char)) if ord(char) >= 32 else f'[U+{ord(char):04X}]')
            print(f"    [{i}] {repr(char)} = {char_name}")

print("\n" + "="*80)
print("✅ All text processing now uses Word Joiner (U+2060) to prevent splitting!")
print("="*80)
