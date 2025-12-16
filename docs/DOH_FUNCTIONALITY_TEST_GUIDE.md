# DOH Dropdown Functionality Test Guide

## Overview
The DOH dropdown in your UI controls whether the `{Label1.DOH}` placeholder in DOCX output includes a `.png` image or remains blank.

## How It Works

### 1. Frontend (UI) - DOH Dropdown
Located in: `static/js/tags_table.js:60-66`

The dropdown has 4 options:
- **None** - No DOH image
- **DOH** - Standard DOH compliance image
- **THC** - High THC warning image
- **CBD** - High CBD warning image

### 2. Backend Storage
Located in: `app.py:7305-7306`

Value mapping:
- `NONE` (from frontend) → stored as `No` in database
- `DOH` → stored as `DOH` in database
- `THC` → stored as `THC` in database
- `CBD` → stored as `CBD` in database
- `Yes` (legacy) → remains as `Yes` in database

### 3. DOCX Generation
Located in: `src/core/generation/template_processor.py:1364-1395`

Decision logic:
```python
if doh_upper in ['NO', 'NONE', 'FALSE', ''] or doh_value in ['No', 'no']:
    # NO IMAGE - placeholder stays empty
    label_context['DOH'] = ''

elif doh_upper in ['YES', 'DOH', 'THC', 'CBD']:
    # INCLUDE IMAGE - appropriate type
    if doh_upper == 'CBD':
        image = 'HighCBD.png'
    elif doh_upper == 'THC':
        image = 'HighTHC.png'
    else:
        image = 'DOH.png'
```

## Current Database Status

Run: `python3 test_doh_functionality.py`

Your Bothell database has:
- **5,412 products** with DOH='No' (no image)
- **3,412 products** with DOH='Yes' (legacy, includes DOH.png)
- **1 product** with DOH='CBD' (includes HighCBD.png)

Example product with new DOH value:
- "Baker's Blend Kief by Mt Baker Homegrown - 1g" has DOH='CBD'

## Testing Instructions

### Step 1: Select a Product and Change DOH
1. Open your app in browser (http://localhost:5000 or your URL)
2. Load your product list
3. Find a product (e.g., "Core Reactor Quartz Banger" which has DOH='No')
4. Change the DOH dropdown from "None" to "DOH"
5. Watch the browser console for confirmation

### Step 2: Check API Update Logs
After changing the dropdown, check your logs:
```bash
tail -f app.log | grep "DOH API UPDATE"
```

You should see:
```
✅ DOH API UPDATE: Updated product DOH in database: 'Core Reactor Quartz Banger' → 'DOH' (frontend sent: 'DOH')
🔍 DOH API UPDATE: For DOCX generation, this product should INCLUDE DOH image
```

### Step 3: Generate DOCX
1. Select the product you just updated
2. Click "Generate Tags" or your DOCX generation button
3. Monitor the logs for DOCX generation messages:

```bash
tail -f app.log | grep "DOH DOCX GENERATION"
```

You should see:
```
🔍 DOH DOCX GENERATION: Product 'Core Reactor Quartz Banger' - DOH field: 'DOH' from record
✅ DOH DOCX GENERATION: Created DOH image for 'Core Reactor Quartz Banger' with value 'DOH' - IMAGE WILL BE ADDED: /path/to/DOH.png
```

### Step 4: Verify DOCX Output
1. Open the generated DOCX file
2. Find the label for your test product
3. Check the `{Label1.DOH}` placeholder location
4. **Expected result**: You should see the DOH.png image

### Step 5: Test "None" Value
1. Change the same product's DOH dropdown to "None"
2. Generate DOCX again
3. Check logs - should see:
```
✅ DOH DOCX GENERATION: Explicitly clearing DOH for 'Core Reactor Quartz Banger' - value: 'No' (NO/NONE/FALSE) - NO IMAGE WILL BE ADDED
```
4. **Expected result**: `{Label1.DOH}` placeholder should be blank (no image)

## Expected Behavior Matrix

| Dropdown Selection | Stored Value | DOCX Output |
|-------------------|--------------|-------------|
| None | `No` | No image (blank) |
| DOH | `DOH` | DOH.png image |
| THC | `THC` | HighTHC.png image |
| CBD | `CBD` | HighCBD.png image |
| (legacy Yes) | `Yes` | DOH.png image |

## Troubleshooting

### Issue: DOH image appears when dropdown is "None"
**Check:**
1. Look at the logs for "DOH DOCX GENERATION" messages
2. Verify the DOH value in database:
   ```bash
   python3 -c "import sqlite3; conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db'); cursor = conn.cursor(); cursor.execute('SELECT DOH FROM products WHERE \"Product Name*\" = \"YOUR_PRODUCT_NAME\"'); print(cursor.fetchone())"
   ```
3. If database shows 'No' but image still appears, check template_processor.py logs

### Issue: DOH image doesn't appear when dropdown is "DOH"
**Check:**
1. Verify the DOH value was saved in database (should be 'DOH', not 'No')
2. Check if the image file exists: `ls templates/DOH.png`
3. Look for errors in "DOH DOCX GENERATION" logs

### Issue: Changes don't persist
**Check:**
1. Verify database file permissions
2. Check if Excel data is overriding database values
3. Clear browser cache and reload

## Log Monitoring Commands

Monitor all DOH-related activity:
```bash
# Real-time monitoring
tail -f app.log | grep -i doh

# Check recent DOH updates
tail -100 app.log | grep "DOH API UPDATE"

# Check DOCX generation DOH processing
tail -100 app.log | grep "DOH DOCX GENERATION"
```

## Success Criteria

✅ The functionality is working correctly if:
1. Changing dropdown to "None" → DOCX has no image
2. Changing dropdown to "DOH" → DOCX has DOH.png
3. Changing dropdown to "THC" → DOCX has HighTHC.png
4. Changing dropdown to "CBD" → DOCX has HighCBD.png
5. Logs show appropriate "INCLUDE" or "EXCLUDE" messages
6. Database values persist correctly

## Additional Notes

- The logging I added will help you debug any issues
- All logs use emoji prefixes (🔍 for info, ✅ for success, ⚠️ for warnings)
- The DOH logic is case-insensitive (handles 'No', 'NO', 'no', etc.)
- Legacy 'Yes' values are automatically converted to DOH.png for backward compatibility
