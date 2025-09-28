#!/usr/bin/env python3
"""
PostgreSQL ProductDatabase for PythonAnywhere
Replaces SQLite ProductDatabase with PostgreSQL for better performance
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import random

def retry_on_connection_error(max_retries=3, base_delay=1.0):
    """Decorator to retry database operations on connection errors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logging.warning(f"Connection error on attempt {attempt + 1}, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)
                    
                    # Clear connection pool for this thread
                    if hasattr(args[0], '_connection_pool'):
                        thread_id = threading.get_ident()
                        if thread_id in args[0]._connection_pool:
                            try:
                                args[0]._connection_pool[thread_id].close()
                            except:
                                pass
                            del args[0]._connection_pool[thread_id]
            return None
        return wrapper
    return decorator

class PostgreSQLProductDatabase:
    """PostgreSQL database for storing and managing product and strain information."""
    
    def __init__(self, store_name: str = None):
        self.store_name = store_name or 'AGT_Bothell'
        self._connection_pool = {}
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._initialized = False
        self._init_lock = threading.Lock()
        self._write_lock = threading.RLock()
        
        # PostgreSQL connection config
        self.config = {
            'host': os.getenv('DB_HOST', 'adamcordova-4822.postgres.pythonanywhere-services.com'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'super'),
            'password': os.getenv('DB_PASSWORD', '193154life'),
            'port': os.getenv('DB_PORT', '14822'),
            'connect_timeout': 60,
            'application_name': 'AGTDesigner',
            'keepalives_idle': 300,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'tcp_keepalives_idle': 300,
            'tcp_keepalives_interval': 10,
            'tcp_keepalives_count': 5
        }
        
        # Performance timing
        self._timing_stats = {
            'queries': 0,
            'total_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _clear_connection_pool(self):
        """Clear all connections in the pool."""
        with self._write_lock:
            for thread_id, conn in list(self._connection_pool.items()):
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()
    
    def _get_connection(self):
        """Get a PostgreSQL connection, reusing if possible."""
        thread_id = threading.get_ident()
        
        # Check if we have a connection and if it's still alive
        if thread_id in self._connection_pool:
            conn = self._connection_pool[thread_id]
            try:
                # Test if connection is still alive
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return conn
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                # Connection is dead, remove it and create a new one
                try:
                    conn.close()
                except:
                    pass
                del self._connection_pool[thread_id]
        
        # Create new connection
        try:
            conn = psycopg2.connect(**self.config)
            conn.autocommit = False
            self._connection_pool[thread_id] = conn
            return conn
        except psycopg2.OperationalError as e:
            logging.error(f"PostgreSQL connection failed: {e}")
            return None
    
    def _normalize_product_name(self, name: str) -> str:
        """Normalize product name for consistent storage."""
        if not name:
            return ""
        return name.strip().title()
    
    def _normalize_strain_name(self, name: str) -> str:
        """Normalize strain name for consistent storage."""
        if not name:
            return ""
        return name.strip().title()
    
    def _normalize_lineage(self, lineage: str) -> str:
        """Normalize lineage for consistent storage."""
        if not lineage:
            return ""
        return lineage.strip()
    
    def _calculate_product_strain(self, product_data):
        """Calculate Product Strain from product_data dictionary."""
        try:
            # Handle both dict and individual parameter formats
            if isinstance(product_data, dict):
                product_type = product_data.get('Product Type*', '') or product_data.get('product_type', '')
                product_name = product_data.get('Product Name*', '') or product_data.get('product_name', '')
                description = product_data.get('Description', '') or product_data.get('description', '')
                ratio = product_data.get('Ratio', '') or product_data.get('ratio', '')
                
                # Call the original method with extracted parameters
                return self._calculate_product_strain_original(product_type, product_name, description, ratio)
            else:
                # If it's not a dict, assume it's the product_type parameter
                return self._calculate_product_strain_original(product_data, '', '', '')
                
        except Exception as e:
            logging.error(f"Error in overloaded _calculate_product_strain: {e}")
            return 'Mixed'
    
    def _calculate_product_strain_original(self, product_type: str, product_name: str, description: str, ratio: str) -> str:
        """Calculate Product Strain using exact Excel processor logic."""
        import re
        
        product_type = str(product_type).strip().lower()
        product_name = str(product_name).strip() if product_name else ""
        description = str(description).strip() if description else ""
        ratio = str(ratio).strip() if ratio else ""
        
        # Handle 'nan' values
        if product_name.lower() == 'nan':
            product_name = ""
        if description.lower() == 'nan':
            description = ""
        if ratio.lower() == 'nan':
            ratio = ""
        
        # Special case: paraphernalia gets Product Strain set to "Paraphernalia"
        if product_type == "paraphernalia":
            return "Paraphernalia"
        
        # Define classic types (these don't get Product Strain logic applied)
        classic_types = [
            'flower', 'pre-roll', 'infused pre-roll', 'concentrate', 'solventless concentrate', 
            'vape cartridge', 'alcohol/ethanol extract', 'co2 concentrate'
        ]
        
        # If it's a classic type, return blank (classic types don't get Product Strain logic)
        if product_type in classic_types:
            return ""
        
        # For non-classic types, determine if it's CBD or Mixed
        # Check if product name contains CBD, CBG, CBC, or CBN
        name_contains_cbd = bool(re.search(r'\b(?:CBD|CBG|CBC|CBN)\b', product_name, re.IGNORECASE))
        
        # Check if description contains CBD, CBG, CBC, or CBN, or ":"
        desc_contains_cbd = bool(re.search(r'\b(?:CBD|CBG|CBC|CBN)\b', description, re.IGNORECASE)) or ':' in description
        
        # Check if ratio contains CBD, CBG, CBC, or CBN
        ratio_contains_cbd = bool(re.search(r'\b(?:CBD|CBG|CBC|CBN)\b', ratio, re.IGNORECASE))
        
        # If any field contains CBD-related terms, return "CBD Blend"
        if name_contains_cbd or desc_contains_cbd or ratio_contains_cbd:
            return "CBD Blend"
        
        # Otherwise, return "Mixed"
        return "Mixed"
    
    def init_database(self):
        """Initialize the database and ensure all required columns exist."""
        if self._initialized:
            return True
            
        with self._init_lock:
            if self._initialized:
                return True
                
            try:
                conn = self._get_connection()
                if not conn:
                    return False
                    
                cursor = conn.cursor()
                
                # Test if tables exist
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'products'
                    )
                """)
                
                if cursor.fetchone()[0]:
                    # Tables exist, ensure all required columns exist
                    self._ensure_columns_exist(cursor)
                    conn.commit()
                    self._initialized = True
                    logging.info(f"PostgreSQL database initialized for store '{self.store_name}'")
                    return True
                else:
                    logging.error("PostgreSQL tables not found. Run migration first.")
                    return False
                    
            except Exception as e:
                logging.error(f"Error initializing PostgreSQL database: {e}")
                if 'conn' in locals():
                    conn.rollback()
                return False
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        return True
    
    def _ensure_columns_exist(self, cursor):
        """Ensure required columns exist in the database tables."""
        try:
            # Check if strain_id column exists in products table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'strain_id'
            """)
            
            if not cursor.fetchone():
                logging.info("Adding strain_id column to products table...")
                cursor.execute("""
                    ALTER TABLE products 
                    ADD COLUMN strain_id INTEGER REFERENCES strains(id)
                """)
                logging.info("✓ Added strain_id column to products table")
            
            # Check if lineage column exists in strains table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'strains' AND column_name = 'lineage'
            """)
            
            if not cursor.fetchone():
                logging.info("Adding lineage column to strains table...")
                cursor.execute("""
                    ALTER TABLE strains 
                    ADD COLUMN lineage TEXT
                """)
                logging.info("✓ Added lineage column to strains table")
            
            # Check if sovereign_lineage column exists in strains table
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'strains' AND column_name = 'sovereign_lineage'
            """)
            
            if not cursor.fetchone():
                logging.info("Adding sovereign_lineage column to strains table...")
                cursor.execute("""
                    ALTER TABLE strains 
                    ADD COLUMN sovereign_lineage TEXT
                """)
                logging.info("✓ Added sovereign_lineage column to strains table")
                
        except Exception as e:
            logging.error(f"Error ensuring columns exist: {e}")
            raise
    
    @retry_on_connection_error(max_retries=3, base_delay=0.5)
    def add_or_update_strain(self, strain_name: str, lineage: str = None, sovereign: bool = False) -> int:
        """Add a new strain or update existing strain information."""
        conn = None
        cursor = None
        try:
            self.init_database()
            normalized_name = self._normalize_strain_name(strain_name)
            current_date = datetime.now().isoformat()
            
            with self._write_lock:
                conn = self._get_connection()
                if not conn:
                    logging.error(f"No connection available for strain '{strain_name}'")
                    return None
                    
                cursor = conn.cursor()
                
                # Check if strain exists
                cursor.execute("""
                    SELECT id FROM strains 
                    WHERE strain_name = %s
                """, (normalized_name,))
                
                existing_strain = cursor.fetchone()
                
                if existing_strain:
                    strain_id = existing_strain[0]
                    # Update existing strain
                    cursor.execute("""
                        UPDATE strains 
                        SET lineage = %s, 
                            sovereign_lineage = %s,
                            updated_at = %s
                        WHERE id = %s
                    """, (lineage or '', lineage if sovereign else '', current_date, strain_id))
                else:
                    # Insert new strain
                    cursor.execute("""
                        INSERT INTO strains (strain_name, lineage, sovereign_lineage, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (normalized_name, lineage or '', lineage if sovereign else '', current_date, current_date))
                    
                    strain_id = cursor.fetchone()[0]
                
                conn.commit()
                return strain_id
                
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            logging.error(f"Connection error for strain '{strain_name}': {e}")
            # Remove the dead connection from pool
            thread_id = threading.get_ident()
            if thread_id in self._connection_pool:
                try:
                    self._connection_pool[thread_id].close()
                except:
                    pass
                del self._connection_pool[thread_id]
            return None
        except Exception as e:
            logging.error(f"Failed to add/update strain '{strain_name}': {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    @retry_on_connection_error(max_retries=3, base_delay=0.5)
    def add_or_update_product(self, product_data: Dict[str, Any]) -> int:
        """Add a new product or update existing product information."""
        conn = None
        cursor = None
        try:
            self.init_database()
            
            # Handle both 'ProductName' and 'Product Name*' column names
            product_name = product_data.get('Product Name*', product_data.get('ProductName', ''))
            normalized_name = self._normalize_product_name(product_name)
            current_date = datetime.now().isoformat()
            
            # Get or create strain
            strain_name = product_data.get('Product Strain', '')
            strain_id = None
            if strain_name:
                normalized_lineage = self._normalize_lineage(product_data.get('Lineage'))
                strain_id = self.add_or_update_strain(strain_name, normalized_lineage)
            
            with self._write_lock:
                conn = self._get_connection()
                if not conn:
                    logging.error(f"No connection available for product '{product_name}'")
                    return None
                    
                cursor = conn.cursor()
                
                # Check if product exists
                cursor.execute("""
                    SELECT id FROM products 
                    WHERE product_name = %s
                """, (normalized_name,))
                
                existing_product = cursor.fetchone()
                
                if existing_product:
                    product_id = existing_product[0]
                    # Update existing product
                    cursor.execute("""
                        UPDATE products 
                        SET product_strain = %s,
                            strain_id = %s,
                            product_type = %s,
                            vendor_supplier = %s,
                            thc_content = %s,
                            cbd_content = %s,
                            price = %s,
                            updated_at = %s
                        WHERE id = %s
                    """, (
                        strain_name or '',
                        strain_id,
                        product_data.get('Product Type', ''),
                        product_data.get('Vendor/Supplier', ''),
                        product_data.get('THC Content', ''),
                        product_data.get('CBD Content', ''),
                        product_data.get('Price', ''),
                        current_date,
                        product_id
                    ))
                else:
                    # Insert new product
                    cursor.execute("""
                        INSERT INTO products (
                            product_name, product_strain, strain_id, product_type,
                            vendor_supplier, thc_content, cbd_content, price,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        normalized_name,
                        strain_name or '',
                        strain_id,
                        product_data.get('Product Type', ''),
                        product_data.get('Vendor/Supplier', ''),
                        product_data.get('THC Content', ''),
                        product_data.get('CBD Content', ''),
                        product_data.get('Price', ''),
                        current_date,
                        current_date
                    ))
                    
                    product_id = cursor.fetchone()[0]
                
                conn.commit()
                return product_id
                
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
            logging.error(f"Connection error for product '{product_name}': {e}")
            # Remove the dead connection from pool
            thread_id = threading.get_ident()
            if thread_id in self._connection_pool:
                try:
                    self._connection_pool[thread_id].close()
                except:
                    pass
                del self._connection_pool[thread_id]
            return None
        except Exception as e:
            logging.error(f"Failed to add/update product '{product_name}': {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search products using PostgreSQL full-text search."""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"search:{query}:{limit}"
        with self._cache_lock:
            if cache_key in self._cache:
                self._timing_stats['cache_hits'] += 1
                self._timing_stats['queries'] += 1
                self._timing_stats['total_time'] += time.time() - start_time
                return self._cache[cache_key]
            self._timing_stats['cache_misses'] += 1
        
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Use PostgreSQL full-text search
            cursor.execute("""
                SELECT *, 
                       ts_rank(to_tsvector('english', COALESCE(product_name, '')), plainto_tsquery('english', %s)) as rank
                FROM products 
                WHERE to_tsvector('english', COALESCE(product_name, '')) @@ plainto_tsquery('english', %s)
                   OR to_tsvector('english', COALESCE(product_strain, '')) @@ plainto_tsquery('english', %s)
                   OR to_tsvector('english', COALESCE(vendor_supplier, '')) @@ plainto_tsquery('english', %s)
                   OR product_name ILIKE %s
                   OR product_strain ILIKE %s
                   OR vendor_supplier ILIKE %s
                ORDER BY rank DESC, product_name
                LIMIT %s
            """, (query, query, query, query, f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Cache results
            with self._cache_lock:
                self._cache[cache_key] = results
                # Limit cache size
                if len(self._cache) > 100:
                    # Remove oldest entries
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
            
            self._timing_stats['queries'] += 1
            self._timing_stats['total_time'] += time.time() - start_time
            
            return results
            
        except Exception as e:
            logging.error(f"PostgreSQL search failed: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_all_products(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all products."""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM products 
                ORDER BY product_name
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Get all products failed: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_products_by_type(self, product_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products by type."""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM products 
                WHERE product_type = %s
                ORDER BY product_name
                LIMIT %s
            """, (product_type, limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Get products by type failed: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = self._get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get product count
            cursor.execute("SELECT COUNT(*) as total_products FROM products")
            total_products = cursor.fetchone()['total_products']
            
            # Get product types
            cursor.execute("SELECT COUNT(DISTINCT product_type) as product_types FROM products")
            product_types = cursor.fetchone()['product_types']
            
            # Get strains
            cursor.execute("SELECT COUNT(DISTINCT product_strain) as strains FROM products WHERE product_strain IS NOT NULL")
            strains = cursor.fetchone()['strains']
            
            # Get vendors
            cursor.execute("SELECT COUNT(DISTINCT vendor_supplier) as vendors FROM products WHERE vendor_supplier IS NOT NULL")
            vendors = cursor.fetchone()['vendors']
            
            return {
                'total_products': total_products,
                'product_types': product_types,
                'strains': strains,
                'vendors': vendors,
                'database_type': 'PostgreSQL',
                'store_name': self.store_name,
                'performance_stats': self._timing_stats.copy()
            }
            
        except Exception as e:
            logging.error(f"Get database stats failed: {e}")
            return {}
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            logging.error(f"PostgreSQL test failed: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close_connections(self):
        """Close all connections."""
        for conn in self._connection_pool.values():
            try:
                conn.close()
            except:
                pass
        self._connection_pool.clear()

# Global PostgreSQL database instance
_postgresql_db = None

def get_postgresql_database(store_name: str = None) -> PostgreSQLProductDatabase:
    """Get PostgreSQL database instance."""
    global _postgresql_db
    if _postgresql_db is None or (store_name and _postgresql_db.store_name != store_name):
        _postgresql_db = PostgreSQLProductDatabase(store_name)
        _postgresql_db.init_database()
    return _postgresql_db

# Compatibility function for existing code
def get_product_database(store_name: str = None) -> PostgreSQLProductDatabase:
    """Compatibility function - returns PostgreSQL database instead of SQLite."""
    return get_postgresql_database(store_name)

# Create ProductDatabase alias for compatibility
ProductDatabase = PostgreSQLProductDatabase

if __name__ == "__main__":
    # Test the PostgreSQL database
    db = PostgreSQLProductDatabase('AGT_Bothell')
    
    if db.test_connection():
        print("✅ PostgreSQL connection successful")
        
        # Test search
        results = db.search_products("Blue Dream", limit=5)
        print(f"🔍 Search test: Found {len(results)} products")
        
        # Test stats
        stats = db.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
    else:
        print("❌ PostgreSQL connection failed")
