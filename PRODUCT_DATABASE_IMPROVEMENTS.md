# Product Database Improvements

## Overview

The product database has been enhanced to track vendor, brand, and product type information similar to the Excel version. The system now automatically adds data to the database with every upload and provides comprehensive statistics and reporting.

## Features

### 1. Automatic Data Integration
- **Background Processing**: Data is automatically added to the database during file uploads
- **Non-blocking**: Database integration happens in the background, so uploads remain fast
- **Batch Processing**: Large files are processed in batches for better performance
- **Error Handling**: Robust error handling ensures uploads continue even if database operations fail

### 2. Comprehensive Data Tracking
- **Vendor Information**: Tracks all vendors with product counts and statistics
- **Brand Information**: Tracks all brands with their associated vendors and product types
- **Product Types**: Categorizes products by type (flower, concentrate, edible, etc.)
- **Strain Information**: For classic product types, tracks strain lineage and relationships
- **Occurrence Tracking**: Counts how many times each product/vendor/brand combination appears

### 3. Enhanced Statistics
The database now provides detailed statistics including:

#### Basic Statistics (`/api/database-stats`)
- Total strains and products
- Lineage distribution
- Top strains by occurrence
- **NEW**: Vendor statistics (top 20 vendors)
- **NEW**: Brand statistics (top 20 brands)
- **NEW**: Product type statistics (top 20 types)
- **NEW**: Vendor-brand combinations (top 15)

#### Detailed Vendor Statistics (`/api/database-vendor-stats`)
- Complete vendor list with product counts
- Complete brand list with vendor associations
- Complete product type list with vendor/brand associations
- Vendor-brand combination analysis
- Summary statistics

### 4. Database Schema

The product database includes the following key tables:

#### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    strain_id INTEGER,
    product_type TEXT NOT NULL,      -- NEW: Product type tracking
    vendor TEXT,                     -- NEW: Vendor tracking
    brand TEXT,                      -- NEW: Brand tracking
    description TEXT,
    weight TEXT,
    units TEXT,
    price TEXT,
    lineage TEXT,
    first_seen_date TEXT NOT NULL,
    last_seen_date TEXT NOT NULL,
    total_occurrences INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (strain_id) REFERENCES strains (id),
    UNIQUE(product_name, vendor, brand)
)
```

#### Strains Table
```sql
CREATE TABLE strains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strain_name TEXT UNIQUE NOT NULL,
    normalized_name TEXT NOT NULL,
    canonical_lineage TEXT,
    first_seen_date TEXT NOT NULL,
    last_seen_date TEXT NOT NULL,
    total_occurrences INTEGER DEFAULT 1,
    lineage_confidence REAL DEFAULT 0.0,
    sovereign_lineage TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

## API Endpoints

### Database Statistics
- `GET /api/database-stats` - Get comprehensive database statistics
- `GET /api/database-vendor-stats` - Get detailed vendor/brand statistics
- `GET /api/database-export` - Export database to Excel file
- `GET /api/database-view` - View database contents in JSON format

### Product Database Control
- `GET /api/product-db/status` - Check if integration is enabled
- `POST /api/product-db/enable` - Enable database integration
- `POST /api/product-db/disable` - Disable database integration

### Performance Monitoring
- `GET /api/performance` - Get performance statistics including database metrics

## Usage Examples

### Check Database Statistics
```bash
curl http://localhost:5000/api/database-stats
```

### View Vendor Information
```bash
curl http://localhost:5000/api/database-vendor-stats
```

### Export Database
```bash
curl http://localhost:5000/api/database-export -o product_database.xlsx
```

### Test Integration
```bash
python test_product_database_integration.py
```

## Data Processing Logic

### Upload Processing
1. **File Upload**: User uploads Excel file
2. **Background Integration**: System schedules database integration in background thread
3. **Batch Processing**: Data is processed in batches of 50 records
4. **Strain Processing**: For classic product types, strains are added/updated
5. **Product Processing**: All products are added/updated with vendor/brand/type info
6. **Statistics Update**: Database statistics are updated automatically

### Product Type Classification
- **Classic Types**: flower, pre-roll, concentrate, vape cartridge, etc.
  - These get full strain processing and lineage tracking
- **Non-Classic Types**: edible, tincture, topical, etc.
  - These get product tracking but no strain processing
  - Lineage is set to 'MIXED' or 'CBD' based on content

### Vendor/Brand Tracking
- **Vendor**: Extracted from 'Vendor/Supplier*' column
- **Brand**: Extracted from 'Product Brand' column
- **Product Type**: Extracted from 'Product Type*' column
- **Unique Combinations**: Products are uniquely identified by (name, vendor, brand)

## Performance Optimizations

### Caching
- **Strain Cache**: Frequently accessed strain information is cached
- **Product Cache**: Product lookups are cached for performance
- **Statistics Cache**: Database statistics are cached and updated periodically

### Background Processing
- **Non-blocking**: Database operations don't block file uploads
- **Daemon Threads**: Background processing doesn't prevent app shutdown
- **Batch Processing**: Large files are processed in manageable chunks

### Database Optimization
- **Indexes**: Optimized indexes on frequently queried columns
- **Connection Pooling**: Database connections are reused efficiently
- **Lazy Initialization**: Database is only initialized when first needed

## Monitoring and Maintenance

### Performance Monitoring
- Query timing statistics
- Cache hit rates
- Memory usage tracking
- Background processing status

### Database Maintenance
- Automatic cache cleanup
- Connection pool management
- Statistics updates
- Error logging and recovery

## Testing

Run the test script to verify integration:
```bash
python test_product_database_integration.py
```

This will test:
- App connectivity
- Database status
- Statistics endpoints
- File upload integration
- Performance monitoring

## Future Enhancements

Potential future improvements:
- Advanced vendor/brand analytics
- Product trend analysis
- Automated lineage suggestions
- Vendor performance metrics
- Product quality scoring
- Integration with external databases 