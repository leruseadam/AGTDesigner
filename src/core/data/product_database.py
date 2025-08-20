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

class ProductDatabase:
    """Database for storing and managing product and strain information."""
    
    def __init__(self, db_path: str = "product_database.db"):
        self.db_path = db_path
        self._connection_pool = {}
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._initialized = False
        self._init_lock = threading.Lock()
        
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
            self._connection_pool[thread_id] = sqlite3.connect(self.db_path)
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
                self._migrate_database_schema(cursor, conn)
                
                self._initialized = True
                
                elapsed = time.time() - start_time
                logger.info(f"Product database initialized successfully in {elapsed:.3f}s")
                
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                raise
    
    def _migrate_database_schema(self, cursor, conn):
        """Force recreate database with correct schema."""
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
    def add_or_update_strain(self, strain_name: str, lineage: str = None, sovereign: bool = False) -> int:
        """Add a new strain or update existing strain information. If sovereign is True, set sovereign_lineage."""
        try:
            self.init_database()  # Ensure DB is initialized
            normalized_name = self._normalize_strain_name(strain_name)
            current_date = datetime.now().isoformat()
            conn = self._get_connection()
            cursor = conn.cursor()
            
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
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if product exists (based on name, vendor, brand combination)
            cursor.execute('''
                SELECT id, total_occurrences
                FROM products 
                WHERE normalized_name = ? AND vendor = ? AND brand = ?
            ''', (normalized_name, product_data.get('Vendor'), product_data.get('Product Brand')))
            
            existing = cursor.fetchone()
            
            if existing:
                product_id, occurrences = existing
                
                # Update existing product
                new_occurrences = occurrences + 1
                cursor.execute('''
                    UPDATE products 
                    SET total_occurrences = ?, last_seen_date = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_occurrences, current_date, current_date, product_id))
                
                conn.commit()
                return product_id
            else:
                # Add new product with essential columns only
                cursor.execute('''
                    INSERT INTO products (
                        product_name, normalized_name, strain_id, product_type, vendor, brand,
                        description, weight, units, price, lineage, first_seen_date, last_seen_date, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_name, normalized_name, strain_id, product_data.get('Product Type*'),
                    product_data.get('Vendor'), product_data.get('Product Brand'),
                    product_data.get('Description'), product_data.get('Weight*'),
                    product_data.get('Units'), product_data.get('Price'),
                    product_data.get('Lineage'), current_date, current_date, current_date, current_date
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
            logger.info(f"Starting to store Excel data with {len(df)} rows")
            
            if df is None or df.empty:
                logger.warning("No data to store - DataFrame is empty")
                return {'stored': 0, 'updated': 0, 'errors': 0, 'message': 'No data to store'}
            
            stored_count = 0
            updated_count = 0
            error_count = 0
            errors = []
            
            # Process each row in the DataFrame
            for index, row in df.iterrows():
                try:
                    # Convert row to dictionary and handle NaN values
                    row_dict = {}
                    for col in df.columns:
                        value = row[col]
                        if pd.isna(value):
                            row_dict[col] = None
                        else:
                            row_dict[col] = str(value).strip() if isinstance(value, str) else value
                    
                    # Simplified product data with only essential columns
                    product_data = {
                        'ProductName': row_dict.get('ProductName', ''),
                        'Product Type*': row_dict.get('Product Type*', ''),
                        'Lineage': row_dict.get('Lineage', ''),
                        'Vendor': row_dict.get('Vendor', ''),
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
                    
                    # Skip rows without product name
                    if not product_data['ProductName']:
                        continue
                    
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
            
            result = {
                'stored': stored_count,
                'updated': updated_count,
                'errors': error_count,
                'total_rows': len(df),
                'source_file': source_file,
                'message': f'Successfully stored {stored_count} products with {error_count} errors'
            }
            
            if errors:
                result['error_details'] = errors[:10]  # Limit error details to first 10
            
            logger.info(f"Excel data storage completed: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing Excel data: {e}")
            return {'stored': 0, 'updated': 0, 'errors': 1, 'message': f'Storage failed: {str(e)}'}
    
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
                           s.strain_name, s.canonical_lineage, p.total_occurrences, p.first_seen_date, p.last_seen_date
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE p.normalized_name = ? AND p.vendor = ? AND p.brand = ?
                ''', (normalized_name, vendor, brand))
            else:
                cursor.execute('''
                    SELECT p.id, p.product_name, p.product_type, p.vendor, p.brand, p.lineage,
                           s.strain_name, s.canonical_lineage, p.total_occurrences, p.first_seen_date, p.last_seen_date
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
                    'last_seen_date': result[10]
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
            
            # Vendor statistics
            cursor.execute('''
                SELECT vendor, COUNT(*) as count
                FROM products 
                WHERE vendor IS NOT NULL AND vendor != ''
                GROUP BY vendor
                ORDER BY count DESC
                LIMIT 20
            ''')
            vendor_stats = [{'vendor': vendor, 'count': count} for vendor, count in cursor.fetchall()]
            
            # Brand statistics
            cursor.execute('''
                SELECT brand, COUNT(*) as count
                FROM products 
                WHERE brand IS NOT NULL AND brand != ''
                GROUP BY brand
                ORDER BY count DESC
                LIMIT 20
            ''')
            brand_stats = [{'brand': brand, 'count': count} for brand, count in cursor.fetchall()]
            
            # Product type statistics
            cursor.execute('''
                SELECT product_type, COUNT(*) as count
                FROM products 
                WHERE product_type IS NOT NULL AND product_type != ''
                GROUP BY product_type
                ORDER BY count DESC
                LIMIT 20
            ''')
            product_type_stats = [{'product_type': product_type, 'count': count} for product_type, count in cursor.fetchall()]
            
            # Vendor-Brand combinations
            cursor.execute('''
                SELECT vendor, brand, COUNT(*) as count
                FROM products 
                WHERE vendor IS NOT NULL AND vendor != '' AND brand IS NOT NULL AND brand != ''
                GROUP BY vendor, brand
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
            
            # Export strains
            strains_df = pd.read_sql_query('''
                SELECT strain_name, canonical_lineage, total_occurrences, first_seen_date, last_seen_date
                FROM strains
                ORDER BY total_occurrences DESC
            ''', conn)
            
            # Export products with all columns
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
            
            # Export to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                strains_df.to_excel(writer, sheet_name='Strains', index=False)
                products_df.to_excel(writer, sheet_name='Products', index=False)
            
            logger.info(f"Database exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            raise
    
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

def get_product_database():
    return ProductDatabase() 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ProductDatabase admin tools")
    parser.add_argument('--update-canonical-to-mode', action='store_true', help='Update all canonical lineages to mode lineage')
    args = parser.parse_args()
    if args.update_canonical_to_mode:
        db = ProductDatabase()
        db.update_all_canonical_lineages_to_mode()
        # Canonical lineages updated to mode for all strains. 