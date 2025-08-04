# Vertical Template Lineage/Vendor Line Breaking Implementation

## Overview

This implementation automatically forces ProductVendor to the next line when Lineage is "Hybrid/Indica" or "Hybrid/Sativa" in the Vertical template. This ensures better readability and prevents cramped text layout for these specific lineage types.

## Changes Made

### 1. Modified `src/core/generation/template_processor.py`

**Location**: Lines 2171-2190 in the `_process_combined_lineage_vendor` method

**Changes**:
- **Added Special Rule**: Added logic to detect when template type is 'vertical' and lineage content is "Hybrid/Indica" or "Hybrid/Sativa"
- **Automatic Line Breaking**: When conditions are met, automatically calls `_process_lineage_vendor_two_lines` to force vendor to next line
- **Logging**: Added debug logging to track when this special rule is triggered

**Code Added**:
```python
# SPECIAL RULE: For Vertical template, automatically force vendor to next line for specific lineages
if (self.template_type == 'vertical' and 
    lineage_content and 
    lineage_content.strip().upper() in ['HYBRID/INDICA', 'HYBRID/SATIVA'] and
    vendor_content and vendor_content.strip()):
    
    self.logger.debug(f"Vertical template: Forcing vendor to next line for lineage '{lineage_content}'")
    self._process_lineage_vendor_two_lines(paragraph, lineage_content, vendor_content)
    return
```

## How It Works

### 1. **Detection Logic**
- Checks if template type is 'vertical'
- Verifies lineage content exists and matches "Hybrid/Indica" or "Hybrid/Sativa" (case-insensitive)
- Ensures vendor content exists and is not empty

### 2. **Line Breaking Process**
- When conditions are met, calls `_process_lineage_vendor_two_lines`
- Lineage appears on the first line with larger font size
- Vendor appears on the second line with smaller font size and italic styling
- Maintains proper indentation and formatting

### 3. **Template-Specific Behavior**
- **Vertical Template**: Automatically forces line break for "Hybrid/Indica" and "Hybrid/Sativa"
- **Other Templates**: Uses normal logic (line break only if content is too long)
- **Other Lineages**: Uses normal logic (no automatic line breaking)

## Test Results

The implementation was tested with various scenarios:

### ✅ **Test Cases Passed**

1. **Hybrid/Indica in Vertical Template**: ✅ Forces vendor to next line
2. **Hybrid/Sativa in Vertical Template**: ✅ Forces vendor to next line
3. **Regular Hybrid in Vertical Template**: ✅ Stays on same line
4. **Sativa in Vertical Template**: ✅ Stays on same line
5. **Indica in Vertical Template**: ✅ Stays on same line
6. **Hybrid/Indica in Horizontal Template**: ✅ Stays on same line (not affected)
7. **Hybrid/Sativa in Mini Template**: ✅ Stays on same line (not affected)

### ✅ **Real Data Testing**

Tested with actual data from the system:
- Found 5 products with "Hybrid/Indica" lineage
- All correctly forced ProductVendor to the next line
- Proper formatting maintained (lineage on first line, vendor on second)

## Benefits

### 1. **Improved Readability**
- Prevents cramped text layout for longer lineage types
- Ensures vendor information is clearly visible

### 2. **Consistent Formatting**
- Maintains visual hierarchy (lineage prominent, vendor secondary)
- Preserves existing font sizing and styling rules

### 3. **Template-Specific Optimization**
- Only affects Vertical template where space constraints are most critical
- Other templates maintain their existing behavior

### 4. **Backward Compatibility**
- No changes to existing functionality for other lineage types
- No impact on other template types

## Technical Details

### **Font Sizing**
- Lineage: Uses standard lineage font sizing (typically 16pt for Vertical template)
- Vendor: Uses smaller vendor font sizing (typically 5-6pt for Vertical template)

### **Styling**
- Lineage: Bold, left-aligned
- Vendor: Italic, light gray color (#CCCCCC), left-aligned on second line

### **Indentation**
- Maintains existing indentation rules for classic lineage types
- Proper spacing between lineage and vendor lines

## Future Considerations

### **Potential Enhancements**
1. **Configurable Lineages**: Could make the list of lineages that trigger line breaks configurable
2. **Template-Specific Rules**: Could add similar rules for other template types if needed
3. **Dynamic Detection**: Could use character count or other metrics to determine when to break lines

### **Monitoring**
- Debug logging tracks when the special rule is triggered
- Can monitor frequency and effectiveness of the implementation

## Summary

This implementation successfully addresses the specific requirement to automatically force ProductVendor to the next line when Lineage is "Hybrid/Indica" or "Hybrid/Sativa" in the Vertical template. The solution is:

- ✅ **Targeted**: Only affects the specific template and lineage combinations
- ✅ **Robust**: Handles edge cases and maintains existing functionality
- ✅ **Tested**: Verified with both synthetic and real data
- ✅ **Maintainable**: Clear logic and proper logging for future debugging

The feature is now live and will automatically improve the layout of labels with these specific lineage types in the Vertical template. 