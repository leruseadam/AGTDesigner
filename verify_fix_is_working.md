# Verification Steps

The fixes have been applied. To verify they're working:

## 1. Restart Flask App
```bash
# Kill any running Flask process
lsof -ti:5000 | xargs kill -9

# Start Flask
python app.py
```

## 2. Clear Browser Cache
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Or clear browser cache completely

## 3. Check Console Log
Open browser console and look for:

### Expected for products WITH sovereign_lineage:
```javascript
{
  "Product Name*": "Honey Banana by Gabriel - 28g",
  "sovereign_lineage": "SATIVA",  // ✅ Should be present
  "canonical_lineage": "SATIVA",
  "currentLineage": "SATIVA"
}
```

### Expected for products WITHOUT sovereign_lineage:
```javascript
{
  "Product Name*": "Zkilatto 45 Pre-Roll by 2727 - 1g x 5 Pack",
  // ✅ NO sovereign_lineage key at all (not 'NONE')
  "canonical_lineage": "HYBRID",
  "currentLineage": "HYBRID"
}
```

## 4. Test in UI
1. Load tags in the Tag Manager
2. Find "Honey Banana by Gabriel - 28g"
3. The lineage dropdown should show "SATIVA"
4. Check console - should show `sovereign_lineage: "SATIVA"`, NOT `"NONE"`

## What Was Fixed

1. **app.py line 7239** - Removed `tag['sovereign_lineage'] = None`
2. **app.py lines 10080-10143** - Added sovereign_lineage to database query (but this code is disabled by `if False:`)
3. **static/js/tags_table.js lines 115-132, 297-314** - Added `isValid()` to filter out 'NONE' strings

## If Still Showing 'NONE'

The issue is that cached tags might still have the old data. Try:
1. Clear all Flask caches
2. Delete `uploads/*.db` files (backup first!)
3. Re-upload Excel file
4. Hard refresh browser

## Debug: Check What's Being Returned

Add this to your browser console:
```javascript
fetch('/api/available-tags?nocache=1')
  .then(r => r.json())
  .then(data => {
    const honeyBanana = data.tags.find(t =>
      t['Product Name*']?.includes('Honey Banana by Gabriel')
    );
    console.log('Honey Banana tag:', honeyBanana);
    console.log('Has sovereign_lineage:', 'sovereign_lineage' in honeyBanana);
    console.log('sovereign_lineage value:', honeyBanana?.sovereign_lineage);
  });
```

Expected output:
```
Honey Banana tag: {Product Name*: "...", sovereign_lineage: "SATIVA", ...}
Has sovereign_lineage: true
sovereign_lineage value: "SATIVA"
```

NOT:
```
sovereign_lineage value: "NONE"  // ❌ This means cache or old data
sovereign_lineage value: null    // ❌ This means not being set
```
