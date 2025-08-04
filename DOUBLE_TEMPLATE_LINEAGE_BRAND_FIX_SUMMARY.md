# Double Template Lineage and Product Brand Fix Summary

## Issue
The double template was missing lineage and product brand content in the rendered labels, even though the data was being processed correctly.

## Root Cause
The double template was missing the `{{Label1.ProductBrand}}` placeholder in the original template file. The template only contained:
- `{{Label1.Lineage}}`
- `{{Label1.ProductStrain}}`

But was missing:
- `{{Label1.ProductBrand}}`

This caused the product brand data to be processed correctly but not rendered in the final template.

## Solution
Modified the `_expand_template_to_4x3_fixed_double` method in `src/core/generation/template_processor.py` to automatically add the missing `{{Label1.ProductBrand}}` placeholder during template expansion.

### Changes Made

**File**: `src/core/generation/template_processor.py`
**Method**: `_expand_template_to_4x3_fixed_double`
**Lines**: 270-295

Added logic to:
1. Check if ProductBrand placeholder is missing from the template
2. Find the position after the Lineage placeholder
3. Insert the ProductBrand placeholder in the correct location
4. Handle split placeholders (where `{{Label1.Lineage}}` is split across multiple text elements)

### Code Changes

```python
# Add ProductBrand placeholder if it doesn't exist
cell_text = ''
for t in tc.iter(qn('w:t')):
    if t.text:
        cell_text += t.text
        if 'Label1' in t.text:
            t.text = t.text.replace('Label1', f'Label{cnt}')

# If ProductBrand placeholder is missing, add it
if '{{Label1.ProductBrand}}' not in cell_text and 'ProductBrand' not in cell_text:
    # Since placeholders are split across multiple text elements, we need to find the right position
    text_elements = list(tc.iter(qn('w:t')))
    lineage_end_index = -1
    
    # Find where the Lineage placeholder ends
    for i, t in enumerate(text_elements):
        if t.text and 'Lineage' in t.text:
            # Found the Lineage text element, look for the closing }}
            for j in range(i, len(text_elements)):
                if text_elements[j].text and '}}' in text_elements[j].text:
                    lineage_end_index = j
                    break
            break
    
    if lineage_end_index >= 0:
        # Insert ProductBrand placeholder after the Lineage placeholder
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        
        # Create a new text element for ProductBrand
        new_text = OxmlElement('w:t')
        new_text.text = f'\n{{{{Label{cnt}.ProductBrand}}}}'
        
        # Insert after the lineage end element
        lineage_end_element = text_elements[lineage_end_index]
        lineage_end_element.getparent().insert(
            lineage_end_element.getparent().index(lineage_end_element) + 1, 
            new_text
        )
```

## Testing
Created comprehensive test script `test_double_template_lineage_brand.py` that verifies:
1. Lineage data is properly processed and rendered
2. Product brand data is properly processed and rendered
3. Template expansion works correctly
4. All placeholders are properly replaced with actual data

## Results
✅ **Lineage is now working**: `•  HYBRID` and `•  SATIVA` appear correctly in cells
✅ **Product brand is now working**: `Test Brand 1` and `Test Brand 2` appear correctly in cells  
✅ **Product strain is working**: `Test Strain 1` and `Test Strain 2` appear correctly in cells
✅ **Template expansion works**: All 12 labels (4x3 grid) are properly generated

## Impact
- Double template now displays lineage and product brand information correctly
- Maintains backward compatibility with existing templates
- Automatically fixes missing placeholders during template expansion
- No manual template file modifications required 