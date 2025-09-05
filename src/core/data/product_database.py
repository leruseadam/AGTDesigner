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

def get_database_path():
    """Get the correct database path for ProductDatabase instances."""
    # Get the current directory of this file
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(current_dir, 'uploads', 'product_database.db')

logger = logging.getLogger(__name__)

# Performance optimization: disable debug logging in production
DEBUG_ENABLED = False

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
    
    def __init__(self, db_path: str = "product_database.db"):
        self.db_path = db_path
        self._connection_pool = {}
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._initialized = False
        self._init_lock = threading.Lock()
        # Serialize writers to avoid 'database is locked' under concurrent writes
        self._write_lock = threading.RLock()
        
        # Performance timing
        self._timing_stats = {
            'queries': 0,
            'total_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _get_connection(self):
        """Get a database connection, reusing if possible."""
        thread_id = threading.get_ident()
        if thread_id not in self._connection_pool:
            # Configure connection for better concurrency
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30 second timeout for database operations
                check_same_thread=False  # Allow connection sharing across threads
            )
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            # Set busy timeout (60s) to ride out background batches
            conn.execute("PRAGMA busy_timeout=60000")
            # Optimize for concurrent access
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self._connection_pool[thread_id] = conn
        return self._connection_pool[thread_id]
    
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
                
                # Create products table with all necessary columns for Excel data
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
                        weight TEXT,
                        units TEXT,
                        price TEXT,
                        lineage TEXT,
                        first_seen_date TEXT NOT NULL,
                        last_seen_date TEXT NOT NULL,
                        total_occurrences INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        product_strain TEXT,
                        quantity TEXT,
                        doh_compliant TEXT,
                        concentrate_type TEXT,
                        ratio TEXT,
                        joint_ratio TEXT,
                        thc_test_result TEXT,
                        cbd_test_result TEXT,
                        test_result_unit TEXT,
                        state TEXT,
                        is_sample TEXT,
                        is_mj_product TEXT,
                        discountable TEXT,
                        room TEXT,
                        batch_number TEXT,
                        lot_number TEXT,
                        barcode TEXT,
                        cost TEXT,
                        medical_only TEXT,
                        med_price TEXT,
                        expiration_date TEXT,
                        is_archived TEXT,
                        thc_per_serving TEXT,
                        allergens TEXT,
                        solvent TEXT,
                        accepted_date TEXT,
                        internal_product_identifier TEXT,
                        product_tags TEXT,
                        image_url TEXT,
                        ingredients TEXT,
                        -- Additional Excel columns for comprehensive JSON matching
                        combined_weight TEXT,
                        ratio_or_thc_cbd TEXT,
                        description_complexity TEXT,
                        total_thc TEXT,
                        thca TEXT,
                        cbda TEXT,
                        cbn TEXT,
                        -- Terpene columns for comprehensive product data
                        a_bisabolol_mg_g TEXT,
                        a_humulene_mg_g TEXT,
                        a_maaliene_mg_g TEXT,
                        a_myrcene_mg_g TEXT,
                        a_pinene_mg_g TEXT,
                        b_caryophyllene_mg_g TEXT,
                        b_myrcene_mg_g TEXT,
                        b_pinene_mg_g TEXT,
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
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products(vendor, brand)')
                
                conn.commit()
                
                # Check if we need to add missing columns (migration)
                # Only migrate if tables are empty or missing critical columns
                self._migrate_database_schema_safe(cursor, conn)
                
                self._initialized = True
                
                elapsed = time.time() - start_time
                logger.info(f"Product database initialized successfully in {elapsed:.3f}s")
                
            except Exception as e:
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
                    product_name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    strain_id INTEGER,
                    product_type TEXT NOT NULL,
                    vendor TEXT,
                    brand TEXT,
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
                    product_strain TEXT,
                    quantity TEXT,
                    doh_compliant TEXT,
                    concentrate_type TEXT,
                    ratio TEXT,
                    joint_ratio TEXT,
                    thc_test_result TEXT,
                    cbd_test_result TEXT,
                    test_result_unit TEXT,
                    state TEXT,
                    is_sample TEXT,
                    is_mj_product TEXT,
                    discountable TEXT,
                    room TEXT,
                    batch_number TEXT,
                    lot_number TEXT,
                    barcode TEXT,
                    cost TEXT,
                    medical_only TEXT,
                    med_price TEXT,
                    expiration_date TEXT,
                    is_archived TEXT,
                    thc_per_serving TEXT,
                    allergens TEXT,
                    solvent TEXT,
                    accepted_date TEXT,
                    internal_product_identifier TEXT,
                    product_tags TEXT,
                    image_url TEXT,
                    ingredients TEXT,
                    -- Additional Excel columns for comprehensive JSON matching
                    combined_weight TEXT,
                    ratio_or_thc_cbd TEXT,
                    description_complexity TEXT,
                    total_thc TEXT,
                    thca TEXT,
                    cbda TEXT,
                    cbn TEXT,
                    -- Terpene columns for comprehensive product data
                    a_bisabolol_mg_g TEXT,
                    a_humulene_mg_g TEXT,
                    a_maaliene_mg_g TEXT,
                    a_myrcene_mg_g TEXT,
                    a_pinene_mg_g TEXT,
                    b_caryophyllene_mg_g TEXT,
                    b_myrcene_mg_g TEXT,
                    b_pinene_mg_g TEXT,
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
                    FOREIGN KEY (strain_id) REFERENCES strains (id),
                    UNIQUE(product_name, vendor, brand)
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
            cursor.execute('CREATE INDEX idx_products_vendor_brand ON products(vendor, brand)')
            
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
            cursor.execute('''
                SELECT lineage, COUNT(*) as count
                FROM products
                WHERE strain_id = ? AND lineage IS NOT NULL AND lineage != ''
                GROUP BY lineage
                ORDER BY count DESC
                LIMIT 1
            ''', (strain_id,))
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
        # Get all strains
        cursor.execute('SELECT id, strain_name, canonical_lineage FROM strains')
        strains = cursor.fetchall()
        updated = 0
        for strain_id, strain_name, canonical_lineage in strains:
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
        """Add a new strain or update existing strain information. If sovereign is True, set sovereign_lineage."""
        try:
            self.init_database()  # Ensure DB is initialized
            normalized_name = self._normalize_strain_name(strain_name)
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
                    SELECT id, canonical_lineage, total_occurrences, lineage_confidence, sovereign_lineage
                    FROM strains 
                    WHERE normalized_name = ?
                ''', (normalized_name,))
                existing = cursor.fetchone()
                
                if existing:
                    strain_id, existing_lineage, occurrences, confidence, existing_sovereign = existing
                    new_occurrences = occurrences + 1
                    # Update lineage if provided and different
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
                        
                        # Notify all sessions of the lineage update (non-blocking)
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
                    # Sovereign lineage update
                    if sovereign and lineage:
                        cursor.execute('''
                            UPDATE strains SET sovereign_lineage = ? WHERE id = ?
                        ''', (lineage, strain_id))
                        
                        # Notify all sessions of the sovereign lineage update (non-blocking)
                        try:
                            from .database_notifier import notify_sovereign_lineage_set
                            notify_sovereign_lineage_set(strain_name, lineage)
                        except Exception as notify_error:
                            logger.warning(f"Failed to notify sovereign lineage update: {notify_error}")
                        
                    conn.commit()
                    cache_key = self._get_cache_key("strain_info", normalized_name)
                    with self._cache_lock:
                        if cache_key in self._cache:
                            del self._cache[cache_key]
                    return strain_id
                else:
                    cursor.execute('''
                        INSERT INTO strains (strain_name, normalized_name, canonical_lineage, first_seen_date, last_seen_date, created_at, updated_at, sovereign_lineage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (strain_name, normalized_name, lineage, current_date, current_date, current_date, current_date, lineage if sovereign else None))
                    strain_id = cursor.lastrowid
                    conn.commit()
                    
                    # Notify all sessions of the new strain (non-blocking)
                    try:
                        from .database_notifier import notify_strain_add
                        notify_strain_add(strain_name, {
                            'lineage': lineage,
                            'sovereign': sovereign,
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
            
            product_name = product_data.get('ProductName', '')
            normalized_name = self._normalize_product_name(product_name)
            current_date = datetime.now().isoformat()
            
            # Get or create strain
            strain_name = product_data.get('Product Strain', '')
            strain_id = None
            if strain_name:
                strain_id = self.add_or_update_strain(strain_name, product_data.get('Lineage'))
            
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
                # First check exact match (name + vendor + brand)
                cursor.execute('''
                    SELECT id, total_occurrences, product_name
                    FROM products 
                    WHERE normalized_name = ? AND vendor = ? AND brand = ?
                ''', (normalized_name, product_data.get('vendor'), product_data.get('brand')))
                
                existing = cursor.fetchone()
                
                if existing:
                    product_id, occurrences, existing_name = existing
                    
                    # Log duplicate detection
                    logger.info(f"Found existing product: '{existing_name}' (ID: {product_id}, occurrences: {occurrences})")
                    
                    # Update existing product
                    new_occurrences = occurrences + 1
                    cursor.execute('''
                        UPDATE products 
                        SET total_occurrences = ?, last_seen_date = ?, updated_at = ?
                        WHERE id = ?
                    ''', (new_occurrences, current_date, current_date, product_id))
                    
                    conn.commit()
                    logger.info(f"Updated existing product '{existing_name}' - new occurrence count: {new_occurrences}")
                    return product_id
                
                # Check for similar products (same name + vendor, different brand)
                cursor.execute('''
                    SELECT id, total_occurrences, product_name, brand
                    FROM products 
                    WHERE normalized_name = ? AND vendor = ? AND brand != ?
                ''', (normalized_name, product_data.get('vendor'), product_data.get('brand')))
                
                similar_products = cursor.fetchall()
                if similar_products:
                    logger.info(f"Found {len(similar_products)} similar products with same name '{product_name}' and vendor '{product_data.get('Vendor')}' but different brands")
                    for similar_id, similar_occurrences, similar_name, similar_brand in similar_products:
                        logger.debug(f"Similar product: '{similar_name}' (Brand: {similar_brand}, ID: {similar_id})")
                else:
                    # Add new product with essential columns only
                    cursor.execute('''
                        INSERT INTO products (
                            product_name, normalized_name, product_strain, product_type, vendor, brand,
                            description, weight, units, price, lineage, first_seen_date, last_seen_date, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product_name, normalized_name, product_data.get('product_strain'), product_data.get('product_type'),
                        product_data.get('vendor'), product_data.get('brand'),
                        product_data.get('description'), product_data.get('weight'),
                        product_data.get('units'), product_data.get('price'),
                        product_data.get('lineage'), current_date, current_date, current_date, current_date
                    ))
                    
                    product_id = cursor.lastrowid
                    conn.commit()
                    if DEBUG_ENABLED:
                        logger.debug(f"Added new product '{product_name}'")
                    return product_id
                    
        except Exception as e:
            logger.error(f"Error adding/updating product '{product_data.get('ProductName', '')}': {e}")
            raise
    
    def store_excel_data(self, df: pd.DataFrame, source_file: str = None) -> Dict[str, Any]:
        """Store Excel data in the database. This is the main method for storing uploaded Excel files."""
        try:
            self.init_database()  # Ensure DB is initialized
            logger.info(f"Starting to store Excel data with {len(df)} rows from {source_file}")
            
            if df is None or df.empty:
                logger.warning("No data to store - DataFrame is empty")
                return {'stored': 0, 'updated': 0, 'errors': 0, 'message': 'No data to store'}
            
            # Enhanced JSON match detection and filtering
            filtered_df = self._filter_json_matched_tags(df)
            
            if filtered_df.empty:
                logger.warning("All data was filtered out as JSON matched tags - nothing to store")
                return {
                    'stored': 0, 
                    'updated': 0, 
                    'errors': 0, 
                    'excluded_json_matches': len(df),
                    'message': f'All {len(df)} rows were JSON matched tags - excluded from database storage'
                }
            
            # Initialize duplicate tracking for this upload
            self._current_upload_products = set()
            
            stored_count = 0
            updated_count = 0
            error_count = 0
            errors = []
            
            # Process each row in the filtered DataFrame
            for index, row in filtered_df.iterrows():
                try:
                    # Convert row to dictionary and handle NaN values
                    row_dict = {}
                    for col in filtered_df.columns:
                        value = row[col]
                        if pd.isna(value):
                            row_dict[col] = None
                        else:
                            row_dict[col] = str(value).strip() if isinstance(value, str) else value
                    
                    # Map to database columns correctly
                    product_data = {
                        'ProductName': row_dict.get('ProductName', ''),
                        'Product Type*': row_dict.get('Product Type*', ''),
                        'Lineage': row_dict.get('Lineage', ''),
                        'Vendor': row_dict.get('Vendor/Supplier*', row_dict.get('Vendor', '')),  # Map to correct column
                        'Product Brand': row_dict.get('Product Brand', ''),
                        'Description': row_dict.get('Description', ''),
                        'Weight*': row_dict.get('Weight*', ''),
                        'Units': row_dict.get('Units', ''),
                        'Price': row_dict.get('Price', ''),
                        'Product Strain': row_dict.get('Product Strain', ''),
                        'Quantity*': row_dict.get('Quantity*', ''),
                        'DOH': row_dict.get('DOH', ''),
                        'Concentrate Type': row_dict.get('Concentrate Type', ''),
                        'Ratio': row_dict.get('Ratio', ''),
                        'JointRatio': row_dict.get('JointRatio', ''),
                        'THC test result': row_dict.get('THC test result', ''),
                        'CBD test result': row_dict.get('CBD test result', ''),
                        'Test result unit (% or mg)': row_dict.get('Test result unit (% or mg)', ''),
                        'State': row_dict.get('State', ''),
                        'Is Sample? (yes/no)': row_dict.get('Is Sample? (yes/no)', ''),
                        'Is MJ product?(yes/no)': row_dict.get('Is MJ product?(yes/no)', ''),
                        'Discountable? (yes/no)': row_dict.get('Discountable? (yes/no)', ''),
                        'Room*': row_dict.get('Room*', ''),
                        'Batch Number': row_dict.get('Batch Number', ''),
                        'Lot Number': row_dict.get('Lot Number', ''),
                        'Barcode*': row_dict.get('Barcode*', ''),
                        'Cost*': row_dict.get('Cost*', ''),
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
                        'THCA': row_dict.get('THCA', ''),
                        'CBDA': row_dict.get('CBDA', ''),
                        'CBN': row_dict.get('CBN', ''),
                        'Ratio_or_THC_CBD': row_dict.get('Ratio_or_THC_CBD', ''),
                        'Vendor/Supplier*': row_dict.get('Vendor/Supplier*', ''),
                        'Vendor/Supplier': row_dict.get('Vendor/Supplier', ''),
                        'Product Name*': row_dict.get('Product Name*', ''),
                        'Product Name': row_dict.get('Product Name', ''),
                        'Quantity Received*': row_dict.get('Quantity Received*', ''),
                        'WeightWithUnits': row_dict.get('WeightWithUnits', ''),
                        'WeightUnits': row_dict.get('WeightUnits', ''),
                        'ProductBrand': row_dict.get('ProductBrand', ''),
                        'ProductBrandCenter': row_dict.get('ProductBrandCenter', ''),
                        'THC_CBD': row_dict.get('THC_CBD', ''),
                        'AI': row_dict.get('AI', ''),
                        'AJ': row_dict.get('AJ', ''),
                        'AK': row_dict.get('AK', ''),
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
                    
                    # Skip rows with only whitespace or special characters
                    if str(product_name).strip() == '' or len(str(product_name).strip()) < 2:
                        logger.warning(f"Row {index + 1}: Skipping product name too short or only whitespace: '{product_name}'")
                        continue
                    
                    # Update the product data with the found name
                    product_data['ProductName'] = str(product_name).strip()
                    
                    # Additional validation: Skip rows with missing essential data
                    vendor = product_data.get('Vendor', '').strip()
                    product_type = product_data.get('Product Type*', '').strip()
                    
                    if not vendor or str(vendor).lower() in ['nan', 'none', 'null', '']:
                        logger.warning(f"Row {index + 1}: Skipping product '{product_name}' - missing vendor information")
                        continue
                    
                    if not product_type or str(product_type).lower() in ['nan', 'none', 'null', '']:
                        logger.warning(f"Row {index + 1}: Skipping product '{product_name}' - missing product type")
                        continue
                    
                    # Skip duplicate entries within the same upload (same name + vendor + type combination)
                    duplicate_key = f"{product_name}|{vendor}|{product_type}"
                    if duplicate_key in self._current_upload_products:
                        logger.warning(f"Row {index + 1}: Skipping duplicate product '{product_name}' from same vendor '{vendor}' and type '{product_type}'")
                        continue
                    
                    # Track this product to prevent duplicates within the same upload
                    self._current_upload_products.add(duplicate_key)
                    
                    # Store the product in database
                    product_id = self.add_or_update_product(product_data)
                    if product_id:
                        stored_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 1}: Failed to store product")
                        
                except Exception as row_error:
                    error_count += 1
                    errors.append(f"Row {index + 1}: {str(row_error)}")
                    logger.error(f"Error processing row {index + 1}: {row_error}")
                    continue
            
            # Calculate excluded counts
            excluded_count = len(df) - len(filtered_df)
            blank_entries_skipped = len(df) - len(filtered_df) - excluded_count
            
            result = {
                'stored': stored_count,
                'updated': updated_count,
                'errors': error_count,
                'excluded_json_matches': excluded_count,
                'blank_entries_skipped': blank_entries_skipped,
                'total_rows': len(df),
                'filtered_rows': len(filtered_df),
                'source_file': source_file,
                'message': f'Successfully stored {stored_count} products with {error_count} errors, excluded {excluded_count} JSON matched tags, skipped {blank_entries_skipped} blank entries'
            }
            
            if errors:
                result['error_details'] = errors[:10]  # Limit error details to first 10
            
            logger.info(f"Excel data storage completed: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing Excel data: {e}")
            return {'stored': 0, 'updated': 0, 'errors': 1, 'excluded_json_matches': 0, 'message': f'Storage failed: {str(e)}'}
    
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
                WHERE product_name IS NULL 
                   OR product_name = '' 
                   OR product_name = 'nan' 
                   OR product_name = 'None' 
                   OR product_name = 'null'
                   OR LENGTH(TRIM(product_name)) < 2
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
                WHERE product_name IS NULL 
                   OR product_name = '' 
                   OR product_name = 'nan' 
                   OR product_name = 'None' 
                   OR product_name = 'null'
                   OR LENGTH(TRIM(product_name)) < 2
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
                        # Look for JSON match indicators in Source column
                        json_match_mask |= filtered_df[col].astype(str).str.contains(
                            'JSON Match|AI Match|JSON|AI|Match|Generated', 
                            case=False, 
                            na=False
                        )
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
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, strain_name, canonical_lineage, total_occurrences, lineage_confidence, first_seen_date, last_seen_date, sovereign_lineage
                FROM strains 
                WHERE normalized_name = ?
            ''', (normalized_name,))
            result = cursor.fetchone()
            if result:
                strain_id = result[0]
                sovereign_lineage = result[7]
                canonical_lineage = result[2]
                # Use sovereign_lineage if set, else mode, else canonical
                display_lineage = None
                if sovereign_lineage and sovereign_lineage.strip():
                    display_lineage = sovereign_lineage
                else:
                    mode_lineage = self.get_mode_lineage(strain_id)
                    if mode_lineage:
                        display_lineage = mode_lineage
                    else:
                        display_lineage = canonical_lineage
                strain_info = {
                    'id': result[0],
                    'strain_name': result[1],
                    'canonical_lineage': canonical_lineage,
                    'total_occurrences': result[3],
                    'lineage_confidence': result[4],
                    'first_seen_date': result[5],
                    'last_seen_date': result[6],
                    'sovereign_lineage': sovereign_lineage,
                    'display_lineage': display_lineage
                }
                self._set_cache(cache_key, strain_info, ttl=300)
                return strain_info
            return None
        except Exception as e:
            logger.error(f"Error getting strain info for '{strain_name}': {e}")
            return None
    
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
            
            if vendor and brand:
                cursor.execute('''
                    SELECT p.id, p.product_name, p.product_type, p.vendor, p.brand, p.lineage,
                           s.strain_name, s.canonical_lineage, p.total_occurrences, p.first_seen_date, p.last_seen_date,
                           p.description, p.weight, p.units, p.price
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE p.normalized_name = ? AND p.vendor = ? AND p.brand = ?
                ''', (normalized_name, vendor, brand))
            else:
                cursor.execute('''
                    SELECT p.id, p.product_name, p.product_type, p.vendor, p.brand, p.lineage,
                           s.strain_name, s.canonical_lineage, p.total_occurrences, p.first_seen_date, p.last_seen_date,
                           p.description, p.weight, p.units, p.price
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE p.normalized_name = ?
                ''', (normalized_name,))
            
            result = cursor.fetchone()
            if result:
                product_info = {
                    'id': result[0],
                    'product_name': result[1],
                    'product_type': result[2],
                    'vendor': result[3],
                    'brand': result[4],
                    'lineage': result[5],
                    'strain_name': result[6],
                    'canonical_lineage': result[7],
                    'total_occurrences': result[8],
                    'first_seen_date': result[9],
                    'last_seen_date': result[10],
                    'description': result[11],
                    'weight': result[12],
                    'units': result[13],
                    'price': result[14]
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
        """Export database to Excel file."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Add missing columns if they don't exist
            self._add_missing_columns_safe(cursor, conn)
            
            # Export strains
            strains_df = pd.read_sql_query('''
                SELECT strain_name, canonical_lineage, total_occurrences, first_seen_date, last_seen_date
                FROM strains
                ORDER BY total_occurrences DESC
            ''', conn)
            
            # Export products with all columns - handle missing columns gracefully
            try:
                products_df = pd.read_sql_query('''
                    SELECT p.product_name, p.product_type, p.vendor, p.brand, p.lineage,
                           s.strain_name, p.total_occurrences, p.first_seen_date, p.last_seen_date,
                           p.description, p.weight, p.units, p.price, p.product_strain, p.quantity,
                           p.doh_compliant, p.concentrate_type, p.ratio, p.joint_ratio,
                           p.thc_test_result, p.cbd_test_result, p.test_result_unit, p.state,
                           p.is_sample, p.is_mj_product, p.discountable, p.room, p.batch_number,
                           p.lot_number, p.barcode, p.cost, p.medical_only, p.med_price,
                           p.expiration_date, p.is_archived, p.thc_per_serving, p.allergens,
                           p.solvent, p.accepted_date, p.internal_product_identifier, p.product_tags,
                           p.image_url, p.ingredients
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    ORDER BY p.total_occurrences DESC
                ''', conn)
            except Exception as e:
                # Fallback to basic columns if some are missing
                logger.warning(f"Full export failed, using fallback columns: {e}")
                products_df = pd.read_sql_query('''
                    SELECT p.product_name, p.product_type, p.vendor, p.brand, p.lineage,
                           s.strain_name, p.total_occurrences, p.first_seen_date, p.last_seen_date,
                           p.description, p.weight, p.units, p.price
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    ORDER BY p.total_occurrences DESC
                ''', conn)
            
            # Export to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                strains_df.to_excel(writer, sheet_name='Strains', index=False)
                products_df.to_excel(writer, sheet_name='Products', index=False)
            
            logger.info(f"Database exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            raise
    
    def _add_missing_columns_safe(self, cursor, conn):
        """Safely add missing columns to existing tables without losing data."""
        try:
            # Check and add missing columns to products table
            cursor.execute("PRAGMA table_info(products)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            missing_columns = []
            
            # Define all expected columns
            expected_columns = [
                ('product_strain', 'TEXT'),
                ('quantity', 'TEXT'),
                ('doh_compliant', 'TEXT'),
                ('concentrate_type', 'TEXT'),
                ('ratio', 'TEXT'),
                ('joint_ratio', 'TEXT'),
                ('thc_test_result', 'TEXT'),
                ('cbd_test_result', 'TEXT'),
                ('test_result_unit', 'TEXT'),
                ('state', 'TEXT'),
                ('is_sample', 'TEXT'),
                ('is_mj_product', 'TEXT'),
                ('discountable', 'TEXT'),
                ('room', 'TEXT'),
                ('batch_number', 'TEXT'),
                ('lot_number', 'TEXT'),
                ('barcode', 'TEXT'),
                ('cost', 'TEXT'),
                ('medical_only', 'TEXT'),
                ('med_price', 'TEXT'),
                ('expiration_date', 'TEXT'),
                ('is_archived', 'TEXT'),
                ('thc_per_serving', 'TEXT'),
                ('allergens', 'TEXT'),
                ('solvent', 'TEXT'),
                ('accepted_date', 'TEXT'),
                ('internal_product_identifier', 'TEXT'),
                ('product_tags', 'TEXT'),
                ('image_url', 'TEXT'),
                ('ingredients', 'TEXT'),
                ('combined_weight', 'TEXT'),
                ('ratio_or_thc_cbd', 'TEXT'),
                ('description_complexity', 'TEXT'),
                ('total_thc', 'TEXT'),
                ('thca', 'TEXT'),
                ('cbda', 'TEXT'),
                ('cbn', 'TEXT'),
                # Terpene columns
                ('a_bisabolol_mg_g', 'TEXT'),
                ('a_humulene_mg_g', 'TEXT'),
                ('a_maaliene_mg_g', 'TEXT'),
                ('a_myrcene_mg_g', 'TEXT'),
                ('a_pinene_mg_g', 'TEXT'),
                ('b_caryophyllene_mg_g', 'TEXT'),
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
                if col_name not in existing_columns:
                    missing_columns.append((col_name, col_type))
            
            # Add missing columns
            for col_name, col_type in missing_columns:
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                    logger.info(f"Added missing column: {col_name}")
                except Exception as e:
                    logger.warning(f"Could not add column {col_name}: {e}")
            
            if missing_columns:
                conn.commit()
                logger.info(f"Added {len(missing_columns)} missing columns to products table")
            
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
        """Get a mapping of normalized strain names to their canonical lineages."""
        try:
            self.init_database()  # Ensure DB is initialized
            
            cache_key = self._get_cache_key("strain_lineage_map")
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT normalized_name, canonical_lineage FROM strains WHERE canonical_lineage IS NOT NULL')
            
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
            current_date = datetime.now().isoformat()
            
            # Update by product name, vendor, and brand if provided
            if vendor and brand:
                cursor.execute('''
                    UPDATE products
                    SET lineage = ?, updated_at = ?
                    WHERE normalized_name = ? AND vendor = ? AND brand = ?
                ''', (new_lineage, current_date, normalized_name, vendor, brand))
                logger.info(f"Updated lineage for product '{product_name}' (vendor={vendor}, brand={brand}) to '{new_lineage}'")
            else:
                cursor.execute('''
                    UPDATE products
                    SET lineage = ?, updated_at = ?
                    WHERE normalized_name = ?
                ''', (new_lineage, current_date, normalized_name))
                logger.info(f"Updated lineage for product '{product_name}' to '{new_lineage}'")
            
            conn.commit()
            rows_updated = cursor.rowcount
            if rows_updated == 0:
                logger.warning(f"No product found in database to update: '{product_name}' (vendor={vendor}, brand={brand})")
            return rows_updated > 0
        except Exception as e:
            logger.error(f"Error updating product lineage for '{product_name}': {e}")
            return False 

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
                cursor.execute('''
                    SELECT p.lineage FROM products p
                    WHERE p.strain_id = (
                        SELECT id FROM strains WHERE normalized_name = ?
                    ) AND p.vendor = ? AND p.brand = ?
                    ORDER BY p.total_occurrences DESC
                    LIMIT 1
                ''', (self._normalize_strain_name(strain_name), vendor, brand))
                
                result = cursor.fetchone()
                if result and result[0]:
                    logger.debug(f"Found product-specific lineage for {strain_name} + {vendor} + {brand}: {result[0]}")
                    return result[0]
            
            # Fallback to canonical lineage from strains table
            strain_info = self.get_strain_info(strain_name)
            if strain_info and strain_info.get('canonical_lineage'):
                logger.debug(f"Using canonical lineage for {strain_name}: {strain_info['canonical_lineage']}")
                return strain_info['canonical_lineage']
            
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
                SELECT product_name, product_type, vendor, brand, description, weight, units, price, lineage,
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
                    SELECT product_name, product_type, vendor, brand, description, weight, units, price, lineage,
                           total_occurrences, first_seen_date, last_seen_date
                    FROM products 
                    WHERE strain_id = ? AND brand = ?
                    ORDER BY total_occurrences DESC
                ''', (strain_id, brand))
            else:
                cursor.execute('''
                    SELECT product_name, product_type, vendor, brand, description, weight, units, price, lineage,
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
            
            cursor.execute(f'''
                SELECT p.id, p.product_name, p.normalized_name, p.product_type, p.vendor, p.brand, p.lineage,
                       s.strain_name, s.canonical_lineage, p.total_occurrences, p.first_seen_date, p.last_seen_date,
                       p.description, p.weight, p.units, p.price, p.thc_test_result, p.cbd_test_result, p.test_result_unit,
                       p.quantity, p.doh_compliant, p.concentrate_type, p.ratio, p.joint_ratio, p.state, p.is_sample,
                       p.is_mj_product, p.discountable, p.room, p.batch_number, p.lot_number, p.barcode, p.cost,
                       p.medical_only, p.med_price, p.expiration_date, p.is_archived, p.thc_per_serving, p.allergens,
                       p.solvent, p.accepted_date, p.internal_product_identifier, p.product_tags, p.image_url, p.ingredients,
                       p.combined_weight, p.ratio_or_thc_cbd, p.description_complexity, p.total_thc, p.thca, p.cbda, p.cbn
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p.normalized_name IN ({placeholders})
            ''', normalized_names)
            
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
                        'Lineage': result[6] or result[8] or 'MIXED',  # lineage or canonical_lineage
                        'strain_name': result[7],  # strain_name
                        'canonical_lineage': result[8],  # canonical_lineage
                        'total_occurrences': result[9],
                        'first_seen_date': result[10],
                        'last_seen_date': result[11],
                        'Description': result[12] or result[1],  # description or product_name
                        'Weight*': result[13],  # weight
                        'Units': result[14],  # units
                        'Price': result[15],  # price
                        'THC test result': result[16],  # thc_test_result
                        'CBD test result': result[17],  # cbd_test_result
                        'Test result unit': result[18],  # test_result_unit
                        'Quantity*': result[19],  # quantity
                        'DOH': result[20],  # doh_compliant
                        'concentrate_type': result[21],  # concentrate_type
                        'Ratio': result[22],  # ratio
                        'JointRatio': result[23],  # joint_ratio
                        'State': result[24],  # state
                        'Is Sample?': result[25],  # is_sample
                        'Is MJ product?': result[26],  # is_mj_product
                        'Discountable?': result[27],  # discountable
                        'Room*': result[28],  # room
                        'batch_number': result[29],  # batch_number
                        'lot_number': result[30],  # lot_number
                        'barcode': result[31],  # barcode
                        'cost': result[32],  # cost
                        'Medical Only': result[33],  # medical_only
                        'med_price': result[34],  # med_price
                        'expiration_date': result[35],  # expiration_date
                        'is_archived': result[36],  # is_archived
                        'thc_per_serving': result[37],  # thc_per_serving
                        'allergens': result[38],  # allergens
                        'solvent': result[39],  # solvent
                        'accepted_date': result[40],  # accepted_date
                        'internal_product_identifier': result[41],  # internal_product_identifier
                        'product_tags': result[42],  # product_tags
                        'image_url': result[43],  # image_url
                        'ingredients': result[44],  # ingredients
                        'combined_weight': result[45],  # combined_weight
                        'ratio_or_thc_cbd': result[46],  # ratio_or_thc_cbd
                        'description_complexity': result[47],  # description_complexity
                        'Total THC': result[48],  # total_thc
                        'THCA': result[49],  # thca
                        'CBDA': result[50],  # cbda
                        'CBN': result[51],  # cbn
                        # Add Excel column name compatibility fields
                        'ProductName': result[1],
                        'ProductBrand': result[5],
                        'ProductStrain': result[7],
                        'WeightWithUnits': f"{result[13]}{result[14]}" if result[13] and result[14] else result[13] or result[14] or '',
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
                SELECT p.id, p.product_name, p.product_strain, p.product_type, p.vendor, p.brand, p.lineage,
                       p.description, p.weight, p.units, p.price, p.quantity, p.doh_compliant, p.concentrate_type, p.ratio, p.joint_ratio,
                       p.state, p.is_sample, p.is_mj_product, p.discountable, p.room, p.batch_number, p.lot_number, p.barcode, p.cost,
                       p.medical_only, p.med_price, p.expiration_date, p.is_archived, p.thc_per_serving, p.allergens, p.solvent, p.accepted_date,
                       p.internal_product_identifier, p.product_tags, p.image_url, p.ingredients, p.combined_weight, p.ratio_or_thc_cbd, 
                       p.description_complexity, p.total_thc, p.thca, p.cbda, p.cbn, p.total_occurrences, p.first_seen_date, p.last_seen_date
                FROM products p
                WHERE 1=1
            '''
            
            params = []
            
            # Add search conditions with priority using actual column names
            if normalized_name:
                # Exact name match (highest priority)
                query += " AND (p.product_name LIKE ? OR p.description LIKE ?)"
                params.extend([f"%{normalized_name}%", f"%{normalized_name}%"])
            
            if vendor:
                # Vendor match
                query += " AND p.vendor LIKE ?"
                params.append(f"%{vendor}%")
            
            # Note: Product Type is often empty in the database, so we'll make this optional
            # if product_type:
            #     # Product type match
            #     query += " AND p.\"Product Type*\" LIKE ?"
            #     params.append(f"%{product_type}%")
            
            if strain:
                # Strain match
                query += " AND (p.product_strain LIKE ? OR p.lineage LIKE ?)"
                params.extend([f"%{strain}%", f"%{strain}%"])
            
            # Order by relevance (exact matches first, then by occurrence count)
            query += " ORDER BY CASE WHEN p.product_name LIKE ? THEN 1 ELSE 0 END DESC, p.total_occurrences DESC LIMIT 1"
            params.append(f"%{normalized_name}%")
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
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
                    'cost': result[24],  # Cost
                    'Medical Only': result[25],  # Medical Only
                    'med_price': result[26],  # Med Price
                    'expiration_date': result[27],  # Expiration Date
                    'is_archived': result[28],  # Is Archived
                    'thc_per_serving': result[29],  # THC Per Serving
                    'allergens': result[30],  # Allergens
                    'solvent': result[31],  # Solvent
                    'accepted_date': result[32],  # Accepted Date
                    'internal_product_identifier': result[33],  # Internal Product Identifier
                    'product_tags': result[34],  # Product Tags
                    'image_url': result[35],  # Image URL
                    'ingredients': result[36],  # Ingredients
                    'combined_weight': result[37],  # Combined Weight
                    'ratio_or_thc_cbd': result[38],  # Ratio or THC/CBD
                    'description_complexity': result[39],  # Description Complexity
                    'Total THC': result[40],  # Total THC
                    'THCA': result[41],  # THCA
                    'CBDA': result[42],  # CBDA
                    'CBN': result[43],  # CBN
                    'total_occurrences': result[44],
                    'first_seen_date': result[45],
                    'last_seen_date': result[46],
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
            'seattle bubble works', 'blue sky farms', 'green and gold brands', 'seatown'
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
                    cursor.execute('''
                        SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", p."Weight Unit* (grams/gm or ounces/oz)", p."Price* (Tier Name for Bulk)",
                               p."Lineage", s.strain_name, p."Description"
                        FROM products p
                        LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                        WHERE p."Product Name*" LIKE ? OR p."Product Name*" LIKE ?
                        ORDER BY p.total_occurrences DESC
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
                cursor.execute('''
                    SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", p."Weight Unit* (grams/gm or ounces/oz)", p."Price* (Tier Name for Bulk)",
                           p."Lineage", s.strain_name, p."Description"
                    FROM products p
                    LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                    WHERE p."Product Type*" = ?
                    ORDER BY p.total_occurrences DESC
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
                cursor.execute('''
                    SELECT p."Product Name*", p."Product Type*", p."Vendor/Supplier*", p."Product Brand", p."Weight*", p."Weight Unit* (grams/gm or ounces/oz)", p."Price* (Tier Name for Bulk)",
                           p."Lineage", s.strain_name, p."Description"
                    FROM products p
                    LEFT JOIN strains s ON p."Product Strain" = s.strain_name
                    WHERE s.strain_name LIKE ? OR p."Product Strain" LIKE ?
                    ORDER BY p.total_occurrences DESC
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
                SELECT p.*, s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p.product_name = ?
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
                SELECT p.*, s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p.product_strain LIKE ? OR s.strain_name LIKE ?
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
                SELECT p.*, s.canonical_lineage, s.sovereign_lineage
                FROM products p
                LEFT JOIN strains s ON p.strain_id = s.id
                WHERE p.product_type = ? AND (p.product_strain = ? OR s.strain_name = ?)
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

def get_product_database():
    # CRITICAL FIX: Use correct database path
    return ProductDatabase(get_database_path()) 

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