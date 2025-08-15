# Final Duplication Fix Summary

## The Root Cause Identified

After extensive debugging and testing, I finally identified the **exact root cause** of the "CONSTELLATION CANNABISCONSTELLATION CANNABIS" duplication issue:

**The Lineage field was being set to the wrapped ProductBrand content in multiple places, causing double-marking and duplication.**

## What Was Happening

### 1. **Context Building (Working Correctly)**
- ProductBrand was properly wrapped with `PRODUCTBRAND_CENTER_STARTCONSTELLATION CANNABISPRODUCTBRAND_CENTER_END`
- Lineage was properly wrapped with `LINEAGE_STARTCONSTELLATION CANNABISLINEAGE_END`

### 2. **Template Expansion (Working Correctly)**
- Template content was preserved without destruction
- Placeholders were correctly updated (e.g., `{{Label1.ProductBrand}}` to `{{Label{cnt}.ProductBrand}}`)

### 3. **Manual Placeholder Replacement (Working Correctly)**
- The `DocxTemplate` or manual replacement logic correctly substituted placeholders with the marked content from the context.

### 4. **The Problematic Lineage Overwriting**
- After the context was built correctly, there was **another section of code** that was overwriting the Lineage field with the wrapped ProductBrand content.
- This happened around line 2137 in the template processor, where `lineage_value` was set to the wrapped ProductBrand instead of the unwrapped value.
- This resulted in the Lineage field containing `LINEAGE_START PRODUCTBRAND_CENTER_STARTCONSTELLATION CANNABISPRODUCTBRAND_CENTER_ENDLINEAGE_END`
- When markers were unwrapped, this displayed as `CONSTELLATION CANNABISCONSTELLATION CANNABIS` due to the nested marker structure.

## The Solution

The solution was to fix **two places** in the code:

### Fix 1: Context Building (Lines 1817-1830)
- Ensure that when building the context for non-classic types, the Lineage field uses the unwrapped ProductBrand value.

### Fix 2: Lineage Processing (Lines 2095-2100)
- Ensure that when processing the Lineage field later in the method, it also uses the unwrapped ProductBrand value instead of the wrapped one.

## Code Changes

**File:** `src/core/generation/template_processor.py`

**Fix 1 - Context Building:**
```python
if product_type in edible_types:
    # For edibles, use ProductBrand instead of Lineage to prevent duplication
    if wrapped_product_brand:
        # CRITICAL: Unwrap the PRODUCTBRAND_CENTER markers from the wrapped ProductBrand
        # This ensures we get just the raw brand name for Lineage
        raw_brand = unwrap_marker(wrapped_product_brand, 'PRODUCTBRAND_CENTER')
        label_context['Lineage'] = wrap_with_marker(raw_brand, 'LINEAGE')
```

**Fix 2 - Lineage Processing:**
```python
if product_type in edible_types:
    # CRITICAL: Use the UNWRAPPED ProductBrand value, not the wrapped one
    # This prevents the duplication issue where Lineage contains wrapped ProductBrand content
    lineage_value = unwrap_marker(product_brand, 'PRODUCTBRAND_CENTER')
```

## Verification

Running the test scripts after these fixes confirmed that:
- ✅ **No duplication found in generated document!**
- ✅ **The duplication fix is working!**
- ✅ Lineage field is correctly set to `LINEAGE_STARTCONSTELLATION CANNABISLINEAGE_END`
- ✅ No more `CONSTELLATION CANNABISCONSTELLATION CANNABIS` duplication

## Summary

The duplication issue was caused by the Lineage field being set to wrapped ProductBrand content in multiple places in the code. By ensuring that both the context building and the later lineage processing use the unwrapped ProductBrand value, the duplication is completely resolved.

This fix addresses the root cause rather than trying to work around it, ensuring a clean and reliable solution.
