#!/usr/bin/env python3
"""
Analyze which approach prevents splitting by examining actual DOCX XML.
"""

import sys
sys.path.insert(0, '/Users/adamcordova/Desktop/labelMaker_ QR copy final')

import zipfile
import re

test_files = [
    'test_1_current_approach.docx',
    'test_2_no_wordwrap.docx',
    'test_3_no_wordwrap_no_suppresshyphens.docx',
    'test_4_zwj_between_number_unit.docx',
    'test_5_word_joiner_u2060.docx',
    'test_6_single_run.docx',
    'test_7_split_at_hyphen_with_nobreak.docx',
    'test_8_nobreak_entire_run.docx',
]

print("="*80)
print("ANALYZING DOCX FILES FOR WRAPPING PREVENTION")
print("="*80)

for filename in test_files:
    filepath = f'/Users/adamcordova/Desktop/labelMaker_ QR copy final/{filename}'

    print(f"\n{filename}:")
    print("-" * 80)

    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            with zip_ref.open('word/document.xml') as xml_file:
                xml_content = xml_file.read().decode('utf-8')

                # Check for various properties
                has_wordwrap = 'w:wordWrap' in xml_content
                has_suppress_hyphens = 'w:suppressAutoHyphens' in xml_content
                has_nobreak = 'w:noBreak' in xml_content
                has_tcfittext = 'w:tcFitText' in xml_content

                # Extract text content
                text_matches = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', xml_content)
                text_content = ''.join(text_matches)

                # Check what character is between number and unit
                char_between = "unknown"
                if '\xa0' in text_content:  # Non-breaking space
                    char_between = "NBSP (U+00A0)"
                elif '\u200d' in text_content:  # Zero-width joiner
                    char_between = "ZWJ (U+200D)"
                elif '\u2060' in text_content:  # Word joiner
                    char_between = "Word Joiner (U+2060)"

                print(f"  Properties:")
                print(f"    - wordWrap: {has_wordwrap}")
                print(f"    - suppressAutoHyphens: {has_suppress_hyphens}")
                print(f"    - noBreak (run-level): {has_nobreak}")
                print(f"    - tcFitText (cell-level): {has_tcfittext}")
                print(f"  Character between number and unit: {char_between}")
                print(f"  Full text: {repr(text_content)}")

    except FileNotFoundError:
        print(f"  ❌ File not found")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)
print("""
Based on Word's text wrapping behavior:

1. NBSP (U+00A0) alone may not be sufficient - Word can still break at NBSP
   under certain conditions (like with wordWrap enabled).

2. Word Joiner (U+2060) is specifically designed to prevent line breaks while
   being invisible. This is stronger than NBSP.

3. The w:noBreak tag at run-level prevents the entire run from breaking across lines.

BEST APPROACH: Use Word Joiner (U+2060) instead of NBSP (U+00A0)
- Change make_nonbreaking_hyphens to use U+2060 instead of U+00A0
- This is the most reliable way to prevent "7g" from splitting
""")
