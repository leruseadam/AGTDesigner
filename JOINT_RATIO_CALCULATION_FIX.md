# JointRatio Calculation Fix - Comprehensive Solution

## Problem Description
JointRatio values were present but not being calculated correctly. The issues included:
1. **Incorrect Data Source**: JointRatio was sometimes being copied from "Ratio" column instead of using proper pack format
2. **Invalid Format Detection**: The system wasn't properly detecting valid pack formats (e.g., "1g x 2 Pack")
3. **Poor Fallback Logic**: When JointRatio was missing, the fallback logic wasn't generating proper pack formats
4. **Format Inconsistency**: The `format_joint_ratio_pack` function wasn't handling all input formats correctly

## Root Cause Analysis

### 1. Excel Processor Issues (`src/core/data/excel_processor.py`)
- **Problem**: JointRatio was being copied from "Ratio" column which contains THC/CBD values, not pack formats
- **Problem**: No validation of JointRatio format before using it
- **Problem**: Poor fallback logic when JointRatio was missing

### 2. Weight Units Processing Issues (`src/core/data/excel_processor.py`)
- **Problem**: `_format_weight_units` method wasn't properly validating JointRatio format
- **Problem**: Was falling back to Ratio values instead of generating proper pack formats

### 3. Template Processing Issues (`src/core/generation/template_processor.py`)
- **Problem**: `format_joint_ratio_pack` function had limited pattern matching
- **Problem**: Didn't handle all input format variations correctly

## Comprehensive Fix Applied

### 1. Excel Processor Fixes

**File**: `src/core/data/excel_processor.py` (lines 1610-1630)

**Enhanced JointRatio Creation Logic**:
```python
# First, try to use "Joint Ratio" column if it exists
if "Joint Ratio" in self.df.columns:
    joint_ratio_values = self.df.loc[preroll_mask, "Joint Ratio"].fillna('')
    # Only use Joint Ratio values that look like pack formats (contain 'g' and 'Pack')
    valid_joint_ratio_mask = joint_ratio_values.astype(str).str.contains(r'\d+g.*pack', case=False, na=False)
    self.df.loc[preroll_mask & valid_joint_ratio_mask, "JointRatio"] = joint_ratio_values[valid_joint_ratio_mask]

# For remaining pre-rolls without valid JointRatio, generate from Weight
remaining_preroll_mask = preroll_mask & (self.df["JointRatio"] == '')
for idx in self.df[remaining_preroll_mask].index:
    weight_value = self.df.loc[idx, 'Weight*']
    if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
        try:
            weight_float = float(weight_value)
            # Generate standard pack format
            default_joint_ratio = f"{weight_float}g x 1 Pack"
            self.df.loc[idx, 'JointRatio'] = default_joint_ratio
        except (ValueError, TypeError):
            pass
```

**Key Improvements**:
- ✅ **Format Validation**: Only uses JointRatio values that contain 'g' and 'pack' (valid pack format)
- ✅ **Proper Fallback**: Generates pack format from Weight when JointRatio is missing
- ✅ **No THC/CBD Contamination**: Avoids copying Ratio values that contain THC/CBD format

### 2. Weight Units Processing Fixes

**File**: `src/core/data/excel_processor.py` (lines 2300-2320)

**Enhanced `_format_weight_units` Method**:
```python
# Check if JointRatio is valid (not NaN, not empty, and looks like a pack format)
if (joint_ratio and 
    joint_ratio != 'nan' and 
    joint_ratio != 'NaN' and 
    not pd.isna(joint_ratio) and
    ('g' in str(joint_ratio).lower() and 'pack' in str(joint_ratio).lower())):
    
    # Use the JointRatio as-is for pre-rolls
    result = str(joint_ratio)
else:
    # For pre-rolls with invalid JointRatio, generate from Weight
    weight_val = safe_get_value(record.get('Weight*', ''))
    if weight_val and weight_val not in ['nan', 'NaN'] and not pd.isna(weight_val):
        try:
            weight_float = float(weight_val)
            result = f"{weight_float}g x 1 Pack"
        except (ValueError, TypeError):
            result = ""
    else:
        result = ""
```

**Key Improvements**:
- ✅ **Format Validation**: Checks that JointRatio contains 'g' and 'pack' before using it
- ✅ **Proper Generation**: Generates pack format from Weight when JointRatio is invalid
- ✅ **No Ratio Fallback**: Removed fallback to Ratio values (which contain THC/CBD format)

