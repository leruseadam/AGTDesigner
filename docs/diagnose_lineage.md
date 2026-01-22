# Lineage Flow Diagnosis

## Database Status: ✅ WORKING
- `products.Lineage` column exists
- `products.sovereign_lineage` column exists
- `strains.canonical_lineage` column exists
- `strains.sovereign_lineage` column exists
- Write operations work correctly
- Read operations return correct values

## Code Flow Analysis

### 1. WRITE PATH (When you edit lineage):

```
Frontend (main.js:7315)
  → POST /api/update-lineage
     Payload: { tag_name, "Product Name*", lineage }

Backend (app.py:12060)
  → update_lineage() endpoint
     ✓ Updates products.sovereign_lineage (line 12104-12108)
     ✓ Updates strains.sovereign_lineage (line 12183-12190)
     ✓ Commits transaction (line 12227)
     ✓ Verifies update (line 12242-12311)
     → Returns: { success, db_updated, verified_lineage }
```

### 2. READ PATH (When page loads/refreshes):

```
Frontend
  → GET /api/products/search?vendor=X&q=Y

Backend (app.py:14147)
  → search_products() endpoint
     Step 1: Read from Excel DataFrame (line 14328)
        lineage = row.get(lineage_col, 'Unknown')

     Step 2: Override with database values (line 14379-14455) ← MY FIX
        Query: products.sovereign_lineage, strains.sovereign_lineage
        Priority: product.sovereign > strain.sovereign > canonical > excel

     → Returns: { strains: [...], total_found }
```

## Priority Logic

When displaying lineage, the system uses this priority:
1. `products.sovereign_lineage` (manual edits for specific products)
2. `strains.sovereign_lineage` (manual edits for strains)
3. `strains.canonical_lineage` (computed lineage)
4. `products.Lineage` (original Excel value)

## Potential Issues

### Issue #1: Excel processor cache
The Excel processor might be caching old values. After update, the code clears the cache (line 12376-12382) but there might be multiple instances.

### Issue #2: Frontend cache
The frontend TagManager might be caching tag data and not refreshing.

### Issue #3: Search not using database override
If the database override code (line 14379) is not executing, Excel values will show.

## Debugging Steps

1. **Check backend logs** after editing lineage:
   ```
   Look for: "✅ Updated sovereign_lineage for N product(s)"
   Look for: "🔍 Checking database for lineage overrides"
   Look for: "📝 Applying N lineage overrides from database"
   ```

2. **Verify database update**:
   ```sql
   SELECT "Product Name*", Lineage, sovereign_lineage
   FROM products
   WHERE "Product Name*" = 'YOUR_PRODUCT_NAME';
   ```

3. **Check API response**:
   Open browser DevTools → Network tab
   After editing lineage, check the response from `/api/update-lineage`
   Should see: `{"success": true, "db_updated": X, ...}`

4. **Check search response**:
   After refresh, check response from `/api/products/search`
   The `lineage` field should match your edit

## Next Steps

Please tell me:
1. What product name are you trying to edit?
2. What lineage are you changing it to?
3. Does the UI update immediately after you edit?
4. When you refresh, does it revert to the old value?
5. Can you check the browser console for any errors?

I'll help you trace through the exact issue.
