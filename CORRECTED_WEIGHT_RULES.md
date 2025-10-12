# Corrected Weight Normalization Rules

## Overview
**Non-classic types are in oz** - The weight normalization system has been corrected to properly handle classic vs non-classic product type distinctions.

---

## 🎯 **Corrected Rules (10 Total)**

### **Rule 1: Constellation Moonshots**
- **Type:** All Moonshots
- **Action:** Always 1.7oz (fixes 2.5oz issue)
- **Example:** `2.5oz` → `1.7oz`

### **Rule 2: Major Beverages**
- **Type:** Classic - Edible (Liquid)
- **Action:** 190g → 6.7oz
- **Example:** `190g` → `6.7oz`

### **Rule 3: Generic 190g Products**
- **Type:** All non-concentrates
- **Action:** 190g → 6.7oz
- **Example:** `190g` → `6.7oz`

### **Rule 4: Classic Types - Edible Liquid**
- **Type:** Classic - Edible (Liquid)
- **Action:** Convert large grams → oz
- **Example:** `50g` → `1.76oz`

### **Rule 5: Non-Classic Types - Topicals & Tinctures**
- **Type:** Non-Classic - Topical, Tincture
- **Action:** Convert large grams → oz
- **Example:** `50g` → `1.76oz`

### **Rule 6: Concentrates (Classic)**
- **Type:** Classic - Concentrate, Solventless Concentrate
- **Action:** Convert oz → grams (stay in g)
- **Example:** `1oz` → `28.35g`

### **Rule 7: Non-Classic Types (All)**
- **Type:** Non-Classic - Vape Cartridge, Capsule, Topical, Tincture, etc.
- **Action:** Convert grams → oz
- **Example:** `28g` → `0.99oz`

### **Rule 8: Paraphernalia (Non-Classic)**
- **Type:** Non-Classic - Paraphernalia
- **Action:** Standardize "each" units
- **Example:** `0each` → `1each`

### **Rule 9: Edible Solids (Classic)**
- **Type:** Classic - Edible (Solid)
- **Action:** Convert large grams → oz
- **Example:** `50g` → `1.76oz`

### **Rule 10: Pre-Rolls (Classic)**
- **Type:** Classic - Pre-Roll, Infused Pre-Roll
- **Action:** Convert oz → grams
- **Example:** `0.5oz` → `14.17g`

---

## 🏗️ **Corrected Classic vs Non-Classic Rules**

### **Classic Types (Cannabis Industry Standards):**
- **Flower:** Always in grams
- **Pre-Roll:** Always in grams
- **Concentrates:** Always in grams
- **Edible (Solid):** Grams for small, oz for large
- **Edible (Liquid):** Always in oz

### **Non-Classic Types (Retail Standards):**
- **Vape Cartridges:** Always in oz
- **Capsules:** Always in oz
- **Topicals:** Always in oz
- **Tinctures:** Always in oz
- **Paraphernalia:** "each" units

---

## 🧪 **Test Results (14/14 Passed)**

```
Test 1: Green Apple Moonshot → 2.5oz → 1.7oz ✅
Test 2: Orange Moonshot → 2.5oz → 1.7oz ✅
Test 3: Major Beverage → 190g → 6.7oz ✅
Test 4: Generic 190g → 190g → 6.7oz ✅
Test 5: Bath Salts → 50g → 1.76oz ✅
Test 6: Blue Dream → 3.5oz → 99.22g ✅
Test 7: Wax Product → 1oz → 28.35g ✅
Test 8: Regular Product → 2.0oz → 2.0oz ✅
Test 9: Blue Dream Vape Cartridge → 28g → 0.99oz ✅
Test 10: CBD Cream → 50g → 1.76oz ✅
Test 11: CBD Capsules → 10g → 0.35oz ✅
Test 12: Large Gummy Package → 50g → 1.76oz ✅
Test 13: Pipe → 0each → 1each ✅
Test 14: Blue Dream Pre-Roll → 0.5oz → 14.17g ✅

RESULTS: 14 passed, 0 failed
🎉 All tests passed!
```

---

## 📊 **Key Corrections Made**

### **Before (Incorrect):**
- Non-classic types were being converted to grams
- Vape cartridges: `0.5oz` → `14.17g` ❌
- Capsules: `0.35oz` → `9.92g` ❌
- Small topicals: `0.05oz` → `1.42g` ❌

### **After (Correct):**
- Non-classic types stay in oz
- Vape cartridges: `28g` → `0.99oz` ✅
- Capsules: `10g` → `0.35oz` ✅
- Topicals: `50g` → `1.76oz` ✅

---

## 🎯 **Final Rule Summary**

### **Classic Types → Grams:**
- Flower, Pre-Rolls, Concentrates

### **Classic Types → oz:**
- Edible Liquids, Large Edible Solids

### **Non-Classic Types → oz:**
- Vape Cartridges, Capsules, Topicals, Tinctures

### **Special Cases:**
- Constellation Moonshots: Always 1.7oz
- Major Beverages: 190g → 6.7oz
- Paraphernalia: "each" units

---

**Status: ✅ CORRECTED - Non-classic types properly use oz!**

*Last Updated: October 11, 2025*
