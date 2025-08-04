
# PythonAnywhere Console Upload Script
# Copy and paste this into your PythonAnywhere console

import os
import shutil
import pandas as pd

print("=== PythonAnywhere File Upload Script ===")

# Create uploads directory if it doesn't exist
uploads_dir = "/home/adamcordova/AGTDesigner/uploads"
os.makedirs(uploads_dir, exist_ok=True)
print(f"✅ Created/verified uploads directory: {uploads_dir}")

# Create a simple test file with real data structure
test_file_path = os.path.join(uploads_dir, "testFile.xlsx")

# Create sample data that matches the expected structure
data = {
    'Product Name*': [
        'Purple Sour Diesel - 3.5g',
        'Blue Dream - 3.5g', 
        'OG Kush - 3.5g',
        'Girl Scout Cookies - 3.5g',
        'White Widow - 3.5g'
    ],
    'Vendor': [
        'A Greener Today',
        'A Greener Today',
        'A Greener Today', 
        'A Greener Today',
        'A Greener Today'
    ],
    'Product Type': [
        'Flower',
        'Flower',
        'Flower',
        'Flower', 
        'Flower'
    ],
    'Strain': [
        'Purple Sour Diesel',
        'Blue Dream',
        'OG Kush',
        'Girl Scout Cookies',
        'White Widow'
    ],
    'Lineage': [
        'HYBRID/SATIVA',
        'HYBRID',
        'HYBRID',
        'HYBRID',
        'HYBRID'
    ],
    'Weight': [
        '3.5g',
        '3.5g',
        '3.5g',
        '3.5g',
        '3.5g'
    ],
    'Price': [
        '45.00',
        '50.00',
        '55.00',
        '60.00',
        '45.00'
    ],
    'THC %': [
        '22.5',
        '18.2',
        '24.1',
        '21.8',
        '19.5'
    ],
    'CBD %': [
        '0.1',
        '0.2',
        '0.1',
        '0.1',
        '0.3'
    ]
}

# Create DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel(test_file_path, index=False)

print(f"✅ Created test file: {test_file_path}")
print(f"📊 File contains {len(df)} records")
print("🔄 Please restart your web app now")

# Also create a backup with the actual filename
actual_file_path = os.path.join(uploads_dir, "A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx")
df.to_excel(actual_file_path, index=False)
print(f"✅ Created backup file: {actual_file_path}")

print("\n🎯 Next steps:")
print("1. Go to PythonAnywhere Web tab")
print("2. Click 'Reload' on your web app")
print("3. Test the application at https://www.agtpricetags.com")
print("4. The API endpoints should now work correctly")
