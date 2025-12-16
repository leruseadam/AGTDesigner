# Backend API Endpoints Analysis - Complete Documentation

This directory contains comprehensive analysis of the tag loading API endpoints in the labelMaker application.

## Documentation Files

### 1. **API_ENDPOINTS_QUICK_REFERENCE.md** (Start Here!)
   - Visual diagrams of all endpoints
   - Performance tier charts
   - Request/response format examples
   - Common issues and fixes
   - Configuration values
   - **Best for**: Quick lookups, understanding flow at a glance

### 2. **api_endpoints_summary.md**
   - Executive summary of all endpoints
   - Key principles and decision trees
   - Lineage alignment logic
   - Caching architecture overview
   - Performance characteristics
   - Common issues with solutions
   - **Best for**: High-level understanding, system overview

### 3. **api_endpoints_analysis.md**
   - Detailed technical analysis (28KB)
   - Complete endpoint implementations (line numbers)
   - SQL query specifications
   - Performance bottleneck analysis
   - Database operations deep dive
   - Request flow diagrams
   - Optimization recommendations
   - **Best for**: Deep technical understanding, optimization work

## Quick Navigation

### I need to understand...

**How fast tags load?**
- Read: API_ENDPOINTS_QUICK_REFERENCE.md → Performance Tiers
- Also: api_endpoints_summary.md → Section 5

**Caching in the system**
- Read: api_endpoints_summary.md → Section 4
- Also: api_endpoints_analysis.md → Section 5

**Lineage alignment process**
- Read: api_endpoints_summary.md → Section 3
- Also: api_endpoints_analysis.md → Section 4

**Database queries**
- Read: api_endpoints_analysis.md → Section 2 & 6
- Also: API_ENDPOINTS_QUICK_REFERENCE.md → Database Operations

**How to optimize performance**
- Read: api_endpoints_analysis.md → Sections 7 & 10
- Also: API_ENDPOINTS_QUICK_REFERENCE.md → Performance Tuning

**What are the slow operations?**
- Read: api_endpoints_analysis.md → Section 7
- Also: API_ENDPOINTS_QUICK_REFERENCE.md → Common Issues

---

## Key Findings Summary

### Main Endpoints (4 Total)

1. **`/api/available-tags`** - Primary endpoint
   - Lines: 7688-8615 in app.py
   - Performance: 10ms (cached) to 15s (fresh database)
   - 4-tier performance system with automatic optimization

2. **`/api/initial-data`** - App initialization
   - Lines: 14888-15122 in app.py
   - Performance: 10ms (cached) to 8s (fresh)
   - Returns tags + filters + file info

3. **`/api/web/available-tags`** - Web-optimized
   - Lines: 10261-10395 in app.py
   - Performance: <100ms (cached), 2-8s (fresh)
   - Aggressive caching + compression

4. **`/api/available-tags-lite`** - Memory-constrained
   - Lines: 14812-14852 in app.py
   - Performance: 1-2s
   - Limited to 1000 tags max

### Caching System (4 Layers)

1. **Flask In-Memory Cache** - Primary (5 min TTL)
2. **Session-Based Keys** - Isolation via SHA256(sid + file_path)
3. **File-Based Persistence** - Emergency fallback
4. **Rate Limit Cache** - Per-IP tracking (100 req/min max)

### Lineage Alignment

- **Key Principle**: DB Lineage > Excel Lineage (always)
- **Method**: Batch query with IN clause (max 500 items)
- **Performance**: 100-500ms for 500 products
- **Update Tracking**: Force refresh if edited < 10 minutes ago

### Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Cached tags (no align) | 10-100ms | Fastest - TIER 1 |
| Cached + align | 1-3s | Fast - TIER 2 |
| Excel + align | 2-8s | Normal - TIER 3 |
| Database query | 3-15s | Slow - TIER 4 |
| First DB access | 2-5s | Lazy loading |
| Reuse DB | <10ms | Cached instance |

### Critical Bottlenecks

1. **Batch Query** (100-500ms) - SQLite IN clause with 500 items
2. **Full Scan** (1-3s) - LIMIT 10,000 with JOIN
3. **Product Processing** (20-50s) - 10,000+ products with weight logic
4. **Memory Checks** (10-50ms) - Runs on every request
5. **PRAGMA Queries** (50-100ms) - Dynamic column detection

---

## Implementation Details

### Request Flow

```
/api/available-tags
  ├─ Rate limit check
  ├─ Memory limit check
  ├─ Check fast_load parameter
  │
  ├─ If cache hit + fast_load=true
  │  └─ Return cached (< 100ms) ✓
  │
  ├─ If cache hit + need alignment
  │  ├─ Batch query database
  │  ├─ Build lineage lookup
  │  ├─ Apply to cached tags
  │  └─ Return (1-3s)
  │
  ├─ If no cache, try Excel
  │  ├─ Get Excel tags
  │  ├─ Batch align lineage
  │  ├─ Cache result (5 min)
  │  └─ Return (2-8s)
  │
  └─ If no Excel, use database
     ├─ Query products table
     ├─ JOIN with strains
     ├─ Cache result (5 min)
     └─ Return (3-15s)
```

### Cache Isolation

```
Session-based key = SHA256(base_key + session_id + file_path)

Examples:
- available_tags_somefile.xlsx
- initial_data_user1_upload.xlsx
- web_available_tags_default.xlsx
```

