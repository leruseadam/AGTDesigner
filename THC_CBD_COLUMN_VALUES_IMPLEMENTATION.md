# THC/CBD Column Values Implementation

## Overview
This implementation adds support for using actual column values for THC and CBD percentages in classic types (flower, pre-roll, concentrate, etc.) instead of just showing "THC: CBD:" placeholders.

## Requirements
- For classic types with `Ratio_or_THC_CBD` value of "THC: CBD:", add actual column values
- For THC: use column "Total THC" first, fallback to "THCA" if Total THC is 0 or empty
- For CBD: use column "CBDA"
- Add % sign to all cannabinoid values

## Implementation Details

### 1. Modified `format_classic_ratio` function in `src/core/generation/template_processor.py`

**Changes:**
- Added `record=None` parameter to accept record data
- Added logic to extract AI, AJ, and AK column values when text is "THC:|BR|CBD:"
- Implemented fallback logic for THC values (Total THC → THCA)
- Added % sign to all cannabinoid values
- Maintained backward compatibility for existing functionality

**Key Logic:**
```python
# Extract THC/CBD values from actual columns
# For THC: use Total THC first, fallback to THCA if Total THC is 0 or empty
total_thc_value = str(record.get('Total THC', '')).strip()
thca_value = str(record.get('THCA', '')).strip()

# Use Total THC if it's not 0 or empty, otherwise use THCA
ai_value = total_thc_value if total_thc_value and total_thc_value != '0' and total_thc_value != '0.0' else thca_value

# For CBD: use CBDA
ak_value = str(record.get('CBDA', '')).strip()
```

### 2. Updated Excel Processor in `src/core/data/excel_processor.py`

**Changes:**
- Modified THC/CBD value extraction to use correct column names:
  - AI field: Uses "Total THC" or "THCA" (fallback)
  - AJ field: Uses "THCA" 
  - AK field: Uses "CBDA"
- Updated processed record to include these values for template processor access

### 3. Updated Function Calls

**Changes:**
- Modified `_build_label_context` function to pass record data to `format_classic_ratio`
- Updated all test files to include record parameter for backward compatibility

## Testing Results

### Unit Tests
✅ All existing unit tests pass with updated function signature
✅ New tests verify THC/CBD value extraction and formatting
✅ Fallback logic works correctly (Total THC → THCA)

### Integration Tests
✅ Real data test shows correct THC/CBD values:
- Product 1: "THC: 9.8% CBD: 0.0%"
- Product 2: "THC: 0.0% CBD: 0.0%"
- Product 3: "THC: 0.0% CBD: 0.0%"
- Product 4: "THC: 51.94% CBD: 0.0%"
- Product 5: "THC: 30.75% CBD: 0.05%"

### Formatting Examples
- Both values: `"THC: 25.5% CBD: 2.1%"`
- THC only: `"THC: 30.0%"`
- CBD only: `"CBD: 5.5%"`
- No values: `"THC: CBD:"` (fallback)

## Files Modified

1. **src/core/generation/template_processor.py**
   - `format_classic_ratio()` function
   - `_build_label_context()` function

2. **src/core/data/excel_processor.py**
   - THC/CBD value extraction logic
   - Processed record field assignments

3. **Test files updated for compatibility:**
   - test_ratio_no_extra_lines.py
   - test_rso_co2_tankers_formatting.py
   - test_classic_ratio_formatting.py

## Backward Compatibility

✅ All existing functionality preserved
✅ Function signatures updated with optional parameters
✅ Test files updated to maintain compatibility
✅ No breaking changes to existing label generation

## Summary

The implementation successfully adds actual THC/CBD column values to classic type labels while maintaining full backward compatibility. The system now:

1. **Extracts real values** from "Total THC", "THCA", and "CBDA" columns
2. **Implements smart fallback** logic for THC values
3. **Adds percentage signs** to all cannabinoid values
4. **Preserves existing functionality** for all other label types
5. **Maintains compatibility** with existing code and tests

The feature is now ready for production use and will display actual THC/CBD percentages instead of placeholder text for classic cannabis product types. 