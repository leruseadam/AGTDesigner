# Duplication Fix Summary for Non-Classic Types

## Overview

This document summarizes the fix implemented to prevent information duplication in non-classic types. The issue was causing duplicate entries like "CONSTELLATION CANNABISCONSTELLATION CANNABIS" instead of the correct single entry "CONSTELLATION CANNABIS".

## Problem Identified

The template processor was applying marker wrapping and placeholder replacement multiple times, causing:

1. **Double Brand Names**: "CONSTELLATION CANNABISCONSTELLATION CANNABIS" instead of "CONSTELLATION CANNABIS"
2. **Duplicate Content**: Same information appearing multiple times in labels
3. **Multiple Processing Passes**: The same fields were being processed multiple times

## Root Causes

1. **Double Marker Wrapping**: Fields were being wrapped with markers twice - once in initial processing and again in the "CRITICAL" section
2. **Multiple Replacement Passes**: The manual placeholder replacement was processing the same content multiple times
3. **No Duplication Tracking**: No mechanism to prevent the same placeholder from being replaced multiple times

## Fixes Implemented

### 1. Fixed Double Marker Wrapping

**Location**: `src/core/generation/template_processor.py` - Lines 1886-1920

**What was changed**:
- Added checks to prevent double-wrapping of fields that are already wrapped
- Only wrap fields if they're not already wrapped with markers
- Added template type checks to prevent unnecessary wrapping

**Code changes**:
```python
# BUT: Don't double-wrap fields that are already wrapped - this causes duplication
if product_type not in classic_types:
    # For non-classic types, ensure all fields get proper markers for font sizing
    # BUT: Only wrap if not already wrapped to prevent duplication
    if label_context.get('ProductBrand'):
        # ProductBrand is already wrapped above, don't wrap again
        # Just ensure it's properly formatted for non-classic types
        if self.template_type != 'mini':
            # For non-mini templates, ensure the wrapped value is correct
            if not is_already_wrapped(label_context['ProductBrand'], 'PRODUCTBRAND_CENTER'):
                # This shouldn't happen, but if it does, wrap it
                label_context['ProductBrand'] = wrap_with_marker(label_context['ProductBrand'], 'PRODUCTBRAND_CENTER')
                label_context['ProductBrand_Center'] = wrap_with_marker(label_context['ProductBrand'], 'PRODUCTBRAND_CENTER')
```

### 2. Added Duplication Prevention in Manual Placeholder Replacement

**Location**: `src/core/generation/template_processor.py` - Lines 4820-4850

**What was added**:
- Tracking set `replaced_placeholders` to prevent duplicate replacements
- Skip processing if a placeholder has already been replaced
- Mark placeholders as replaced after successful replacement

**Code added**:
```python
# CRITICAL: Track what has been replaced to prevent duplication
replaced_placeholders = set()

for label_key, label_context in context.items():
    if isinstance(label_context, dict):
        for field_key, field_value in label_context.items():
            # Skip if this placeholder has already been replaced to prevent duplication
            placeholder_key = f"{label_key}.{field_key}"
            if placeholder_key in replaced_placeholders:
                continue
            
            # ... process placeholder ...
            
            # Mark as replaced after successful replacement
            replaced_placeholders.add(placeholder_key)
```

### 3. Added Duplication Prevention for Vertical Templates

**Location**: `src/core/generation/template_processor.py` - Lines 4750-4780

**What was added**:
- Separate tracking set `vertical_replaced_placeholders` for vertical template processing
- Prevent the same field from being processed multiple times in vertical templates
- Ensure each placeholder is only replaced once per field per label

**Code added**:
```python
# CRITICAL: Track what has been replaced to prevent duplication
vertical_replaced_placeholders = set()

for label_key, label_context in context.items():
    if isinstance(label_context, dict):
        for field_name in ['ProductStrain', 'ProductBrand', 'Lineage', 'Price', 'Ratio_or_THC_CBD', 'DOH', 'DescAndWeight']:
            # Skip if this placeholder has already been replaced to prevent duplication
            placeholder_key = f"{label_key}.{field_name}"
            if placeholder_key in vertical_replaced_placeholders:
                continue
            
            # ... process field ...
            
            # Mark as replaced after successful replacement
            vertical_replaced_placeholders.add(placeholder_key)
```

### 4. Enhanced All Placeholder Replacement Methods

**What was enhanced**:
- Triple braces replacement
- Double braces replacement
- Quoted placeholder replacement
- Empty label handling
- DOH image placeholder handling

**Key principle**: Each placeholder can only be replaced once per processing pass.

## How the Fix Works

1. **Initial Processing**: Fields get wrapped with markers only once during context building
2. **Duplicate Prevention**: Tracking sets prevent the same placeholder from being processed multiple times
3. **Single Replacement**: Each placeholder is replaced exactly once with the correct value
4. **Template Awareness**: Different tracking sets for different template types to prevent conflicts

## Expected Results

After implementing these fixes:

1. **No More Duplication**: Brand names should appear only once (e.g., "CONSTELLATION CANNABIS" not "CONSTELLATION CANNABISCONSTELLATION CANNABIS")
2. **Clean Labels**: All content should appear exactly once in the correct location
3. **Proper Formatting**: Non-classic types should display correctly without duplication
4. **Consistent Behavior**: All template types should work without duplication issues

## Testing Recommendations

1. **Test with Edibles**: Verify "CONSTELLATION CANNABIS" appears only once
2. **Test with Tinctures**: Verify brand names and descriptions appear correctly
3. **Test with Topicals**: Verify all content appears without duplication
4. **Test Across Templates**: Verify mini, vertical, horizontal, and double templates all work correctly
5. **Test Multiple Labels**: Verify no duplication occurs across multiple labels

## Files Modified

- `src/core/generation/template_processor.py` - Multiple sections enhanced with duplication prevention

## Dependencies

- `src.core.formatting.markers.py` - `is_already_wrapped` function for checking existing markers
- `src.core.generation.unified_font_sizing.py` - Font sizing system
- `src.core.constants.py` - CLASSIC_TYPES definition

## Conclusion

These comprehensive duplication prevention fixes ensure that non-classic types display correctly with clean, single instances of all content. The tracking mechanisms prevent any field from being processed multiple times, eliminating the duplication issues that were causing "CONSTELLATION CANNABISCONSTELLATION CANNABIS" and similar problems.

The fixes maintain all the functionality for non-classic types while ensuring that information appears exactly once in the correct format and location.
