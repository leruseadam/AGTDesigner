"""
Excel data validation module.
Validates data quality and consistency during Excel processing.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class ExcelDataValidator:
    """Validates Excel data quality and consistency."""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.validation_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'validation_errors': []
        }
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate product data against all rules.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Run all validation rules
            errors.extend(self._validate_required_fields(product_data))
            errors.extend(self._validate_product_name(product_data))
            errors.extend(self._validate_weight_and_units(product_data))
            errors.extend(self._validate_price(product_data))
            errors.extend(self._validate_thc_cbd_content(product_data))
            errors.extend(self._validate_barcode(product_data))
            errors.extend(self._validate_brand(product_data))
            errors.extend(self._validate_product_type(product_data))
            errors.extend(self._validate_vendor(product_data))
            errors.extend(self._validate_cross_field_consistency(product_data))
            
            # Update validation stats
            self.validation_stats['total_validations'] += 1
            if not errors:
                self.validation_stats['passed_validations'] += 1
            else:
                self.validation_stats['failed_validations'] += 1
                self.validation_stats['validation_errors'].extend(errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules."""
        return {
            'required_fields': [
                'Product Name*', 'Product Type*', 'Product Brand'
            ],
            'weight_ranges': {
                'flower': (0.1, 100),  # grams
                'pre-roll': (0.1, 10),  # grams
                'concentrate': (0.1, 5),  # grams
                'edible (solid)': (1, 1000),  # grams or oz
                'edible (liquid)': (1, 1000),  # ml or oz
                'topical': (1, 500),  # grams or oz
                'tincture': (1, 100),  # ml or oz
                'capsule': (1, 100),  # count or grams
                'vape cartridge': (0.3, 2),  # grams
            },
            'price_range': (0, 1000),  # dollars
            'thc_range': (0, 100),  # percentage
            'cbd_range': (0, 100),  # percentage
            'barcode_patterns': [
                r'^\d{8,14}$',  # Standard barcode lengths
                r'^[A-Z0-9]{6,12}$'  # Alphanumeric codes
            ]
        }
    
    def _validate_required_fields(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate that required fields are present and not empty."""
        errors = []
        
        for field in self.validation_rules['required_fields']:
            value = product_data.get(field, '')
            if not value or str(value).strip().lower() in ['', 'nan', 'none', 'null']:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_product_name(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate product name format and content."""
        errors = []
        product_name = str(product_data.get('Product Name*', '')).strip()
        
        if not product_name:
            return errors
        
        # Check for minimum length
        if len(product_name) < 3:
            errors.append("Product name too short (minimum 3 characters)")
        
        # Check for maximum length
        if len(product_name) > 200:
            errors.append("Product name too long (maximum 200 characters)")
        
        # Check for invalid characters
        invalid_chars = re.findall(r'[<>"\'\`]', product_name)
        if invalid_chars:
            errors.append(f"Product name contains invalid characters: {invalid_chars}")
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', product_name):
            errors.append("Product name contains excessive whitespace")
        
        return errors
    
    def _validate_weight_and_units(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate weight and units consistency."""
        errors = []
        
        weight = product_data.get('Weight*', '')
        units = product_data.get('Units', '')
        product_type = str(product_data.get('Product Type*', '')).lower()
        
        if not weight or str(weight).strip().lower() in ['', 'nan', 'none', 'null']:
            return errors
        
        try:
            weight_val = float(str(weight))
        except ValueError:
            errors.append(f"Invalid weight value: {weight}")
            return errors
        
        # Check weight ranges by product type
        if product_type in self.validation_rules['weight_ranges']:
            min_weight, max_weight = self.validation_rules['weight_ranges'][product_type]
            
            # Convert to grams for comparison if needed
            if str(units).lower() in ['oz', 'ounce', 'ounces']:
                weight_in_grams = weight_val * 28.3495
            else:
                weight_in_grams = weight_val
            
            if weight_in_grams < min_weight:
                errors.append(f"Weight too low for {product_type}: {weight_val}{units}")
            elif weight_in_grams > max_weight:
                errors.append(f"Weight too high for {product_type}: {weight_val}{units}")
        
        # Validate units
        valid_units = ['g', 'gram', 'grams', 'gm', 'oz', 'ounce', 'ounces', 'ml', 'each', 'count']
        if units and str(units).lower() not in valid_units:
            errors.append(f"Invalid unit: {units}")
        
        return errors
    
    def _validate_price(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate price format and range."""
        errors = []
        
        price_fields = ['Price*', 'Price']
        price_value = None
        
        for field in price_fields:
            if field in product_data:
                price_value = product_data[field]
                break
        
        if not price_value or str(price_value).strip().lower() in ['', 'nan', 'none', 'null']:
            return errors
        
        try:
            # Clean price value
            price_str = re.sub(r'[^\d.,]', '', str(price_value))
            price_float = float(price_str)
            
            min_price, max_price = self.validation_rules['price_range']
            if price_float < min_price:
                errors.append(f"Price too low: ${price_float}")
            elif price_float > max_price:
                errors.append(f"Price too high: ${price_float}")
                
        except ValueError:
            errors.append(f"Invalid price format: {price_value}")
        
        return errors
    
    def _validate_thc_cbd_content(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate THC and CBD content values."""
        errors = []
        
        # Validate THC content
        thc_fields = ['THC test result', 'THC Content', 'THC', 'THCA']
        for field in thc_fields:
            if field in product_data:
                thc_value = product_data[field]
                if thc_value and str(thc_value).strip().lower() not in ['', 'nan', 'none', 'null']:
                    try:
                        thc_float = float(str(thc_value))
                        min_thc, max_thc = self.validation_rules['thc_range']
                        if thc_float < min_thc or thc_float > max_thc:
                            errors.append(f"THC content out of range: {thc_value}%")
                    except ValueError:
                        errors.append(f"Invalid THC content format: {thc_value}")
        
        # Validate CBD content
        cbd_fields = ['CBD test result', 'CBD Content', 'CBD', 'CBDA']
        for field in cbd_fields:
            if field in product_data:
                cbd_value = product_data[field]
                if cbd_value and str(cbd_value).strip().lower() not in ['', 'nan', 'none', 'null']:
                    try:
                        cbd_float = float(str(cbd_value))
                        min_cbd, max_cbd = self.validation_rules['cbd_range']
                        if cbd_float < min_cbd or cbd_float > max_cbd:
                            errors.append(f"CBD content out of range: {cbd_value}%")
                    except ValueError:
                        errors.append(f"Invalid CBD content format: {cbd_value}")
        
        return errors
    
    def _validate_barcode(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate barcode format."""
        errors = []
        
        barcode = product_data.get('Barcode*', '')
        if not barcode or str(barcode).strip().lower() in ['', 'nan', 'none', 'null']:
            return errors
        
        barcode_str = str(barcode).strip()
        
        # Check against valid patterns
        valid_pattern = False
        for pattern in self.validation_rules['barcode_patterns']:
            if re.match(pattern, barcode_str):
                valid_pattern = True
                break
        
        if not valid_pattern:
            errors.append(f"Invalid barcode format: {barcode}")
        
        return errors
    
    def _validate_brand(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate brand name."""
        errors = []
        
        brand = str(product_data.get('Product Brand', '')).strip()
        if not brand:
            return errors
        
        # Check for minimum length
        if len(brand) < 2:
            errors.append("Brand name too short (minimum 2 characters)")
        
        # Check for maximum length
        if len(brand) > 100:
            errors.append("Brand name too long (maximum 100 characters)")
        
        # Check for invalid characters
        invalid_chars = re.findall(r'[<>"\'\`]', brand)
        if invalid_chars:
            errors.append(f"Brand name contains invalid characters: {invalid_chars}")
        
        return errors
    
    def _validate_product_type(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate product type."""
        errors = []
        
        product_type = str(product_data.get('Product Type*', '')).strip()
        if not product_type:
            return errors
        
        # Check against known product types
        from src.core.constants import CLASSIC_TYPES
        
        # All known product types (classic + common non-classic)
        known_types = list(CLASSIC_TYPES) + [
            'edible (solid)', 'edible (liquid)', 'topical', 'tincture', 
            'capsule', 'suppository', 'transdermal', 'beverage', 'powder',
            'paraphernalia', 'accessory', 'equipment'
        ]
        
        if product_type.lower() not in [t.lower() for t in known_types]:
            errors.append(f"Unknown product type: {product_type}")
        
        return errors
    
    def _validate_vendor(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate vendor/supplier information."""
        errors = []
        
        vendor_fields = ['Vendor/Supplier*', 'Vendor/Supplier', 'Vendor']
        vendor_value = None
        
        for field in vendor_fields:
            if field in product_data and product_data[field]:
                vendor_value = product_data[field]
                break
        
        if vendor_value:
            vendor_str = str(vendor_value).strip()
            
            # Check for minimum length
            if len(vendor_str) < 2:
                errors.append("Vendor name too short (minimum 2 characters)")
            
            # Check for maximum length
            if len(vendor_str) > 100:
                errors.append("Vendor name too long (maximum 100 characters)")
        
        return errors
    
    def _validate_cross_field_consistency(self, product_data: Dict[str, Any]) -> List[str]:
        """Validate consistency between related fields."""
        errors = []
        
        # Check weight vs product type consistency
        weight = product_data.get('Weight*', '')
        units = product_data.get('Units', '')
        product_type = str(product_data.get('Product Type*', '')).lower()
        
        if weight and units and product_type:
            try:
                weight_val = float(str(weight))
                
                # Concentrates should typically be in grams and small amounts
                if 'concentrate' in product_type:
                    if str(units).lower() in ['oz', 'ounce', 'ounces'] and weight_val > 2:
                        errors.append("Concentrate weight seems high for ounces")
                    elif str(units).lower() in ['g', 'gram', 'grams'] and weight_val > 5:
                        errors.append("Concentrate weight seems high for grams")
                
                # Flower should typically be in grams
                if 'flower' in product_type and str(units).lower() in ['oz', 'ounce', 'ounces']:
                    if weight_val > 1:
                        errors.append("Flower weight in ounces seems high")
                
                # Edibles should have reasonable weights
                if 'edible' in product_type:
                    if str(units).lower() in ['g', 'gram', 'grams'] and weight_val > 500:
                        errors.append("Edible weight in grams seems very high")
                    elif str(units).lower() in ['oz', 'ounce', 'ounces'] and weight_val > 20:
                        errors.append("Edible weight in ounces seems very high")
                        
            except ValueError:
                pass  # Weight validation already caught this
        
        return errors
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        stats = self.validation_stats.copy()
        
        if stats['total_validations'] > 0:
            stats['pass_rate'] = (stats['passed_validations'] / stats['total_validations']) * 100
            stats['fail_rate'] = (stats['failed_validations'] / stats['total_validations']) * 100
        else:
            stats['pass_rate'] = 0
            stats['fail_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.validation_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'validation_errors': []
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        stats = self.get_validation_stats()
        
        # Categorize validation errors
        error_categories = {}
        for error in self.validation_stats['validation_errors']:
            category = error.split(':')[0] if ':' in error else 'General'
            error_categories[category] = error_categories.get(category, 0) + 1
        
        return {
            'summary': stats,
            'error_categories': error_categories,
            'top_errors': self._get_top_errors(),
            'recommendations': self._generate_validation_recommendations()
        }
    
    def _get_top_errors(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most common validation errors."""
        error_counts = {}
        for error in self.validation_stats['validation_errors']:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def _generate_validation_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        stats = self.get_validation_stats()
        
        if stats['fail_rate'] > 20:
            recommendations.append("High validation failure rate. Review data quality in source Excel files.")
        
        if stats['fail_rate'] > 50:
            recommendations.append("Very high validation failure rate. Consider data cleaning before import.")
        
        # Check for common error patterns
        error_categories = {}
        for error in self.validation_stats['validation_errors']:
            category = error.split(':')[0] if ':' in error else 'General'
            error_categories[category] = error_categories.get(category, 0) + 1
        
        if error_categories.get('Missing required field', 0) > 0:
            recommendations.append("Missing required fields detected. Ensure all required columns are present.")
        
        if error_categories.get('Invalid weight', 0) > 0:
            recommendations.append("Invalid weight values detected. Review weight and unit formatting.")
        
        if error_categories.get('Invalid price', 0) > 0:
            recommendations.append("Invalid price values detected. Use consistent price formatting.")
        
        return recommendations

# Global instance for use throughout the application
excel_data_validator = ExcelDataValidator()
