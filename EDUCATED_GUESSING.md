# Educated Guessing System

## Overview

The Educated Guessing System is a powerful feature that automatically infers product information for items that don't exist in either the database or Excel sheet. Instead of leaving fields empty or using generic defaults, the system analyzes similar existing products to make intelligent estimates for weight, price, product type, strain information, and other properties.

## How It Works

### 1. **Multi-Strategy Similarity Matching**

The system uses three complementary strategies to find similar products:

- **Name-based Matching**: Extracts key terms from product names and finds products with similar terminology
- **Product Type Matching**: Identifies products of the same type (flower, concentrate, vape, etc.)
- **Strain Matching**: Finds products with similar strain names or characteristics

### 2. **Intelligent Property Inference**

For each property, the system uses different approaches:

- **Weight & Units**: Uses median values from similar products, with pattern matching fallbacks
- **Price**: Calculates median price from similar products, with type-based estimation
- **Product Type**: Uses keyword analysis and similarity matching
- **Strain & Lineage**: Extracts from product names and matches against known strains
- **Brand & Vendor**: Uses provided information or extracts from similar products

### 3. **Confidence Scoring**

Each educated guess includes a confidence level:
- **High**: Strong similarity with multiple matching products
- **Medium**: Moderate similarity with some matching products  
- **Low**: Weak similarity, relying on pattern matching

## Example Use Cases

### Example 1: New Product Variant
```
Input: "Glazed Apricots Live Resin Disposable Vape"
Existing: "Wedding Cake Live Resin Disposable Vape"

Result:
- Product Type: vape (from existing similar product)
- Weight: 0.5g (median from similar vapes)
- Price: $40 (median from similar vapes)
- Strain: Glazed Apricots (extracted from name)
- Lineage: HYBRID (inferred from strain characteristics)
```

### Example 2: Different Format
```
Input: "Blueberry Kush Flower 3.5g"
Existing: "Blueberry Kush Concentrate 1g"

Result:
- Product Type: flower (from name analysis)
- Weight: 3.5g (extracted from name)
- Price: $120 (flower pricing for 3.5g)
- Strain: Blueberry Kush (from existing product)
- Lineage: INDICA (from strain characteristics)
```

### Example 3: New Brand
```
Input: "Sour Diesel Pre-Roll 1g" (new brand)
Existing: "Sour Diesel Flower 3.5g" (different brand)

Result:
- Product Type: pre-roll (from name analysis)
- Weight: 1g (extracted from name)
- Price: $20 (pre-roll pricing)
- Strain: Sour Diesel (from existing product)
- Lineage: SATIVA (from strain characteristics)
```

## Integration Points

### 1. **JSON Matcher Integration**

When processing JSON inventory data, the system now follows this priority:

1. **Exact Database Match** - Use existing product information
2. **Educated Guess** - Infer from similar products
3. **JSON Processing** - Create new product from JSON data

### 2. **Excel Processor Integration**

For manual product additions:

```python
# Add a new product with educated guessing
excel_processor.add_product_with_educated_guess(
    product_name="New Product Name",
    vendor="Vendor Name",
    brand="Brand Name"
)
```

### 3. **Product Database Integration**

Direct educated guessing:

```python
from src.core.data.product_database import ProductDatabase

product_db = ProductDatabase()
educated_guess = product_db.make_educated_guess(
    product_name="Product Name",
    vendor="Vendor Name", 
    brand="Brand Name"
)
```

## Configuration

### Similarity Thresholds

The system uses configurable thresholds for similarity matching:

- **Name Similarity**: 30% word overlap for comprehensive matching
- **Type Matching**: Exact product type matches
- **Strain Matching**: Partial strain name matches

### Fallback Strategies

When no similar products are found:

1. **Pattern Matching**: Extract information from product names
2. **Type-based Defaults**: Use industry-standard defaults
3. **Conservative Estimates**: Use safe, conservative values

## Benefits

### 1. **Improved Data Quality**
- Reduces empty or generic fields
- Provides realistic estimates based on actual data
- Maintains consistency with existing products

### 2. **Time Savings**
- Automatically fills in missing information
- Reduces manual data entry
- Speeds up product onboarding

### 3. **Better User Experience**
- Users get complete product information immediately
- Reduces the need for manual corrections
- Provides confidence levels for transparency

### 4. **Data Consistency**
- Uses actual market data for estimates
- Maintains pricing consistency within product types
- Preserves strain and lineage relationships

## Testing

Run the test script to see educated guessing in action:

```bash
python test_educated_guess.py
```

This will demonstrate the system with various product examples and show how it makes intelligent inferences.

## Monitoring and Logging

The system provides detailed logging for transparency:

- **Similarity Scores**: Shows how similar products were matched
- **Inference Details**: Explains how each property was inferred
- **Confidence Levels**: Indicates the reliability of each guess
- **Fallback Usage**: Shows when pattern matching was used

## Future Enhancements

Potential improvements to the educated guessing system:

1. **Machine Learning**: Train models on historical data for better predictions
2. **Market Data Integration**: Use real-time pricing data
3. **Strain Database**: Expand strain recognition capabilities
4. **User Feedback**: Learn from user corrections to improve accuracy
5. **Regional Pricing**: Account for geographic price variations

## Conclusion

The Educated Guessing System transforms how new products are handled in the system. Instead of requiring complete manual entry or leaving fields empty, it provides intelligent, data-driven estimates that improve both data quality and user experience. The system is transparent about its confidence levels and provides detailed logging for monitoring and improvement.
