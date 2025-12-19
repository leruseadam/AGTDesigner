# Sync Production Database to Match Local (10,000+ Products)

## Quick Fix: Use Web Interface (Recommended)

1. **Upload via Web Interface**:
   - Go to `https://www.agtpricetags.com`
   - Click "Data & Analytics" button
   - Click "Upload Database" 
   - Select your Excel file with all sheets
   - Wait for upload to complete
   - The system will automatically load ALL sheets and rebuild the database

## Alternative: Command Line Sync

If you prefer command line:

```bash
# 1. Navigate to project root
cd ~/AGTDesigner

# 2. Run sync script (finds latest Excel automatically)
python scripts/database/force_database_sync.py sync

# OR specify a specific file:
python scripts/database/force_database_sync.py file uploads/your_file.xlsx
```

## Verify It Worked

After syncing, check the database stats:

1. **Via Web Interface**:
   - Go to "Data & Analytics"
   - Should show **10,000+ TOTAL PRODUCTS**

2. **Via Command Line**:
   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM products')
   count = cursor.fetchone()[0]
   print(f'Total products in database: {count}')
   conn.close()
   "
   ```

## Troubleshooting

**"No Excel files found"**:
- Make sure your Excel file is in `~/AGTDesigner/uploads/`
- The file should be named something like `A Greener Today - Bothell_inventory_*.xlsx`

**"ModuleNotFoundError: No module named 'app'"**:
- Make sure you're in the project root: `cd ~/AGTDesigner`
- Don't run from `scripts/database/` directory

**Still showing ~2,000 products**:
- Make sure you uploaded the Excel file with ALL sheets
- Check server logs for "Excel file loaded from X sheets" message
- Try clearing the database first, then re-upload
