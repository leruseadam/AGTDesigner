# API Endpoints - Quick Reference Guide

## Endpoint Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TAG LOADING API ENDPOINTS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  /api/available-tags          Primary endpoint (7688-8615)         │
│  ├─ Purpose: Load all product tags with lineage alignment         │
│  ├─ Cache: 5 min (session-based key)                              │
│  ├─ Fast mode: <100ms (cached, no alignment)                      │
│  └─ Full mode: 1-15s (fresh query with alignment)                 │
│                                                                     │
│  /api/initial-data            Init endpoint (14888-15122)          │
│  ├─ Purpose: Load initial app state after page refresh            │
│  ├─ Cache: 5 min (per session)                                    │
│  ├─ Response: tags + filters + columns + file info                │
│  └─ Time: 10ms-8s depending on source                             │
│                                                                     │
│  /api/web/available-tags      Web endpoint (10261-10395)           │
│  ├─ Purpose: Web-optimized tags with compression                  │
│  ├─ Cache: Aggressive (5 min)                                     │
│  └─ Time: <100ms cached, 2-8s fresh                               │
│                                                                     │
│  /api/available-tags-lite     Lite endpoint (14812-14852)          │
│  ├─ Purpose: Low-memory version (max 1000 tags)                   │
│  ├─ Cache: No caching                                             │
│  └─ Time: 1-2s                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Request/Response Formats

### /api/available-tags

```
REQUEST:
GET /api/available-tags?nocache=1&prefer_db=1&fast_load=0

RESPONSE (200 OK):
{
  "tags": [
    {
      "Product Name*": "Blue Dream",
      "Product Type*": "Flower",
      "Lineage": "HYBRID",
      "currentLineage": "HYBRID",
      "Weight*": "1",
      "Units": "oz",
      "CombinedWeight": "1oz",
      ...
    },
    ...
  ],
  "total_count": 1250,
  "source": "cache-fast|cache+db-lineage|excel+db-lineage|database",
  "X-Cache": "HIT-FAST|HIT|MISS",
  "X-Response-Time": "45ms"
}
```

### /api/initial-data

```
REQUEST:
GET /api/initial-data?nocache=0

RESPONSE (200 OK):
{
  "success": true,
  "data_loaded": true,
  "filename": "products.xlsx",
  "filepath": "/path/to/products.xlsx",
  "columns": ["Product Name*", "Product Type*", "Lineage", ...],
  "filters": {
    "vendor": ["Vendor A", "Vendor B"],
    "brand": ["Brand 1", "Brand 2"],
    "productType": ["Flower", "Concentrate"],
    "lineage": ["HYBRID", "SATIVA"],
    "weight": ["1oz", "2oz"],
    "strain": ["Blue Dream"],
    "doh": ["Yes", "No"],
    "highCbd": ["Yes", "No"]
  },
  "available_tags": [...],
  "selected_tags": [],
  "total_records": 1250,
  "source": "excel|database|empty",
  "X-Cache": "HIT|MISS|BYPASS"
}
```

## Performance Tiers

```
┌──────────────────────────────────────────────────────────────┐
│            /api/available-tags PERFORMANCE TIERS             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ TIER 1: FAST CACHE (< 100ms) ⚡⚡⚡ FASTEST                 │
│ ├─ Condition: Cached + fast_load=true + no lineage edits   │
│ ├─ Operation: Return cached tags immediately               │
│ ├─ Trade-off: May have stale lineage                       │
│ └─ Source: Memory cache                                    │
│                                                              │
│ TIER 2: ALIGNED CACHE (1-3s) ⚡⚡ FAST                      │
│ ├─ Condition: Cached + (fast_load=false OR lineage edited) │
│ ├─ Operation: Load cached + align DB lineage              │
│ ├─ Trade-off: Extra 1-3s for accuracy                      │
│ └─ Source: Memory cache + Database query                  │
│                                                              │
│ TIER 3: EXCEL PROCESSING (2-8s) ⚡ NORMAL                  │
│ ├─ Condition: No cache + Excel has data                    │
│ ├─ Operation: Get Excel tags + align DB lineage           │
│ ├─ Trade-off: Slower but fresh data                        │
│ └─ Source: Excel file + Database query                    │
│                                                              │
│ TIER 4: DATABASE QUERY (3-15s)   SLOWEST                   │
│ ├─ Condition: No Excel + prefer_db=true                    │
│ ├─ Operation: Query products table directly                │
│ ├─ Trade-off: Slowest but always available                 │
│ └─ Source: SQLite database                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Lineage Alignment Flow

```
Cached Tags
    ↓
