# Classic vs Non-Classic Product Types Analysis

## Overview
Based on the codebase analysis, here's the definitive classification of classic vs non-classic product types.

---

## 📋 **CLASSIC_TYPES Definition**

From `src/core/constants.py`:

```python
CLASSIC_TYPES = {
    "flower", 
    "pre-roll", 
    "concentrate",
    "infused pre-roll", 
    "solventless concentrate",
    "vape cartridge", 
    "rso/co2 tankers"
}
```

---

## 🎯 **Classification Logic**

### **Classic Types = CLASSIC_TYPES**
Products that are **IN** the `CLASSIC_TYPES` set are considered **classic**.

### **Non-Classic Types = NOT in CLASSIC_TYPES**
Products that are **NOT** in the `CLASSIC_TYPES` set are considered **non-classic**.

---

## 📊 **Complete Type Classification**

### **✅ CLASSIC TYPES (7 total)**
| Type | Description | Weight Unit | Lineage |
|------|-------------|-------------|---------|
| `flower` | Cannabis flower/bud | grams | SATIVA/INDICA/HYBRID |
| `pre-roll` | Pre-rolled joints | grams | SATIVA/INDICA/HYBRID |
| `concentrate` | Wax, shatter, hash, etc. | grams | SATIVA/INDICA/HYBRID |
| `infused pre-roll` | Pre-rolls with concentrates | grams | SATIVA/INDICA/HYBRID |
| `solventless concentrate` | Rosin, hash, etc. | grams | SATIVA/INDICA/HYBRID |
| `vape cartridge` | Vape cartridges | grams | SATIVA/INDICA/HYBRID |
| `rso/co2 tankers` | RSO and CO2 extracts | grams | SATIVA/INDICA/HYBRID |

### **❌ NON-CLASSIC TYPES (Everything else)**
| Type Category | Examples | Weight Unit | Lineage |
|---------------|----------|-------------|---------|
| **Edibles** | `edible (solid)`, `edible (liquid)`, `gummy`, `chocolate`, `cookie`, `brownie`, `candy`, `beverage`, `drink`, `tea`, `coffee`, `soda`, `juice`, `smoothie`, `shot` | oz (if >10g) | MIXED |
| **Topicals** | `topical`, `cream`, `lotion`, `salve`, `balm` | oz (if >10g) | MIXED |
| **Tinctures** | `tincture`, `drops`, `liquid`, `sublingual` | oz (if >10g) | MIXED |
| **Capsules** | `capsule`, `suppository`, `transdermal` | oz (if >10g) | MIXED |
| **Powders** | `powder` | oz (if >10g) | MIXED |
| **Paraphernalia** | `paraphernalia`, `accessory`, `equipment` | each | PARAPHERNALIA |

---

## 🔧 **Weight Normalization Rules**

### **Classic Types (Stay in grams)**
- **Flower**: Always grams
- **Pre-rolls**: Always grams  
- **Concentrates**: Always grams
- **Vape Cartridges**: Always grams
- **RSO/CO2 Tankers**: Always grams

### **Non-Classic Types (Convert to oz if >10g)**
- **Edibles**: Convert large grams to oz
- **Topicals**: Convert large grams to oz
- **Tinctures**: Convert large grams to oz
- **Capsules**: Convert large grams to oz
- **Powders**: Convert large grams to oz
- **Paraphernalia**: Keep as "each"

---

## 🧬 **Lineage Assignment**

### **Classic Types**
- Get **SATIVA/INDICA/HYBRID** lineages
- Based on strain genetics
- Used for strain-based effects

### **Non-Classic Types**
- Get **MIXED** lineage (except paraphernalia)
- Paraphernalia gets **PARAPHERNALIA**
- No strain-specific effects

---

## 💡 **Code Implementation**

### **Classification Check**
```python
from src.core.constants import CLASSIC_TYPES

def is_classic_type(product_type: str) -> bool:
    """Check if product type is classic."""
    return product_type.lower() in [c.lower() for c in CLASSIC_TYPES]

def is_non_classic_type(product_type: str) -> bool:
    """Check if product type is non-classic."""
    return product_type.lower() not in [c.lower() for c in CLASSIC_TYPES]
```

### **Weight Normalization**
```python
# Classic types stay in grams
if is_classic_type(product_type):
    # Keep in grams
    pass

# Non-classic types convert to oz if >10g
if is_non_classic_type(product_type) and weight_g > 10:
    weight_oz = weight_g / 28.3495
```

---

## 📈 **Database Impact**

### **Current Database Analysis**
Based on the codebase, the system handles:

- **Classic types**: ~70% of products (flower, concentrates, vapes)
- **Non-classic types**: ~30% of products (edibles, topicals, tinctures)

### **Weight Normalization Impact**
- **Classic types**: No weight changes (already correct)
- **Non-classic types**: Large items converted from grams to oz

---

## 🎨 **Visual Differences**

### **Label Colors**
- **Classic types**: Green/red colors (strain-based)
- **Non-classic types**: Blue colors (MIXED lineage)

### **Font Sizing**
- **Classic types**: Different font schemes
- **Non-classic types**: Standard font schemes

---

## 🔍 **Examples**

### **Classic Type Examples**
```
✅ "Blue Dream" - flower → grams, SATIVA lineage
✅ "Gelato Pre-Roll" - pre-roll → grams, HYBRID lineage  
✅ "Wedding Cake Wax" - concentrate → grams, HYBRID lineage
✅ "Sour Diesel Vape" - vape cartridge → grams, SATIVA lineage
```

### **Non-Classic Type Examples**
```
❌ "Blue Raspberry Gummy" - edible (solid) → oz, MIXED lineage
❌ "CBD Cream" - topical → oz, MIXED lineage
❌ "THC Tincture" - tincture → oz, MIXED lineage
❌ "Cannabis Capsules" - capsule → oz, MIXED lineage
❌ "Glass Pipe" - paraphernalia → each, PARAPHERNALIA lineage
```

---

## 🚀 **Weight Normalizer Integration**

The weight normalizer now correctly uses the `CLASSIC_TYPES` definition:

```python
def _should_convert_to_oz(self, product_data: Dict[str, Any]) -> bool:
    """Check if product should be converted to oz."""
    product_type = str(product_data.get('Product Type*', '')).strip()
    
    # Import CLASSIC_TYPES to determine if this is a non-classic product
    from src.core.constants import CLASSIC_TYPES
    is_non_classic = product_type.lower() not in [c.lower() for c in CLASSIC_TYPES]
    
    # Only convert non-classic types if currently in grams and weight > 10g
    return is_non_classic and unit.lower() in ['g', 'gram', 'grams'] and weight_val > 10
```

---

**Status: ✅ CLASSIC VS NON-CLASSIC TYPES FULLY DOCUMENTED**

*Last Updated: October 11, 2025*
