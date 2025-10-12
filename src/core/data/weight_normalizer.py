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
            
            # Rule 7: Vape Cartridges should be in grams (non-classic)
            if self._is_vape_cartridge(product_type) and current_unit.lower() == 'oz':
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting vape cartridge to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # Rule 8: Small oz topicals should be in grams
            if self._is_small_oz_topical(product_data):
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting small oz topical to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # Rule 9: Capsules should be in grams (non-classic)
            if self._is_capsule(product_type) and current_unit.lower() == 'oz':
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting capsule to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
                    return str(weight_g), 'g'
            
            # Rule 10: Paraphernalia with "each" units should be standardized
            if self._is_paraphernalia(product_type) and current_unit.lower() == 'each':
                # Keep as "each" but standardize weight
                if current_weight in ['0', '0.0', '0.00']:
                    return '1', 'each'
            
            # Rule 11: Edible Solids with mixed units - convert large grams to oz
            if self._is_edible_solid(product_type) and self._should_edible_solid_be_oz(product_data):
                weight_oz = self._convert_grams_to_oz(current_weight, current_unit)
                if weight_oz is not None:
                    logger.info(f"Converting edible solid to oz: {product_name} {current_weight}{current_unit} -> {weight_oz}oz")
                    return str(weight_oz), 'oz'
            
            # Rule 12: Pre-rolls and Infused Pre-rolls should be in grams
            if self._is_pre_roll(product_type) and current_unit.lower() == 'oz':
                weight_g = self._convert_oz_to_grams(current_weight, current_unit)
                if weight_g is not None:
                    logger.info(f"Converting pre-roll to grams: {product_name} {current_weight}{current_unit} -> {weight_g}g")
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
        
        # Classic types that should be in oz (Edible Liquid)
        classic_oz_types = ['edible (liquid)']
        is_classic_oz = any(ct in product_type.lower() for ct in classic_oz_types)
        
        # Non-classic types that should be in oz (Topicals, Tinctures)
        non_classic_oz_types = ['topical', 'tincture']
        is_non_classic_oz = any(nc_type in product_type.lower() for nc_type in non_classic_oz_types)
        
        # Only convert if currently in grams and weight > 10g
        try:
            weight_val = float(weight)
            return ((is_classic_oz or is_non_classic_oz) and 
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
        concentrate_types = ['concentrate', 'wax', 'shatter', 'hash', 'rosin', 'solventless concentrate']
        return any(ctype in product_type.lower() for ctype in concentrate_types)
    
    def _is_vape_cartridge(self, product_type: str) -> bool:
        """Check if product is a vape cartridge (non-classic)."""
        return 'vape cartridge' in product_type.lower()
    
    def _is_capsule(self, product_type: str) -> bool:
        """Check if product is a capsule (non-classic)."""
        return 'capsule' in product_type.lower()
    
    def _is_paraphernalia(self, product_type: str) -> bool:
        """Check if product is paraphernalia (non-classic)."""
        return 'paraphernalia' in product_type.lower()
    
    def _is_edible_solid(self, product_type: str) -> bool:
        """Check if product is an edible solid (classic)."""
        return 'edible (solid)' in product_type.lower()
    
    def _is_pre_roll(self, product_type: str) -> bool:
        """Check if product is a pre-roll (classic)."""
        return 'pre-roll' in product_type.lower() or 'infused pre-roll' in product_type.lower()
    
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
    
    def _is_small_oz_topical(self, product_data: Dict[str, Any]) -> bool:
        """Check if product is a topical with small oz weight that should be grams."""
        product_type = str(product_data.get('Product Type*', '')).strip()
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        # Check if it's a topical
        if 'topical' not in product_type.lower():
            return False
        
        try:
            weight_val = float(current_weight)
            # Small oz weights (< 0.1oz) should be in grams
            return (current_unit.lower() == 'oz' and weight_val < 0.1)
        except ValueError:
            return False
    
    def _should_edible_solid_be_oz(self, product_data: Dict[str, Any]) -> bool:
        """Check if edible solid should be converted to oz."""
        current_weight = str(product_data.get('Weight*', '')).strip()
        current_unit = str(product_data.get('Units', '')).strip()
        
        try:
            weight_val = float(current_weight)
            # Convert edible solids from grams to oz if weight > 20g
            return (current_unit.lower() in ['g', 'gram', 'grams'] and weight_val > 20)
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
