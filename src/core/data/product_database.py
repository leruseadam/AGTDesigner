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
                # Add new product with all available columns
                cursor.execute('''
                    INSERT INTO products (
                        product_name, normalized_name, strain_id, product_type, vendor, brand,
                        description, weight, units, price, lineage, first_seen_date, last_seen_date, created_at, updated_at,
                        product_strain, quantity, doh_compliant, concentrate_type, ratio, joint_ratio,
                        thc_test_result, cbd_test_result, test_result_unit, state, is_sample, is_mj_product,
                        discountable, room, batch_number, lot_number, barcode, cost, medical_only, med_price,
                        expiration_date, is_archived, thc_per_serving, allergens, solvent, accepted_date,
                        internal_product_identifier, product_tags, image_url, ingredients
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product_name, normalized_name, strain_id, product_data.get('Product Type*'),
                    product_data.get('Vendor'), product_data.get('Product Brand'),
                    product_data.get('Description'), product_data.get('Weight*'),
                    product_data.get('Units'), product_data.get('Price'),
                    product_data.get('Lineage'), current_date, current_date, current_date, current_date,
                    product_data.get('Product Strain'), product_data.get('Quantity*'),
                    product_data.get('DOH'), product_data.get('Concentrate Type'),
                    product_data.get('Ratio'), product_data.get('Joint Ratio'),
                    product_data.get('THC test result'), product_data.get('CBD test result'),
                    product_data.get('Test result unit (% or mg)'), product_data.get('State'),
                    product_data.get('Is Sample? (yes/no)'), product_data.get('Is MJ product?(yes/no)'),
                    product_data.get('Discountable? (yes/no)'), product_data.get('Room*'),
                    product_data.get('Batch Number'), product_data.get('Lot Number'),
                    product_data.get('Barcode*'), product_data.get('Cost*'),
                    product_data.get('Medical Only (Yes/No)'), product_data.get('Med Price'),
                    product_data.get('Expiration Date(YYYY-MM-DD)'), product_data.get('Is Archived? (yes/no)'),
                    product_data.get('THC Per Serving'), product_data.get('Allergens'),
                    product_data.get('Solvent'), product_data.get('Accepted Date'),
                    product_data.get('Internal Product Identifier'), product_data.get('Product Tags (comma separated)'),
                    product_data.get('Image URL'), product_data.get('Ingredients')
                ))
                
                product_id = cursor.lastrowid
                conn.commit()
                if DEBUG_ENABLED:
                    logger.debug(f"Added new product '{product_name}'")
                return product_id
                
        except Exception as e:
            logger.error(f"Error adding/updating product '{product_data.get('ProductName', '')}': {e}")
            raise
    
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