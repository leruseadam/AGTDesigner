# JointRatio Extraction Fix Summary

## Issue
The `JointRatio` column was showing incorrect values like "28.0g" instead of the proper format like "1g x 28 Pack". The system was trying to read from a non-existent "Joint Ratio" column in the Excel file.

## Root Cause Analysis
1. **No "Joint Ratio" Column**: The Excel file does not contain a separate "Joint Ratio" column
2. **Joint Ratio Data in Product Name**: The joint ratio information is embedded in the `Product Name*` field
3. **Incorrect Fallback Logic**: When no "Joint Ratio" column was found, the system generated simple weight values instead of extracting from the product name

## Solution
Updated the JointRatio processing logic in `src/core/data/excel_processor.py` to:

### 1. Extract Joint Ratio from Product Name
Instead of looking for a non-existent "Joint Ratio" column, the system now extracts joint ratio information from the `Product Name*` field using regex patterns.

### 2. Handle Multiple Formats
The extraction function handles various joint ratio formats:
- **Pattern 1**: "weight x count Pack" (e.g., "0.5g x 2 Pack", ".75g x 5 Pack")
- **Pattern 2**: "weight x count" (e.g., "0.5g x 2", ".75g x 5")  
- **Pattern 3**: "weight only" (e.g., "1g", "0.5g", ".75g")

### 3. Fix Decimal Weight Handling
Updated regex patterns to properly handle decimal weights that start with a dot:
- **Before**: `r'(\d+\.?\d*g)'` - missed `.75g` (matched `75g` instead)
- **After**: `r'(\d*\.?\d+g)'` - correctly matches `.75g`, `0.5g`, `1g`

## Code Changes

### Updated JointRatio Processing Logic
```python
# Extract joint ratio from Product Name since there's no separate "Joint Ratio" column
def extract_joint_ratio_from_name(product_name):
    if pd.isna(product_name) or str(product_name).strip() == '':
        return ''
    
    product_name_str = str(product_name)
    
    # Pattern 1: "weight x count Pack" (e.g., "0.5g x 2 Pack", ".75g x 5 Pack")
    pattern1 = r'(\d*\.?\d+g)\s*x\s*(\d+)\s*Pack'
    match1 = re.search(pattern1, product_name_str, re.IGNORECASE)
    if match1:
        weight = match1.group(1)
        count = match1.group(2)
        return f"{weight} x {count} Pack"
    
    # Pattern 2: "weight x count" (e.g., "0.5g x 2", ".75g x 5")
    pattern2 = r'(\d*\.?\d+g)\s*x\s*(\d+)'
    match2 = re.search(pattern2, product_name_str, re.IGNORECASE)
    if match2:
        weight = match2.group(1)
        count = match2.group(2)
        return f"{weight} x {count}"
    
    # Pattern 3: Just weight (e.g., "1g", "0.5g", ".75g")
    pattern3 = r'(\d*\.?\d+g)'
    match3 = re.search(pattern3, product_name_str, re.IGNORECASE)
    if match3:
        weight = match3.group(1)
        return weight
    
    return ''
```

## Test Results

### Before Fix
- ❌ "Blueberry Banana Pie Flavour Stix Infused Pre-Roll by Dank Czar - .75g x 5 Pack" → "75g x 5 Pack" (incorrect)
- ❌ "Peach Rings Flavour Stix Infused Pre-Roll by Dank Czar - .75g" → "75g" (incorrect)

### After Fix
- ✅ "Blueberry Banana Pie Flavour Stix Infused Pre-Roll by Dank Czar - .75g x 5 Pack" → ".75g x 5 Pack" (correct)
- ✅ "Peach Rings Flavour Stix Infused Pre-Roll by Dank Czar - .75g" → ".75g" (correct)
- ✅ "Gelato Live Resin Infused Pre-Roll by Dabstract - 0.5g x 2 Pack" → "0.5g x 2 Pack" (correct)
- ✅ "Forbidden Fruit Core Flower Pre-Roll by Phat Panda - 1g" → "1g" (correct)

## Files Modified
1. `src/core/data/excel_processor.py` - Updated JointRatio processing logic
2. `test_joint_ratio_extraction.py` - Created test script to verify extraction
3. `debug_joint_ratio_columns.py` - Created debug script to analyze column structure
4. `debug_joint_ratio_simple.py` - Created debug script to analyze Excel file directly

## Impact
- **Fixed**: JointRatio now correctly extracts from Product Name field
- **Improved**: Handles decimal weights starting with dot (e.g., ".75g")
- **Enhanced**: Supports multiple joint ratio formats (Pack, count, weight-only)
- **Maintained**: Fallback logic for products without joint ratio info

## Deployment
Changes have been committed and pushed to GitHub:
- Commit: `fbc8d26`
- Message: "Fix JointRatio extraction - extract from Product Name instead of non-existent column, handle decimal weights like .75g"

The fix is ready for deployment to PythonAnywhere. 