# Price Investigation Results

## Problem
Missing prices were defaulting to `$25` on the web version, making it hard to identify which products actually had missing price data.

## Root Cause
Multiple fallback points in the code were using `'25'` as a default price value when actual price data was missing:

### Files Fixed:

1. **`src/core/data/excel_processor.py`** (3 occurrences):
   - Line 3864: Changed `else '25'` to `else ''`
   - Line 5926-5927: Changed educated guess default from `"25"` to `""`
   - Line 6530: Changed `else '25'` to `else ''`

2. **`src/core/data/json_matcher.py`** (4 occurrences):
   - Line 2166: Changed `price or '25'` to `price or ''`
   - Line 2146: Changed final fallback from `"25"` to `""`
   - Line 2229: Changed `or '25'` to `or ''`

3. **`app.py`** (1 occurrence):
   - Line 5400: Changed `json_product.get('Price', '25')` to `json_product.get('Price', '')`

4. **`src/core/generation/tag_generator.py`**:
   - Added logging to warn when prices are missing
   - Added check to skip products with no name (prevents empty labels)

## Impact
- Missing prices will now be empty instead of showing `$25`
- Logs will show exactly which products have missing prices
- Makes it easy to identify data quality issues

## Flow Trace
1. **Data Source** → Excel/Database → Extract price from `Price*` or `Price` field
2. **Processing** → Pass through to records with NO default
3. **Generation** → Format price if present, leave empty if not
4. **Rendering** → Show empty price (easy to spot)

## Next Steps
1. Test locally - should show empty prices when data is missing
2. Deploy to PythonAnywhere
3. Monitor logs for missing prices
4. Fix source data issues identified by the logging

