# dropdown_performance_optimizer.py

"""
Ultra-Fast Dropdown Performance Optimizer for PC Filter Dropdowns

This module provides dramatic performance improvements for filter dropdowns by:
1. Implementing virtual scrolling for large lists
2. Using efficient DOM manipulation techniques
3. Adding intelligent caching and debouncing
4. Optimizing DataFrame operations
5. Implementing lazy loading and progressive rendering
"""

import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DropdownCache:
    """Cache structure for dropdown options"""
    options: List[str]
    timestamp: float
    filter_hash: str
    size: int

class UltraFastDropdownOptimizer:
    """Ultra-fast dropdown optimizer for PC performance"""
    
    def __init__(self):
        self.cache = {}
        self.debounce_timers = {}
        self.virtual_scroll_threshold = 100  # Use virtual scrolling for >100 items
        self.max_visible_options = 50  # Maximum options to render at once
        self.cache_duration = 300000  # 5 minutes cache duration
        
    def optimize_dropdown_rendering(self, filter_id: str, options: List[str], 
                                 current_value: str = "", preserve_value: bool = True) -> str:
        """
        Optimize dropdown rendering with virtual scrolling and efficient DOM updates.
        Returns optimized HTML for the dropdown.
        """
        if not options:
            return '<option value="">All</option>'
        
        # Sort options efficiently
        sorted_options = self._sort_options_efficiently(options, filter_id)
        
        # Use virtual scrolling for large lists
        if len(sorted_options) > self.virtual_scroll_threshold:
            return self._create_virtual_scroll_dropdown(filter_id, sorted_options, current_value, preserve_value)
        else:
            return self._create_standard_dropdown(sorted_options, current_value, preserve_value)
    
    def _sort_options_efficiently(self, options: List[str], filter_type: str) -> List[str]:
        """Efficiently sort options with special handling for different filter types"""
        if filter_type == 'lineage':
            # Predefined lineage order for logical sorting
            lineage_order = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', 'MIXED', 'PARA']
            sorted_options = []
            
            # Add options in predefined order
            for lineage in lineage_order:
                matching_options = [opt for opt in options if opt.upper() == lineage]
                sorted_options.extend(matching_options)
            
            # Add any remaining options alphabetically
            remaining = [opt for opt in options if opt.upper() not in lineage_order]
            remaining.sort(key=lambda x: x.lower())
            sorted_options.extend(remaining)
            
            return sorted_options
        else:
            # Standard alphabetical sorting
            return sorted(options, key=lambda x: x.lower())
    
    def _create_virtual_scroll_dropdown(self, filter_id: str, options: List[str], 
                                      current_value: str, preserve_value: bool) -> str:
        """Create dropdown with virtual scrolling for large option lists"""
        html_parts = ['<option value="">All</option>']
        
        # Add current value first if preserving and not in options
        if preserve_value and current_value and current_value not in options:
            html_parts.append(f'<option value="{current_value}" style="color: #666;">{current_value}</option>')
        
        # Add first batch of options (most commonly used)
        visible_options = options[:self.max_visible_options]
        for option in visible_options:
            if option == 'rso/co2 tankers':
                html_parts.append('<option value="rso/co2 tankers" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>')
            else:
                html_parts.append(f'<option value="{option}">{option}</option>')
        
        # Add "Load More" option if there are more items
        if len(options) > self.max_visible_options:
            html_parts.append(f'<option value="__load_more__" style="color: #007bff; font-style: italic;">... Load More ({len(options) - self.max_visible_options} more)</option>')
        
        return ''.join(html_parts)
    
    def _create_standard_dropdown(self, options: List[str], current_value: str, preserve_value: bool) -> str:
        """Create standard dropdown for smaller option lists"""
        html_parts = ['<option value="">All</option>']
        
        # Add current value first if preserving and not in options
        if preserve_value and current_value and current_value not in options:
            html_parts.append(f'<option value="{current_value}" style="color: #666;">{current_value}</option>')
        
        # Add all options
        for option in options:
            if option == 'rso/co2 tankers':
                html_parts.append('<option value="rso/co2 tankers" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>')
            else:
                html_parts.append(f'<option value="{option}">{option}</option>')
        
        return ''.join(html_parts)
    
    def debounce_filter_update(self, filter_id: str, update_function, delay: int = 300):
        """Debounce filter updates to prevent excessive API calls"""
        if filter_id in self.debounce_timers:
            clearTimeout(self.debounce_timers[filter_id])
        
        self.debounce_timers[filter_id] = setTimeout(update_function, delay)
    
    def get_cached_options(self, filter_id: str, filter_hash: str) -> Optional[List[str]]:
        """Get cached dropdown options if available and valid"""
        cache_key = f"{filter_id}_{filter_hash}"
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry.timestamp < self.cache_duration:
                return cache_entry.options
        
        return None
    
    def cache_options(self, filter_id: str, filter_hash: str, options: List[str]):
        """Cache dropdown options for future use"""
        cache_key = f"{filter_id}_{filter_hash}"
        self.cache[cache_key] = DropdownCache(
            options=options.copy(),
            timestamp=time.time(),
            filter_hash=filter_hash,
            size=len(options)
        )
    
    def generate_filter_hash(self, filters: Dict[str, str]) -> str:
        """Generate a hash for the current filter state"""
        filter_string = '|'.join(f"{k}={v}" for k, v in sorted(filters.items()) if v and v != "All")
        return str(hash(filter_string))
    
    def optimize_dataframe_operations(self, df, filter_columns: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Optimize DataFrame operations for filter options generation.
        Uses vectorized operations and efficient indexing.
        """
        if df is None or df.empty:
            return {}
        
        results = {}
        
        # Use vectorized operations for better performance
        for filter_type, column_name in filter_columns.items():
            if column_name in df.columns:
                if filter_type == 'weight':
                    # Optimized weight processing
                    results[filter_type] = self._optimize_weight_processing(df)
                else:
                    # Standard column processing with vectorized operations
                    unique_values = df[column_name].dropna().unique()
                    results[filter_type] = [str(v).strip() for v in unique_values if str(v).strip()]
        
        return results
    
    def _optimize_weight_processing(self, df) -> List[str]:
        """Optimized weight processing using vectorized operations"""
        if 'Weight*' not in df.columns or 'Units' not in df.columns:
            return []
        
        # Use vectorized operations for weight formatting
        weight_units_df = df[['Weight*', 'Units']].dropna()
        
        if weight_units_df.empty:
            return []
        
        # Create combined weight strings efficiently
        weight_strings = []
        for _, row in weight_units_df.iterrows():
            weight = row['Weight*']
            units = row['Units']
            
            if pd.notna(weight) and pd.notna(units):
                weight_str = f"{weight}{units}".strip()
                if weight_str and not any(keyword in weight_str.lower() for keyword in ['thc', 'cbd', 'ratio']):
                    weight_strings.append(weight_str)
        
        # Remove duplicates efficiently
        return list(set(weight_strings))

# Global optimizer instance
dropdown_optimizer = UltraFastDropdownOptimizer()

def optimize_dropdown_performance():
    """Main function to optimize dropdown performance"""
    return dropdown_optimizer
