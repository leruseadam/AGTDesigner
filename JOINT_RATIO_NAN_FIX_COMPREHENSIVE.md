# JointRatio NaN Fix - Comprehensive Solution

## Problem Description
JointRatio values were showing as "NaN" in the generated labels for pre-roll products. This occurred when:
1. The original Excel file contained NaN values in the "Joint Ratio" column
2. The system was not properly handling NaN values during processing
3. NaN values were being passed through to the template output

## Root Cause Analysis
The issue was occurring at multiple points in the processing pipeline:

### 1. Excel Processor (`src/core/data/excel_processor.py`)
- NaN values were being converted to empty strings but not consistently
- 'nan' string values were not being handled properly
- Fallback logic was not comprehensive enough

### 2. Template Processor (`src/core/generation/template_processor.py`)
- NaN values were not being checked before processing
- The `_build_label_context` method was not handling NaN values

### 3. Tag Generator (`src/core/generation/tag_generator.py`)
- NaN values were not being filtered out before marker wrapping

## Comprehensive Fix Applied

### 1. Excel Processor Fixes

**File**: `src/core/data/excel_processor.py` (lines 1622-1640)

**Added comprehensive NaN handling**:
```python
# Fix: Replace any 'nan' string values with empty strings
nan_string_mask = (self.df["JointRatio"].astype(str).str.lower() == 'nan')
self.df.loc[nan_string_mask, "JointRatio"] = ''

# Fix: For pre-rolls with empty JointRatio, try to use Ratio as fallback
empty_joint_ratio_mask = preroll_mask & (self.df["JointRatio"] == '')
for idx in self.df[empty_joint_ratio_mask].index:
    ratio_value = self.df.loc[idx, 'Ratio']
    if pd.notna(ratio_value) and str(ratio_value).strip() != '' and str(ratio_value).lower() != 'nan':
        self.df.loc[idx, 'JointRatio'] = str(ratio_value).strip()

# Fix: For still empty JointRatio, generate default from Weight
still_empty_mask = preroll_mask & (self.df["JointRatio"] == '')
for idx in self.df[still_empty_mask].index:
    weight_value = self.df.loc[idx, 'Weight*']
    if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
        try:
            weight_float = float(weight_value)
            default_joint_ratio = f"{weight_float}g x 1 Pack"
            self.df.loc[idx, 'JointRatio'] = default_joint_ratio
        except (ValueError, TypeError):
            pass
```

**Enhanced `_format_weight_units` method**:
```python
# Ensure the joint_ratio is not NaN or 'nan' string
if pd.isna(joint_ratio) or str(joint_ratio).lower() == 'nan':
    result = ""
else:
    result = str(joint_ratio)
```

### 2. Template Processor Fixes

**File**: `src/core/generation/template_processor.py` (lines 757-763)

**Added NaN check in `_build_label_context`**:
```python
# Fix: Handle NaN values in JointRatio
if pd.isna(val) or str(val).lower() == 'nan':
    val = ''
```

**Added pandas import**:
```python
import pandas as pd
```

### 3. Tag Generator Fixes

**File**: `src/core/generation/tag_generator.py` (lines 265-270)

**Added NaN filtering before marker wrapping**:
```python
# Fix: Handle NaN values in JointRatio
joint_ratio_value = row.get("JointRatio", "")
if pd.isna(joint_ratio_value) or str(joint_ratio_value).lower() == 'nan':
    joint_ratio_value = ""
label_data["JointRatio"] = wrap_with_marker(str(joint_ratio_value), "JOINT_RATIO")
```

**Added pandas import**:
```python
import pandas as pd
```

## How the Fix Works

### Multi-Layer Protection
1. **Data Loading**: NaN values are converted to empty strings
2. **String Filtering**: 'nan' string values are converted to empty strings
3. **Fallback Logic**: Empty JointRatio values get fallback from Ratio field
4. **Default Generation**: Still empty values get default format from Weight field
5. **Template Processing**: NaN values are filtered out before template processing
6. **Marker Wrapping**: NaN values are filtered out before marker wrapping

### Fallback Strategy
1. **Primary**: Use JointRatio if available and valid
2. **Secondary**: Use Ratio field as fallback if JointRatio is missing/NaN
3. **Tertiary**: Generate default format using Weight field (e.g., "1g x 1 Pack")
4. **Last Resort**: Return empty string if no fallback data is available

## Testing Results

### Before Fix
- JointRatio values showing as "NaN" in labels
- Pre-roll products with missing data showing NaN
- Inconsistent handling of NaN values

### After Fix
- ✅ All NaN values properly converted to empty strings
- ✅ 'nan' string values properly filtered out
- ✅ Fallback logic working for missing JointRatio data
- ✅ Default generation working for completely missing data
- ✅ Template processing handles NaN values gracefully
- ✅ No "NaN" text appearing in final labels

## Benefits

1. **Eliminates NaN Display**: No more "NaN" text in generated labels
2. **Robust Fallback**: Multiple levels of fallback for missing data
3. **Consistent Handling**: NaN values handled consistently across all processing stages
4. **Backward Compatibility**: Works with existing data without breaking changes
5. **Performance**: Minimal performance impact with efficient NaN checking

## Files Modified

1. `src/core/data/excel_processor.py` - Enhanced NaN handling and fallback logic
2. `src/core/generation/template_processor.py` - Added NaN filtering in template processing
3. `src/core/generation/tag_generator.py` - Added NaN filtering in marker wrapping

## Verification

The fix has been tested with:
- ✅ Test data with explicit NaN values
- ✅ Test data with 'nan' string values
- ✅ Test data with empty JointRatio values
- ✅ Real-world data scenarios
- ✅ All template types (vertical, horizontal, mini, double)

**Result**: No more "NaN" text appearing in generated labels for pre-roll products. 