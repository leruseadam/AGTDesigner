import sqlite3
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
from pathlib import Path
from functools import lru_cache
import threading

logger = logging.getLogger(__name__)

class OptimizedProductDatabase:
    """Optimized database for storing and managing product and strain information."""
    
    def __init__(self, db_path: str = "product_database.db"):
        self.db_path = db_path
        self._connection_pool = {}
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._initialized = False
        self._init_lock = threading.Lock()
        self._connection_lock = threading.Lock()  # Lock for connection creation
        
        # Database connection settings
        self._connection_timeout = 30.0  # 30 seconds timeout for connection operations
        self._busy_timeout = 30000  # 30 seconds in milliseconds for SQLite busy_timeout
        
        # Performance timing
        self._timing_stats = {
            'queries': 0,
            'total_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _create_connection(self):
        """Create a new database connection with proper settings for concurrent access."""
        max_retries = 5
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Create connection with timeout and thread safety
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=self._connection_timeout,
                    check_same_thread=False  # Allow connections from different threads
                )
                
                # CRITICAL: Enable WAL mode immediately for better concurrent access
                conn.execute("PRAGMA journal_mode = WAL")
                
                # CRITICAL: Set busy_timeout to handle locked database gracefully
                conn.execute(f"PRAGMA busy_timeout = {self._busy_timeout}")
                
                # Performance optimizations
                conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and speed
                conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
                conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temp tables
                
                # Enable row factory for named access
                conn.row_factory = sqlite3.Row
                
                logger.debug(f"Created new database connection (attempt {attempt + 1})")
                return conn
                
            except sqlite3.OperationalError as e:
                error_str = str(e).lower()
                if "database is locked" in error_str and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Database locked during connection creation (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to create database connection after {attempt + 1} attempts: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error creating database connection: {e}")
                raise
    
    def _get_connection(self):
        """Get a database connection, reusing if possible. Creates new connection with proper settings."""
        thread_id = threading.get_ident()
        
        # Check if we have a valid connection for this thread
        if thread_id in self._connection_pool:
            conn = self._connection_pool[thread_id]
            try:
                # Test if connection is still valid
                conn.execute("SELECT 1")
                return conn
            except (sqlite3.ProgrammingError, sqlite3.OperationalError, sqlite3.DatabaseError):
                # Connection is invalid, remove it and create a new one
                logger.warning(f"Connection for thread {thread_id} is invalid, creating new one")
                try:
                    conn.close()
                except:
                    pass
                del self._connection_pool[thread_id]
        
        # Create new connection with proper locking to prevent race conditions
        with self._connection_lock:
            # Double-check after acquiring lock
            if thread_id in self._connection_pool:
                return self._connection_pool[thread_id]
            
            # Create new connection with proper settings
            conn = self._create_connection()
            self._connection_pool[thread_id] = conn
            return conn

    def _clear_connection(self):
        """Clear the current thread's connection from the pool."""
        thread_id = threading.get_ident()
        with self._connection_lock:
            if thread_id in self._connection_pool:
                try:
                    conn = self._connection_pool[thread_id]
                    # Try to rollback any pending transaction
                    try:
                        conn.rollback()
                    except:
                        pass
                    # Close the connection
                    try:
                        conn.close()
                    except:
                        pass
                except:
                    pass
                del self._connection_pool[thread_id]
                logger.debug(f"Cleared connection for thread {thread_id}")

    def _timed_operation(self, operation_name: str):
        """Decorator to time database operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed = time.time() - start_time
                    self._timing_stats['queries'] += 1
                    self._timing_stats['total_time'] += elapsed
                    if elapsed > 0.1:  # Log slow operations
                        logger.warning(f"Slow DB operation '{operation_name}': {elapsed:.3f}s")
            return wrapper
        return decorator
    
    def init_database(self):
        """Initialize the database with required tables (lazy initialization)."""
        if self._initialized:
            return
            
        with self._init_lock:
            if self._initialized:  # Double-check pattern
                return
                
            start_time = time.time()
            logger.info("Initializing product database...")
            
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Ensure WAL mode is enabled (should already be set in _create_connection, but double-check)
                try:
                    cursor.execute("PRAGMA journal_mode = WAL")
                    journal_mode = cursor.fetchone()[0]
                    if journal_mode.upper() != 'WAL':
                        logger.warning(f"WAL mode not enabled, current mode: {journal_mode}")
                except:
                    pass  # Non-critical
                
                # Create strains table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS strains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strain_name TEXT UNIQUE NOT NULL,
                        normalized_name TEXT NOT NULL,
                        canonical_lineage TEXT,
                        first_seen_date TEXT NOT NULL,
                        last_seen_date TEXT NOT NULL,
                        total_occurrences INTEGER DEFAULT 1,
                        lineage_confidence REAL DEFAULT 0.0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Create products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL,
                        strain_id INTEGER,
                        product_type TEXT NOT NULL,
                        vendor TEXT,
                        brand TEXT,
                        description TEXT,
                        json TEXT,  -- Original Description value before processing
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
                ''')
                
                # Create lineage_history table for tracking lineage changes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS lineage_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strain_id INTEGER,
                        old_lineage TEXT,
                        new_lineage TEXT,
                        change_date TEXT NOT NULL,
                        change_reason TEXT,
                        FOREIGN KEY (strain_id) REFERENCES strains (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_normalized ON strains(normalized_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products(vendor, brand)')
                
                conn.commit()
                self._initialized = True
                
                elapsed = time.time() - start_time
                logger.info(f"Product database initialized successfully in {elapsed:.3f}s")
                
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                raise
    
    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate a cache key for the given operation and arguments."""
        return f"{operation}:{hash(str(args))}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache with thread safety."""
        with self._cache_lock:
            if cache_key in self._cache:
                self._timing_stats['cache_hits'] += 1
                return self._cache[cache_key]
            self._timing_stats['cache_misses'] += 1
            return None
    
    def _set_cache(self, cache_key: str, value: Any, ttl: int = 300):
        """Set value in cache with thread safety and TTL."""
        with self._cache_lock:
            self._cache[cache_key] = {
                'value': value,
                'expires': time.time() + ttl
            }
    
    def _clean_expired_cache(self):
        """Remove expired cache entries."""
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                key for key, data in self._cache.items()
                if data['expires'] < current_time
            ]
            for key in expired_keys:
                del self._cache[key]
    
    @_timed_operation("get_strain_info")
    def get_strain_info(self, strain_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific strain (with caching)."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            normalized_name = self._normalize_strain_name(strain_name)
            cache_key = self._get_cache_key("strain_info", normalized_name)
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, first_seen_date, last_seen_date
                FROM strains 
                WHERE normalized_name = ?
            ''', (normalized_name,))
            
            result = cursor.fetchone()
            if result:
                strain_info = {
                    'id': result[0],
                    'strain_name': result[1],
                    'canonical_lineage': result[2],
                    'total_occurrences': result[3],
                    'lineage_confidence': result[4],
                    'first_seen_date': result[5],
                    'last_seen_date': result[6]
                }
                
                # Cache the result for 5 minutes
                self._set_cache(cache_key, strain_info, ttl=300)
                return strain_info
            return None
            
        except Exception as e:
            logger.error(f"Error getting strain info for '{strain_name}': {e}")
            return None
    
    def validate_and_suggest_lineage(self, strain_name: str, proposed_lineage: str = None) -> Dict[str, Any]:
        """Validate strain lineage against database and suggest corrections."""
        try:
            strain_info = self.get_strain_info(strain_name)
            
            if not strain_info:
                return {
                    'valid': True,
                    'suggestion': proposed_lineage,
                    'confidence': 0.0,
                    'reason': 'New strain'
                }
            
            canonical_lineage = strain_info['canonical_lineage']
            occurrences = strain_info['total_occurrences']
            
            if not canonical_lineage:
                return {
                    'valid': True,
                    'suggestion': proposed_lineage,
                    'confidence': 0.0,
                    'reason': 'Strain exists but no lineage recorded'
                }
            
            # Calculate confidence based on occurrences
            confidence = min(occurrences / 10.0, 1.0)  # Max confidence at 10+ occurrences
            
            if proposed_lineage == canonical_lineage:
                return {
                    'valid': True,
                    'suggestion': canonical_lineage,
                    'confidence': confidence,
                    'reason': 'Matches database'
                }
            elif proposed_lineage:
                return {
                    'valid': False,
                    'suggestion': canonical_lineage,
                    'confidence': confidence,
                    'reason': f'Database suggests {canonical_lineage} (seen {occurrences} times)'
                }
            else:
                return {
                    'valid': True,
                    'suggestion': canonical_lineage,
                    'confidence': confidence,
                    'reason': f'Database suggests {canonical_lineage} (seen {occurrences} times)'
                }
                
        except Exception as e:
            logger.error(f"Error validating lineage for '{strain_name}': {e}")
            return {
                'valid': True,
                'suggestion': proposed_lineage,
                'confidence': 0.0,
                'reason': 'Error occurred during validation'
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the database."""
        self._clean_expired_cache()
        return {
            'total_queries': self._timing_stats['queries'],
            'total_time': self._timing_stats['total_time'],
            'average_time': self._timing_stats['total_time'] / max(self._timing_stats['queries'], 1),
            'cache_hits': self._timing_stats['cache_hits'],
            'cache_misses': self._timing_stats['cache_misses'],
            'cache_hit_rate': self._timing_stats['cache_hits'] / max(self._timing_stats['cache_hits'] + self._timing_stats['cache_misses'], 1),
            'cache_size': len(self._cache),
            'initialized': self._initialized
        }
    
    def clear_cache(self):
        """Clear the cache."""
        with self._cache_lock:
            self._cache.clear()
        self._timing_stats['cache_hits'] = 0
        self._timing_stats['cache_misses'] = 0
    
    def close_connections(self):
        """Close all database connections."""
        with self._connection_lock:
            for thread_id, conn in list(self._connection_pool.items()):
                try:
                    conn.rollback()  # Rollback any pending transactions
                except:
                    pass
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()
            logger.debug("Closed all database connections")
    
    def _normalize_strain_name(self, strain_name: str) -> str:
        """Normalize strain name for consistent matching."""
        if not isinstance(strain_name, str):
            return ""
        
        # Use the existing normalization function
        from .excel_processor import normalize_strain_name
        return normalize_strain_name(strain_name) 