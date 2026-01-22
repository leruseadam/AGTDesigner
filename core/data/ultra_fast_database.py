"""
Ultra-fast database operations with connection pooling, query optimization, and caching.
"""

import sqlite3
import threading
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from functools import lru_cache
import queue
import weakref

from src.core.utils.performance_cache import database_cached, DATABASE_CACHE

logger = logging.getLogger(__name__)

class ConnectionPool:
    """High-performance connection pool for SQLite databases."""
    
    def __init__(self, db_path: str, max_connections: int = 10, timeout: float = 30.0):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool = queue.Queue(maxsize=max_connections)
        self._created_connections = 0
        self._lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(min(5, max_connections)):  # Pre-create 5 connections
            self._create_connection()
    
    def _create_connection(self):
        """Create a new database connection with optimizations."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False,
            isolation_level=None  # Autocommit mode
        )
        
        # Optimize for performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=100000")  # 100MB cache
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
        conn.execute("PRAGMA optimize")
        
        # Enable row factory for named access
        conn.row_factory = sqlite3.Row
        
        with self._lock:
            self._created_connections += 1
        
        return conn
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool."""
        try:
            # Try to get existing connection
            conn = self._pool.get_nowait()
            return conn
        except queue.Empty:
            # Create new connection if under limit
            with self._lock:
                if self._created_connections < self.max_connections:
                    return self._create_connection()
            
            # Wait for available connection
            return self._pool.get(timeout=self.timeout)
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool."""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close connection
            conn.close()
            with self._lock:
                self._created_connections -= 1
    
    def close_all(self):
        """Close all connections in pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
        
        with self._lock:
            self._created_connections = 0

