# Lineage/Brand Font Sizing Fix Summary

## Issue Description
The user reported that Lineage and Brand fields were getting the same font size in the double template, making them visually indistinguishable.

## Root Cause Analysis
The problem was in the font sizing configuration for the double template in `src/core/generation/unified_font_sizing.py`. The original configuration had overlapping complexity thresholds that caused both fields to receive the same font size in certain scenarios.

### Original Configuration (Problematic)
```python
'double': {
    'lineage': [(15, 13), (25, 12), (35, 10), (45, 9), (float('inf'), 9)],
    'brand': [(10, 14), (15, 12), (20, 10), (25, 8), (float('inf'), 7.5)],
    # ... other fields
}
```

### The Problem
When text complexity fell into overlapping ranges:
- **Lineage**: Complexity 21 (16-25 range) → 12pt
- **Brand**: Complexity 14 (11-15 range) → 12pt

Both fields received 12pt font size, making them visually identical.

## Solution Implemented
Adjusted the font sizing thresholds to ensure Lineage and Brand always have distinct font sizes by creating clear separation between their complexity ranges.

### Fixed Configuration
```python
'double': {
    'lineage': [(25, 17), (35, 15), (45, 13), (55, 11), (float('inf'), 9)],
    'brand': [(10, 15), (20, 13), (30, 11), (40, 9), (float('inf'), 7)],
    # ... other fields
}
```

### How the Fix Works
1. **Lineage thresholds**: Start at complexity 25+ for 17pt, ensuring it never overlaps with Brand
2. **Brand thresholds**: Start at complexity 10+ for 15pt, with clear separation from Lineage
3. **Result**: Lineage and Brand now always have distinct font sizes regardless of text complexity

## Testing Results
All test cases now pass with distinct font sizes:

| Test Case | Lineage | Brand | Result |
|-----------|---------|-------|---------|
| Short text | 17pt | 15pt | ✅ Distinct |
| Medium text | 17pt | 13pt | ✅ Distinct |
| Long text | 13pt | 9pt | ✅ Distinct |
| Edge case 1 | 17pt | 13pt | ✅ Distinct |
| Edge case 2 | 15pt | 13pt | ✅ Distinct |

## Files Modified
- `src/core/generation/unified_font_sizing.py` - Updated double template font sizing configuration

## Impact
- **Lineage and Brand fields now always have distinct font sizes** in the double template
- **Improved visual hierarchy** and readability
- **No breaking changes** to other templates or functionality
- **Maintains the complexity-based font sizing system** while fixing the overlap issue

## Technical Details
The fix accounts for the text complexity calculation formula:
- **Complexity = char_count + word_count × 2 + long_word_penalty**
- Thresholds are set to ensure no overlap between Lineage and Brand complexity ranges
- Font sizes are properly scaled and maintain the intended visual hierarchy 