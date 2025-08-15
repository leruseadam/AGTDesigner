# Non-Classic Types Fix Summary

## Overview

This document summarizes the comprehensive fixes implemented for non-classic types in the template processor. The previous implementation was missing critical logic for handling non-classic types (edibles, tinctures, topicals, etc.), which caused them to display incorrectly or not at all.

## Issues Identified

1. **Missing Brand Handling**: Non-classic types weren't getting proper brand markers and font sizing
2. **Missing Font Sizing**: Non-classic type content wasn't getting appropriate font sizes
3. **Missing Marker Processing**: Non-classic types weren't getting proper marker wrapping
4. **Missing Post-Processing**: Non-classic types weren't getting proper formatting in the final document

## Fixes Implemented

### 1. Enhanced Brand Handling for Non-Classic Types

**Location**: `src/core/generation/template_processor.py` - Lines 1886-1920

**What was added**:
- Comprehensive marker wrapping for non-classic types
- Ensures all fields get proper markers for font sizing
- Applies PRODUCTBRAND_CENTER, DESC, PRICE, RATIO, and WEIGHTUNITS markers

**Code added**:
```python
# CRITICAL: For non-classic types, ensure proper font sizing and marker handling
# This was missing from the current implementation and is key for non-classic types to work properly
if product_type not in classic_types:
    # For non-classic types, ensure all fields get proper markers for font sizing
    if label_context.get('ProductBrand'):
        # Ensure ProductBrand gets proper PRODUCTBRAND_CENTER marker for centering
        if not is_already_wrapped(label_context['ProductBrand'], 'PRODUCTBRAND_CENTER'):
            label_context['ProductBrand'] = wrap_with_marker(label_context['ProductBrand'], 'PRODUCTBRAND_CENTER')
        if not is_already_wrapped(label_context['ProductBrand_Center'], 'PRODUCTBRAND_CENTER'):
            label_context['ProductBrand_Center'] = wrap_with_marker(label_context['ProductBrand_Center'], 'PRODUCTBRAND_CENTER')
    
    # For non-classic types, ensure Description gets proper DESC marker
    if label_context.get('DescAndWeight'):
        if not is_already_wrapped(label_context['DescAndWeight'], 'DESC'):
            label_context['DescAndWeight'] = wrap_with_marker(label_context['DescAndWeight'], 'DESC')
    
    # For non-classic types, ensure Price gets proper PRICE marker
    if label_context.get('Price'):
        if not is_already_wrapped(label_context['Price'], 'PRICE'):
            label_context['Price'] = wrap_with_marker(label_context['Price'], 'PRICE')
    
    # For non-classic types, ensure ProductStrain gets proper PRODUCTSTRAIN marker
    if label_context.get('ProductStrain'):
        if not is_already_wrapped(label_context['ProductStrain'], 'PRODUCTSTRAIN'):
            label_context['ProductStrain'] = wrap_with_marker(label_context['ProductStrain'], 'PRODUCTSTRAIN')
    
    # For non-classic types, ensure Ratio gets proper RATIO marker
    if label_context.get('Ratio'):
        if not is_already_wrapped(label_context['Ratio'], 'RATIO'):
            label_context['Ratio'] = wrap_with_marker(label_context['Ratio'], 'RATIO')
    
    # For non-classic types, ensure WeightUnits gets proper WEIGHTUNITS marker
    if label_context.get('WeightUnits'):
        if not is_already_wrapped(label_context['WeightUnits'], 'WEIGHTUNITS'):
            label_context['WeightUnits'] = wrap_with_marker(label_context['WeightUnits'], 'WEIGHTUNITS')
    
    self.logger.debug(f"Applied comprehensive marker wrapping for non-classic type: {product_type}")
```

### 2. Enhanced Post-Processing for Non-Classic Types

**Location**: `src/core/generation/template_processor.py` - Lines 2520-2530

**What was added**:
- Call to new method `_ensure_non_classic_types_font_sizing(doc)`
- Ensures non-classic types get proper font sizing after template rendering

**Code added**:
```python
# CRITICAL: Ensure non-classic types get proper font sizing
# This was missing and is essential for non-classic types to display correctly
self._ensure_non_classic_types_font_sizing(doc)
```

### 3. New Method: `_ensure_non_classic_types_font_sizing`

**Location**: `src/core/generation/template_processor.py` - Lines 2530-2580

**What it does**:
- Identifies non-classic types in the document
- Applies proper font sizing and formatting
- Ensures all text is properly formatted for non-classic types

**Key features**:
- Detects non-classic product types
- Processes all tables and paragraphs
- Applies specialized formatting for non-classic types

### 4. New Method: `_apply_non_classic_type_formatting`

**Location**: `src/core/generation/template_processor.py` - Lines 2580-2650

