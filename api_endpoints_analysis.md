# Backend API Endpoints Analysis - Tag Loading System

## Overview
This document provides a comprehensive analysis of the backend API endpoints that handle tag loading, including their implementations, performance characteristics, and caching mechanisms.

---

## 1. API Endpoints Summary

### Primary Endpoints
| Endpoint | Route | Purpose | Performance |
|----------|-------|---------|-------------|
| `/api/available-tags` | POST/GET | Primary tag loading with lineage alignment | ~5-10 seconds (cached) |
| `/api/initial-data` | GET | Initial app state load after page refresh | ~1-5 seconds (cached) |
| `/api/available-tags-lite` | GET | Lightweight tag loading for resource-constrained environments | ~1-2 seconds |
| `/api/web/available-tags` | GET | Web-optimized tags with aggressive caching | <100ms (cached) |

---

## 2. `/api/available-tags` Endpoint Implementation

**File:** `/Users/adamcordova/Desktop/labelMaker_ QR copy final/app.py` (Lines 7688-8615)

### Key Characteristics:
- **Purpose**: Load all available tags from Excel or database, with optional lineage alignment
- **Rate Limiting**: 5 requests per 10 seconds per IP address
- **Memory Checks**: Verifies memory usage before processing (limit: MAX_MEMORY_MB)
- **Cache Key Structure**: Session ID + File Path (SHA256 hashed)

### Request Parameters:
```
GET /api/available-tags?
  nocache=1|0          # Bypass cache if set to 1
  prefer_db=1|0        # Force database query (skip Excel)
  fast_load=1|0        # Default: true - skip lineage alignment for speed
  platform=windows     # Web client optimization flag
```

### Response Format:
```json
{
  "tags": [...],
  "total_count": 1250,
  "source": "cache-fast|cache+db-lineage|excel+db-lineage|database",
  "X-Cache": "HIT-FAST|HIT|MISS",
  "X-Response-Time": "45ms"
}
```

### Performance Optimization Tiers:

#### Tier 1: Fast Cache (< 100ms)
- **Condition**: Cached tags exist AND fast_load=true (default) AND no recent lineage updates
- **Operation**: Returns cached tags immediately WITHOUT lineage alignment
- **Source**: `cache-fast`
- **Trade-off**: May have stale lineage data if database lineage changed

#### Tier 2: Cache with Lineage Alignment (1-3 seconds)
- **Condition**: Cached tags exist AND (fast_load=false OR lineage_update_timestamp < 10 minutes)
- **Operation**: 
  1. Load cached tags
  2. Batch query database for lineage data (500 products max per query)
  3. Apply lineage overrides to cached tags
- **Source**: `cache+db-lineage`
- **Key Optimization**: Batch query reduces 1000+ individual queries to 1-2 queries

#### Tier 3: Excel Processing (2-8 seconds)
- **Condition**: No cache OR prefer_db=0 AND Excel has data
- **Operation**:
  1. Get tags from Excel processor
  2. Batch align lineage from database
  3. Cache results for 5 minutes
- **Source**: `excel+db-lineage`

#### Tier 4: Database Query (3-15 seconds)
- **Condition**: No Excel data OR prefer_db=1
- **Operation**:
  1. Query `products` table directly (LIMIT 10,000-20,000)
  2. LEFT JOIN with `strains` table for canonical_lineage
  3. Prefer products.Lineage over strains.canonical_lineage
  4. Cache results
- **Source**: `database`

### Database Queries Used:

#### Batch Lineage Alignment Query (Optimized):
```sql
SELECT DISTINCT
    COALESCE(p."Lineage", s.canonical_lineage) AS current_lineage,
    COALESCE(s.strain_name, p."Product Strain") AS current_strain,
    p."Product Name*" AS product_name,
    p.normalized_name AS normalized_name
FROM products p
LEFT JOIN strains s ON TRIM(LOWER(s.strain_name)) = TRIM(LOWER(p."Product Strain"))
WHERE p."Product Name*" IN (?) OR p.normalized_name IN (?)
ORDER BY p.id DESC
LIMIT (batch of up to 500 names)
```

**Performance:**
- Typical execution: 100-500ms for 500 products
- Fallback: Individual queries if batch fails (slower but reliable)
- Critical fix: Batch size capped at 500 to prevent SQLite query timeout

