# Horizontal Template THC/CBD Same Line Fix Summary

## Issue
The horizontal template was formatting THC/CBD percentages with line breaks, making them appear on separate lines instead of keeping them on the same line as intended.

## Solution
Modified the `format_thc_cbd_bold_labels()` function in `src/core/generation/text_processing.py` to accept a `template_type` parameter and format content differently based on the template type.

## Changes Made

### 1. Updated `format_thc_cbd_bold_labels()` function
- **File**: `src/core/generation/text_processing.py`
- **Change**: Added `template_type='vertical'` parameter
- **Logic**: 
  - For `horizontal` template: Keep THC/CBD on same line with double space separation
  - For `vertical`/`double` templates: Maintain original multi-line format with indented values

### 2. Updated template processor calls
- **File**: `src/core/generation/template_processor.py`
- **Change**: Pass `self.template_type` to `format_thc_cbd_bold_labels()` function
- **Line**: Updated function call to include template type parameter

### 3. Updated pythonanywhere deployment files
- **Files**: 
  - `pythonanywhere_deployment/src/core/generation/text_processing.py`
  - `pythonanywhere_deployment/src/core/generation/template_processor.py`
- **Change**: Applied same modifications to keep deployment files in sync

## Format Examples

### Horizontal Template (Before)
```
THC:
  74.51%
CBD:
  0.15%
```

### Horizontal Template (After)
```
THC: 74.51%  CBD: 0.15%
```

### Vertical Template (Unchanged)
```
THC:
  74.51%
CBD:
  0.15%
```

## Testing
Created `test_horizontal_thc_cbd_formatting.py` to verify:
- Horizontal template keeps THC/CBD on same line
- Vertical template maintains multi-line format
- Various input formats work correctly (percentages, mg values, placeholders)

## Files Modified
1. `src/core/generation/text_processing.py`
2. `src/core/generation/template_processor.py`
3. `pythonanywhere_deployment/src/core/generation/text_processing.py`
4. `pythonanywhere_deployment/src/core/generation/template_processor.py`
5. `test_horizontal_thc_cbd_formatting.py` (new test file)

## Result
Horizontal template now displays THC/CBD percentages on the same line as requested, while maintaining the existing formatting for vertical and double templates. 