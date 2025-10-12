# Weight Normalization System for Excel Uploads

## Overview
Automatically normalizes product weights during Excel upload processing, preventing incorrect weights from entering the database.

---

## 🎯 **Problem Solved**

**Before:** Excel uploads could introduce wrong weights (e.g., Moonshots at 2.5oz instead of 1.7oz), requiring manual post-upload fixes.

**After:** All weights are automatically normalized during upload, ensuring consistency without manual intervention.

---

## 🔧 **How It Works**

### **Integration Point**
The weight normalizer is integrated into `src/core/data/product_database.py` in the `store_excel_data()` method:

```python
# Normalize weights before storing in database
try:
    from src.core.data.weight_normalizer import weight_normalizer
    product_data = weight_normalizer.normalize_product_data(product_data)
    logger.info(f"Normalized weights for product: {product_name}")
except Exception as e:
    logger.warning(f"Failed to normalize weights for {product_name}: {e}")
```

### **Processing Flow**
1. **Excel Upload** → Raw product data
2. **Weight Normalization** → Apply rules and convert units
3. **Database Storage** → Store normalized data
4. **Label Generation** → Use correct weights

---

## 📋 **Normalization Rules**

### **1. Constellation Moonshots**
- **Rule:** Always 1.7oz
- **Pattern:** Product name contains "moonshot" AND brand contains "constellation"
- **Example:** `2.5oz` → `1.7oz`

### **2. Major Beverages**
- **Rule:** 190g → 6.7oz
- **Pattern:** Brand = "Major" AND weight = 190g AND type = "Edible (Liquid)"
- **Example:** `190g` → `6.7oz`

### **3. Generic 190g Products**
- **Rule:** 190g → 6.7oz (non-concentrates only)
- **Pattern:** Weight = 190g AND NOT concentrate type
- **Example:** `190g` → `6.7oz`

### **4. Topicals**
- **Rule:** Convert large grams to oz
- **Pattern:** Type contains "Topical" AND weight > 10g AND unit = g
- **Example:** `50g` → `1.76oz`

### **5. Flower Products**
- **Rule:** Convert oz to grams
- **Pattern:** Type contains "Flower" OR "Pre-Roll" AND unit = oz
- **Example:** `3.5oz` → `99.22g`

### **6. Concentrates**
- **Rule:** Convert oz to grams (concentrates stay in g)
- **Pattern:** Type contains "Concentrate", "Wax", "Shatter", etc. AND unit = oz
- **Example:** `1oz` → `28.35g`

### **7. Other Products**
- **Rule:** No change if already correct
- **Example:** `2.0oz` → `2.0oz` (unchanged)

---

## 🧪 **Testing**

### **Test Suite**
Run the test suite to verify all rules work correctly:

```bash
python3 test_weight_normalization.py
```

### **Test Results**
```
================================================================================
TESTING WEIGHT NORMALIZATION
================================================================================

Test 1: Green Apple Moonshot → 2.5oz → 1.7oz ✅
Test 2: Orange Moonshot → 2.5oz → 1.7oz ✅
Test 3: Major Beverage → 190g → 6.7oz ✅
Test 4: Generic 190g → 190g → 6.7oz ✅
Test 5: Bath Salts → 50g → 1.76oz ✅
Test 6: Blue Dream → 3.5oz → 99.22g ✅
Test 7: Wax Product → 1oz → 28.35g ✅
Test 8: Regular Product → 2.0oz → 2.0oz ✅

RESULTS: 8 passed, 0 failed
🎉 All tests passed!
```

---

## 📁 **Files Added/Modified**

### **New Files**
- `src/core/data/weight_normalizer.py` - Main normalization logic
- `test_weight_normalization.py` - Test suite
- `WEIGHT_NORMALIZATION_SYSTEM.md` - This documentation

### **Modified Files**
- `src/core/data/product_database.py` - Added weight normalization integration

---

## 🚀 **Deployment**

### **Local Development**
The system is already integrated and will work automatically on Excel uploads.

### **PythonAnywhere Deployment**
1. **Pull latest changes:**
   ```bash
   cd ~/AGTDesigner
   git pull origin main
   ```

2. **Reload web app:**
   - Go to: https://www.pythonanywhere.com/user/adamcordova/webapps/
   - Click "Reload"

3. **Test with Excel upload:**
   - Upload an Excel file with Moonshots at 2.5oz
   - Verify they become 1.7oz in the database

---

## 🔍 **Monitoring**

### **Logging**
The system logs all normalization actions:

```
INFO - Normalized weights for product: Green Apple Moonshot by Constellation Cannabis - 100mg THC
INFO - Normalized weights for product: Major Beverage
INFO - Converting to oz: Bath Salts 50g -> 1.76oz
INFO - Converting to grams: Blue Dream 3.5oz -> 99.22g
```

### **Verification**
Check normalized weights in the database:

```python
import sqlite3
conn = sqlite3.connect('uploads/product_database_AGT_Bothell.db')
cursor = conn.cursor()
cursor.execute('SELECT "Product Name*", "Weight*", "Units" FROM products WHERE "Product Name*" LIKE "%Moonshot%" ORDER BY "Product Name*"')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}{row[2]}')
```

---

## 🎉 **Benefits**

### **Automatic Prevention**
- ✅ No more wrong Moonshot weights (2.5oz → 1.7oz)
- ✅ No more Major beverage issues (190g → 6.7oz)
- ✅ Consistent units across product types
- ✅ No manual post-upload fixes needed

### **Consistency**
- ✅ All Moonshots always 1.7oz
- ✅ All concentrates in grams
- ✅ All topicals in oz
- ✅ All flower in grams

### **Maintenance**
- ✅ Self-healing system
- ✅ Works on every upload
- ✅ Comprehensive logging
- ✅ Easy to extend with new rules

---

## 🔧 **Extending the System**

### **Adding New Rules**
Edit `src/core/data/weight_normalizer.py`:

```python
def _custom_rule(self, product_data: Dict[str, Any]) -> Tuple[str, str]:
    """Custom normalization rule."""
    product_name = str(product_data.get('Product Name*', '')).strip()
    # Add your logic here
    return normalized_weight, normalized_unit
```

### **Testing New Rules**
Add test cases to `test_weight_normalization.py`:

```python
{
    'name': 'Test Product',
    'brand': 'Test Brand',
    'type': 'Test Type',
    'weight': 'input_weight',
    'unit': 'input_unit',
    'expected': ('expected_weight', 'expected_unit')
}
```

---

## 📊 **Impact**

### **Before Normalization System:**
- ❌ Manual weight fixes required after every Excel upload
- ❌ Inconsistent weights across products
- ❌ Wrong Moonshot weights (2.5oz instead of 1.7oz)
- ❌ Major beverages showing 190g instead of 6.7oz

### **After Normalization System:**
- ✅ Automatic weight correction during upload
- ✅ Consistent weights across all products
- ✅ All Moonshots correctly 1.7oz
- ✅ All Major beverages correctly 6.7oz
- ✅ Proper units for each product type
- ✅ Zero manual intervention needed

---

**Status: 🎉 WEIGHT NORMALIZATION SYSTEM ACTIVE!**

*Last Updated: October 11, 2025*