#### Products Table Query:
```sql
SELECT {dynamic_columns}, 
       COALESCE(p."Lineage", s.canonical_lineage) AS preferred_lineage
FROM products p
LEFT JOIN strains s ON TRIM(LOWER(s.strain_name)) = TRIM(LOWER(p."Product Strain"))
ORDER BY p.id DESC
LIMIT 10000
```

**Performance:**
- Typical: 1-3 seconds for 10,000 products
- Includes dynamic column detection via PRAGMA
- Fallback query without strain join if join fails

### Potential Slow Operations:

1. **Lineage Batch Query (500-1000ms)**
   - Large IN clauses with 500+ parameters
   - TRIM(LOWER()) on both sides of JOIN
   - DISTINCT aggregation

2. **Full Database Scan (1-3 seconds)**
   - No filtered query - scans entire products table
   - LEFT JOIN with strains adds overhead
   - Dynamic column detection via PRAGMA table_info

3. **Memory Checks (variable)**
   - Uses psutil.Process() or resource module
   - Runs on every /api/available-tags request
   - Can add 10-50ms if memory is high

4. **First-Time Database Load (5-10 seconds)**
   - ProductDatabase initialization
   - Index creation if needed
   - Connection pooling setup

---

## 3. `/api/initial-data` Endpoint Implementation

**File:** `/Users/adamcordova/Desktop/labelMaker_ QR copy final/app.py` (Lines 14888-15122)

### Key Characteristics:
- **Purpose**: Load initial application state after page refresh
- **Cache Duration**: 5 minutes (300 seconds)
- **Fallback Strategy**: Excel → Database → Empty state
- **Session Dependency**: Loads uploaded file from session if available

### Request Parameters:
```
GET /api/initial-data?
  nocache=1  # Bypass cache (default: use cache if available)
```

### Response Format:
```json
{
  "success": true,
  "data_loaded": true,
  "filename": "upload.xlsx",
  "filepath": "/path/to/file.xlsx",
  "columns": ["column1", "column2", ...],
  "filters": {
    "vendor": [...],
    "brand": [...],
    "productType": [...],
    "lineage": [...],
    "weight": [...],
    "strain": [...],
    "doh": [...],
    "highCbd": [...]
  },
  "available_tags": [...],
  "selected_tags": [],
  "total_records": 1250,
  "source": "excel|database|empty",
  "X-Cache": "HIT|MISS|BYPASS"
}
```

### Processing Logic:

1. **Cache Check** (First)
   - Check session cache with key: `initial_data:{session_id}:{file_path}`
   - If found and nocache != '1': Return cached response (< 100ms)

2. **Session File Loading**
   - Check if uploaded file exists in session: `session['file_path']`
   - Load file if it exists and hasn't been loaded yet
   - Clear invalid session data if file not found

3. **Excel Processing** (If data available)
   - Call `excel_processor.get_available_tags()` for tags
   - Call `excel_processor.get_dynamic_filter_options({})` for filters
   - Clean NaN and None values from filter lists
   - Cache result for 5 minutes

4. **Database Fallback** (If Excel empty)
   - Query all products: `product_db.get_all_products()`
   - Process each product: `process_database_product_for_api(product)`
   - Build filter options from products
   - Only cache if data available (avoids caching empty states)

### Performance Characteristics:

| Scenario | Time | Source |
|----------|------|--------|
| Cached (with data) | 10-50ms | Cache HIT |
| No cache, small file (< 5000 rows) | 500-1500ms | Excel |
| No cache, large file (10,000+ rows) | 2-5s | Excel |
| Database fallback | 2-8s | Database |
| Empty state | 100-200ms | None |

### Filter Processing Pipeline:

```python
# For each product in available_tags:
vendor = processed.get('Vendor') or processed.get('Vendor/Supplier*')
brand = processed.get('Product Brand') or processed.get('Brand')
productType = processed.get('Product Type*') or processed.get('ProductType')
lineage = processed.get('Lineage') or processed.get('canonical_lineage') or processed.get('currentLineage')
weight = processed.get('Weight*') or processed.get('CombinedWeight')
strain = processed.get('Product Strain') or processed.get('strain')
doh = processed.get('DOH') or processed.get('DOH Compliant (Yes/No)')
highCbd = processed.get('High CBD') or processed.get('HighCBD')

# De-duplicate and sort
filters['vendor'] = sorted(set(vendor_values))
filters['brand'] = sorted(set(brand_values))
# ... etc for all 8 filter categories
```

---

## 4. Lineage Alignment Logic

### Purpose
Ensure that the frontend always displays lineage values from the database, not stale values from Excel uploads.

