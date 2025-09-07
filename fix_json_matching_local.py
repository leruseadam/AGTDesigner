import sqlite3
import os

# Path to the database
db_path = 'uploads/product_database.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Fixing database schema for JSON matching at {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current schema
    cursor.execute("PRAGMA table_info(products);")
    columns = cursor.fetchall()
    print("Current columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Add missing columns if they don't exist
    columns_to_add = [
        ('product_name', 'TEXT'),
        ('vendor', 'TEXT'),
        ('product_type', 'TEXT'),
        ('brand', 'TEXT'),
        ('weight', 'TEXT'),
        ('product_strain', 'TEXT')
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type};")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists")
            else:
                print(f"Error adding {col_name}: {e}")
    
    # Update the new columns with data from existing columns
    print("Updating column data...")
    
    # Map old column names to new ones
    column_mapping = {
        'product_name': 'Product Name*',
        'vendor': 'Vendor/Supplier*',
        'product_type': 'Product Type*',
        'brand': 'Product Brand',
        'weight': 'Weight*',
        'product_strain': 'Product Strain'
    }
    
    for new_col, old_col in column_mapping.items():
        try:
            # Check if old column exists
            cursor.execute(f"SELECT COUNT(*) FROM pragma_table_info('products') WHERE name = '{old_col}';")
            if cursor.fetchone()[0] > 0:
                cursor.execute(f"UPDATE products SET {new_col} = \"{old_col}\" WHERE {new_col} IS NULL;")
                print(f"Updated {new_col} from {old_col}")
            else:
                print(f"Old column {old_col} not found, skipping")
        except Exception as e:
            print(f"Error updating {new_col}: {e}")
    
    # Fix NOT NULL constraint issues by setting default values
    print("Fixing NOT NULL constraints...")
    
    # Set default values for required columns
    default_values = {
        'product_name': 'Unknown Product',
        'vendor': 'Unknown Vendor',
        'product_type': 'Unknown Type',
        'brand': 'Unknown Brand',
        'weight': 'Unknown Weight',
        'product_strain': 'Unknown Strain'
    }
    
    for col, default_val in default_values.items():
        try:
            cursor.execute(f"UPDATE products SET {col} = ? WHERE {col} IS NULL OR {col} = '';", (default_val,))
            print(f"Set default value for {col}")
        except Exception as e:
            print(f"Error setting default for {col}: {e}")
    
    # Commit changes
    conn.commit()
    print("Database schema fixed successfully!")
    
    # Verify the fix
    cursor.execute("SELECT COUNT(*) FROM products;")
    count = cursor.fetchone()[0]
    print(f"Total products: {count}")
    
    # Check if new columns exist and have data
    cursor.execute("PRAGMA table_info(products);")
    columns = cursor.fetchall()
    new_columns = [col[1] for col in columns if col[1] in ['product_name', 'vendor', 'product_type', 'brand', 'weight', 'product_strain']]
    print(f"New columns found: {new_columns}")
    
    # Test a sample query
    try:
        cursor.execute("SELECT product_name, vendor, product_type FROM products LIMIT 5;")
        sample = cursor.fetchall()
        print("Sample data:")
        for row in sample:
            print(f"  {row}")
    except Exception as e:
        print(f"Error testing sample query: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("Database fix complete!")