### Database Queries

**Batch Lineage Alignment:**
```sql
SELECT DISTINCT
    COALESCE(p."Lineage", s.canonical_lineage) AS lineage,
    p."Product Name*" AS product_name
FROM products p
LEFT JOIN strains s ON ...
WHERE p."Product Name*" IN (?, ?, ...) -- max 500
```

**Full Products Scan:**
```sql
SELECT {dynamic_columns}, 
       COALESCE(p."Lineage", s.canonical_lineage) AS preferred_lineage
FROM products p
LEFT JOIN strains s ON ...
ORDER BY p.id DESC
LIMIT 10000
```

---

## Configuration

### Constants (app.py)

```python
CACHE_DURATION = 300              # 5 minutes
MAX_BATCH_SIZE = 500              # SQL batch limit
MAX_MEMORY_MB = 425               # PythonAnywhere limit
CACHE_SIZE_LIMIT = 50             # Max cached items
RATE_LIMIT_WINDOW = 60            # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 100     # Per minute per IP
```

### Environment Variables

```bash
# Override cache duration
export CACHE_DURATION=600

# Override memory limit
export MAX_MEMORY_MB=500

# Override batch size
export BATCH_SIZE_LIMIT=500
```

---

## Performance Tuning Recommendations

### Quick Wins (Easy)
- Cache column list in ProductDatabase
- Cache memory status for 5 seconds
- Pre-compute Moonshot weight mappings
- Add database indexes on Product Name*, normalized_name

### Medium Effort
- Implement pagination (500 items per page)
- Add Redis/memcache for batch results
- Pre-compute lineage mappings
- Optimize IN clause handling

### Long Term
- Migrate to PostgreSQL
- Add full-text search
- Materialized views for filters
- Incremental sync

---

## Common Issues

### Issue: Slow Tag Loading (10+ seconds)

**Symptoms:**
- /api/available-tags takes 10+ seconds
- First page load is very slow

**Causes:**
- Large dataset (10,000+ products)
- No database indexes
- Batch query falling back to individual queries
- Slow product processing loop

**Fixes:**
```bash
# Try forcing database query with cache bypass
curl "/api/available-tags?nocache=1&prefer_db=1&fast_load=0"

# Add database indexes
# CREATE INDEX idx_product_name ON products("Product Name*")
# CREATE INDEX idx_normalized ON products(normalized_name)
```

### Issue: Lineage Not Updating

**Symptoms:**
- Edit lineage in UI
- Lineage doesn't change in display
- Same value shows across requests

**Causes:**
- Cache not invalidated
- Recent edit (< 10 min) forcing fast load
- Session timestamp not set

**Fixes:**
```bash
# Force full refresh
curl "/api/available-tags?nocache=1&fast_load=0"

# Or clear cache in code
clear_available_tags_cache(reason="manual-refresh")
```

### Issue: High Memory Usage

**Symptoms:**
- Memory usage near 425MB limit
- API requests start failing
- PythonAnywhere issues

**Causes:**
- Large cache (100+ items)
- Memory check runs on every request
- Old cache entries not cleaned

**Fixes:**
- Reduce CACHE_SIZE_LIMIT in config
- Clear cache more aggressively
- Reduce BATCH_SIZE_LIMIT
- Cache memory status (check every 5s, not every request)

---

## File References

### Main Implementation
- **app.py** - All endpoint implementations
  - /api/available-tags: 7688-8615
  - /api/initial-data: 14888-15122
  - /api/web/available-tags: 10261-10395
  - /api/available-tags-lite: 14812-14852

### Core Functions
- **get_product_database()**: Line 1293
- **get_excel_processor()**: Line 1047
- **get_session_excel_processor()**: Line 2074
- **get_session_cache_key()**: Line 7398
- **process_database_product_for_api()**: Line 7525
- **get_current_store_name()**: Line 639

### Caching
- **Cache initialization**: Lines 509, 1690-1692
- **Cache functions**: Lines 238-264, 7418-7430
- **save_available_tags_cache()**: Line 244
- **load_available_tags_cache()**: Line 254
- **clear_available_tags_cache()**: Line 7418

### Performance
- **Memory monitoring**: Lines 102-138
- **Rate limiting**: Lines 512-516
- **Configuration**: Lines 74-99
- **Performance headers**: Lines 1697-1709

---

## How to Use These Documents

1. **Start with API_ENDPOINTS_QUICK_REFERENCE.md**
   - Get visual overview of all endpoints
   - Understand performance tiers
   - See common issues

2. **If you need more detail, read api_endpoints_summary.md**
   - Understand caching system
   - Learn lineage alignment
   - See configuration options

3. **For optimization work, use api_endpoints_analysis.md**
   - Deep dive into implementations
   - See exact SQL queries
   - Find bottleneck details
   - Review optimization recommendations

---

## Questions?

All information in this analysis is sourced from:
- `/Users/adamcordova/Desktop/labelMaker_ QR copy final/app.py`
- Specific line numbers are provided for each section

The analysis covers:
- All 4 tag-loading endpoints
- Complete lineage alignment logic
- All caching mechanisms
- Database query specifications
- Performance characteristics
- Configuration options
- Optimization recommendations

Generated: November 16, 2025
