# LINEAGE GENERATION FIX

## Problem
Manual lineage dropdown changes (e.g., changing "HYBRID" to "HYBRID/INDICA") were not being reflected in generated tags. The tags would still show "HYBRID" instead of "HYBRID/INDICA" in the final Word document.

## Root Cause
The issue was a disconnect between the frontend lineage updates and the tag generation process:

1. **Frontend**: Lineage dropdown changes updated `tag.lineage` and `tag.Lineage` in tag objects
2. **Generation**: Used `persistentSelectedTags` (just tag names as strings)
3. **Backend**: Looked up tags by name and got original lineage data (without manual changes)

## Solution

### Frontend Changes (`static/js/main.js`)
**Modified the generation process to send full tag objects with updated lineage:**

```javascript
// CRITICAL FIX: Collect full tag data with updated lineage for generation
const selectedTagObjects = [];
for (const tagName of checkedTags) {
    // Find the tag in the current state with updated lineage
    const tagWithUpdatedLineage = this.state.tags.find(t => 
        (t['Product Name*'] === tagName) || (t.ProductName === tagName)
    );
    if (tagWithUpdatedLineage) {
        selectedTagObjects.push(tagWithUpdatedLineage);
        console.log(`📝 Using tag with updated lineage: ${tagName} -> ${tagWithUpdatedLineage.lineage || tagWithUpdatedLineage.Lineage}`);
    } else {
        // Fallback: create a basic tag object with just the name
        selectedTagObjects.push({ 'Product Name*': tagName, ProductName: tagName });
        console.log(`⚠️ Tag not found in state, using fallback: ${tagName}`);
    }
}

// Send full tag objects instead of just tag names
body: JSON.stringify({
    selected_tags: selectedTagObjects,  // CRITICAL FIX: Send full tag objects with updated lineage
    template_type: templateType,
    scale_factor: scaleFactor
})
```

### Frontend Changes (`static/js/tags_table.js`)
**Fixed data-lineage attribute updates:**

```javascript
// CRITICAL FIX: Update the data-lineage attribute
tagElement.dataset.lineage = newLineage;
```

### Backend Changes (`app.py`)
**Added logic to handle full tag objects and apply lineage updates:**

```python
# CRITICAL FIX: Handle both tag names (strings) and full tag objects with updated lineage
selected_tags_to_use = selected_tags_from_request

# If selected_tags contains full tag objects (new format), extract tag names and update lineage
if selected_tags_to_use and isinstance(selected_tags_to_use[0], dict):
    logging.info("LINEAGE FIX: Processing full tag objects with updated lineage data")
    tag_names = []
    lineage_updates = {}
    
    for tag_obj in selected_tags_to_use:
        # Extract tag name
        tag_name = tag_obj.get('Product Name*') or tag_obj.get('ProductName', '')
        if tag_name:
            tag_names.append(tag_name)
            
            # Extract updated lineage
            updated_lineage = tag_obj.get('lineage') or tag_obj.get('Lineage', '')
            if updated_lineage:
                lineage_updates[tag_name] = updated_lineage
                logging.info(f"LINEAGE FIX: Tag '{tag_name}' has updated lineage: '{updated_lineage}'")
    
    selected_tags_to_use = tag_names
    
    # Update Excel processor lineage data with manual changes
    if lineage_updates and has_excel_data and excel_processor.df is not None and 'Lineage' in excel_processor.df.columns:
        logging.info("LINEAGE FIX: Applying manual lineage updates to Excel processor data")
        for tag_name, new_lineage in lineage_updates.items():
            # Try different column names for product names
            product_name_columns = ['ProductName', 'Product Name*', 'Product Name']
            for col in product_name_columns:
                if col in excel_processor.df.columns:
                    mask = excel_processor.df[col] == tag_name
                    if mask.any():
                        old_lineage = excel_processor.df.loc[mask, 'Lineage'].iloc[0]
                        excel_processor.df.loc[mask, 'Lineage'] = new_lineage
                        logging.info(f"LINEAGE FIX: Updated '{tag_name}' lineage from '{old_lineage}' to '{new_lineage}'")
                        break
```

## Expected Results

After this fix:
- ✅ **Manual lineage dropdown changes** (e.g., "HYBRID" → "HYBRID/INDICA") are preserved
- ✅ **Generated tags show correct lineage** (e.g., "HYBRID/INDICA" instead of "HYBRID")
- ✅ **Word document displays proper lineage values** matching the dropdown selections
- ✅ **Backward compatibility** maintained for existing tag name-only requests

## Testing Steps

1. **Upload Excel file** with products
2. **Change lineage dropdown** from "HYBRID" to "HYBRID/INDICA" for a product
3. **Select the product** for generation
4. **Generate tags** and download Word document
5. **Verify** the tag shows "HYBRID/INDICA" instead of "HYBRID"

## Files Modified
- `static/js/main.js` - Modified generation process to send full tag objects
- `static/js/tags_table.js` - Fixed data-lineage attribute updates
- `app.py` - Added backend logic to handle full tag objects and apply lineage updates

## Technical Details

The fix ensures that:
1. **Frontend** collects full tag objects with updated lineage from the state
2. **Backend** receives full tag objects and extracts both tag names and lineage updates
3. **Excel processor** is updated with the manual lineage changes before generation
4. **Tag generation** uses the updated lineage data from the Excel processor

This creates a complete data flow from manual dropdown changes to final generated tags.
