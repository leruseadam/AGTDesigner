"""
Fast Tag Generation Module
Optimizes label generation for speed using caching, batching, and parallel processing
"""

import logging
import time
import hashlib
import json
from io import BytesIO
from typing import List, Dict, Any, Optional
from functools import lru_cache
from docx import Document

logger = logging.getLogger(__name__)

# Try to import cachetools, fall back to simple dict if not available
try:
    from cachetools import TTLCache
    # PERFORMANCE: Increased cache from 100 to 500 entries for better hit rate
    _generation_cache = TTLCache(maxsize=500, ttl=300)  # 5-minute cache
    HAS_CACHETOOLS = True
except ImportError:
    logger.warning("cachetools not available, using simple dict cache (install with: pip install cachetools)")
    _generation_cache = {}  # Simple dict fallback
    HAS_CACHETOOLS = False

# CRITICAL FIX: Clear cache on module load to remove documents with markers
# Cache version: increment this when cleanup logic changes to invalidate old cache
CACHE_VERSION = "v2.2"  # Updated when marker cleanup changes - force cache invalidation
logger.warning(f"🧹 CLEARING GENERATION CACHE (version {CACHE_VERSION}) - Removing old cached documents with markers")
_generation_cache.clear()

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
        # Create a deterministic hash of the inputs
        cache_data = {
            'records': [
                {
                    'name': r.get('Product Name*', r.get('ProductName', '')),
                    'type': r.get('ProductType', ''),
                    'lineage': r.get('Lineage', '')
                }
                for r in records
            ],
            'template': template_type,
            'scale': scale_factor,
            'cache_version': CACHE_VERSION  # Include cache version to invalidate old caches
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
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
            logger.warning(f"⚡⚡⚡ CACHE HIT PATH - RETURNING CACHED DOC FOR {len(records)} RECORDS ⚡⚡⚡")
            
            # Return a copy of the cached document
            cached_bytes = _generation_cache[cache_key]
            cached_doc = Document(BytesIO(cached_bytes))
            
            # CRITICAL: Clean markers from cached document too
            logger.warning("🧹🧹🧹 ABOUT TO CALL CLEANUP ON CACHED DOC")
            
            # DEBUG: Check for markers before cleanup - scan ALL cells
            marker_count = 0
            marker_samples = []
            cells_checked = 0
            
            # Check all tables, all rows, all cells - check BOTH cell.text AND paragraph.text
            import re
            for table_idx, table in enumerate(cached_doc.tables):
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        cells_checked += 1
                        
                        # Check cell.text (aggregated text)
                        cell_text = cell.text or ''
                        # Also check all paragraph texts individually (more reliable)
                        para_texts = []
                        for para in cell.paragraphs:
                            para_text = para.text or ''
                            para_texts.append(para_text)
                        # Combine all paragraph texts
                        all_text = cell_text + ' ' + ' '.join(para_texts)
                        text_upper = all_text.upper()
                        
                        if not text_upper.strip():
                            continue
                        
                        # Count all marker types
                        markers_found = []
                        if 'DESC_START' in text_upper or 'DESC_END' in text_upper:
                            count = text_upper.count('DESC_START') + text_upper.count('DESC_END')
                            marker_count += count
                            markers_found.append(f'DESC({count})')
                        
                        if 'PRICE_START' in text_upper or 'PRICE_END' in text_upper or 'PRICE_STARTS' in text_upper or 'RICE_END' in text_upper:
                            count = text_upper.count('PRICE_START') + text_upper.count('PRICE_END') + text_upper.count('PRICE_STARTS') + text_upper.count('RICE_END')
                            marker_count += count
                            markers_found.append(f'PRICE({count})')
                        
                        # Check for any _START or _END pattern
                        if re.search(r'\w+_(?:START|END)', text_upper):
                            count = len(re.findall(r'\w+_(?:START|END)', text_upper))
                            marker_count += count
                            markers_found.append(f'OTHER({count})')
                        
                        if markers_found and len(marker_samples) < 5:
                            marker_samples.append({
                                'table': table_idx,
                                'row': row_idx,
                                'cell': cell_idx,
                                'markers': markers_found,
                                'cell_text': cell_text[:100],
                                'para_texts': [p[:50] for p in para_texts[:2]]
                            })
            
            if marker_count > 0:
                logger.error(f"❌ FOUND {marker_count} MARKERS IN CACHED DOC BEFORE CLEANUP! Checked {cells_checked} cells. Samples: {marker_samples}")
            else:
                logger.debug(f"✅ No markers found in cached doc before cleanup (checked {cells_checked} cells)")
            
            try:
                self.template_processor._final_marker_cleanup(cached_doc)
                logger.warning("🧹 FIRST CLEANUP DONE")
                self.template_processor._nuclear_marker_cleanup(cached_doc)
                logger.warning("🧹 NUCLEAR CLEANUP DONE")
                self.template_processor._ultimate_marker_cleanup(cached_doc)
                logger.warning("🧹 ULTIMATE CLEANUP DONE")
                
                # DEBUG: Check for markers after cleanup - scan ALL cells
                marker_count_after = 0
                marker_samples_after = []
                cells_checked_after = 0
                import re
                
                for table_idx, table in enumerate(cached_doc.tables):
                    for row_idx, row in enumerate(table.rows):
                        for cell_idx, cell in enumerate(row.cells):
                            cells_checked_after += 1
                            
                            # Check cell.text AND paragraph.text
                            cell_text = cell.text or ''
                            para_texts = []
                            for para in cell.paragraphs:
                                para_texts.append(para.text or '')
                            all_text = cell_text + ' ' + ' '.join(para_texts)
                            text_upper = all_text.upper()
                            
                            if not text_upper.strip():
                                continue
                            
                            # Count all marker types
                            markers_found = []
                            if 'DESC_START' in text_upper or 'DESC_END' in text_upper:
                                count = text_upper.count('DESC_START') + text_upper.count('DESC_END')
                                marker_count_after += count
                                markers_found.append(f'DESC({count})')
                            
                            if 'PRICE_START' in text_upper or 'PRICE_END' in text_upper or 'PRICE_STARTS' in text_upper or 'RICE_END' in text_upper:
                                count = text_upper.count('PRICE_START') + text_upper.count('PRICE_END') + text_upper.count('PRICE_STARTS') + text_upper.count('RICE_END')
                                marker_count_after += count
                                markers_found.append(f'PRICE({count})')
                            
                            # Check for any _START or _END pattern
                            if re.search(r'\w+_(?:START|END)', text_upper):
                                count = len(re.findall(r'\w+_(?:START|END)', text_upper))
                                marker_count_after += count
                                markers_found.append(f'OTHER({count})')
                            
                            if markers_found and len(marker_samples_after) < 5:
                                marker_samples_after.append({
                                    'table': table_idx,
                                    'row': row_idx,
                                    'cell': cell_idx,
                                    'markers': markers_found,
                                    'cell_text': cell_text[:100],
                                    'para_texts': [p[:50] for p in para_texts[:2]]
                                })
                
                if marker_count_after > 0:
                    logger.error(f"❌❌❌ CLEANUP FAILED: {marker_count_after} markers still present after cleanup! Checked {cells_checked_after} cells. Samples: {marker_samples_after}")
                else:
                    logger.debug(f"✅ Cleanup successful: all markers removed (checked {cells_checked_after} cells)")
            except Exception as e:
                logger.error(f"❌❌❌ CLEANUP FAILED: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            logger.warning("⚡ RETURNING CACHED DOC AFTER CLEANUP")
            return cached_doc
        
        self.cache_misses += 1
        logger.warning(f"⚡⚡⚡ CACHE MISS PATH - GENERATING NEW DOC FOR {len(records)} RECORDS ⚡⚡⚡")
        
        # Generate the document
        final_doc = self.template_processor.process_records(records)
        if final_doc is None:
            logger.error("❌ FastGenerationEngine: process_records returned None (no document generated)")
            raise RuntimeError("Failed to generate document: no valid records or template error.")

        # CRITICAL: Remove markers before caching
        logger.warning("🧹 FastGenerationEngine: Calling marker cleanup before caching")
        self.template_processor._final_marker_cleanup(final_doc)
        self.template_processor._nuclear_marker_cleanup(final_doc)
        self.template_processor._ultimate_marker_cleanup(final_doc)
        logger.warning("🧹 FastGenerationEngine: All marker cleanup done")

        # Cache the result
        buffer = BytesIO()
        final_doc.save(buffer)
        buffer.seek(0)
        _generation_cache[cache_key] = buffer.getvalue()

        # Track timestamp for manual TTL
        if not HAS_CACHETOOLS:
            _cache_timestamps[cache_key] = time.time()
            # PERFORMANCE: Increased cache limit from 100 to 500 for better hit rate
            if len(_generation_cache) > 500:
                self._cleanup_cache()

        generation_time = time.time() - start_time
        logger.info(f"⚡ Generation completed in {generation_time:.2f}s (cache hit rate: {self._get_hit_rate():.1f}%)")

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
    
    optimized = []
    for record in records:
        # Create a minimal record with only required fields
        optimized_record = {
            'Product Name*': record.get('Product Name*', record.get('ProductName', '')),
            'ProductName': record.get('Product Name*', record.get('ProductName', '')),
            'ProductType': record.get('ProductType', ''),
            'Lineage': record.get('Lineage', 'MIXED'),
            'ProductBrand': record.get('ProductBrand', record.get('Product Brand', '')),
            'Product Brand': record.get('Product Brand', record.get('ProductBrand', '')),
            'Vendor': record.get('Vendor', record.get('Vendor/Supplier*', '')),
            'Product Strain': record.get('Product Strain', ''),
            'ProductStrain': record.get('ProductStrain', record.get('Product Strain', '')),
            'Price': record.get('Price', ''),
            'DOH': record.get('DOH', ''),
            'DOH Compliant (Yes/No)': record.get('DOH Compliant (Yes/No)', ''),
            'Weight*': record.get('Weight*', '1'),
            'Units': record.get('Units', 'g'),
            'WeightUnits': record.get('WeightUnits', record.get('CombinedWeight', '')),
            'CombinedWeight': record.get('CombinedWeight', ''),
            'Description': record.get('Description', ''),
            'DescAndWeight': record.get('DescAndWeight', ''),
            'THC test result': record.get('THC test result', ''),
            'CBD test result': record.get('CBD test result', ''),
            'Test result unit (% or mg)': record.get('Test result unit (% or mg)', '%'),
            'Ratio': record.get('Ratio', ''),
            'JointRatio': record.get('JointRatio', ''),
            'Ratio_or_THC_CBD': record.get('Ratio_or_THC_CBD', ''),
        }
        optimized.append(optimized_record)
    
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

