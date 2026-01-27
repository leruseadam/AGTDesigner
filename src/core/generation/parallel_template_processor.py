"""
Parallel Template Generation
Optimizes label generation using multiprocessing for faster throughput
"""

import logging
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable
from multiprocessing import cpu_count
import os
from io import BytesIO
from copy import deepcopy

logger = logging.getLogger(__name__)


class ParallelTemplateProcessor:
    """
    Processes templates in parallel for improved performance
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_threads: bool = False):
        """
        Initialize parallel processor
        
        Args:
            max_workers: Maximum number of workers (default: CPU count)
            use_threads: Use threads instead of processes (better for I/O bound tasks)
        """
        self.max_workers = max_workers or max(1, cpu_count() - 1)  # Leave one CPU free
        self.use_threads = use_threads
        self.total_processed = 0
        self.total_time = 0
    
    def process_in_parallel(
        self,
        items: List[Any],
        processor_func: Callable,
        chunk_size: int = 10,
        progress_callback: Optional[Callable] = None
    ) -> List[Any]:
        """
        Process items in parallel
        
        Args:
            items: List of items to process
            processor_func: Function to apply to each item/chunk
            chunk_size: Number of items per chunk
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of processed results
        """
        if not items:
            return []
        
        start_time = time.time()
        
        # Split items into chunks
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
        logger.info(f"Processing {len(items)} items in {len(chunks)} chunks using {self.max_workers} workers")
        
        results = []
        completed_items = 0
        
        # Choose executor based on configuration
        ExecutorClass = ThreadPoolExecutor if self.use_threads else ProcessPoolExecutor
        
        try:
            with ExecutorClass(max_workers=self.max_workers) as executor:
                # Submit all chunks
                future_to_chunk = {
                    executor.submit(processor_func, chunk): i 
                    for i, chunk in enumerate(chunks)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    
                    try:
                        result = future.result()
                        results.append((chunk_idx, result))
                        
                        # Update progress
                        completed_items += len(chunks[chunk_idx])
                        if progress_callback:
                            progress = (completed_items / len(items)) * 100
                            progress_callback(progress, completed_items, len(items))
                        
                    except Exception as e:
                        logger.error(f"Error processing chunk {chunk_idx}: {e}")
                        results.append((chunk_idx, None))
            
            # Sort results by original chunk order
            results.sort(key=lambda x: x[0])
            results = [r[1] for r in results if r[1] is not None]
            
            # Flatten results if they're lists
            if results and isinstance(results[0], list):
                results = [item for sublist in results for item in sublist]
            
            elapsed = time.time() - start_time
            self.total_processed += len(items)
            self.total_time += elapsed
            
            logger.info(f"Processed {len(items)} items in {elapsed:.2f}s ({len(items)/elapsed:.1f} items/sec)")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in parallel processing: {e}")
            raise
    
    def batch_process_templates(
        self,
        templates: List[Dict[str, Any]],
        generation_func: Callable,
        batch_size: int = 20
    ) -> List[Any]:
        """
        Process template generation in batches with optimal parallelization
        
        Args:
            templates: List of template data
            generation_func: Function that generates a template
            batch_size: Size of each batch
        
        Returns:
            List of generated templates
        """
        logger.info(f"Batch processing {len(templates)} templates with batch size {batch_size}")
        
        # For small numbers of templates, don't use parallelization
        if len(templates) < batch_size:
            logger.info("Small template count, using sequential processing")
            return [generation_func(t) for t in templates]
        
        # Use parallel processing for larger batches
        return self.process_in_parallel(
            templates,
            lambda batch: [generation_func(t) for t in batch],
            chunk_size=batch_size
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        avg_time = self.total_time / max(1, self.total_processed)
        
        return {
            'total_processed': self.total_processed,
            'total_time': round(self.total_time, 2),
            'avg_time_per_item': round(avg_time, 3),
            'items_per_second': round(1 / avg_time if avg_time > 0 else 0, 1),
            'max_workers': self.max_workers,
            'executor_type': 'threads' if self.use_threads else 'processes'
        }


class OptimizedDocxGenerator:
    """
    Optimized DOCX generation with parallel processing and caching
    """
    
    def __init__(self):
        self.parallel_processor = ParallelTemplateProcessor(use_threads=True)
        self.template_cache = {}
        self.generated_count = 0
    
    def generate_labels_batch(
        self,
        label_data: List[Dict[str, Any]],
        template_path: str,
        output_dir: str,
        parallel: bool = True
    ) -> List[str]:
        """
        Generate multiple labels efficiently
        
        Args:
            label_data: List of label data dictionaries
            template_path: Path to template file
            output_dir: Output directory for generated files
            parallel: Whether to use parallel processing
        
        Returns:
            List of generated file paths
        """
        start_time = time.time()
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Preload template bytes and a parsed base template to avoid reparsing per-label
        tpl_bytes = None
        base_doc = None
        try:
            with open(template_path, 'rb') as fh:
                tpl_bytes = fh.read()
            # Create a base DocxTemplate instance once and deepcopy it per-label
            try:
                from docxtpl import DocxTemplate
                base_doc = DocxTemplate(BytesIO(tpl_bytes))
            except Exception:
                base_doc = None
        except Exception as e:
            logger.warning(f"Could not preload template bytes: {e}")

        def generate_single_label(data: Dict[str, Any]) -> str:
            """Generate a single label"""
            try:
                # Generate output filename
                output_filename = f"label_{data.get('id', self.generated_count)}.docx"
                output_path = os.path.join(output_dir, output_filename)

                # Use a deepcopy of the parsed template when possible to avoid reparsing
                if base_doc is not None:
                    doc = deepcopy(base_doc)
                else:
                    from docxtpl import DocxTemplate
                    if tpl_bytes is not None:
                        doc = DocxTemplate(BytesIO(tpl_bytes))
                    else:
                        doc = DocxTemplate(template_path)

                # Render with data
                doc.render(data)

                # Save
                doc.save(output_path)

                self.generated_count += 1
                return output_path

            except Exception as e:
                logger.error(f"Error generating label: {e}")
                return None
        
        if parallel and len(label_data) > 10:
            results = self.parallel_processor.batch_process_templates(
                label_data,
                generate_single_label,
                batch_size=20
            )
        else:
            results = [generate_single_label(data) for data in label_data]
        
        # Filter out None results
        results = [r for r in results if r is not None]
        
        elapsed = time.time() - start_time
        logger.info(f"Generated {len(results)} labels in {elapsed:.2f}s ({len(results)/elapsed:.1f} labels/sec)")
        
        return results


def optimize_template_generation(
    label_data: List[Dict[str, Any]],
    template_processor: Any,
    use_parallel: bool = True,
    max_workers: Optional[int] = None
) -> Any:
    """
    Optimize template generation process
    
    Args:
        label_data: List of label data
        template_processor: Template processor instance
        use_parallel: Whether to use parallel processing
        max_workers: Maximum parallel workers
    
    Returns:
        Generated document or result
    """
    if not use_parallel or len(label_data) < 20:
        # For small batches, sequential is faster
        return template_processor.process_all(label_data)
    
    # Use parallel processing for large batches
    processor = ParallelTemplateProcessor(max_workers=max_workers, use_threads=True)
    
    # Split into chunks and process
    chunk_size = max(10, len(label_data) // (max_workers or 4))
    
    results = processor.process_in_parallel(
        label_data,
        lambda chunk: template_processor.process_chunk(chunk),
        chunk_size=chunk_size
    )
    
    # Combine results
    if hasattr(template_processor, 'combine_results'):
        return template_processor.combine_results(results)
    else:
        return results


class TemplateCache:
    """Cache for template objects to avoid repeated loading"""
    
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.cache = {}
        self.access_count = {}
    
    def get(self, template_path: str) -> Optional[Any]:
        """Get cached template"""
        if template_path in self.cache:
            self.access_count[template_path] += 1
            return self.cache[template_path]
        return None
    
    def set(self, template_path: str, template: Any):
        """Cache template"""
        # Evict least accessed if at max size
        if len(self.cache) >= self.max_size:
            least_accessed = min(self.access_count.keys(), key=lambda k: self.access_count[k])
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
        
        self.cache[template_path] = template
        self.access_count[template_path] = 0
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_count.clear()


# Global template cache
_template_cache = TemplateCache()


def get_cached_template(template_path: str, loader_func: Callable) -> Any:
    """
    Get template from cache or load it
    
    Args:
        template_path: Path to template
        loader_func: Function to load template if not cached
    
    Returns:
        Loaded template
    """
    cached = _template_cache.get(template_path)
    if cached is not None:
        return cached
    
    template = loader_func(template_path)
    _template_cache.set(template_path, template)
    
    return template

