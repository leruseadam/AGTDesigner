#!/usr/bin/env python3
"""
Test to debug the double line break issue.
"""

def break_after_2nd_space(s):
    parts = s.split(' ')
    out = []
    for i, part in enumerate(parts):
        out.append(part)
        if (i+1) % 2 == 0 and i != len(parts)-1:
            out.append('\n')
    result = ' '.join(out).replace(' \n ', '\n')
    return result

# Test cases
test_cases = [
    '10mg THC 30mg CBD 5mg CBG 5mg CBN',
    'THC 10mg CBD 20mg',
    '5mg THC 15mg CBD 2mg CBG'
]

print("Testing line break logic:")
print("=" * 50)

for test_case in test_cases:
    print(f"\nInput: '{test_case}'")
    result = break_after_2nd_space(test_case)
    print(f"Result: '{result}'")
    print(f"Result repr: {repr(result)}")
    
    # Count newlines
    newline_count = result.count('\n')
    print(f"Newline count: {newline_count}")
    
    # Show each character
    print("Characters:")
    for i, char in enumerate(result):
        if char == '\n':
            print(f"  {i}: \\n")
        else:
            print(f"  {i}: '{char}'") 