Query Database for Lineage
    ├─ Method: Batch query (max 500 products)
    ├─ SQL: IN clause with product names
    ├─ Time: 100-500ms
    └─ Fallback: Individual queries if batch fails
    ↓
Build Lookup Map
    ├─ Key: Product Name
    ├─ Value: (Lineage, Strain)
    └─ Lookup time: O(1) per product
    ↓
Apply to Tags
    ├─ For each tag:
    │  ├─ tag['currentLineage'] = db_lineage
    │  ├─ tag['canonical_lineage'] = db_lineage
    │  └─ tag['Lineage'] = db_lineage
    └─ Update cache with aligned tags
```

## Cache Architecture

```
┌─────────────────────────────────────────────────────────┐
│             4-LAYER CACHING SYSTEM                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  LAYER 1: Flask In-Memory Cache                        │
│  ├─ Type: SimpleCache                                  │
│  ├─ TTL: 5 minutes                                     │
│  ├─ Isolation: Per session ID + file path              │
│  └─ Purged: On app restart                             │
│                                                         │
│  LAYER 2: Session-Based Keys                           │
│  ├─ Key: SHA256(base_key + sid + file_path)            │
│  ├─ Examples:                                          │
│  │  ├─ available_tags_{file_path}                      │
│  │  ├─ initial_data                                    │
│  │  └─ web_available_tags                              │
│  └─ Check: Every request (< 1ms)                       │
│                                                         │
│  LAYER 3: File-Based Persistence                       │
│  ├─ Location: /uploads/cache/available_tags_{store}.json
│  ├─ Purpose: Emergency fallback                        │
│  ├─ Lifetime: Until manual cleanup                     │
│  └─ Recovery: On cache miss or DB error                │
│                                                         │
│  LAYER 4: Rate Limit Cache                             │
│  ├─ Type: In-memory dict per IP                        │
│  ├─ Limit: 100 requests/minute per IP                  │
│  ├─ Cleanup: Entries >60s old removed                  │
│  └─ Response: Returns cached data if exceeded          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Database Operations

```
Lazy Loading Pattern:

ProductDatabase (Line 1293):
  First access:   2-5 seconds (init + indexes)
  Reuse:          < 10ms
  Store change:   1-3 seconds (reload)

ExcelProcessor (Line 1047):
  First access:   1-5 seconds (load file)
  Reuse:          < 10ms
  File change:    1-5 seconds (reload)

Product Processing (Line 7525):
  Per product:    1-5ms
  Batch (10k):    20-50 seconds ⚠️ SLOW
  
  Weight Logic:
  ├─ Pre-roll:         Use JointRatio
  ├─ Moonshot:         Force 2.5oz
  ├─ Nonclassic:       Convert grams → oz
  └─ Classic:          Keep original
```

## Request Parameters

```
/api/available-tags

nocache=1|0
├─ 1: Bypass cache, force fresh query
└─ 0 (default): Use cache if available

prefer_db=1|0
├─ 1: Skip Excel, use database only
└─ 0 (default): Try Excel first

fast_load=1|0
├─ 1 (default): Skip lineage alignment (< 100ms)
└─ 0: Force lineage alignment (1-3s slower)

platform=windows
└─ Web client optimization hint


/api/initial-data

nocache=1|0
├─ 1: Bypass cache, force fresh query
└─ 0 (default): Use cache if available
```

