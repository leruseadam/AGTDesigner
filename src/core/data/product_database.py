from .field_mapping import get_canonical_field
import sqlite3
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import pandas as pd
from pathlib import Path
from functools import lru_cache
import threading
import os

def get_database_path(store_name=None):
    """Get the path to the single product database."""
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    uploads_dir = os.path.join(current_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    return os.path.join(uploads_dir, 'product_database.db')

logger = logging.getLogger(__name__)

# Performance optimization: disable debug logging in production
DEBUG_ENABLED = False

# PERFORMANCE: TTL Cache for lineage queries (5 minute cache)
_lineage_cache = {}
_lineage_cache_timestamps = {}
_lineage_cache_lock = threading.Lock()
LINEAGE_CACHE_TTL = 300  # 5 minutes in seconds

# PERFORMANCE: TTL Cache for fuzzy match results (10 minute cache)
_fuzzy_match_cache = {}
_fuzzy_match_cache_timestamps = {}
_fuzzy_match_cache_lock = threading.Lock()
FUZZY_MATCH_CACHE_TTL = 600  # 10 minutes in seconds

def _get_cached_lineage(product_name: str) -> Optional[str]:
    """Get cached lineage if available and not expired."""
    if not product_name:
        return None

    with _lineage_cache_lock:
        cache_key = product_name.strip().lower()
        if cache_key in _lineage_cache:
            timestamp = _lineage_cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < LINEAGE_CACHE_TTL:
                return _lineage_cache[cache_key]
            else:
                # Expired, remove from cache
                del _lineage_cache[cache_key]
                del _lineage_cache_timestamps[cache_key]
    return None

def _set_cached_lineage(product_name: str, lineage: Optional[str]):
    """Cache lineage result."""
    if not product_name:
        return

    with _lineage_cache_lock:
        cache_key = product_name.strip().lower()
        _lineage_cache[cache_key] = lineage
        _lineage_cache_timestamps[cache_key] = time.time()

        # Prevent unbounded cache growth - limit to 10000 entries
        if len(_lineage_cache) > 10000:
            # Remove oldest 1000 entries
            sorted_keys = sorted(_lineage_cache_timestamps.items(), key=lambda x: x[1])
            for key, _ in sorted_keys[:1000]:
                del _lineage_cache[key]
                del _lineage_cache_timestamps[key]

def _get_cached_fuzzy_match(product_name: str) -> Optional[Dict[str, Any]]:
    """Get cached fuzzy match result if available and not expired."""
    if not product_name:
        return None

    with _fuzzy_match_cache_lock:
        cache_key = product_name.strip().lower()
        if cache_key in _fuzzy_match_cache:
            timestamp = _fuzzy_match_cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < FUZZY_MATCH_CACHE_TTL:
                return _fuzzy_match_cache[cache_key]
            else:
                # Expired, remove from cache
                del _fuzzy_match_cache[cache_key]
                del _fuzzy_match_cache_timestamps[cache_key]
    return None

def _set_cached_fuzzy_match(product_name: str, result: Optional[Dict[str, Any]]):
    """Cache fuzzy match result."""
    if not product_name:
        return

    with _fuzzy_match_cache_lock:
        cache_key = product_name.strip().lower()
        _fuzzy_match_cache[cache_key] = result
        _fuzzy_match_cache_timestamps[cache_key] = time.time()

        # Prevent unbounded cache growth - limit to 5000 entries
        if len(_fuzzy_match_cache) > 5000:
            # Remove oldest 500 entries
            sorted_keys = sorted(_fuzzy_match_cache_timestamps.items(), key=lambda x: x[1])
            for key, _ in sorted_keys[:500]:
                del _fuzzy_match_cache[key]
                del _fuzzy_match_cache_timestamps[key]

def timed_operation(operation_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            try:
                return func(self, *args, **kwargs)
            finally:
                elapsed = time.time() - start_time
                # You can log or store timing here if you want
                if elapsed > 0.1:
                    logger.warning(f"⏱️  {operation_name}: {elapsed:.3f}s")
        return wrapper
    return decorator

def retry_on_lock(max_retries=3, delay=0.5):
    """Decorator to retry database operations on locking errors."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            current_delay = delay  # Use a local variable to avoid scope issues
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(f"Database locked for {func.__name__}, retrying in {current_delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        raise e
            return None
        return wrapper
    return decorator

class ProductDatabase:
    """Database for storing and managing product and strain information."""
    
    def __init__(self, db_path: str = None, store_name: str = None):
        self.db_path = db_path if db_path is not None else get_database_path()
        self._store_name = 'AGT_Bothell'
        
        # Enhanced connection pooling
        self._connection_pool = {}
        self._pool_lock = threading.Lock()
        self._max_pool_size = 10  # Maximum connections per thread
        self._pool_timeout = 30.0  # Connection timeout in seconds
        
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._initialized = False
        self._init_lock = threading.Lock()
        # Serialize writers to avoid 'database is locked' under concurrent writes
        self._write_lock = threading.RLock()
        self._products_columns = None
        
        # Track rejected products to reduce log noise
        self._rejected_blank_names = 0
        self._rejected_invalid_names = 0
        self._rejected_short_names = 0
        self._rejected_missing_vendor = 0
        self._rejected_missing_type = 0
        
        # Performance timing
        self._timing_stats = {
            'queries': 0,
            'total_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'connection_reuses': 0,
            'connection_creates': 0
        }
        
        # Corruption recovery flag to prevent infinite loops
        self._corruption_recovery_attempted = False
        self._corruption_recovery_lock = threading.Lock()
    
    def _is_corruption_error(self, error: Exception) -> bool:
        """Check if an error indicates database corruption."""
        error_str = str(error).lower()
        corruption_indicators = [
            'database disk image is malformed',
            'database is corrupted',
            'file is encrypted or is not a database',
            'unable to open database file',
            'sqlite3.databaseerror'
        ]
        return any(indicator in error_str for indicator in corruption_indicators)
    
    def _attempt_database_recovery(self) -> bool:
        """Attempt to recover a corrupted database.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        with self._corruption_recovery_lock:
            if self._corruption_recovery_attempted:
                # Already attempted recovery, don't try again
                return False
            
            self._corruption_recovery_attempted = True
        
        db_path = Path(self.db_path)
        
        if not db_path.exists():
            logger.warning(f"Database file does not exist: {self.db_path}")
            return False
        
        logger.error(f"⚠️  Database corruption detected: {self.db_path}")
        logger.info("Attempting automatic database recovery...")
        
        try:
            # Create backup of corrupted database
            from datetime import datetime
            backup_path = db_path.parent / f"{db_path.stem}_corrupted_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                import shutil
                shutil.copy2(db_path, backup_path)
                logger.info(f"✓ Backup created: {backup_path.name}")
            except Exception as backup_error:
                logger.warning(f"Could not create backup: {backup_error}")
            
            # Method 1: Try to dump and restore
            logger.info("Method 1: Attempting dump and restore...")
            try:
                dump_file = db_path.parent / f"{db_path.stem}_dump.sql"
                recovered_db = db_path.parent / f"{db_path.stem}_recovered.db"
                
                # Try to dump the database (may fail if severely corrupted)
                try:
                    old_conn = sqlite3.connect(str(db_path))
                    with open(dump_file, 'w') as f:
                        for line in old_conn.iterdump():
                            f.write(f"{line}\n")
                    old_conn.close()
                except Exception as dump_error:
                    logger.warning(f"Cannot dump corrupted database: {dump_error}")
                    raise  # Re-raise to skip to Method 2
                
                # Create new database from dump
                if recovered_db.exists():
                    recovered_db.unlink()
                
                new_conn = sqlite3.connect(str(recovered_db))
                with open(dump_file, 'r') as f:
                    new_conn.executescript(f.read())
                new_conn.close()
                
                # Verify recovered database
                verify_conn = sqlite3.connect(str(recovered_db))
                cursor = verify_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                verify_conn.close()
                
                if table_count > 0:
                    # Replace corrupted database with recovered one
                    db_path.unlink()
                    recovered_db.rename(db_path)
                    dump_file.unlink()
                    
                    logger.info(f"✅ Database successfully recovered! ({table_count} tables)")
                    self._corruption_recovery_attempted = False  # Reset for future use
                    return True
                else:
                    logger.warning("Recovered database has no tables, trying method 2...")
                    recovered_db.unlink()
                    dump_file.unlink()
            except Exception as e:
                logger.warning(f"Method 1 failed: {e}")
            
            # Method 2: Try integrity check and partial recovery
            logger.info("Method 2: Attempting integrity check...")
            try:
                # Try to connect - may fail if severely corrupted
                try:
                    old_conn = sqlite3.connect(str(db_path))
                except Exception as conn_error:
                    logger.warning(f"Cannot connect to corrupted database for integrity check: {conn_error}")
                    raise  # Skip to Method 3
                
                cursor = old_conn.cursor()
                
                # Run integrity check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    logger.info("Integrity check passed, database may be recoverable")
                    old_conn.close()
                    # Reset flag since integrity check passed
                    self._corruption_recovery_attempted = False
                    return True
                else:
                    logger.warning(f"Integrity check failed: {result}")
                    old_conn.close()
            except Exception as e:
                logger.warning(f"Integrity check failed: {e}")
            
            # Method 3: Create fresh database (last resort)
            logger.warning("All recovery methods failed. Creating fresh database...")
            try:
                # Move corrupted database to backup location if not already done
                if not backup_path.exists():
                    db_path.rename(backup_path)
                else:
                    db_path.unlink()
                
                # Create new empty database file
                new_conn = sqlite3.connect(str(db_path))
                new_conn.close()
                
                logger.warning(f"⚠️  Fresh database created. Original backed up to: {backup_path.name}")
                logger.warning("⚠️  You will need to re-upload your Excel file to populate the database.")
                
                # Reset initialization flag so database can be reinitialized
                self._initialized = False
                self._corruption_recovery_attempted = False
                return True
                
            except Exception as e:
                logger.error(f"Failed to create fresh database: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            return False
    
    def _get_connection(self):
        """Get a database connection from pool, with enhanced connection management."""
        thread_id = threading.get_ident()

        with self._pool_lock:
            # Check if we have a connection for this thread
            if thread_id in self._connection_pool:
                conn = self._connection_pool[thread_id]
                # Verify connection is still valid with a safer check
                try:
                    # Use cursor().execute() instead of conn.execute() to avoid autocommit issues
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    self._timing_stats['connection_reuses'] += 1
                    return conn
                except (sqlite3.Error, sqlite3.DatabaseError, sqlite3.OperationalError) as e:
                    # Check if this is a corruption error
                    if self._is_corruption_error(e):
                        logging.error(f"Database corruption detected during connection validation: {e}")
                        try:
                            conn.close()
                        except:
                            pass
                        del self._connection_pool[thread_id]
                        # Attempt recovery
                        if self._attempt_database_recovery():
                            # Recovery successful, will create new connection below
                            pass
                        else:
                            raise
                    else:
                        # Connection is dead or database is locked, remove it and create new one
                        logging.warning(f"Connection validation failed for thread {thread_id}: {e}, creating new connection")
                        try:
                            conn.close()
                        except:
                            pass
                        del self._connection_pool[thread_id]

            # Create new connection with optimized settings
            max_retries = 3
            retry_delay = 0.1  # 100ms

            for attempt in range(max_retries):
                try:
                    conn = sqlite3.connect(
                        self.db_path,
                        timeout=self._pool_timeout,
                        check_same_thread=False,  # Allow connection sharing
                        isolation_level='DEFERRED'  # Better concurrency for reads
                    )

                    # Apply performance optimizations with error handling
                    # WAL mode can fail on some filesystems, so make it optional
                    try:
                        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                    except sqlite3.OperationalError as e:
                        logging.warning(f"WAL mode not supported, using default journal mode: {e}")

                    conn.execute("PRAGMA busy_timeout=60000")  # 60 second busy timeout
                    conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
                    conn.execute("PRAGMA cache_size=-20000")  # 20MB cache
                    conn.execute("PRAGMA temp_store=MEMORY")  # Temp tables in memory

                    try:
                        conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
                    except sqlite3.OperationalError as e:
                        logging.warning(f"Memory-mapped I/O not supported: {e}")

                    try:
                        conn.execute("PRAGMA page_size=4096")  # Optimal page size
                    except sqlite3.OperationalError as e:
                        logging.warning(f"Could not set page size: {e}")

                    # Verify connection works before returning
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()

                    # Store in pool
                    self._connection_pool[thread_id] = conn
                    self._timing_stats['connection_creates'] += 1

                    return conn

                except (sqlite3.Error, sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    # Check if this is a corruption error
                    if self._is_corruption_error(e):
                        logging.error(f"Database corruption detected: {e}")
                        # Attempt recovery once
                        if self._attempt_database_recovery():
                            # Recovery successful, try connecting again
                            logging.info("Database recovery successful, retrying connection...")
                            # Reset retry counter to give recovery a chance
                            attempt = -1  # Will be incremented to 0 in next iteration
                            continue
                        else:
                            # Recovery failed, raise the error
                            logging.error("Database recovery failed")
                            raise
                    
                    if attempt < max_retries - 1:
                        logging.warning(f"Connection attempt {attempt + 1} failed: {e}, retrying...")
                        import time
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    else:
                        logging.error(f"Failed to create database connection after {max_retries} attempts: {e}")
                        raise
    
    def close_connection(self):
        """Close the connection for the current thread."""
        thread_id = threading.get_ident()
        with self._pool_lock:
            if thread_id in self._connection_pool:
                try:
                    self._connection_pool[thread_id].close()
                except:
                    pass
                del self._connection_pool[thread_id]
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        with self._pool_lock:
            for conn in self._connection_pool.values():
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self._pool_lock:
            return {
                'active_connections': len(self._connection_pool),
                'max_pool_size': self._max_pool_size,
                'connection_reuses': self._timing_stats.get('connection_reuses', 0),
                'connection_creates': self._timing_stats.get('connection_creates', 0),
                'reuse_ratio': self._timing_stats.get('connection_reuses', 0) / max(1, self._timing_stats.get('connection_creates', 0))
            }
    
    def init_database(self):
        """Initialize the database with required tables (lazy initialization)."""
        if self._initialized:
            return
            
        with self._init_lock:
            if self._initialized:  # Double-check pattern
                return
                
            start_time = time.time()
            logger.info(f"Initializing product database at {self.db_path}...")
            
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Check if products table exists and has data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                products_exists = cursor.fetchone() is not None
                
                if products_exists:
                    # Check if table has data
                    cursor.execute("SELECT COUNT(*) FROM products")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        logger.info(f"Database already initialized with {count} products")
                        try:
                            # Even with existing data, ensure new columns are present
                            self._add_missing_columns_safe(cursor, conn)
                        except Exception as column_error:
                            logger.warning(f"Could not add missing columns on existing DB: {column_error}")
                        try:
                            self._ensure_essential_columns_exist(cursor, conn)
                        except Exception as essential_error:
                            logger.warning(f"Could not ensure essential columns on existing DB: {essential_error}")
                        self._initialized = True
                        return
                
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
                        sovereign_lineage TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Create products table with essential columns for Excel data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        "Product Name*" TEXT NOT NULL,
                        normalized_name TEXT NOT NULL,
                        strain_id INTEGER,
                        "Product Type*" TEXT NOT NULL,
                        "Vendor/Supplier*" TEXT,
                        "Product Brand" TEXT,
                        "Description" TEXT,
                        "Weight*" TEXT,
                        "Units" TEXT,
                        "Price" TEXT,
                        "Lineage" TEXT,
                        first_seen_date TEXT NOT NULL,
                        last_seen_date TEXT NOT NULL,
                        total_occurrences INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        "Product Strain" TEXT,
                        "Quantity*" TEXT,
                        "DOH" TEXT,
                        "Concentrate Type" TEXT,
                        "Ratio" TEXT,
                        "JointRatio" TEXT,
                        "THC test result" TEXT,
                        "CBD test result" TEXT,
                        "Test result unit (% or mg)" TEXT,
                        "State" TEXT,
                        "Is Sample? (yes/no)" TEXT,
                        "Is MJ product?(yes/no)" TEXT,
                        "Discountable? (yes/no)" TEXT,
                        "Room*" TEXT,
                        "Batch Number" TEXT,
                        "Lot Number" TEXT,
                        "Barcode*" TEXT,
                        "Medical Only (Yes/No)" TEXT,
                        "Med Price" TEXT,
                        "Expiration Date(YYYY-MM-DD)" TEXT,
                        "Is Archived? (yes/no)" TEXT,
                        "THC Per Serving" TEXT,
                        "Allergens" TEXT,
                        "Solvent" TEXT,
                        "Accepted Date" TEXT,
                        "Internal Product Identifier" TEXT,
                        "Product Tags (comma separated)" TEXT,
                        "Image URL" TEXT,
                        "Ingredients" TEXT,
                        -- Additional cannabinoid columns for comprehensive testing
                        "Total THC" TEXT,
                        "THCA" TEXT,
                        "CBDA" TEXT,
                        "CBN" TEXT,
                        "THC" TEXT,
                        "CBD" TEXT,
                        "Total CBD" TEXT,
                        "CBGA" TEXT,
                        "CBG" TEXT,
                        "Total CBG" TEXT,
                        "CBC" TEXT,
                        "CBDV" TEXT,
                        "THCV" TEXT,
                        "CBGV" TEXT,
                        "CBNV" TEXT,
                        "CBGVA" TEXT,
                        "sovereign_lineage" TEXT,  -- Manual lineage override for products without strains
                        FOREIGN KEY (strain_id) REFERENCES strains (id),
                        UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand", "Weight*")
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
                
                # Create strain-brand lineage overrides
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS strain_brand_lineage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strain_name TEXT NOT NULL,
                        brand TEXT NOT NULL,
                        lineage TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(strain_name, brand)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_normalized ON strains(normalized_name)')
                
                # Only create normalized_name index if the column exists
                cursor.execute("PRAGMA table_info(products)")
                product_columns = [col[1] for col in cursor.fetchall()]
                if 'normalized_name' in product_columns:
                    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
                
                # Only create strain_id index if the column exists
                if 'strain_id' in product_columns:
                    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain_id)')

                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
                # PERFORMANCE: Index on Product Strain for faster lineage lookups
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_product_strain ON products("Product Strain")')
                
                conn.commit()
                
                # Check if we need to add missing columns (migration)
                # Only migrate if tables are empty or missing critical columns
                self._migrate_database_schema_safe(cursor, conn)
                
                # CRITICAL FIX: Force check for essential columns and add if missing
                self._ensure_essential_columns_exist(cursor, conn)
                
                self._initialized = True
                
                elapsed = time.time() - start_time
                logger.info(f"Product database initialized successfully in {elapsed:.3f}s")
                
            except Exception as e:
                # Check if this is a corruption error
                if self._is_corruption_error(e):
                    logger.error(f"Database corruption detected during initialization: {e}")
                    if self._attempt_database_recovery():
                        # Recovery successful, try initializing again
                        logger.info("Database recovery successful, retrying initialization...")
                        # Reset initialization flag
                        self._initialized = False
                        # Recursively call init_database (with protection against infinite loops)
                        return self.init_database()
                    else:
                        logger.error("Database recovery failed during initialization")
                        raise
                else:
                    logger.error(f"Error initializing database: {e}")
                    raise
    
    def _migrate_database_schema_safe(self, cursor, conn):
        """Safely migrate database schema only if necessary."""
        try:
            # Check if tables exist and have data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strains'")
            strains_table_exists = cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            products_table_exists = cursor.fetchone() is not None
            
            if strains_table_exists and products_table_exists:
                # Check if tables have data
                cursor.execute("SELECT COUNT(*) FROM strains")
                strain_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM products")
                product_count = cursor.fetchone()[0]
                
                if strain_count > 0 or product_count > 0:
                    logger.info(f"Database has existing data ({strain_count} strains, {product_count} products). Skipping destructive migration.")
                    # Add missing columns to existing tables
                    self._add_missing_columns_safe(cursor, conn)
                    return
            
            logger.info("Database is empty or missing tables. Performing safe schema migration...")
            # Only proceed with migration if tables are empty or don't exist
            self._migrate_database_schema(cursor, conn)
            
        except Exception as e:
            logger.error(f"Error during safe schema migration: {e}")
            # Don't raise - continue with existing schema
    
    def _ensure_essential_columns_exist(self, cursor, conn):
        """Ensure essential columns exist that are needed for Excel processor compatibility."""
        try:
            # Get current columns
            cursor.execute("PRAGMA table_info(products)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # Essential columns that must exist for Excel processor compatibility
            essential_columns = [
                'ProductName',
                'Units', 
                'Price',
                '"Price*"',
                '"Price* (Tier Name for Bulk)"',
                '"Product Name*"',
                '"Vendor/Supplier*"',
                '"Weight*"',
                '"Weight Unit*"',
                '"Quantity*"',
                '"Quantity Received*"',
                '"DOH Compliant*"',
                '"DOH Compliant (Yes/No)"',
                '"Joint Ratio"',
                'qty',
                '"Weight Unit* (grams/gm or ounces/oz)"',
                'Vendor',
                'Source'  # Add Source column for compatibility
            ]
            
            advanced_columns = [
                '"THC Per Serving"',
                '"Allergens"',
                '"Solvent"',
                '"Accepted Date"',
                '"Internal Product Identifier"',
                '"Product Tags (comma separated)"',
                '"Image URL"',
                '"Ingredients"',
                '"CombinedWeight"',
                '"Ratio_or_THC_CBD"',
                '"Description_Complexity"',
                '"Total THC"',
                '"THCA"',
                '"CBDA"',
                '"CBN"',
                '"THC"',
                '"CBD"',
                '"Total CBD"',
                '"CBGA"',
                '"CBG"',
                '"Total CBG"',
                '"CBC"',
                '"CBDV"',
                '"THCV"',
                '"CBGV"',
                '"CBNV"',
                '"CBGVA"'
            ]
            
            essential_columns.extend(advanced_columns)
            
            added_columns = []
            for col_name in essential_columns:
                # Strip quotes for comparison with existing columns
                col_name_clean = col_name.strip('"')
                if col_name_clean not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} TEXT")
                        added_columns.append(col_name)
                        logger.info(f"Added essential column: {col_name}")
                    except sqlite3.OperationalError as e:
                        if "duplicate column name" not in str(e).lower():
                            logger.warning(f"Could not add essential column {col_name}: {e}")
                    except Exception as e:
                        logger.warning(f"Could not add essential column {col_name}: {e}")
            
            if added_columns:
                conn.commit()
                logger.info(f"Added {len(added_columns)} essential columns to products table")
            else:
                logger.debug("All essential columns already exist")
            
            # Ensure lineage_history table exists even on legacy databases
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
            conn.commit()
                
        except Exception as e:
            logger.error(f"Error ensuring essential columns exist: {e}")

    def _migrate_database_schema(self, cursor, conn):
        """Force recreate database with correct schema - USE WITH CAUTION."""
        try:
            logger.info("Forcing database recreation with correct schema...")
            
            # Drop existing tables
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS strains")
            cursor.execute("DROP TABLE IF EXISTS lineage_history")
            cursor.execute("DROP TABLE IF EXISTS strain_brand_lineage")
            
            # Recreate tables with correct schema
            cursor.execute('''
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
            ''')
            
            cursor.execute('''
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    "Product Name*" TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    strain_id INTEGER,
                    "Product Type*" TEXT NOT NULL,
                    "Vendor/Supplier*" TEXT,
                    "Product Brand" TEXT,
                    "Description" TEXT,
                    "Weight*" TEXT,
                    "Units" TEXT,
                    "Price" TEXT,
                    "Lineage" TEXT,
                    first_seen_date TEXT NOT NULL,
                    last_seen_date TEXT NOT NULL,
                    total_occurrences INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    "Product Strain" TEXT,
                    "Quantity*" TEXT,
                    "DOH" TEXT,
                    "Concentrate Type" TEXT,
                    "Ratio" TEXT,
                    "JointRatio" TEXT,
                    "THC test result" TEXT,
                    "CBD test result" TEXT,
                    "Test result unit (% or mg)" TEXT,
                    "State" TEXT,
                    "Is Sample? (yes/no)" TEXT,
                    "Is MJ product?(yes/no)" TEXT,
                    "Discountable? (yes/no)" TEXT,
                    "Room*" TEXT,
                    "Batch Number" TEXT,
                    "Lot Number" TEXT,
                    "Barcode*" TEXT,
                    "Medical Only (Yes/No)" TEXT,
                    "Med Price" TEXT,
                    "Expiration Date(YYYY-MM-DD)" TEXT,
                    "Is Archived? (yes/no)" TEXT,
                    "THC Per Serving" TEXT,
                    "Allergens" TEXT,
                    "Solvent" TEXT,
                    "Accepted Date" TEXT,
                    "Internal Product Identifier" TEXT,
                    "Product Tags (comma separated)" TEXT,
                    "Image URL" TEXT,
                    "Ingredients" TEXT,
                    -- Additional Excel columns for comprehensive JSON matching
                    "CombinedWeight" TEXT,
                    "Ratio_or_THC_CBD" TEXT,
                    "Description_Complexity" TEXT,
                    "Total THC" TEXT,
                    "THCA" TEXT,
                    "CBDA" TEXT,
                    "CBN" TEXT,
                    -- Additional cannabinoid columns for comprehensive testing
                    "THC" TEXT,
                    "CBD" TEXT,
                    "Total CBD" TEXT,
                    "CBGA" TEXT,
                    "CBG" TEXT,
                    "Total CBG" TEXT,
                    "CBC" TEXT,
                    "CBDV" TEXT,
                    "THCV" TEXT,
                    "CBGV" TEXT,
                    "CBNV" TEXT,
                    "CBGVA" TEXT,
                    -- Calculated THC/CBD values
                    "AI" TEXT,
                    "AJ" TEXT,
                    "AK" TEXT,
                    -- Terpene columns for comprehensive product data
                    "A-Bisabolol (mg/g)" TEXT,
                    "A-Humulene (mg/g)" TEXT,
                    "A-Maaliene (mg/g)" TEXT,
                    "A-Myrcene (mg/g)" TEXT,
                    "A-Pinene (mg/g)" TEXT,
                    "B-Caryophyllene (mg/g)" TEXT,
                    "B-Myrcene (mg/g)" TEXT,
                    "B-Pinene (mg/g)" TEXT,
                    bisabolol_mg_g TEXT,
                    borneol_mg_g TEXT,
                    camphene_mg_g TEXT,
                    camphor_mg_g TEXT,
                    carene_mg_g TEXT,
                    carvacrol_mg_g TEXT,
                    carvone_mg_g TEXT,
                    caryophyllene_mg_g TEXT,
                    cedrol_mg_g TEXT,
                    citral_mg_g TEXT,
                    citronellol_mg_g TEXT,
                    cymene_mg_g TEXT,
                    delta_3_carene_mg_g TEXT,
                    eucalyptol_mg_g TEXT,
                    fenchol_mg_g TEXT,
                    fenchone_mg_g TEXT,
                    geraniol_mg_g TEXT,
                    geranyl_acetate_mg_g TEXT,
                    guaiol_mg_g TEXT,
                    humulene_mg_g TEXT,
                    isoborneol_mg_g TEXT,
                    isobornyl_acetate_mg_g TEXT,
                    isopulegol_mg_g TEXT,
                    limonene_mg_g TEXT,
                    linalool_mg_g TEXT,
                    linalyl_acetate_mg_g TEXT,
                    m_cymene_mg_g TEXT,
                    menthal_mg_g TEXT,
                    menthone_mg_g TEXT,
                    myrcene_mg_g TEXT,
                    nerolidol_mg_g TEXT,
                    o_cymene_mg_g TEXT,
                    ocimene_mg_g TEXT,
                    p_cymene_mg_g TEXT,
                    phellandrene_mg_g TEXT,
                    phytol_mg_g TEXT,
                    pinene_mg_g TEXT,
                    piperitone_mg_g TEXT,
                    pulegone_mg_g TEXT,
                    sabinene_mg_g TEXT,
                    safranal_mg_g TEXT,
                    selinadiene_mg_g TEXT,
                    terpineol_mg_g TEXT,
                    terpinolene_mg_g TEXT,
                    thujene_mg_g TEXT,
                    thymol_mg_g TEXT,
                    trans_nerolidol_mg_g TEXT,
                    trans_alpha_bergamotene_mg_g TEXT,
                    valencene_mg_g TEXT,
                    alpha_bisabolene_mg_g TEXT,
                    alpha_bulnesene_mg_g TEXT,
                    alpha_farnesene_mg_g TEXT,
                    alpha_maaliene_mg_g TEXT,
                    alpha_ocimene_mg_g TEXT,
                    alpha_phellandrene_mg_g TEXT,
                    alpha_pinene_mg_g TEXT,
                    alpha_terpinene_mg_g TEXT,
                    alpha_thujone_mg_g TEXT,
                    beta_farnesene_mg_g TEXT,
                    beta_maaliene_mg_g TEXT,
                    beta_ocimene_mg_g TEXT,
                    beta_pinene_mg_g TEXT,
                    gamma_terpinene_mg_g TEXT,
                    -- Additional source Excel columns for comprehensive matching
                    product_name_alt TEXT,
                    vendor_supplier TEXT,
                    vendor_supplier_alt TEXT,
                    weight_with_units TEXT,
                    weight_units TEXT,
                    quantity_received TEXT,
                    product_type_alt TEXT,
                    product_brand_alt TEXT,
                    product_brand_center TEXT,
                    ratio_or_thc_cbd_alt TEXT,
                    thc_cbd TEXT,
                    thc_cbd_alt TEXT,
                    ai_column TEXT,
                    aj_column TEXT,
                    ak_column TEXT,
                    al_column TEXT,
                    am_column TEXT,
                    an_column TEXT,
                    ao_column TEXT,
                    ap_column TEXT,
                    aq_column TEXT,
                    ar_column TEXT,
                    as_column TEXT,
                    at_column TEXT,
                    au_column TEXT,
                    av_column TEXT,
                    aw_column TEXT,
                    ax_column TEXT,
                    ay_column TEXT,
                    az_column TEXT,
                    ba_column TEXT,
                    bb_column TEXT,
                    bc_column TEXT,
                    bd_column TEXT,
                    be_column TEXT,
                    bf_column TEXT,
                    bg_column TEXT,
                    bh_column TEXT,
                    bi_column TEXT,
                    bj_column TEXT,
                    bk_column TEXT,
                    bl_column TEXT,
                    bm_column TEXT,
                    bn_column TEXT,
                    bo_column TEXT,
                    bp_column TEXT,
                    bq_column TEXT,
                    br_column TEXT,
                    bs_column TEXT,
                    bt_column TEXT,
                    bu_column TEXT,
                    bv_column TEXT,
                    bw_column TEXT,
                    bx_column TEXT,
                    by_column TEXT,
                    bz_column TEXT,
                    ca_column TEXT,
                    cb_column TEXT,
                    cc_column TEXT,
                    cd_column TEXT,
                    ce_column TEXT,
                    cf_column TEXT,
                    cg_column TEXT,
                    ch_column TEXT,
                    ci_column TEXT,
                    cj_column TEXT,
                    ck_column TEXT,
                    cl_column TEXT,
                    cm_column TEXT,
                    cn_column TEXT,
                    co_column TEXT,
                    cp_column TEXT,
                    cq_column TEXT,
                    cr_column TEXT,
                    cs_column TEXT,
                    ct_column TEXT,
                    cu_column TEXT,
                    cv_column TEXT,
                    cw_column TEXT,
                    cx_column TEXT,
                    cy_column TEXT,
                    cz_column TEXT,
                    -- Excel processor compatibility columns
                    "ProductName" TEXT,  -- Alternative to "Product Name*"
                    "DOH Compliant (Yes/No)" TEXT,  -- Alternative to "DOH"
                    "Joint Ratio" TEXT,  -- Alternative to "JointRatio"
                    "Quantity Received*" TEXT,  -- Alternative to "Quantity*"
                    "qty" TEXT,  -- Alternative to "Quantity*"
                    "Source" TEXT,  -- Source of product data (Excel Import, JSON Match, etc.)
                    "sovereign_lineage" TEXT,  -- Manual lineage override for products without strains
                    FOREIGN KEY (strain_id) REFERENCES strains (id),
                    UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand", "Weight*")
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE lineage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strain_id INTEGER,
                    old_lineage TEXT,
                    new_lineage TEXT,
                    change_date TEXT NOT NULL,
                    change_reason TEXT,
                    FOREIGN KEY (strain_id) REFERENCES strains (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE strain_brand_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strain_name TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    lineage TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(strain_name, brand)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX idx_strains_normalized ON strains(normalized_name)')
            cursor.execute('CREATE INDEX idx_products_normalized ON products(normalized_name)')
            cursor.execute('CREATE INDEX idx_products_strain ON products(strain_id)')
            cursor.execute('CREATE INDEX idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
            # PERFORMANCE: Index on Product Strain for faster lineage lookups
            cursor.execute('CREATE INDEX idx_products_product_strain ON products("Product Strain")')

            conn.commit()
            logger.info("Database recreated with correct schema")
            
        except Exception as e:
            logger.error(f"Error recreating database: {e}")
            raise
    
    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate a cache key for the given operation and arguments."""
        return f"{operation}:{hash(str(args))}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache with thread safety."""
        with self._cache_lock:
            if cache_key in self._cache:
                cached_data = self._cache[cache_key]
                # Check if cache entry has expired
                if cached_data['expires'] < time.time():
                    del self._cache[cache_key]
                    self._timing_stats['cache_misses'] += 1
                    return None
                self._timing_stats['cache_hits'] += 1
                return cached_data['value']
            self._timing_stats['cache_misses'] += 1
            return None
    
    def _set_cache(self, cache_key: str, value: Any, ttl: int = 300):
        """Set value in cache with thread safety and TTL."""
        with self._cache_lock:
            self._cache[cache_key] = {
                'value': value,
                'expires': time.time() + ttl
            }

    def _products_has_column(self, column_name: str) -> bool:
        """Check if the products table includes the given column (cached)."""
        if self._products_columns is None:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute('PRAGMA table_info(products)')
                self._products_columns = {row[1] for row in cursor.fetchall()}
            except Exception as e:
                logger.warning(f"Unable to inspect products table columns: {e}")
                self._products_columns = set()
        return column_name in self._products_columns
    
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
    
    def get_mode_lineage(self, strain_id: int) -> str:
        """Return the most common (mode) lineage for a strain from the products table."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First get the strain name from the strains table
            cursor.execute('SELECT strain_name FROM strains WHERE id = ?', (strain_id,))
            strain_result = cursor.fetchone()
            if not strain_result:
                return None
            
            strain_name = strain_result[0]
            
            # Then find the most common lineage for this strain in products
            cursor.execute('''
                SELECT "Lineage", COUNT(*) as count
                FROM products
                WHERE "Product Strain" = ? AND "Lineage" IS NOT NULL AND "Lineage" != ''
                GROUP BY "Lineage"
                ORDER BY count DESC
                LIMIT 1
            ''', (strain_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"Error getting mode lineage for strain_id {strain_id}: {e}")
            return None

    def update_all_canonical_lineages_to_mode(self):
        """Update all strains' canonical_lineage to the mode lineage from the products table."""
        self.init_database()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, strain_name, canonical_lineage FROM strains')
        strains = cursor.fetchall()
        updated = 0
        # Generic/non-strain buckets must never be overwritten by product-mode lineage.
        protected_generic = {'mixed', 'mix', 'unknown', 'none', 'nan'}
        for strain_id, strain_name, canonical_lineage in strains:
            normalized_strain = self._normalize_strain_name(strain_name or '')
            if normalized_strain in protected_generic:
                target_lineage = 'MIXED'
                if (canonical_lineage or '').strip().upper() != target_lineage:
                    cursor.execute('''
                        UPDATE strains SET canonical_lineage = ?, updated_at = ? WHERE id = ?
                    ''', (target_lineage, datetime.now().isoformat(), strain_id))
                    logger.info(f"Protected generic strain '{strain_name}': set canonical_lineage to '{target_lineage}' (was '{canonical_lineage}')")
                    updated += 1
                continue

            mode_lineage = self.get_mode_lineage(strain_id)
            if mode_lineage and mode_lineage != canonical_lineage:
                cursor.execute('''
                    UPDATE strains SET canonical_lineage = ?, updated_at = ? WHERE id = ?
                ''', (mode_lineage, datetime.now().isoformat(), strain_id))
                logger.info(f"Updated canonical_lineage for '{strain_name}' to '{mode_lineage}' (was '{canonical_lineage}')")
                updated += 1
        conn.commit()
        logger.info(f"Canonical lineage update complete. {updated} strains updated.")

    @timed_operation("add_or_update_strain")
    @retry_on_lock(max_retries=3, delay=0.5)
    def add_or_update_strain(self, strain_name: str, lineage: str = None, sovereign: bool = False) -> int:
        """Add a new strain or update existing strain information."""
        try:
            self.init_database()  # Ensure DB is initialized
            normalized_name = self._normalize_strain_name(strain_name)
            # Guard generic buckets from receiving classic lineages.
            if normalized_name in {'mixed', 'mix', 'unknown', 'none', 'nan'}:
                lineage = 'MIXED'
            current_date = datetime.now().isoformat()
            # Serialize write operations
            with self._write_lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                # Check if we're already in a transaction
                try:
                    cursor.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as e:
                    if "cannot start a transaction within a transaction" in str(e):
                        # We're already in a transaction, continue without BEGIN
                        pass
                    else:
                        raise e
                
                # Check if strain exists
                cursor.execute('''
                    SELECT id, canonical_lineage, total_occurrences, lineage_confidence
                    FROM strains 
                    WHERE normalized_name = ?
                ''', (normalized_name,))
                existing = cursor.fetchone()
                if existing:
                    strain_id, existing_lineage, occurrences, confidence = existing
                    new_occurrences = occurrences + 1
                    if lineage and lineage != existing_lineage:
                        cursor.execute('''
                            INSERT INTO lineage_history (strain_id, old_lineage, new_lineage, change_date, change_reason)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (strain_id, existing_lineage, lineage, current_date, 'New data upload'))
                        cursor.execute('''
                            UPDATE strains 
                            SET canonical_lineage = ?, total_occurrences = ?, last_seen_date = ?, updated_at = ?
                            WHERE id = ?
                        ''', (lineage, new_occurrences, current_date, current_date, strain_id))
                        try:
                            from .database_notifier import notify_lineage_update
                            notify_lineage_update(strain_name, existing_lineage, lineage)
                        except Exception as notify_error:
                            logger.warning(f"Failed to notify lineage update: {notify_error}")
                    else:
                        cursor.execute('''
                            UPDATE strains 
                            SET total_occurrences = ?, last_seen_date = ?, updated_at = ?
                            WHERE id = ?
                        ''', (new_occurrences, current_date, current_date, strain_id))
                    conn.commit()
                    cache_key = self._get_cache_key("strain_info", normalized_name)
                    with self._cache_lock:
                        if cache_key in self._cache:
                            del self._cache[cache_key]
                    return strain_id
                else:
                    cursor.execute('''
                        INSERT INTO strains (strain_name, normalized_name, canonical_lineage, first_seen_date, last_seen_date, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (strain_name, normalized_name, lineage, current_date, current_date, current_date, current_date))
                    strain_id = cursor.lastrowid
                    conn.commit()
                    try:
                        from .database_notifier import notify_strain_add
                        notify_strain_add(strain_name, {
                            'lineage': lineage,
                            'strain_id': strain_id
                        })
                    except Exception as notify_error:
                        logger.warning(f"Failed to notify strain add: {notify_error}")
                    if DEBUG_ENABLED:
                        logger.debug(f"Added new strain '{strain_name}' with lineage '{lineage}'")
                    return strain_id
        except Exception as e:
            logger.error(f"Error adding/updating strain '{strain_name}': {e}")
            raise
    
    @timed_operation("add_or_update_product")
    @retry_on_lock(max_retries=3, delay=0.5)
    def add_or_update_product(self, product_data: Dict[str, Any]) -> int:
        """Add a new product or update existing product information."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            # Handle both 'ProductName' and 'Product Name*' column names
            product_name = product_data.get(get_canonical_field('Product Name*'), product_data.get(get_canonical_field('ProductName'), ''))
            
            # CRITICAL VALIDATION: Prevent blank entries from being added to database
            if not product_name or str(product_name).strip() == '':
                # Attempt to auto-fill Product Name from common fallback fields (Description, ProductName, alt names)
                fallback_keys = ['Description', 'ProductName', 'product_name_alt', 'product_name', 'Description_Complexity']
                filled = False
                for fk in fallback_keys:
                    try:
                        cand = product_data.get(fk)
                    except Exception:
                        cand = None
                    if cand and str(cand).strip() and str(cand).strip().lower() not in ['nan', 'none', 'null']:
                        product_name = str(cand).strip()
                        # Update both common keys so downstream code sees the name
                        try:
                            product_data['Product Name*'] = product_name
                        except Exception:
                            pass
                        try:
                            product_data['ProductName'] = product_name
                        except Exception:
                            pass
                        logger.info(f"Auto-filled missing Product Name from '{fk}': '{product_name[:80]}'")
                        filled = True
                        break

                if not filled:
                    self._rejected_blank_names += 1
                    # Log a compact sample of the offending product_data periodically to aid diagnosis
                    try:
                        sample_preview = {k: (str(product_data.get(k))[:120] if product_data.get(k) is not None else None)
                                          for k in list(product_data.keys())[:8]}
                    except Exception:
                        sample_preview = None

                    if self._rejected_blank_names <= 5 or (self._rejected_blank_names % 500) == 0:
                        logger.warning(
                            f"❌ REJECTED: Cannot add product with blank/empty product name (count: {self._rejected_blank_names}). "
                            f"Sample keys: {list(product_data.keys())[:8]} Sample preview: {sample_preview}"
                        )
                    else:
                        logger.debug(f"❌ REJECTED: Cannot add product with blank/empty product name (count: {self._rejected_blank_names})")

                    return None
            
            # Check for invalid values
            if str(product_name).lower() in ['nan', 'none', 'null', '']:
                self._rejected_invalid_names += 1
                logger.warning(f"❌ REJECTED: Cannot add product with invalid product name: '{product_name}' (count: {self._rejected_invalid_names})")
                return None
            
            # RELAXED VALIDATION: Allow single character names for vertical template compatibility
            # Check for minimum length (at least 1 character instead of 2)
            if len(str(product_name).strip()) < 1:
                self._rejected_short_names += 1
                logger.warning(f"❌ REJECTED: Product name too short (must be at least 1 character): '{product_name}' (count: {self._rejected_short_names})")
                return None
            
            # CRITICAL FIX: Apply defaults for essential fields BEFORE validation
            # This ensures products are added even if vendor/product_type are missing
            # Check ALL vendor column name variations
            vendor_raw = (product_data.get('Vendor/Supplier*', '') or 
                          product_data.get('Vendor/Supplier', '') or 
                          product_data.get('Vendor', '') or 
                          product_data.get('vendor', '') or 
                          product_data.get('Supplier', '') or 
                          product_data.get('supplier', '') or 
                          '')
            vendor = self._ensure_crucial_value(vendor_raw, 'Unknown Vendor', 'Vendor')
            product_data['Vendor/Supplier*'] = vendor  # Update product_data with default
            product_data['Vendor'] = vendor  # Also set Vendor for compatibility
            
            product_type_raw = product_data.get('Product Type*', '')
            product_type = self._ensure_crucial_value(product_type_raw, 'Unknown', 'Product Type')
            product_data['Product Type*'] = product_type  # Update product_data with default
            
            # Validation removed - defaults are always applied above, so vendor and product_type will never be empty
            # Products will always be added with at least 'Unknown Vendor' and 'Unknown' product type
            
            normalized_name = self._normalize_product_name(product_name)
            current_date = datetime.now().isoformat()
            
            # Get or create strain
            strain_name = product_data.get('Product Strain', '').strip() if product_data.get('Product Strain') else ''
            strain_id = None

            # CRITICAL FIX: If no Product Strain, extract strain from product name (classic types only)
            # This ensures products without "Product Strain" field still get linked to strains
            # so their lineage edits can be saved to the strains table
            if not strain_name:
                product_type = product_data.get('Product Type*', '').strip() if product_data.get('Product Type*') else ''
                strain_name = self._extract_strain_from_product_name(product_name, product_type)

            if strain_name:
                # Normalize lineage before storing
                normalized_lineage = self._normalize_lineage(product_data.get('Lineage'))
                strain_id = self.add_or_update_strain(strain_name, normalized_lineage)
            
            # Serialize write operations
            with self._write_lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                # Check if we're already in a transaction
                try:
                    cursor.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as e:
                    if "cannot start a transaction within a transaction" in str(e):
                        # We're already in a transaction, continue without BEGIN
                        pass
                    else:
                        raise e
                
                # Enhanced duplicate detection: Check multiple combinations
                # Normalize vendor and brand for better matching
                vendor_value = product_data.get(get_canonical_field('Vendor/Supplier*'), '')
                brand_value = product_data.get(get_canonical_field('Product Brand'), '')
                weight_value = product_data.get('Weight*', '')
                
                # Import CLASSIC_TYPES for unit preference logic
                import re
                from src.core.constants import CLASSIC_TYPES
                product_type_for_cbd = product_data.get('Product Type*', '').strip().lower()
                is_classic_type = product_type_for_cbd in CLASSIC_TYPES or any(ct in product_type_for_cbd for ct in CLASSIC_TYPES)
                
                # Helper function to check if units are "better" (proper units preferred over g for non-classic types)
                def has_better_units(new_units: str, existing_units: str, is_nonclassic: bool) -> bool:
                    """Return True if new_units is better than existing_units for non-classic types.
                    
                    For edibles/non-classic types, proper units are:
                    - mg (milligrams) - preferred over grams
                    - count/each/pieces - preferred over grams  
                    - oz - preferred over grams
                    - ml (milliliters) - preferred over grams
                    """
                    if not is_nonclassic:
                        return False  # No preference for classic types
                    new_units_lower = (new_units or '').strip().lower()
                    existing_units_lower = (existing_units or '').strip().lower()
                    
                    # Proper units for edibles/non-classic types (in order of preference)
                    proper_units = ['mg', 'milligram', 'count', 'each', 'piece', 'pieces', 'oz', 'ounce', 'ml', 'milliliter']
                    
                    # Check if new has proper units and existing has grams
                    new_has_proper = any(unit in new_units_lower for unit in proper_units)
                    existing_has_grams = 'g' in existing_units_lower or 'gram' in existing_units_lower
                    
                    if new_has_proper and existing_has_grams:
                        return True  # New has proper units, existing has grams -> prefer new
                    
                    # Also prefer oz over g (already handled above, but keep for clarity)
                    if ('oz' in new_units_lower or 'ounce' in new_units_lower) and ('g' in existing_units_lower or 'gram' in existing_units_lower):
                        return True
                    
                    # Prefer mg over g
                    if ('mg' in new_units_lower or 'milligram' in new_units_lower) and ('g' in existing_units_lower or 'gram' in existing_units_lower):
                        return True
                    
                    # Prefer count/each/pieces over g
                    if any(unit in new_units_lower for unit in ['count', 'each', 'piece', 'pieces']) and ('g' in existing_units_lower or 'gram' in existing_units_lower):
                        return True
                    
                    return False
                
                # First check exact match (name + vendor + brand + weight + product type) - matches UNIQUE constraint
                cursor.execute('''
                    SELECT id, total_occurrences, "Product Name*", Units, "Product Type*"
                    FROM products 
                    WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Brand" = ? AND "Weight*" = ? AND "Product Type*" = ?
                ''', (normalized_name, vendor_value, brand_value, weight_value, product_data.get('Product Type*', '')))
                
                existing = cursor.fetchone()
                
                if existing:
                    product_id, occurrences, existing_name, existing_units, existing_product_type = existing
                    
                    # Check if we should prefer existing or new based on units (for non-classic types)
                    new_units = product_data.get('Units', '') or product_data.get('Weight Unit* (grams/gm or ounces/oz)', '')
                    existing_is_nonclassic = existing_product_type and existing_product_type.strip().lower() not in CLASSIC_TYPES and not any(ct in existing_product_type.strip().lower() for ct in CLASSIC_TYPES)
                    
                    # Check if existing has better units - if so, keep existing
                    if existing_is_nonclassic and has_better_units(existing_units or '', new_units, True):
                        # Existing has better units (mg/count/oz vs g), keep existing and skip update
                        logger.info(f"Found existing product '{existing_name}' (ID: {product_id}) with better units ({existing_units} vs {new_units}) - KEEPING EXISTING")
                        conn.commit()
                        return product_id
                    
                    # Check if new has better units - if so, prefer new (update existing)
                    if existing_is_nonclassic and has_better_units(new_units, existing_units or '', True):
                        # New has better units (mg/count/oz vs g), prefer new - will update below
                        logger.info(f"Found existing product '{existing_name}' (ID: {product_id}) - NEW has better units ({new_units} vs {existing_units}) - PREFERRING NEW")
                    
                    # Log duplicate detection and update
                    logger.info(f"Found existing product: '{existing_name}' (ID: {product_id}, occurrences: {occurrences}) - REPLACING WITH NEW EXCEL DATA")
                    
                    # CBD detection before update: Check product name/description for ratios/CBD tokens
                    if not is_classic_type:
                        product_name_upper = (product_name or '').upper()
                        description_upper = (product_data.get('Description', '') or '').upper()
                        has_ratio = bool(re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', product_name_upper) or re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', description_upper))
                        has_cbd_token = any(token in product_name_upper for token in ['CBD', 'CBG', 'CBN', 'CBC']) or any(token in description_upper for token in ['CBD', 'CBG', 'CBN', 'CBC'])
                        
                        if has_ratio or has_cbd_token:
                            product_data['Product Strain'] = 'CBD Blend'
                            product_data['Lineage'] = 'CBD'
                            logger.info(f"✅ CBD DETECTION (update): Product '{product_name}' has CBD indicators -> Product Strain='CBD Blend', Lineage='CBD'")
                    
                    # Update existing product with new data (new data always replaces old values)
                    try:
                        self._update_existing_product(cursor, product_id, product_data)
                        conn.commit()
                        logger.info(f"Successfully replaced existing product '{existing_name}' with new Excel data")
                        return product_id
                    except RuntimeError as e:
                        # Handle database corruption recovery - retry the entire operation
                        if "corruption" in str(e).lower() or "recovered" in str(e).lower():
                            logger.info(f"🔄 Retrying product update after corruption recovery...")
                            conn.rollback()
                            # Close connection and retry from the beginning
                            self.close_all_connections()
                            return self.add_or_update_product(product_data)
                        raise
                
                # If no exact match, check by name and vendor only (ignore brand differences)
                # Also check for duplicates with different weights but prefer ones with better units
                cursor.execute('''
                    SELECT id, total_occurrences, "Product Name*", "Product Brand", Units, "Product Type*", "Weight*"
                    FROM products 
                    WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Type*" = ?
                    ORDER BY updated_at DESC
                ''', (normalized_name, vendor_value, product_data.get('Product Type*', '')))
                
                vendor_matches = cursor.fetchall()
                if vendor_matches:
                    # For non-classic types, prefer matches with proper units (mg, count, oz) over grams
                    best_match = None
                    best_match_score = -1
                    
                    for match in vendor_matches:
                        match_id, match_occurrences, match_name, match_brand, match_units, match_product_type, match_weight = match
                        match_is_nonclassic = match_product_type and match_product_type.strip().lower() not in CLASSIC_TYPES and not any(ct in match_product_type.strip().lower() for ct in CLASSIC_TYPES)
                        
                        # Score: prefer proper units (mg, count, oz, ml) over grams for non-classic types
                        score = 0
                        if match_is_nonclassic:
                            match_units_lower = (match_units or '').strip().lower()
                            # Highest priority: mg, count, each, pieces (proper units for edibles)
                            if 'mg' in match_units_lower or 'milligram' in match_units_lower:
                                score = 4  # mg is most preferred for edibles
                            elif any(unit in match_units_lower for unit in ['count', 'each', 'piece', 'pieces']):
                                score = 4  # count/each/pieces also most preferred
                            elif 'oz' in match_units_lower or 'ounce' in match_units_lower:
                                score = 3  # oz is preferred
                            elif 'ml' in match_units_lower or 'milliliter' in match_units_lower:
                                score = 3  # ml is preferred
                            elif 'g' in match_units_lower or 'gram' in match_units_lower:
                                score = 1  # g is least preferred for non-classic types
                        
                        if score > best_match_score:
                            best_match_score = score
                            best_match = match
                    
                    if best_match:
                        product_id, occurrences, existing_name, existing_brand, existing_units, existing_product_type, existing_weight = best_match
                        
                        # Check if new data has better units
                        new_units = product_data.get('Units', '') or product_data.get('Weight Unit* (grams/gm or ounces/oz)', '')
                        existing_is_nonclassic = existing_product_type and existing_product_type.strip().lower() not in CLASSIC_TYPES and not any(ct in existing_product_type.strip().lower() for ct in CLASSIC_TYPES)
                        
                        # Check if existing has better units - if so, keep existing
                        if existing_is_nonclassic and has_better_units(existing_units or '', new_units, True):
                            # Existing has better units (mg/count/oz vs g), keep existing
                            logger.info(f"Found similar product '{existing_name}' (ID: {product_id}) with better units ({existing_units} vs {new_units}) - KEEPING EXISTING")
                            conn.commit()
                            return product_id
                        
                        # Check if new has better units - if so, prefer new (update existing)
                        if existing_is_nonclassic and has_better_units(new_units, existing_units or '', True):
                            # New has better units (mg/count/oz vs g), prefer new - will update below
                            logger.info(f"Found similar product '{existing_name}' (ID: {product_id}) - NEW has better units ({new_units} vs {existing_units}) - PREFERRING NEW")
                        
                        logger.info(f"Found similar product by name+vendor: '{existing_name}' (Brand: {existing_brand}) - REPLACING WITH NEW DATA")
                        try:
                            self._update_existing_product(cursor, product_id, product_data)
                            conn.commit()
                            logger.info(f"Successfully updated product '{existing_name}' with new Excel data")
                            return product_id
                        except RuntimeError as e:
                            # Handle database corruption recovery - retry the entire operation
                            if "corruption" in str(e).lower() or "recovered" in str(e).lower():
                                logger.info(f"🔄 Retrying product update after corruption recovery...")
                                conn.rollback()
                                # Close connection and retry from the beginning
                                self.close_all_connections()
                                return self.add_or_update_product(product_data)
                            raise
                
                # Check for similar products (same name + vendor + product type, different brand)
                cursor.execute('''
                    SELECT id, total_occurrences, "Product Name*", "Product Brand"
                    FROM products 
                    WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Type*" = ? AND "Product Brand" != ?
                ''', (normalized_name, product_data.get('Vendor/Supplier*'), product_data.get('Product Type*', ''), product_data.get('Product Brand')))
                
                similar_products = cursor.fetchall()
                if similar_products:
                    logger.info(f"Found {len(similar_products)} similar products with same name '{product_name}' and vendor '{product_data.get('Vendor')}' but different brands")
                    for similar_id, similar_occurrences, similar_name, similar_brand in similar_products:
                        logger.debug(f"Similar product: '{similar_name}' (Brand: {similar_brand}, ID: {similar_id})")
                else:
                    # Get available columns dynamically to avoid SQL errors
                    cursor.execute("PRAGMA table_info(products)")
                    available_columns = {row[1] for row in cursor.fetchall()}
                    
                    # CRITICAL FIX: For NEW products from Excel, ALWAYS use Excel lineage
                    # Don't check sovereign_lineage - that's only for manual Tag Manager overrides
                    # Excel is the source of truth for new products
                    lineage_to_use = self._normalize_lineage(product_data.get('Lineage'))
                    logger.info(f"📊 NEW PRODUCT: Using Excel lineage '{lineage_to_use}' for '{product_name}'")
                    
                    # Build column list and values list based on what exists
                    columns_to_insert = []
                    values_to_insert = []
                    
                    # CBD detection: Check product name/description for ratios (1:1:1, etc.) or CBD tokens
                    # Only for nonclassic types - classic types keep their Lineage
                    import re
                    from src.core.constants import CLASSIC_TYPES
                    product_type_for_cbd = product_data.get('Product Type*', '').strip().lower()
                    is_classic_type = product_type_for_cbd in CLASSIC_TYPES or any(ct in product_type_for_cbd for ct in CLASSIC_TYPES)
                    
                    product_name_upper = (product_name or '').upper()
                    description_upper = (product_data.get('Description', '') or '').upper()
                    has_ratio = bool(re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', product_name_upper) or re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', description_upper))
                    has_cbd_token = any(token in product_name_upper for token in ['CBD', 'CBG', 'CBN', 'CBC']) or any(token in description_upper for token in ['CBD', 'CBG', 'CBN', 'CBC'])
                    
                    # Calculate Product Strain first
                    calculated_strain = self._calculate_product_strain_original(
                        product_data.get('Product Type*', ''),
                        product_data.get('Product Name*', ''),
                        product_data.get('Description', ''),
                        product_data.get('Ratio', '')
                    )
                    
                    # For nonclassic types: if CBD indicators found, override Product Strain and Lineage
                    final_strain = calculated_strain
                    final_lineage = lineage_to_use
                    if not is_classic_type and (has_ratio or has_cbd_token):
                        final_strain = 'CBD Blend'
                        final_lineage = 'CBD'
                        logger.info(f"✅ CBD DETECTION: Product '{product_name}' has CBD indicators -> Product Strain='CBD Blend', Lineage='CBD'")
                    
                    # Map of data to potential column names
                    column_data_map = {
                        'Product Name*': product_name,
                        'normalized_name': normalized_name,
                        'Product Strain': final_strain,
                        'Product Type*': product_data.get('Product Type*'),  # EXCEL PRIORITY: Excel Product Type (High THC/CBD) always overwrites DB
                        'Vendor/Supplier*': product_data.get('Vendor/Supplier*'),
                        'Product Brand': product_data.get('Product Brand'),
                        'Description': self._process_description(product_data.get('Product Name*', ''), product_data.get('Description', '')),
                        'Weight*': product_data.get('Weight*'),
                        'Units': product_data.get('Units'),
                        'Price': product_data.get('Price'),  # EXCEL PRIORITY: Excel Price always overwrites DB
                        'Lineage': final_lineage,  # CBD override for nonclassic types
                        'first_seen_date': current_date,
                        'last_seen_date': current_date,
                        'created_at': current_date,
                        'updated_at': current_date,
                        'Quantity*': product_data.get('Quantity*', ''),
                        'DOH': product_data.get('DOH', ''),  # EXCEL PRIORITY: Excel DOH always overwrites DB
                        'Concentrate Type': product_data.get('Concentrate Type', ''),
                        'Ratio': product_data.get('Ratio', ''),
                        'JointRatio': product_data.get('JointRatio', ''),
                        'Test result unit (% or mg)': product_data.get('Test result unit (% or mg)', ''),
                        'State': product_data.get('State', ''),
                        'Is Sample? (yes/no)': product_data.get('Is Sample? (yes/no)', ''),
                        'Is MJ product?(yes/no)': product_data.get('Is MJ product?(yes/no)', ''),
                        'Discountable? (yes/no)': product_data.get('Discountable? (yes/no)', ''),
                        'Room*': product_data.get('Room*', ''),
                        'Batch Number': product_data.get('Batch Number', ''),
                        'Lot Number': product_data.get('Lot Number', ''),
                        'Barcode*': product_data.get('Barcode*', ''),
                        'Medical Only (Yes/No)': product_data.get('Medical Only (Yes/No)', ''),
                        'Med Price': product_data.get('Med Price', ''),
                        'Expiration Date(YYYY-MM-DD)': product_data.get('Expiration Date(YYYY-MM-DD)', ''),
                        'Is Archived? (yes/no)': product_data.get('Is Archived? (yes/no)', ''),
                        'THC Per Serving': product_data.get('THC Per Serving', ''),
                        'Allergens': product_data.get('Allergens', ''),
                        'Solvent': product_data.get('Solvent', ''),
                        'Accepted Date': product_data.get('Accepted Date', ''),
                        'Internal Product Identifier': product_data.get('Internal Product Identifier', ''),
                        'Product Tags (comma separated)': product_data.get('Product Tags (comma separated)', ''),
                        'Image URL': product_data.get('Image URL', ''),
                        'Ingredients': product_data.get('Ingredients', ''),
                        'CombinedWeight': product_data.get('CombinedWeight', ''),
                        'Ratio_or_THC_CBD': self._calculate_ratio_or_thc_cbd(
                            product_data.get('Product Type*', ''),
                            product_data.get('Ratio', ''),
                            product_data.get('JointRatio', ''),
                            product_name
                        ),
                        'Total THC': product_data.get('Total THC', ''),
                        'THCA': product_data.get('THCA', ''),
                        'CBDA': product_data.get('CBDA', ''),
                        'CBN': product_data.get('CBN', ''),
                        'THC': product_data.get('THC', ''),
                        'CBD': product_data.get('CBD', ''),
                        'Total CBD': product_data.get('Total CBD', ''),
                        'CBGA': product_data.get('CBGA', ''),
                        'CBG': product_data.get('CBG', ''),
                        'Total CBG': product_data.get('Total CBG', ''),
                        'CBC': product_data.get('CBC', ''),
                        'CBDV': product_data.get('CBDV', ''),
                        'THCV': product_data.get('THCV', ''),
                        'CBGV': product_data.get('CBGV', ''),
                        'CBNV': product_data.get('CBNV', ''),
                        'CBGVA': product_data.get('CBGVA', ''),
                        'total_occurrences': 1,
                        'strain_id': strain_id,
                        'Weight Unit* (grams/gm or ounces/oz)': product_data.get('Weight Unit* (grams/gm or ounces/oz)', product_data.get('Units', '')),
                        'THC test result': product_data.get('THC test result', ''),
                        'CBD test result': product_data.get('CBD test result', ''),
                        'JSON': product_data.get('JSON', ''),  # Original Description for JSON URL matching
                    }

                    # CRITICAL FIX: Include ALL remaining fields from product_data that aren't already in column_data_map
                    # This ensures all Excel columns are included, not just the hardcoded ones
                    # CRITICAL: Block canonical_lineage from Excel - it must ONLY come from strains table
                    BLOCKED_EXCEL_COLUMNS = ['canonical_lineage', 'currentLineage']  # Never allow Excel to set these
                    for col_name, col_value in product_data.items():
                        if col_name not in column_data_map:
                            # CRITICAL: Block canonical_lineage from being set via Excel uploads
                            if col_name in BLOCKED_EXCEL_COLUMNS:
                                logger.info(f"✅ BLOCKED Excel column '{col_name}' from being written to database (must come from strains table only)")
                                continue
                            # Only add if the column exists in the database
                            # Also validate column name to prevent SQL injection
                            if col_name in available_columns and isinstance(col_name, str):
                                # Clean the value - convert None to empty string, handle NaN
                                if col_value is None:
                                    clean_value = ''
                                elif isinstance(col_value, str) and col_value.lower() in ['nan', 'none', 'null']:
                                    clean_value = ''
                                else:
                                    clean_value = col_value
                                column_data_map[col_name] = clean_value
                    
                    # Only include columns that exist in the database
                    # SECURITY: Validate column names to prevent SQL injection
                    for col_name, col_value in column_data_map.items():
                        if col_name in available_columns:
                            # Additional security check: ensure column name doesn't contain SQL injection patterns
                            if any(char in col_name for char in [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']):
                                logger.warning(f"SECURITY: Suspicious column name detected and rejected: {col_name}")
                                continue
                            columns_to_insert.append(f'"{col_name}"')
                            values_to_insert.append(col_value)
                    
                    # Build the INSERT statement dynamically
                    columns_str = ', '.join(columns_to_insert)
                    placeholders = ', '.join(['?' for _ in values_to_insert])
                    
                    # VALIDATION: reject blank/empty normalized names to avoid creating empty entries
                    if not normalized_name or str(normalized_name).strip() == '':
                        self._rejected_blank_names += 1
                        logger.warning(f"Rejected product with blank normalized name: original='{product_name}'")
                        return None

                    # SAFETY: check for existing product with same normalized name and update instead
                    try:
                        cursor.execute('SELECT id FROM products WHERE normalized_name = ? AND "Product Type*" = ? LIMIT 1', (normalized_name, product_data.get('Product Type*', '')))
                        existing_row = cursor.fetchone()
                        if existing_row:
                            existing_id = existing_row[0]
                            logger.info(f"Found existing product with same normalized_name='{normalized_name}' and type='{product_data.get('Product Type*', '')}' (ID: {existing_id}) - updating instead of inserting")
                            try:
                                self._update_existing_product(cursor, existing_id, product_data)
                                conn.commit()
                                return existing_id
                            except Exception as upd_err:
                                logger.warning(f"Failed to update existing product (ID: {existing_id}), will attempt insert: {upd_err}")
                                conn.rollback()
                    except Exception as e:
                        logger.debug(f"Pre-insert existence check failed: {e}")

                    # SECURITY: Final validation - ensure we have valid columns
                    if not columns_to_insert:
                        logger.error("SECURITY: No valid columns to insert after validation")
                        return None
                    
                    insert_query = f'INSERT INTO products ({columns_str}) VALUES ({placeholders})'
                    try:
                        cursor.execute(insert_query, values_to_insert)
                        product_id = cursor.lastrowid
                        conn.commit()
                        logger.info(f"✅ ADDED NEW product '{product_name}' (ID: {product_id}, Vendor: {vendor_value}, Brand: {brand_value})")
                        return product_id
                    except sqlite3.IntegrityError as e:
                        # Handle UNIQUE constraint violation - product already exists with same name/vendor/brand/weight
                        if "UNIQUE constraint failed" in str(e) or "unique constraint" in str(e).lower():
                            logger.warning(f"⚠️ UNIQUE constraint violation for '{product_name}' (Vendor: {vendor_value}, Brand: {brand_value}) - attempting to find and update existing product")
                            conn.rollback()
                            
                            # Try to find the existing product using only the 4 fields
                            # that make up the UNIQUE constraint — NOT Product Type*, which
                            # may differ and would cause the lookup to miss the row.
                            weight_value = product_data.get('Weight*', '')
                            cursor.execute('''
                                SELECT id, total_occurrences, "Product Name*"
                                FROM products
                                WHERE "Product Name*" = ? AND "Vendor/Supplier*" = ? AND "Product Brand" = ? AND "Weight*" = ?
                            ''', (product_name, vendor_value, brand_value, weight_value))
                            
                            existing = cursor.fetchone()
                            if existing:
                                product_id, occurrences, existing_name = existing
                                logger.info(f"Found existing product via UNIQUE constraint: '{existing_name}' (ID: {product_id}) - UPDATING")
                                try:
                                    self._update_existing_product(cursor, product_id, product_data)
                                    conn.commit()
                                    logger.info(f"Successfully updated product '{existing_name}' after UNIQUE constraint violation")
                                    return product_id
                                except Exception as update_error:
                                    logger.error(f"Failed to update product after UNIQUE constraint: {update_error}")
                                    conn.rollback()
                                    raise
                            else:
                                logger.error(f"UNIQUE constraint violation but could not find existing product: {e}")
                                raise
                        else:
                            # Other integrity errors
                            logger.error(f"Integrity error inserting product '{product_name}': {e}")
                            conn.rollback()
                            raise
                
        except Exception as e:
            product_name = product_data.get('Product Name*', product_data.get('ProductName', ''))
            logger.error(f"Error adding/updating product '{product_name}': {e}")
            raise
    
    def log_rejection_summary(self):
        """Log summary of rejected products to provide insight into data quality issues."""
        total_rejected = (self._rejected_blank_names + self._rejected_invalid_names + 
                         self._rejected_short_names + self._rejected_missing_vendor + 
                         self._rejected_missing_type)
        
        if total_rejected > 0:
            logger.info(f"📊 Product Rejection Summary:")
            logger.info(f"   Blank/empty names: {self._rejected_blank_names}")
            logger.info(f"   Invalid names: {self._rejected_invalid_names}")
            logger.info(f"   Too short names: {self._rejected_short_names}")
            logger.info(f"   Missing vendor: {self._rejected_missing_vendor}")
            logger.info(f"   Missing product type: {self._rejected_missing_type}")
            logger.info(f"   Total rejected: {total_rejected}")
    
    def store_excel_data(self, df: pd.DataFrame, source_file: str = None, _retry_on_schema_error: bool = True) -> Dict[str, Any]:
        """Store Excel data in the database. New data replaces existing data when duplicates are found."""
        try:
            self.init_database()  # Ensure DB is initialized
            logger.info(f"Starting to store Excel data with {len(df)} rows from {source_file}")
            
            if df is None or df.empty:
                logger.warning("No data to store - DataFrame is empty")
                return {'stored': 0, 'updated': 0, 'errors': 0, 'message': 'No data to store'}
            
            # CRITICAL FIX: Store ALL Excel data - don't filter it out
            # The filter should ONLY exclude products that are EXPLICITLY JSON matched tags
            # Excel uploads should ALWAYS be stored
            filtered_df = self._filter_json_matched_tags(df)
            
            # CRITICAL: If filtering removed everything, check if this is Excel data
            # Excel data should NEVER be filtered out completely
            if filtered_df.empty and not df.empty:
                logger.warning(f"⚠️ Filter removed all {len(df)} rows - checking if this is Excel data")
                # Check if any rows have Excel indicators
                has_excel_indicators = False
                if 'Source' in df.columns:
                    excel_mask = df['Source'].astype(str).str.contains('Excel|Upload|Import', case=False, na=False)
                    has_excel_indicators = excel_mask.any()
                
                # If this looks like Excel data, don't filter it
                if has_excel_indicators or 'Source' not in df.columns:
                    logger.warning(f"⚠️ This appears to be Excel data - storing ALL {len(df)} rows (bypassing filter)")
                    filtered_df = df.copy()
                else:
                    logger.warning(f"⚠️ All rows were filtered as JSON matched tags - nothing to store")
            
            logger.info(f"📊 Excel storage: {len(df)} original rows → {len(filtered_df)} rows to store")

            # CRITICAL NORMALIZATION: map common column aliases used by different upload paths
            try:
                cols = set(filtered_df.columns)
                # Product name
                if 'Product Name*' not in cols and 'ProductName' in cols:
                    filtered_df['Product Name*'] = filtered_df['ProductName']
                    cols.add('Product Name*')
                if 'Product Name*' in cols:
                    filtered_df['Product Name*'] = filtered_df['Product Name*'].astype(str).str.strip()

                # Vendor - check multiple column name variations
                vendor_cols = ['Vendor/Supplier*', 'Vendor/Supplier', 'Vendor', 'vendor', 'Supplier', 'supplier']
                vendor_found = None
                for vcol in vendor_cols:
                    if vcol in cols:
                        vendor_found = vcol
                        break
                
                if vendor_found and 'Vendor/Supplier*' not in cols:
                    filtered_df['Vendor/Supplier*'] = filtered_df[vendor_found]
                    cols.add('Vendor/Supplier*')
                    logger.info(f"📊 VENDOR MAPPING: Mapped '{vendor_found}' column to 'Vendor/Supplier*'")
                
                if 'Vendor/Supplier*' in cols:
                    filtered_df['Vendor/Supplier*'] = filtered_df['Vendor/Supplier*'].astype(str).str.strip()
                    # Log vendor values to debug missing vendors
                    non_empty_vendors = filtered_df['Vendor/Supplier*'].notna() & (filtered_df['Vendor/Supplier*'] != '')
                    vendor_count = non_empty_vendors.sum()
                    logger.info(f"📊 VENDOR CHECK: Found {vendor_count}/{len(filtered_df)} rows with vendor values")
                    if vendor_count < len(filtered_df):
                        empty_vendor_rows = filtered_df[~non_empty_vendors]
                        if len(empty_vendor_rows) > 0:
                            logger.warning(f"⚠️ VENDOR MISSING: {len(empty_vendor_rows)} rows have empty vendor values")
                            logger.warning(f"   First few product names with missing vendors: {empty_vendor_rows['Product Name*'].head(3).tolist() if 'Product Name*' in empty_vendor_rows.columns else 'N/A'}")

                # Product type
                if 'Product Type*' not in cols and 'Product Type' in cols:
                    filtered_df['Product Type*'] = filtered_df['Product Type']
                    cols.add('Product Type*')
                if 'Product Type*' in cols:
                    filtered_df['Product Type*'] = filtered_df['Product Type*'].astype(str).str.strip()

                # Price
                if 'Price' not in cols and 'Price* (Tier Name for Bulk)' in cols:
                    filtered_df['Price'] = filtered_df['Price* (Tier Name for Bulk)']
                    cols.add('Price')
                if 'Price' in cols:
                    filtered_df['Price'] = filtered_df['Price'].astype(str).str.strip()

                # Ensure minimal required fields exist to avoid skipping rows later
                for required_col in ['Product Name*', 'Product Type*', 'Vendor/Supplier*']:
                    if required_col not in filtered_df.columns:
                        filtered_df[required_col] = ''
            except Exception as norm_err:
                logger.warning(f"Column normalization failed: {norm_err}")
            
            print(f"🔍 DEBUG: Database storage - Original rows: {len(df)}, Filtered rows: {len(filtered_df)}")
            print(f"🔍 DEBUG: Database storage - Columns: {list(filtered_df.columns)}")
            
            # if filtered_df.empty:
            #     logger.warning("All data was filtered out as JSON matched tags - nothing to store")
            #     return {
            #         'stored': 0, 
            #         'updated': 0, 
            #         'errors': 0, 
            #         'excluded_json_matches': len(df),
            #         'message': f'All {len(df)} rows were JSON matched tags - excluded from database storage'
            #     }
            
            # Initialize duplicate tracking for this upload
            self._current_upload_products = set()
            
            stored_count = 0
            updated_count = 0
            skipped_duplicates = 0
            error_count = 0
            errors = []
            
            # CRITICAL FIX: Filter out rows with blank product names BEFORE processing
            # This prevents trying to add empty rows and avoids thousands of rejection log messages
            if 'Product Name*' in filtered_df.columns:
                valid_mask = filtered_df['Product Name*'].notna() & (filtered_df['Product Name*'].astype(str).str.strip() != '')
                filtered_df = filtered_df[valid_mask]
                print(f"🔍 DEBUG: Filtered out blank product names - Processing {len(filtered_df)} valid rows")
            
            # Process each row in the filtered DataFrame
            print(f"🔍 DEBUG: Starting to process {len(filtered_df)} rows for database storage")
            for index, row in filtered_df.iterrows():
                try:
                    if index % 100 == 0:  # Log every 100 rows
                        print(f"🔍 DEBUG: Processing row {index}/{len(filtered_df)}")
                    # Convert row to dictionary and handle NaN values
                    row_dict = {}
                    for col in filtered_df.columns:
                        value = row[col]
                        if pd.isna(value):
                            row_dict[col] = None
                        else:
                            row_dict[col] = str(value).strip() if isinstance(value, str) else value
                    
                    # Map to database columns correctly
                    # CRITICAL FIX: Preserve actual Excel weight values, don't use fallbacks
                    excel_weight = row_dict.get('Weight*', row_dict.get('Weight', ''))
                    excel_units = row_dict.get('Units', row_dict.get('Weight Unit*', row_dict.get('Weight Unit* (grams/gm or ounces/oz)', '')))
                    
                    # Log first few weight extractions for debugging
                    if index < 5:  # Log first 5 products
                        product_name_for_log = row_dict.get('Product Name*', 'Unknown')
                        logger.info(f"[WEIGHT DEBUG] Product: '{product_name_for_log}' | Excel Weight: '{excel_weight}' | Excel Units: '{excel_units}'")
                    
                    # CRITICAL: Use explicit None check instead of truthiness to handle '0' values correctly
                    # Only use fallback if weight is None, empty string, or invalid (not when it's '0')
                    if excel_weight is not None and str(excel_weight).strip() not in ['', 'nan', 'none', 'null', 'NaN', 'None']:
                        weight_value = str(excel_weight).strip()
                    else:
                        weight_value = '1'  # Numeric value only as fallback
                        if index < 5:
                            logger.warning(f"[WEIGHT DEBUG] Using fallback weight '1' for product '{row_dict.get('Product Name*', 'Unknown')}' (original: '{excel_weight}')")
                    
                    if excel_units is not None and str(excel_units).strip() not in ['', 'nan', 'none', 'null', 'NaN', 'None']:
                        units_value = str(excel_units).strip()
                    else:
                        units_value = 'g'  # Default unit as fallback
                        if index < 5:
                            logger.warning(f"[WEIGHT DEBUG] Using fallback units 'g' for product '{row_dict.get('Product Name*', 'Unknown')}' (original: '{excel_units}')")
                    
                    # Final debug log
                    if index < 5:
                        logger.info(f"[WEIGHT DEBUG] Final values - Weight: '{weight_value}' | Units: '{units_value}'")
                    
                    # CRITICAL FIX: Check ALL vendor column name variations from Excel
                    vendor_raw = (row_dict.get('Vendor/Supplier*', '') or 
                                 row_dict.get('Vendor/Supplier', '') or 
                                 row_dict.get('Vendor', '') or 
                                 row_dict.get('vendor', '') or 
                                 row_dict.get('Supplier', '') or 
                                 row_dict.get('supplier', '') or 
                                 '')
                    vendor_value = self._ensure_crucial_value(vendor_raw, 'Unknown Vendor', 'Vendor')
                    
                    # CBD detection: Check product name/description for ratios (1:1:1, etc.) or CBD tokens
                    # Only for nonclassic types - classic types keep their Lineage
                    import re
                    from src.core.constants import CLASSIC_TYPES
                    product_name_for_cbd = row_dict.get('Product Name*', '')
                    product_type_for_cbd = self._ensure_crucial_value(row_dict.get('Product Type*', ''), 'Unknown', 'Product Type').strip().lower()
                    is_classic_type = product_type_for_cbd in CLASSIC_TYPES or any(ct in product_type_for_cbd for ct in CLASSIC_TYPES)
                    
                    product_name_upper = (product_name_for_cbd or '').upper()
                    description_upper = (row_dict.get('Description', '') or '').upper()
                    has_ratio = bool(re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', product_name_upper) or re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', description_upper))
                    has_cbd_token = any(token in product_name_upper for token in ['CBD', 'CBG', 'CBN', 'CBC']) or any(token in description_upper for token in ['CBD', 'CBG', 'CBN', 'CBC'])
                    
                    # Determine Product Strain and Lineage
                    original_strain = row_dict.get('Product Strain', '')
                    original_lineage = row_dict.get('Lineage', '')
                    
                    # For nonclassic types: if CBD indicators found, override Product Strain and Lineage
                    final_strain = original_strain
                    final_lineage = original_lineage
                    if not is_classic_type and (has_ratio or has_cbd_token):
                        final_strain = 'CBD Blend'
                        final_lineage = 'CBD'
                        logger.info(f"✅ CBD DETECTION (store_excel_data): Product '{product_name_for_cbd}' has CBD indicators -> Product Strain='CBD Blend', Lineage='CBD'")
                    
                    product_data = {
                        'Product Name*': product_name_for_cbd,
                        'Product Type*': self._ensure_crucial_value(row_dict.get('Product Type*', ''), 'Unknown', 'Product Type'),
                        'Lineage': final_lineage,
                        'Vendor/Supplier*': vendor_value,
                        'Vendor': vendor_value,
                        'Product Brand': self._ensure_crucial_value(row_dict.get('Product Brand', ''), 'Unknown Brand', 'Product Brand'),
                        'Description': self._process_description(
                            row_dict.get('Product Name*', ''), 
                            row_dict.get('Description', '')
                        ),
                        'Weight*': weight_value,
                        'Units': units_value,
                        'Price': self._ensure_crucial_value(row_dict.get('Price*', row_dict.get('Price', '')), '0.00', 'Price'),
                        'Product Strain': final_strain,
                        'Quantity*': row_dict.get('Quantity*', ''),
                        # CRITICAL FIX: Check multiple DOH column names from Excel
                        'DOH': (row_dict.get('DOH', '') or 
                                row_dict.get('DOH Compliant (Yes/No)', '') or 
                                row_dict.get('DOH Compliant*', '') or 
                                row_dict.get('DOH*', '') or 
                                ''),
                        'Concentrate Type': row_dict.get('Concentrate Type', ''),
                        'Ratio': self._extract_ratio_from_product_name(
                            row_dict.get('Product Name*', ''), 
                            row_dict.get('Product Type*', '')
                        ) if not (row_dict.get('Ratio', '') or '').strip() else row_dict.get('Ratio', ''),
                        'JointRatio': row_dict.get('JointRatio', ''),
                        'THC test result': self._ensure_crucial_value(row_dict.get('THC Content', ''), '0.0', 'THC Content'),
                        'CBD test result': self._ensure_crucial_value(row_dict.get('CBD test result', ''), '0.0', 'CBD test result'),
                        'Test result unit (% or mg)': row_dict.get('Test result unit (% or mg)', ''),
                        'State': row_dict.get('State', ''),
                        'Is Sample? (yes/no)': row_dict.get('Is Sample? (yes/no)', ''),
                        'Is MJ product?(yes/no)': row_dict.get('Is MJ product?(yes/no)', ''),
                        'Discountable? (yes/no)': row_dict.get('Discountable? (yes/no)', ''),
                        'Room*': row_dict.get('Room*', ''),
                        'Batch Number': row_dict.get('Batch Number', ''),
                        'Lot Number': row_dict.get('Lot Number', ''),
                        'Barcode*': row_dict.get('Barcode*', ''),
                        'Medical Only (Yes/No)': row_dict.get('Medical Only (Yes/No)', ''),
                        'Med Price': row_dict.get('Med Price', ''),
                        'Expiration Date(YYYY-MM-DD)': row_dict.get('Expiration Date(YYYY-MM-DD)', ''),
                        'Is Archived? (yes/no)': row_dict.get('Is Archived? (yes/no)', ''),
                        'THC Per Serving': row_dict.get('THC Per Serving', ''),
                        'Allergens': row_dict.get('Allergens', ''),
                        'Solvent': row_dict.get('Solvent', ''),
                        'Accepted Date': row_dict.get('Accepted Date', ''),
                        'Internal Product Identifier': row_dict.get('Internal Product Identifier', ''),
                        'Product Tags (comma separated)': row_dict.get('Product Tags (comma separated)', ''),
                        'Image URL': row_dict.get('Image URL', ''),
                        'Ingredients': row_dict.get('Ingredients', ''),
                        # Additional columns for comprehensive Excel data matching
                        'Total THC': row_dict.get('Total THC', ''),
                        'THCA': row_dict.get('THC Content', ''),
                        'CBDA': row_dict.get('Total CBD', ''),
                        'CBN': row_dict.get('CBN', ''),
                        'Ratio_or_THC_CBD': row_dict.get('Ratio_or_THC_CBD', ''),
                        # CRITICAL FIX: Check ALL vendor column name variations from Excel
                        'Vendor/Supplier*': (row_dict.get('Vendor/Supplier*', '') or 
                                             row_dict.get('Vendor/Supplier', '') or 
                                             row_dict.get('Vendor', '') or 
                                             row_dict.get('vendor', '') or 
                                             row_dict.get('Supplier', '') or 
                                             row_dict.get('supplier', '') or 
                                             ''),
                        'Vendor/Supplier': (row_dict.get('Vendor/Supplier', '') or 
                                           row_dict.get('Vendor/Supplier*', '') or 
                                           row_dict.get('Vendor', '') or 
                                           ''),
                        'Vendor': (row_dict.get('Vendor', '') or 
                                  row_dict.get('Vendor/Supplier*', '') or 
                                  row_dict.get('Vendor/Supplier', '') or 
                                  ''),
                        'Product Name*': row_dict.get('Product Name*', ''),
                        'Product Name': row_dict.get('Product Name', ''),
                        'Quantity Received*': row_dict.get('Quantity Received*', ''),
                        'WeightWithUnits': row_dict.get('WeightWithUnits', ''),
                        'WeightUnits': row_dict.get('WeightUnits', ''),
                        'ProductBrand': row_dict.get('ProductBrand', ''),
                        'ProductBrandCenter': row_dict.get('ProductBrandCenter', ''),
                        'THC_CBD': row_dict.get('THC_CBD', ''),
                        'THC': row_dict.get('THC', ''),  # Direct THC value from Excel
                        'CBD': row_dict.get('CBD', ''),  # Direct CBD value from Excel
                        'AI': self._calculate_ai_value(row_dict),  # Calculate THC value
                        'AJ': row_dict.get('THC Content', ''),  # THC Content
                        'AK': self._calculate_ak_value(row_dict),  # Calculate CBD value
                        # Source field to track where the data came from
                        'Source': row_dict.get('Source', f'Excel Import - {source_file}' if source_file else 'Excel Import'),
                        # Date Added field to track when the data was added
                        'Date Added': row_dict.get('Date Added', datetime.now().isoformat()),
                        # Terpene columns
                        'A-Bisabolol (mg/g)': row_dict.get('A-Bisabolol (mg/g)', ''),
                        'A-Humulene (mg/g)': row_dict.get('A-Humulene (mg/g)', ''),
                        'A-Maaliene (mg/g)': row_dict.get('A-Maaliene (mg/g)', ''),
                        'A-Myrcene (mg/g)': row_dict.get('A-Myrcene (mg/g)', ''),
                        'A-Pinene (mg/g)': row_dict.get('A-Pinene (mg/g)', ''),
                        'B-Caryophyllene (mg/g)': row_dict.get('B-Caryophyllene (mg/g)', ''),
                        'B-Myrcene (mg/g)': row_dict.get('B-Myrcene (mg/g)', ''),
                        'B-Pinene (mg/g)': row_dict.get('B-Pinene (mg/g)', ''),
                        'Bisabolol (mg/g)': row_dict.get('Bisabolol (mg/g)', ''),
                        'Borneol (mg/g)': row_dict.get('Borneol (mg/g)', ''),
                        'Camphene (mg/g)': row_dict.get('Camphene (mg/g)', ''),
                        'Camphor (mg/g)': row_dict.get('Camphor (mg/g)', ''),
                        'Carene (mg/g)': row_dict.get('Carene (mg/g)', ''),
                        'Carvacrol (mg/g)': row_dict.get('Carvacrol (mg/g)', ''),
                        'Carvone (mg/g)': row_dict.get('Carvone (mg/g)', ''),
                        'Caryophyllene (mg/g)': row_dict.get('Caryophyllene (mg/g)', ''),
                        'Cedrol (mg/g)': row_dict.get('Cedrol (mg/g)', ''),
                        'Citral (mg/g)': row_dict.get('Citral (mg/g)', ''),
                        'Citronellol (mg/g)': row_dict.get('Citronellol (mg/g)', ''),
                        'Cymene (mg/g)': row_dict.get('Cymene (mg/g)', ''),
                        'Delta-3-Carene (mg/g)': row_dict.get('Delta-3-Carene (mg/g)', ''),
                        'Eucalyptol (mg/g)': row_dict.get('Eucalyptol (mg/g)', ''),
                        'Fenchol (mg/g)': row_dict.get('Fenchol (mg/g)', ''),
                        'Fenchone (mg/g)': row_dict.get('Fenchone (mg/g)', ''),
                        'Geraniol (mg/g)': row_dict.get('Geraniol (mg/g)', ''),
                        'Geranyl Acetate (mg/g)': row_dict.get('Geranyl Acetate (mg/g)', ''),
                        'Guaiol (mg/g)': row_dict.get('Guaiol (mg/g)', ''),
                        'Humulene (mg/g)': row_dict.get('Humulene (mg/g)', ''),
                        'Isoborneol (mg/g)': row_dict.get('Isoborneol (mg/g)', ''),
                        'Isobornyl Acetate (mg/g)': row_dict.get('Isobornyl Acetate (mg/g)', ''),
                        'Isopulegol (mg/g)': row_dict.get('Isopulegol (mg/g)', ''),
                        'Limonene (mg/g)': row_dict.get('Limonene (mg/g)', ''),
                        'Linalool (mg/g)': row_dict.get('Linalool (mg/g)', ''),
                        'Linalyl Acetate (mg/g)': row_dict.get('Linalyl Acetate (mg/g)', ''),
                        'M-Cymene (mg/g)': row_dict.get('M-Cymene (mg/g)', ''),
                        'Menthal (mg/g)': row_dict.get('Menthal (mg/g)', ''),
                        'Menthone (mg/g)': row_dict.get('Menthone (mg/g)', ''),
                        'Myrcene (mg/g)': row_dict.get('Myrcene (mg/g)', ''),
                        'Nerolidol (mg/g)': row_dict.get('Nerolidol (mg/g)', ''),
                        'O-Cymene (mg/g)': row_dict.get('O-Cymene (mg/g)', ''),
                        'Ocimene (mg/g)': row_dict.get('Ocimene (mg/g)', ''),
                        'P-Cymene (mg/g)': row_dict.get('P-Cymene (mg/g)', ''),
                        'Phellandrene (mg/g)': row_dict.get('Phellandrene (mg/g)', ''),
                        'Phytol (mg/g)': row_dict.get('Phytol (mg/g)', ''),
                        'Pinene (mg/g)': row_dict.get('Pinene (mg/g)', ''),
                        'Piperitone (mg/g)': row_dict.get('Piperitone (mg/g)', ''),
                        'Pulegone (mg/g)': row_dict.get('Pulegone (mg/g)', ''),
                        'Sabinene (mg/g)': row_dict.get('Sabinene (mg/g)', ''),
                        'Safranal (mg/g)': row_dict.get('Safranal (mg/g)', ''),
                        'Selinadiene (mg/g)': row_dict.get('Selinadiene (mg/g)', ''),
                        'Terpineol (mg/g)': row_dict.get('Terpineol (mg/g)', ''),
                        'Terpinolene (mg/g)': row_dict.get('Terpinolene (mg/g)', ''),
                        'Thujene (mg/g)': row_dict.get('Thujene (mg/g)', ''),
                        'Thymol (mg/g)': row_dict.get('Thymol (mg/g)', ''),
                        'Trans-Nerolidol (mg/g)': row_dict.get('Trans-Nerolidol (mg/g)', ''),
                        'Trans-Alpha-Bergamotene (mg/g)': row_dict.get('Trans-Alpha-Bergamotene (mg/g)', ''),
                        'Valencene (mg/g)': row_dict.get('Valencene (mg/g)', ''),
                        'Alpha-Bisabolene (mg/g)': row_dict.get('Alpha-Bisabolene (mg/g)', ''),
                        'Alpha-Bulnesene (mg/g)': row_dict.get('Alpha-Bulnesene (mg/g)', ''),
                        'Alpha-Farnesene (mg/g)': row_dict.get('Alpha-Farnesene (mg/g)', ''),
                        'Alpha-Maaliene (mg/g)': row_dict.get('Alpha-Maaliene (mg/g)', ''),
                        'Alpha-Ocimene (mg/g)': row_dict.get('Alpha-Ocimene (mg/g)', ''),
                        'Alpha-Phellandrene (mg/g)': row_dict.get('Alpha-Phellandrene (mg/g)', ''),
                        'Alpha-Pinene (mg/g)': row_dict.get('Alpha-Pinene (mg/g)', ''),
                        'Alpha-Terpinene (mg/g)': row_dict.get('Alpha-Terpinene (mg/g)', ''),
                        'Alpha-Thujone (mg/g)': row_dict.get('Alpha-Thujone (mg/g)', ''),
                        'Beta-Farnesene (mg/g)': row_dict.get('Beta-Farnesene (mg/g)', ''),
                        'Beta-Maaliene (mg/g)': row_dict.get('Beta-Maaliene (mg/g)', ''),
                        'Alpha-Maaliene (mg/g)': row_dict.get('Alpha-Maaliene (mg/g)', ''),
                        'Beta-Ocimene (mg/g)': row_dict.get('Beta-Ocimene (mg/g)', ''),
                        'Beta-Pinene (mg/g)': row_dict.get('Beta-Pinene (mg/g)', ''),
                        'Gamma-Terpinene (mg/g)': row_dict.get('Gamma-Terpinene (mg/g)', ''),
                        # Generic column placeholders for any additional Excel columns
                        'AL': row_dict.get('AL', ''),
                        'AM': row_dict.get('AM', ''),
                        'AN': row_dict.get('AN', ''),
                        'AO': row_dict.get('AO', ''),
                        'AP': row_dict.get('AP', ''),
                        'AQ': row_dict.get('AQ', ''),
                        'AR': row_dict.get('AR', ''),
                        'AS': row_dict.get('AS', ''),
                        'AT': row_dict.get('AT', ''),
                        'AU': row_dict.get('AU', ''),
                        'AV': row_dict.get('AV', ''),
                        'AW': row_dict.get('AW', ''),
                        'AX': row_dict.get('AX', ''),
                        'AY': row_dict.get('AY', ''),
                        'AZ': row_dict.get('AZ', ''),
                        'BA': row_dict.get('BA', ''),
                        'BB': row_dict.get('BB', ''),
                        'BC': row_dict.get('BC', ''),
                        'BD': row_dict.get('BD', ''),
                        'BE': row_dict.get('BE', ''),
                        'BF': row_dict.get('BF', ''),
                        'BG': row_dict.get('BG', ''),
                        'BH': row_dict.get('BH', ''),
                        'BI': row_dict.get('BI', ''),
                        'BJ': row_dict.get('BJ', ''),
                        'BK': row_dict.get('BK', ''),
                        'BL': row_dict.get('BL', ''),
                        'BM': row_dict.get('BM', ''),
                        'BN': row_dict.get('BN', ''),
                        'BO': row_dict.get('BO', ''),
                        'BP': row_dict.get('BP', ''),
                        'BQ': row_dict.get('BQ', ''),
                        'BR': row_dict.get('BR', ''),
                        'BS': row_dict.get('BS', ''),
                        'BT': row_dict.get('BT', ''),
                        'BU': row_dict.get('BU', ''),
                        'BV': row_dict.get('BV', ''),
                        'BW': row_dict.get('BW', ''),
                        'BX': row_dict.get('BX', ''),
                        'BY': row_dict.get('BY', ''),
                        'BZ': row_dict.get('BZ', ''),
                        'CA': row_dict.get('CA', ''),
                        'CB': row_dict.get('CB', ''),
                        'CC': row_dict.get('CC', ''),
                        'CD': row_dict.get('CD', ''),
                        'CE': row_dict.get('CE', ''),
                        'CF': row_dict.get('CF', ''),
                        'CG': row_dict.get('CG', ''),
                        'CH': row_dict.get('CH', ''),
                        'CI': row_dict.get('CI', ''),
                        'CJ': row_dict.get('CJ', ''),
                        'CK': row_dict.get('CK', ''),
                        'CL': row_dict.get('CL', ''),
                        'CM': row_dict.get('CM', ''),
                        'CN': row_dict.get('CN', ''),
                        'CO': row_dict.get('CO', ''),
                        'CP': row_dict.get('CP', ''),
                        'CQ': row_dict.get('CQ', ''),
                        'CR': row_dict.get('CR', ''),
                        'CS': row_dict.get('CS', ''),
                        'CT': row_dict.get('CT', ''),
                        'CU': row_dict.get('CU', ''),
                        'CV': row_dict.get('CV', ''),
                        'CW': row_dict.get('CW', ''),
                        'CX': row_dict.get('CX', ''),
                        'CY': row_dict.get('CY', ''),
                        'CZ': row_dict.get('CZ', '')
                    }
                    
                    # CRITICAL FIX: Include ALL remaining Excel columns that aren't already in product_data
                    # This ensures no data from Excel is lost - store EVERYTHING from Excel
                    for col_name, col_value in row_dict.items():
                        if col_name not in product_data:
                            # Include ALL values from Excel, even if empty (they might be needed)
                            if col_value is not None:
                                # Convert to string and clean, but keep the value
                                clean_value = str(col_value).strip() if isinstance(col_value, str) else col_value
                                # Don't skip empty strings - they might be meaningful
                                product_data[col_name] = clean_value
                            # If None, skip it (but empty strings are OK)
                    
                    # Skip rows without product name - check multiple possible column names
                    product_name = (product_data.get('ProductName') or 
                                  product_data.get('Product Name*') or 
                                  product_data.get('Product Name') or 
                                  product_data.get('product_name') or 
                                  '')
                    
                    # Enhanced validation: Skip blank or invalid entries
                    if not product_name or str(product_name).strip() == '' or str(product_name).lower() in ['nan', 'none', 'null', '']:
                        logger.warning(f"Row {index + 1}: Skipping blank/invalid product name: '{product_name}'")
                        continue
                    
                    # Skip rows with only whitespace (allow 1 character minimum)
                    if str(product_name).strip() == '' or len(str(product_name).strip()) < 1:
                        logger.warning(f"Row {index + 1}: Skipping product name too short or only whitespace: '{product_name}'")
                        continue
                    
                    # Update the product data with the found name
                    product_data['Product Name*'] = str(product_name).strip()
                    
                    # CRITICAL FIX: Apply defaults BEFORE validation to prevent products from being skipped
                    # This ensures products are added even if vendor/product_type are missing
                    vendor_raw = product_data.get('Vendor/Supplier*', product_data.get('Vendor', ''))
                    vendor = self._ensure_crucial_value(vendor_raw, 'Unknown Vendor', 'Vendor')
                    product_data['Vendor/Supplier*'] = vendor
                    product_data['Vendor'] = vendor
                    
                    product_type_raw = product_data.get('Product Type*', '')
                    product_type = self._ensure_crucial_value(product_type_raw, 'Unknown', 'Product Type')
                    product_data['Product Type*'] = product_type
                    
                    # Validation removed - defaults are always applied above, so products will never be skipped for missing vendor/product_type
                    
                    # Skip duplicate entries within the same upload (same name + vendor + type combination)
                    duplicate_key = f"{product_name}|{vendor}|{product_type}"
                    if duplicate_key in self._current_upload_products:
                        skipped_duplicates += 1
                        logger.warning(f"Row {index + 1}: Skipping duplicate product '{product_name}' from same vendor '{vendor}' and type '{product_type}'")
                        continue
                    
                    # Track this product to prevent duplicates within the same upload
                    self._current_upload_products.add(duplicate_key)
                    
                    # CRITICAL FIX: Preserve existing database lineage if Excel lineage is empty
                    # Check if this product already exists in database and has lineage
                    preserved_db_lineage = None
                    excel_lineage = product_data.get('Lineage', '').strip() if product_data.get('Lineage') else ''
                    
                    # Only check database if Excel lineage is empty - this is the key preservation point
                    if not excel_lineage or excel_lineage in ['', 'nan', 'none', 'null', 'None', 'NaN']:
                        conn_check = self._get_connection()
                        cursor_check = conn_check.cursor()
                        
                        # Try multiple lookup strategies to find existing product
                        normalized_name = self._normalize_product_name(product_name)
                        vendor = product_data.get('Vendor/Supplier*', '').strip() if product_data.get('Vendor/Supplier*') else ''
                        product_type = product_data.get('Product Type*', '').strip() if product_data.get('Product Type*') else ''
                        
                        # Strategy 1: Exact normalized name + vendor + product type match
                        cursor_check.execute('''
                            SELECT "Lineage" FROM products 
                            WHERE normalized_name = ? AND TRIM("Vendor/Supplier*") = ? AND TRIM("Product Type*") = ?
                            LIMIT 1
                        ''', (normalized_name, vendor, product_type))
                        existing_lineage_result = cursor_check.fetchone()
                        
                        # Strategy 2: If no match, try by product name directly (case-insensitive) + vendor + product type
                        if not existing_lineage_result or not existing_lineage_result[0]:
                            cursor_check.execute('''
                                SELECT "Lineage" FROM products 
                                WHERE TRIM(LOWER("Product Name*")) = TRIM(LOWER(?)) 
                                  AND TRIM("Vendor/Supplier*") = ?
                                  AND TRIM("Product Type*") = ?
                                LIMIT 1
                            ''', (product_name, vendor, product_type))
                            existing_lineage_result = cursor_check.fetchone()
                        
                        # Strategy 3: If still no match, try without vendor requirement but with product type
                        if not existing_lineage_result or not existing_lineage_result[0]:
                            cursor_check.execute('''
                                SELECT "Lineage" FROM products 
                                WHERE normalized_name = ? AND TRIM("Product Type*") = ?
                                ORDER BY updated_at DESC
                                LIMIT 1
                            ''', (normalized_name, product_type))
                            existing_lineage_result = cursor_check.fetchone()
                        
                        if existing_lineage_result and existing_lineage_result[0]:
                            db_lineage = str(existing_lineage_result[0]).strip()
                            if db_lineage and db_lineage not in ['', 'nan', 'none', 'null', 'None', 'NaN']:
                                preserved_db_lineage = db_lineage
                                logger.info(f"✅ LINEAGE PRESERVATION: Found existing database lineage '{db_lineage}' for product '{product_name}' - will preserve (Excel had empty lineage)")
                        else:
                            logger.debug(f"⚠️ No existing lineage found in database for product '{product_name}' (Excel also has empty lineage)")
                        
                        cursor_check.close()
                    
                    # Comprehensive smart normalization before storing in database
                    try:
                        from src.core.data.smart_excel_normalizer import smart_normalizer
                        product_data = smart_normalizer.normalize_product_data(product_data)
                        logger.info(f"Smart normalized product: {product_name}")
                    except Exception as e:
                        logger.warning(f"Failed to smart normalize {product_name}: {e}")
                        # Fallback to basic weight normalization
                        try:
                            from src.core.data.weight_normalizer import weight_normalizer
                            product_data = weight_normalizer.normalize_product_data(product_data)
                            logger.info(f"Fallback weight normalized product: {product_name}")
                        except Exception as e2:
                            logger.warning(f"Fallback weight normalization also failed for {product_name}: {e2}")
                    
                    # CRITICAL: Restore preserved database lineage AFTER normalization (normalization might have cleared it)
                    if preserved_db_lineage:
                        final_excel_lineage = product_data.get('Lineage', '').strip() if product_data.get('Lineage') else ''
                        if not final_excel_lineage or final_excel_lineage in ['', 'nan', 'none', 'null', 'None', 'NaN']:
                            product_data['Lineage'] = preserved_db_lineage
                            logger.info(f"✅ RESTORED preserved database lineage '{preserved_db_lineage}' for product '{product_name}' after normalization")
                    
                    # Store the product in database
                    # Get the count before to determine if it's new or updated
                    conn = self._get_connection()
                    cursor_temp = conn.cursor()
                    cursor_temp.execute("SELECT COUNT(*) FROM products")
                    count_before = cursor_temp.fetchone()[0]
                    cursor_temp.close()
                    
                    # Log before attempting to add - show vendor source
                    vendor_in_data = product_data.get('Vendor/Supplier*', '') or product_data.get('Vendor', '') or product_data.get('Vendor/Supplier', '')
                    logger.info(f"🔍 Row {index + 1}: Attempting to add product '{product_name}'")
                    logger.info(f"   Vendor in product_data: '{vendor_in_data}' -> Final vendor: '{vendor}'")
                    logger.info(f"   Type: {product_type}, Weight: {product_data.get('Weight*', 'N/A')}")
                    if not vendor_in_data or vendor_in_data in ['', 'Unknown Vendor', 'nan', 'none', 'null']:
                        logger.warning(f"⚠️ VENDOR MISSING: Product '{product_name}' has no vendor in Excel data!")
                        logger.warning(f"   Available vendor columns in row_dict: {[k for k in row_dict.keys() if 'vendor' in k.lower() or 'supplier' in k.lower()]}")
                    
                    try:
                        product_id = self.add_or_update_product(product_data)
                    
                        if product_id:
                            cursor_temp = conn.cursor()
                            cursor_temp.execute("SELECT COUNT(*) FROM products")
                            count_after = cursor_temp.fetchone()[0]
                            cursor_temp.close()
                            
                            if count_after > count_before:
                                stored_count += 1
                                logger.info(f"✅ Row {index + 1}: STORED NEW product '{product_name}' (ID: {product_id})")
                            else:
                                updated_count += 1
                                logger.info(f"🔄 Row {index + 1}: UPDATED existing product '{product_name}' (ID: {product_id})")
                        elif product_id is None:
                            # Product was rejected (validation failed or duplicate)
                            skipped_duplicates += 1
                            logger.warning(f"⚠️ Row {index + 1}: Product '{product_name}' was rejected (returned None) - check validation logs above")
                            continue
                        else:
                            error_count += 1
                            error_msg = f"Row {index + 1}: Failed to store product '{product_name}' (product_id={product_id})"
                            errors.append(error_msg)
                            logger.error(f"❌ {error_msg}")
                    except Exception as add_error:
                        error_count += 1
                        error_msg = f"Row {index + 1}: Exception adding product '{product_name}': {str(add_error)}"
                        errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        continue
                        
                except Exception as row_error:
                    error_count += 1
                    error_msg = f"Row {index + 1}: {str(row_error)}"
                    errors.append(error_msg)
                    logger.error(f"❌ ERROR processing row {index + 1} for product '{product_name}': {row_error}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Don't continue - try to add the product anyway with minimal data
                    try:
                        # Try to add with just the essentials
                        minimal_product_data = {
                            'Product Name*': product_name,
                            'Vendor/Supplier*': vendor if 'vendor' in locals() else 'Unknown Vendor',
                            'Product Type*': product_type if 'product_type' in locals() else 'Unknown',
                            'Weight*': product_data.get('Weight*', '1'),
                            'Units': product_data.get('Units', 'g'),
                            'Price': product_data.get('Price', '0.00')
                        }
                        fallback_id = self.add_or_update_product(minimal_product_data)
                        if fallback_id:
                            stored_count += 1
                            logger.info(f"✅ FALLBACK: Added product '{product_name}' with minimal data after error")
                    except Exception as fallback_error:
                        logger.error(f"❌ FALLBACK also failed for '{product_name}': {fallback_error}")
                    continue
            
            # Calculate excluded counts
            excluded_count = len(df) - len(filtered_df)
            blank_entries_skipped = len(df) - len(filtered_df) - excluded_count
            
            result = {
                'stored': stored_count,
                'updated': updated_count,
                'skipped_duplicates': skipped_duplicates,
                'errors': error_count,
                'excluded_json_matches': excluded_count,
                'blank_entries_skipped': blank_entries_skipped,
                'total_rows': len(df),
                'filtered_rows': len(filtered_df),
                'source_file': source_file,
                'message': f'Successfully processed {stored_count} products (new data replaces existing), skipped {skipped_duplicates} duplicates, {error_count} errors, excluded {excluded_count} JSON matched tags, skipped {blank_entries_skipped} blank entries'
            }
            
            if errors:
                result['error_details'] = errors[:10]  # Limit error details to first 10
            
            print(f"🔍 DEBUG: Database storage completed - Stored: {stored_count}, Updated: {updated_count}, Errors: {error_count}")
            logger.info(f"Excel data storage completed: {result['message']}")
            
            # Log rejection summary to provide insight into data quality issues
            self.log_rejection_summary()
            
            return result
            
        except sqlite3.OperationalError as op_error:
            error_text = str(op_error).lower()
            if _retry_on_schema_error and 'no such column' in error_text:
                self._attempt_schema_repair(op_error)
                return self.store_excel_data(df, source_file, _retry_on_schema_error=False)
            
            logger.error(f"SQLite operational error while storing Excel data: {op_error}")
            return {'stored': 0, 'updated': 0, 'errors': 1, 'excluded_json_matches': 0, 'message': f'Storage failed: {str(op_error)}'}
            
        except Exception as e:
            logger.error(f"Error storing Excel data: {e}")
            return {'stored': 0, 'updated': 0, 'errors': 1, 'excluded_json_matches': 0, 'message': f'Storage failed: {str(e)}'}
    
    def _attempt_schema_repair(self, op_error: sqlite3.OperationalError) -> None:
        """Attempt to repair the products table schema when a missing-column error is detected."""
        try:
            error_text = str(op_error)
            missing_column = None
            match = re.search(r'no such column: ([^ ]+)', error_text.lower())
            if match:
                missing_column = match.group(1)
            
            if missing_column:
                logger.error(f"⚠️ Missing column detected in products table: '{missing_column}'. Attempting automatic repair...")
            else:
                logger.error("⚠️ Database schema mismatch detected. Attempting automatic repair...")
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            self._add_missing_columns_safe(cursor, conn)
            self._ensure_essential_columns_exist(cursor, conn)
            conn.commit()
            
            logger.info("✅ Schema repair completed successfully.")
            
        except Exception as repair_error:
            logger.error(f"❌ Schema repair failed: {repair_error}")
            raise
    
    def cleanup_duplicate_products(self) -> Dict[str, Any]:
        """
        Clean up duplicate products in the database, keeping only the most recent entry.
        Duplicates are identified by matching: normalized_name + Vendor/Supplier* + Product Brand
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            logger.info("Starting duplicate product cleanup...")
            
            # Find duplicates by grouping on normalized_name, vendor, and brand
            cursor.execute('''
                SELECT normalized_name, "Vendor/Supplier*", "Product Brand", COUNT(*) as count
                FROM products
                GROUP BY normalized_name, "Vendor/Supplier*", "Product Brand"
                HAVING count > 1
            ''')
            
            duplicate_groups = cursor.fetchall()
            total_duplicates = len(duplicate_groups)
            deleted_count = 0
            
            logger.info(f"Found {total_duplicates} duplicate product groups")
            
            for norm_name, vendor, brand, count in duplicate_groups:
                # Get all entries for this duplicate group, ordered by most recent first
                cursor.execute('''
                    SELECT id, "Product Name*", updated_at
                    FROM products
                    WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Brand" = ?
                    ORDER BY updated_at DESC
                ''', (norm_name, vendor, brand))
                
                entries = cursor.fetchall()
                
                if len(entries) > 1:
                    # Keep the first (most recent), delete the rest
                    keep_id = entries[0][0]
                    keep_name = entries[0][1]
                    
                    ids_to_delete = [entry[0] for entry in entries[1:]]
                    
                    logger.info(f"Keeping most recent '{keep_name}' (ID: {keep_id}), deleting {len(ids_to_delete)} older duplicates")
                    
                    # Delete older duplicates
                    cursor.executemany('DELETE FROM products WHERE id = ?', [(id,) for id in ids_to_delete])
                    deleted_count += len(ids_to_delete)
            
            conn.commit()
            
            # Get final product count
            cursor.execute("SELECT COUNT(*) FROM products")
            final_count = cursor.fetchone()[0]
            
            logger.info(f"Duplicate cleanup completed: Deleted {deleted_count} duplicate entries, {final_count} products remaining")
            
            return {
                'success': True,
                'duplicate_groups': total_duplicates,
                'deleted_count': deleted_count,
                'final_product_count': final_count,
                'message': f'Deleted {deleted_count} duplicate products from {total_duplicates} duplicate groups. {final_count} products remaining.'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate products: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Cleanup failed: {str(e)}'
            }
    
    def cleanup_blank_entries(self) -> Dict[str, Any]:
        """
        Clean up existing blank entries in the database.
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Find and count blank entries
            cursor.execute('''
                SELECT COUNT(*) FROM products 
                WHERE "Product Name*" IS NULL 
                   OR "Product Name*" = '' 
                   OR "Product Name*" = 'nan' 
                   OR "Product Name*" = 'None' 
                   OR "Product Name*" = 'null'
                   OR LENGTH(TRIM("Product Name*")) < 2
            ''')
            
            blank_count = cursor.fetchone()[0]
            
            if blank_count == 0:
                return {
                    'cleaned': 0,
                    'message': 'No blank entries found in database'
                }
            
            # Delete blank entries
            cursor.execute('''
                DELETE FROM products 
                WHERE "Product Name*" IS NULL 
                   OR "Product Name*" = '' 
                   OR "Product Name*" = 'nan' 
                   OR "Product Name*" = 'None' 
                   OR "Product Name*" = 'null'
                   OR LENGTH(TRIM("Product Name*")) < 2
            ''')
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} blank entries from database")
            
            return {
                'cleaned': deleted_count,
                'message': f'Successfully cleaned up {deleted_count} blank entries from database'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up blank entries: {e}")
            return {
                'cleaned': 0,
                'error': str(e),
                'message': f'Failed to clean up blank entries: {str(e)}'
            }

    # ============================================================
    # FAST TAG LIST FOR AVAILABLE-TAGS ENDPOINT (MIRROR)
    # ============================================================
    def get_available_tags_fast(self) -> List[Dict[str, Any]]:
        """
        Return a lightweight list of tags built directly from the products table.

        This mirrors the shape of ExcelProcessor.get_available_tags() closely
        enough for the frontend available-tags UI, but uses a single SQL query
        instead of walking the Excel DataFrame.
        """
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()

            query_start = time.time()
            cursor.execute(
                '''
                SELECT
                    "Product Name*"            AS product_name,
                    "Product Type*"            AS product_type,
                    "Vendor/Supplier*"         AS vendor,
                    "Product Brand"            AS brand,
                    COALESCE("Lineage", '')    AS lineage,
                    "Quantity*"                AS quantity,
                    "DOH"                      AS doh,
                    "Weight*"                  AS weight,
                    "Units"                    AS units,
                    "Price"                    AS price,
                    "Product Strain"           AS product_strain,
                    "Ratio_or_THC_CBD"         AS ratio_or_thc_cbd,
                    "THC test result"          AS thc_test_result,
                    "CBD test result"          AS cbd_test_result,
                    "Test result unit (% or mg)" AS test_unit
                FROM products
                WHERE ("Is Archived? (yes/no)" IS NULL OR "Is Archived? (yes/no)" != 'yes')
                '''
            )
            rows = cursor.fetchall()
            elapsed_ms = (time.time() - query_start) * 1000
            logger.info(f"[PERF] ProductDatabase.get_available_tags_fast query returned {len(rows)} rows in {elapsed_ms:.1f}ms")

            tags: List[Dict[str, Any]] = []
            for (
                product_name,
                product_type,
                vendor,
                brand,
                lineage,
                quantity,
                doh,
                weight,
                units,
                price,
                product_strain,
                ratio_or_thc_cbd,
                thc_test_result,
                cbd_test_result,
                test_unit,
            ) in rows:
                if not product_name:
                    continue

                tag: Dict[str, Any] = {
                    'Product Name*': product_name,
                    'ProductName': product_name,
                    'Product Type*': product_type or '',
                    'Type': product_type or '',
                    'Vendor/Supplier*': vendor or '',
                    'Vendor': vendor or '',
                    'Product Brand': brand or '',
                    'Brand': brand or '',
                    'Lineage': (lineage or '').strip().upper() or 'MIXED',
                    'canonical_lineage': (lineage or '').strip().upper() or 'MIXED',
                    'currentLineage': (lineage or '').strip().upper() or 'MIXED',
                    'Quantity*': quantity,
                    'Quantity': quantity,
                    'DOH': doh or '',
                    'Weight*': weight or '',
                    'Weight': weight or '',
                    'Units': units or '',
                    'Price': price,
                    'Product Strain': product_strain or '',
                    'Ratio_or_THC_CBD': ratio_or_thc_cbd or '',
                    'THC test result': thc_test_result or '',
                    'CBD test result': cbd_test_result or '',
                    'Test result unit (% or mg)': test_unit or '',
                    'Source': 'DB Fast',
                }
                tags.append(tag)

            return tags
        except Exception as e:
            logger.error(f"Error in get_available_tags_fast: {e}")
            return []
    
    def _filter_json_matched_tags(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out JSON matched tags from the DataFrame.
        
        Args:
            df: DataFrame to filter
            
        Returns:
            Filtered DataFrame with JSON matched tags removed
        """
        try:
            if df is None or df.empty:
                return df
            
            # Create a copy to avoid modifying the original
            filtered_df = df.copy()
            
            # Define JSON match indicators
            json_match_indicators = [
                'Source', 'ai_match_score', 'ai_confidence', 'ai_match_type',
                'json_match_score', 'json_confidence', 'json_match_type',
                'match_score', 'confidence', 'match_type'
            ]
            
            # Create a mask for JSON matched tags
            json_match_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            
            for col in json_match_indicators:
                if col in filtered_df.columns:
                    if col == 'Source':
                        # CRITICAL FIX: Only filter products EXPLICITLY marked as JSON matched
                        # Don't filter Excel uploads - they should always be stored
                        # Look for JSON match indicators BUT exclude Excel/Upload sources
                        json_match_indicators = filtered_df[col].astype(str).str.contains(
                            'JSON Match|AI Match|Generated Tag', 
                            case=False, 
                            na=False
                        )
                        # Exclude Excel/Upload sources from filtering - these should ALWAYS be stored
                        excel_sources = filtered_df[col].astype(str).str.contains(
                            'Excel|Upload|Import', 
                            case=False, 
                            na=False
                        )
                        # Only mark as JSON match if it's JSON match AND not Excel
                        json_match_mask |= (json_match_indicators & ~excel_sources)
                    else:
                        # Look for non-null values in other JSON match columns
                        json_match_mask |= filtered_df[col].notna()
            
            # Apply the filter
            original_count = len(filtered_df)
            filtered_df = filtered_df[~json_match_mask]
            filtered_count = len(filtered_df)
            excluded_count = original_count - filtered_count
            
            if excluded_count > 0:
                logger.info(f"Filtered out {excluded_count} JSON matched tags, {filtered_count} rows remaining for database storage")
                
                # Log some examples of excluded tags for debugging
                excluded_examples = df[json_match_mask].head(3)
                for idx, row in excluded_examples.iterrows():
                    source_info = row.get('Source', 'Unknown') if 'Source' in row else 'No Source'
                    logger.debug(f"Excluded JSON matched tag: {row.get('Product Name*', row.get('ProductName', 'Unknown'))} (Source: {source_info})")
            
            return filtered_df
            
        except Exception as e:
            logger.error(f"Error filtering JSON matched tags: {e}")
            # Return original DataFrame if filtering fails
            return df
    
    @timed_operation("get_strain_info")
    def get_strain_info(self, strain_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific strain (with caching)."""
        try:
            self.init_database()  # Ensure DB is initialized
            normalized_name = self._normalize_strain_name(strain_name)
            cache_key = self._get_cache_key("strain_info", normalized_name)
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Known sativa hybrid strains - override database lineage if it's just "HYBRID"
            KNOWN_SATIVA_HYBRIDS = {
                'blue dream', 'blue dream haze', 'blueberry dream', 'dream', 'dream star',
                'sour diesel', 'sour d', 'green crack', 'green crack haze',
                'jack herer', 'jack', 'super silver haze', 'silver haze',
                'durban poison', 'durban', 'trainwreck', 'train wreck',
                'amnesia haze', 'amnesia', 'strawberry cough', 'strawberry',
                'white widow', 'white', 'ak-47', 'ak47', 'ak 47',
                'purple haze', 'haze', 'lemon haze', 'lemon',
                'pineapple express', 'pineapple', 'maui wowie', 'maui',
                'chocolope', 'chocolate', 'tangie', 'tangerine dream',
                'cannatonic', 'harlequin', 'acdc', 'ac/dc', 'pennywise'
            }
            
            # Check if this is a known sativa hybrid
            is_known_sativa_hybrid = normalized_name in KNOWN_SATIVA_HYBRIDS or any(
                known in normalized_name for known in KNOWN_SATIVA_HYBRIDS
            )
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, first_seen_date, last_seen_date
                FROM strains 
                WHERE normalized_name = ?
            ''', (normalized_name,))
            result = cursor.fetchone()
            if result:
                strain_id = result[0]
                canonical_lineage = result[2]
                mode_lineage = self.get_mode_lineage(strain_id)
                display_lineage = mode_lineage if mode_lineage else canonical_lineage
                # CRITICAL FIX: Override lineage for known sativa hybrids if database has just "HYBRID"
                if is_known_sativa_hybrid and display_lineage and str(display_lineage).strip().upper() == 'HYBRID':
                    logger.info(f"🌿 SATIVA HYBRID OVERRIDE: '{strain_name}' - Overriding 'HYBRID' to 'HYBRID/SATIVA'")
                    display_lineage = 'HYBRID/SATIVA'
                    if not canonical_lineage or str(canonical_lineage).strip().upper() == 'HYBRID':
                        canonical_lineage = 'HYBRID/SATIVA'
                strain_info = {
                    'id': result[0],
                    'strain_name': result[1],
                    'canonical_lineage': canonical_lineage,
                    'total_occurrences': result[3],
                    'lineage_confidence': result[4],
                    'first_seen_date': result[5],
                    'last_seen_date': result[6],
                    'display_lineage': display_lineage
                }
                self._set_cache(cache_key, strain_info, ttl=300)
                return strain_info
            elif is_known_sativa_hybrid:
                logger.info(f"🌿 SATIVA HYBRID DEFAULT: '{strain_name}' - Not in database, using default 'HYBRID/SATIVA'")
                return {
                    'id': None,
                    'strain_name': strain_name,
                    'canonical_lineage': 'HYBRID/SATIVA',
                    'total_occurrences': 0,
                    'lineage_confidence': 0.0,
                    'first_seen_date': '',
                    'last_seen_date': '',
                    'display_lineage': 'HYBRID/SATIVA'
                }
            return None
        except Exception as e:
            logger.error(f"Error getting strain info for '{strain_name}': {e}")
            return None

    def get_strain_info_batch(self, strain_names: list) -> Dict[str, Dict[str, Any]]:
        """Get information about multiple strains in a single batch query (PERFORMANCE OPTIMIZATION).

        Returns a dict mapping normalized strain name -> strain info dict.
        This eliminates N+1 queries when processing many tags.
        """
        if not strain_names:
            return {}

        try:
            self.init_database()

            # Normalize all strain names and build lookup
            normalized_to_original = {}
            unique_normalized = set()
            for name in strain_names:
                if name:
                    normalized = self._normalize_strain_name(name)
                    normalized_to_original[normalized] = name
                    unique_normalized.add(normalized)

            if not unique_normalized:
                return {}

            # Known sativa hybrid strains (same as get_strain_info)
            KNOWN_SATIVA_HYBRIDS = {
                'blue dream', 'blue dream haze', 'blueberry dream', 'dream', 'dream star',
                'sour diesel', 'sour d', 'green crack', 'green crack haze',
                'jack herer', 'jack', 'super silver haze', 'silver haze',
                'durban poison', 'durban', 'trainwreck', 'train wreck',
                'amnesia haze', 'amnesia', 'strawberry cough', 'strawberry',
                'white widow', 'white', 'ak-47', 'ak47', 'ak 47',
                'purple haze', 'haze', 'lemon haze', 'lemon',
                'pineapple express', 'pineapple', 'maui wowie', 'maui',
                'chocolope', 'chocolate', 'tangie', 'tangerine dream',
                'cannatonic', 'harlequin', 'acdc', 'ac/dc', 'pennywise'
            }

            conn = self._get_connection()
            cursor = conn.cursor()

            # Batch query all strains at once
            result_map = {}
            normalized_list = list(unique_normalized)
            chunk_size = 400

            for start in range(0, len(normalized_list), chunk_size):
                chunk = normalized_list[start:start + chunk_size]
                placeholders = ','.join(['?' for _ in chunk])
                cursor.execute(f'''
                    SELECT id, strain_name, normalized_name, canonical_lineage, sovereign_lineage,
                           total_occurrences, lineage_confidence, first_seen_date, last_seen_date
                    FROM strains
                    WHERE normalized_name IN ({placeholders})
                ''', chunk)

                for row in cursor.fetchall():
                    strain_id = row[0]
                    strain_name = row[1]
                    normalized_name = row[2]
                    canonical_lineage = row[3]
                    sovereign_lineage = row[4]

                    # Use canonical_lineage directly (skip mode_lineage query for performance)
                    # The canonical_lineage should already be set to mode via update_all_canonical_lineages_to_mode()
                    display_lineage = sovereign_lineage or canonical_lineage

                    # Check if known sativa hybrid
                    is_known_sativa_hybrid = normalized_name in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized_name for known in KNOWN_SATIVA_HYBRIDS
                    )

                    # Override for known sativa hybrids
                    if is_known_sativa_hybrid and display_lineage and str(display_lineage).strip().upper() == 'HYBRID':
                        display_lineage = 'HYBRID/SATIVA'
                        if not canonical_lineage or str(canonical_lineage).strip().upper() == 'HYBRID':
                            canonical_lineage = 'HYBRID/SATIVA'

                    result_map[normalized_name] = {
                        'id': strain_id,
                        'strain_name': strain_name,
                        'canonical_lineage': canonical_lineage,
                        'sovereign_lineage': sovereign_lineage,
                        'total_occurrences': row[5],
                        'lineage_confidence': row[6],
                        'first_seen_date': row[7],
                        'last_seen_date': row[8],
                        'display_lineage': display_lineage
                    }

            # Add default entries for known sativa hybrids not found in database
            for normalized in unique_normalized:
                if normalized not in result_map:
                    is_known_sativa_hybrid = normalized in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized for known in KNOWN_SATIVA_HYBRIDS
                    )
                    if is_known_sativa_hybrid:
                        result_map[normalized] = {
                            'id': None,
                            'strain_name': normalized_to_original.get(normalized, normalized),
                            'canonical_lineage': 'HYBRID/SATIVA',
                            'sovereign_lineage': None,
                            'total_occurrences': 0,
                            'lineage_confidence': 0.0,
                            'first_seen_date': '',
                            'last_seen_date': '',
                            'display_lineage': 'HYBRID/SATIVA'
                        }

            logger.debug(f"Batch strain lookup: {len(strain_names)} requested, {len(result_map)} found")
            return result_map

        except Exception as e:
            logger.error(f"Error in batch strain lookup: {e}")
            return {}

    @timed_operation("get_product_info")
    def get_product_info(self, product_name: str, vendor: str = None, brand: str = None) -> Optional[Dict[str, Any]]:
        """Get information about a specific product (with caching)."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            normalized_name = self._normalize_product_name(product_name)
            cache_key = self._get_cache_key("product_info", normalized_name, vendor, brand)
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            has_strain_id = self._products_has_column('strain_id')
            lineage_select = 's.strain_name, s.canonical_lineage' if has_strain_id else 'p."Product Strain" as strain_name, p."Lineage" as canonical_lineage'
            join_clause = 'LEFT JOIN strains s ON p.strain_id = s.id' if has_strain_id else ''
            
            if vendor and brand:
                cursor.execute(f'''
                    SELECT p.id, p."Product Name*", p.normalized_name, p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                           {lineage_select}, 0 as total_occurrences, '' as first_seen_date, '' as last_seen_date,
                           p."Description", p."Weight*", p."Units", p."Price"
                    FROM products p
                    {join_clause}
                    WHERE p.normalized_name = ? AND p."Vendor/Supplier*" = ? AND p."Product Brand" = ?
                    ORDER BY p."Vendor/Supplier*" IS NOT NULL DESC, p.rowid DESC
                ''', (normalized_name, vendor, brand))
            else:
                cursor.execute(f'''
                    SELECT p.id, p."Product Name*", p.normalized_name, p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                           {lineage_select}, 0 as total_occurrences, '' as first_seen_date, '' as last_seen_date,
                           p."Description", p."Weight*", p."Units", p."Price"
                    FROM products p
                    {join_clause}
                    WHERE p.normalized_name = ?
                    ORDER BY p."Vendor/Supplier*" IS NOT NULL DESC, p.rowid DESC
                ''', (normalized_name,))
            
            result = cursor.fetchone()
            if result:
                product_info = {
                    'id': result[0],
                    'product_name': result[1],
                    'normalized_name': result[2],
                    'product_type': result[3],
                    'vendor': result[4],
                    'brand': result[5],
                    'lineage': result[6],
                    'strain_name': result[7],
                    'canonical_lineage': result[8],
                    'total_occurrences': result[9],
                    'first_seen_date': result[10],
                    'last_seen_date': result[11],
                    'description': result[12],
                    'weight': result[13],
                    'units': result[14],
                    'price': result[15]
                }
                
                # Cache the result for 5 minutes
                self._set_cache(cache_key, product_info, ttl=300)
                return product_info
            return None
            
        except Exception as e:
            logger.error(f"Error getting product info for '{product_name}': {e}")
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
    
    @timed_operation("get_strain_statistics")
    def get_strain_statistics(self) -> Dict[str, Any]:
        """Get statistics about strains in the database, excluding MIXED, CBD Blend, and Paraphernalia from stats."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Total strains
            cursor.execute('SELECT COUNT(*) FROM strains')
            total_strains = cursor.fetchone()[0]
            
            # Strains by lineage (exclude unwanted)
            cursor.execute('''
                SELECT canonical_lineage, COUNT(*) 
                FROM strains 
                WHERE canonical_lineage IS NOT NULL 
                GROUP BY canonical_lineage
            ''')
            lineage_counts = dict(cursor.fetchall())
            # Exclude unwanted
            exclude_keys = {k.lower() for k in ['MIXED', 'CBD Blend', 'Paraphernalia']}
            lineage_counts = {k: v for k, v in lineage_counts.items() if k and k.strip().lower() not in exclude_keys}
            
            # Most common strains (exclude unwanted)
            cursor.execute('''
                SELECT strain_name, total_occurrences, canonical_lineage
                FROM strains 
                ORDER BY total_occurrences DESC 
                LIMIT 50
            ''')
            top_strains_raw = cursor.fetchall()
            top_strains = [
                {'name': name, 'occurrences': count}
                for name, count, lineage in top_strains_raw
                if lineage and lineage.strip().lower() not in exclude_keys and name and name.strip().lower() not in exclude_keys
            ][:10]
            
            # Total products
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            
            # Vendor statistics - use correct Excel column names
            cursor.execute('''
                SELECT "Vendor/Supplier*", COUNT(*) as count
                FROM products 
                WHERE "Vendor/Supplier*" IS NOT NULL AND "Vendor/Supplier*" != ''
                GROUP BY "Vendor/Supplier*"
                ORDER BY count DESC
                LIMIT 20
            ''')
            vendor_stats = [{'vendor': vendor, 'count': count} for vendor, count in cursor.fetchall()]
            
            # Brand statistics - use correct Excel column names
            cursor.execute('''
                SELECT "Product Brand", COUNT(*) as count
                FROM products 
                WHERE "Product Brand" IS NOT NULL AND "Product Brand" != ''
                GROUP BY "Product Brand"
                ORDER BY count DESC
                LIMIT 20
            ''')
            brand_stats = [{'brand': brand, 'count': count} for brand, count in cursor.fetchall()]
            
            # Product type statistics - use correct Excel column names
            cursor.execute('''
                SELECT "Product Type*", COUNT(*) as count
                FROM products 
                WHERE "Product Type*" IS NOT NULL AND "Product Type*" != ''
                GROUP BY "Product Type*"
                ORDER BY count DESC
                LIMIT 20
            ''')
            product_type_stats = [{'product_type': product_type, 'count': count} for product_type, count in cursor.fetchall()]
            
            # Vendor-Brand combinations - use correct Excel column names
            cursor.execute('''
                SELECT "Vendor/Supplier*", "Product Brand", COUNT(*) as count
                FROM products 
                WHERE "Vendor/Supplier*" IS NOT NULL AND "Vendor/Supplier*" != '' AND "Product Brand" IS NOT NULL AND "Product Brand" != ''
                GROUP BY "Vendor/Supplier*", "Product Brand"
                ORDER BY count DESC
                LIMIT 15
            ''')
            vendor_brand_stats = [{'vendor': vendor, 'brand': brand, 'count': count} for vendor, brand, count in cursor.fetchall()]
            
            return {
                'total_strains': total_strains,
                'total_products': total_products,
                'lineage_distribution': lineage_counts,
                'top_strains': top_strains,
                'vendor_statistics': vendor_stats,
                'brand_statistics': brand_stats,
                'product_type_statistics': product_type_stats,
                'vendor_brand_combinations': vendor_brand_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting strain statistics: {e}")
            return {}
    
    def export_database(self, output_path: str):
        """Export database to Excel file - optimized for large datasets."""
        try:
            self.init_database()  # Ensure DB is initialized

            conn = self._get_connection()
            cursor = conn.cursor()

            # Export strains directly using pandas read_sql_query (fast)
            strains_df = pd.read_sql_query('''
                SELECT strain_name, canonical_lineage, total_occurrences, first_seen_date, last_seen_date
                FROM strains
                ORDER BY total_occurrences DESC
            ''', conn)

            # Get available columns dynamically
            cursor.execute("PRAGMA table_info(products)")
            available_columns = [row[1] for row in cursor.fetchall()]

            # Filter columns to export
            exclude_cols = {'normalized_name', 'Ratio_or_THC_CBD', 'Description_Complexity', 'strain_id'}
            columns_to_export = [col for col in available_columns if col not in exclude_cols]

            # Build SELECT query with proper quoting
            select_columns = ', '.join([f'"{col}"' for col in columns_to_export])

            # Use pandas read_sql_query directly - much faster than row-by-row
            products_df = pd.read_sql_query(f'''
                SELECT {select_columns}
                FROM products
                ORDER BY id
            ''', conn)

            logger.info(f"Exporting {len(products_df)} products and {len(strains_df)} strains")

            # Export to Excel using xlsxwriter (much faster than openpyxl for large files)
            try:
                with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                    strains_df.to_excel(writer, sheet_name='Strains', index=False)
                    products_df.to_excel(writer, sheet_name='Products', index=False)
            except Exception:
                # Fallback to openpyxl if xlsxwriter fails
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    strains_df.to_excel(writer, sheet_name='Strains', index=False)
                    products_df.to_excel(writer, sheet_name='Products', index=False)

            logger.info(f"Database exported to {output_path}")

        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def update_all_descriptions(self) -> Dict[str, Any]:
        """Update ALL Description column values with formula-created values from Product Name*."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products with their Product Name* values
            cursor.execute('''
                SELECT id, "Product Name*" FROM products 
                WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ""
            ''')
            
            products_to_update = cursor.fetchall()
            updated_count = 0
            
            for product_id, product_name in products_to_update:
                # Generate description using the comprehensive processing formula
                new_description = self._process_description(product_name, '')
                
                # Update the Description column
                cursor.execute('''
                    UPDATE products 
                    SET "Description" = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_description, datetime.now().isoformat(), product_id))
                updated_count += 1
            
            conn.commit()
            logger.info(f"Updated {updated_count} product descriptions with formula-created values")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Successfully updated {updated_count} product descriptions with formula-created values'
            }
            
        except Exception as e:
            logger.error(f"Error updating descriptions: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update descriptions: {str(e)}'
            }

    def populate_missing_columns(self) -> Dict[str, Any]:
        """Populate missing columns in existing products with default values."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products that need updating
            cursor.execute('''
                SELECT id, "Product Name*", "Product Type*", "Weight*", "Price* (Tier Name for Bulk)", 
                       "Quantity*", "DOH", "Concentrate Type", "Ratio", "JointRatio", "State"
                FROM products 
                WHERE "DOH Compliant (Yes/No)" IS NULL 
                   OR "Description" IS NULL 
                   OR "Description" = ''
            ''')
            
            products_to_update = cursor.fetchall()
            updated_count = 0
            
            for product in products_to_update:
                product_id, name, product_type, weight, price, quantity, doh, concentrate_type, ratio, joint_ratio, state = product
                
                # Set default values for missing columns
                updates = []
                values = []
                
                # CRITICAL FIX: Always use 'No' as the empty state, never None
                # CRITICAL FIX: Always use 'No' as the empty state, never None or empty string
                if not doh or doh == 'None' or doh is None or str(doh).strip() == '':
                    doh = 'No'
                    updates.append('"DOH" = ?')
                    values.append('No')
                
                if not concentrate_type or concentrate_type == 'None':
                    updates.append('"Concentrate Type" = ?')
                    values.append('')
                
                if not ratio or ratio == 'None':
                    updates.append('"Ratio" = ?')
                    values.append('')
                
                if not joint_ratio or joint_ratio == 'None':
                    # Calculate joint ratio for pre-roll products
                    if product_type and 'pre-roll' in str(product_type).lower():
                        joint_ratio = self._calculate_joint_ratio_from_name(name, product_type, weight)
                    else:
                        joint_ratio = ''
                    updates.append('"JointRatio" = ?')
                    values.append(joint_ratio)
                
                if not state or state == 'None':
                    updates.append('"State" = ?')
                    values.append('active')
                
                # Set other missing columns with defaults (only for columns that exist)
                # Check which columns exist in the database
                cursor.execute("PRAGMA table_info(products)")
                existing_columns = {row[1] for row in cursor.fetchall()}
                
                # Define column mappings with existence checks
                column_mappings = [
                    ('"Description"', self._get_description(name)),
                    ('"Is Sample? (yes/no)"', 'no'),
                    ('"Is MJ product?(yes/no)"', 'yes' if product_type and 'mj' in str(product_type).lower() else 'no'),
                    ('"Discountable? (yes/no)"', 'yes'),
                    ('"Room*"', 'Default'),
                    ('"Batch Number"', ''),
                    ('"Lot Number"', ''),
                    ('"Barcode*"', ''),
                    ('"Medical Only (Yes/No)"', 'No'),
                    ('"Med Price"', ''),
                    ('"Expiration Date(YYYY-MM-DD)"', ''),
                    ('"Is Archived? (yes/no)"', 'no'),
                    ('"THC Per Serving"', ''),
                    ('"Allergens"', ''),
                    ('"Solvent"', ''),
                    ('"Accepted Date"', ''),
                    ('"Internal Product Identifier"', ''),
                    ('"Product Tags (comma separated)"', ''),
                    ('"Image URL"', ''),
                    ('"Ingredients"', ''),
                    ('"CombinedWeight"', ''),
                    ('"Ratio_or_THC_CBD"', ''),
                    ('"Description_Complexity"', ''),
                    ('"Total THC"', ''),
                    ('"THCA"', ''),
                    ('"CBDA"', ''),
                    ('"CBN"', ''),
                    ('"Units"', 'g'),
                    ('"Price"', price or ''),
                    ('"DOH Compliant (Yes/No)"', doh),
                    ('"Joint Ratio"', joint_ratio),
                    ('"Quantity Received*"', quantity or '')
                ]
                
                # Only add columns that exist in the database
                # SECURITY: Validate column names to prevent SQL injection
                for col_name, default_value in column_mappings:
                    clean_col_name = col_name.strip('"')
                    if clean_col_name in existing_columns:
                        # Additional security check: ensure column name doesn't contain SQL injection patterns
                        if any(char in clean_col_name for char in [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']):
                            logger.warning(f"SECURITY: Suspicious column name detected and rejected: {clean_col_name}")
                            continue
                        updates.append(f'{col_name} = ?')
                        values.append(default_value)
                
                if updates:
                    values.append(product_id)
                    update_query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(update_query, values)
                    updated_count += 1
            
            conn.commit()
            logger.info(f"Updated {updated_count} products with missing column data")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Successfully updated {updated_count} products with missing column data'
            }
            
        except Exception as e:
            logger.error(f"Error populating missing columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to populate missing columns: {str(e)}'
            }
    
    def _get_description(self, product_name):
        """Generate description from product name by removing vendor information."""
        if not product_name:
            return ""
        
        name = str(product_name).strip()
        if not name:
            return ""
        
        # Remove everything after " by " or " By " to eliminate vendor information
        if ' by ' in name:
            return name.split(' by ')[0].strip()
        elif ' By ' in name:
            return name.split(' By ')[0].strip()
        
        # If no "by" pattern, return the name as-is
        return name.strip()
    
    def _calculate_joint_ratio_from_name(self, product_name, product_type, weight):
        """Calculate joint ratio for pre-roll products from product name."""
        if not product_name or not product_type or 'pre-roll' not in str(product_type).lower():
            return ''
        
        import re
        product_name_str = str(product_name)
        
        # Look for patterns like "0.5g x 2 Pack", "1g x 28 Pack", etc.
        patterns = [
            r'(\d+(?:\.\d+)?)g\s*x\s*(\d+)\s*pack',  # "0.5g x 2 Pack"
            r'(\d+(?:\.\d+)?)g\s*x\s*(\d+)',         # "0.5g x 2"
            r'(\d+(?:\.\d+)?)g\s*×\s*(\d+)',         # "0.5g × 2" (different x character)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, product_name_str, re.IGNORECASE)
            if match:
                amount = match.group(1)
                count = match.group(2)
                try:
                    count_int = int(count)
                    if count_int == 1:
                        return f"{amount}g"
                    else:
                        return f"{amount}g x {count} Pack"
                except ValueError:
                    continue
        
        # If no pattern found, try to generate from weight
        if weight and str(weight).strip() != '' and str(weight).lower() != 'nan':
            try:
                weight_float = float(weight)
                if weight_float == 1.0:
                    return "1g"
                else:
                    # Format weight similar to price formatting - no decimals unless original has decimals
                    if weight_float.is_integer():
                        formatted_weight = f"{int(weight_float)}g"
                    else:
                        # Round to 2 decimal places and remove trailing zeros
                        formatted_weight = f"{weight_float:.2f}".rstrip("0").rstrip(".") + "g"
                    return formatted_weight
            except (ValueError, TypeError):
                pass
        
        return ''

    def _add_missing_columns_safe(self, cursor, conn):
        """Safely add missing columns to existing tables without losing data."""
        try:
            from datetime import datetime
            # Check if we've already run this migration to avoid repeated attempts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_migration_log'")
            if not cursor.fetchone():
                cursor.execute("CREATE TABLE _migration_log (migration_name TEXT PRIMARY KEY, applied_date TEXT)")
                conn.commit()
            
            # Track whether we've previously logged the v2 migration so we only log once,
            # but we still want to re-run the safety checks in case new columns were added
            cursor.execute("SELECT migration_name FROM _migration_log WHERE migration_name = 'column_migration_v2'")
            migration_logged = cursor.fetchone() is not None
            
            migration_applied_this_session = getattr(self, '_migration_applied', False)
            
            # Check and add missing columns to products table
            cursor.execute("PRAGMA table_info(products)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            missing_columns = []
            
            # Define all expected columns using the actual database schema names
            expected_columns = [
                ('strain_id', 'INTEGER'),
                ('"Product Strain"', 'TEXT'),
                ('"Quantity*"', 'TEXT'),
                ('"DOH"', 'TEXT'),
                ('"Concentrate Type"', 'TEXT'),
                ('"Ratio"', 'TEXT'),
                ('"JointRatio"', 'TEXT'),
                ('"THC test result"', 'TEXT'),
                ('"CBD test result"', 'TEXT'),
                ('"Test result unit (% or mg)"', 'TEXT'),
                ('"State"', 'TEXT'),
                ('"Is Sample? (yes/no)"', 'TEXT'),
                ('"Is MJ product?(yes/no)"', 'TEXT'),
                ('"Discountable? (yes/no)"', 'TEXT'),
                ('"Room*"', 'TEXT'),
                ('"Batch Number"', 'TEXT'),
                ('"Lot Number"', 'TEXT'),
                ('"Barcode*"', 'TEXT'),
                ('"Medical Only (Yes/No)"', 'TEXT'),
                ('"Med Price"', 'TEXT'),
                ('"Expiration Date(YYYY-MM-DD)"', 'TEXT'),
                ('"Is Archived? (yes/no)"', 'TEXT'),
                # Excel processor compatibility columns
                ('"ProductName"', 'TEXT'),  # Alternative to "Product Name*"
                ('"DOH Compliant (Yes/No)"', 'TEXT'),  # Alternative to "DOH"
                ('"Joint Ratio"', 'TEXT'),  # Alternative to "JointRatio"
                ('"Quantity Received*"', 'TEXT'),  # Alternative to "Quantity*"
                ('"qty"', 'TEXT'),  # Alternative to "Quantity*"
                ('"THC Per Serving"', 'TEXT'),
                ('"Allergens"', 'TEXT'),
                ('"Solvent"', 'TEXT'),
                ('"Accepted Date"', 'TEXT'),
                ('"Internal Product Identifier"', 'TEXT'),
                ('"Product Tags (comma separated)"', 'TEXT'),
                ('"Image URL"', 'TEXT'),
                ('"Ingredients"', 'TEXT'),
                ('"CombinedWeight"', 'TEXT'),
                ('"Ratio_or_THC_CBD"', 'TEXT'),
                ('"Description_Complexity"', 'TEXT'),
                ('"Total THC"', 'TEXT'),
                ('"THCA"', 'TEXT'),
                ('"CBDA"', 'TEXT'),
                ('"CBN"', 'TEXT'),
                # Additional cannabinoid columns for comprehensive testing
                ('"THC"', 'TEXT'),
                ('"CBD"', 'TEXT'),
                ('"Total CBD"', 'TEXT'),
                ('"CBGA"', 'TEXT'),
                ('"CBG"', 'TEXT'),
                ('"Total CBG"', 'TEXT'),
                ('"CBC"', 'TEXT'),
                ('"CBDV"', 'TEXT'),
                ('"THCV"', 'TEXT'),
                ('"CBGV"', 'TEXT'),
                ('"CBNV"', 'TEXT'),
                ('"CBGVA"', 'TEXT'),
                # Calculated THC/CBD values
                ('"AI"', 'TEXT'),
                ('"AJ"', 'TEXT'),
                ('"AK"', 'TEXT'),
                # Terpene columns - using the actual schema names
                ('"A-Bisabolol (mg/g)"', 'TEXT'),
                ('"A-Humulene (mg/g)"', 'TEXT'),
                ('"A-Maaliene (mg/g)"', 'TEXT'),
                ('"A-Myrcene (mg/g)"', 'TEXT'),
                ('"A-Pinene (mg/g)"', 'TEXT'),
                ('"B-Caryophyllene (mg/g)"', 'TEXT'),
                ('b_myrcene_mg_g', 'TEXT'),
                ('b_pinene_mg_g', 'TEXT'),
                ('bisabolol_mg_g', 'TEXT'),
                ('borneol_mg_g', 'TEXT'),
                ('camphene_mg_g', 'TEXT'),
                ('camphor_mg_g', 'TEXT'),
                ('carene_mg_g', 'TEXT'),
                ('carvacrol_mg_g', 'TEXT'),
                ('carvone_mg_g', 'TEXT'),
                ('caryophyllene_mg_g', 'TEXT'),
                ('cedrol_mg_g', 'TEXT'),
                ('citral_mg_g', 'TEXT'),
                ('citronellol_mg_g', 'TEXT'),
                ('cymene_mg_g', 'TEXT'),
                ('delta_3_carene_mg_g', 'TEXT'),
                ('eucalyptol_mg_g', 'TEXT'),
                ('fenchol_mg_g', 'TEXT'),
                ('fenchone_mg_g', 'TEXT'),
                ('geraniol_mg_g', 'TEXT'),
                ('geranyl_acetate_mg_g', 'TEXT'),
                ('guaiol_mg_g', 'TEXT'),
                ('humulene_mg_g', 'TEXT'),
                ('isoborneol_mg_g', 'TEXT'),
                ('isobornyl_acetate_mg_g', 'TEXT'),
                ('isopulegol_mg_g', 'TEXT'),
                ('limonene_mg_g', 'TEXT'),
                ('linalool_mg_g', 'TEXT'),
                ('linalyl_acetate_mg_g', 'TEXT'),
                ('m_cymene_mg_g', 'TEXT'),
                ('menthal_mg_g', 'TEXT'),
                ('menthone_mg_g', 'TEXT'),
                ('myrcene_mg_g', 'TEXT'),
                ('nerolidol_mg_g', 'TEXT'),
                ('o_cymene_mg_g', 'TEXT'),
                ('ocimene_mg_g', 'TEXT'),
                ('p_cymene_mg_g', 'TEXT')
            ]
            
            for col_name, col_type in expected_columns:
                # Strip quotes for comparison with existing columns
                col_name_clean = col_name.strip('"')
                if col_name_clean not in existing_columns:
                    missing_columns.append((col_name, col_type))
            
            # Add missing columns
            for col_name, col_type in missing_columns:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                    logger.info(f"Added missing column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        logger.debug(f"Column {col_name} already exists, skipping")
                    else:
                        logger.warning(f"Could not add column {col_name}: {e}")
                except Exception as e:
                    logger.warning(f"Could not add column {col_name}: {e}")
            
            if missing_columns:
                conn.commit()
                logger.info(f"Added {len(missing_columns)} missing columns to products table")
            
            # Only log the migration once we've performed the check at least once
            if not migration_logged:
                cursor.execute("INSERT OR REPLACE INTO _migration_log (migration_name, applied_date) VALUES (?, ?)", 
                              ('column_migration_v2', datetime.now().isoformat()))
                conn.commit()
            
            # Mark migration as applied in this session so we can optionally skip repeated logging
            if not migration_applied_this_session:
                self._migration_applied = True
            
            # Check and add missing columns to strains table
            cursor.execute("PRAGMA table_info(strains)")
            existing_strain_columns = {row[1] for row in cursor.fetchall()}
            
            missing_strain_columns = []
            
            # Define expected strain columns
            expected_strain_columns = [
                ('lineage_confidence', 'REAL'),
                ('sovereign_lineage', 'TEXT')
            ]
            
            for col_name, col_type in expected_strain_columns:
                if col_name not in existing_strain_columns:
                    missing_strain_columns.append((col_name, col_type))
            
            # Add missing strain columns
            for col_name, col_type in missing_strain_columns:
                try:
                    cursor.execute(f"ALTER TABLE strains ADD COLUMN {col_name} {col_type}")
                    logger.info(f"Added missing strain column: {col_name}")
                except Exception as e:
                    logger.warning(f"Could not add strain column {col_name}: {e}")
            
            if missing_strain_columns:
                conn.commit()
                logger.info(f"Added {len(missing_strain_columns)} missing columns to strains table")
            
        except Exception as e:
            logger.error(f"Error adding missing columns: {e}")
            # Don't raise - continue with existing schema
    
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


    def clear_lineage_cache(product_name: str = None):
        """Clear the internal lineage TTL cache.

        If `product_name` is provided, only that entry is removed. If `None`,
        the entire lineage cache is cleared.
        """
        with _lineage_cache_lock:
            if product_name:
                key = product_name.strip().lower()
                if key in _lineage_cache:
                    del _lineage_cache[key]
                    del _lineage_cache_timestamps[key]
                    logger.info(f"Cleared lineage cache entry for '{product_name}'")
            else:
                _lineage_cache.clear()
                _lineage_cache_timestamps.clear()
                logger.info("Cleared entire lineage cache")
    
    def close_connections(self):
        """Close all database connections."""
        for conn in self._connection_pool.values():
            conn.close()
        self._connection_pool.clear()
    
    def _normalize_strain_name(self, strain_name: str) -> str:
        """Normalize strain name for consistent matching."""
        if not isinstance(strain_name, str):
            return ""
        
        # Use the existing normalization function
        from .excel_processor import normalize_strain_name
        return normalize_strain_name(strain_name)
    
    def _normalize_product_name(self, product_name: str) -> str:
        """Normalize product name for consistent matching."""
        if not isinstance(product_name, str):
            return ""

        # Use the existing normalization function
        from .excel_processor import normalize_name
        return normalize_name(product_name)

    def _extract_strain_from_product_name(self, product_name: str, product_type: str = None) -> str:
        """Extract strain name from product name for classic product types.

        Only extracts for classic types: flower, pre-roll, concentrate, etc.
        Returns empty string for non-classic types (edibles, tinctures, topicals).
        """
        if not product_name or not isinstance(product_name, str):
            return ''

        # Define classic types (same as Excel processor)
        classic_types = [
            "flower", "pre-roll", "infused pre-roll", "concentrate",
            "solventless concentrate", "vape cartridge", "rso/co2 tankers"
        ]

        # Only extract for classic types
        if product_type and product_type.lower() not in classic_types:
            return ''

        # Extract strain name from product name
        # Common patterns:
        # "Pocket Aces Badder by Super Mega Bussin' - 1g" -> "Pocket Aces"
        # "Blue Dream Flower by Vendor - 3.5g" -> "Blue Dream"
        # "OG Kush Pre-Roll - 1g x 5 Pack" -> "OG Kush"

        import re

        # Remove common suffixes and brand info
        # Pattern: "StrainName ProductType by Brand - Weight"
        name = product_name.strip()

        # Remove " by [Brand]" part
        name = re.sub(r'\s+by\s+.+$', '', name, flags=re.IGNORECASE)

        # Remove weight info like " - 1g", " - 3.5g", etc.
        name = re.sub(r'\s*-\s*[\d.]+\s*g.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*-\s*\d+\s*x\s*[\d.]+.*$', '', name, flags=re.IGNORECASE)

        # Remove product type keywords
        product_type_keywords = [
            'badder', 'wax', 'crumble', 'sugar', 'sauce', 'diamonds', 'shatter',
            'live resin', 'live rosin', 'cured resin', 'hash rosin',
            'honey', 'butter', 'rocks', 'oil', 'distillate',
            'flower', 'pre-roll', 'preroll', 'infused', 'vape', 'cartridge'
        ]

        for keyword in product_type_keywords:
            # Remove keyword and anything after it (case-insensitive)
            pattern = r'\s+' + re.escape(keyword) + r'.*$'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        # Clean up and return
        strain_name = name.strip()

        # Validate: must be at least 2 characters and not a common non-strain word
        if len(strain_name) < 2:
            return ''

        non_strain_words = ['the', 'and', 'or', 'with', 'pack', 'box']
        if strain_name.lower() in non_strain_words:
            return ''

        return strain_name

    def _decode_json_abbreviations(self, json_name: str) -> str:
        """Decode JSON abbreviations to full product names."""
        decoded = json_name.lower().strip()
        
        # Decode product type abbreviations
        type_mappings = {
            'ball': 'chocolate ball',
            'bite': 'chocolate bites', 
            'chew': 'fruit chews',
            'caps': 'capsules',
            'tincs': 'tincture',
            'jar': 'balm',
            'squeeze_tube': 'squeeze tube',
            'roll_ups': 'roll up',
        }
        
        # Decode strain abbreviations
        strain_mappings = {
            'sat': 'sativa',
            'ind': 'indica',
        }
        
        # Decode flavor/type abbreviations
        flavor_mappings = {
            'caramel': 'salted caramel',
            'assorted': 'assorted',
            'dark': 'dark chocolate',
            'milk': 'milk chocolate',
            'cookies&cream': 'cookies cream',
            'dragon': 'dragon',
            'malt': 'malt',
            'cherry': 'cherry',
            'mango': 'mango',
            'watermelon': 'watermelon',
            'sour_apple': 'sour apple',
            'tropical': 'tropical',
            'mixed_berry': 'mixed berry',
            'guava': 'guava',
            'balance': 'balance',
            'chill': 'chill',
            'lifted': 'lifted',
            'relief': 'relief',
            'gold_max': 'max gold',
            'xtra': 'xtra strength',
        }
        
        # Split and decode
        parts = decoded.replace('_', ' ').split()
        decoded_parts = []
        
        for part in parts:
            if part in type_mappings:
                decoded_parts.append(type_mappings[part])
            elif part in strain_mappings:
                decoded_parts.append(strain_mappings[part])
            elif part in flavor_mappings:
                decoded_parts.append(flavor_mappings[part])
            elif part.endswith('pk'):
                continue  # Skip pack indicators
            else:
                decoded_parts.append(part)
        
        return ' '.join(decoded_parts)
    
    def _extract_key_words(self, product_name: str) -> set:
        """Extract key identifying words from a product name."""
        
        # First decode if it's a JSON abbreviation
        if '_' in product_name and any(c.isupper() for c in product_name):
            name = self._decode_json_abbreviations(product_name)
        else:
            name = product_name.lower()
        
        # Remove brand info
        import re
        name = re.sub(r'\bby\s+ceres\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\bceres\s*-\s*\d+\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\bceres\b', '', name, flags=re.IGNORECASE)
        
        # Remove common filler words
        filler_words = {
            'by', 'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 
            'for', 'with', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'through',
            'pack', 'pk', 'single', '10', '20', 'mg', 'thc', 'cbd', 'cbg', 'cbn'
        }
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', name.lower())
        key_words = set()
        
        for word in words:
            if len(word) >= 3 and word not in filler_words:
                key_words.add(word)
        
        return key_words
    
    def _fuzzy_match_products(self, json_name: str, db_name: str, threshold: float = 0.4) -> tuple:
        """Calculate fuzzy match score between JSON and database product names."""
        
        json_words = self._extract_key_words(json_name)
        db_words = self._extract_key_words(db_name)
        
        if not json_words or not db_words:
            return False, 0.0, set(), json_words, db_words
        
        # Find intersection
        common_words = json_words & db_words
        
        # Calculate Jaccard similarity
        union_words = json_words | db_words
        jaccard_score = len(common_words) / len(union_words) if union_words else 0.0
        
        # Calculate overlap percentage for JSON words (how many JSON words are found in DB)
        json_coverage = len(common_words) / len(json_words) if json_words else 0.0
        
        # Use the higher of the two scores
        final_score = max(jaccard_score, json_coverage)
        
        is_match = final_score >= threshold
        
        return is_match, final_score, common_words, json_words, db_words
    
    def get_products_by_names_with_fuzzy(self, product_names: List[str]) -> List[Dict[str, Any]]:
        """Enhanced product lookup with fuzzy matching for JSON abbreviations."""
        
        # First try exact matching
        exact_results = self.get_products_by_names(product_names)
        
        # Count how many exact matches we got
        exact_matches = [r for r in exact_results if r.get('id') is not None]
        
        if len(exact_matches) >= len(product_names) * 0.8:  # If we got 80%+ exact matches
            logger.info(f"🔍 EXACT MATCHING: Found {len(exact_matches)}/{len(product_names)} exact matches, skipping fuzzy matching")
            return exact_results
        
        # Otherwise, try fuzzy matching for missing items
        logger.info(f"🔍 FUZZY MATCHING: Only {len(exact_matches)}/{len(product_names)} exact matches found, trying fuzzy matching")
        
        # Get all CERES products for fuzzy matching
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, "Product Name*", normalized_name, "Vendor/Supplier*"
            FROM products 
            WHERE "Vendor/Supplier*" LIKE '%CERES%'
            LIMIT 500
        """)
        
        ceres_products = cursor.fetchall()
        logger.info(f"🔍 FUZZY MATCHING: Checking against {len(ceres_products)} CERES products")
        
        # Create fuzzy matching results
        fuzzy_results = []
        fuzzy_match_count = 0
        
        for product_name in product_names:
            best_match = None
            best_score = 0.0
            
            # Check if we already have an exact match
            exact_match = None
            for result in exact_results:
                if (result.get('Product Name*') == product_name or 
                    result.get('normalized_name') == self._normalize_product_name(product_name)):
                    exact_match = result
                    break
            
            if exact_match and exact_match.get('id'):
                fuzzy_results.append(exact_match)
                continue
            
            # Try fuzzy matching
            for db_product in ceres_products:
                db_name = db_product[1]  # Product Name*
                
                is_match, score, common, json_words, db_words = self._fuzzy_match_products(product_name, db_name)
                
                if score > best_score and score >= 0.4:  # 40% threshold
                    best_score = score
                    best_match = db_product
            
            if best_match:
                logger.info(f"🔍 FUZZY MATCH: '{product_name}' -> '{best_match[1]}' (score: {best_score:.3f})")
                fuzzy_match_count += 1
                
                # Get full product info
                full_products = self.get_products_by_names([best_match[1]])
                if full_products and full_products[0].get('id'):
                    fuzzy_results.append(full_products[0])
                else:
                    # Create placeholder
                    fuzzy_results.append({
                        'ProductName': product_name,
                        'Product Name*': product_name,
                        'Description': product_name,
                        'Vendor': '',
                        'Vendor/Supplier*': '',
                    })
            else:
                logger.info(f"🔍 FUZZY NO MATCH: '{product_name}' - no suitable match found")
                # Create placeholder
                fuzzy_results.append({
                    'ProductName': product_name,
                    'Product Name*': product_name,
                    'Description': product_name,
                    'Vendor': '',
                    'Vendor/Supplier*': '',
                })
        
        logger.info(f"🔍 FUZZY MATCHING COMPLETE: Found {fuzzy_match_count} additional fuzzy matches")
        logger.info(f"🔍 TOTAL MATCHES: {len(exact_matches)} exact + {fuzzy_match_count} fuzzy = {len(exact_matches) + fuzzy_match_count}/{len(product_names)}")
        
        return fuzzy_results
    
    def _normalize_lineage(self, lineage: str) -> str:
        """Normalize lineage to proper ALL CAPS format without losing hybrid details."""
        if lineage is None:
            return "HYBRID"
        
        raw_value = str(lineage).strip()
        if not raw_value:
            return "HYBRID"
        
        import re
        
        lowered = raw_value.lower()
        # Normalize separators to underscores so we can match variations consistently
        normalized = re.sub(r'[\s\-\\/]+', '_', lowered)
        normalized = re.sub(r'_+', '_', normalized).strip('_')
        
        # Direct mappings for the most common lineage strings
        lineage_mapping = {
            'hybrid': 'HYBRID',
            'indica': 'INDICA',
            'sativa': 'SATIVA',
            'cbd': 'CBD',
            'mixed': 'MIXED',
            'unknown': 'HYBRID',
            'none': 'HYBRID',
            'hybrid_indica': 'HYBRID/INDICA',
            'indica_hybrid': 'HYBRID/INDICA',
            'indica_dominant_hybrid': 'HYBRID/INDICA',
            'indica_dominant': 'HYBRID/INDICA',
            'hybrid_sativa': 'HYBRID/SATIVA',
            'sativa_hybrid': 'HYBRID/SATIVA',
            'sativa_dominant_hybrid': 'HYBRID/SATIVA',
            'sativa_dominant': 'HYBRID/SATIVA',
            'hybrid_cbd': 'CBD',
            'cbd_hybrid': 'CBD'
        }
        
        if normalized in lineage_mapping:
            return lineage_mapping[normalized]
        
        # Heuristic fallbacks when direct mapping failed
        if 'indica' in normalized and 'sativa' not in normalized:
            return 'HYBRID/INDICA'
        if 'sativa' in normalized and 'indica' not in normalized:
            return 'HYBRID/SATIVA'
        if 'cbd' in normalized:
            return 'CBD'
        
        # As a final fallback, return the upper-cased raw value so we keep user-provided info
        cleaned = raw_value.upper()
        return cleaned if cleaned else "HYBRID"
    
    def _ensure_crucial_value(self, value, fallback, field_name):
        """Ensure crucial values are not empty, providing intelligent fallbacks."""
        if value is None or not value or str(value).strip() == '' or str(value).lower() in ['nan', 'none', 'null']:
            logger.debug(f"Missing crucial value for {field_name}, using fallback: {fallback}")
            return fallback
        return str(value).strip()
    
    def _calculate_ai_value(self, row_dict):
        """Calculate AI value (THC) using all available THC columns."""
        try:
            # Get THC values from all available columns
            total_thc_value = str(row_dict.get('Total THC', '') or '').strip()
            thc_content_value = str(row_dict.get('THC Content', row_dict.get('THCA', '')) or '').strip()
            thc_test_result = str(row_dict.get('THC test result', '') or '').strip()
            thc_cbd_value = str(row_dict.get('THC_CBD', '') or '').strip()
            
            # Clean up values
            if total_thc_value in ['nan', 'NaN', '']:
                total_thc_value = ''
            if thc_content_value in ['nan', 'NaN', '']:
                thc_content_value = ''
            if thc_test_result in ['nan', 'NaN', '']:
                thc_test_result = ''
            if thc_cbd_value in ['nan', 'NaN', '']:
                thc_cbd_value = ''
            
            # Helper function to safely convert to float
            def safe_float(value):
                if not value or value in ['nan', 'NaN', '']:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # Helper function to extract THC value from THC_CBD string
            def extract_thc_from_thc_cbd(thc_cbd_str):
                if not thc_cbd_str:
                    return 0.0
                try:
                    # Look for patterns like "18.5% THC / 0.5% CBD" or "0.3% THC / 900mg CBD"
                    import re
                    # Match THC value with %
                    thc_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*THC', thc_cbd_str, re.IGNORECASE)
                    if thc_match:
                        return float(thc_match.group(1))
                    return 0.0
                except (ValueError, AttributeError):
                    return 0.0
            
            # Calculate THC values from all sources
            total_thc_float = safe_float(total_thc_value)
            thc_content_float = safe_float(thc_content_value)
            thc_test_float = safe_float(thc_test_result)
            thc_cbd_thc_float = extract_thc_from_thc_cbd(thc_cbd_value)
            
            # Find the highest THC value from all sources
            thc_values = [
                (total_thc_float, total_thc_value),
                (thc_content_float, thc_content_value),
                (thc_test_float, thc_test_result),
                (thc_cbd_thc_float, str(thc_cbd_thc_float) if thc_cbd_thc_float > 0 else '')
            ]
            
            # Sort by float value (highest first) and return the first non-empty string value
            thc_values.sort(key=lambda x: x[0], reverse=True)
            
            for float_val, str_val in thc_values:
                if float_val > 0 and str_val:
                    return str_val
            
            # If no valid THC value found, return empty string
            return ''
        except Exception as e:
            logger.error(f"Error calculating AI value: {e}")
            return ''
    
    def _calculate_ak_value(self, row_dict):
        """Calculate AK value (CBD) using all available CBD columns."""
        try:
            # Get CBD values from all available columns
            total_cbd_value = str(row_dict.get('Total CBD', row_dict.get('CBDA', '')) or '').strip()
            cbd_test_result_value = str(row_dict.get('CBD test result', '') or '').strip()
            cbd_content_value = str(row_dict.get('CBD Content', '') or '').strip()
            thc_cbd_value = str(row_dict.get('THC_CBD', '') or '').strip()
            
            # Clean up values
            if total_cbd_value in ['nan', 'NaN', '']:
                total_cbd_value = ''
            if cbd_test_result_value in ['nan', 'NaN', '']:
                cbd_test_result_value = ''
            if cbd_content_value in ['nan', 'NaN', '']:
                cbd_content_value = ''
            if thc_cbd_value in ['nan', 'NaN', '']:
                thc_cbd_value = ''
            
            # Helper function to safely convert to float
            def safe_float(value):
                if not value or value in ['nan', 'NaN', '']:
                    return 0.0
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # Helper function to extract CBD value from THC_CBD string
            def extract_cbd_from_thc_cbd(thc_cbd_str):
                if not thc_cbd_str:
                    return 0.0
                try:
                    # Look for patterns like "18.5% THC / 0.5% CBD" or "0.3% THC / 900mg CBD"
                    import re
                    # Match CBD value with % or mg
                    cbd_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|mg)?\s*CBD', thc_cbd_str, re.IGNORECASE)
                    if cbd_match:
                        return float(cbd_match.group(1))
                    return 0.0
                except (ValueError, AttributeError):
                    return 0.0
            
            # Calculate CBD values from all sources
            total_cbd_float = safe_float(total_cbd_value)
            cbd_test_result_float = safe_float(cbd_test_result_value)
            cbd_content_float = safe_float(cbd_content_value)
            thc_cbd_cbd_float = extract_cbd_from_thc_cbd(thc_cbd_value)
            
            # Find the highest CBD value from all sources
            cbd_values = [
                (total_cbd_float, total_cbd_value),
                (cbd_test_result_float, cbd_test_result_value),
                (cbd_content_float, cbd_content_value),
                (thc_cbd_cbd_float, str(thc_cbd_cbd_float) if thc_cbd_cbd_float > 0 else '')
            ]
            
            # Sort by float value (highest first) and return the first non-empty string value
            cbd_values.sort(key=lambda x: x[0], reverse=True)
            
            for float_val, str_val in cbd_values:
                if float_val > 0 and str_val:
                    return str_val
            
            # If no valid CBD value found, return empty string
            return ''
        except Exception as e:
            logger.error(f"Error calculating AK value: {e}")
            return ''
    
    def _update_existing_product(self, cursor, product_id, product_data):
        """Update an existing product with new data from Excel.

        HYBRID PRIORITY SYSTEM:
        - Price & DOH: Excel can overwrite (these change frequently in inventory)
        - Lineage & Other Fields: Database takes precedence, Excel only fills gaps
        - Exception: sovereign_lineage (manual edits) always wins over everything

        This allows Excel to update volatile fields (prices, compliance status) while
        preserving stable fields (lineage, product info) that are managed in database.
        """
        try:
            current_date = datetime.now().isoformat()

            # Get current product data for comparison
            cursor.execute('SELECT "Price", "THC test result", "CBD test result", "Weight*", "Units" FROM products WHERE id = ?', (product_id,))
            current_data = cursor.fetchone()
            
            # Log changes for important fields
            if current_data:
                old_price, old_thc, old_cbd, old_weight, old_units = current_data
                new_price = product_data.get('Price', '')
                new_thc = product_data.get('THC test result', '')
                new_cbd = product_data.get('CBD test result', '')
                new_weight = product_data.get('Weight*', '')
                new_units = product_data.get('Units', '')
                
                changes = []
                if str(old_price) != str(new_price):
                    changes.append(f"Price: {old_price} → {new_price}")
                if str(old_thc) != str(new_thc):
                    changes.append(f"THC: {old_thc} → {new_thc}")
                if str(old_cbd) != str(new_cbd):
                    changes.append(f"CBD: {old_cbd} → {new_cbd}")
                if str(old_weight) != str(new_weight):
                    changes.append(f"Weight: {old_weight} → {new_weight}")
                if str(old_units) != str(new_units):
                    changes.append(f"Units: {old_units} → {new_units}")
                
                if changes:
                    logger.info(f"Product ID {product_id} data changes: {'; '.join(changes)}")
                else:
                    logger.info(f"Product ID {product_id} updated with same values (no changes detected)")
            
            # Calculate AI and AK values
            ai_value = self._calculate_ai_value(product_data)
            ak_value = self._calculate_ak_value(product_data)
            
            # Update the product with new data
            # PRIORITY: Sovereign (manual) lineage ALWAYS takes precedence over Excel
            # Excel data overwrites database values ONLY if no sovereign lineage exists
            incoming_lineage = self._normalize_lineage(product_data.get('Lineage'))
            incoming_lineage_clean = str(incoming_lineage).strip() if incoming_lineage else ''

            # Check if incoming lineage is valid (not empty/null)
            has_valid_incoming_lineage = (incoming_lineage_clean and
                                        incoming_lineage_clean not in ['', 'nan', 'none', 'null', 'None', 'NaN'])

            # CRITICAL: Check if product has sovereign_lineage (manual override)
            cursor.execute('SELECT "sovereign_lineage" FROM products WHERE id = ?', (product_id,))
            sovereign_result = cursor.fetchone()
            sovereign_lineage = sovereign_result[0] if sovereign_result and sovereign_result[0] else ''
            sovereign_lineage_clean = str(sovereign_lineage).strip() if sovereign_lineage else ''
            has_sovereign_lineage = (sovereign_lineage_clean and
                                    sovereign_lineage_clean not in ['', 'nan', 'none', 'null', 'None', 'NaN'])

            # If product has sovereign lineage, NEVER overwrite it with Excel data
            if has_sovereign_lineage:
                final_lineage = sovereign_lineage_clean
                logger.info(f"🔒 SOVEREIGN LINEAGE PROTECTED: Keeping manual lineage '{final_lineage}' for product ID {product_id} (Excel update blocked)")
            # Otherwise use Excel lineage if it's valid
            elif has_valid_incoming_lineage:
                final_lineage = incoming_lineage_clean
                logger.info(f"✅ LINEAGE FROM EXCEL: Using Excel lineage '{final_lineage}' for product ID {product_id}")
            else:
                # Only preserve DB lineage if Excel has no lineage and no sovereign lineage
                cursor.execute('SELECT "Lineage" FROM products WHERE id = ?', (product_id,))
                current_db_lineage = cursor.fetchone()
                current_lineage = current_db_lineage[0] if current_db_lineage and current_db_lineage[0] else ''
                current_lineage_clean = str(current_lineage).strip() if current_lineage else ''
                has_existing_lineage = (current_lineage_clean and
                                      current_lineage_clean not in ['', 'nan', 'none', 'null', 'None', 'NaN'])

                if has_existing_lineage:
                    final_lineage = current_lineage_clean
                    logger.info(f"✅ LINEAGE PRESERVE: Keeping existing DB lineage '{final_lineage}' for product ID {product_id} (Excel had no lineage)")
                else:
                    final_lineage = ''
                    logger.info(f"⚠️ LINEAGE EMPTY: No lineage available for product ID {product_id}")
            
            # Get available columns in the database
            cursor.execute("PRAGMA table_info(products)")
            available_columns = {row[1] for row in cursor.fetchall()}
            
            # Build dynamic UPDATE statement to include ALL fields from product_data
            update_fields = []
            update_values = []
            
            # Core fields that need special handling
            product_name = product_data.get('Product Name*', product_data.get('ProductName', ''))
            normalized_name = self._normalize_product_name(product_name) if product_name else ''

            # PRIORITY SYSTEM:
            # - Price and DOH: Excel can overwrite (these change frequently)
            # - Other fields: Database takes precedence, Excel only fills gaps
            excel_doh = product_data.get('DOH', '')
            excel_price = product_data.get('Price', '')

            # Determine Price: ALWAYS use Excel if available (prices change frequently)
            has_excel_price = excel_price and str(excel_price).strip() not in ['', '0', '0.00', 'nan', 'none', 'null', 'None', 'NaN']

            if has_excel_price:
                final_price = excel_price
                logger.info(f"💰 PRICE FROM EXCEL: Using Excel price '{final_price}' for product '{product_name}'")
            else:
                # Fall back to DB price if Excel has no price
                cursor.execute('SELECT "Price" FROM products WHERE id = ?', (product_id,))
                current_price_result = cursor.fetchone()
                current_price = current_price_result[0] if current_price_result and current_price_result[0] else ''
                has_db_price = current_price and str(current_price).strip() not in ['', '0', '0.00', 'nan', 'none', 'null', 'None', 'NaN']

                if has_db_price:
                    final_price = current_price
                    logger.info(f"💰 PRICE FROM DB: Using database price '{final_price}' for product '{product_name}' (Excel had no price)")
                else:
                    final_price = ''
                    logger.info(f"⚠️ PRICE EMPTY: No price available for product '{product_name}'")

            # Determine DOH: ALWAYS use Excel if available (DOH status changes frequently)
            has_excel_doh = excel_doh and str(excel_doh).strip() not in ['', 'nan', 'none', 'null', 'None', 'NaN']

            if has_excel_doh:
                final_doh = excel_doh
                logger.info(f"🏷️ DOH FROM EXCEL: Using Excel DOH '{final_doh}' for product '{product_name}'")
            else:
                # Fall back to DB DOH if Excel has no DOH
                cursor.execute('SELECT "DOH" FROM products WHERE id = ?', (product_id,))
                current_doh_result = cursor.fetchone()
                current_doh = current_doh_result[0] if current_doh_result and current_doh_result[0] else ''
                has_db_doh = current_doh and str(current_doh).strip() not in ['', 'nan', 'none', 'null', 'None', 'NaN']

                if has_db_doh:
                    final_doh = current_doh
                    logger.info(f"🏷️ DOH FROM DB: Using database DOH '{final_doh}' for product '{product_name}' (Excel had no DOH)")
                else:
                    final_doh = ''

            # Update fields
            update_fields.append('"Product Type*" = ?')
            update_values.append(product_data.get('Product Type*'))

            update_fields.append('"Lineage" = ?')
            update_values.append(final_lineage)

            update_fields.append('"Price" = ?')
            update_values.append(final_price)

            update_fields.append('"DOH" = ?')
            update_values.append(final_doh)
            
            if normalized_name and 'normalized_name' in available_columns:
                update_fields.append('"normalized_name" = ?')
                update_values.append(normalized_name)
            
            update_fields.append('"last_seen_date" = ?')
            update_values.append(current_date)
            
            update_fields.append('"updated_at" = ?')
            update_values.append(current_date)
            
            # Add all other fields from product_data that exist in the database
            # Skip fields that are already handled above or are internal/metadata fields
            # CRITICAL: Block canonical_lineage from Excel - it must ONLY come from strains table
            skip_fields = {
                'Product Type*', 'Lineage', 'DOH', 'Price', 'last_seen_date', 'updated_at',
                'first_seen_date', 'created_at', 'total_occurrences', 'normalized_name',
                'id', 'strain_id',  # These are handled separately or shouldn't be updated
                'canonical_lineage', 'currentLineage'  # CRITICAL: Never allow Excel to overwrite these
            }
            
            # Fields that should NOT be overwritten by blank/empty Excel values
            preserve_nonblank_fields = {'Vendor/Supplier*', 'Vendor', 'Product Brand'}

            for col_name, col_value in product_data.items():
                if col_name in skip_fields:
                    continue
                # Only include if column exists in database
                if col_name in available_columns:
                    # If this is a vendor/brand-like field, only update when Excel provides a non-empty value
                    if col_name in preserve_nonblank_fields:
                        val = col_value
                        if val is None or (isinstance(val, str) and val.strip().lower() in ['', 'nan', 'none', 'null']):
                            # Skip updating vendor/brand with blank Excel value to avoid clobbering DB
                            logger.debug(f"Skipping update of '{col_name}' for product ID {product_id} because Excel provided empty value")
                            continue

                    update_fields.append(f'"{col_name}" = ?')
                    # Handle special calculated fields
                    if col_name == 'AI':
                        update_values.append(self._calculate_ai_value(product_data))
                    elif col_name == 'AK':
                        update_values.append(self._calculate_ak_value(product_data))
                    elif col_name == 'AJ':
                        update_values.append(product_data.get('THC Content', ''))
                    elif col_name == 'Product Strain':
                        update_values.append(self._calculate_product_strain_original(
                            product_data.get('Product Type*', ''),
                            product_data.get('Product Name*', ''),
                            product_data.get('Description', ''),
                            product_data.get('Ratio', '')
                        ))
                    else:
                        update_values.append(col_value)
            
            # Build and execute the UPDATE query
            update_query = f'UPDATE products SET {", ".join(update_fields)} WHERE id = ?'
            update_values.append(product_id)
            cursor.execute(update_query, update_values)
            
            # CRITICAL: Ensure lineage change is logged (commit handled by caller)
            logger.info(f"✅ Successfully updated product ID {product_id} with lineage '{final_lineage}'")
            
        except Exception as e:
            # Check if this is a database corruption error
            if self._is_corruption_error(e):
                logger.error(f"⚠️ Database corruption detected while updating product {product_id}: {e}")
                # Attempt recovery
                recovery_successful = self._attempt_database_recovery()
                if recovery_successful:
                    logger.info(f"🔄 Database recovered successfully. Connection will be refreshed on next operation.")
                    # Close all connections to force refresh
                    self.close_all_connections()
                    # Reset recovery flag so future corruptions can be handled
                    self._corruption_recovery_attempted = False
                    # Re-raise as a recoverable error - caller should retry the operation
                    raise RuntimeError(f"Database corruption detected and recovered. Please retry the operation: {e}") from e
                else:
                    logger.error(f"❌ Database recovery failed for product {product_id}")
                    raise RuntimeError(f"Database corruption detected and recovery failed. Database may need manual repair: {e}") from e
            else:
                logger.error(f"Error updating existing product {product_id}: {e}")
                raise
    
    def _process_description(self, product_name, original_description=''):
        """Process product name to create a clean description using the same rules as Excel processor."""
        if not product_name or str(product_name).strip() == '':
            return original_description if original_description else ''
        
        name = str(product_name).strip()
        if not name:
            return original_description if original_description else ''
        
        # Apply the same description processing rules as the Excel processor
        # Handle "Product Name by Vendor - Weight" format
        if ' by ' in name and ' - ' in name:
            # Extract just the product name part before " by "
            return name.split(' by ')[0].strip()
        elif ' by ' in name:
            return name.split(' by ')[0].strip()
        elif ' - ' in name:
            # Only split on dashes followed by weight information (numbers, decimals, units)
            import re
            if re.search(r' - [\d.]', name):
                # Remove weight part but preserve the dash in product names
                return re.sub(r' - [\d.].*$', '', name).strip()
            else:
                # No weight information, return the name as-is
                return name.strip()
        return name.strip()
    
    def fix_description_format(self):
        """Fix Description field format to extract just product name from 'Product Name by Vendor - Weight' format."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products with descriptions that contain " by " and " - "
            cursor.execute('''
                SELECT id, "Description", "Product Name*" 
                FROM products 
                WHERE "Description" LIKE '% by %' AND "Description" LIKE '% - %'
            ''')
            
            products_to_fix = cursor.fetchall()
            logger.info(f"Found {len(products_to_fix)} products with 'by Vendor - Weight' format in Description")
            
            fixed_count = 0
            for product_id, current_desc, product_name in products_to_fix:
                # Process the description to extract just the product name
                fixed_desc = self._process_description(current_desc, '')
                if fixed_desc != current_desc:
                    cursor.execute('''
                        UPDATE products 
                        SET "Description" = ?
                        WHERE id = ?
                    ''', (fixed_desc, product_id))
                    fixed_count += 1
                    logger.debug(f"Fixed Description for product {product_id}: '{current_desc}' -> '{fixed_desc}'")
            
            conn.commit()
            logger.info(f"Fixed {fixed_count} product descriptions")
            return {'fixed': fixed_count, 'total_checked': len(products_to_fix)}
            
        except Exception as e:
            logger.error(f"Error fixing description format: {e}")
            return {'fixed': 0, 'total_checked': 0, 'error': str(e)}

    def fix_all_description_values(self):
        """
        Comprehensive fix for all description values to ensure they meet Product Name transformation criteria.
        This function will:
        1. Replace Description with Product Name (everything before 'by')
        2. Remove vendor information after 'by'
        3. Remove weight information after ' - ' followed by numbers
        4. Clean parentheses and brackets but preserve content
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products that have both Product Name and Description AND valid IDs
            cursor.execute('''
                SELECT id, "Product Name*", "Description"
                FROM products 
                WHERE "Product Name*" IS NOT NULL AND "Product Name*" != '' AND id IS NOT NULL
            ''')
            
            all_products = cursor.fetchall()
            logger.info(f"Found {len(all_products)} products with Product Name and valid IDs to process")
            
            fixed_count = 0
            skipped_count = 0
            
            for product_id, product_name, current_desc in all_products:
                # Apply the same transformation logic as Excel processing
                # Use Product Name as base, everything before 'by'
                transformed_desc = self._process_description(product_name, current_desc)
                
                # Only update if the description would change
                if transformed_desc != current_desc:
                    cursor.execute('''
                        UPDATE products 
                        SET "Description" = ?
                        WHERE id = ?
                    ''', (transformed_desc, product_id))
                    fixed_count += 1
                    logger.debug(f"Fixed Description for product {product_id}: '{current_desc}' -> '{transformed_desc}'")
                else:
                    skipped_count += 1
            
            conn.commit()
            logger.info(f"Fixed {fixed_count} product descriptions, skipped {skipped_count} (already correct)")
            return {
                'fixed': fixed_count, 
                'skipped': skipped_count,
                'total_processed': len(all_products),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error fixing all description values: {e}")
            return {'fixed': 0, 'skipped': 0, 'total_processed': 0, 'error': str(e), 'success': False}

    def identify_bad_descriptions(self):
        """
        Identify all description values that don't meet the Product Name transformation criteria.
        Returns a list of products that need fixing.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products that have both Product Name and Description
            cursor.execute('''
                SELECT id, "Product Name*", "Description"
                FROM products 
                WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
            ''')
            
            all_products = cursor.fetchall()
            bad_descriptions = []
            
            for product_id, product_name, current_desc in all_products:
                # Apply the transformation logic to see what the description should be
                expected_desc = self._process_description(product_name, current_desc)
                
                # Check if current description doesn't match expected
                if current_desc != expected_desc:
                    bad_descriptions.append({
                        'id': product_id,
                        'product_name': product_name,
                        'current_description': current_desc,
                        'expected_description': expected_desc
                    })
            
            logger.info(f"Found {len(bad_descriptions)} products with incorrect descriptions")
            return {
                'bad_descriptions': bad_descriptions,
                'total_products': len(all_products),
                'bad_count': len(bad_descriptions),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error identifying bad descriptions: {e}")
            return {'bad_descriptions': [], 'total_products': 0, 'bad_count': 0, 'error': str(e), 'success': False}

    def backfill_missing_crucial_values(self):
        """Backfill missing crucial values in existing products."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Update products with missing or old descriptions using processed descriptions
            # First, get all products that need description updates
            cursor.execute('''
                SELECT "id", "Product Name*", "Description"
                FROM products 
                WHERE "Description" IS NULL OR "Description" = "" OR "Description" = "nan"
                   OR "Description" LIKE "%Hustler's Ambition -%" 
                   OR "Description" LIKE "%Hustler's Ambition Flower%"
                   OR "Description" LIKE "%Hustler's Ambition - Wax%"
                   OR "Description" LIKE "%Hustler's Ambition - Preroll%"
            ''')
            products_to_update = cursor.fetchall()
            
            desc_updated = 0
            old_desc_updated = 0
            
            for product_id, product_name, current_desc in products_to_update:
                # Process the description using the same rules
                processed_desc = self._process_description(product_name, current_desc)
                
                # Update the product with the processed description
                cursor.execute('''
                    UPDATE products 
                    SET "Description" = ?
                    WHERE "id" = ?
                ''', (processed_desc, product_id))
                
                if not current_desc or current_desc.strip() == '' or current_desc == 'nan':
                    desc_updated += 1
                else:
                    old_desc_updated += 1
            
            # Update products with missing Weight
            cursor.execute('''
                UPDATE products 
                SET "Weight*" = "1g"
                WHERE "Weight*" IS NULL OR "Weight*" = "" OR "Weight*" = "nan"
            ''')
            weight_updated = cursor.rowcount
            
            # Update products with missing Price
            cursor.execute('''
                UPDATE products 
                SET "Price" = "0.00"
                WHERE "Price" IS NULL OR "Price" = "" OR "Price" = "nan"
            ''')
            price_updated = cursor.rowcount
            
            # Update products with missing THC test result
            cursor.execute('''
                UPDATE products 
                SET "THC test result" = "0.0"
                WHERE "THC test result" IS NULL OR "THC test result" = "" OR "THC test result" = "nan"
            ''')
            thc_updated = cursor.rowcount
            
            # Update products with missing CBD test result
            cursor.execute('''
                UPDATE products 
                SET "CBD test result" = "0.0"
                WHERE "CBD test result" IS NULL OR "CBD test result" = "" OR "CBD test result" = "nan"
            ''')
            cbd_updated = cursor.rowcount
            
            # Update products with missing Product Type
            cursor.execute('''
                UPDATE products 
                SET "Product Type*" = "Unknown"
                WHERE "Product Type*" IS NULL OR "Product Type*" = "" OR "Product Type*" = "nan"
            ''')
            type_updated = cursor.rowcount
            
            # Update products with missing Vendor
            cursor.execute('''
                UPDATE products 
                SET "Vendor/Supplier*" = "Unknown Vendor"
                WHERE "Vendor/Supplier*" IS NULL OR "Vendor/Supplier*" = "" OR "Vendor/Supplier*" = "nan"
            ''')
            vendor_updated = cursor.rowcount
            
            # Update products with missing Units
            cursor.execute('''
                UPDATE products 
                SET "Units" = "each"
                WHERE "Units" IS NULL OR "Units" = "" OR "Units" = "nan"
            ''')
            units_updated = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Backfilled missing crucial values:")
            logger.info(f"  - Description (missing): {desc_updated} products")
            logger.info(f"  - Description (old Excel format): {old_desc_updated} products")
            logger.info(f"  - Weight: {weight_updated} products")
            logger.info(f"  - Price: {price_updated} products")
            logger.info(f"  - THC test result: {thc_updated} products")
            logger.info(f"  - CBD test result: {cbd_updated} products")
            logger.info(f"  - Product Type: {type_updated} products")
            logger.info(f"  - Vendor: {vendor_updated} products")
            logger.info(f"  - Units: {units_updated} products")
            
            return {
                'description': desc_updated + old_desc_updated,
                'description_missing': desc_updated,
                'description_old_format': old_desc_updated,
                'weight': weight_updated,
                'price': price_updated,
                'thc': thc_updated,
                'cbd': cbd_updated,
                'type': type_updated,
                'vendor': vendor_updated,
                'units': units_updated
            }
            
        except Exception as e:
            logger.error(f"Error backfilling missing crucial values: {e}")
            return None
    
    def _calculate_product_strain_original(self, product_type: str, product_name: str, description: str, ratio: str) -> str:
        """Calculate Product Strain using exact Excel processor logic."""
        from src.core.constants import CLASSIC_TYPES
        
        product_type = str(product_type).strip().lower()
        product_name = str(product_name).strip()
        description = str(description).strip()
        ratio = str(ratio).strip()
        
        # Handle 'nan' values
        if product_name.lower() == 'nan':
            product_name = ''
        if description.lower() == 'nan':
            description = ''
        if ratio.lower() == 'nan':
            ratio = ''
        
        # Classic types don't need Product Strain values set by this logic
        # They use actual strain names from the Product Strain column
        if product_type in CLASSIC_TYPES:
            return ''  # Let the actual strain name be used
        
        # For non-classic types, determine if it's CBD or Mixed
        # CRITICAL: CBD detection is ONLY based on product name/title
        import re
        
        # Check if product name contains CBD, CBG, CBC, or CBN
        name_contains_cbd = bool(re.search(r'\b(?:CBD|CBG|CBC|CBN)\b', product_name, re.IGNORECASE))
        
        # If product name contains cannabinoids, set to "CBD Blend"
        if name_contains_cbd:
            return "CBD Blend"
        
        # Otherwise, set to "Mixed"
        return "Mixed"
    
    def _extract_ratio_from_product_name(self, product_name: str, product_type: str) -> str:
        """Extract ratio from product name for NonClassic types using same logic as Excel processor."""
        import re
        
        # Define classic types (same as Excel processor)
        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
        
        # Only extract ratio for non-classic types (including capsules)
        if product_type.lower() not in classic_types:
            if product_name and isinstance(product_name, str):
                # Extract text after final dash (cannabinoid content)
                # This is what the Excel processor does - it extracts the part after the dash
                # which contains the actual cannabinoid amounts, not the ratios
                match = re.search(r".*-\s*(.+)", product_name)
                if match:
                    extracted_content = match.group(1).strip()
                    # Replace "/" with space to remove backslash formatting (same as Excel processor)
                    # But preserve the slash in ratios like "10mg THC / 5mg CBD"
                    if "/" in extracted_content and not any(cannabinoid in extracted_content.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                        extracted_content = extracted_content.replace("/", " ")
                    # Replace "nan" values with empty string (same as Excel processor)
                    if extracted_content.lower() == "nan":
                        extracted_content = ""
                    return extracted_content
        
        return ""

    def _calculate_ratio_or_thc_cbd(self, product_type: str, ratio: str, joint_ratio: str, product_name: str = "", thc_value: str = "", cbd_value: str = "") -> str:
        """Calculate Ratio_or_THC_CBD using exact Excel processor logic."""
        import re
        
        def is_real_ratio(text: str) -> bool:
            """Check if a string represents a valid ratio format."""
            if not text or not isinstance(text, str):
                return False
            
            # Clean the text
            text = text.strip()
            
            # Check for common invalid values
            if text in ['', 'CBD', 'THC', 'CBD:', 'THC:', 'CBD:\n', 'THC:\n']:
                return False
            
            # Check for mg values (e.g., '100mg', '500mg THC', '10mg CBD')
            if 'mg' in text.lower():
                return True
            
            # Check for ratio patterns (e.g., '1:1', '2:1', '1:2:1')
            ratio_pattern = r'^\d+(?::\d+)+$'
            if re.match(ratio_pattern, text):
                return True
            
            # Check for percentage patterns (e.g., '20%', '15.5%')
            percent_pattern = r'^\d+(?:\.\d+)?%$'
            if re.match(percent_pattern, text):
                return True
            
            return False
        
        def is_weight_with_unit(text: str) -> bool:
            """Check if a string represents a weight with unit format (e.g., '1g', '3.5g', '1oz')."""
            if not text or not isinstance(text, str):
                return False
            
            # Clean the text
            text = text.strip()
            
            # Check for weight + unit patterns
            weight_patterns = [
                r'^\d+(?:\.\d+)?\s*(?:g|gram|grams|gm|oz|ounce|ounces)$',  # 1g, 3.5g, 1oz, etc.
                r'^\d+(?:\.\d+)?\s*(?:g|gram|grams|gm|oz|ounce|ounces)\s*$',  # with trailing space
            ]
            
            for pattern in weight_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    return True
            
            return False
        
        product_type = str(product_type).strip().lower()
        ratio = str(ratio).strip()
        
        # Handle 'nan' values by replacing with empty string
        if ratio.lower() == 'nan':
            ratio = ''
        
        # For NonClassic types, extract ratio from product name if no ratio is provided
        if not ratio or ratio in ['', 'nan']:
            extracted_ratio = self._extract_ratio_from_product_name(product_name, product_type)
            if extracted_ratio:
                ratio = extracted_ratio
        
        classic_types = [
            'flower', 'pre-roll', 'infused pre-roll', 'concentrate', 'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'
        ]
        # Note: capsules are NOT classic types for ratio processing - they should be treated as edibles
        BAD_VALUES = {'', 'CBD', 'THC', 'CBD:', 'THC:', 'CBD:\n', 'THC:\n', 'nan'}
        
        # For paraphernalia/hardware products, don't show THC/CBD values
        if product_type in ['paraphernalia', 'hardware', 'accessory']:
            return ''  # Empty for non-cannabis products
        
        # For pre-rolls, infused pre-rolls, concentrates, and solventless concentrates, treat as classic types
        if product_type in ['pre-roll', 'infused pre-roll', 'concentrate', 'solventless concentrate']:
            # Use actual THC/CBD values if available, otherwise use default format
            if thc_value and cbd_value and str(thc_value).strip() not in ['nan', 'NaN', ''] and str(cbd_value).strip() not in ['nan', 'NaN', '']:
                thc_str = str(thc_value).strip()
                cbd_str = str(cbd_value).strip()
                return f"THC: {thc_str}% CBD: {cbd_str}%"
            elif thc_value and str(thc_value).strip() not in ['nan', 'NaN', '']:
                thc_str = str(thc_value).strip()
                return f"THC: {thc_str}%"
            elif cbd_value and str(cbd_value).strip() not in ['nan', 'NaN', '']:
                cbd_str = str(cbd_value).strip()
                return f"CBD: {cbd_str}%"
            else:
                return 'THC: | BR | C'
        
        if product_type in classic_types:
            # For classic types, prioritize THC/CBD values if available
            if thc_value and cbd_value and str(thc_value).strip() not in ['nan', 'NaN', ''] and str(cbd_value).strip() not in ['nan', 'NaN', '']:
                thc_str = str(thc_value).strip()
                cbd_str = str(cbd_value).strip()
                return f"THC: {thc_str}% CBD: {cbd_str}%"
            elif thc_value and str(thc_value).strip() not in ['nan', 'NaN', '']:
                thc_str = str(thc_value).strip()
                return f"THC: {thc_str}%"
            elif cbd_value and str(cbd_value).strip() not in ['nan', 'NaN', '']:
                cbd_str = str(cbd_value).strip()
                return f"CBD: {cbd_str}%"
            elif not ratio or ratio in BAD_VALUES:
                return 'THC: | BR | C'
            # If ratio contains THC/CBD values, use it directly
            elif any(cannabinoid in ratio.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                return ratio
            # If it's a valid ratio format, use it
            elif is_real_ratio(ratio):
                return ratio
            # If it's a weight format (like '1g', '28g'), use it
            elif is_weight_with_unit(ratio):
                return ratio
            # Otherwise, use default THC:CBD format
            else:
                return 'THC: | BR | C'
        
        # For Edibles, Topicals, Tinctures, etc., use the ratio if it contains cannabinoid content
        edible_types = {'edible (solid)', 'edible (liquid)', 'high cbd edible liquid', 'tincture', 'topical', 'capsule'}
        if product_type in edible_types:
            if not ratio or ratio in BAD_VALUES:
                return 'THC: | BR | C'
            # If ratio contains cannabinoid content, use it
            if any(cannabinoid in ratio.upper() for cannabinoid in ['THC', 'CBD', 'CBC', 'CBG', 'CBN']):
                return ratio
            # If it's a valid ratio format, use it
            if is_real_ratio(ratio):
                return ratio
            # If it's a weight format, use it
            if is_weight_with_unit(ratio):
                return ratio
            # Otherwise, use default THC:CBD format
            return 'THC: | BR | C'
        
        # For any other product type, return the ratio as-is
        return ratio
    
    
    def batch_fix_cbd_products(self) -> Dict[str, Any]:
        """Batch update all products in database: set Product Strain='CBD Blend' and Lineage='CBD' for products with CBD indicators."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            import re
            from src.core.constants import CLASSIC_TYPES
            
            # Get all nonclassic products
            cursor.execute('''
                SELECT id, "Product Name*", "Product Type*", "Description", "Product Strain", "Lineage"
                FROM products
            ''')
            
            products = cursor.fetchall()
            updated_count = 0
            
            for product_id, product_name, product_type, description, current_strain, current_lineage in products:
                if not product_name:
                    continue
                    
                product_type_lower = (product_type or '').strip().lower()
                is_classic_type = product_type_lower in CLASSIC_TYPES or any(ct in product_type_lower for ct in CLASSIC_TYPES)
                
                if is_classic_type:
                    continue  # Skip classic types
                
                # Check for CBD indicators
                product_name_upper = (product_name or '').upper()
                description_upper = (description or '').upper()
                has_ratio = bool(re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', product_name_upper) or re.search(r'\b\d+\s*:\s*\d+(?:\s*:\s*\d+)?\b', description_upper))
                has_cbd_token = any(token in product_name_upper for token in ['CBD', 'CBG', 'CBN', 'CBC']) or any(token in description_upper for token in ['CBD', 'CBG', 'CBN', 'CBC'])
                
                if has_ratio or has_cbd_token:
                    # Update to CBD Blend / CBD
                    cursor.execute('''
                        UPDATE products 
                        SET "Product Strain" = ?,
                            "Lineage" = ?,
                            sovereign_lineage = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', ('CBD Blend', 'CBD', 'CBD', product_id))
                    updated_count += 1
                    logger.info(f"✅ BATCH CBD FIX: Updated '{product_name}' -> Product Strain='CBD Blend', Lineage='CBD'")
            
            conn.commit()
            logger.info(f"✅ BATCH CBD FIX: Updated {updated_count} products with CBD indicators")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Successfully updated {updated_count} products with CBD indicators'
            }
            
        except Exception as e:
            logger.error(f"Error batch fixing CBD products: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to batch fix CBD products: {str(e)}'
            }
    
    def batch_fix_nonclassic_gram_weights(self) -> Dict[str, Any]:
        """Batch fix non-classic products that have gram weights by converting them to ounces."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            from src.core.constants import CLASSIC_TYPES
            
            # Get all non-classic products with gram weights
            cursor.execute('''
                SELECT id, "Product Name*", "Product Type*", "Weight*", Units
                FROM products
            ''')
            
            products = cursor.fetchall()
            updated_count = 0
            skipped_count = 0
            
            for product_id, product_name, product_type, weight, units in products:
                if not product_name or not product_type:
                    continue
                
                product_type_lower = (product_type or '').strip().lower()
                is_classic_type = product_type_lower in CLASSIC_TYPES or any(ct in product_type_lower for ct in CLASSIC_TYPES)
                
                if is_classic_type:
                    continue  # Skip classic types
                
                # Check if units are grams
                units_lower = (units or '').strip().lower()
                if 'g' not in units_lower and 'gram' not in units_lower:
                    continue  # Not grams, skip
                
                # Check if already has oz
                if 'oz' in units_lower or 'ounce' in units_lower:
                    skipped_count += 1
                    continue  # Already has ounces
                
                # Convert grams to ounces
                try:
                    weight_val = float(str(weight).strip())
                    oz_val = round(weight_val / 28.3495, 2)
                    
                    # Format weight without trailing zeros
                    if oz_val.is_integer():
                        formatted_weight = str(int(oz_val))
                    else:
                        formatted_weight = f"{oz_val:.2f}".rstrip('0').rstrip('.')
                    
                    # Update product with ounces
                    cursor.execute('''
                        UPDATE products 
                        SET "Weight*" = ?,
                            Units = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (formatted_weight, 'oz', product_id))
                    updated_count += 1
                    logger.info(f"✅ BATCH GRAM FIX: Converted '{product_name}' from {weight}g to {formatted_weight}oz")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"⚠️ Could not convert weight '{weight}' for product '{product_name}': {e}")
                    skipped_count += 1
                    continue
            
            conn.commit()
            logger.info(f"✅ BATCH GRAM FIX: Converted {updated_count} non-classic products from grams to ounces (skipped {skipped_count})")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'skipped_count': skipped_count,
                'message': f'Successfully converted {updated_count} non-classic products from grams to ounces'
            }
            
        except Exception as e:
            logger.error(f"Error batch fixing non-classic gram weights: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to batch fix non-classic gram weights: {str(e)}'
            }
    
    def update_all_product_strains(self) -> Dict[str, Any]:
        """Update all products with correct Product Strain values based on Excel logic."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all products that need Product Strain updates
            cursor.execute('''
                SELECT id, "Product Name*", "Product Type*", "Description", "Ratio"
                FROM products
            ''')
            
            products = cursor.fetchall()
            updated_count = 0
            
            for product_id, product_name, product_type, description, ratio in products:
                # Calculate the correct Product Strain value
                new_strain = self._calculate_product_strain_original(
                    product_type or '',
                    product_name or '',
                    description or '',
                    ratio or ''
                )
                
                # Update the Product Strain
                cursor.execute('''
                    UPDATE products 
                    SET "Product Strain" = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_strain, datetime.now().isoformat(), product_id))
                updated_count += 1
            
            conn.commit()
            logger.info(f"Updated {updated_count} products with correct Product Strain values")
            
            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Successfully updated {updated_count} products with correct Product Strain values'
            }
            
        except Exception as e:
            logger.error(f"Error updating Product Strain values: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update Product Strain values: {str(e)}'
            }
    
    @timed_operation("get_all_strains")
    def get_all_strains(self) -> Set[str]:
        """Get all normalized strain names from the database for fast lookup."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            cache_key = self._get_cache_key("all_strains")
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT normalized_name FROM strains')
            
            strains = {row[0] for row in cursor.fetchall() if row[0]}
            
            # Cache the result for 10 minutes (strains don't change often)
            self._set_cache(cache_key, strains, ttl=600)
            return strains
            
        except Exception as e:
            logger.error(f"Error getting all strains: {e}")
            return set()
    
    @timed_operation("get_strain_lineage_map")
    def get_strain_lineage_map(self) -> Dict[str, str]:
        """Get a mapping of normalized strain names to their lineages, prioritizing sovereign (manual) lineages."""
        try:
            self.init_database()  # Ensure DB is initialized

            cache_key = self._get_cache_key("strain_lineage_map")

            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            conn = self._get_connection()
            cursor = conn.cursor()
            # CRITICAL FIX: Prioritize sovereign_lineage (manual edits) over canonical_lineage (Excel data)
            cursor.execute('SELECT normalized_name, COALESCE(sovereign_lineage, canonical_lineage) FROM strains WHERE COALESCE(sovereign_lineage, canonical_lineage) IS NOT NULL')

            lineage_map = {row[0]: row[1] for row in cursor.fetchall() if row[0] and row[1]}

            # Cache the result for 10 minutes
            self._set_cache(cache_key, lineage_map, ttl=600)
            return lineage_map

        except Exception as e:
            logger.error(f"Error getting strain lineage map: {e}")
            return {}
    
    def upsert_strain_brand_lineage(self, strain_name: str, brand: str, lineage: str):
        """Insert or update lineage for a (strain_name, brand) pair."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO strain_brand_lineage (strain_name, brand, lineage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(strain_name, brand) DO UPDATE SET lineage=excluded.lineage, updated_at=excluded.updated_at
            ''', (strain_name, brand, lineage, now, now))
            conn.commit()
            logger.info(f"Upserted lineage for ({strain_name}, {brand}) -> {lineage}")
        except Exception as e:
            logger.error(f"Error upserting strain_brand_lineage: {e}")
            raise 

    def update_product_lineage(self, product_name: str, new_lineage: str, vendor: str = None, brand: str = None) -> bool:
        """Update the lineage for a product in the database."""
        try:
            self.init_database()
            normalized_name = self._normalize_product_name(product_name)
            conn = self._get_connection()
            cursor = conn.cursor()
            import re

            def _name_variants(raw_name: str):
                variants = []
                if not raw_name:
                    return variants
                name = str(raw_name).replace('\u2011', '-').strip()
                if not name:
                    return variants
                variants.append(name)
                vendor_removed = re.sub(r'\s+by\s+[^-]+(?=(\s*-\s*\d|\s*$))', '', name, flags=re.IGNORECASE)
                vendor_removed = re.sub(r'\s+by\s+[^-]+$', '', vendor_removed, flags=re.IGNORECASE)
                variants.append(vendor_removed.strip())
                weight_removed = re.sub(
                    r'\s*-\s*\d+(?:\.\d+)?\s*(?:g|gram|grams|gm|oz|ounce|ounces|ml|mg|ct|pack|pk|pcs|pc)?$',
                    '',
                    vendor_removed,
                    flags=re.IGNORECASE
                ).strip()
                variants.append(weight_removed)
                deduped = []
                seen = set()
                for v in variants:
                    c = re.sub(r'\s+', ' ', str(v or '').strip())
                    if c and c.lower() not in seen:
                        deduped.append(c)
                        seen.add(c.lower())
                return deduped

            variants = _name_variants(product_name)
            lower_variants = [v.lower() for v in variants]
            normalized_variants = []
            for v in variants:
                nv = self._normalize_product_name(v)
                if nv and nv not in normalized_variants:
                    normalized_variants.append(nv)
            if normalized_name and normalized_name not in normalized_variants:
                normalized_variants.append(normalized_name)

            # CRITICAL FIX: Use normalized name and try both column names
            # This ensures updates work even with formatting differences
            # CRITICAL: Set BOTH Lineage and sovereign_lineage for manual updates
            if vendor and brand:
                where_parts = []
                params = [new_lineage, new_lineage]
                if lower_variants:
                    placeholders = ','.join(['?'] * len(lower_variants))
                    where_parts.append(f'LOWER(TRIM("Product Name*")) IN ({placeholders})')
                    params.extend(lower_variants)
                    where_parts.append(f'LOWER(TRIM("ProductName")) IN ({placeholders})')
                    params.extend(lower_variants)
                if normalized_variants:
                    placeholders = ','.join(['?'] * len(normalized_variants))
                    where_parts.append(f'normalized_name IN ({placeholders})')
                    params.extend(normalized_variants)
                if not where_parts:
                    where_parts.append('"Product Name*" = ?')
                    params.append(product_name)

                params.extend([vendor, brand])
                cursor.execute(f'''
                    UPDATE products
                    SET "Lineage" = ?, sovereign_lineage = ?
                    WHERE ({" OR ".join(where_parts)})
                    AND "Vendor/Supplier*" = ? AND "Product Brand" = ?
                ''', params)
                logger.info(f"Updated lineage (and sovereign_lineage) for product '{product_name}' (vendor={vendor}, brand={brand}) to '{new_lineage}'")
            else:
                where_parts = []
                params = [new_lineage, new_lineage]
                if lower_variants:
                    placeholders = ','.join(['?'] * len(lower_variants))
                    where_parts.append(f'LOWER(TRIM("Product Name*")) IN ({placeholders})')
                    params.extend(lower_variants)
                    where_parts.append(f'LOWER(TRIM("ProductName")) IN ({placeholders})')
                    params.extend(lower_variants)
                if normalized_variants:
                    placeholders = ','.join(['?'] * len(normalized_variants))
                    where_parts.append(f'normalized_name IN ({placeholders})')
                    params.extend(normalized_variants)
                if not where_parts:
                    where_parts.append('"Product Name*" = ?')
                    params.append(product_name)

                cursor.execute(f'''
                    UPDATE products
                    SET "Lineage" = ?, sovereign_lineage = ?
                    WHERE {" OR ".join(where_parts)}
                ''', params)
                logger.info(f"Updated lineage (and sovereign_lineage) for product '{product_name}' to '{new_lineage}' using variant matching")

            conn.commit()
            rows_updated = cursor.rowcount
            if rows_updated == 0:
                logger.warning(f"No product found in database to update: '{product_name}' (vendor={vendor}, brand={brand})")
            else:
                logger.info(f"Successfully updated {rows_updated} row(s) for product '{product_name}'")

                # CRITICAL FIX: Clear full lineage cache after updates.
                # Product lookups are done via multiple name variants (exact/lower/normalized),
                # so clearing only one key can leave stale lineage in cache.
                with _lineage_cache_lock:
                    _lineage_cache.clear()
                    _lineage_cache_timestamps.clear()
                    logger.info(f"✅ Cleared entire lineage cache after update for '{product_name}'")

            return rows_updated > 0
        except Exception as e:
            logger.error(f"Error updating product lineage for '{product_name}': {e}")
            return False 

    def get_product_lineage(self, product_name: str, bypass_cache: bool = False) -> Optional[str]:
        """Get the lineage for a specific product by name.

        Uses case-insensitive and whitespace-insensitive matching to ensure
        updates are found even if there are minor differences in formatting.
        Also applies sativa hybrid override for known sativa hybrid strains.
        """
        # PERFORMANCE: Check cache first unless explicitly bypassed.
        if not bypass_cache:
            cached_result = _get_cached_lineage(product_name)
            if cached_result is not None:
                return cached_result

        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()

            # Known sativa hybrid strains - override database lineage if it's just "HYBRID"
            KNOWN_SATIVA_HYBRIDS = {
                'blue dream', 'blue dream haze', 'blueberry dream', 'dream', 'dream star',
                'sour diesel', 'sour d', 'green crack', 'green crack haze',
                'jack herer', 'jack', 'super silver haze', 'silver haze',
                'durban poison', 'durban', 'trainwreck', 'train wreck',
                'amnesia haze', 'amnesia', 'strawberry cough', 'strawberry',
                'white widow', 'white', 'ak-47', 'ak47', 'ak 47',
                'purple haze', 'haze', 'lemon haze', 'lemon',
                'pineapple express', 'pineapple', 'maui wowie', 'maui',
                'chocolope', 'chocolate', 'tangie', 'tangerine dream',
                'cannatonic', 'harlequin', 'acdc', 'ac/dc', 'pennywise'
            }
            
            # CRITICAL FIX: Use case-insensitive and whitespace-insensitive matching
            # This ensures updates are found even with minor formatting differences
            product_name_norm = str(product_name).strip() if product_name else ""
            if not product_name_norm:
                logger.debug(f"No product name provided for lineage lookup")
                return None
            
            # Try exact match first (fastest) - also get strain for sativa hybrid check
            # Strains-sheet lineage path: never fall back to products."Lineage" here.
            # Priority: product.sovereign_lineage > strain.sovereign_lineage > strain.canonical_lineage
            cursor.execute('''
                SELECT COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage) as lineage,
                       p."Product Strain"
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p."Product Name*" = ? OR p."ProductName" = ?
                ORDER BY p.id DESC
                LIMIT 1
            ''', (product_name_norm, product_name_norm))
            
            result = cursor.fetchone()
            if result and result[0] and str(result[0]).strip():
                lineage = str(result[0]).strip()
                product_strain = result[1] if len(result) > 1 and result[1] else None
                
                # CRITICAL FIX: Apply sativa hybrid override if product has a known sativa hybrid strain or name
                is_known_sativa_hybrid = False
                if product_strain and str(product_strain).strip():
                    normalized_strain = self._normalize_strain_name(str(product_strain).strip())
                    is_known_sativa_hybrid = normalized_strain in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized_strain for known in KNOWN_SATIVA_HYBRIDS
                    )
                # Also check product name itself (e.g., "Blue Dream Super Sale")
                if not is_known_sativa_hybrid:
                    normalized_product_name = self._normalize_strain_name(product_name_norm)
                    is_known_sativa_hybrid = normalized_product_name in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized_product_name for known in KNOWN_SATIVA_HYBRIDS
                    )
                
                if is_known_sativa_hybrid and str(lineage).strip().upper() == 'HYBRID':
                    strain_display = product_strain or 'N/A'
                    logger.info(f"🌿 SATIVA HYBRID OVERRIDE (product): '{product_name}' (strain: '{strain_display}') - Overriding 'HYBRID' to 'HYBRID/SATIVA'")
                    _set_cached_lineage(product_name, 'HYBRID/SATIVA')
                    return 'HYBRID/SATIVA'

                logger.debug(f"✅ Found product lineage (exact match) for '{product_name}': '{lineage}'")
                _set_cached_lineage(product_name, lineage)
                return lineage
            
            # Fallback: Case-insensitive and whitespace-insensitive match
            # Strains-sheet lineage path: never fall back to products."Lineage" here.
            # Priority: product.sovereign_lineage > strain.sovereign_lineage > strain.canonical_lineage
            cursor.execute('''
                SELECT COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage) as lineage,
                       p."Product Strain"
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE TRIM(LOWER(p."Product Name*")) = TRIM(LOWER(?))
                   OR TRIM(LOWER(p."ProductName")) = TRIM(LOWER(?))
                ORDER BY p.id DESC
                LIMIT 1
            ''', (product_name_norm, product_name_norm))
            
            result = cursor.fetchone()
            if result and result[0] and str(result[0]).strip():
                lineage = str(result[0]).strip()
                product_strain = result[1] if len(result) > 1 and result[1] else None
                
                # CRITICAL FIX: Apply sativa hybrid override
                if product_strain and str(product_strain).strip():
                    normalized_strain = self._normalize_strain_name(str(product_strain).strip())
                    is_known_sativa_hybrid = normalized_strain in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized_strain for known in KNOWN_SATIVA_HYBRIDS
                    )
                    if is_known_sativa_hybrid and str(lineage).strip().upper() == 'HYBRID':
                        logger.info(f"🌿 SATIVA HYBRID OVERRIDE (product): '{product_name}' (strain: '{product_strain}') - Overriding 'HYBRID' to 'HYBRID/SATIVA'")
                        _set_cached_lineage(product_name, 'HYBRID/SATIVA')
                        return 'HYBRID/SATIVA'

                logger.debug(f"✅ Found product lineage (case-insensitive match) for '{product_name}': '{lineage}'")
                _set_cached_lineage(product_name, lineage)
                return lineage
            
            # Last resort: Partial match (in case product name has extra characters)
            # Strains-sheet lineage path: never fall back to products."Lineage" here.
            # Priority: product.sovereign_lineage > strain.sovereign_lineage > strain.canonical_lineage
            cursor.execute('''
                SELECT COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage) as lineage,
                       p."Product Strain"
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p."Product Name*" LIKE ? OR p."ProductName" LIKE ?
                ORDER BY p.id DESC
                LIMIT 1
            ''', (f'%{product_name_norm}%', f'%{product_name_norm}%'))
            
            result = cursor.fetchone()
            if result and result[0] and str(result[0]).strip():
                lineage = str(result[0]).strip()
                product_strain = result[1] if len(result) > 1 and result[1] else None
                
                # CRITICAL FIX: Apply sativa hybrid override
                if product_strain and str(product_strain).strip():
                    normalized_strain = self._normalize_strain_name(str(product_strain).strip())
                    is_known_sativa_hybrid = normalized_strain in KNOWN_SATIVA_HYBRIDS or any(
                        known in normalized_strain for known in KNOWN_SATIVA_HYBRIDS
                    )
                    if is_known_sativa_hybrid and str(lineage).strip().upper() == 'HYBRID':
                        logger.info(f"🌿 SATIVA HYBRID OVERRIDE (product): '{product_name}' (strain: '{product_strain}') - Overriding 'HYBRID' to 'HYBRID/SATIVA'")
                        _set_cached_lineage(product_name, 'HYBRID/SATIVA')
                        return 'HYBRID/SATIVA'

                logger.debug(f"✅ Found product lineage (partial match) for '{product_name}': '{lineage}'")
                _set_cached_lineage(product_name, lineage)
                return lineage

            logger.debug(f"⚠️  No lineage found for product '{product_name}' (tried exact, case-insensitive, and partial match)")
            _set_cached_lineage(product_name, None)  # Cache negative results too
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting product lineage for '{product_name}': {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def get_vendor_strain_lineage(self, strain_name: str, vendor: str = None, brand: str = None) -> Optional[str]:
        """Get vendor-specific lineage for a strain, with fallback to canonical lineage."""
        try:
            self.init_database()
            
            # First, try to get vendor/brand-specific lineage
            if vendor and brand:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Check strain_brand_lineage table first (most specific)
                cursor.execute('''
                    SELECT lineage FROM strain_brand_lineage 
                    WHERE strain_name = ? AND brand = ?
                ''', (strain_name, brand))
                
                result = cursor.fetchone()
                if result:
                    logger.debug(f"Found vendor-specific lineage for {strain_name} + {brand}: {result[0]}")
                    return result[0]
                
                # Check products table for vendor/brand combination
                # CRITICAL FIX: Join with strains and prioritize sovereign_lineage
                normalized_strain = self._normalize_strain_name(strain_name)
                cursor.execute('''
                    SELECT COALESCE(s.sovereign_lineage, s.canonical_lineage, p."Lineage") as lineage
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE LOWER(TRIM(COALESCE(p."Product Strain", ''))) = ?
                      AND p."Vendor/Supplier*" = ? AND p."Product Brand" = ?
                    ORDER BY p.id DESC
                    LIMIT 1
                ''', (normalized_strain, vendor, brand))
                
                result = cursor.fetchone()
                if result and result[0]:
                    logger.debug(f"Found product-specific lineage for {strain_name} + {vendor} + {brand}: {result[0]}")
                    return result[0]
            
            # Fallback to strain lineage from strains table (prioritizes sovereign_lineage)
            strain_info = self.get_strain_info(strain_name)
            if strain_info:
                # CRITICAL FIX: Use display_lineage which prioritizes sovereign_lineage over canonical
                lineage = strain_info.get('display_lineage') or strain_info.get('canonical_lineage')
                if lineage:
                    logger.debug(f"Using strain lineage for {strain_name}: {lineage}")
                    return lineage
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vendor strain lineage for '{strain_name}': {e}")
            return None

    def get_vendor_strain_statistics(self) -> Dict[str, Any]:
        """Get statistics about vendor-specific strain lineages."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get vendor-specific lineage counts
            cursor.execute('''
                SELECT brand, COUNT(*) as count, 
                       GROUP_CONCAT(DISTINCT lineage) as lineages
                FROM strain_brand_lineage 
                GROUP BY brand
                ORDER BY count DESC
            ''')
            
            vendor_stats = []
            for row in cursor.fetchall():
                brand, count, lineages = row
                vendor_stats.append({
                    'brand': brand,
                    'strain_count': count,
                    'lineages': lineages.split(',') if lineages else []
                })
            
            # Get strain diversity by vendor
            cursor.execute('''
                SELECT p.vendor, p.brand, s.strain_name, p.lineage
                FROM products p
                JOIN strains s ON p.strain_id = s.id
                WHERE p.lineage IS NOT NULL AND p.lineage != ''
                ORDER BY p.vendor, p.brand, s.strain_name
            ''')
            
            vendor_strains = {}
            for row in cursor.fetchall():
                vendor, brand, strain, lineage = row
                key = f"{vendor} - {brand}" if vendor and brand else (vendor or brand or "Unknown")
                if key not in vendor_strains:
                    vendor_strains[key] = {}
                if strain not in vendor_strains[key]:
                    vendor_strains[key][strain] = set()
                vendor_strains[key][strain].add(lineage)
            
            # Find strains with different lineages across vendors
            strain_vendor_conflicts = {}
            for vendor_key, strains in vendor_strains.items():
                for strain, lineages in strains.items():
                    if len(lineages) > 1:
                        if strain not in strain_vendor_conflicts:
                            strain_vendor_conflicts[strain] = {}
                        strain_vendor_conflicts[strain][vendor_key] = list(lineages)
            
            return {
                'vendor_stats': vendor_stats,
                'vendor_strains': vendor_strains,
                'strain_vendor_conflicts': strain_vendor_conflicts,
                'total_vendors': len(vendor_stats),
                'conflicting_strains': len(strain_vendor_conflicts)
            }
            
        except Exception as e:
            logger.error(f"Error getting vendor strain statistics: {e}")
            return {}

    def update_product_doh(self, product_name: str, new_doh: str, vendor: str = None, brand: str = None) -> bool:
        """Update the DOH status for a product in the database. Aggressively overwrites all matching products."""
        try:
            self.init_database()
            normalized_name = self._normalize_product_name(product_name)
            conn = self._get_connection()
            cursor = conn.cursor()
            current_date = datetime.now().isoformat()
            
            # Strategy 1: Most specific match (vendor + brand + normalized name)
            if vendor and brand:
                cursor.execute('''
                    UPDATE products
                    SET "DOH" = ?, "DOH Compliant (Yes/No)" = ?, updated_at = ?
                    WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Brand" = ?
                ''', (new_doh, new_doh, current_date, normalized_name, vendor, brand))
                rows_updated = cursor.rowcount
                if rows_updated > 0:
                    logger.info(f"✅ DOH UPDATE: Updated {rows_updated} product(s) matching '{product_name}' (vendor={vendor}, brand={brand}) → '{new_doh}'")
            
            # Strategy 2: Fallback to normalized name match (overwrite all variants)
            if cursor.rowcount == 0 or not (vendor and brand):
                cursor.execute('''
                    UPDATE products
                    SET "DOH" = ?, "DOH Compliant (Yes/No)" = ?, updated_at = ?
                    WHERE normalized_name = ?
                ''', (new_doh, new_doh, current_date, normalized_name))
                rows_updated = cursor.rowcount
                if rows_updated > 0:
                    logger.info(f"✅ DOH UPDATE: Updated {rows_updated} product(s) matching normalized name '{normalized_name}' → '{new_doh}'")
            
            # Strategy 3: Fallback to exact product name match (case-insensitive)
            if rows_updated == 0:
                cursor.execute('''
                    UPDATE products
                    SET "DOH" = ?, "DOH Compliant (Yes/No)" = ?, updated_at = ?
                    WHERE UPPER("Product Name*") = UPPER(?)
                ''', (new_doh, new_doh, current_date, product_name))
                rows_updated = cursor.rowcount
                if rows_updated > 0:
                    logger.info(f"✅ DOH UPDATE: Updated {rows_updated} product(s) matching exact name '{product_name}' → '{new_doh}'")
            
            conn.commit()
            
            if rows_updated == 0:
                logger.warning(f"⚠️ DOH UPDATE: No product found in database to update DOH: '{product_name}' (vendor={vendor}, brand={brand})")
            
            return rows_updated > 0
        except Exception as e:
            logger.error(f"Error updating product DOH for '{product_name}': {e}")
            return False

    def upsert_strain_vendor_lineage(self, strain_name: str, vendor: str, brand: str, lineage: str):
        """Insert or update lineage for a (strain_name, vendor, brand) combination."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # First, ensure the strain exists in the strains table
            strain_id = self.add_or_update_strain(strain_name, lineage)
            
            # Update or insert in products table with vendor/brand specificity
            cursor.execute('''
                INSERT INTO products (
                    product_name, normalized_name, strain_id, product_type, vendor, brand,
                    lineage, first_seen_date, last_seen_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(product_name, vendor, brand) DO UPDATE SET 
                    lineage = excluded.lineage, 
                    last_seen_date = excluded.last_seen_date,
                    updated_at = excluded.updated_at
            ''', (
                strain_name, self._normalize_product_name(strain_name), strain_id,
                'Unknown', vendor, brand, lineage, now, now, now, now
            ))
            
            # Also update strain_brand_lineage for brand-specific overrides
            cursor.execute('''
                INSERT INTO strain_brand_lineage (strain_name, brand, lineage, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(strain_name, brand) DO UPDATE SET 
                    lineage = excluded.lineage, 
                    updated_at = excluded.updated_at
            ''', (strain_name, brand, lineage, now, now))
            
            conn.commit()
            logger.info(f"Upserted vendor-specific lineage: {strain_name} + {vendor} + {brand} = {lineage}")
            
        except Exception as e:
            logger.error(f"Error upserting strain vendor lineage: {e}")
            raise 

    def get_strain_with_products_info(self, strain_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive strain information including all associated products with brand, weight, vendor, and price data."""
        try:
            self.init_database()
            normalized_name = self._normalize_strain_name(strain_name)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get strain basic info
            cursor.execute('''
                SELECT id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, 
                       first_seen_date, last_seen_date, sovereign_lineage
                FROM strains 
                WHERE normalized_name = ?
            ''', (normalized_name,))
            
            strain_result = cursor.fetchone()
            if not strain_result:
                return None
                
            strain_id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, first_seen_date, last_seen_date, sovereign_lineage = strain_result
            
            # Get all products associated with this strain
            cursor.execute('''
                SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Description", "Weight*", "Units", "Price", "Lineage",
                       total_occurrences, first_seen_date, last_seen_date
                FROM products 
                WHERE strain_id = ?
                ORDER BY total_occurrences DESC
            ''', (strain_id,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'product_name': row[0],
                    'product_type': row[1],
                    'vendor': row[2],
                    'brand': row[3],
                    'description': row[4],
                    'weight': row[5],
                    'units': row[6],
                    'price': row[7],
                    'lineage': row[8],
                    'total_occurrences': row[9],
                    'first_seen_date': row[10],
                    'last_seen_date': row[11]
                })
            
            # Get brand-specific lineage overrides
            cursor.execute('''
                SELECT brand, lineage FROM strain_brand_lineage 
                WHERE strain_name = ?
                ORDER BY brand
            ''', (strain_name,))
            
            brand_lineages = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Calculate aggregated information
            brands = list(set(p['brand'] for p in products if p['brand']))
            vendors = list(set(p['vendor'] for p in products if p['vendor']))
            weights = list(set(p['weight'] for p in products if p['weight']))
            units = list(set(p['units'] for p in products if p['units']))
            
            # Get most common values
            brand_counts = {}
            vendor_counts = {}
            weight_counts = {}
            price_counts = {}
            
            for product in products:
                if product['brand']:
                    brand_counts[product['brand']] = brand_counts.get(product['brand'], 0) + product['total_occurrences']
                if product['vendor']:
                    vendor_counts[product['vendor']] = vendor_counts.get(product['vendor'], 0) + product['total_occurrences']
                if product['weight']:
                    weight_counts[product['weight']] = weight_counts.get(product['weight'], 0) + product['total_occurrences']
                if product['price']:
                    price_counts[product['price']] = price_counts.get(product['price'], 0) + product['total_occurrences']
            
            most_common_brand = max(brand_counts.items(), key=lambda x: x[1])[0] if brand_counts else None
            most_common_vendor = max(vendor_counts.items(), key=lambda x: x[1])[0] if vendor_counts else None
            most_common_weight = max(weight_counts.items(), key=lambda x: x[1])[0] if weight_counts else None
            most_common_price = max(price_counts.items(), key=lambda x: x[1])[0] if price_counts else None
            
            # Determine display lineage (sovereign > mode > canonical)
            display_lineage = None
            if sovereign_lineage and sovereign_lineage.strip():
                display_lineage = sovereign_lineage
            else:
                mode_lineage = self.get_mode_lineage(strain_id)
                if mode_lineage:
                    display_lineage = mode_lineage
                else:
                    display_lineage = canonical_lineage
            
            return {
                'strain_info': {
                    'id': strain_id,
                    'strain_name': strain_name,
                    'canonical_lineage': canonical_lineage,
                    'display_lineage': display_lineage,
                    'sovereign_lineage': sovereign_lineage,
                    'total_occurrences': total_occurrences,
                    'lineage_confidence': lineage_confidence,
                    'first_seen_date': first_seen_date,
                    'last_seen_date': last_seen_date
                },
                'products': products,
                'brand_lineages': brand_lineages,
                'aggregated_info': {
                    'brands': brands,
                    'vendors': vendors,
                    'weights': weights,
                    'units': units,
                    'most_common_brand': most_common_brand,
                    'most_common_vendor': most_common_vendor,
                    'most_common_weight': most_common_weight,
                    'most_common_price': most_common_price,
                    'total_products': len(products)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting strain with products info for '{strain_name}': {e}")
            return None

    def get_strain_brand_info(self, strain_name: str, brand: str = None) -> Optional[Dict[str, Any]]:
        """Get strain information with specific brand context, including weight, vendor, and price data."""
        try:
            self.init_database()
            normalized_name = self._normalize_strain_name(strain_name)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get strain basic info
            cursor.execute('''
                SELECT id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, 
                       first_seen_date, last_seen_date, sovereign_lineage
                FROM strains 
                WHERE normalized_name = ?
            ''', (normalized_name,))
            
            strain_result = cursor.fetchone()
            if not strain_result:
                return None
                
            strain_id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, first_seen_date, last_seen_date, sovereign_lineage = strain_result
            
            # Get products for this strain with optional brand filter
            if brand:
                cursor.execute('''
                    SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Description", "Weight*", "Units", "Price", "Lineage",
                           total_occurrences, first_seen_date, last_seen_date
                    FROM products 
                    WHERE strain_id = ? AND "Product Brand" = ?
                    ORDER BY total_occurrences DESC
                ''', (strain_id, brand))
            else:
                cursor.execute('''
                    SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Description", "Weight*", "Units", "Price", "Lineage",
                           total_occurrences, first_seen_date, last_seen_date
                    FROM products 
                    WHERE strain_id = ?
                    ORDER BY total_occurrences DESC
                ''', (strain_id,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'product_name': row[0],
                    'product_type': row[1],
                    'vendor': row[2],
                    'brand': row[3],
                    'description': row[4],
                    'weight': row[5],
                    'units': row[6],
                    'price': row[7],
                    'lineage': row[8],
                    'total_occurrences': row[9],
                    'first_seen_date': row[10],
                    'last_seen_date': row[11]
                })
            
            # Get brand-specific lineage
            brand_lineage = None
            if brand:
                cursor.execute('''
                    SELECT lineage FROM strain_brand_lineage 
                    WHERE strain_name = ? AND brand = ?
                ''', (strain_name, brand))
                result = cursor.fetchone()
                if result:
                    brand_lineage = result[0]
            
            # Determine display lineage (brand-specific > sovereign > mode > canonical)
            display_lineage = None
            if brand_lineage:
                display_lineage = brand_lineage
            elif sovereign_lineage and sovereign_lineage.strip():
                display_lineage = sovereign_lineage
            else:
                mode_lineage = self.get_mode_lineage(strain_id)
                if mode_lineage:
                    display_lineage = mode_lineage
                else:
                    display_lineage = canonical_lineage
            
            # Aggregate product information
            if products:
                weights = list(set(p['weight'] for p in products if p['weight']))
                units = list(set(p['units'] for p in products if p['units']))
                vendors = list(set(p['vendor'] for p in products if p['vendor']))
                prices = list(set(p['price'] for p in products if p['price']))
                
                # Get most common values
                weight_counts = {}
                price_counts = {}
                vendor_counts = {}
                
                for product in products:
                    if product['weight']:
                        weight_counts[product['weight']] = weight_counts.get(product['weight'], 0) + product['total_occurrences']
                    if product['price']:
                        price_counts[product['price']] = price_counts.get(product['price'], 0) + product['total_occurrences']
                    if product['vendor']:
                        vendor_counts[product['vendor']] = vendor_counts.get(product['vendor'], 0) + product['total_occurrences']
                
                most_common_weight = max(weight_counts.items(), key=lambda x: x[1])[0] if weight_counts else None
                most_common_price = max(price_counts.items(), key=lambda x: x[1])[0] if price_counts else None
                most_common_vendor = max(vendor_counts.items(), key=lambda x: x[1])[0] if vendor_counts else None
            else:
                weights = units = vendors = prices = []
                most_common_weight = most_common_price = most_common_vendor = None
            
            return {
                'strain_name': strain_name,
                'canonical_lineage': canonical_lineage,
                'display_lineage': display_lineage,
                'brand_lineage': brand_lineage,
                'sovereign_lineage': sovereign_lineage,
                'total_occurrences': total_occurrences,
                'lineage_confidence': lineage_confidence,
                'products': products,
                'aggregated_info': {
                    'weights': weights,
                    'units': units,
                    'vendors': vendors,
                    'prices': prices,
                    'most_common_weight': most_common_weight,
                    'most_common_price': most_common_price,
                    'most_common_vendor': most_common_vendor,
                    'total_products': len(products)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting strain brand info for '{strain_name}' (brand: {brand}): {e}")
            return None

    def get_strains_with_brand_info(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get a list of strains with their associated brand, weight, vendor, and price information."""
        try:
            self.init_database()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get strains with their most common associated information
            cursor.execute('''
                SELECT s.strain_name, s.canonical_lineage, s.total_occurrences, s.sovereign_lineage,
                       p.brand, p.vendor, p.weight, p.units, p.price, p.lineage
                FROM strains s
                LEFT JOIN products p ON s.id = p.strain_id
                WHERE p.id = (
                    SELECT p2.id FROM products p2 
                    WHERE p2.strain_id = s.id 
                    ORDER BY p2.total_occurrences DESC 
                    LIMIT 1
                )
                ORDER BY s.total_occurrences DESC
                LIMIT ?
            ''', (limit,))
            
            strains = []
            for row in cursor.fetchall():
                strain_name, canonical_lineage, total_occurrences, sovereign_lineage, brand, vendor, weight, units, price, lineage = row
                
                # Get brand-specific lineage
                cursor.execute('''
                    SELECT lineage FROM strain_brand_lineage 
                    WHERE strain_name = ? AND brand = ?
                ''', (strain_name, brand))
                brand_lineage_result = cursor.fetchone()
                brand_lineage = brand_lineage_result[0] if brand_lineage_result else None
                
                # Determine display lineage
                display_lineage = None
                if brand_lineage:
                    display_lineage = brand_lineage
                elif sovereign_lineage and sovereign_lineage.strip():
                    display_lineage = sovereign_lineage
                else:
                    display_lineage = canonical_lineage
                
                strains.append({
                    'strain_name': strain_name,
                    'canonical_lineage': canonical_lineage,
                    'display_lineage': display_lineage,
                    'brand_lineage': brand_lineage,
                    'sovereign_lineage': sovereign_lineage,
                    'total_occurrences': total_occurrences,
                    'brand': brand,
                    'vendor': vendor,
                    'weight': weight,
                    'units': units,
                    'price': price,
                    'lineage': lineage
                })
            
            return strains
            
        except Exception as e:
            logger.error(f"Error getting strains with brand info: {e}")
            return []

    def add_missing_columns(self):
        """Public method to add missing columns to existing database tables."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            self._add_missing_columns_safe(cursor, conn)
            logger.info("Missing columns check completed")
        except Exception as e:
            logger.error(f"Error adding missing columns: {e}")
            raise

    @timed_operation("get_products_by_names")
    def get_products_by_names(self, product_names: List[str]) -> List[Dict[str, Any]]:
        """Get information about multiple products by their names (with caching)."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            if not product_names:
                return []
            
            # Normalize all product names
            normalized_names = [self._normalize_product_name(name) for name in product_names]
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Use placeholders for the IN clause
            placeholders = ','.join(['?' for _ in normalized_names])
            
            # One row per normalized_name (latest by id) to avoid redundant DB rows slowing tag load
            cursor.execute(f'''
                SELECT id, "Product Name*", normalized_name, "Product Type*", "Vendor/Supplier*", "Product Brand", "Lineage",
                       "Product Strain" as strain_name, "Lineage" as canonical_lineage, sovereign_lineage, total_occurrences, first_seen_date, last_seen_date,
                       "Description", "Weight*", "Units", "Price", 
                       "THC test result", "CBD test result", "Test result unit (% or mg)",
                       "Quantity*", "DOH", "Concentrate Type", "Ratio", "JointRatio", "State", "Is Sample? (yes/no)",
                       "Is MJ product?(yes/no)", "Discountable? (yes/no)", "Room*", "Batch Number", "Lot Number", "Barcode*",
                       "Medical Only (Yes/No)", "Med Price", "Expiration Date(YYYY-MM-DD)", "Is Archived? (yes/no)", "THC Per Serving", "Allergens",
                       "Solvent", "Accepted Date", "Internal Product Identifier", "Product Tags (comma separated)", "Image URL", "Ingredients",
                       "CombinedWeight", "Ratio_or_THC_CBD", "Description_Complexity", "Total THC", "THCA", "CBDA", "CBN"
                FROM products
                WHERE normalized_name IN ({placeholders})
                  AND id IN (SELECT MAX(id) FROM products WHERE normalized_name IN ({placeholders}) GROUP BY normalized_name)
            ''', normalized_names + normalized_names)
            
            results = cursor.fetchall()
            
            # Create a mapping from normalized names to results
            products_map = {}
            for result in results:
                normalized_name = result[2]  # normalized_name column
                if normalized_name not in products_map:
                    products_map[normalized_name] = []
                products_map[normalized_name].append(result)
            
            # Build the final list maintaining the order of requested product names
            products = []
            for i, product_name in enumerate(product_names):
                normalized_name = normalized_names[i]
                if normalized_name in products_map:
                    # Use the first result for each product (or could implement logic to choose best match)
                    result = products_map[normalized_name][0]
                    
                    product_info = {
                        'id': result[0],
                        'ProductName': result[1],  # product_name
                        'Product Name*': result[1],  # Excel column name compatibility
                        'normalized_name': result[2],
                        'Product Type*': result[3],  # product_type
                        'Vendor': result[4],  # vendor
                        'Vendor/Supplier*': result[4],  # Excel column name compatibility
                        'Product Brand': result[5],  # brand
                        # CRITICAL: Prioritize sovereign_lineage (manual overrides) over regular Lineage
                        'sovereign_lineage': result[9],  # CRITICAL: sovereign_lineage contains manual tag manager edits
                        'Lineage': (result[9] if result[9] and str(result[9]).strip() not in ['', 'None', 'nan'] else result[6]) or 'MIXED',  # Use sovereign_lineage if available, otherwise use Lineage
                        'Product Strain': result[7],  # strain_name from Product Strain column
                        'strain_name': result[7],  # strain_name from Product Strain column
                        'canonical_lineage': (result[9] if result[9] and str(result[9]).strip() not in ['', 'None', 'nan'] else result[8]),  # Use sovereign_lineage if available, otherwise use Lineage
                        'total_occurrences': result[10],
                        'first_seen_date': result[11],
                        'last_seen_date': result[12],
                        'Description': result[13] or result[1],  # description or product_name
                        'Weight*': result[14],  # weight
                        'Units': result[15],  # units
                        'Price': result[16],  # price
                        'THC test result': result[17],  # thc_test_result
                        'CBD test result': result[18],  # cbd_test_result
                        'Test result unit (% or mg)': result[19],  # test_result_unit with correct field name
                        'Quantity*': result[20],  # quantity
                        'DOH': result[21],  # doh_compliant
                        'Concentrate Type': result[22],  # concentrate_type with correct field name
                        'Ratio': result[23],  # ratio
                        'JointRatio': result[24],  # joint_ratio
                        'State': result[25],  # state
                        'Is Sample? (yes/no)': result[26],  # is_sample with correct field name
                        'Is MJ product?(yes/no)': result[27],  # is_mj_product with correct field name
                        'Discountable? (yes/no)': result[28],  # discountable with correct field name
                        'Room*': result[29],  # room
                        'Batch Number': result[30],  # batch_number with correct field name
                        'Lot Number': result[31],  # lot_number with correct field name
                        'Barcode*': result[32],  # barcode with correct field name
                        'Medical Only (Yes/No)': result[33],  # medical_only with correct field name
                        'Med Price': result[34],  # med_price with correct field name
                        'Expiration Date(YYYY-MM-DD)': result[35],  # expiration_date with correct field name
                        'Is Archived? (yes/no)': result[36],  # is_archived with correct field name
                        'THC Per Serving': result[37],  # thc_per_serving with correct field name
                        'Allergens': result[38],  # allergens with correct field name
                        'Solvent': result[39],  # solvent with correct field name
                        'Accepted Date': result[40],  # accepted_date with correct field name
                        'Internal Product Identifier': result[41],  # internal_product_identifier with correct field name
                        'Product Tags (comma separated)': result[42],  # product_tags with correct field name
                        'Image URL': result[43],  # image_url with correct field name
                        'Ingredients': result[44],  # ingredients with correct field name
                        'CombinedWeight': result[45],  # combined_weight with correct field name
                        'Ratio_or_THC_CBD': result[46],  # ratio_or_thc_cbd with correct field name
                        'Description_Complexity': result[47],  # description_complexity with correct field name
                        'Total THC': result[48],  # total_thc
                        'THCA': result[49],  # thca
                        'CBDA': result[50],  # cbda
                        'CBN': result[51],  # cbn
                        # Add Excel column name compatibility fields
                        'ProductBrand': result[5],
                        'ProductStrain': result[7],
                        'WeightWithUnits': f"{result[14]}{result[15]}" if result[14] and result[15] else result[14] or result[15] or '',
                        'displayName': result[1]  # For frontend compatibility
                    }
                    
                    products.append(product_info)
                else:
                    # Product not found in database, create a placeholder
                    logger.warning(f"Product '{product_name}' not found in database")
                    products.append({
                        'ProductName': product_name,
                        'Product Name*': product_name,
                        'Description': product_name,
                        'Vendor': '',
                        'Vendor/Supplier*': '',
                        'Product Brand': '',
                        'Lineage': 'MIXED',
                        'Product Type*': '',
                        'Weight*': '',
                        'Units': '',
                        'Price': '',
                        'displayName': product_name
                    })
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting products by names: {e}")
            return []

    def get_products_by_names_fuzzy(self, product_names: List[str]) -> List[Dict[str, Any]]:
        """Get products by their names with fuzzy matching for better name variations."""
        try:
            if not product_names:
                return []
            
            # First try exact matches
            exact_matches = self.get_products_by_names(product_names)
            
            # Check if exact matches have vendor/brand information
            has_vendor_brand_info = all(
                product.get('Vendor/Supplier*', '').strip() and 
                product.get('Product Brand', '').strip()
                for product in exact_matches
            )
            
            # If we found all products AND they have vendor/brand info, return them
            if len(exact_matches) == len(product_names) and has_vendor_brand_info:
                return exact_matches
            
            # If we didn't find all products, try fuzzy matching
            logger.info(f"Found {len(exact_matches)} exact matches, trying fuzzy matching for remaining products")
            
            # Get all products for fuzzy matching
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY "Product Name*"')
            all_rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            all_products = [dict(zip(columns, row)) for row in all_rows]
            
            # Find fuzzy matches for all products (since exact matches may not have vendor/brand info)
            found_products = []
            found_names = set()
            
            for search_name in product_names:
                # PERFORMANCE: Check cache first
                cached_result = _get_cached_fuzzy_match(search_name)
                if cached_result is not None:
                    if cached_result:  # Non-empty result
                        found_products.append(cached_result)
                        found_names.add(search_name)
                    continue

                # Try fuzzy matching for this search name
                best_match = None
                best_score = 0
                candidates = []

                for product in all_products:
                    product_name = product.get('Product Name*', '')
                    if not product_name:
                        continue

                    # Calculate similarity score
                    score = self._calculate_name_similarity(search_name, product_name)

                    if score > 0.3:  # 30% similarity threshold
                        candidates.append((product, score))
                
                # Sort candidates by score (highest first), then prioritize records with processed descriptions
                # (shorter descriptions are more likely to be processed)
                candidates.sort(key=lambda x: (
                    x[1],  # Score (highest first)
                    -len(x[0].get('Description', '')),  # Shorter descriptions first (negative for reverse)
                    x[0].get('Product Name*', '')  # Product name for consistency
                ), reverse=True)
                
                if candidates:
                    best_match, best_score = candidates[0]
                
                if best_match:
                    logger.info(f"Fuzzy match: '{search_name}' -> '{best_match.get('Product Name*', '')}' (score: {best_score:.2f})")
                    # Convert to the same format as get_products_by_names
                    converted_match = self._convert_product_to_standard_format(best_match)
                    found_products.append(converted_match)
                    found_names.add(search_name)
                    # PERFORMANCE: Cache the result
                    _set_cached_fuzzy_match(search_name, converted_match)
                else:
                    logger.warning(f"No fuzzy match found for: '{search_name}'")
                    # If no fuzzy match found, use exact match if available
                    exact_match = next((p for p in exact_matches if p.get('Product Name*') == search_name), None)
                    if exact_match:
                        found_products.append(exact_match)
                        found_names.add(search_name)
                        # PERFORMANCE: Cache the exact match result
                        _set_cached_fuzzy_match(search_name, exact_match)
                    else:
                        # PERFORMANCE: Cache negative result
                        _set_cached_fuzzy_match(search_name, {})
            
            logger.info(f"Found {len(found_products)} total products (exact + fuzzy) for: {product_names}")
            return found_products
            
        except Exception as e:
            logger.error(f"Error getting products by names with fuzzy matching: {e}")
            return []

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two product names with improved matching."""
        try:
            # Normalize names for comparison
            def normalize(name):
                return ' '.join(name.lower().split())
            
            norm1 = normalize(name1)
            norm2 = normalize(name2)
            
            # Check for exact match after normalization
            if norm1 == norm2:
                return 1.0
            
            # Check for substring matches
            if norm1 in norm2 or norm2 in norm1:
                return 0.9
            
            # Extract key components for better matching
            def extract_components(name):
                # Remove common prefixes and suffixes
                cleaned = name.lower()
                # Remove common cannabis terms for better matching
                cannabis_terms = ['flower', 'wax', 'pre-roll', 'cartridge', 'distillate', 'concentrate', 'edible', 'gummy', 'chocolate', 'beverage', 'topical', 'cream', 'lotion', 'salve', 'balm', 'spray', 'drops', 'syrup', 'sauce', 'dab', 'shatter', 'live', 'rosin', 'resin', 'kief', 'hash', 'bubble', 'ice', 'water', 'solventless', 'full', 'spectrum', 'broad', 'isolate', 'terpene', 'terpenes', 'terp', 'terps']
                
                for term in cannabis_terms:
                    cleaned = cleaned.replace(term, '')
                
                # Remove common weight indicators
                weight_terms = ['28g', '3.5g', '1g', '7g', '14g', '28g', '1oz', '0.5g', '2g', '4g', '8g', '16g', '32g']
                for term in weight_terms:
                    cleaned = cleaned.replace(term, '')
                
                # Remove common separators and clean up
                cleaned = cleaned.replace('(', '').replace(')', '').replace('-', ' ').replace('/', ' ').replace(' by ', ' ').replace('  ', ' ').strip()
                
                return cleaned.split()
            
            comp1 = extract_components(norm1)
            comp2 = extract_components(norm2)
            
            if not comp1 or not comp2:
                return 0.0
            
            # Calculate similarity based on key components
            set1 = set(comp1)
            set2 = set(comp2)
            
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            
            jaccard_score = len(intersection) / len(union) if union else 0.0
            
            # Boost score for strain name matches (most important)
            strain_boost = 0.0
            for comp in comp1:
                if comp in comp2 and len(comp) > 2:  # Avoid single character matches
                    strain_boost += 0.2
            
            # Boost score for brand name matches
            brand_boost = 0.0
            brand_terms = ['hustler', 'ambition', 'mama', 'j\'s', 'blue', 'roots', 'cannabis']
            for term in brand_terms:
                if term in norm1 and term in norm2:
                    brand_boost += 0.1
            
            # Prioritize exact strain name matches
            exact_strain_boost = 0.0
            
            # Check if the strain name components are the same (ignoring order)
            set1 = set(comp1)
            set2 = set(comp2)
            
            # If all components match, it's likely the same strain
            if set1 == set2:
                exact_strain_boost = 0.5
            # If the strain name components match (excluding brand components)
            elif len(set1.intersection(set2)) >= 2:  # At least 2 common components
                # Check if the strain-specific components match
                strain_components1 = set1 - {'hustler\'s', 'ambition', 'mama', 'j\'s', 'blue', 'roots', 'cannabis'}
                strain_components2 = set2 - {'hustler\'s', 'ambition', 'mama', 'j\'s', 'blue', 'roots', 'cannabis'}
                
                if strain_components1 == strain_components2 and len(strain_components1) > 0:
                    exact_strain_boost = 0.3
            
            final_score = jaccard_score + strain_boost + brand_boost + exact_strain_boost
            
            # Don't cap the score at 1.0 to allow for tie-breaking with boosts
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating name similarity: {e}")
            return 0.0

    def _convert_product_to_standard_format(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a raw database product to the standard format expected by the system."""
        try:
            return {
                'id': product.get('id', ''),
                'ProductName': product.get('Product Name*', ''),
                'Product Name*': product.get('Product Name*', ''),
                'normalized_name': product.get('normalized_name', ''),
                'Product Type*': product.get('Product Type*', ''),
                'Vendor': product.get('Vendor/Supplier*', ''),
                'Vendor/Supplier*': product.get('Vendor/Supplier*', ''),
                'Product Brand': product.get('Product Brand', ''),
                'Lineage': product.get('Lineage', 'MIXED'),
                'strain_name': product.get('Product Strain', ''),
                'canonical_lineage': product.get('Lineage', 'MIXED'),
                'total_occurrences': product.get('total_occurrences', 0),
                'first_seen_date': product.get('first_seen_date', ''),
                'last_seen_date': product.get('last_seen_date', ''),
                'Description': product.get('Description', product.get('Product Name*', '')),
                'Weight*': product.get('Weight*', ''),
                'Units': product.get('Units', ''),
                'Price': product.get('Price', ''),
                'THC test result': product.get('THC test result', ''),
                'CBD test result': product.get('CBD test result', ''),
                'Test result unit': product.get('Test result unit (% or mg)', ''),
                'Quantity*': product.get('Quantity*', ''),
                'DOH': product.get('DOH', ''),
                'concentrate_type': product.get('Concentrate Type', ''),
                'Ratio': product.get('Ratio', ''),
                'JointRatio': product.get('JointRatio', ''),
                'State': product.get('State', ''),
                'Is Sample?': product.get('Is Sample? (yes/no)', ''),
                'Is MJ product?': product.get('Is MJ product?(yes/no)', ''),
                'Discountable?': product.get('Discountable? (yes/no)', ''),
                'Room*': product.get('Room*', ''),
                'batch_number': product.get('Batch Number', ''),
                'lot_number': product.get('Lot Number', ''),
                'barcode': product.get('Barcode*', ''),
                'Medical Only': product.get('Medical Only (Yes/No)', ''),
                'med_price': product.get('Med Price', ''),
                'expiration_date': product.get('Expiration Date(YYYY-MM-DD)', ''),
                'is_archived': product.get('Is Archived? (yes/no)', ''),
                'thc_per_serving': product.get('THC Per Serving', ''),
                'allergens': product.get('Allergens', ''),
                'solvent': product.get('Solvent', ''),
                'accepted_date': product.get('Accepted Date', ''),
                'internal_product_identifier': product.get('Internal Product Identifier', ''),
                'product_tags': product.get('Product Tags (comma separated)', ''),
                'image_url': product.get('Image URL', ''),
                'ingredients': product.get('Ingredients', ''),
                'combined_weight': product.get('CombinedWeight', ''),
                'ratio_or_thc_cbd': product.get('Ratio_or_THC_CBD', ''),
                'description_complexity': product.get('Description_Complexity', ''),
                'Total THC': product.get('Total THC', ''),
                'THCA': product.get('THCA', ''),
                'CBDA': product.get('CBDA', ''),
                'CBN': product.get('CBN', ''),
                # Add Excel column name compatibility fields
                'ProductBrand': product.get('Product Brand', ''),
                'ProductStrain': product.get('Product Strain', ''),
                'WeightWithUnits': f"{product.get('Weight*', '')}{product.get('Units', '')}" if product.get('Weight*') and product.get('Units') else product.get('Weight*', '') or product.get('Units', '') or '',
                'displayName': product.get('Product Name*', '')
            }
        except Exception as e:
            logger.error(f"Error converting product to standard format: {e}")
            return {}

    def find_best_product_match(self, product_name: str, vendor: str = None, product_type: str = None, strain: str = None) -> Optional[Dict[str, Any]]:
        """
        Find the best matching product in the database based on multiple criteria.
        
        Args:
            product_name: The product name to search for
            vendor: The vendor/supplier name
            product_type: The product type/category
            strain: The strain name
            
        Returns:
            Best matching product dictionary or None if no match found
        """
        try:
            self.init_database()  # Ensure DB is initialized
            
            if not product_name:
                return None
            
            # Normalize the product name
            normalized_name = self._normalize_product_name(product_name)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build a flexible search query using the actual column names
            query = '''
                SELECT p.id, p."Product Name*", p."Product Strain", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                       p."Description", p."Weight*", p."Units", p."Price", p."Quantity*", p."DOH", p."Concentrate Type", p."Ratio", p."JointRatio",
                       p."State", p."Is Sample? (yes/no)", p."Is MJ product?(yes/no)", p."Discountable? (yes/no)", p."Room*", p."Batch Number", p."Lot Number", p."Barcode*",
                       p."Medical Only (Yes/No)", p."Med Price", p."Expiration Date(YYYY-MM-DD)", p."Is Archived? (yes/no)", p."THC Per Serving", p."Allergens", p."Solvent", p."Accepted Date",
                       p."Internal Product Identifier", p."Product Tags (comma separated)", p."Image URL", p."Ingredients", p."CombinedWeight", p."Ratio_or_THC_CBD", 
                       p."Description_Complexity", p."Total THC", p."THCA", p."CBDA", p."CBN", 0 as total_occurrences, '' as first_seen_date, '' as last_seen_date
                FROM products p
                WHERE 1=1
            '''
            
            params = []
            
            # Add search conditions with priority using actual column names
            if normalized_name:
                # Create multiple search patterns for better matching
                # 1. Original normalized name
                # 2. Individual words from the name
                # 3. Partial matches
                
                search_patterns = [normalized_name]
                
                # Add individual words for partial matching
                words = normalized_name.split('_')
                search_patterns.extend(words)
                
                # Add space-separated version
                space_name = normalized_name.replace('_', ' ')
                search_patterns.append(space_name)
                search_patterns.extend(space_name.split())
                
                # Build more intelligent search conditions
                # Priority 1: Exact normalized name match
                # Priority 2: Product name contains the full search term
                # Priority 3: Product name contains the space-separated version
                
                pattern_conditions = []
                
                # Exact match (highest priority)
                pattern_conditions.append("p.normalized_name = ?")
                params.append(normalized_name)
                
                # Full search term in product name (high priority)
                pattern_conditions.append("LOWER(p.\"Product Name*\") LIKE ?")
                params.append(f"%{normalized_name.lower()}%")
                
                # Space-separated version in product name
                space_name = normalized_name.replace('_', ' ')
                pattern_conditions.append("LOWER(p.\"Product Name*\") LIKE ?")
                params.append(f"%{space_name.lower()}%")
                
                # Only add individual word matches for very specific cases
                # Only match individual words if they are meaningful (longer than 4 chars) and not common words
                common_words = {'the', 'and', 'or', 'for', 'with', 'by', 'from', 'to', 'of', 'in', 'on', 'at', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
                meaningful_words = [w for w in normalized_name.split('_') if len(w) > 4 and w.lower() not in common_words]
                for word in meaningful_words:
                    pattern_conditions.append("LOWER(p.\"Product Name*\") LIKE ?")
                    params.append(f"%{word.lower()}%")
                
                if pattern_conditions:
                    query += " AND (" + " OR ".join(pattern_conditions) + ")"
            
            # Add product type filtering for better accuracy
            if product_type:
                # Map product types to database values
                product_type_mapping = {
                    'capsule': ['capsule', 'pill', 'cap'],
                    'solid edible': ['solid edible', 'edible', 'gummy', 'chocolate', 'candy', 'cookie', 'brownie'],
                    'topical ointment': ['topical ointment', 'topical', 'cream', 'balm', 'lotion', 'salve'],
                    'liquid edible': ['liquid edible', 'tincture', 'drops'],
                    'core flower': ['core flower', 'flower', 'bud', 'nug'],
                    # Vape/Concentrate for Inhalation must NOT match Flower - add explicit mappings
                    'vape cartridge': ['vape', 'cartridge', 'cart', 'disposable', 'all-in-one', 'vape cartridge'],
                    'concentrate': ['concentrate', 'rosin', 'wax', 'shatter', 'live resin', 'distillate', 'badder', 'diamonds', 'sauce', 'crumble'],
                }
                
                product_type_lower = product_type.lower().strip()
                # Also match "concentrate for inhalation" -> vape/concentrate (exclude flower)
                if 'concentrate' in product_type_lower and 'inhalation' in product_type_lower:
                    product_type_lower = 'vape cartridge'  # Treat as vape for filtering
                if product_type_lower in product_type_mapping:
                    type_conditions = []
                    for db_type in product_type_mapping[product_type_lower]:
                        type_conditions.append("LOWER(p.\"Product Type*\") LIKE ?")
                        params.append(f"%{db_type}%")
                    
                    if type_conditions:
                        query += " AND (" + " OR ".join(type_conditions) + ")"
            
            if vendor:
                # Vendor match
                query += " AND p.\"Vendor/Supplier*\" LIKE ?"
                params.append(f"%{vendor}%")
            
            # Note: Product Type is often empty in the database, so we'll make this optional
            # if product_type:
            #     # Product type match
            #     query += " AND p.\"Product Type*\" LIKE ?"
            #     params.append(f"%{product_type}%")
            
            if strain:
                # Strain match - be more flexible with strain matching
                strain_conditions = []
                
                # Direct strain match
                strain_conditions.append("p.\"Product Strain\" LIKE ?")
                params.append(f"%{strain}%")
                
                # Lineage match
                strain_conditions.append("p.\"Lineage\" LIKE ?")
                params.append(f"%{strain}%")
                
                # Flexible strain matching for common variations
                if strain.lower() in ['mix', 'mixed']:
                    strain_conditions.append("p.\"Product Strain\" LIKE ?")
                    params.append("%Mixed%")
                    strain_conditions.append("p.\"Lineage\" LIKE ?")
                    params.append("%MIXED%")
                elif strain.lower() in ['sativa', 'sat']:
                    strain_conditions.append("p.\"Product Strain\" LIKE ?")
                    params.append("%Sativa%")
                    strain_conditions.append("p.\"Lineage\" LIKE ?")
                    params.append("%SATIVA%")
                elif strain.lower() in ['indica', 'ind']:
                    strain_conditions.append("p.\"Product Strain\" LIKE ?")
                    params.append("%Indica%")
                    strain_conditions.append("p.\"Lineage\" LIKE ?")
                    params.append("%INDICA%")
                
                if strain_conditions:
                    query += " AND (" + " OR ".join(strain_conditions) + ")"
            
            # Store the query for potential fallback
            original_query = query
            original_params = params.copy()
            
            # Order by relevance with product type priority
            if product_type:
                product_type_lower = product_type.lower().strip()
                query += f""" ORDER BY 
                    CASE WHEN LOWER(p."Product Type*") = ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN LOWER(p."Product Type*") LIKE ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p.normalized_name = ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Product Name*" = ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Product Name*" LIKE ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Description" LIKE ? THEN 1 ELSE 0 END DESC,
                    p.id DESC 
                    LIMIT 1"""
                params.extend([product_type_lower, f"%{product_type_lower}%", normalized_name, normalized_name, f"%{normalized_name}%", f"%{normalized_name}%"])
            else:
                query += """ ORDER BY 
                    CASE WHEN p.normalized_name = ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Product Name*" = ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Product Name*" LIKE ? THEN 1 ELSE 0 END DESC,
                    CASE WHEN p."Description" LIKE ? THEN 1 ELSE 0 END DESC,
                    p.id DESC 
                    LIMIT 1"""
                params.extend([normalized_name, normalized_name, f"%{normalized_name}%", f"%{normalized_name}%"])
            
            # DEBUG: Log the actual query being executed
            print(f"🔍 DEBUG: Executing query: {query}")
            print(f"🔍 DEBUG: With params: {params}")
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # CRITICAL FIX: Handle multiple results and deduplicate
            if results:
                # If we got multiple results, deduplicate by product name
                seen_names = set()
                unique_results = []
                
                for result in results:
                    product_name = result[1] if len(result) > 1 else None  # Product Name* is at index 1
                    if product_name and product_name not in seen_names:
                        seen_names.add(product_name)
                        unique_results.append(result)
                
                # Use the first unique result (highest priority due to ORDER BY)
                result = unique_results[0] if unique_results else None
                
                if len(unique_results) > 1:
                    print(f"🔍 DEBUG: Found {len(results)} results, deduplicated to {len(unique_results)} unique products")
            else:
                result = None
            
            # DEBUG: Log database query results
            print(f"🔍 DEBUG: Database query returned: {result is not None}")
            if result:
                print(f"🔍 DEBUG: Found database match: {result[1]}")  # Product Name*
            else:
                print(f"🔍 DEBUG: No database match found for '{normalized_name}'")
                
                # FALLBACK: Try without strain matching if strain was specified
                if strain and 'original_query' in locals():
                    print(f"🔍 DEBUG: Trying fallback query without strain matching...")
                    
                    # Build a clean fallback query without strain conditions
                    fallback_query = """SELECT p.id, p."Product Name*", p."Product Strain", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                       p."Description", p."Weight*", p."Units", p."Price", p."Quantity*", p."DOH", p."Concentrate Type", p."Ratio", p."JointRatio",
                       p."State", p."Is Sample? (yes/no)", p."Is MJ product?(yes/no)", p."Discountable? (yes/no)", p."Room*", p."Batch Number", p."Lot Number", p."Barcode*",
                       p."Medical Only (Yes/No)", p."Med Price", p."Expiration Date(YYYY-MM-DD)", p."Is Archived? (yes/no)", p."THC Per Serving", p."Allergens", p."Solvent", p."Accepted Date",
                       p."Internal Product Identifier", p."Product Tags (comma separated)", p."Image URL", p."Ingredients", p."CombinedWeight", p."Ratio_or_THC_CBD", 
                       p."Description_Complexity", p."Total THC", p."THCA", p."CBDA", p."CBN", 0 as total_occurrences, '' as first_seen_date, '' as last_seen_date
                FROM products p
                WHERE 1=1"""
                    fallback_params = []
                    
                    # Add name conditions
                    if normalized_name:
                        fallback_query += " AND (p.normalized_name = ? OR LOWER(p.\"Product Name*\") LIKE ? OR LOWER(p.\"Product Name*\") LIKE ? OR LOWER(p.\"Product Name*\") LIKE ?)"
                        fallback_params.extend([normalized_name, f"%{normalized_name.lower()}%", f"%{normalized_name.lower()}%", f"%{normalized_name.lower()}%"])
                    
                    # Add vendor condition
                    if vendor:
                        fallback_query += " AND p.\"Vendor/Supplier*\" LIKE ?"
                        fallback_params.append(f"%{vendor}%")
                    
                    # Add product type conditions
                    if product_type:
                        product_type_lower = product_type.lower().strip()
                        product_type_mapping = {
                            'capsule': ['capsule', 'pill', 'cap'],
                            'solid edible': ['solid edible', 'edible', 'gummy', 'chocolate', 'candy', 'cookie', 'brownie'],
                            'topical ointment': ['topical ointment', 'topical', 'cream', 'balm', 'lotion', 'salve'],
                            'liquid edible': ['liquid edible', 'tincture', 'drops'],
                            'core flower': ['core flower', 'flower', 'bud', 'nug']
                        }
                        
                        if product_type_lower in product_type_mapping:
                            type_conditions = []
                            for db_type in product_type_mapping[product_type_lower]:
                                type_conditions.append("LOWER(p.\"Product Type*\") LIKE ?")
                                fallback_params.append(f"%{db_type}%")
                            
                            if type_conditions:
                                fallback_query += " AND (" + " OR ".join(type_conditions) + ")"
                    
                    # Add ordering
                    if product_type:
                        fallback_query += f""" ORDER BY 
                            CASE WHEN LOWER(p."Product Type*") = ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN LOWER(p."Product Type*") LIKE ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p.normalized_name = ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Product Name*" = ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Product Name*" LIKE ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Description" LIKE ? THEN 1 ELSE 0 END DESC,
                            p.id DESC 
                            LIMIT 1"""
                        fallback_params.extend([product_type_lower, f"%{product_type_lower}%", normalized_name, normalized_name, f"%{normalized_name}%", f"%{normalized_name}%"])
                    else:
                        fallback_query += """ ORDER BY 
                            CASE WHEN p.normalized_name = ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Product Name*" = ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Product Name*" LIKE ? THEN 1 ELSE 0 END DESC,
                            CASE WHEN p."Description" LIKE ? THEN 1 ELSE 0 END DESC,
                            p.id DESC 
                            LIMIT 1"""
                        fallback_params.extend([normalized_name, normalized_name, f"%{normalized_name}%", f"%{normalized_name}%"])
                    
                    print(f"🔍 DEBUG: Executing fallback query: {fallback_query}")
                    print(f"🔍 DEBUG: With fallback params: {fallback_params}")
                    
                    cursor.execute(fallback_query, fallback_params)
                    fallback_results = cursor.fetchall()
                    
                    # CRITICAL FIX: Handle multiple fallback results and deduplicate
                    if fallback_results:
                        # If we got multiple results, deduplicate by product name
                        seen_names = set()
                        unique_fallback_results = []
                        
                        for fallback_result in fallback_results:
                            product_name = fallback_result[1] if len(fallback_result) > 1 else None  # Product Name* is at index 1
                            if product_name and product_name not in seen_names:
                                seen_names.add(product_name)
                                unique_fallback_results.append(fallback_result)
                        
                        # Use the first unique result (highest priority due to ORDER BY)
                        result = unique_fallback_results[0] if unique_fallback_results else None
                        
                        if len(unique_fallback_results) > 1:
                            print(f"🔍 DEBUG: Fallback found {len(fallback_results)} results, deduplicated to {len(unique_fallback_results)} unique products")
                    else:
                        result = None
                    
                    print(f"🔍 DEBUG: Fallback query returned: {result is not None}")
                    if result:
                        print(f"🔍 DEBUG: Found fallback database match: {result[1]}")  # Product Name*
                
                # DEBUG: Let's see what's actually in the database
                try:
                    debug_cursor = conn.cursor()
                    debug_cursor.execute("SELECT \"Product Name*\", \"Description\" FROM products WHERE \"Product Name*\" LIKE ? OR \"Description\" LIKE ? LIMIT 5", [f"%{normalized_name}%", f"%{normalized_name}%"])
                    debug_results = debug_cursor.fetchall()
                    print(f"🔍 DEBUG: Database search for '{normalized_name}' returned {len(debug_results)} results")
                    for i, row in enumerate(debug_results):
                        print(f"🔍 DEBUG:   {i+1}. Product: '{row[0]}', Description: '{row[1][:50]}...'")
                    
                    # Also check what product names actually exist
                    debug_cursor.execute("SELECT \"Product Name*\" FROM products WHERE \"Product Name*\" LIKE ? LIMIT 10", [f"%{normalized_name.split('_')[0]}%"])  # Search for first word
                    debug_names = debug_cursor.fetchall()
                    print(f"🔍 DEBUG: Products containing '{normalized_name.split('_')[0]}': {[row[0] for row in debug_names]}")
                except Exception as debug_error:
                    print(f"🔍 DEBUG: Debug query failed: {debug_error}")
            
            if result:
                # Convert to the same format as get_products_by_names using actual column indices
                product_info = {
                    'id': result[0],
                    'ProductName': result[1],  # Product Name*
                    'Product Name*': result[1],  # Excel column name compatibility
                    'Product Strain': result[2],  # Product Strain
                    'Product Type*': result[3],  # Product Type*
                    'Vendor': result[4],  # Vendor/Supplier*
                    'Vendor/Supplier*': result[4],  # Excel column name compatibility
                    'Product Brand': result[5],  # Product Brand
                    'Lineage': result[6] or 'MIXED',  # Lineage
                    'Description': result[7] or result[1],  # Description or Product Name*
                    'Weight*': result[8],  # Weight*
                    'Units': result[9],  # Units
                    'Price': result[10],  # Price
                    'Quantity*': result[11],  # Quantity*
                    'DOH': result[12],  # DOH
                    'concentrate_type': result[13],  # Concentrate Type
                    'Ratio': result[14],  # Ratio
                    'JointRatio': result[15],  # Joint Ratio
                    'State': result[16],  # State
                    'Is Sample?': result[17],  # Is Sample
                    'Is MJ product?': result[18],  # Is MJ Product
                    'Discountable?': result[19],  # Discountable
                    'Room*': result[20],  # Room
                    'batch_number': result[21],  # Batch Number
                    'lot_number': result[22],  # Lot Number
                    'barcode': result[23],  # Barcode
                    'Medical Only': result[24],  # Medical Only
                    'med_price': result[25],  # Med Price
                    'expiration_date': result[26],  # Expiration Date
                    'is_archived': result[27],  # Is Archived
                    'thc_per_serving': result[28],  # THC Per Serving
                    'allergens': result[29],  # Allergens
                    'solvent': result[30],  # Solvent
                    'accepted_date': result[31],  # Accepted Date
                    'internal_product_identifier': result[32],  # Internal Product Identifier
                    'product_tags': result[33],  # Product Tags
                    'image_url': result[34],  # Image URL
                    'ingredients': result[35],  # Ingredients
                    'combined_weight': result[36],  # Combined Weight
                    'ratio_or_thc_cbd': result[37],  # Ratio or THC/CBD
                    'description_complexity': result[38],  # Description Complexity
                    'Total THC': result[39],  # Total THC
                    'THCA': result[40],  # THCA
                    'CBDA': result[41],  # CBDA
                    'CBN': result[42],  # CBN
                    'total_occurrences': result[43],
                    'first_seen_date': result[44],
                    'last_seen_date': result[45],
                    # Add Excel column name compatibility fields
                    'ProductBrand': result[5],
                    'ProductStrain': result[2],
                    'WeightWithUnits': f"{result[8]}{result[9]}" if result[8] and result[9] else result[8] or result[9] or '',
                    'displayName': result[1],  # For frontend compatibility
                    'Source': 'Product Database Match'  # Indicate this came from database
                }
                
                logger.info(f"Found database match for '{product_name}': {product_info['ProductName']}")
                return product_info
            
            logger.info(f"No database match found for '{product_name}'")
            return None
            
        except Exception as e:
            logger.error(f"Error finding best product match: {e}")
            return None

    def make_educated_guess(self, product_name: str, vendor: str = None, brand: str = None) -> Optional[Dict[str, Any]]:
        """
        Make an educated guess for a product based primarily on the product name itself.
        Extracts vendor, brand, weight, product type, and strain from the product name.
        
        Args:
            product_name: The product name to make a guess for
            vendor: Optional vendor name (will be extracted from product name if not provided)
            brand: Optional brand name (will be extracted from product name if not provided)
            
        Returns:
            Dictionary with inferred product information or None if no good matches found
        """
        try:
            self.init_database()
            
            logger.info(f"Making educated guess for: {product_name}")
            
            # Extract all information directly from the product name
            extracted_info = self._extract_all_info_from_product_name(product_name, vendor, brand)
            
            if extracted_info:
                logger.info(f"Successfully extracted info from product name: {extracted_info}")
                return extracted_info
            
            # Fallback: Use similar products if direct extraction fails
            logger.info("Direct extraction failed, falling back to similar products approach")
            return self._make_educated_guess_from_similar_products(product_name, vendor, brand)
            
        except Exception as e:
            logger.error(f"Error making educated guess for '{product_name}': {e}")
            return None
    
    def _extract_all_info_from_product_name(self, product_name: str, vendor: str = None, brand: str = None) -> Optional[Dict[str, Any]]:
        """
        Extract all product information directly from the product name.
        Handles patterns like "Liquid Diamond Disposable Vape by Oleum"
        """
        try:
            # Extract vendor and brand from product name if not provided
            extracted_vendor, extracted_brand = self._extract_vendor_and_brand_from_name(product_name, vendor, brand)
            
            # Extract weight and units
            weight_info = self._infer_weight_from_name(product_name)
            
            # Extract product type
            product_type = self._infer_product_type_from_name(product_name)
            
            # Extract strain name
            strain_name = self._extract_strain_from_name(product_name)
            
            # Infer price based on product type and weight
            price = self._infer_price_from_type_and_weight(product_type, float(weight_info['weight']))
            
            # Default lineage to HYBRID if we can't determine it
            lineage = 'HYBRID'
            
            # Create the result
            result = {
                'product_name': product_name,
                'source': 'Educated Guess',
                'confidence': 'high' if extracted_brand else 'medium',
                'weight': weight_info['weight'],
                'units': weight_info['units'],
                'price': str(price),
                'product_type': product_type or 'Unknown',
                'lineage': lineage,
                'strain_name': strain_name or 'Unknown',
                'vendor': extracted_vendor or 'Unknown',
                'brand': extracted_brand or 'Unknown',
                'description': f"{product_name} - {weight_info['weight']}{weight_info['units']}"
            }
            
            logger.info(f"Extracted from product name: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting info from product name '{product_name}': {e}")
            return None
    
    def _extract_vendor_and_brand_from_name(self, product_name: str, vendor: str = None, brand: str = None) -> tuple[str, str]:
        """
        Extract vendor and brand from product name patterns like:
        - "Product Name by Brand"
        - "Brand Product Name"
        - "Product Name - Brand"
        """
        import re
        
        if vendor and brand:
            return vendor, brand
        
        name_lower = product_name.lower()
        
        # Pattern 1: "Product Name by Brand"
        by_match = re.search(r'by\s+([A-Za-z0-9\s&]+)(?:\s|$)', product_name, re.IGNORECASE)
        if by_match:
            brand_name = by_match.group(1).strip()
            return brand_name, brand_name  # Brand and vendor are often the same
        
        # Pattern 2: "Brand Product Name" (brand at the beginning)
        # Common brand names to look for
        common_brands = [
            'oleum', 'dank czar', 'omega labs', 'airo pro', 'jsm', "hustler's ambition",
            'ceres', 'harmony farms', "farmer's daughter", 'greasy runtz', 'kelloggz koffee',
            'trop banana', 'velvet koffee', 'trigonal industries', 'peak supply', 'fk it',
            'conscious cannabis', 'honey tree', 'bodhi high', 'skagit organics', 'super fog',
            'seattle bubble works', 'blue sky farms', 'green and gold brands', 'seatown',
            'lil ray', 'lil ray\'s', 'green revolution'
        ]
        
        for brand_name in common_brands:
            if brand_name in name_lower:
                return brand_name.title(), brand_name.title()
        
        # Pattern 3: "Product Name - Brand" (brand at the end)
        if " - " in product_name:
            parts = product_name.split(" - ")
            if len(parts) > 1:
                potential_brand = parts[-1].strip()
                if len(potential_brand) > 2:
                    return potential_brand, potential_brand
        
        return vendor or 'Unknown', brand or 'Unknown'
    
    def _make_educated_guess_from_similar_products(self, product_name: str, vendor: str = None, brand: str = None) -> Optional[Dict[str, Any]]:
        """
        Fallback method: Make educated guess using similar products approach.
        This is the original method logic.
        """
        try:
            # Normalize the product name for comparison
            normalized_name = self._normalize_product_name(product_name)
            name_lower = product_name.lower()
            
            # Extract key terms from product name for matching
            key_terms = self._extract_key_terms(product_name)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Strategy 1: Find products with similar names
            similar_products = []
            
            # Search for products with similar key terms
            for term in key_terms:
                if len(term) > 3:  # Only use meaningful terms
                    # Try to use Weight Unit column, fallback to Units if it doesn't exist
                    try:
                        cursor.execute('''
                            SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                                   COALESCE(p."Weight Unit* (grams/gm or ounces/oz)", p."Units") AS "WeightUnit", 
                                   p."Price* (Tier Name for Bulk)",
                                   p."Lineage", s.strain_name, p."Description"
                            FROM products p
                            LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                            WHERE p."Product Name*" LIKE ? OR p."Product Name*" LIKE ?
                            ORDER BY p.id DESC
                            LIMIT 20
                        ''', (f'%{term}%', f'%{term}%'))
                    except Exception as col_error:
                        # Fallback if Weight Unit column doesn't exist
                        logger.warning(f"Weight Unit column not found, using Units: {col_error}")
                        cursor.execute('''
                            SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                                   p."Units" AS "WeightUnit", 
                                   p."Price* (Tier Name for Bulk)",
                                   p."Lineage", s.strain_name, p."Description"
                            FROM products p
                            LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                            WHERE p."Product Name*" LIKE ? OR p."Product Name*" LIKE ?
                            ORDER BY p.id DESC
                            LIMIT 20
                        ''', (f'%{term}%', f'%{term}%'))
                    
                    results = cursor.fetchall()
                    for result in results:
                        similar_products.append({
                            'product_name': result[0],
                            'product_type': result[1],
                            'vendor': result[2],
                            'brand': result[3],
                            'weight': result[4],
                            'units': result[5],
                            'price': result[6],
                            'lineage': result[7],
                            'strain_name': result[8],
                            'description': result[9],
                            'similarity_score': self._calculate_similarity_score(product_name, result[0])
                        })
            
            # Strategy 2: Find products with similar product types
            product_type = self._infer_product_type_from_name(product_name)
            if product_type:
                try:
                    cursor.execute('''
                        SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                               COALESCE(p."Weight Unit* (grams/gm or ounces/oz)", p."Units") AS "WeightUnit", 
                               p."Price* (Tier Name for Bulk)",
                               p."Lineage", s.strain_name, p."Description"
                        FROM products p
                        LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                        WHERE p."Product Type*" = ?
                        ORDER BY p.id DESC
                        LIMIT 10
                    ''', (product_type,))
                except Exception as col_error:
                    # Fallback if Weight Unit column doesn't exist
                    logger.warning(f"Weight Unit column not found, using Units: {col_error}")
                    cursor.execute('''
                        SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                               p."Units" AS "WeightUnit", 
                               p."Price* (Tier Name for Bulk)",
                               p."Lineage", s.strain_name, p."Description"
                        FROM products p
                        LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                        WHERE p."Product Type*" = ?
                        ORDER BY p.id DESC
                        LIMIT 10
                    ''', (product_type,))
                
                results = cursor.fetchall()
                for result in results:
                    similar_products.append({
                        'product_name': result[0],
                        'product_type': result[1],
                        'vendor': result[2],
                        'brand': result[3],
                        'weight': result[4],
                        'units': result[5],
                        'price': result[6],
                        'lineage': result[7],
                        'strain_name': result[8],
                        'description': result[9],
                        'similarity_score': 0.3  # Lower score for type-only matches
                    })
            
            # Strategy 3: Find products with similar strains
            strain_name = self._extract_strain_from_name(product_name)
            if strain_name:
                try:
                    cursor.execute('''
                        SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                               COALESCE(p."Weight Unit* (grams/gm or ounces/oz)", p."Units") AS "WeightUnit", 
                               p."Price* (Tier Name for Bulk)",
                               p."Lineage", s.strain_name, p."Description"
                        FROM products p
                        LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                        WHERE s.strain_name LIKE ? OR p."Product Strain" LIKE ?
                        ORDER BY p.id DESC
                        LIMIT 10
                    ''', (f'%{strain_name}%', f'%{strain_name}%'))
                except Exception as col_error:
                    # Fallback if Weight Unit column doesn't exist
                    logger.warning(f"Weight Unit column not found, using Units: {col_error}")
                    cursor.execute('''
                        SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", 
                               p."Units" AS "WeightUnit", 
                               p."Price* (Tier Name for Bulk)",
                               p."Lineage", s.strain_name, p."Description"
                        FROM products p
                        LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                        WHERE s.strain_name LIKE ? OR p."Product Strain" LIKE ?
                        ORDER BY p.id DESC
                        LIMIT 10
                    ''', (f'%{strain_name}%', f'%{strain_name}%'))
                
                results = cursor.fetchall()
                for result in results:
                    similar_products.append({
                        'product_name': result[0],
                        'product_type': result[1],
                        'vendor': result[2],
                        'brand': result[3],
                        'weight': result[4],
                        'units': result[5],
                        'price': result[6],
                        'lineage': result[7],
                        'strain_name': result[8],
                        'description': result[9],
                        'similarity_score': 0.4  # Medium score for strain matches
                    })
            
            # Remove duplicates and sort by similarity score
            unique_products = {}
            for product in similar_products:
                key = f"{product['product_name']}_{product['vendor']}_{product['brand']}"
                if key not in unique_products or product['similarity_score'] > unique_products[key]['similarity_score']:
                    unique_products[key] = product
            
            similar_products = list(unique_products.values())
            similar_products.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            if not similar_products:
                logger.warning(f"No similar products found for '{product_name}'")
                return None
            
            logger.info(f"Found {len(similar_products)} similar products for '{product_name}'")
            logger.info(f"Key terms extracted: {key_terms}")
            logger.info(f"Product type inferred: {product_type}")
            logger.info(f"Strain name extracted: {strain_name}")
            
            # Take top 5 most similar products for analysis
            top_similar = similar_products[:5]
            
            # Infer properties from similar products
            inferred_data = self._infer_properties_from_similar_products(product_name, top_similar)
            
            if inferred_data:
                logger.info(f"Made educated guess for '{product_name}': {inferred_data}")
                return inferred_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error making educated guess from similar products for '{product_name}': {e}")
            return None
    
    def _extract_key_terms(self, product_name: str) -> Set[str]:
        """Extract key terms from product name for matching."""
        import re
        
        # Remove common words and punctuation
        name_lower = product_name.lower()
        
        # Remove common product words that don't help with matching
        common_words = {
            'live', 'resin', 'rosin', 'wax', 'shatter', 'hash', 'flower', 'bud', 'pre', 'roll', 
            'joint', 'cartridge', 'vape', 'pen', 'edible', 'gummy', 'chocolate', 'cookie', 
            'brownie', 'candy', 'sweet', 'food', 'drink', 'beverage', 'tincture', 'drops', 
            'capsule', 'pill', 'tablet', 'lozenge', 'mint', 'chew', 'chewing', 'cream', 
            'lotion', 'salve', 'balm', 'ointment', 'gel', 'spray', 'patch', 'transdermal', 
            'skin', 'external', 'apply', 'rub', 'disposable', 'pod', 'battery', 'oil', 
            'extract', 'concentrate', 'distillate', 'sauce', 'terp', 'terpene', 'diamond',
            'crystal', 'powder', 'granule', 'pellet', 'tablet', 'capsule', 'liquid', 'solid'
        }
        
        # Extract words, filter out common words and short words
        words = re.findall(r'\b[a-zA-Z]+\b', name_lower)
        key_terms = {word for word in words if len(word) > 2 and word not in common_words}
        
        # Add broader matching terms for better similarity
        # For example, "Glazed Apricots" should match "Wedding Cake" (both are dessert-like)
        dessert_terms = {'glazed', 'apricots', 'wedding', 'cake', 'cherry', 'lemon', 'blueberry', 'strawberry'}
        if any(term in key_terms for term in dessert_terms):
            # Add dessert-related terms to improve matching
            key_terms.update({'cake', 'dessert', 'fruit', 'sweet'})
        
        # Add strain-related terms for better matching
        strain_terms = {'kush', 'haze', 'diesel', 'og', 'cookies', 'runtz', 'gelato'}
        if any(term in key_terms for term in strain_terms):
            key_terms.update({'strain', 'cannabis', 'marijuana'})
        
        return key_terms
    
    def _calculate_similarity_score(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two product names."""
        from difflib import SequenceMatcher
        
        # Use sequence matcher for overall similarity
        similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        
        # Boost score for exact word matches
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        word_overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        
        if total_words > 0:
            word_similarity = word_overlap / total_words
            # Combine overall similarity with word overlap
            final_score = (similarity + word_similarity) / 2
        else:
            final_score = similarity
        
        return final_score
    
    def _infer_product_type_from_name(self, product_name: str) -> Optional[str]:
        """Infer product type from product name using consistent logic."""
        if not isinstance(product_name, str):
            return "Unknown Type"
        
        name_lower = product_name.lower()
        
        # Check TYPE_OVERRIDES first
        from src.core.constants import TYPE_OVERRIDES
        for key, value in TYPE_OVERRIDES.items():
            if key in name_lower:
                return value
        
        # Pattern-based inference - prioritize vape keywords over concentrate keywords
        if any(x in name_lower for x in ["flower", "bud", "nug", "herb", "marijuana", "cannabis"]):
            return "Flower"
        elif any(x in name_lower for x in ["vape", "cart", "cartridge", "disposable", "pod", "battery", "jefe", "twisted", "fire", "pen"]):
            return "Vape Cartridge"
        elif any(x in name_lower for x in ["concentrate", "rosin", "shatter", "wax", "live resin", "diamonds", "sauce", "extract", "oil", "distillate"]):
            return "Concentrate"
        elif any(x in name_lower for x in ["edible", "gummy", "chocolate", "cookie", "brownie", "candy"]):
            return "Edible (Solid)"
        elif any(x in name_lower for x in ["tincture", "oil", "drops", "liquid"]):
            return "Edible (Liquid)"
        elif any(x in name_lower for x in ["pre-roll", "joint", "cigar", "blunt"]):
            return "Pre-roll"
        elif any(x in name_lower for x in ["topical", "cream", "lotion", "salve", "balm"]):
            return "Topical"
        elif any(x in name_lower for x in ["tincture", "sublingual"]):
            return "Tincture"
        else:
            # Default to Vape Cartridge for any remaining unknown types since most products are concentrates
            return "Vape Cartridge"
    
    def _extract_strain_from_name(self, product_name: str) -> Optional[str]:
        """Extract strain name from product name."""
        import re
        
        # Common strain keywords
        strain_keywords = [
            'og', 'kush', 'haze', 'diesel', 'cookies', 'runtz', 'gelato', 'wedding', 'cake',
            'blueberry', 'strawberry', 'banana', 'mango', 'pineapple', 'lemon', 'lime', 'cherry',
            'grape', 'apple', 'orange', 'guava', 'dragon', 'fruit', 'passion', 'peach', 'apricot',
            'watermelon', 'cantaloupe', 'honeydew', 'kiwi', 'plum', 'raspberry', 'blackberry',
            'yoda', 'amnesia', 'afghani', 'hashplant', 'super', 'boof', 'grandy', 'candy',
            'tricho', 'jordan', 'cosmic', 'combo', 'honey', 'bread', 'mintz', 'grinch'
        ]
        
        name_lower = product_name.lower()
        words = name_lower.split()
        
        # Look for multi-word strain names first (e.g., "Wedding Cake", "Sour Diesel")
        multi_word_strains = [
            'wedding cake', 'sour diesel', 'blueberry kush', 'lemon haze', 'strawberry cough',
            'granddaddy purple', 'northern lights', 'white widow', 'jack herer', 'durban poison',
            'trainwreck', 'chemdawg', 'sour cheese', 'dream crack', 'maui wowie', 'bubba kush',
            'master kush', 'hindu kush', 'afghan kush', 'master og', 'sour og', 'cheese og',
            'dream og', 'high life', 'white gummie', 'seattle trophy wife', 'tangerine queen',
            'triangle kush', 'red velvet cake', 'grape goji', 'watermelon mojito', 'candy pound cake',
            'truffle cake', 'emerald apricot', 'bollywood runtz', 'mango punch', 'raspberry lemonade',
            'strawberry burst', 'watermelon wave', 'grape soda', 'strawberry bliss', 'cherry ztripez',
            'metaverse', 'galactic jack', 'gdpunch', 'grape ape', 'rainbow cake', 'strawberry mimosa',
            'yoda og', 'goji og', 'cookies and cream', 'grape gas gelatti', 'maui wowie', 
            'strawberry shortcake', 'grapefruit', 'purple rain', 'crepe ape', 'trunk funk', 
            'sub woofer', 'golden pineapple', 'chicken & waffles'
        ]
        
        for strain in multi_word_strains:
            if strain in name_lower:
                # Return the proper case version
                return strain.title()
        
        # Look for single word strain keywords
        for word in words:
            if word in strain_keywords:
                return word.title()
        
        # Look for capitalized words that might be strain names (but exclude common product words)
        common_product_words = {
            'live', 'resin', 'rosin', 'wax', 'shatter', 'hash', 'flower', 'bud', 'pre', 'roll', 
            'joint', 'cartridge', 'vape', 'pen', 'edible', 'gummy', 'chocolate', 'cookie', 
            'brownie', 'candy', 'sweet', 'food', 'drink', 'beverage', 'tincture', 'drops', 
            'capsule', 'pill', 'tablet', 'lozenge', 'mint', 'chew', 'chewing', 'cream', 
            'lotion', 'salve', 'balm', 'ointment', 'gel', 'spray', 'patch', 'transdermal', 
            'skin', 'external', 'apply', 'rub', 'disposable', 'pod', 'battery', 'oil', 
            'extract', 'concentrate', 'distillate', 'sauce', 'terp', 'terpene', 'diamond',
            'crystal', 'powder', 'granule', 'pellet', 'tablet', 'capsule', 'liquid', 'solid'
        }
        
        for word in product_name.split():
            if (len(word) > 2 and word[0].isupper() and word[1:].islower() and 
                word.lower() not in common_product_words):
                return word
        
        return None
    
    def _infer_properties_from_similar_products(self, product_name: str, similar_products: List[Dict]) -> Optional[Dict[str, Any]]:
        """Infer product properties from similar products."""
        if not similar_products:
            return None
        
        # Extract weight and units
        weights = []
        units = []
        prices = []
        product_types = []
        lineages = []
        strains = []
        vendors = []
        brands = []
        
        for product in similar_products:
            # Weight and units
            if product['weight'] and product['weight'] != 'nan':
                try:
                    weight_val = float(product['weight'])
                    if weight_val > 0:
                        weights.append(weight_val)
                        if product['units'] and product['units'] != 'nan':
                            units.append(product['units'])
                except (ValueError, TypeError):
                    pass
            
            # Price
            if product['price'] and product['price'] != 'nan':
                try:
                    price_val = float(product['price'])
                    if price_val > 0:
                        prices.append(price_val)
                except (ValueError, TypeError):
                    pass
            
            # Product type
            if product['product_type'] and product['product_type'] != 'nan':
                product_types.append(product['product_type'])
            
            # Lineage
            if product['lineage'] and product['lineage'] != 'nan':
                lineages.append(product['lineage'])
            
            # Strain
            if product['strain_name'] and product['strain_name'] != 'nan':
                strains.append(product['strain_name'])
            
            # Vendor
            if product['vendor'] and product['vendor'] != 'nan':
                vendors.append(product['vendor'])
            
            # Brand
            if product['brand'] and product['brand'] != 'nan':
                brands.append(product['brand'])
        
        # Calculate most common values
        from collections import Counter
        
        inferred_data = {
            'product_name': product_name,
            'source': 'Educated Guess',
            'confidence': 'medium'
        }
        
        # Weight and units - PRIORITY: Use weight from product name first, then similar products
        weight_info = self._infer_weight_from_name(product_name)
        if weight_info['weight'] != '1.0' or 'g' not in product_name.lower():  # If we found a specific weight in the name
            inferred_data['weight'] = weight_info['weight']
            inferred_data['units'] = weight_info['units']
            logger.info(f"Using weight from product name: {weight_info['weight']}{weight_info['units']}")
        elif weights:
            # Use median weight from similar products
            weights.sort()
            median_weight = weights[len(weights) // 2]
            inferred_data['weight'] = str(median_weight)
            
            if units:
                most_common_unit = Counter(units).most_common(1)[0][0]
                inferred_data['units'] = most_common_unit
            else:
                inferred_data['units'] = 'g'  # Default
            logger.info(f"Using weight from similar products: {inferred_data['weight']}{inferred_data['units']}")
        else:
            # Fallback weight inference
            inferred_data['weight'] = weight_info['weight']
            inferred_data['units'] = weight_info['units']
            logger.info(f"Using fallback weight: {weight_info['weight']}{weight_info['units']}")
        
        # Price
        if prices:
            # Use median price for more stability
            prices.sort()
            median_price = prices[len(prices) // 2]
            inferred_data['price'] = str(median_price)
        else:
            # Fallback price inference
            inferred_data['price'] = self._infer_price_from_type_and_weight(
                inferred_data.get('product_type', 'Unknown'),
                float(inferred_data['weight'])
            )
        
        # Product type
        if product_types:
            most_common_type = Counter(product_types).most_common(1)[0][0]
            inferred_data['product_type'] = most_common_type
        else:
            inferred_data['product_type'] = self._infer_product_type_from_name(product_name) or 'Unknown'
        
        # Lineage
        if lineages:
            most_common_lineage = Counter(lineages).most_common(1)[0][0]
            inferred_data['lineage'] = most_common_lineage
        else:
            inferred_data['lineage'] = 'HYBRID'  # Default
        
        # Strain - PRIORITY: Extract from product name first, then use similar products
        extracted_strain = self._extract_strain_from_name(product_name)
        if extracted_strain and extracted_strain != 'Unknown':
            inferred_data['strain_name'] = extracted_strain
            logger.info(f"Using strain from product name: {extracted_strain}")
        elif strains:
            most_common_strain = Counter(strains).most_common(1)[0][0]
            inferred_data['strain_name'] = most_common_strain
            logger.info(f"Using strain from similar products: {most_common_strain}")
        else:
            inferred_data['strain_name'] = 'Unknown'
            logger.info("No strain information available")
        
        # Vendor
        if vendors:
            most_common_vendor = Counter(vendors).most_common(1)[0][0]
            inferred_data['vendor'] = most_common_vendor
        else:
            inferred_data['vendor'] = 'Unknown'
        
        # Brand
        if brands:
            most_common_brand = Counter(brands).most_common(1)[0][0]
            inferred_data['brand'] = most_common_brand
        else:
            inferred_data['brand'] = 'Unknown'
        
        # Description
        inferred_data['description'] = f"{product_name} - {inferred_data['weight']}{inferred_data['units']}"
        
        return inferred_data
    
    def _infer_weight_from_name(self, product_name: str) -> Dict[str, str]:
        """Infer weight from product name."""
        import re
        
        # Look for weight patterns in product name
        weight_patterns = [
            r'(\d+\.?\d*)\s*(g|gram|grams|gm)',  # 3.5g, 3.5 gram, etc.
            r'(\d+\.?\d*)\s*(mg|milligram|milligrams)',  # 100mg, etc.
            r'(\d+\.?\d*)\s*(oz|ounce|ounces)',  # 1oz, etc.
            r'(\d+\.?\d*)\s*(lb|pound|pounds)',  # 1lb, etc.
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                weight = match.group(1)
                units = match.group(2).lower()
                if units in ['gram', 'grams', 'gm']:
                    units = 'g'
                elif units in ['milligram', 'milligrams']:
                    units = 'mg'
                elif units in ['ounce', 'ounces']:
                    units = 'oz'
                elif units in ['pound', 'pounds']:
                    units = 'lb'
                return {'weight': weight, 'units': units}
        
        # Default weights based on product type
        product_type = self._infer_product_type_from_name(product_name)
        default_weights = {
            'flower': {'weight': '3.5', 'units': 'g'},
            'pre-roll': {'weight': '1.0', 'units': 'g'},
            'concentrate': {'weight': '1.0', 'units': 'g'},
            'vape': {'weight': '0.5', 'units': 'g'},
            'edible': {'weight': '10', 'units': 'mg'},
            'tincture': {'weight': '30', 'units': 'ml'},
            'topical': {'weight': '30', 'units': 'ml'}
        }
        
        return default_weights.get(product_type, {'weight': '1.0', 'units': 'g'})
    
    def _infer_price_from_type_and_weight(self, product_type: str, weight: float) -> str:
        """Infer price based on product type and weight."""
        product_type_lower = product_type.lower()
        
        if 'pre-roll' in product_type_lower:
            return '20'
        elif 'flower' in product_type_lower:
            if weight <= 1:
                return '35'
            elif weight <= 3.5:
                return '120'
            elif weight <= 7:
                return '220'
            else:
                return '400'
        elif 'concentrate' in product_type_lower:
            if weight <= 1:
                return '50'
            elif weight <= 2:
                return '90'
            else:
                return '150'
        elif 'vape' in product_type_lower:
            return '40'
        elif 'edible' in product_type_lower:
            return '25'
        else:
            return '25'
    
    def search_products_by_name(self, product_name: str) -> List[Dict]:
        """Search for products by exact product name."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Search for products with exact name match
            cursor.execute('''
                SELECT p.id, p."Product Name*", p.normalized_name, p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                       p."Description", p."Weight*", p."Units", p."Price", p."Quantity*", p."DOH", p."Concentrate Type", p."Ratio", p."JointRatio",
                       p."State", p."Is Sample? (yes/no)", p."Is MJ product?(yes/no)", p."Discountable? (yes/no)", p."Room*", p."Batch Number", p."Lot Number", p."Barcode*",
                       p."Medical Only (Yes/No)", p."Med Price", p."Expiration Date(YYYY-MM-DD)", p."Is Archived? (yes/no)", p."THC Per Serving", p."Allergens", p."Solvent", p."Accepted Date",
                       p."Internal Product Identifier", p."Product Tags (comma separated)", p."Image URL", p."Ingredients", p."CombinedWeight", p."Ratio_or_THC_CBD", 
                       p."Description_Complexity", p."Total THC", p."THCA", p."CBDA", p."CBN", p.total_occurrences, p.first_seen_date, p.last_seen_date,
                       s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p."Product Name*" = ?
                ORDER BY p.last_seen_date DESC
            ''', (product_name,))
            
            results = []
            for row in cursor.fetchall():
                product = dict(zip([col[0] for col in cursor.description], row))
                results.append(product)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching products by name: {e}")
            return []
    
    def search_products_by_strain(self, strain_name: str) -> List[Dict]:
        """Search for products by strain name."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Search for products with matching strain
            cursor.execute('''
                SELECT p.id, p."Product Name*", p.normalized_name, p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                       p."Description", p."Weight*", p."Units", p."Price", p."Quantity*", p."DOH", p."Concentrate Type", p."Ratio", p."JointRatio",
                       p."State", p."Is Sample? (yes/no)", p."Is MJ product?(yes/no)", p."Discountable? (yes/no)", p."Room*", p."Batch Number", p."Lot Number", p."Barcode*",
                       p."Medical Only (Yes/No)", p."Med Price", p."Expiration Date(YYYY-MM-DD)", p."Is Archived? (yes/no)", p."THC Per Serving", p."Allergens", p."Solvent", p."Accepted Date",
                       p."Internal Product Identifier", p."Product Tags (comma separated)", p."Image URL", p."Ingredients", p."CombinedWeight", p."Ratio_or_THC_CBD", 
                       p."Description_Complexity", p."Total THC", p."THCA", p."CBDA", p."CBN", p.total_occurrences, p.first_seen_date, p.last_seen_date,
                       s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p."Product Strain" LIKE ? OR s.strain_name LIKE ?
                ORDER BY p.last_seen_date DESC
            ''', (f'%{strain_name}%', f'%{strain_name}%'))
            
            results = []
            for row in cursor.fetchall():
                product = dict(zip([col[0] for col in cursor.description], row))
                results.append(product)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching products by strain: {e}")
            return []
    
    def search_products_by_type_and_strain(self, product_type: str, strain_name: str) -> List[Dict]:
        """Search for products by product type and strain combination."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Search for products with matching type and strain
            cursor.execute('''
                SELECT p.id, p."Product Name*", p.normalized_name, p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Lineage",
                       p."Description", p."Weight*", p."Units", p."Price", p."Quantity*", p."DOH", p."Concentrate Type", p."Ratio", p."JointRatio",
                       p."State", p."Is Sample? (yes/no)", p."Is MJ product?(yes/no)", p."Discountable? (yes/no)", p."Room*", p."Batch Number", p."Lot Number", p."Barcode*",
                       p."Medical Only (Yes/No)", p."Med Price", p."Expiration Date(YYYY-MM-DD)", p."Is Archived? (yes/no)", p."THC Per Serving", p."Allergens", p."Solvent", p."Accepted Date",
                       p."Internal Product Identifier", p."Product Tags (comma separated)", p."Image URL", p."Ingredients", p."CombinedWeight", p."Ratio_or_THC_CBD", 
                       p."Description_Complexity", p."Total THC", p."THCA", p."CBDA", p."CBN", p.total_occurrences, p.first_seen_date, p.last_seen_date,
                       s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p."Product Type*" = ? AND (p."Product Strain" = ? OR s.strain_name = ?)
                ORDER BY p.last_seen_date DESC
            ''', (product_type, strain_name, strain_name))
            
            results = []
            for row in cursor.fetchall():
                product = dict(zip([col[0] for col in cursor.description], row))
                results.append(product)
            
            return results
            
        except Exception as e:
            logging.error(f"Error searching products by type and strain: {e}")
            return []
    
    def clear_all_data(self):
        """Clear all data from the database tables."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Clear all data from tables
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM strains")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='strains'")
            
            conn.commit()
            logging.info("All database data cleared successfully")
            
        except Exception as e:
            logging.error(f"Error clearing database data: {e}")
            raise

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from the database for export."""
        try:
            self.init_database()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First, get the actual column names from the database
            cursor.execute("PRAGMA table_info(products)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Build the SELECT query dynamically based on available columns
            select_columns = []
            for col_name in column_names:
                if col_name != 'id':  # Skip id as it's handled separately
                    select_columns.append(f'p."{col_name}"')
            
            query = f'''
                SELECT p.id, {", ".join(select_columns)}
                FROM products p
                ORDER BY p.id
            '''
            
            cursor.execute(query)
            results = cursor.fetchall()
            products = []
            
            for result in results:
                product = {'id': result[0]}
                
                # Map remaining columns dynamically
                for i, col_name in enumerate(column_names[1:], 1):  # Skip id column
                    if i < len(result):
                        product[col_name] = result[i]
                    else:
                        product[col_name] = None
                
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            return []

    def get_products_dataframe(self, limit: Optional[int] = 10000) -> Optional[pd.DataFrame]:
        """Get products as DataFrame (fast path for export/download). Uses single read_sql_query."""
        try:
            self.init_database()
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(products)")
            available_columns = [row[1] for row in cursor.fetchall()]
            exclude_cols = {'normalized_name', 'Ratio_or_THC_CBD', 'Description_Complexity', 'strain_id'}
            columns_to_export = [col for col in available_columns if col not in exclude_cols]
            select_columns = ', '.join([f'"{col}"' for col in columns_to_export])
            limit_clause = f' LIMIT {int(limit)}' if limit else ''
            query = f'SELECT {select_columns} FROM products ORDER BY id{limit_clause}'
            return pd.read_sql_query(query, conn)
        except Exception as e:
            logger.error(f"Error getting products DataFrame: {e}")
            return None
    
    def update_all_product_strains(self) -> Dict[str, Any]:
        """Update all existing Product Strain column values using the _calculate_product_strain logic."""
        try:
            self.init_database()
            
            with self._write_lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Get all products with their data
                cursor.execute('''
                    SELECT id, "Product Type*", "Product Name*", "Description", "Ratio"
                    FROM products
                ''')
                products = cursor.fetchall()
                
                updated_count = 0
                for product_id, product_type, product_name, description, ratio in products:
                    # Calculate the correct Product Strain value
                    new_strain = self._calculate_product_strain_original(
                        product_type or '',
                        product_name or '',
                        description or '',
                        ratio or ''
                    )
                    
                    # Update the product
                    cursor.execute('''
                        UPDATE products 
                        SET "Product Strain" = ?
                        WHERE id = ?
                    ''', (new_strain, product_id))
                    updated_count += 1
                
                conn.commit()
                logger.info(f"Updated {updated_count} product strains")
                
                return {
                    'success': True,
                    'updated_count': updated_count,
                    'message': f'Successfully updated {updated_count} product strains'
                }
                
        except Exception as e:
            logger.error(f"Error updating product strains: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update product strains: {e}'
            }
    
    def update_all_ratio_or_thc_cbd(self) -> Dict[str, Any]:
        """Update all existing Ratio_or_THC_CBD column values using the _calculate_ratio_or_thc_cbd logic."""
        try:
            self.init_database()
            
            with self._write_lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Get all products with their THC/CBD values and Ratio column
                cursor.execute('''
                    SELECT id, "Product Name*", "Product Type*", "THC test result", "CBD test result", "Ratio", "Ratio_or_THC_CBD"
                    FROM products
                ''')
                products = cursor.fetchall()
                
                updated_count = 0
                for product_id, product_name, product_type, thc_value, cbd_value, ratio_value, current_ratio in products:
                    # Only update if current value is placeholder or doesn't contain actual values
                    if (current_ratio in ['THC: | BR | C', 'THC: CBD:', 'THC:\nCBD:', '', "'THC: | BR | C'"] or 
                        (current_ratio and 'THC:' in current_ratio and 'CBD:' in current_ratio and '%' not in current_ratio) or
                        (current_ratio and current_ratio.strip() == 'THC: | BR | C') or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'") or
                        (current_ratio and current_ratio.strip() == "'THC: | BR | C'")):
                        # Use the proper calculation method based on product type
                        new_ratio = self._calculate_ratio_or_thc_cbd(
                            product_type, 
                            ratio_value,  # Use Ratio column for non-classic types
                            '',  # joint_ratio not used in this context
                            product_name,
                            str(thc_value) if thc_value else '',  # Pass THC value for classic types
                            str(cbd_value) if cbd_value else ''   # Pass CBD value for classic types
                        )
                        
                        # Update the product
                        cursor.execute('''
                            UPDATE products 
                            SET "Ratio_or_THC_CBD" = ?
                            WHERE id = ?
                        ''', (new_ratio, product_id))
                        updated_count += 1
                
                conn.commit()
                logger.info(f"Updated {updated_count} ratio_or_thc_cbd values")
                
                return {
                    'success': True,
                    'updated_count': updated_count,
                    'message': f'Successfully updated {updated_count} ratio_or_thc_cbd values'
                }
                
        except Exception as e:
            logger.error(f"Error updating ratio_or_thc_cbd: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update ratio_or_thc_cbd: {e}'
            }
    
    def update_all_joint_ratios(self) -> Dict[str, Any]:
        """Update all JointRatio values to remove ' x 1' suffix."""
        try:
            self.init_database()
            
            with self._write_lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Get all products with JointRatio values
                cursor.execute('''
                    SELECT id, "JointRatio"
                    FROM products
                    WHERE "JointRatio" LIKE '% x 1'
                ''')
                products = cursor.fetchall()
                
                updated_count = 0
                for product_id, joint_ratio in products:
                    # Remove ' x 1' from the end
                    new_joint_ratio = joint_ratio.replace(' x 1', '')
                    
                    # Update the product
                    cursor.execute('''
                        UPDATE products 
                        SET "JointRatio" = ?
                        WHERE id = ?
                    ''', (new_joint_ratio, product_id))
                    updated_count += 1
                
                conn.commit()
                logger.info(f"Updated {updated_count} joint ratios")
                
                return {
                    'success': True,
                    'updated_count': updated_count,
                    'message': f'Successfully updated {updated_count} joint ratios'
                }
                
        except Exception as e:
            logger.error(f"Error updating joint ratios: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to update joint ratios: {e}'
            }

    def _calculate_product_strain(self, product_type='', product_name='', description='', ratio=''):
        """Calculate Product Strain from individual parameters (overloaded version)."""
        try:
            # Call the original method with the provided parameters
            return self._calculate_product_strain_original(product_type, product_name, description, ratio)
                
        except Exception as e:
            print(f"Error in _calculate_product_strain: {e}")
            return 'Mixed'

def get_product_database(store_name=None):
    """Get a ProductDatabase instance for the specified store."""
    return ProductDatabase(store_name=store_name) 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ProductDatabase admin tools")
    parser.add_argument('--update-canonical-to-mode', action='store_true', help='Update all canonical lineages to mode lineage')
    args = parser.parse_args()
    if args.update_canonical_to_mode:
        # CRITICAL FIX: Use correct database path
        db = ProductDatabase(get_database_path())
        db.update_all_canonical_lineages_to_mode()
        # Canonical lineages updated to mode for all strains. 
