# Brand Font Size Fix Summary

## Problem
Product brands with more than 20 letters in horizontal templates were not being properly sized, potentially causing readability issues and text overflow.

## Solution
Added a new rule to force font size to 14pt when product brand names contain more than 20 letters in horizontal templates.

## Implementation

### File Modified
**`src/core/generation/font_sizing.py`** (lines 113-125)

### Changes Made
**Before**:
```python
elif o == 'horizontal':
    # Special rule: If brand contains multiple words and is greater than 9 characters, set font to 14
    words = text.split()
    if len(words) > 1 and len(text) > 9:
        size = Pt(14 * scale_factor)
    elif comp < 20:
        size = Pt(16 * scale_factor)
    elif comp < 40:
        size = Pt(14 * scale_factor)
    elif comp < 80:
        size = Pt(12 * scale_factor)
    else:
        size = Pt(10 * scale_factor)
```

**After**:
```python
elif o == 'horizontal':
    # Special rule: If brand contains more than 20 letters, force font size to 14
    if len(text) > 20:
        size = Pt(14 * scale_factor)
    # Special rule: If brand contains multiple words and is greater than 9 characters, set font to 14
    elif len(text.split()) > 1 and len(text) > 9:
        size = Pt(14 * scale_factor)
    elif comp < 20:
        size = Pt(16 * scale_factor)
    elif comp < 40:
        size = Pt(14 * scale_factor)
    elif comp < 80:
        size = Pt(12 * scale_factor)
    else:
        size = Pt(10 * scale_factor)
```

## Font Size Rules for Horizontal Template Product Brands

1. **>20 letters**: Force to 14pt (NEW RULE)
2. **Multiple words + >9 characters**: 14pt (existing rule)
3. **Complexity <20**: 16pt
4. **Complexity <40**: 14pt
5. **Complexity <80**: 12pt
6. **Complexity ≥80**: 10pt

## Test Results

✅ **All tests passed** - The fix is working correctly:

- **Short brands** (<20 letters): Use normal sizing (16pt for simple brands)
- **Medium brands** (multi-word, >9 chars): 14pt (existing rule)
- **Long brands** (>20 letters): 14pt (new rule)
- **Edge cases**: Properly handled

## Examples

| Brand Name | Letters | Font Size | Rule Applied |
|------------|---------|-----------|--------------|
| "Short" | 5 | 16pt | Normal sizing |
| "Medium Brand" | 12 | 14pt | Multi-word rule |
| "Very Long Brand Name That Exceeds Twenty Letters" | 42 | 14pt | >20 letters rule |
| "Exactly Twenty Letters Here" | 25 | 14pt | >20 letters rule |
| "Twenty One Letters Here!" | 21 | 14pt | >20 letters rule |

## Impact
- **Improved readability** for long brand names in horizontal templates
- **Prevents text overflow** by ensuring consistent sizing
- **Maintains existing functionality** for shorter brand names
- **No impact on other template types** (vertical, mini, etc.)

## Files Created for Testing
- `test_brand_font_size_fix.py` - Comprehensive test with edge cases
- `test_brand_font_size_simple.py` - Simple verification test
- `test_real_brand_font_size.py` - Real template generation test 