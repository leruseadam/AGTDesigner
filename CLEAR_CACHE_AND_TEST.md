# Clear Cache and Test Sovereign Lineage Fix

## Problem Identified

Your tags have `sovereign_lineage: 'NONE'` (string) coming from **cached data** in localStorage. The cache was created before the fix was applied.

## Solution: Clear All Caches

### Step 1: Clear Browser Cache
Open browser console and run:

```javascript
// Clear localStorage cache
localStorage.removeItem('agt_available_tags_mac_AGT_Bothell_nofile');
localStorage.removeItem('agt_last_cache_timestamp');

// Clear all AGT-related items
Object.keys(localStorage).forEach(key => {
  if (key.includes('agt_') || key.includes('AGT_')) {
    localStorage.removeItem(key);
    console.log('Removed:', key);
  }
});

console.log('✅ Browser cache cleared');
```

### Step 2: Clear Flask Cache
Run in terminal:

```bash
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"

# Stop Flask if running
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Clear Flask cache directory
rm -rf __pycache__
rm -rf .cache/*
rm -rf instance/cache/*

echo "✅ Flask cache cleared"
```

### Step 3: Force Fresh Data Load

In browser console:

```javascript
// Force reload tags with nocache
fetch('/api/available-tags?nocache=1&prefer_db=1&t=' + Date.now())
  .then(r => r.json())
  .then(data => {
    console.log('Fresh tags loaded:', data.tags.length);

    // Check a specific product
    const honeyBanana = data.tags.find(t =>
      t['Product Name*']?.includes('Honey Banana by Gabriel')
    );

    if (honeyBanana) {
      console.log('Honey Banana tag:', honeyBanana);
      console.log('sovereign_lineage:', honeyBanana.sovereign_lineage);
      console.log('Expected: "SATIVA", Got:', honeyBanana.sovereign_lineage);

      if (honeyBanana.sovereign_lineage === 'SATIVA') {
        console.log('✅✅✅ FIX WORKING! sovereign_lineage is SATIVA');
      } else if (honeyBanana.sovereign_lineage === 'NONE') {
        console.log('❌ Still showing NONE - backend not updated');
      } else if (!('sovereign_lineage' in honeyBanana)) {
        console.log('⚠️ sovereign_lineage field missing entirely');
      }
    } else {
      console.log('Product not found');
    }
  });
```

### Step 4: Restart Flask and Test

```bash
# Restart Flask
python app.py
```

Then refresh browser with **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows).

### Expected Result After Fix

For products WITH sovereign_lineage (like "Honey Banana by Gabriel - 28g"):
```javascript
{
  "Product Name*": "Honey Banana by Gabriel - 28g",
  "sovereign_lineage": "SATIVA",  // ✅ Should be SATIVA, not 'NONE'
  "canonical_lineage": "SATIVA",
  "currentLineage": "SATIVA"
}
```

For products WITHOUT sovereign_lineage (like "Zkilatto 45 Pre-Roll"):
```javascript
{
  "Product Name*": "Zkilatto 45 Pre-Roll by 2727 - 1g x 5 Pack",
  // ✅ NO sovereign_lineage key (or null, but NOT 'NONE')
  "canonical_lineage": "HYBRID",
  "currentLineage": "HYBRID"
}
```

## If Still Showing 'NONE'

If after clearing cache you still see `sovereign_lineage: 'NONE'`, the problem is in the backend. Check where tags are getting `sovereign_lineage` set to the string `'NONE'`.

Run this in Python to test:
```python
cd "/Users/adamcordova/Desktop/labelMaker_ QR copy final"
python3 << 'EOF'
from src.core.data.product_database import ProductDatabase

db = ProductDatabase('AGT_Bothell')
conn = db._get_connection()
cursor = conn.cursor()

# Test the _align query
cursor.execute('''
    SELECT p."Product Name*",
           COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p."Lineage") as lineage,
           p.sovereign_lineage as product_sovereign
    FROM products p
    LEFT JOIN strains s ON p.strain_id = s.id
    WHERE p."Product Name*" = "Honey Banana by Gabriel - 28g"
''')

result = cursor.fetchone()
print(f"DB Result: {result}")
print(f"product_sovereign is None: {result[2] is None}")
print(f"product_sovereign value: '{result[2]}'")
print(f"product_sovereign type: {type(result[2])}")

conn.close()
EOF
```

Expected output:
```
DB Result: ('Honey Banana by Gabriel - 28g', 'SATIVA', 'SATIVA')
product_sovereign is None: False
product_sovereign value: 'SATIVA'
product_sovereign type: <class 'str'>
```

NOT:
```
product_sovereign value: 'NONE'  # ❌ This means backend is setting it wrong
```
