# Frontend classicTypes Fix - HYBRID → MIXED Bug for Blunts

## Problem Discovered
Console logs showed the frontend was incorrectly converting HYBRID → MIXED for blunt products:
```
🔄 FORCING database lineage for Blackberry Kush Infused Pre-Roll by 2727 - 1g: HYBRID → MIXED
🔄 FORCING database lineage for Blue Lobster Blueberry Flavored Blunt by 2727 - 1.5g: HYBRID → MIXED
🔄 FORCING database lineage for Garlic Breath Pre-Roll by 2727 - 1g x 5 Pack: HYBRID → MIXED
```

## Root Cause
Frontend JavaScript had an incomplete `classicTypes` array that was **missing "blunt" and "flavored blunt"**.

### Backend Definition (Correct)
```python
# src/core/constants.py line 109-125
CLASSIC_TYPES = {
    "flower", "bud",
    "pre-roll", "infused pre-roll", "preroll", "blunt", "flavored blunt",  # ← INCLUDES BLUNT
    "concentrate", "solventless concentrate",
    "live resin", "rosin", "wax", "shatter", "hash", "kief",
    "butane extract", "distillate", "rso", "co2 extract",
    "honey crystal", "liquid diamond", "caviar",
    "vape cartridge", "vape pen", "disposable",
    "rso/co2 tankers"
}
```

### Frontend Definition (Broken - Before Fix)
```javascript
// static/js/main.js - 3 locations
const classicTypes = ['flower', 'pre-roll', 'concentrate', 'infused pre-roll', 'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'];
// ❌ MISSING: blunt, flavored blunt, and many other classic types
```

## Impact
Because "blunt" and "flavored blunt" were missing from the frontend's `classicTypes` array:
1. Frontend classified blunts as **non-classic types**
2. Non-classic types get HYBRID → MIXED conversion (correct for edibles/tinctures)
3. But blunts ARE classic types and should keep HYBRID lineage
4. Result: Blunts displayed "Mixed" (blue) instead of "Hybrid" (green) in the UI

## Solution
Updated all 3 locations in `static/js/main.js` where `classicTypes` is defined to **match backend CLASSIC_TYPES exactly**:

### Fixed Frontend Definition
```javascript
// static/js/main.js - lines 7147, 8899, 14279
// MUST MATCH backend CLASSIC_TYPES in src/core/constants.py
const classicTypes = ['flower', 'bud', 'pre-roll', 'preroll', 'infused pre-roll', 'blunt', 'flavored blunt', 'concentrate', 'solventless concentrate', 'live resin', 'rosin', 'wax', 'shatter', 'hash', 'kief', 'butane extract', 'distillate', 'rso', 'co2 extract', 'honey crystal', 'liquid diamond', 'caviar', 'vape cartridge', 'vape pen', 'disposable', 'rso/co2 tankers'];
```

## Files Modified
- **static/js/main.js** - 3 locations updated (lines 7147, 8899, 14279)

## Normalization Rules (Reminder)
- **Classic types** (flower, pre-roll, blunt, concentrates, vapes):
  - Convert MIXED/THC → HYBRID
  - Allow: SATIVA, INDICA, HYBRID, CBD
  - Display lineage color markers

- **Non-classic types** (edibles, tinctures, topicals, accessories):
  - Convert SATIVA/INDICA/HYBRID → MIXED (displayed as "THC")
  - Allow: MIXED (shown as "THC" in blue), CBD (yellow), PARAPHERNALIA (pink)
  - No lineage color markers

## Testing
After reloading the UI, blunts should now:
- ✅ Be classified as classic types
- ✅ Keep HYBRID lineage (display green "Hybrid" marker)
- ✅ NOT convert HYBRID → MIXED
- ✅ Match Word document output lineage

## Commits
- **f0609947**: "Fix frontend classicTypes to include blunt and flavored blunt"
  - Added missing product types to classicTypes array in all 3 locations
  - Now matches backend CLASSIC_TYPES definition exactly

## Related Fixes
This completes the lineage normalization fix series:
1. ✅ **503d6439**: Fixed database enrichment in excel_processor.py files
2. ✅ **9cfece40**: Fixed canonical_lineage in app.py
3. ✅ **f0609947**: Fixed frontend classicTypes to include blunt/flavored blunt

All normalization is now consistent across backend and frontend!
