"""
Fast Tag Generation Module
Optimizes label generation for speed using caching, batching, and parallel processing
"""

import logging
import time
import hashlib
import json
from io import BytesIO
import traceback
from typing import List, Dict, Any, Optional
from functools import lru_cache
from docx import Document

logger = logging.getLogger(__name__)

# Try to import cachetools, fall back to simple dict if not available
try:
    from cachetools import TTLCache
    _generation_cache = TTLCache(maxsize=100, ttl=300)  # 5-minute cache
    HAS_CACHETOOLS = True
except ImportError:
    logger.warning("cachetools not available, using simple dict cache (install with: pip install cachetools)")
    _generation_cache = {}  # Simple dict fallback
    HAS_CACHETOOLS = False

_template_buffer_cache = {}  # Persistent cache for template buffers
_cache_timestamps = {}  # Track cache entry times for manual TTL


class FastGenerationEngine:
    """
    High-performance label generation engine with caching and optimization
    """
    
    def __init__(self, template_processor):
        """
        Initialize fast generation engine
        
        Args:
            template_processor: The TemplateProcessor instance to use
        """
        self.template_processor = template_processor
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_cache_key(self, records: List[Dict], template_type: str, scale_factor: float) -> str:
        """Generate a cache key for the generation request"""
        # Create a deterministic but faster hash of the inputs by concatenating
        # only the minimal identifying fields per record. Avoid expensive
        # json.dumps on large lists.
        parts = []
        for r in records:
            name = str(r.get('Product Name*', r.get('ProductName', '')) or '')
            ptype = str(r.get('ProductType', '') or '')
            lineage = str(r.get('Lineage', '') or '')
            # CRITICAL: Include _group_key for preroll templates to ensure unique cache per product
            group_key = str(r.get('_group_key', '') or '') if template_type == 'preroll' else ''
            parts.append(f"{name}||{ptype}||{lineage}||{group_key}")
        parts.append(f"TEMPLATE||{template_type}")
        parts.append(f"SCALE||{scale_factor}")
        cache_str = '\n'.join(parts)
        return hashlib.md5(cache_str.encode('utf-8')).hexdigest()
    
    def generate_with_cache(
        self,
        records: List[Dict],
        template_type: str,
        scale_factor: float = 1.0
    ) -> Document:
        """
        Generate labels with caching support
        
        Args:
            records: List of product records
            template_type: Type of template ('horizontal', 'vertical', etc.)
            scale_factor: Scale factor for the template
        
        Returns:
            Generated Document
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(records, template_type, scale_factor)
        
        # Handle manual TTL for simple dict cache
        if not HAS_CACHETOOLS and cache_key in _generation_cache:
            cache_age = time.time() - _cache_timestamps.get(cache_key, 0)
            if cache_age > 300:  # 5 minute TTL
                logger.info(f"⚡ CACHE EXPIRED: Removing stale entry (age: {cache_age:.1f}s)")
                del _generation_cache[cache_key]
                del _cache_timestamps[cache_key]
        
        if cache_key in _generation_cache:
            self.cache_hits += 1
            logger.debug(f"⚡ CACHE HIT: Returning cached generation for {len(records)} records")
            # Return a copy of the cached document
            cached_bytes = _generation_cache[cache_key]
            return Document(BytesIO(cached_bytes))
        
        self.cache_misses += 1
        logger.debug(f"⚡ CACHE MISS: Generating labels for {len(records)} records")
        
        # Generate the document (wrap to capture internal errors and context)
        try:
            final_doc = self.template_processor.process_records(records)
        except Exception as e:
            logger.error(f"Exception in template_processor.process_records: {e}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to generate document: template processing failed: {e}")

        if final_doc is None:
            logger.error("❌ FastGenerationEngine: process_records returned None (no document generated)")
            try:
                tmpl_type = getattr(self.template_processor, 'template_type', 'UNKNOWN')
                expanded_buffer = getattr(self.template_processor, '_expanded_template_buffer', None)
                logger.error(f"TemplateProcessor state: template_type={tmpl_type}, has_expanded_buffer={expanded_buffer is not None}")
                sample_names = [r.get('ProductName', r.get('Product Name*', '')) for r in records[:5]]
                logger.error(f"Sample records: {sample_names}")
            except Exception:
                pass
            raise RuntimeError("Failed to generate document: no valid records or template error. See logs for details.")

        # Cache the result
        buffer = BytesIO()
        final_doc.save(buffer)
        buffer.seek(0)
        _generation_cache[cache_key] = buffer.getvalue()

        # Track timestamp for manual TTL
        if not HAS_CACHETOOLS:
            _cache_timestamps[cache_key] = time.time()
            # Clean up old entries if cache is too large
            if len(_generation_cache) > 100:
                self._cleanup_cache()

        generation_time = time.time() - start_time
        logger.debug(f"⚡ Generation completed in {generation_time:.2f}s (cache hit rate: {self._get_hit_rate():.1f}%)")

        # Return the document
        buffer.seek(0)
        return Document(buffer)
    
    def _cleanup_cache(self):
        """Clean up old cache entries when using simple dict"""
        if HAS_CACHETOOLS:
            return  # TTLCache handles this automatically
        
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in _cache_timestamps.items()
            if current_time - timestamp > 300
        ]
        
        for key in expired_keys:
            if key in _generation_cache:
                del _generation_cache[key]
            if key in _cache_timestamps:
                del _cache_timestamps[key]
        
        logger.info(f"⚡ Cache cleanup: Removed {len(expired_keys)} expired entries")
    
    def _get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100
    
    def clear_cache(self):
        """Clear the generation cache"""
        _generation_cache.clear()
        logger.info("⚡ Generation cache cleared")


class BatchedDatabaseQuerier:
    """
    Optimizes database queries by batching requests
    """
    
    def __init__(self, product_db):
        """
        Initialize batched querier
        
        Args:
            product_db: ProductDatabase instance
        """
        self.product_db = product_db
        self.query_count = 0
        self.batch_count = 0
    
    def get_products_batch(self, product_names: List[str], batch_size: int = 50) -> List[Dict]:
        """
        Get products in batches for better performance
        
        Args:
            product_names: List of product names to query
            batch_size: Number of products per batch
        
        Returns:
            List of product records
        """
        if not product_names:
            return []
        
        start_time = time.time()
        logger.info(f"⚡ Batched query: Fetching {len(product_names)} products in batches of {batch_size}")
        
        all_records = []
        
        # Split into batches
        for i in range(0, len(product_names), batch_size):
            batch = product_names[i:i + batch_size]
            
            # Query this batch
            try:
                records = self.product_db.get_products_by_names(batch)
                all_records.extend(records)
                self.batch_count += 1
            except Exception as e:
                logger.error(f"Error querying batch {i // batch_size + 1}: {e}")
        
        self.query_count += len(product_names)
        query_time = time.time() - start_time
        
        logger.info(f"⚡ Batched query completed: {len(all_records)} records in {query_time:.2f}s")
        logger.info(f"⚡ Query stats: {self.query_count} total products, {self.batch_count} batches")
        
        return all_records


class ProgressTracker:
    """
    Track and report generation progress
    """
    
    def __init__(self, total_items: int):
        """
        Initialize progress tracker
        
        Args:
            total_items: Total number of items to process
        """
        self.total_items = total_items
        self.completed_items = 0
        self.start_time = time.time()
        self.checkpoints = []
    
    def update(self, items_completed: int):
        """Update progress"""
        self.completed_items = items_completed
        progress_pct = (self.completed_items / self.total_items) * 100
        elapsed = time.time() - self.start_time
        
        # Estimate remaining time
        if self.completed_items > 0:
            items_per_second = self.completed_items / elapsed
            remaining_items = self.total_items - self.completed_items
            eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
            
            logger.info(f"⚡ Progress: {self.completed_items}/{self.total_items} ({progress_pct:.1f}%) - ETA: {eta_seconds:.1f}s")
        
        # Store checkpoint
        self.checkpoints.append({
            'time': elapsed,
            'completed': self.completed_items,
            'progress': progress_pct
        })
    
    def complete(self):
        """Mark as complete and log stats"""
        total_time = time.time() - self.start_time
        items_per_second = self.total_items / total_time if total_time > 0 else 0
        
        logger.info(f"⚡ Generation complete: {self.total_items} items in {total_time:.2f}s ({items_per_second:.1f} items/sec)")


def optimize_records_for_generation(records: List[Dict]) -> List[Dict]:
    """
    Optimize records before generation to reduce processing time
    
    Args:
        records: List of product records
    
    Returns:
        Optimized list of records
    """
    start_time = time.time()
    
    # Use local variables and comprehension for speed
    def _get(r, *keys, default=''):
        for k in keys:
            val = r.get(k)
            if val is not None and val != '':
                return val
        return default

    optimized = [
        {
            'Product Name*': _get(record, 'Product Name*', 'ProductName'),
            'ProductName': _get(record, 'Product Name*', 'ProductName'),
            'ProductType': _get(record, 'ProductType'),
            'Lineage': _get(record, 'Lineage', default='MIXED'),
            'ProductBrand': _get(record, 'ProductBrand', 'Product Brand'),
            'Product Brand': _get(record, 'Product Brand', 'ProductBrand'),
            'Vendor': _get(record, 'Vendor', 'Vendor/Supplier*'),
            'Product Strain': _get(record, 'Product Strain'),
            'ProductStrain': _get(record, 'ProductStrain', 'Product Strain'),
            'Price': _get(record, 'Price', 'Price*', 'Price* (Tier Name for Bulk)', 'Med Price'),
            'DOH': _get(record, 'DOH'),
            'DOH Compliant (Yes/No)': _get(record, 'DOH Compliant (Yes/No)'),
            'Weight*': _get(record, 'Weight*', default='1'),
            'Units': _get(record, 'Units', default='g'),
            'WeightUnits': _get(record, 'WeightUnits', 'CombinedWeight'),
            'CombinedWeight': _get(record, 'CombinedWeight'),
            'Description': _get(record, 'Description'),
            'DescAndWeight': _get(record, 'DescAndWeight'),
            'THC test result': _get(record, 'THC test result'),
            'CBD test result': _get(record, 'CBD test result'),
            'Test result unit (% or mg)': _get(record, 'Test result unit (% or mg)', default='%'),
            'Ratio': _get(record, 'Ratio'),
            'JointRatio': _get(record, 'JointRatio'),
            'Ratio_or_THC_CBD': _get(record, 'Ratio_or_THC_CBD'),
        }
        for record in records
    ]
    
    optimization_time = time.time() - start_time
    logger.info(f"⚡ Optimized {len(records)} records in {optimization_time:.3f}s")
    
    return optimized


# Global cache for template generation statistics
_generation_stats = {
    'total_generated': 0,
    'total_time': 0.0,
    'cache_hits': 0,
    'cache_misses': 0,
    'avg_time_per_label': 0.0
}


def get_generation_stats() -> Dict[str, Any]:
    """Get generation statistics"""
    return _generation_stats.copy()


def update_generation_stats(num_labels: int, generation_time: float, cache_hit: bool):
    """Update global generation statistics"""
    _generation_stats['total_generated'] += num_labels
    _generation_stats['total_time'] += generation_time
    
    if cache_hit:
        _generation_stats['cache_hits'] += 1
    else:
        _generation_stats['cache_misses'] += 1
    
    # Calculate average
    if _generation_stats['total_generated'] > 0:
        _generation_stats['avg_time_per_label'] = (
            _generation_stats['total_time'] / _generation_stats['total_generated']
        )


def clear_all_caches():
    """Clear all generation caches"""
    _generation_cache.clear()
    _template_buffer_cache.clear()
    logger.info("⚡ All generation caches cleared")

