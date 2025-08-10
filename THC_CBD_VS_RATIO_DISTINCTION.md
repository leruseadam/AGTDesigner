# THC_CBD vs Ratio Field Distinction

## Overview
This document explains the proper distinction between THC_CBD and Ratio fields in the label generation system to ensure consistent formatting and proper field handling.

## Field Definitions

### THC_CBD Field
- **Purpose**: Contains percentage-based THC/CBD content for classic cannabis products
- **Format**: "THC: 25.5% | CBD: 2.1%" or similar percentage-based content
- **Usage**: Applied to classic cannabis product types (flower, pre-roll, concentrate, etc.)
- **Font Sizing**: Uses `thc_cbd` field type with smaller, more compact font sizing
- **Line Spacing**: Uses tighter line spacing (1.3-1.5) for better readability
- **Marker**: `THC_CBD_START` / `THC_CBD_END`

### Ratio Field
- **Purpose**: Contains ratio information for non-classic products or mg-based content
- **Format**: "1:1", "2:1", "10mg THC / 5mg CBD" or similar ratio/mg content
- **Usage**: Applied to edibles, tinctures, or other non-classic cannabis products
- **Font Sizing**: Uses `ratio` field type with standard font sizing
- **Line Spacing**: Uses standard line spacing (2.4) for better readability
- **Marker**: `RATIO_START` / `RATIO_END`

## Product Type Classification

### Classic Types (Use THC_CBD)
- flower
- pre-roll
- infused pre-roll
- concentrate
- solventless concentrate
- vape cartridge
- rso/co2 tankers

### Non-Classic Types (Use Ratio)
- edible
- tincture
- topicals
- other non-classic products

## Content Detection Logic

### THC_CBD Detection
Content is classified as THC_CBD if:
1. Product type is classic AND
2. Content contains percentage symbols (%) AND
3. Content contains "THC:" or "CBD:" indicators

### Ratio Detection
Content is classified as Ratio if:
1. Product type is non-classic OR
2. Content contains ratio indicators (":") OR
3. Content contains mg-based measurements OR
4. Content doesn't meet THC_CBD criteria

## Implementation Changes

### 1. Excel Processor Updates
- Separate logic for setting THC_CBD vs Ratio fields
- Product type-based classification
- Content format validation

### 2. Template Processor Updates
- Proper marker assignment based on content type
- Consistent field handling
- Font sizing and line spacing application

### 3. Tag Generator Updates
- Support for both THC_CBD and Ratio markers
- Proper field mapping
- Backward compatibility maintenance

## Font Sizing Configuration

### THC_CBD Font Sizes
- **Mini**: 8pt base, scaling down to 4pt
- **Double**: 8pt base, scaling down to 6.5pt
- **Vertical**: 11pt base, scaling down to 6pt
- **Horizontal**: 14pt base (fixed)

### Ratio Font Sizes
- **Mini**: 10pt base, scaling down to 6pt
- **Double**: 9pt base, scaling down to 5pt
- **Vertical**: 12pt base, scaling down to 10pt
- **Horizontal**: 14pt base, scaling down to 6pt

## Line Spacing Configuration

### THC_CBD Line Spacing
- **Mini**: 1.3
- **Double**: 1.4
- **Vertical**: 1.3
- **Horizontal**: 1.35

### Ratio Line Spacing
- **All Templates**: 2.4 (consistent across all template types)

## Migration Notes

### Backward Compatibility
- `Ratio_or_THC_CBD` field is maintained for existing templates
- New templates can use separate `THC_CBD` and `Ratio` fields
- Automatic fallback to combined field if separate fields are not available

### Template Updates
- Existing templates will continue to work with the combined field
- New templates can be designed with separate fields for better control
- Font sizing and line spacing will be automatically applied based on content type

## Testing

### Test Cases
1. Classic product with percentage THC/CBD → Should use THC_CBD field
2. Non-classic product with ratio → Should use Ratio field
3. Mixed content → Should default to appropriate field type
4. Empty content → Should handle gracefully

### Validation
- Font sizes should be appropriate for content type
- Line spacing should match field type
- Markers should be correctly applied
- Content should be properly formatted
