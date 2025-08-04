# THC/CBD Percentage Right-Alignment Fix

## Problem
The user requested to right-align the THC and CBD percentage values in the labels so that the '%' symbols align vertically. Currently, the percentages were left-aligned, which made the visual alignment inconsistent.

## Root Cause
The existing `format_thc_cbd_vertical_alignment` function in `src/core/generation/template_processor.py` was using a fixed number of spaces (3 spaces) for alignment, which didn't account for the varying lengths of percentage values.

## Solution
I've implemented a comprehensive solution that automatically calculates the proper spacing needed to right-align percentage values based on the maximum width of all percentage values in the content.

### 1. Enhanced `format_thc_cbd_vertical_alignment` Function
- **File**: `src/core/generation/template_processor.py` lines 2213-2332
- **Changes**:
  - Added two-pass algorithm: first pass collects all percentage values to determine maximum width
  - Second pass formats each line with proper right-alignment spacing
  - Calculates spacing dynamically based on the difference between max width and current percentage length
  - Preserves existing spaces after colons (THC:, CBD:)
  - Handles both single-line and multi-line THC/CBD formats
  - Supports additional cannabinoids (CBC, CBG, etc.) without affecting their alignment

### 2. Algorithm Details
```python
# First pass: determine maximum percentage width
max_percentage_width = max(len(percentage) for percentage in all_percentages)

# Second pass: apply right-alignment
spacing_needed = max_percentage_width - len(current_percentage)
spaces = ' ' * max(0, spacing_needed)
formatted_line = f"{label}{spaces}{percentage}%"
```

### 3. Test Cases Verified
- **Same length percentages**: No alignment needed (e.g., "21.0%" and "0.25%" both 4 chars)
- **Different length percentages**: Proper right-alignment (e.g., "24.0%" vs "0.0%")
- **Mixed formats**: Handles THC/CBD with additional cannabinoids
- **Edge cases**: Zero values, single digits, large numbers

### 4. Visual Examples
**Before (left-aligned):**
```
THC: 21.0%
CBD: 0.25%
```

**After (right-aligned):**
```
THC: 21.0%
CBD: 0.25%
```

**Before (left-aligned):**
```
THC: 24.0%
CBD: 0.0%
```

**After (right-aligned):**
```
THC: 24.0%
CBD:  0.0%
```

**Before (left-aligned):**
```
THC: 100.0%
CBD: 0.1%
```

**After (right-aligned):**
```
THC: 100.0%
CBD:   0.1%
```

## Implementation Details

### Key Features
1. **Dynamic Spacing**: Calculates spacing based on actual percentage lengths
2. **Preserves Formatting**: Maintains existing spaces after colons
3. **Multi-line Support**: Handles both single-line and multi-line THC/CBD formats
4. **Extensible**: Supports additional cannabinoids without breaking alignment
5. **Backward Compatible**: Doesn't affect existing functionality

### Template Integration
- Function is automatically called for vertical templates
- Applied during the `_build_label_context` method
- Integrated with existing marker system (`THC_CBD` markers)

### Test Coverage
- Created comprehensive test suite (`test_thc_cbd_right_alignment_fix.py`)
- Tests various percentage length combinations
- Verifies alignment with actual data from the image
- All test cases pass successfully

## Files Modified
1. **`src/core/generation/template_processor.py`**
   - Enhanced `format_thc_cbd_vertical_alignment` function
   - Improved regex patterns to preserve spacing
   - Added dynamic spacing calculation

2. **`test_thc_cbd_right_alignment_fix.py`** (new)
   - Comprehensive test suite
   - Visual alignment verification
   - Edge case testing

## Result
✅ **All percentage values are now properly right-aligned**
✅ **'%' symbols align vertically for better visual consistency**
✅ **Dynamic spacing adapts to varying percentage lengths**
✅ **Backward compatibility maintained**
✅ **Comprehensive test coverage**

This fix ensures that THC/CBD percentage values in vertical templates are properly right-aligned, providing a cleaner and more professional appearance for the product labels. 