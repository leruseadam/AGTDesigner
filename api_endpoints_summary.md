# Backend API Tag Loading - Executive Summary

## Quick Reference

### 1. What Are the Main Endpoints?

**`/api/available-tags`** (Primary - Lines 7688-8615)
- Loads all product tags with optional database lineage alignment
- 4-tier performance system (fast cache → lineage alignment → Excel → database)
- Default behavior: Returns cached tags in < 100ms (fast_load=true by default)

**`/api/initial-data`** (Lines 14888-15122)
- Called after page load to initialize app state
- Returns: tags, filters, columns, file info
- Cached for 5 minutes per session

**`/api/web/available-tags`** (Lines 10261-10395)
- Web-optimized version with aggressive caching
- Used by web frontend clients

**`/api/available-tags-lite`** (Lines 14812-14852)
- Lightweight version for memory-constrained environments
- Limited to first 1000 tags

### 2. How Are Tags Loaded?

**Decision Tree:**
```
1. Is it in cache?
   → YES + fast_load enabled → Return immediately (< 100ms) ✓ FASTEST
   → YES + lineage alignment needed → Align then return (1-3s)
   
2. No cache - try Excel?
   → YES + has data → Get tags + align lineage (2-8s)
   
3. No Excel - use database?
   → YES → Query products table (3-15s)
```

### 3. What's the Lineage Alignment Logic?

**Key Principle:** Always prefer database lineage over Excel lineage
- Products.Lineage (user-editable) > Strains.canonical_lineage (reference)
- Batch aligned: ~500 products per database query (not 1 query per product!)
- Update tracking: If lineage edited < 10 mins ago, force full refresh

**SQL Query (Optimized):**
```sql
SELECT COALESCE(p."Lineage", s.canonical_lineage) AS lineage
FROM products p
LEFT JOIN strains s ON TRIM(LOWER(s.strain_name)) = TRIM(LOWER(p."Product Strain"))
WHERE p."Product Name*" IN (?) OR p.normalized_name IN (?)
```
Performance: 100-500ms for 500 products

### 4. Caching Architecture

**4 Cache Layers:**

1. **Flask In-Memory** (Line 1690)
   - SimpleCache with 5-min timeout
   - Session-isolated: includes session ID + file path in key
   - Purged on app restart

2. **Session-Based Keys** (Line 7398)
   ```python
   get_session_cache_key(base_key) = SHA256(base_key + session_id + file_path)
   ```

3. **File-Based Persistence** (Line 244)
   - Location: `/uploads/cache/available_tags_{store_name}.json`
   - Purpose: Emergency fallback
   - Never auto-deleted (manual cleanup only)

4. **Rate Limit Cache** (Line 512-516)
   - Per-IP tracking: max 100 requests/minute
   - Returns cached data if limit exceeded (no 429 error)

**Cache Invalidation:**
- On file upload: Clear session cache
- On lineage edit: Mark for full refresh (10-min window)
- On store change: Clear store cache

### 5. Performance Characteristics

**Response Times (Typical):**
| Scenario | Time | Cached | Source |
|----------|------|--------|--------|
| Cached tags (fast_load=true) | 10-100ms | YES | Memory |
| Cached + lineage align | 1-3s | YES | Memory+DB |
| Fresh Excel tags | 2-8s | NO | Excel+DB |
| Fresh database query | 3-15s | NO | Database |
| Empty state | 100-200ms | NO | None |

**Bottlenecks:**
1. Batch lineage query: 100-500ms (SQL IN clause with 500 items)
2. Full database scan: 1-3s (LIMIT 10,000 with JOIN)
3. Product processing loop: 20-50s (for 10,000+ with weight conversions)
4. Memory checks: 10-50ms per request

### 6. Database Query Operations

**Lazy Loaded:**
- ProductDatabase (Line 1293): 2-5s first access, <10ms reuse
- ExcelProcessor (Line 1047): Thread-safe with session file priority

**Product Processing** (Line 7525):
- Converts DB products to Excel format
- Creates CombinedWeight from Weight* + Units
- Special handling: Pre-rolls (JointRatio), Moonshots (2.5oz)
- Per-product: 1-5ms (mostly dict lookups)

**Weight Logic:**
- Pre-roll: Use JointRatio ("0.5g x 2 Pack")
- Moonshot: Force to 2.5oz
- Nonclassic (grams): Convert to ounces
- Classic: Keep original

### 7. Request Parameters & Behavior

**`/api/available-tags` Parameters:**
```
?nocache=1        # Bypass cache, force fresh query
?prefer_db=1      # Skip Excel, use database only
?fast_load=0      # Force lineage alignment (slower)
?platform=windows # Web client hint
```

**`/api/initial-data` Parameters:**
```
?nocache=1        # Bypass cache
```

### 8. Response Headers

**Standard Headers:**
```
X-Cache: HIT|HIT-FAST|MISS  # Cache status
X-Response-Time: 45ms       # Time in milliseconds
Cache-Control: private, max-age=60  # Browser cache (1 min)
```

### 9. Configuration Constants

**Performance Settings (app.py):**
```python
CACHE_DURATION = 300              # 5 minutes
MAX_BATCH_SIZE = 500              # SQL batch limit
MAX_MEMORY_MB = 425-500           # Memory limit
CACHE_SIZE_LIMIT = 50-100         # Cached items
RATE_LIMIT_WINDOW = 60            # 1 minute
RATE_LIMIT_MAX_REQUESTS = 100     # Per minute per IP
```

**PythonAnywhere Optimization:**
- Stricter limits: 425MB memory, 250 batch size
- Reduced cache size: 50 items max
- 5MB upload limit (vs 25MB locally)

### 10. Code Locations - Quick Reference

| What | File | Line |
|------|------|------|
| /api/available-tags | app.py | 7688-8615 |
| /api/initial-data | app.py | 14888-15122 |
| /api/web/available-tags | app.py | 10261-10395 |
| /api/available-tags-lite | app.py | 14812-14852 |
| Cache setup | app.py | 1690-1692 |
| Cache functions | app.py | 238-264, 7398-7430 |
| get_session_cache_key() | app.py | 7398 |
| get_product_database() | app.py | 1293 |
| get_excel_processor() | app.py | 1047 |
| get_session_excel_processor() | app.py | 2074 |
| process_database_product_for_api() | app.py | 7525 |
| Memory monitoring | app.py | 102-138 |
| Performance config | app.py | 74-99 |

---

## Common Issues & Solutions

**Issue: Tags take 10+ seconds to load**
- Check if database has indexes on Product Name*, normalized_name
- Consider using fast_load=true (default) instead of false
- Verify product_db query execution time in logs

**Issue: Lineage not updating after edit**
- Check session['lineage_update_timestamp']
- If timestamp exists, force full refresh (< 10 mins)
- Manual fix: ?nocache=1&fast_load=0

**Issue: Memory usage high**
- Memory check runs on every /api/available-tags request
- Consider caching memory status for 5 seconds
- Check if cache is clearing old entries properly

**Issue: Batch query fails**
- If IN clause > 500 items, fallback to individual queries
- Check logs for "Batch lineage query failed"
- May add significant latency but ensures reliability

---

## Key Files to Modify

**For Performance:**
1. ProductDatabase - Add column caching, optimize queries
2. ExcelProcessor - Cache weight conversions, batch processing
3. app.py - Reduce memory check frequency, add query caching

**For Reliability:**
1. Batch query fallback already implemented ✓
2. File-based cache persistence already implemented ✓
3. Memory checks already implemented ✓

