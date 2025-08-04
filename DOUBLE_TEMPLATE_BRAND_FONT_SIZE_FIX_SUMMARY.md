# Double Template Brand Font Size Fix

## Problem
Brand names in the double template with words longer than 9 characters were appearing too large and potentially overflowing the label space.

## Solution
Added a special rule in the unified font sizing system to automatically reduce font size to 8pt for brand names in the double template when any single word contains more than 9 characters.

## Implementation

### File Modified
- `src/core/generation/unified_font_sizing.py`

### Changes Made
Added a new special rule in the `get_font_size` function:

```python
# Special rule: If any brand name in double template has more than 9 letters in single word, reduce font to 8pt
if field_type.lower() == 'brand' and orientation.lower() == 'double':
    words = text.split()
    for word in words:
        if len(word) > 9:
            final_size = 8 * scale_factor
            logger.debug(f"Special double template brand rule: text='{text}' has word '{word}' with {len(word)} chars > 9, forcing 8pt font")
            return Pt(final_size)
```

### Rule Details
- **Trigger**: Any brand name in double template with a word containing more than 9 characters
- **Action**: Reduces font size to 8pt
- **Scope**: Only applies to double template brand names
- **Other templates**: Unaffected by this rule

## Test Results

### Test Cases
1. **"Supercalifragilisticexpialidocious"** → 8pt ✅
2. **"VeryLongBrandName"** → 8pt ✅
3. **"Short Brand"** → 9pt (normal sizing) ✅
4. **"Short VeryLongBrandName"** → 8pt ✅
5. **"VeryLongBrandName Short"** → 8pt ✅
6. **"Multiple VeryLongBrandNames Here"** → 8pt ✅
7. **Empty string** → 14pt (default) ✅

### Other Template Types
- **Horizontal template**: "VeryLongBrandName" → 16pt (unaffected) ✅
- **Vertical template**: "VeryLongBrandName" → 14pt (unaffected) ✅
- **Mini template**: "VeryLongBrandName" → 12pt (unaffected) ✅

## Benefits
1. **Prevents overflow**: Long brand names no longer overflow label boundaries
2. **Maintains readability**: 8pt font is still readable while fitting in the space
3. **Template-specific**: Only affects double template, preserving existing behavior for other templates
4. **Automatic**: No manual intervention required - rule applies automatically

## Integration
The rule integrates seamlessly with the existing font sizing system:
- Uses the same `get_font_size` function that all templates use
- Respects scale factors for consistent sizing
- Includes proper logging for debugging
- Maintains backward compatibility

## Files Created
- `test_double_brand_font_size.py` - Test script to verify the rule works correctly
- `DOUBLE_TEMPLATE_BRAND_FONT_SIZE_FIX_SUMMARY.md` - This documentation 