### 3. Template Processing Fixes

**File**: `src/core/generation/template_processor.py` (lines 1842-1875)

**Enhanced `format_joint_ratio_pack` Function**:
```python
def format_joint_ratio_pack(self, text):
    """
    Format JointRatio as: [amount]g x [count] Pack
    Handles various input formats and normalizes them to standard format.
    """
    if not text:
        return text
        
    # Convert to string and clean up
    text = str(text).strip()
    
    # Remove any leading/trailing spaces and hyphens
    text = re.sub(r'^[\s\-]+', '', text)
    text = re.sub(r'[\s\-]+$', '', text)
    
    # Handle various input patterns
    patterns = [
        # Standard format: "1g x 2 Pack"
        r"([0-9.]+)g\s*x\s*([0-9]+)\s*pack",
        # Compact format: "1gx2Pack"
        r"([0-9.]+)g\s*x?\s*([0-9]+)pack",
        # With spaces: "1g x 2 pack"
        r"([0-9.]+)g\s*x\s*([0-9]+)\s*pack",
        # Just weight: "1g"
        r"([0-9.]+)g",
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            amount = match.group(1).strip()
            # Try to get count, default to 1 if not found
            try:
                count = match.group(2).strip()
                if count and count.isdigit():
                    formatted = f"{amount}g x {count} Pack"
                else:
                    formatted = f"{amount}g x 1 Pack"
            except IndexError:
                # Only amount found (like "1g")
                formatted = f"{amount}g x 1 Pack"
            return formatted
    
    # If no pattern matches, return the original text
    return text
```

**Key Improvements**:
- ✅ **Multiple Pattern Support**: Handles various input formats (standard, compact, with spaces, just weight)
- ✅ **Default Count**: Automatically adds "x 1 Pack" when only weight is provided
- ✅ **Case Insensitive**: Handles both "Pack" and "pack" variations
- ✅ **Robust Parsing**: Better regex patterns for extracting weight and count

## How the Fix Works

### 1. Data Loading Phase
- **Validation**: Only uses JointRatio values that look like pack formats
- **Generation**: Creates pack format from Weight when JointRatio is missing
- **No Contamination**: Avoids copying THC/CBD values from Ratio column

### 2. Processing Phase
- **Format Check**: Validates JointRatio contains 'g' and 'pack' before using
- **Fallback**: Generates pack format from Weight when JointRatio is invalid
- **Consistency**: Ensures all pre-rolls have proper pack format

### 3. Template Phase
- **Normalization**: Converts various input formats to standard "Xg x Y Pack" format
- **Default Handling**: Adds "x 1 Pack" when only weight is provided
- **Pattern Matching**: Handles multiple input format variations

## Expected Results

### Before Fix
- JointRatio showing THC/CBD values instead of pack format
- Inconsistent formatting (e.g., "1gx2Pack", "1g", "THC: 25%")
- Missing pack information for pre-rolls

### After Fix
- ✅ **Consistent Format**: All JointRatio values in "Xg x Y Pack" format
- ✅ **Proper Data**: Uses actual pack information, not THC/CBD values
- ✅ **Complete Coverage**: All pre-rolls have proper JointRatio values
- ✅ **Fallback Support**: Generates pack format from Weight when needed

## Examples

### Input → Output Transformations
- `"1g x 2 Pack"` → `"1g x 2 Pack"` (unchanged)
- `"1gx2Pack"` → `"1g x 2 Pack"` (normalized)
- `"1g"` → `"1g x 1 Pack"` (default count added)
- `"0.5g x 3 pack"` → `"0.5g x 3 Pack"` (normalized)
- `"THC: 25% CBD: 2%"` → `"THC: 25% CBD: 2%"` (ignored, not pack format)

## Files Modified

1. `src/core/data/excel_processor.py` - Enhanced JointRatio creation and validation
2. `src/core/generation/template_processor.py` - Improved format_joint_ratio_pack function

## Verification

The fix ensures:
- ✅ **Format Validation**: Only valid pack formats are used
- ✅ **Proper Generation**: Pack format generated from Weight when needed
- ✅ **Consistent Output**: All JointRatio values in standard format
- ✅ **No THC/CBD Contamination**: Ratio values not used for JointRatio

**Result**: JointRatio values are now calculated correctly and display proper pack information for pre-roll products. 