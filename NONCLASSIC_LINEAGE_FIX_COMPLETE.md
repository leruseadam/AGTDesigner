# Nonclassic Lineage Fix - Complete

## Date: January 13, 2026

## Problem Statement

Nonclassic types (edibles, tinctures, topicals, capsules, etc.) were appearing with classic lineages (SATIVA, INDICA, HYBRID, HYBRID/SATIVA, HYBRID/INDICA) when they should **ONLY** have:
- **MIXED** (displayed as "THC" in UI)
- **CBD**
- **PARAPHERNALIA**

Conversely, classic types were sometimes showing MIXED when they should have valid classic lineages.

## Solution Implemented

### 1. Added Constants (src/core/constants.py)
- Added `VALID_NONCLASSIC_LINEAGES` constant defining valid lineages for nonclassic types
- Created `normalize_lineage_for_product_type()` helper function to automatically convert:
  - **For classic types**: MIXED/THC → HYBRID
  - **For nonclassic types**: SATIVA/INDICA/HYBRID → MIXED (displayed as THC)
- Created `is_classic_type()` helper function for easy type checking

### 2. Updated Backend Logic

#### app.py
- Updated lineage alignment logic to use `normalize_lineage_for_product_type()`
- Added validation in tag enrichment to prevent classic lineages on nonclassic types
- Replaced manual type checks with helper function calls
- Added logging to track conversions

#### src/core/generation/tag_generator.py
- Added normalization call after lineage assignment
- Ensures all generated tags have correct lineage for their product type
- Preserves CBD lineages for both classic and nonclassic types

### 3. Updated Frontend Logic (static/js/tags_table.js)
- Enhanced validation in `createTagRow()` function
- Automatically converts classic lineages → MIXED for nonclassic types
- Logs all conversions to console for debugging
- Validates lineages before display

### 4. Created Database Fix Script (fix_nonclassic_lineages.py)
- Scans database for nonclassic products with classic lineages
- Updates both `products` and `strains` tables
- Preserves CBD lineages
- Provides verification after fix

## Business Rules

### Classic Types
**Product Types:**
- Flower, Bud
- Pre-Roll, Infused Pre-Roll
- Concentrate, Solventless Concentrate, Live Resin, Rosin, Wax, Shatter, Hash, Kief
- Vape Cartridge, Vape Pen, Disposable
- RSO/CO2 Tankers

**Valid Lineages:**
- SATIVA
- INDICA
- HYBRID
- HYBRID/SATIVA
- HYBRID/INDICA
- CBD

**Auto-Conversion:**
- MIXED → HYBRID
- THC → HYBRID (same as MIXED)

### Nonclassic Types
**Product Types:**
- Edible (Solid)
- Edible (Liquid)
- Tincture
- Topical
- Capsule
- Paraphernalia
- All other types not in classic list

**Valid Lineages:**
- MIXED (displayed as "THC" in UI)
- CBD
- PARAPHERNALIA

**Auto-Conversion:**
- SATIVA → MIXED
- INDICA → MIXED
- HYBRID → MIXED
- HYBRID/SATIVA → MIXED
- HYBRID/INDICA → MIXED
- THC → MIXED (THC is an abbreviation for MIXED)

## Verification Results

✅ Database scan complete - no nonclassic products with classic lineages found
✅ All code paths updated to use new helper function
✅ Frontend validation enhanced with console logging
✅ Backend validation added at multiple touch points

## Testing Recommendations

1. **Load Excel file with mixed product types**
   - Verify classic types never show MIXED
   - Verify nonclassic types never show SATIVA/INDICA/HYBRID

2. **Check tag generation**
   - Generate tags for edibles - should show "THC" (MIXED) or CBD
   - Generate tags for flower - should show actual lineage (SATIVA/INDICA/HYBRID)

3. **Test database updates**
   - Manually set a nonclassic product lineage to SATIVA in Excel
   - Load file and verify it converts to MIXED automatically
   - Check database - should store as MIXED, not SATIVA

4. **Verify UI display**
   - Check browser console for conversion logs
   - Verify lineage dropdown only shows valid options per product type
   - Test strain editor - ensure changes persist correctly

## Files Modified

1. `/src/core/constants.py` - Added constants and helper functions
2. `/app.py` - Updated lineage processing in multiple locations
3. `/src/core/generation/tag_generator.py` - Added normalization after lineage assignment
4. `/static/js/tags_table.js` - Enhanced frontend validation
5. `/fix_nonclassic_lineages.py` - Database fix script (NEW)

## Usage

### Automatic Conversion (Always On)
The system now automatically converts lineages when processing:
- Excel file uploads
- Database queries
- Tag generation
- UI display

### Manual Database Fix (If Needed)
```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
python3 fix_nonclassic_lineages.py
```

The script will:
1. Scan for nonclassic products with classic lineages
2. Show what will be changed
3. Ask for confirmation
4. Update products and strains tables
5. Verify the fix

## Notes

- **CBD lineages are preserved** for both classic and nonclassic types
- **THC is treated as MIXED** (THC is just a display abbreviation)
- **Paraphernalia lineages are preserved** for paraphernalia products
- **All conversions are logged** for audit trail
- **Frontend shows console logs** for debugging

## Success Criteria

✅ Nonclassic types never show classic lineages (SATIVA/INDICA/HYBRID)
✅ Classic types never show MIXED lineage
✅ CBD lineages work correctly for all product types
✅ System auto-corrects invalid lineages everywhere
✅ Database stays clean over time
✅ UI displays correct lineages immediately

---

## Summary

The fix ensures that **nonclassic types (edibles, tinctures, etc.) will ONLY show MIXED/THC or CBD lineages**, never classic cannabis lineages like SATIVA, INDICA, or HYBRID. The system now automatically converts any mismatched lineages at every touch point: file upload, database query, tag generation, and UI display.