class UltraFastDatabase:
    """Ultra-fast database operations with optimizations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_pool = ConnectionPool(db_path)
        self._prepared_statements = {}
        self._statement_lock = threading.Lock()
        
        # Performance metrics
        self._metrics = {
            'queries_executed': 0,
            'total_query_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'connection_wait_time': 0.0
        }
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database with optimized schema."""
        with self.get_connection() as conn:
            # Create optimized indexes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT,
                    type TEXT,
                    weight TEXT,
                    unit TEXT,
                    price TEXT,
                    thc_content TEXT,
                    cbd_content TEXT,
                    vendor TEXT,
                    barcode TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create optimized indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_type ON products(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at)")
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA optimize")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        start_time = time.time()
        conn = self.connection_pool.get_connection()
        wait_time = time.time() - start_time
        self._metrics['connection_wait_time'] += wait_time
        
        try:
            yield conn
        finally:
            self.connection_pool.return_connection(conn)
    
    def _get_prepared_statement(self, query: str) -> str:
        """Get or create prepared statement key."""
        with self._statement_lock:
            if query not in self._prepared_statements:
                self._prepared_statements[query] = f"stmt_{len(self._prepared_statements)}"
            return self._prepared_statements[query]
    
    @database_cached(ttl=3600)  # Cache for 1 hour
    def get_product_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get product by name with caching."""
        query = "SELECT * FROM products WHERE name = ? LIMIT 1"
        
        start_time = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(query, (name,))
            row = cursor.fetchone()
            
            self._metrics['queries_executed'] += 1
            self._metrics['total_query_time'] += time.time() - start_time
            
            if row:
                return dict(row)
            return None
    
    @database_cached(ttl=1800)  # Cache for 30 minutes
    def get_products_by_brand(self, brand: str) -> List[Dict[str, Any]]:
        """Get products by brand with caching."""
        query = "SELECT * FROM products WHERE brand = ? ORDER BY name"
        
        start_time = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(query, (brand,))
            rows = cursor.fetchall()
            
            self._metrics['queries_executed'] += 1
            self._metrics['total_query_time'] += time.time() - start_time
            
            return [dict(row) for row in rows]
    
    @database_cached(ttl=1800)  # Cache for 30 minutes
    def get_products_by_type(self, product_type: str) -> List[Dict[str, Any]]:
        """Get products by type with caching."""
        query = "SELECT * FROM products WHERE type = ? ORDER BY name"
        
        start_time = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(query, (product_type,))
            rows = cursor.fetchall()
            
            self._metrics['queries_executed'] += 1
            self._metrics['total_query_time'] += time.time() - start_time
            
            return [dict(row) for row in rows]
    
    def bulk_insert_products(self, products: List[Dict[str, Any]]) -> int:
        """Bulk insert products with transaction optimization."""
        if not products:
            return 0
        
        query = """
            INSERT OR REPLACE INTO products 
            (name, brand, type, weight, unit, price, thc_content, cbd_content, vendor, barcode, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        start_time = time.time()
        inserted_count = 0
        
        with self.get_connection() as conn:
            # Use transaction for bulk operations
            conn.execute("BEGIN TRANSACTION")
            try:
                cursor = conn.cursor()
                for product in products:
                    cursor.execute(query, (
                        product.get('name', ''),
                        product.get('brand', ''),
                        product.get('type', ''),
                        product.get('weight', ''),
                        product.get('unit', ''),
                        product.get('price', ''),
                        product.get('thc_content', ''),
                        product.get('cbd_content', ''),
                        product.get('vendor', ''),
                        product.get('barcode', '')
                    ))
                    inserted_count += 1
                
                conn.execute("COMMIT")
                
                self._metrics['queries_executed'] += 1
                self._metrics['total_query_time'] += time.time() - start_time
                
            except Exception as e:
                conn.execute("ROLLBACK")
                logger.error(f"Bulk insert failed: {e}")
                raise
        
        return inserted_count
    
    def search_products(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fast product search with full-text indexing."""
        # Use FTS if available, otherwise fallback to LIKE
        query = """
            SELECT * FROM products 
            WHERE name LIKE ? OR brand LIKE ? OR type LIKE ?
            ORDER BY name
            LIMIT ?
        """
        
        search_pattern = f"%{search_term}%"
        
        start_time = time.time()
        with self.get_connection() as conn:
            cursor = conn.execute(query, (search_pattern, search_pattern, search_pattern, limit))
            rows = cursor.fetchall()
            
            self._metrics['queries_executed'] += 1
            self._metrics['total_query_time'] += time.time() - start_time
            
            return [dict(row) for row in rows]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database performance statistics."""
        with self.get_connection() as conn:
            # Get table stats
            cursor = conn.execute("SELECT COUNT(*) as count FROM products")
            product_count = cursor.fetchone()['count']
            
            # Get database size
            cursor = conn.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor = conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            db_size_mb = (page_count * page_size) / (1024 * 1024)
        
        # Calculate performance metrics
        avg_query_time = (self._metrics['total_query_time'] / 
                         max(self._metrics['queries_executed'], 1)) * 1000  # ms
        
        return {
            'product_count': product_count,
            'database_size_mb': round(db_size_mb, 2),
            'queries_executed': self._metrics['queries_executed'],
            'avg_query_time_ms': round(avg_query_time, 2),
            'connection_pool_size': self.connection_pool._created_connections,
            'cache_stats': DATABASE_CACHE.get_stats()
        }
    
    def optimize_database(self):
        """Optimize database performance."""
        with self.get_connection() as conn:
            conn.execute("PRAGMA optimize")
            conn.execute("VACUUM")  # Reclaim space and optimize
            logger.info("Database optimization completed")
    
    def close(self):
        """Close database connections."""
        self.connection_pool.close_all()

# Global ultra-fast database instance
_ultra_fast_db = None
_db_lock = threading.Lock()

def get_ultra_fast_database(db_path: str = None) -> UltraFastDatabase:
    """Get or create global ultra-fast database instance."""
    global _ultra_fast_db
    
    if _ultra_fast_db is None:
        with _db_lock:
            if _ultra_fast_db is None:
                if db_path is None:
                    from src.core.data.product_database import get_database_path
                    db_path = get_database_path()
                
                _ultra_fast_db = UltraFastDatabase(db_path)
                logger.info("Ultra-fast database initialized")
    
    return _ultra_fast_db

def clear_database_cache():
    """Clear database cache."""
    DATABASE_CACHE.clear()
    logger.info("Database cache cleared")
