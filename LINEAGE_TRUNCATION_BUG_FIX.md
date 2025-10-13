# LINEAGE TRUNCATION BUG FIX

## 🎯 **ROOT CAUSE IDENTIFIED**

The issue where "HYBRID/INDICA" was being converted to "HYBRID" was caused by **incorrect ordering** in lineage processing arrays throughout the codebase.

## **The Bug**

In multiple locations, the lineage arrays were ordered like this:
```python
classic_lineages = ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD", "MIXED"]
```

When the code checked `cleaned_lineage_val.upper().startswith(classic_lineage.upper())`, a value like "HYBRID/INDICA" would match "HYBRID" first (because "HYBRID/INDICA" starts with "HYBRID"), and then truncate it to just "HYBRID".

## **The Fix**

Reordered all lineage arrays to put **longer, more specific lineages first**:

```python
classic_lineages = ["HYBRID/SATIVA", "HYBRID/INDICA", "SATIVA", "INDICA", "HYBRID", "CBD", "MIXED"]
```

## **Files Fixed**

### 1. `src/core/data/excel_processor.py`
**Fixed Excel processor lineage standardization:**
```python
# Before (missing forward slash formats)
.replace({
    "indica_hybrid": "HYBRID/INDICA",
    "sativa_hybrid": "HYBRID/SATIVA",
    "sativa": "SATIVA",
    "hybrid": "HYBRID",
    "indica": "INDICA",
    "cbd": "CBD"
})

# After (includes forward slash formats)
.replace({
    "indica_hybrid": "HYBRID/INDICA",
    "indica/hybrid": "HYBRID/INDICA",  # FIX: Add forward slash format
    "hybrid/indica": "HYBRID/INDICA",  # FIX: Add reverse format
    "sativa_hybrid": "HYBRID/SATIVA",
    "sativa/hybrid": "HYBRID/SATIVA",  # FIX: Add forward slash format
    "hybrid/sativa": "HYBRID/SATIVA",  # FIX: Add reverse format
    "sativa": "SATIVA",
    "hybrid": "HYBRID",
    "indica": "INDICA",
    "cbd": "CBD"
})
```

### 2. `src/core/generation/template_processor.py`
**Fixed lineage processing order (3 locations):**
```python
# Before (incorrect order)
classic_lineages = ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD", "MIXED"]

# After (correct order - specific lineages first)
classic_lineages = ["HYBRID/SATIVA", "HYBRID/INDICA", "SATIVA", "INDICA", "HYBRID", "CBD", "MIXED"]
```

### 3. `static/js/main.js`
**Fixed JavaScript lineage arrays (2 locations):**
```javascript
// Before (incorrect order)
const lineageOrder = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA'];

// After (correct order)
const lineageOrder = ['HYBRID/SATIVA', 'HYBRID/INDICA', 'SATIVA', 'INDICA', 'HYBRID', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA'];
```

### 4. `static/js/tags_table.js`
**Fixed JavaScript lineage arrays (2 locations):**
```javascript
// Before (incorrect order)
return ['SATIVA','INDICA','HYBRID','HYBRID/SATIVA','HYBRID/INDICA','CBD','MIXED','PARA'];

// After (correct order)
return ['HYBRID/SATIVA','HYBRID/INDICA','SATIVA','INDICA','HYBRID','CBD','MIXED','PARA'];
```

## **Expected Results**

After this fix:
- ✅ **"HYBRID/INDICA" will stay "HYBRID/INDICA"** (not truncated to "HYBRID")
- ✅ **"HYBRID/SATIVA" will stay "HYBRID/SATIVA"** (not truncated to "HYBRID")
- ✅ **All combination lineage types will display correctly** in generated tags
- ✅ **Manual lineage dropdown changes will persist** through generation

## **Testing**

1. **Upload Excel file** with products that have "indica/hybrid" or "hybrid/indica" lineage
2. **Change lineage dropdown** from "HYBRID" to "HYBRID/INDICA" for products
3. **Generate tags** and download Word document
4. **Verify** tags show "HYBRID/INDICA" instead of "HYBRID"

## **Technical Details**

The fix ensures that when the template processor checks lineage values:
1. **"HYBRID/INDICA"** matches "HYBRID/INDICA" first (not "HYBRID")
2. **"HYBRID/SATIVA"** matches "HYBRID/SATIVA" first (not "HYBRID")
3. **Longer, more specific lineages are processed before shorter, generic ones**

This prevents the truncation bug that was converting combination lineages to simple lineages.
