"""
Comprehensive Performance Optimization Module
Implements database indexing, query optimization, and caching improvements
"""

import sqlite3
import logging
import time
from functools import wraps
from typing import Any, Dict, Optional
import hashlib
import json

logger = logging.getLogger(__name__)


class PerformanceBooster:
    """Comprehensive performance optimization for the application"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def optimize_database(self):
        """Apply all database optimizations"""
        logger.info("🚀 Starting database performance optimization...")
        
        try:
            conn = sqlite3.connect(self.db_path, timeout=60.0)
            cursor = conn.cursor()
            
            # Step 1: Add missing indexes for common queries
            self._add_performance_indexes(cursor, conn)
            
            # Step 2: Optimize database settings
            self._optimize_database_settings(cursor)
            
            # Step 3: Analyze tables for query planner
            self._analyze_tables(cursor, conn)
            
            # Step 4: Vacuum database to reclaim space and optimize
            self._vacuum_database(conn)
            
            conn.close()
            logger.info("✅ Database optimization complete!")
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            raise
    
    def _add_performance_indexes(self, cursor, conn):
        """Add critical indexes for frequently queried columns"""
        logger.info("📊 Adding performance indexes...")
        
        indexes = [
            # Product name lookups (most common query)
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(`Product Name*`)",
            
            # Price lookups
            "CREATE INDEX IF NOT EXISTS idx_products_price ON products(`Price* (Tier Name for Bulk)`)",
            
            # Weight lookups
            "CREATE INDEX IF NOT EXISTS idx_products_weight ON products(`Weight*`)",
            
            # Product type filtering
            "CREATE INDEX IF NOT EXISTS idx_products_type ON products(`Product Type*`)",
            
            # Vendor filtering
            "CREATE INDEX IF NOT EXISTS idx_products_vendor ON products(`Vendor/Supplier*`)",
            
            # Brand filtering
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(`Product Brand`)",
            
            # Composite index for common filter combinations
            "CREATE INDEX IF NOT EXISTS idx_products_type_vendor ON products(`Product Type*`, `Vendor/Supplier*`)",
            
            # Composite index for type and brand
            "CREATE INDEX IF NOT EXISTS idx_products_type_brand ON products(`Product Type*`, `Product Brand`)",
            
            # THC/CBD filtering
            "CREATE INDEX IF NOT EXISTS idx_products_thc ON products(`THC test result`)",
            "CREATE INDEX IF NOT EXISTS idx_products_cbd ON products(`CBD test result`)",
            
            # DOH compliance filtering
            "CREATE INDEX IF NOT EXISTS idx_products_doh ON products(`DOH Compliant (Yes/No)`)",
            
            # Strain lookups
            "CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(`strain_name`)",
            "CREATE INDEX IF NOT EXISTS idx_strains_type ON strains(`product_type`)",
            
            # Composite index for strain + type (common in queries)
            "CREATE INDEX IF NOT EXISTS idx_strains_name_type ON strains(`strain_name`, `product_type`)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                logger.warning(f"Could not create index: {e}")
        
        conn.commit()
        logger.info("✅ Indexes created successfully")
    
    def _optimize_database_settings(self, cursor):
        """Optimize SQLite settings for better performance"""
        logger.info("⚙️  Optimizing database settings...")
        
        optimizations = [
            # Enable Write-Ahead Logging for better concurrency
            "PRAGMA journal_mode=WAL",
            
            # Increase cache size to 20MB (default is ~2MB)
            "PRAGMA cache_size=-20000",
            
            # Store temp tables in memory
            "PRAGMA temp_store=MEMORY",
            
            # Faster synchronous mode (still safe)
            "PRAGMA synchronous=NORMAL",
            
            # Increase page size for better I/O
            "PRAGMA page_size=4096",
            
            # Auto vacuum to keep database compact
            "PRAGMA auto_vacuum=INCREMENTAL",
            
            # Memory-mapped I/O for faster reads
            "PRAGMA mmap_size=268435456",  # 256MB
            
            # Longer busy timeout for concurrent access
            "PRAGMA busy_timeout=60000",  # 60 seconds
        ]
        
        for pragma in optimizations:
            try:
                cursor.execute(pragma)
                result = cursor.fetchone()
                logger.info(f"✓ {pragma.split('=')[0]} = {result[0] if result else 'set'}")
            except Exception as e:
                logger.warning(f"Could not set {pragma}: {e}")
    
    def _analyze_tables(self, cursor, conn):
        """Analyze tables to update statistics for query optimizer"""
        logger.info("📈 Analyzing tables for query optimizer...")
        
        try:
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                try:
                    cursor.execute(f"ANALYZE {table}")
                    logger.info(f"✓ Analyzed table: {table}")
                except Exception as e:
                    logger.warning(f"Could not analyze {table}: {e}")
            
            conn.commit()
            logger.info("✅ Table analysis complete")
            
        except Exception as e:
            logger.error(f"Error analyzing tables: {e}")
    
    def _vacuum_database(self, conn):
        """Vacuum database to reclaim space and optimize storage"""
        logger.info("🧹 Vacuuming database...")
        
        try:
            # Vacuum requires no transaction
            conn.execute("VACUUM")
            logger.info("✅ Database vacuumed successfully")
        except Exception as e:
            logger.warning(f"Could not vacuum database: {e}")


class QueryCache:
    """High-performance query result cache"""
    
    def __init__(self, max_size: int = 5000, ttl: int = 600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, query: str, params: tuple = ()) -> str:
        """Generate cache key from query and parameters"""
        key_str = f"{query}:{str(params)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, params: tuple = ()) -> Optional[Any]:
        """Get cached query result"""
        key = self._generate_key(query, params)
        
        if key in self.cache:
            # Check if expired
            if time.time() - self.access_times[key] < self.ttl:
                self.hit_count += 1
                return self.cache[key]
            else:
                # Expired, remove from cache
                del self.cache[key]
                del self.access_times[key]
        
        self.miss_count += 1
        return None
    
    def set(self, query: str, params: tuple, result: Any):
        """Cache query result"""
        key = self._generate_key(query, params)
        
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total
        }


def cached_query(cache: QueryCache, ttl: Optional[int] = None):
    """Decorator to cache database query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key, ())
            if result is not None:
                return result
            
            # Execute query
            result = func(self, *args, **kwargs)
            
            # Cache result
            cache.set(cache_key, (), result)
            
            return result
        return wrapper
    return decorator