**What it does**:
- Applies specific formatting for non-classic types
- Centers brand names
- Applies proper font sizing for different field types
- Ensures Arial Bold formatting

**Key features**:
- Brand name centering
- Description font sizing
- Price font sizing
- Ratio font sizing
- Comprehensive Arial Bold enforcement

### 5. Enhanced Marker Detection for Non-Classic Types

**Location**: `src/core/generation/template_processor.py` - Lines 2750-2760

**What was added**:
- Check for non-classic type markers when no standard markers are found
- Ensures non-classic types get proper marker processing

**Code added**:
```python
# CRITICAL: For non-classic types, ensure proper marker handling
# This was missing and is essential for non-classic types to display correctly
if not found_markers:
    # Check if this is a non-classic type that needs marker processing
    found_markers = self._check_for_non_classic_type_markers(paragraph, markers)
```

### 6. New Method: `_check_for_non_classic_type_markers`

**Location**: `src/core/generation/template_processor.py` - Lines 2700-2750

**What it does**:
- Detects content that should be processed as markers for non-classic types
- Identifies brand, description, price, and ratio content
- Returns appropriate marker types for processing

**Key features**:
- Brand content detection
- Description content detection
- Price content detection
- Ratio content detection
- Product type awareness

### 7. Enhanced Font Sizing for Non-Classic Types

**Location**: `src/core/generation/template_processor.py` - Lines 3650-3700

**What was added**:
- Enhanced handling for non-classic types in font sizing
- Specialized font sizing for different marker types
- Product type awareness in font sizing calculations

**Code added**:
```python
# CRITICAL: Enhanced handling for non-classic types
# This was missing and is essential for non-classic types to display correctly
current_product_type = None
if hasattr(self, 'current_product_type'):
    current_product_type = self.current_product_type
elif hasattr(self, 'label_context') and 'ProductType' in self.label_context:
    current_product_type = self.label_context['ProductType']

if current_product_type:
    current_product_type = current_product_type.lower()
    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", 
                   "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
    is_non_classic = current_product_type not in classic_types
    
    if is_non_classic:
        self.logger.debug(f"Applying non-classic type font sizing for marker '{marker_name}' with content '{content[:50]}...'")
        
        # For non-classic types, use specialized font sizing
        if marker_name == 'PRODUCTBRAND_CENTER':
            # Brand names for non-classic types get larger font sizes
            return get_font_size_by_marker(content, 'PRODUCTBRAND_CENTER', self.template_type, self.scale_factor, current_product_type)
        elif marker_name == 'DESC':
            # Descriptions for non-classic types get appropriate sizing
            return get_font_size_by_marker(content, 'DESC', self.template_type, self.scale_factor, current_product_type)
        elif marker_name == 'PRICE':
            # Prices for non-classic types get appropriate sizing
            return get_font_size_by_marker(content, 'PRICE', self.template_type, self.scale_factor, current_product_type)
        elif marker_name == 'RATIO':
            # Ratios for non-classic types get appropriate sizing
            return get_font_size_by_marker(content, 'RATIO', self.template_type, self.scale_factor, current_product_type)
```

## How the Fixes Work Together

1. **Context Building**: Non-classic types now get proper marker wrapping during context building
2. **Template Rendering**: Markers are properly processed during template rendering
3. **Post-Processing**: Non-classic types get specialized font sizing and formatting
4. **Font Sizing**: Enhanced font sizing calculations consider product type
5. **Marker Detection**: Improved marker detection for non-classic type content

## Expected Results

After implementing these fixes, non-classic types should:

1. **Display Properly**: All content should be visible and properly formatted
2. **Have Correct Font Sizes**: Brand names, descriptions, prices, and ratios should have appropriate font sizes
3. **Be Properly Centered**: Brand names should be centered as intended
4. **Have Arial Bold Formatting**: All text should be Arial Bold as required
5. **Work Across All Templates**: Mini, vertical, horizontal, and double templates should all work correctly

## Testing Recommendations

1. **Test with Edibles**: Verify edibles display with proper brand names and formatting
2. **Test with Tinctures**: Verify tinctures display with proper descriptions and ratios
3. **Test with Topicals**: Verify topicals display with proper formatting
4. **Test Across Templates**: Verify all template types work correctly with non-classic types
5. **Test Font Sizing**: Verify font sizes are appropriate for different content types

## Files Modified

- `src/core/generation/template_processor.py` - Multiple sections enhanced for non-classic types

## Dependencies

- `src/core/generation/unified_font_sizing.py` - Font sizing system
- `src/core/formatting/markers.py` - Marker wrapping utilities
- `src/core/constants.py` - CLASSIC_TYPES definition

## Conclusion

These comprehensive fixes address all the missing functionality for non-classic types that was present in the old working template processor. Non-classic types should now display correctly with proper formatting, font sizing, and marker processing across all template types.
