# Upload Excel File to Fix Dashboard

## Problem
The database is working (10,543 products) but the dashboard shows 0 products because **no Excel file is loaded**.

## Solution: Upload an Excel File

### Option 1: Upload via Web Interface (Recommended)

1. **Go to:** https://www.agtpricetags.com
2. **Click "Upload" button** or drag-and-drop area
3. **Select an Excel file** (like "A Greener Today - Bothell_inventory_10-12-2025 6_37 AM.xlsx")
4. **Wait for upload to complete**
5. **Dashboard should populate with data**

### Option 2: Upload to PythonAnywhere Files

1. **Go to:** https://www.pythonanywhere.com
2. **Files tab** → Navigate to `/home/adamcordova/AGTDesigner/uploads/`
3. **Upload Excel file** (drag-and-drop or click "Upload a file")
4. **Restart web app** (Web tab → Reload)
5. **Visit** https://www.agtpricetags.com

### Option 3: Copy Excel File to Downloads

The app also looks in `~/Downloads/` for Excel files:

1. **Copy Excel file** to your Downloads folder
2. **Restart web app** (Web tab → Reload)
3. **Visit** https://www.agtpricetags.com

## Expected Results

After uploading an Excel file:
- ✅ **TOTAL PRODUCTS: 2,000+** (from Excel file)
- ✅ **UNIQUE VENDORS: 50+** 
- ✅ **UNIQUE BRANDS: 100+**
- ✅ **Product Type Distribution** shows data
- ✅ **Top Vendors/Brands** tables populate

## File Requirements

- **Format:** .xlsx or .xls
- **Size:** Any size (tested up to 50MB)
- **Name:** Any name (app prefers "A Greener Today" files)

## Troubleshooting

If upload doesn't work:
1. **Check browser console** for errors
2. **Try different Excel file**
3. **Restart web app** after upload
4. **Clear browser cache** and refresh

The database is ready - just need to upload an Excel file! 🎉
