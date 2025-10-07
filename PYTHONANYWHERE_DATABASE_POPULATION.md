# PythonAnywhere Database Population Guide
# ========================================

## 🎯 Quick Solution for Your Database Issue

Your PythonAnywhere database is working but empty. Here's how to populate it with your full product data:

### 📊 **Current Status:**
- ✅ Database exists and is working
- ✅ All tables created properly
- ✅ Application connects successfully
- ⚠️ **Database is empty** (0 products, 0 strains)

### 🚀 **Solution: Upload Compressed Database**

#### **Step 1: Download Compressed Database**
From your local repository, download:
- `uploads/product_database_compressed.sql.gz` (0.3MB)

#### **Step 2: Upload to PythonAnywhere**
1. Go to PythonAnywhere **Files** tab
2. Navigate to `/home/adamcordova/AGTDesigner/uploads/`
3. Upload `product_database_compressed.sql.gz`

#### **Step 3: Restore Database**
Run this in PythonAnywhere Bash console:

```bash
cd ~/AGTDesigner
python3 populate_pythonanywhere_database.py
```

### 🔧 **Alternative: Create Sample Data**

If you can't upload the compressed file, run this to create sample data:

```bash
cd ~/AGTDesigner
python3 -c "
import sqlite3
from datetime import datetime

# Create sample data
conn = sqlite3.connect('uploads/product_database.db')
cursor = conn.cursor()
now = datetime.now().isoformat()

# Add sample products
sample_products = [
    ('Blue Dream Flower', 'Flower', 'Sample Vendor', 'Premium Blue Dream strain', '3.5g', '$45.00', 'HYBRID', 'Blue Dream'),
    ('Wedding Cake Pre-Roll', 'Pre-Roll', 'Sample Vendor', 'Smooth wedding cake pre-roll', '1g', '$15.00', 'HYBRID', 'Wedding Cake'),
    ('Sour Diesel Cartridge', 'Vape Cartridge', 'Sample Vendor', 'Classic sativa cartridge', '1g', '$35.00', 'SATIVA', 'Sour Diesel')
]

for name, ptype, vendor, desc, weight, price, lineage, strain in sample_products:
    cursor.execute('''
        INSERT INTO products 
        (\"Product Name*\", \"Product Type*\", \"Vendor/Supplier*\", \"Description\", 
         \"Weight*\", \"Price\", \"Lineage\", \"Product Strain\", 
         first_seen_date, last_seen_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, ptype, vendor, desc, weight, price, lineage, strain, now, now, now, now))

# Add sample strains
sample_strains = [
    ('Blue Dream', 'HYBRID'),
    ('Wedding Cake', 'HYBRID'),
    ('Sour Diesel', 'SATIVA')
]

for strain_name, lineage in sample_strains:
    cursor.execute('''
        INSERT INTO strains 
        (strain_name, canonical_lineage, first_seen_date, last_seen_date, 
         total_occurrences, lineage_confidence, sovereign_lineage, 
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (strain_name, lineage, now, now, 1, 0.9, lineage, now, now))

conn.commit()
conn.close()
print('✅ Sample data created!')
"
```

### 📋 **What You'll Get:**

#### **With Full Database (5,201 products):**
- ✅ 5,201 products
- ✅ 1,530 strains
- ✅ 1,358 products with JointRatio
- ✅ Complete product database

#### **With Sample Data (3 products):**
- ✅ 3 sample products
- ✅ 3 sample strains
- ✅ All functionality working
- ✅ Ready for testing

### 🧪 **Test Your Database:**

```bash
# Test database
python3 -c "
import sqlite3
conn = sqlite3.connect('uploads/product_database.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM products')
products = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM strains')
strains = cursor.fetchone()[0]

print(f'Products: {products}')
print(f'Strains: {strains}')

if products > 0:
    cursor.execute('SELECT \"Product Name*\", \"Product Type*\" FROM products LIMIT 3')
    samples = cursor.fetchall()
    print('Sample products:')
    for name, ptype in samples:
        print(f'  - {name} ({ptype})')

conn.close()
"
```

### 🎉 **After Population:**

1. **Reload your web app** in PythonAnywhere Web tab
2. **Test the application** by visiting your site
3. **Upload a small Excel file** to verify functionality
4. **Check JointRatio processing** works correctly

### 📊 **Expected Results:**

- ✅ Database populated with products
- ✅ Application loads without errors
- ✅ File upload functionality works
- ✅ JointRatio processing functional
- ✅ All features working properly

Your PythonAnywhere database is ready - just needs to be populated with data!
