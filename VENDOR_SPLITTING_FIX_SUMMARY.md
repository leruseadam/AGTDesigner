# Product Vendor Splitting Fix Summary

## Issue Description
The Product Vendor text was being split up when the combined lineage and vendor content was too long for a single line. Users wanted the Product Vendor to never be split up, and instead have the Lineage break to a new line if it's too long.

## Root Cause
The `_process_combined_lineage_vendor` method was always trying to fit both lineage and vendor content on a single line, which could cause the vendor text to be split or wrapped when the combined content exceeded the available space.

## Problem
- **Single Line Layout**: Always attempted to put lineage and vendor on the same line
- **Vendor Splitting**: When content was too long, vendor text could be split up
- **Poor Readability**: Split vendor names were hard to read and looked unprofessional

## Fixes Implemented

### 1. Added Content Length Detection
**File**: `src/core/generation/template_processor.py`
- Added character limit checks based on template type:
  - Mini template: 25 characters per line
  - Vertical template: 35 characters per line
  - Horizontal/Double templates: 45 characters per line
- Combined content length is calculated before processing

### 2. Implemented Two-Line Layout
**File**: `src/core/generation/template_processor.py`
- Created `_process_lineage_vendor_two_lines` method
- When content is too long, automatically switches to two-line layout:
  - Lineage on first line (left-aligned, bold)
  - Vendor on second line (left-aligned, italic, gray color)
- Preserves all styling and formatting

### 3. Enhanced Processing Logic
**File**: `src/core/generation/template_processor.py`
- Modified `_process_combined_lineage_vendor` to check content length
- Automatically chooses between single-line and two-line layout
- Maintains backward compatibility with existing functionality

## Code Changes

### Content Length Detection
```python
# Check if we need to split to multiple lines due to content length
# Calculate approximate character limits based on template type
if self.template_type == 'mini':
    max_chars_per_line = 25
elif self.template_type == 'vertical':
    max_chars_per_line = 35
else:  # horizontal, double
    max_chars_per_line = 45

# Check if combined content would be too long for one line
combined_length = len(lineage_content or '') + len(vendor_content or '')

if combined_length > max_chars_per_line and vendor_content and vendor_content.strip():
    # Split to two lines: lineage on first line, vendor on second line
    self._process_lineage_vendor_two_lines(paragraph, lineage_content, vendor_content)
    return
```

### Two-Line Layout Method
```python
def _process_lineage_vendor_two_lines(self, paragraph, lineage_content, vendor_content):
    """
    Process lineage and vendor on two separate lines to prevent vendor splitting.
    Lineage goes on the first line, vendor goes on the second line.
    """
    # Clear paragraph and set left alignment
    paragraph.clear()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Add lineage on first line with larger font size
    if lineage_content and lineage_content.strip():
        lineage_run = paragraph.add_run(lineage_content.strip())
        lineage_run.font.name = "Arial"
        lineage_run.font.bold = True
        # ... font sizing logic
    
    # Add line break
    if lineage_content and vendor_content:
        paragraph.add_run("\n")
    
    # Add vendor on second line with smaller font size
    if vendor_content and vendor_content.strip():
        vendor_run = paragraph.add_run(vendor_content.strip())
        vendor_run.font.name = "Arial"
        vendor_run.font.bold = False
        vendor_run.font.italic = True
        vendor_run.font.color.rgb = RGBColor(204, 204, 204)  # Light gray
        # ... font sizing logic
```

## What This Fixes
1. **Prevents Vendor Splitting**: Product Vendor text is never split up
2. **Automatic Layout Selection**: Intelligently chooses single-line or two-line layout
3. **Maintains Readability**: Vendor names remain intact and readable
4. **Preserves Styling**: All existing formatting and styling is maintained
5. **Template-Aware**: Different character limits for different template types

## Example Output

### Before (Vendor Split):
```
HYBRID/INDICA  Industrial LL
C
```

### After (Two-Line Layout):
```
HYBRID/INDICA
Industrial LLC
```

## Testing
- Product Vendor should never be split up in any template
- Long lineage content should automatically trigger two-line layout
- Short content should still use single-line layout
- All styling (bold lineage, italic gray vendor) should be preserved
- Different template types should use appropriate character limits 