class ConnectionPool:
    """Simple connection pool for database connections"""
    
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.in_use = set()
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool"""
        # Try to get an available connection
        for conn in self.connections:
            if conn not in self.in_use:
                self.in_use.add(conn)
                return conn
        
        # Create new connection if pool not full
        if len(self.connections) < self.pool_size:
            conn = self._create_connection()
            self.connections.append(conn)
            self.in_use.add(conn)
            return conn
        
        # Pool exhausted, wait and retry
        time.sleep(0.1)
        return self.get_connection()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new optimized database connection"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=60.0,
            check_same_thread=False
        )
        
        # Optimize connection
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA cache_size=-20000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=60000")
        
        return conn
    
    def release_connection(self, conn: sqlite3.Connection):
        """Release connection back to pool"""
        if conn in self.in_use:
            self.in_use.remove(conn)
    
    def close_all(self):
        """Close all connections in pool"""
        for conn in self.connections:
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
        
        self.connections.clear()
        self.in_use.clear()


def optimize_all_databases():
    """Optimize all database files in the application"""
    import os
    from glob import glob
    
    logger.info("🚀 Starting comprehensive database optimization...")
    
    # Find all database files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_patterns = [
        os.path.join(base_dir, "*.db"),
        os.path.join(base_dir, "uploads", "*.db"),
    ]
    
    db_files = []
    for pattern in db_patterns:
        db_files.extend(glob(pattern))
    
    if not db_files:
        logger.warning("No database files found to optimize")
        return
    
    logger.info(f"Found {len(db_files)} database(s) to optimize")
    
    for db_path in db_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"Optimizing: {os.path.basename(db_path)}")
        logger.info(f"{'='*60}")
        
        try:
            booster = PerformanceBooster(db_path)
            booster.optimize_database()
        except Exception as e:
            logger.error(f"Failed to optimize {db_path}: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ All database optimizations complete!")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run optimization
    optimize_all_databases()

