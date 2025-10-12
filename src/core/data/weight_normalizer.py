"""
Weight normalization module for Excel uploads.
Ensures consistent weight values and units across all product types.
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

class WeightNormalizer:
    """Normalizes product weights during Excel upload processing."""
    
    def __init__(self):
        self.normalization_rules = {
            # Constellation Moonshots - always 1.7oz
            'moonshot': {
                'pattern': r'.*moonshot.*',
                'weight': '1.7',
                'unit': 'oz',
                'case_sensitive': False
            },
            # Major beverages - 190g should be 6.7oz
            'major_beverages': {
                'pattern': r'^Major$',
                'weight': '6.7',
                'unit': 'oz',
                'condition': lambda row: self._is_major_beverage(row)
            },
            # Generic 190g conversion (non-concentrates)
            'generic_190g': {
                'pattern': r'.*',
                'weight': '6.7',
                'unit': 'oz',
                'condition': lambda row: self._is_190g_non_concentrate(row)
            },
            # Pre-roll packs - standardize pack weights
            'pre_roll_packs': {
                'pattern': r'.*pre-roll.*|.*preroll.*',
                'condition': lambda row: self._is_pre_roll_pack(row)
            },
            # Gummies - standardize weights
            'gummies': {
                'pattern': r'.*gumm.*|.*gummie.*',
                'condition': lambda row: self._is_gummy_product(row)
            },
            # Chocolate - standardize weights
            'chocolate': {
                'pattern': r'.*chocol.*',
                'condition': lambda row: self._is_chocolate_product(row)
            },
            # Capsules - should be in grams
            'capsules': {
                'pattern': r'.*capsul.*',
                'condition': lambda row: self._is_capsule_product(row)
            },
            # Tinctures - should be in oz
            'tinctures': {
                'pattern': r'.*tinctur.*',
                'condition': lambda row: self._is_tincture_product(row)
            },
            # Topical small oz weights - convert to grams
            'topical_small_oz': {
                'pattern': r'.*topical.*|.*cream.*|.*salve.*|.*bath.*',
                'condition': lambda row: self._is_small_oz_topical(row)
            }
        }
    
    def normalize_weight(self, product_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Normalize weight and units for a product based on rules.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Tuple of (normalized_weight, normalized_unit)
        """
        try:
            product_name = str(product_data.get('Product Name*', '')).strip()
            product_brand = str(product_data.get('Product Brand', '')).strip()
            product_type = str(product_data.get('Product Type*', '')).strip()
            current_weight = str(product_data.get('Weight*', '')).strip()
            current_unit = str(product_data.get('Units', '')).strip()
            
            # Skip if no weight data
            if not current_weight or current_weight.lower() in ['', 'nan', 'none']:
                return current_weight, current_unit
            
            # Rule 1: Constellation Moonshots - always 1.7oz
            if self._is_moonshot(product_name, product_brand):
                logger.info(f"Normalizing Moonshot: {product_name} -> 1.7oz")
                return '1.7', 'oz'
            
            # Rule 2: Major beverages - 190g -> 6.7oz
            if self._is_major_beverage(product_data):
                logger.info(f"Normalizing Major beverage: {product_name} -> 6.7oz")
                return '6.7', 'oz'
            
            # Rule 3: Generic 190g conversion (non-concentrates)
            if self._is_190g_non_concentrate(product_data):
                logger.info(f"Normalizing 190g product: {product_name} -> 6.7oz")
                return '6.7', 'oz'
            
            # Rule 4: Non-classic types should be in oz (except concentrates)
            if self._should_convert_to_oz(product_data):
                weight_oz = self._convert_grams_to_oz(current_weight, current_unit)
                if weight_oz is not None:
                    logger.info(f"Converting to oz: {product_name} {current_weight}{current_unit} -> {weight_oz}oz")
                    return str(weight_oz), 'oz'
            
            # Rule 5: Flower products should be in grams
            if self._should_be_in_grams(product_data):
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # Rule 6: Concentrates should stay in grams
            if self._is_concentrate(product_type) and current_unit.lower() == 'oz':
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting concentrate to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # Rule 7: Pre-roll packs - standardize pack weights
            if self._is_pre_roll_pack(product_data):
                normalized_weight, normalized_unit = self._normalize_pre_roll_pack(product_data)
                if normalized_weight != current_weight or normalized_unit != current_unit:
                    logger.info(f"Normalizing pre-roll pack: {product_name} {current_weight}{current_unit} -> {normalized_weight}{normalized_unit}")
                    return normalized_weight, normalized_unit
            
            # Rule 8: Gummies - standardize weights
            if self._is_gummy_product(product_data):
                normalized_weight, normalized_unit = self._normalize_gummy_weight(product_data)
                if normalized_weight != current_weight or normalized_unit != current_unit:
                    logger.info(f"Normalizing gummy weight: {product_name} {current_weight}{current_unit} -> {normalized_weight}{normalized_unit}")
                    return normalized_weight, normalized_unit
            
            # Rule 9: Chocolate - standardize weights
            if self._is_chocolate_product(product_data):
                normalized_weight, normalized_unit = self._normalize_chocolate_weight(product_data)
                if normalized_weight != current_weight or normalized_unit != current_unit:
                    logger.info(f"Normalizing chocolate weight: {product_name} {current_weight}{current_unit} -> {normalized_weight}{normalized_unit}")
                    return normalized_weight, normalized_unit
            
            # Rule 10: Capsules should be in grams
            if self._is_capsule_product(product_data):
                if current_unit.lower() == 'oz':
                    weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                    if weight_g is not None:
                        logger.info(f"Converting capsule to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                        return str(weight_g), 'g'
            
            # Rule 11: Tinctures should be in oz
            if self._is_tincture_product(product_data):
                if current_unit.lower() == 'g' and float(current_weight) > 10:
                    weight_oz = self._convert_grams_to_oz(current_weight, current_unit)
                    if weight_oz is not None:
                        logger.info(f"Converting tincture to oz: {product_name} {current_weight}{current_unit} -> {weight_oz}oz")
                        return str(weight_oz), 'oz'
            
            # Rule 12: Small oz topicals should be in grams
            if self._is_small_oz_topical(product_data):
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting small oz topical to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # No normalization needed
            return current_weight, current_unit
            
        except Exception as e:
            logger.error(f"Error normalizing weight for product {product_data.get('Product Name*', 'Unknown')}: {e}")
            return product_data.get('Weight*', ''), product_data.get('Units', '')
    
    def _is_moonshot(self, product_name: str, product_brand: str) -> bool:
        """Check if product is a Constellation Moonshot."""
        moonshot_pattern = r'.*moonshot.*'
        constellation_brand = r'.*constellation.*'
        
        return (re.search(moonshot_pattern, product_name, re.IGNORECASE) and 
                re.search(constellation_brand, product_brand, re.IGNORECASE))
    
    def _is_major_beverage(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a Major beverage with 190g weight."""
        brand = str(product_data.get('Product Brand', '')).strip()
        weight = str(product_data.get('Weight*', '')).strip()
        unit = str(product_data.get('Units', '')).strip()
        product_type = str(product_data.get('Product Type*', '')).strip()
        
        return (brand.lower() == 'major' and 
                weight in ['190', '190.0', '190g', '190.0g'] and 
                unit.lower() in ['g', 'gram', 'grams'] and
                'liquid' in product_type.lower())
    
    def _is_190g_non_concentrate(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is 190g and not a concentrate."""
        weight = str(product_data.get('Weight*', '')).strip()
        unit = str(product_data.get('Units', '')).strip()
        product_type = str(product_data.get('Product Type*', '')).strip()
        
        return (weight in ['190', '190.0', '190g', '190.0g'] and 
                unit.lower() in ['g', 'gram', 'grams'] and
                'concentrate' not in product_type.lower())
    
    def _should_convert_to_oz(self, product_data: Dict[str, Any]) -> bool:
        """Check if product should be converted to oz."""
        product_type = str(product_data.get('Product Type*', '')).strip()
        weight = str(product_data.get('Weight*', '')).strip()
        unit = str(product_data.get('Units', '')).strip()
        
        # Non-classic types that should be in oz
        non_classic_types = ['topical', 'edible (solid)', 'tincture', 'capsule']
        is_non_classic = any(nc_type in product_type.lower() for nc_type in non_classic_types)
        
        # Only convert if currently in grams and weight > 10g
        try:
            weight_val = float(weight)
            return (is_non_classic and 
                    unit.lower() in ['g', 'gram', 'grams'] and 
                    weight_val > 10)
        except ValueError:
            return False
    
    def _should_be_in_grams(self, product_data: Dict[str, Any]) -> bool:
        """Check if product should be in grams."""
        product_type = str(product_data.get('Product Type*', '')).strip()
        unit = str(product_data.get('Units', '')).strip()
        
        # Flower products should be in grams
        flower_types = ['flower', 'pre-roll', 'infused pre-roll']
        is_flower = any(ftype in product_type.lower() for ftype in flower_types)
        
        return is_flower and unit.lower() == 'oz'
    
    def _is_concentrate(self, product_type: str) -> bool:
        """Check if product is a concentrate."""
        concentrate_types = ['concentrate', 'wax', 'shatter', 'hash', 'rosin']
        return any(ctype in product_type.lower() for ctype in concentrate_types)
    
    def _convert_grams_to_oz(self, weight: str, unit: str) -> Optional[float]:
        """Convert grams to ounces."""
        try:
            if unit.lower() in ['g', 'gram', 'grams']:
                weight_val = float(weight)
                oz_val = round(weight_val / 28.3495, 2)
                return oz_val
        except ValueError:
            pass
        return None
    
    def _convert_oz_to_grams(self, weight: str, unit: str) -> Optional[float]:
        """Convert ounces to grams."""
        try:
            if unit.lower() in ['oz', 'ounce', 'ounces']:
                weight_val = float(weight)
                g_val = round(weight_val * 28.3495, 2)
                return g_val
        except ValueError:
            pass
        return None
    
    def _is_pre_roll_pack(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a pre-roll pack."""
        name = str(product_data.get('Product Name*', '')).lower()
        ptype = str(product_data.get('Product Type*', '')).lower()
        
        return ('pre-roll' in name or 'preroll' in name or 
                'pre-roll' in ptype or 'preroll' in ptype)
    
    def _normalize_pre_roll_pack(self, product_data: Dict[str, Any]) -> Tuple[str, str]:
        """Normalize pre-roll pack weights."""
        name = str(product_data.get('Product Name*', '')).lower()
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        try:
            weight_val = float(current_weight)
        except ValueError:
            return current_weight, current_unit
        
        # Pre-roll packs should show total weight in grams
        if current_unit.lower() == 'each':
            # Extract pack size from name
            if 'x 2' in name or '2 pack' in name:
                return '1.0', 'g'  # 0.5g x 2 = 1.0g total
            elif 'x 5' in name or '5 pack' in name:
                return '2.5', 'g'  # 0.5g x 5 = 2.5g total
            elif 'x 10' in name or '10 pack' in name:
                return '5.0', 'g'  # 0.5g x 10 = 5.0g total
            elif 'x 14' in name or '14 pack' in name:
                return '14.0', 'g'  # 1g x 14 = 14g total
            elif 'x 28' in name or '28 pack' in name:
                return '28.0', 'g'  # 1g x 28 = 28g total
        
        # If already in grams, keep as is
        return current_weight, 'g'
    
    def _is_gummy_product(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a gummy."""
        name = str(product_data.get('Product Name*', '')).lower()
        ptype = str(product_data.get('Product Type*', '')).lower()
        
        return ('gumm' in name or 'gummie' in name)
    
    def _normalize_gummy_weight(self, product_data: Dict[str, Any]) -> Tuple[str, str]:
        """Normalize gummy weights."""
        name = str(product_data.get('Product Name*', '')).lower()
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        try:
            weight_val = float(current_weight)
        except ValueError:
            return current_weight, current_unit
        
        # Most gummies should be in oz, but small ones in grams
        if current_unit.lower() == 'g':
            # Small gummies in grams are fine
            if weight_val <= 5.0:
                return current_weight, 'g'
            # Large gummies should be in oz
            else:
                weight_oz = self._convert_grams_to_oz(current_weight, current_unit)
                return str(weight_oz), 'oz'
        elif current_unit.lower() == 'oz':
            # Small oz weights should be grams
            if weight_val < 0.1:
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                return str(weight_g), 'g'
        
        return current_weight, current_unit
    
    def _is_chocolate_product(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is chocolate."""
        name = str(product_data.get('Product Name*', '')).lower()
        
        return 'chocol' in name
    
    def _normalize_chocolate_weight(self, product_data: Dict[str, Any]) -> Tuple[str, str]:
        """Normalize chocolate weights."""
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        try:
            weight_val = float(current_weight)
        except ValueError:
            return current_weight, current_unit
        
        # Chocolate products should be in grams for small amounts, oz for large
        if current_unit.lower() == 'oz':
            if weight_val < 0.5:  # Small oz amounts
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                return str(weight_g), 'g'
        elif current_unit.lower() == 'g':
            if weight_val > 50:  # Large gram amounts
                weight_oz = self._convert_grams_to_oz(current_weight, current_unit)
                return str(weight_oz), 'oz'
        
        return current_weight, current_unit
    
    def _is_capsule_product(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a capsule."""
        ptype = str(product_data.get('Product Type*', '')).lower()
        name = str(product_data.get('Product Name*', '')).lower()
        
        return ('capsul' in ptype or 'capsul' in name)
    
    def _is_tincture_product(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a tincture."""
        ptype = str(product_data.get('Product Type*', '')).lower()
        name = str(product_data.get('Product Name*', '')).lower()
        
        return ('tinctur' in ptype or 'tinctur' in name)
    
    def _is_small_oz_topical(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a topical with small oz weight."""
        ptype = str(product_data.get('Product Type*', '')).lower()
        name = str(product_data.get('Product Name*', '')).lower()
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        # Check if it's a topical type
        topical_types = ['topical', 'cream', 'salve', 'bath']
        is_topical = any(ttype in ptype for ttype in topical_types) or any(ttype in name for ttype in topical_types)
        
        if not is_topical:
            return False
        
        try:
            weight_val = float(current_weight)
            return (current_unit.lower() == 'oz' and weight_val < 0.1)
        except ValueError:
            return False
    
    def normalize_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all weight-related fields in product data.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Dictionary with normalized weight fields
        """
        try:
            # Create a copy to avoid modifying the original
            normalized_data = product_data.copy()
            
            # Normalize weight and units
            normalized_weight, normalized_unit = self.normalize_weight(product_data)
            
            # Update the data
            normalized_data['Weight*'] = normalized_weight
            normalized_data['Units'] = normalized_unit
            
            # Add normalization timestamp
            from datetime import datetime
            normalized_data['weight_normalized_at'] = datetime.now().isoformat()
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing product data: {e}")
            return product_data

# Global instance for use throughout the application
weight_normalizer = WeightNormalizer()
