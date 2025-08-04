# Double Template Brand Centering Fix Summary

## Issue
The double template was not centering brand names for non-classic types, unlike the vertical and horizontal templates which already had this functionality.

## Root Cause
The issue was that the `PRODUCTBRAND_CENTER` markers were being processed and removed during the DocxTemplate rendering phase, before the post-processing phase could apply the centering logic. This meant that the centering logic in the marker processing was never reached.

## Solution
Implemented a post-processing step specifically for the double template that:

1. **Detects non-classic product types**: Uses the product type from the record to determine if centering should be applied
2. **Applies centering directly to paragraphs**: Instead of relying on markers, directly sets paragraph alignment for paragraphs containing brand content
3. **Preserves classic type behavior**: Classic types (flower, pre-roll, concentrate, etc.) are not centered, maintaining the existing behavior

## Implementation Details

### 1. Updated `_build_label_context` method
- Modified the logic to use `PRODUCTBRAND_CENTER` markers for non-classic types in the double template
- Now treats double template the same as vertical and horizontal templates for brand centering

### 2. Added `_apply_brand_centering_for_double_template` method
- New method that applies centering logic specifically for the double template
- Takes product type as a parameter to determine if centering should be applied
- Only centers paragraphs containing brand content for non-classic types

### 3. Updated `_post_process_and_replace_content` method
- Added call to the new brand centering method for double template
- Passes the current record's product type to the centering method

### 4. Updated `_process_chunk` method
- Sets `current_record` attribute during processing to make product type available for centering logic

## Testing
Created and ran comprehensive tests that verify:
- ✅ Non-classic types (edible) have centered brand names
- ✅ Classic types (flower) have left-aligned brand names (default alignment)
- ✅ The logic correctly identifies product types and applies appropriate centering

## Result
The double template now has the same brand centering behavior as the vertical and horizontal templates:
- **Non-classic types**: Brand names are centered
- **Classic types**: Brand names use default alignment (left-aligned)

This ensures consistent behavior across all template types for brand name positioning. 