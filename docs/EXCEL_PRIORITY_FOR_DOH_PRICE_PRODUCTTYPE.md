# Excel Priority for DOH, Price, and Product Type

## Summary
Modified the system to ensure that **DOH designation**, **High THC/CBD designation (Product Type)**, and **Price** always come directly from the Excel file and overwrite any existing database values.

## Changes Made

### 1. Excel Processor (`src/core/data/excel_processor.py`)

#### Database Fallback Records (Lines 3722-3783)
- Added `EXCEL PRIORITY` comments throughout the database fallback code
- Clarified that when Excel data is not available and database fallback is used, database values are only temporary
- Updated logging to show DOH, Price, and Product Type values when creating fallback records
- **Key Change**: Database fallback records now clearly indicate they will be overwritten by Excel data

#### JSON Cache Fallback (Lines 3793-3828)
- Added `EXCEL PRIORITY` comments for cached product records
- Updated logging to show DOH, Price, and Product Type values from cache
- Ensured cache values are only used as fallback when Excel data is unavailable

#### Database Weight/Units Lookup (Lines 3952-3974)
- Added explicit comment: `"EXCEL PRIORITY: DOH, Price, and Product Type are NEVER taken from database"`
- Clarified that database lookups only retrieve Weight and Units as fallback
- DOH, Price, and Product Type always come from Excel when Excel data exists

#### Processed Records (Lines 4197-4219)
- **Line 4203**: Price comes directly from Excel record (`record.get('Price*')` or `record.get('Price')`)
- **Line 4205**: DOH comes directly from Excel record (via `doh_value` from `record.get('DOH')`)
- **Line 4208**: Product Type comes directly from Excel record (`record.get('Product Type*')`)

### 2. Product Database (`src/core/data/product_database.py`)

#### New Product Insertion (Lines 1043-1056)
- **Line 1043**: Added comment `"EXCEL PRIORITY: Excel Product Type (High THC/CBD) always overwrites DB"`
- **Line 1049**: Added comment `"EXCEL PRIORITY: Excel Price always overwrites DB"`
- **Line 1056**: Added comment `"EXCEL PRIORITY: Excel DOH always overwrites DB"`

#### Existing Product Updates (Lines 3132-3179)
- **Lines 3132-3133**: Existing comment confirms "Excel values for DOH, Price, and Product Type always overwrite database"
- **Line 3164**: Product Type from Excel with comment
- **Line 3171**: Price from Excel with comment  
- **Line 3179**: DOH from Excel with comment

## How It Works

### When Excel is Uploaded:
1. Excel data is processed and stored in the database
2. DOH, Price, and Product Type from Excel **always overwrite** existing database values
3. Database is updated with the latest Excel values for these fields

### When Generating Labels:
1. **Primary Source**: Excel DataFrame values are used for DOH, Price, and Product Type
2. **Database Fallback**: Only used when Excel data is not available (e.g., after page refresh)
3. **Cache Fallback**: Only used for JSON-matched products when Excel is not available

### Priority Order:
```
Excel Data (HIGHEST PRIORITY)
    ↓
Database Values (if Excel unavailable)
    ↓  
Cache Values (if both Excel and Database unavailable)
```

## Fields Affected

### 1. DOH (DOH Compliant Yes/No)
- **Excel Column**: `DOH Compliant (Yes/No)` or `DOH`
- **Values**: YES, NO, THC, CBD, or empty
- **Impact**: Determines which compliance image appears on labels (High THC, High CBD, or none)

### 2. Product Type (High THC/CBD Designation)
- **Excel Column**: `Product Type*`
- **Values**: flower, pre-roll, High THC flower, High CBD edible, etc.
- **Impact**: Affects product classification and label formatting

### 3. Price
- **Excel Column**: `Price*` or `Price`
- **Values**: Numeric price value
- **Impact**: Price displayed on labels and in the system

## Testing Recommendations

1. **Upload Excel with DOH Values**: Verify DOH images appear correctly on labels
2. **Upload Excel with Price Changes**: Verify prices update in database and on labels
3. **Upload Excel with Product Type Changes**: Verify High THC/CBD designations update correctly
4. **Database Fallback Test**: After upload, refresh page and verify values still correct
5. **Multiple Upload Test**: Upload multiple times with different values, verify latest always wins

## Key Takeaways

✅ **Excel is Source of Truth**: DOH, Price, and Product Type always come from Excel
✅ **Database Always Overwrites**: Each Excel upload replaces database values for these fields
✅ **No Manual Database Edits**: Manual database edits will be overwritten on next Excel upload
✅ **Consistent Behavior**: Same logic applies whether data comes from Excel, database, or cache

## Files Modified

1. `/src/core/data/excel_processor.py` - Excel processing and record retrieval
2. `/src/core/data/product_database.py` - Database storage and updates

## Date
November 1, 2025