## Response Headers

```
X-Cache: HIT|HIT-FAST|MISS
├─ HIT: Returned from cache with full processing
├─ HIT-FAST: Returned from cache without processing
└─ MISS: Not in cache, fresh query

X-Response-Time: {milliseconds}ms
└─ Total time in milliseconds

Cache-Control: private, max-age=60
└─ Browser cache: 1 minute for API responses

Vary: Accept-Encoding
└─ Compression support indicated
```

## Common Issues & Fixes

```
Issue 1: Tags take 10+ seconds to load
├─ Check logs for "Batch query size exceeds limit"
├─ Try: ?nocache=1&fast_load=0
├─ Check: Database indexes on Product Name*, normalized_name
└─ Root: Large dataset + lineage alignment + no indexes

Issue 2: Lineage doesn't update after edit
├─ Check: session['lineage_update_timestamp']
├─ Try: ?nocache=1&fast_load=0
├─ Root: Recent edit (< 10 min) + cache not cleared
└─ Fix: Manual cache clear + page reload

Issue 3: Memory usage high (425MB limit)
├─ Check: Every /api/available-tags request checks memory
├─ Try: Reduce batch size in config
├─ Root: Cache + memory checks + large dataset
└─ Fix: Clear cache more aggressively on PythonAnywhere

Issue 4: Batch query fails, falls back to slow queries
├─ Check logs: "Batch lineage query failed"
├─ Root: IN clause > 500 items or DB connection issue
├─ Impact: Each product gets individual query (slow)
└─ Time: Can add 5-10 seconds per 100 products
```

## Performance Tuning

```
QUICK WINS (Easy):
├─ Cache column list (avoid PRAGMA table_info)
├─ Cache memory status (check every 5s, not every request)
├─ Pre-compute weight conversions for Moonshot
└─ Add DB indexes on Product Name*, normalized_name

MEDIUM EFFORT:
├─ Implement pagination (load 500 at a time)
├─ Redis/memcache layer for batch query results
├─ Pre-compute lineage mappings during init
└─ Optimize IN clause with better parameter handling

LONG TERM:
├─ Migrate to PostgreSQL (better IN clause handling)
├─ Add full-text search on product names
├─ Materialized views for filter aggregation
└─ Incremental sync instead of full reload
```

## Configuration Values

```
CACHE_DURATION = 300              # 5 minutes
MAX_BATCH_SIZE = 500              # SQL IN clause limit
MAX_MEMORY_MB = 425               # PythonAnywhere limit
CACHE_SIZE_LIMIT = 50             # Max items in cache
RATE_LIMIT_WINDOW = 60            # 1 minute
RATE_LIMIT_MAX_REQUESTS = 100     # Per minute per IP

# Can override with environment variables:
export MAX_MEMORY_MB=500
export CACHE_SIZE_LIMIT=100
export BATCH_SIZE_LIMIT=500
```

## File References

```
Main Implementation:  /app.py
  ├─ /api/available-tags        Lines 7688-8615
  ├─ /api/initial-data          Lines 14888-15122
  ├─ /api/web/available-tags    Lines 10261-10395
  ├─ /api/available-tags-lite   Lines 14812-14852
  
Caching:
  ├─ Cache initialization       Lines 509, 1690-1692
  ├─ get_session_cache_key()    Line 7398
  ├─ Cache functions            Lines 238-264, 7418
  ├─ save_available_tags_cache() Line 244
  └─ load_available_tags_cache() Line 254

Database:
  ├─ get_product_database()           Line 1293
  ├─ get_excel_processor()            Line 1047
  ├─ get_session_excel_processor()    Line 2074
  ├─ process_database_product_for_api Line 7525
  └─ get_current_store_name()         Line 639

Performance:
  ├─ Memory monitoring          Lines 102-138
  ├─ Rate limiting             Lines 512-516
  ├─ Configuration             Lines 74-99
  └─ Performance headers       Lines 1697-1709
```