### Key Principle
**Products.Lineage (product-level, user-editable) > Strains.canonical_lineage (strain-level reference)**

This ensures consistency with output generation which uses `get_product_lineage()` (reads products.Lineage).

### Lineage Update Tracking

```python
# When lineage is edited in UI:
session['lineage_update_timestamp'] = time.time()

# In /api/available-tags:
lineage_update_ts = session.get('lineage_update_timestamp')
force_full_refresh = False
if lineage_update_ts:
    force_full_refresh = (time.time() - float(lineage_update_ts)) < 600  # 10 minutes
    
# If recently updated (< 10 mins ago):
# - Disable fast_load cache override
# - Force full lineage alignment from database
```

### Batch Lineage Alignment Process

1. **Collect product names** from cached/Excel tags
2. **Normalize names** using `product_db._normalize_product_name()`
3. **Execute single batch query** with IN clause (max 500 products)
4. **Build lookup map** from query results: `product_name → (lineage, strain)`
5. **Apply to tags** via dictionary lookup: O(1) per tag
6. **Update cache** with aligned tags

### Tag Fields Populated by Alignment

When lineage is found in database:
```python
tag['currentLineage'] = db_lineage_cleaned      # UI prefers this field
tag['canonical_lineage'] = db_lineage_cleaned
tag['Lineage'] = db_lineage_cleaned             # Override original value

# Special handling for CBD products:
if db_lineage in ('CBD', 'CBD_BLEND'):
    tag['Product Strain'] = 'CBD Blend'
    tag['ProductStrain'] = 'CBD Blend'
    tag['productStrain'] = 'CBD Blend'
```

---

## 5. Caching Mechanisms

### Cache Types Implemented

#### 1. Flask-Caching (In-Memory)
**Configuration:**
```python
# app.py line 1690
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
})
```

**Characteristics:**
- In-process memory cache
- Shared across all users (with session key isolation)
- Purged on app restart
- No persistence

**Timeout Overrides:**
- Most endpoints: 300 seconds (5 minutes)
- API responses header: `Cache-Control: private, max-age=60` (1 minute)
- Static assets: `Cache-Control: public, max-age=31536000` (1 year)

#### 2. Session-Based Cache Keys
**Key Generation** (line 7398):
```python
def get_session_cache_key(base_key):
    # base_key: available_tags, initial_data, etc.
    # sid: session ID
    # file_path: loaded Excel file path
    key_str = f"{base_key}:{sid}:{file_path}"
    return hashlib.sha256(key_str.encode()).hexdigest()
```

**Cache Keys Used:**
| Endpoint | Cache Key |
|----------|-----------|
| available-tags | `available_tags_{file_path}` |
| initial-data | `initial_data` |
| web/available-tags | `web_available_tags` |
| available-tags-lite | (no cache) |

#### 3. File-Based Cache (Persistence)
**Location:** `/uploads/cache/available_tags_{store_name}.json`

**Purpose:** Emergency fallback when:
- Database query fails
- Cache is empty
- Server restart recovery

**Operations:**
```python
# Save successful response
save_available_tags_cache(store_name, tags)  # Writes JSON to disk

# Load for fallback
load_available_tags_cache(store_name)  # Reads JSON from disk
```

#### 4. Rate Limiting Cache
**Location:** In-memory dict `rate_limit_data`

**Structure:**
```python
rate_limit_data = {
    '192.168.1.100': [time1, time2, time3, ...],  # Recent request timestamps
    '192.168.1.101': [...]
}
```

**Limits:**
- Max requests per IP: 100 per minute
- Cleanup: Old entries (>60s) are removed
- Returns cached data if limit exceeded (no 429 error)

### Cache Invalidation Strategy

#### Automatic Invalidation
- **On new file upload**: Clear cache for current session
- **On lineage update**: Force full refresh within 10 minutes
- **On store change**: Clear store-specific cache

#### Manual Invalidation
```python
# Clear available tags cache
clear_available_tags_cache(reason="manual-refresh")

# Clear initial data cache
clear_initial_data_cache()
```

#### Cache Cleanup Function
```python
# app.py line 7418
def clear_available_tags_cache(reason=None):
    """Clear cache entries related to available tags and dependent datasets."""
    cache.delete('available_tags_{session_id}_{file_path}')
    cache.delete('initial_data')
    cache.delete('web_available_tags')
    # File-based cache files not auto-deleted
```

### Memory Optimization (PythonAnywhere)

