# Double Template THC_CBD Font Fix Summary

## Problem
The double template was generating THC_CBD content with 8pt font instead of the configured 6.5pt font. This was happening because the THC_CBD content was being processed as 'ratio' field type instead of 'thc_cbd' field type.

## Root Cause
The issue was in the `_get_template_specific_font_size` function in `src/core/generation/template_processor.py`. When processing THC_CBD content that was marked as 'RATIO' marker, the function was using the 'ratio' field type configuration instead of the 'thc_cbd' field type configuration.

The double template uses `Ratio_or_THC_CBD` as the field name, and when the content contains THC/CBD data, it should be processed as 'thc_cbd' field type, but it was being processed as 'ratio' field type.

## Solution
Modified the `_get_template_specific_font_size` function to detect when RATIO marker content contains THC/CBD data and use the correct field type:

```python
def _get_template_specific_font_size(self, content, marker_name):
    """
    Get font size using the unified font sizing system.
    """
    # Special handling for RATIO marker: if content contains THC/CBD data, use THC_CBD field type
    if marker_name == 'RATIO' and ('THC:' in content or 'CBD:' in content):
        # Use THC_CBD field type for THC/CBD content
        return get_font_size(content, 'thc_cbd', self.template_type, self.scale_factor)
    
    # Use unified font sizing with appropriate complexity type
    complexity_type = 'mini' if self.template_type == 'mini' else 'standard'
    return get_font_size_by_marker(content, marker_name, self.template_type, self.scale_factor)
```

## Results
- **Before**: THC_CBD content was using 5pt font (ratio field type fallback)
- **After**: THC_CBD content now uses 6.5pt font (thc_cbd field type)

## Testing
- Created comprehensive test scripts to verify the fix
- Confirmed that all THC_CBD content now uses the correct 6.5pt font size
- Verified that the fix works for all test cases

## Files Modified
- `src/core/generation/template_processor.py`: Modified `_get_template_specific_font_size` function

## Impact
This fix ensures that THC_CBD content in the double template uses the proper configured font size (6.5pt) instead of the incorrect ratio field type font size (5pt), improving readability and consistency with the unified font sizing system. 