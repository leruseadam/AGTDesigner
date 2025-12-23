"""
Pytest configuration and fixtures for comprehensive test suite.
"""
import pytest
import os
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ['TESTING'] = '1'
os.environ['FLASK_ENV'] = 'testing'

@pytest.fixture(scope='session')
def test_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix='label_maker_tests_')
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope='function')
def temp_db(test_data_dir):
    """Create a temporary SQLite database for testing."""
    db_path = os.path.join(test_data_dir, 'test_product_database.db')
    conn = sqlite3.connect(db_path)
    
    # Create schema matching actual ProductDatabase schema with quoted column names
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Product Name*" TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            "Product Type*" TEXT NOT NULL,
            "Vendor/Supplier*" TEXT,
            "Product Brand" TEXT,
            Description TEXT,
            "Weight*" TEXT,
            Units TEXT,
            Price TEXT,
            Lineage TEXT,
            "Product Strain" TEXT,
            "Internal Product Identifier" TEXT,
            first_seen_date TEXT NOT NULL,
            last_seen_date TEXT NOT NULL,
            total_occurrences INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_product_name ON products("Product Name*")
    ''')
    
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_normalized_name ON products(normalized_name)
    ''')
    
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_vendor ON products("Vendor/Supplier*")
    ''')
    
    conn.commit()
    yield db_path
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(scope='function')
def sample_products():
    """Sample product data for testing."""
    return [
        {
            'product_name': 'Blue Dream Flower',
            'product_brand': 'Premium Cannabis Co',
            'vendor': 'Premium Cannabis Co',
            'product_type': 'Flower',
            'weight': 3.5,
            'weight_unit': 'g',
            'price': 35.00,
            'lineage': 'Sativa',
            'strain': 'Blue Dream',
            'sku': 'BD-FL-3.5',
            'description': 'Premium Blue Dream flower',
            'units': 'each'
        },
        {
            'product_name': 'OG Kush Pre-Roll',
            'product_brand': 'Kush Co',
            'vendor': 'Kush Co',
            'product_type': 'Pre-Roll',
            'weight': 1.0,
            'weight_unit': 'g',
            'price': 12.00,
            'lineage': 'Indica',
            'strain': 'OG Kush',
            'sku': 'OG-PR-1',
            'description': 'Single pre-roll',
            'units': 'each'
        },
        {
            'product_name': 'CBD Tincture 500mg',
            'product_brand': 'Wellness Labs',
            'vendor': 'Wellness Labs',
            'product_type': 'Tincture',
            'weight': 30.0,
            'weight_unit': 'ml',
            'price': 45.00,
            'lineage': 'Mixed',
            'strain': '',
            'sku': 'CBD-TIN-500',
            'description': 'High CBD tincture',
            'units': 'each'
        }
    ]

@pytest.fixture(scope='function')
def populated_db(temp_db, sample_products):
    """Create a database populated with sample products."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Create products table with proper schema matching the app
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Product Name*" TEXT NOT NULL,
            "Product Brand" TEXT,
            "Vendor/Supplier*" TEXT,
            "Product Type*" TEXT,
            "Weight*" REAL,
            "Weight Unit* (grams/gm or ounces/oz)" TEXT,
            "Price* (Tier Name for Bulk)" REAL,
            Lineage TEXT,
            "Product Strain" TEXT,
            "Internal Product Identifier" TEXT,
            Description TEXT,
            Units TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    for product in sample_products:
        cursor.execute('''
            INSERT INTO products (
                "Product Name*", "Product Brand", "Vendor/Supplier*", "Product Type*",
                "Weight*", "Weight Unit* (grams/gm or ounces/oz)", "Price* (Tier Name for Bulk)", 
                Lineage, "Product Strain", "Internal Product Identifier",
                Description, Units
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['product_name'],
            product['product_brand'],
            product['vendor'],
            product['product_type'],
            product['weight'],
            product['weight_unit'],
            product['price'],
            product['lineage'],
            product['strain'],
            product['sku'],
            product['description'],
            product['units']
        ))
    
    conn.commit()
    conn.close()
    return temp_db

@pytest.fixture(scope='function')
def sample_excel_file(test_data_dir, sample_products):
    """Create a sample Excel file for testing."""
    df = pd.DataFrame(sample_products)
    excel_path = os.path.join(test_data_dir, 'test_products.xlsx')
    df.to_excel(excel_path, index=False)
    return excel_path

@pytest.fixture(scope='function')
def sample_excel_data():
    """Sample Excel data as dictionary."""
    return {
        'Product Name*': ['Blue Dream Flower', 'OG Kush Pre-Roll', 'CBD Tincture 500mg'],
        'Product Brand': ['Premium Cannabis Co', 'Kush Co', 'Wellness Labs'],
        'Vendor/Supplier*': ['Premium Cannabis Co', 'Kush Co', 'Wellness Labs'],
        'Product Type*': ['Flower', 'Pre-Roll', 'Tincture'],
        'Weight*': [3.5, 1.0, 30.0],
        'Weight Unit* (grams/gm or ounces/oz)': ['g', 'g', 'ml'],
        'Price* (Tier Name for Bulk)': [35.00, 12.00, 45.00],
        'Lineage': ['Sativa', 'Indica', 'Mixed'],
        'Product Strain': ['Blue Dream', 'OG Kush', ''],
        'Internal Product Identifier': ['BD-FL-3.5', 'OG-PR-1', 'CBD-TIN-500'],
        'Description': ['Premium Blue Dream flower', 'Single pre-roll', 'High CBD tincture'],
        'Units': ['each', 'each', 'each']
    }

@pytest.fixture(scope='function')
def mock_flask_app():
    """Create a mock Flask app for testing."""
    app = MagicMock()
    app.config = {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    }
    return app

@pytest.fixture(scope='function')
def mock_session():
    """Create a mock Flask session."""
    return {
        'session_id': 'test-session-123',
        'file_store': 'AGT_Bothell',
        'selected_tags': [],
        'filters': {}
    }

@pytest.fixture(scope='function')
def mock_excel_processor():
    """Create a mock Excel processor."""
    processor = MagicMock()
    processor.df = pd.DataFrame({
        'Product Name*': ['Test Product'],
        'Price* (Tier Name for Bulk)': [25.00]
    })
    processor.selected_tags = []
    processor._last_loaded_file = 'test.xlsx'
    return processor

@pytest.fixture(scope='function')
def sample_json_product():
    """Sample JSON product data for matching tests."""
    return {
        'product_name': 'Blue Dream Flower',
        'brand': 'Premium Cannabis Co',
        'vendor': 'Premium Cannabis Co',
        'product_type': 'Flower',
        'weight': '3.5g',
        'price': 35.00,
        'lineage': 'Sativa',
        'strain': 'Blue Dream'
    }

@pytest.fixture(scope='function', autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    # Cleanup can be added here if needed