**Environment-based settings** (line 74-94):
```python
if PYTHONANYWHERE_OPTIMIZATION:
    MAX_MEMORY_MB = 425        # Strict limit
    CACHE_SIZE_LIMIT = 50      # Fewer cached items
    BATCH_SIZE_LIMIT = 250     # Smaller batch sizes
else:
    MAX_MEMORY_MB = 500        # Relaxed for local
    CACHE_SIZE_LIMIT = 100
    BATCH_SIZE_LIMIT = 500
```

**Memory Check Before Processing:**
```python
def check_memory_limit():
    """Check if memory usage is within limits."""
    memory_mb = get_memory_usage()
    if memory_mb > MAX_MEMORY_MB:
        cleanup_memory()  # Clear cache + force GC
        return False
    return True
```

---

## 6. Database Operations Performance

### Product Database Lazy Loading
**File:** Line 1293

```python
def get_product_database(store_name=None):
    """Lazy load ProductDatabase to avoid startup delay."""
    global _product_database
    
    db_path, resolved_store = _resolve_database_path_for_store(store_name)
    
    # Check if reload needed
    needs_reload = (
        _product_database is None or 
        current_store_in_db != effective_store or 
        current_db_path != db_path
    )
    
    if needs_reload:
        _product_database = ProductDatabase(db_path)
        _product_database.init_database()
    
    return _product_database
```

**Performance:**
- First access: 2-5 seconds (initialization)
- Subsequent accesses: < 10ms (reuse existing instance)
- Store change: 1-3 seconds (reload for new store)

### Excel Processor Lazy Loading
**File:** Line 1047

```python
def get_excel_processor():
    """Lazy load ExcelProcessor to avoid startup delay."""
    global _excel_processor
    
    with excel_processor_lock:  # Thread-safe
        # Check session file first
        session_file_path = session.get('file_path')
        
        if _excel_processor is None:
            _excel_processor = ExcelProcessor(store_name=processor_store)
        
        # Force reload if session has different file
        if current_file != session_file_path:
            _excel_processor = None  # Force recreation
        
        # Load default file only if no session file and DISABLE_STARTUP_FILE_LOADING=False
        if not session_file_path and not _excel_processor_reset_flag:
            success = _excel_processor.load_file(default_file)
    
    return _excel_processor
```

**Key Optimizations:**
- Thread lock prevents race conditions
- Session file takes priority over default
- Default file loading disabled by default (DISABLE_STARTUP_FILE_LOADING)
- Force reload detection based on file path

### Database Product Processing
**File:** Line 7525

```python
def process_database_product_for_api(db_product):
    """Convert database product to Excel-compatible format."""
    # Create CombinedWeight from Weight* + Units
    # Handle weight conversions for nonclassic products
    # Apply special logic for pre-rolls (JointRatio)
    # Apply special overrides for Moonshot products
    return processed_product
```

**Weight Processing Logic:**
- **Pre-roll/Infused pre-roll**: Use JointRatio field (e.g., "0.5g x 2 Pack")
- **Moonshot products**: Force to 2.5oz
- **Nonclassic products in grams**: Convert to ounces using lookup
- **Classic products**: Keep original format
- **Fallback**: Use Weight* + Units directly

**Performance:**
- Per-product: 1-5ms (mostly dict lookups)
- Batch processing 10,000 products: 20-50 seconds (can be bottleneck!)

---

## 7. Potential Performance Bottlenecks

### Critical Bottlenecks

1. **Lineage Batch Query with Large IN Clause** (100-500ms)
   - Problem: SQLite struggles with IN clauses > 1000 items
   - Solution: Capped at 500 items per query
   - Fallback: Individual queries (slower but reliable)

2. **Full Database Scan Without Filters** (1-3 seconds)
   - Problem: LIMIT 10,000 scans entire table
   - Solution: Add WHERE clause filters if possible
   - Index needed on: `Product Name*`, `normalized_name`, `Product Strain`

3. **Database Product Processing Loop** (20-50 seconds for 10,000+)
   - Problem: 1000+ individual product_db lookups during Moonshot check
   - Solution: Pre-compute weight mapping for nonclassic products

4. **Memory Checks on Every Request** (10-50ms)
   - Problem: psutil.Process() call on every /api/available-tags
   - Solution: Cache memory status for 5 seconds

5. **PRAGMA table_info() Query** (50-100ms)
   - Problem: Dynamic column detection on every fresh DB query
   - Solution: Cache column list per database

### Warnings from Code Comments

