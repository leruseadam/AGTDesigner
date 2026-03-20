"""
Smart Excel normalization module for comprehensive data cleaning and standardization.
Handles weight normalization, unit conversion, data validation, and consistency checks.
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class SmartExcelNormalizer:
    """Comprehensive Excel data normalization for all product fields."""
    
    def __init__(self):
        self.weight_normalizer = None  # Will be imported when needed
        self.validator = None  # Will be imported when needed
        self.normalization_stats = {
            'weights_normalized': 0,
            'units_converted': 0,
            'names_cleaned': 0,
            'brands_standardized': 0,
            'types_corrected': 0,
            'prices_normalized': 0,
            'thc_cbd_cleaned': 0,
            'ratios_standardized': 0,
            'validation_errors': 0,
            'validation_warnings': 0
        }

    def debug_log_vendor_columns(self, product_data: Dict[str, Any]):
        """Log all possible vendor/brand fields and their values for this product."""
        try:
            vendor_fields = [
                'Vendor/Supplier*', 'Vendor', 'vendor', 'Product Brand', 'Brand', 'brand'
            ]
            values = {field: product_data.get(field, None) for field in vendor_fields}
            logger.debug(f"[VENDOR DEBUG] Product: {product_data.get('Product Name*', '')} | Vendor fields: {values}")
        except Exception:
            logger.debug("Failed to debug vendor columns for product.")
    
    def normalize_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive normalization of all product data fields.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with normalized product data
        """
        try:
            # Create a copy to avoid modifying the original
            normalized_data = product_data.copy()
            
            # 1. Weight and Unit Normalization
            normalized_data = self._normalize_weights_and_units(normalized_data)
            
            # 2. Product Name Cleaning
            normalized_data = self._normalize_product_name(normalized_data)
            
            # 3. Brand Standardization
            normalized_data = self._normalize_brand(normalized_data)
            
            # 4. Product Type Correction
            normalized_data = self._normalize_product_type(normalized_data)
            
            # 5. Price Normalization
            normalized_data = self._normalize_price(normalized_data)
            
            # 6. THC/CBD Content Cleaning
            normalized_data = self._normalize_thc_cbd_content(normalized_data)
            
            # 7. Ratio Standardization
            normalized_data = self._normalize_ratios(normalized_data)
            
            # 8. Vendor/Supplier Normalization
            normalized_data = self._normalize_vendor(normalized_data)
            
            # 9. Description Enhancement
            normalized_data = self._enhance_description(normalized_data)
            
            # 10. Barcode Validation
            normalized_data = self._validate_barcode(normalized_data)
            
            # 11. Data Validation
            normalized_data = self._validate_data_quality(normalized_data)
            
            # Add normalization metadata
            normalized_data['normalized_at'] = datetime.now().isoformat()
            normalized_data['normalization_version'] = '2.0'
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing product data: {e}")
            return product_data
    
    def _normalize_weights_and_units(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize weight and units using the weight normalizer."""
        try:
            # Import weight normalizer
            from src.core.data.weight_normalizer import weight_normalizer
            
            # Apply weight normalization
            normalized_data = weight_normalizer.normalize_product_data(product_data)
            
            # Check if weights were actually changed
            original_weight = str(product_data.get('Weight*', ''))
            original_unit = str(product_data.get('Units', ''))
            new_weight = str(normalized_data.get('Weight*', ''))
            new_unit = str(normalized_data.get('Units', ''))
            
            if original_weight != new_weight or original_unit != new_unit:
                self.normalization_stats['weights_normalized'] += 1
                logger.info(f"Weight normalized: {original_weight}{original_unit} → {new_weight}{new_unit}")
            
            return normalized_data
            
        except Exception as e:
            logger.warning(f"Failed to normalize weights: {e}")
            return product_data
    
    def _normalize_product_name(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize product names."""
        try:
            product_name = str(product_data.get('Product Name*', '')).strip()
            
            if not product_name or product_name.lower() in ['nan', 'none', 'null']:
                return product_data
            
            # Remove extra whitespace and normalize
            cleaned_name = re.sub(r'\s+', ' ', product_name).strip()
            
            # Fix common naming issues
            cleaned_name = self._fix_product_name_patterns(cleaned_name)
            
            if cleaned_name != product_name:
                product_data['Product Name*'] = cleaned_name
                self.normalization_stats['names_cleaned'] += 1
                logger.info(f"Product name cleaned: '{product_name}' → '{cleaned_name}'")
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to normalize product name: {e}")
            return product_data
    
    def _fix_product_name_patterns(self, name: str) -> str:
        """Fix common product name patterns."""
        # Remove duplicate words
        words = name.split()
        cleaned_words = []
        prev_word = None
        
        for word in words:
            if word.lower() != prev_word:
                cleaned_words.append(word)
                prev_word = word.lower()
        
        return ' '.join(cleaned_words)
    
    def _normalize_brand(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize brand/vendor names using all possible aliases, no inference."""
        try:
            self.debug_log_vendor_columns(product_data)
            vendor_fields = [
                'Vendor/Supplier*', 'Vendor', 'vendor', 'Product Brand', 'Brand', 'brand'
            ]
            brand = ''
            for field in vendor_fields:
                val = str(product_data.get(field, '')).strip()
                if val and val.lower() not in ['nan', 'none', 'null', '']:
                    brand = val
                    break
            if not brand:
                logger.warning(f"No vendor/brand found for product: {product_data.get('Product Name*', '')}")
                return product_data
            # Standardize brand formatting
            standardized_brand = self._standardize_brand_format(brand)
            if standardized_brand != brand:
                product_data['Product Brand'] = standardized_brand
                self.normalization_stats['brands_standardized'] += 1
                logger.info(f"Brand standardized: '{brand}' → '{standardized_brand}'")
            else:
                product_data['Product Brand'] = brand
            return product_data
        except Exception as e:
            logger.warning(f"Failed to normalize brand: {e}")
            return product_data
    
    def _extract_brand_from_name(self, product_name: str) -> Optional[str]:
        """Extract brand name from product name."""
        if not product_name:
            return None
        
        # Look for "by Brand" pattern
        by_pattern = r'by\s+([A-Za-z][A-Za-z\s&]+?)(?:\s+-|\s+–|\s*$)'
        match = re.search(by_pattern, product_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _standardize_brand_format(self, brand: str) -> str:
        """Standardize brand name formatting."""
        # Remove extra whitespace
        brand = re.sub(r'\s+', ' ', brand).strip()
        
        # Fix common brand issues
        brand_fixes = {
            'constellation cannabis': 'Constellation Cannabis',
            'major': 'Major',
            'dank czar': 'Dank Czar',
            'sticky frog': 'Sticky Frog',
            'snickle fritz': 'Snickle Fritz',
            'dabstract': 'Dabstract'
        }
        
        return brand_fixes.get(brand.lower(), brand)
    
    def _normalize_product_type(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Correct and standardize product types."""
        try:
            from src.core.constants import CLASSIC_TYPES, TYPE_OVERRIDES
            product_type = str(product_data.get('Product Type*', '')).strip()
            original_type = product_type
            
            # Map using TYPE_OVERRIDES if available
            if product_type.lower() in TYPE_OVERRIDES:
                product_type = TYPE_OVERRIDES[product_type.lower()]
            
            # If missing/invalid, try to infer from product name
            if not product_type or product_type.lower() in ['nan', 'none', 'null']:
                product_name = str(product_data.get('Product Name*', ''))
                inferred_type = self._infer_product_type(product_name)
                if inferred_type:
                    product_type = inferred_type
                    product_data['Product Type*'] = inferred_type
                    self.normalization_stats['types_corrected'] += 1
                    logger.info(f"Product type inferred: '{inferred_type}'")
                else:
                    logger.warning(f"Unmapped product type for product '{product_name}' (Excel type: '{original_type}')")
                return product_data
            
            # Standardize product type
            standardized_type = self._standardize_product_type(product_type)
            
            # Check if standardized type is a classic type
            if standardized_type.lower() in CLASSIC_TYPES:
                product_data['Product Type*'] = standardized_type
                self.normalization_stats['types_corrected'] += 1
                logger.info(f"Product type corrected: '{original_type}' → '{standardized_type}' (classic)")
            else:
                # Log unmapped types for review
                logger.warning(f"Unmapped/non-classic product type: '{standardized_type}' (original: '{original_type}')")
                product_data['Product Type*'] = standardized_type
            return product_data
        except Exception as e:
            logger.warning(f"Failed to normalize product type: {e}")
            return product_data
    
    def _infer_product_type(self, product_name: str) -> Optional[str]:
        """Coarse name hints only — shared json_matcher rules (no dessert words → edible)."""
        from src.core.data.json_matcher import infer_product_type_from_name

        if not product_name:
            return None
        t = infer_product_type_from_name(product_name)
        if not t or t == "Unknown Type":
            return None
        if t == "Pre-roll":
            return "Pre-Roll"
        nl = product_name.lower()
        if t == "Concentrate" and ("rosin" in nl or "solventless" in nl):
            return "Solventless Concentrate"
        return t
    
    def _standardize_product_type(self, product_type: str) -> str:
        """Standardize product type formatting."""
        # Remove extra whitespace
        product_type = re.sub(r'\s+', ' ', product_type).strip()
        
        # Type standardization mappings
        type_standardization = {
            'edible solid': 'Edible (Solid)',
            'edible (solid)': 'Edible (Solid)',
            'edible liquid': 'Edible (Liquid)',
            'edible (liquid)': 'Edible (Liquid)',
            'pre roll': 'Pre-Roll',
            'pre-roll': 'Pre-Roll',
            'infused pre roll': 'Infused Pre-Roll',
            'infused pre-roll': 'Infused Pre-Roll',
            'vape cartridge': 'Vape Cartridge',
            'solventless concentrate': 'Solventless Concentrate'
        }
        
        return type_standardization.get(product_type.lower(), product_type)
    
    def _normalize_price(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize price formatting."""
        try:
            price = str(product_data.get('Price*', product_data.get('Price', ''))).strip()
            if not price or price.lower() in ['nan', 'none', 'null', '']:
                logger.warning(f"Missing or invalid price for product: {product_data.get('Product Name*', '')}")
                return product_data
            # Clean price
            cleaned_price = self._clean_price(price)
            if cleaned_price != price:
                product_data['Price*'] = cleaned_price
                self.normalization_stats['prices_normalized'] += 1
                logger.info(f"Price normalized: '{price}' → '{cleaned_price}'")
            return product_data
        except Exception as e:
            logger.warning(f"Failed to normalize price: {e}")
            return product_data
    
    def _clean_price(self, price: str) -> str:
        """Clean and format price."""
        # Remove currency symbols and extra characters
        cleaned = re.sub(r'[^\d.,]', '', price)
        
        # Handle different decimal formats
        if ',' in cleaned and '.' in cleaned:
            # European format (1,234.56)
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Check if it's decimal separator
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        # Ensure proper decimal format
        try:
            price_float = float(cleaned)
            return f"{price_float:.2f}"
        except ValueError:
            return price
    
    def _normalize_thc_cbd_content(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize THC/CBD content values."""
        try:
            # THC content
            thc_fields = ['THC test result', 'THC Content', 'THC', 'THCA']
            for field in thc_fields:
                if field in product_data:
                    original_value = str(product_data[field])
                    cleaned_value = self._clean_cannabinoid_value(original_value)
                    if cleaned_value != original_value:
                        product_data[field] = cleaned_value
                        self.normalization_stats['thc_cbd_cleaned'] += 1
            
            # CBD content
            cbd_fields = ['CBD test result', 'CBD Content', 'CBD', 'CBDA']
            for field in cbd_fields:
                if field in product_data:
                    original_value = str(product_data[field])
                    cleaned_value = self._clean_cannabinoid_value(original_value)
                    if cleaned_value != original_value:
                        product_data[field] = cleaned_value
                        self.normalization_stats['thc_cbd_cleaned'] += 1
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to normalize THC/CBD content: {e}")
            return product_data
    
    def _clean_cannabinoid_value(self, value: str) -> str:
        """Clean cannabinoid percentage values."""
        if not value or value.lower() in ['nan', 'none', 'null', '']:
            return '0.0'
        
        # Remove percentage signs and extra text
        cleaned = re.sub(r'[^\d.,]', '', str(value))
        
        # Handle decimal formats
        if ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        try:
            float_val = float(cleaned)
            return f"{float_val:.1f}"
        except ValueError:
            return value
    
    def _normalize_ratios(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize ratio formats."""
        try:
            ratio_fields = ['Ratio', 'Ratio_or_THC_CBD', 'JointRatio']
            
            for field in ratio_fields:
                if field in product_data:
                    original_ratio = str(product_data[field])
                    cleaned_ratio = self._clean_ratio(original_ratio)
                    
                    if cleaned_ratio != original_ratio:
                        product_data[field] = cleaned_ratio
                        self.normalization_stats['ratios_standardized'] += 1
                        logger.info(f"Ratio standardized: '{original_ratio}' → '{cleaned_ratio}'")
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to normalize ratios: {e}")
            return product_data
    
    def _clean_ratio(self, ratio: str) -> str:
        """Clean and standardize ratio format."""
        if not ratio or ratio.lower() in ['nan', 'none', 'null', '']:
            return ''
        
        # Standardize common ratio formats
        ratio_patterns = {
            r'(\d+):(\d+)': r'\1:\2',  # 1:1, 2:1, etc.
            r'(\d+)\s*to\s*(\d+)': r'\1:\2',  # 1 to 1
            r'(\d+)\s*/\s*(\d+)': r'\1:\2',  # 1/1
        }
        
        for pattern, replacement in ratio_patterns.items():
            if re.search(pattern, ratio, re.IGNORECASE):
                return re.sub(pattern, replacement, ratio, flags=re.IGNORECASE)
        
        return ratio
    
    def _normalize_vendor(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize vendor/supplier information."""
        try:
            vendor_fields = ['Vendor/Supplier*', 'Vendor/Supplier', 'Vendor']
            
            for field in vendor_fields:
                if field in product_data:
                    vendor = str(product_data[field]).strip()
                    if vendor and vendor.lower() not in ['nan', 'none', 'null']:
                        # Use the same brand standardization
                        standardized_vendor = self._standardize_brand_format(vendor)
                        if standardized_vendor != vendor:
                            product_data[field] = standardized_vendor
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to normalize vendor: {e}")
            return product_data
    
    def _enhance_description(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance product descriptions."""
        try:
            description = str(product_data.get('Description', '')).strip()
            
            if not description or description.lower() in ['nan', 'none', 'null']:
                # Generate description from product name and type
                product_name = str(product_data.get('Product Name*', ''))
                product_type = str(product_data.get('Product Type*', ''))
                
                if product_name and product_type:
                    generated_description = f"{product_type}: {product_name}"
                    product_data['Description'] = generated_description
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to enhance description: {e}")
            return product_data
    
    def _validate_barcode(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean barcode format."""
        try:
            barcode = str(product_data.get('Barcode*', '')).strip()
            
            if barcode and barcode.lower() not in ['nan', 'none', 'null']:
                # Remove non-numeric characters
                cleaned_barcode = re.sub(r'[^\d]', '', barcode)
                
                if cleaned_barcode != barcode:
                    product_data['Barcode*'] = cleaned_barcode
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to validate barcode: {e}")
            return product_data
    
    def get_normalization_stats(self) -> Dict[str, int]:
        """Get normalization statistics."""
        return self.normalization_stats.copy()
    
    def _validate_data_quality(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality and add validation metadata."""
        try:
            # Import validator
            from src.core.data.excel_data_validator import excel_data_validator
            
            # Validate the data
            is_valid, errors = excel_data_validator.validate_product_data(product_data)
            
            # Add validation metadata
            product_data['validation_status'] = 'valid' if is_valid else 'invalid'
            product_data['validation_errors'] = errors
            product_data['validation_timestamp'] = datetime.now().isoformat()
            
            # Update stats
            if errors:
                self.normalization_stats['validation_errors'] += len(errors)
                logger.warning(f"Validation errors for product {product_data.get('Product Name*', 'Unknown')}: {errors}")
            else:
                self.normalization_stats['validation_warnings'] += 1
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Failed to validate data quality: {e}")
            product_data['validation_status'] = 'error'
            product_data['validation_errors'] = [str(e)]
            return product_data
    
    def reset_stats(self):
        """Reset normalization statistics."""
        self.normalization_stats = {
            'weights_normalized': 0,
            'units_converted': 0,
            'names_cleaned': 0,
            'brands_standardized': 0,
            'types_corrected': 0,
            'prices_normalized': 0,
            'thc_cbd_cleaned': 0,
            'ratios_standardized': 0,
            'validation_errors': 0,
            'validation_warnings': 0
        }

# Global instance for use throughout the application
smart_normalizer = SmartExcelNormalizer()
