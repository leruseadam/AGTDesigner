# THC/CBD Column Merging Implementation

## Overview

This implementation merges THC and CBD test result columns with their respective Total THC and CBDA columns, using the highest values to ensure the most accurate potency information is displayed on labels.

## Changes Made

### 1. Modified `src/core/data/excel_processor.py`

**Location**: Lines 2271-2300 in the `get_selected_records` method

**Changes**:
- **THC Merging Logic**: 
  - Compares `Total THC` (column AI) with `THC test result` (column K)
  - Uses the highest value between the two
  - If `Total THC` is 0 or empty, compares `THCA` vs `THC test result` and uses the highest
  - Falls back to `THCA` if `THC test result` is empty or invalid

- **CBD Merging Logic**:
  - Compares `CBDA` (column AK) with `CBD test result` (column L)  
  - Uses the highest value between the two
  - Falls back to `CBDA` if `CBD test result` is empty or invalid

### 2. Key Features

#### Safe Value Handling
- Converts all values to float for comparison
- Handles empty strings, 'nan', 'NaN', and invalid values gracefully
- Returns empty string for completely invalid data

#### Priority Logic
**For THC:**
1. If `Total THC` > 0: Compare with `THC test result`, use highest
2. If `Total THC` = 0 or empty: Compare `THCA` vs `THC test result`, use highest
3. If all values are invalid: Return empty string

**For CBD:**
1. Compare `CBDA` vs `CBD test result`, use highest
2. If one is invalid, use the other
3. If both invalid: Return empty string

#### Debug Logging
- Logs when `THC test result` is used over `Total THC`
- Logs when `CBD test result` is used over `CBDA`
- Helps track when the merging logic is making decisions

## Test Results

All test cases pass:

✅ **Test 1**: THC test result higher (18.2% vs 15.5%) → Uses 18.2%
✅ **Test 2**: Total THC higher (22.0% vs 19.8%) → Uses 22.0%  
✅ **Test 3**: Empty THC test result → Uses Total THC (16.5%)
✅ **Test 4**: Zero Total THC, use THCA → Uses THCA (13.2%)
✅ **Test 5**: Invalid values → Uses valid THCA (15.0%)

## Column Mapping

| Source Column | Target Column | Description |
|---------------|---------------|-------------|
| `Total THC` | `AI` | Primary THC value |
| `THC test result` | `AI` | Alternative THC value (merged) |
| `THCA` | `AJ` | Fallback THC value |
| `CBDA` | `AK` | Primary CBD value |
| `CBD test result` | `AK` | Alternative CBD value (merged) |

## Implementation Details

### Code Location
```python
# In src/core/data/excel_processor.py, get_selected_records method
# Lines 2271-2300

# THC merging logic
if total_thc_float > 0:
    if thc_test_float > total_thc_float:
        ai_value = thc_test_result
    else:
        ai_value = total_thc_value
else:
    if thca_float > 0 and thca_float >= thc_test_float:
        ai_value = thca_value
    elif thc_test_float > 0:
        ai_value = thc_test_result
    else:
        ai_value = ''

# CBD merging logic  
if cbd_test_float > cbda_float:
    ak_value = cbd_test_result
else:
    ak_value = cbda_value
```

### Benefits

1. **Accuracy**: Always uses the highest available potency values
2. **Compatibility**: Maintains backward compatibility with existing templates
3. **Robustness**: Handles edge cases and invalid data gracefully
4. **Transparency**: Logs decisions for debugging and verification

## Testing

Run the test script to verify the implementation:
```bash
python test_thc_cbd_merge.py
```

This will test both synthetic data and actual data from the loaded file to ensure the merging logic works correctly in all scenarios.

## Impact

- **Labels**: Will now display the highest available THC/CBD values
- **Templates**: No changes needed to existing templates
- **Data Processing**: More accurate potency information in generated labels
- **User Experience**: Better representation of product potency on labels 