**Lines 8054-8068 (Batch Size Limit):**
```python
# CRITICAL FIX: Limit batch size to prevent query timeouts
# SQLite can struggle with very large IN clauses (>1000 items)
MAX_BATCH_SIZE = 500
if len(all_search_names) > MAX_BATCH_SIZE:
    logging.warning(f"Batch query size ({len(all_search_names)}) exceeds limit")
```

**Lines 8108-8127 (Batch Query Fallback):**
```python
except Exception as batch_err:
    logging.warning(f"Batch lineage query failed, using fallback: {batch_err}")
    # Fallback to individual queries (but slower)
```

**Lines 8232-8240 (Database Fallback):**
```python
# If store-specific database doesn't have products table,
# fall back to main database
logging.info(f"Falling back to main database")
```

---

## 8. Request Flow Diagrams

### /api/available-tags Flow
```
Request → Rate Limit Check
        → Memory Check
        → Check fast_load parameter
        ↓
    Cached data exists?
        ├─ YES + fast_load=true → Return cached immediately (< 100ms)
        └─ NO or fast_load=false
            ↓
        Check lineage_update_timestamp
        ├─ Recent (< 10 min) → Force full refresh
        └─ Old → Allow fast load if cached
            ↓
        Has cached data?
        ├─ YES → Batch align lineage from DB (1-3s)
        └─ NO
            ↓
        Has Excel data?
        ├─ YES → Get tags + batch align lineage (2-8s)
        └─ NO
            ↓
        Query database (3-15s)
            ↓
        Cache result (300s)
        ↓
Response
```

### /api/initial-data Flow
```
Request
    ↓
Check session cache
├─ Hit + nocache!=1 → Return cached (< 100ms)
└─ Miss or nocache=1
    ↓
Check session file
├─ File exists → Load it
└─ No file
    ↓
Check Excel processor
├─ Has data → Get tags + filters (500-1500ms)
└─ Empty
    ↓
Database fallback
├─ Available → Process products (2-8s)
└─ Unavailable → Return empty state
    ↓
Cache if data available (300s)
    ↓
Response
```

---

## 9. Configuration Summary

### Key Constants

| Variable | Value | Purpose |
|----------|-------|---------|
| `CACHE_DURATION` | 300s | Initial data cache timeout |
| `RATE_LIMIT_WINDOW` | 60s | Rate limit window |
| `RATE_LIMIT_MAX_REQUESTS` | 100 | Max requests per minute per IP |
| `MAX_BATCH_SIZE` | 500 | Batch query size limit |
| `MAX_MEMORY_MB` | 425-500 | Memory usage limit |
| `CACHE_SIZE_LIMIT` | 50-100 | Max cached items |

### Flask Cache Configuration

```python
CACHE_TYPE: 'SimpleCache'              # In-process memory
CACHE_DEFAULT_TIMEOUT: 300             # 5 minutes
```

### Response Headers

```
X-Cache: HIT|HIT-FAST|MISS
X-Response-Time: {milliseconds}ms
Cache-Control: private, max-age=60     # API responses
Cache-Control: public, max-age=31536000 # Static assets
```

---

## 10. Recommendations for Optimization

### Short-term (Easy Wins)

1. **Cache column list** in ProductDatabase to avoid PRAGMA calls
2. **Pre-compute Moonshot product mapping** instead of per-product lookup
3. **Cache memory status** for 5 seconds instead of checking every request
4. **Add database indexes** on Product Name*, normalized_name, Product Strain

### Medium-term (Moderate Effort)

1. **Implement query result caching** in database layer (memcache/Redis)
2. **Add pagination** to available-tags endpoint (load 500 at a time)
3. **Pre-compute weight conversions** for nonclassic products during DB init
4. **Optimize batch query** with better IN clause handling

### Long-term (Architectural)

1. **Migrate to PostgreSQL** with better query optimization
2. **Implement full-text search** for product name matching
3. **Add materialized views** for filter aggregation
4. **Implement incremental sync** for DB updates instead of full reload

---

## File References

- **Main app file**: `/Users/adamcordova/Desktop/labelMaker_ QR copy final/app.py`
- **Endpoint implementations**: Lines 7688-8615, 14888-15122, 10261-10395, 14812-14852
- **Caching setup**: Lines 509, 1690-1692
- **Cache functions**: Lines 238-264, 7398-7430, 14854-14886
- **Database functions**: Lines 639-721, 1293-1329, 1047-1160, 7525-7630, 2074-2160
- **Performance monitoring**: Lines 102-138
- **Configuration**: Lines 74-99

