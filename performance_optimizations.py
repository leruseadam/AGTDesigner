#!/usr/bin/env python3
"""
Performance optimization utilities for the Label Maker application.
"""

import os
import time
import logging
from functools import wraps
from typing import Dict, Any, Optional
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

# Global performance settings
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'max_workers': 4,
    'cache_ttl': 300,  # 5 minutes
    'request_timeout': 30,
    'upload_chunk_size': 8192,
    'max_file_size': 50 * 1024 * 1024,  # 50MB
}

# In-memory caches
_memory_cache = {}
_cache_timestamps = {}
_cache_lock = threading.Lock()

def get_cache_key(*args, **kwargs):
    """Generate a cache key from arguments."""
    key_parts = []
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif hasattr(arg, '__dict__'):
            key_parts.append(str(hash(str(arg.__dict__))))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    return "|".join(key_parts)

def cached(ttl=300):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not PERFORMANCE_CONFIG['enable_caching']:
                return func(*args, **kwargs)
            
            cache_key = get_cache_key(func.__name__, *args, **kwargs)
            current_time = time.time()
            
            with _cache_lock:
                # Check if cached result exists and is still valid
                if (cache_key in _memory_cache and 
                    cache_key in _cache_timestamps and
                    current_time - _cache_timestamps[cache_key] < ttl):
                    logging.debug(f"Cache hit for {func.__name__}")
                    return _memory_cache[cache_key]
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                _memory_cache[cache_key] = result
                _cache_timestamps[cache_key] = current_time
                
                # Clean up old cache entries
                _cleanup_cache(current_time)
                
                return result
        return wrapper
    return decorator

def _cleanup_cache(current_time):
    """Remove expired cache entries."""
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if current_time - timestamp > PERFORMANCE_CONFIG['cache_ttl']
    ]
    for key in expired_keys:
        _memory_cache.pop(key, None)
        _cache_timestamps.pop(key, None)

def clear_cache():
    """Clear all cached data."""
    with _cache_lock:
        _memory_cache.clear()
        _cache_timestamps.clear()
    logging.info("Performance cache cleared")

def performance_monitor(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 1.0:  # Log slow operations
                logging.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Error in {func.__name__} after {execution_time:.2f}s: {e}")
            raise
    return wrapper

class AsyncProcessor:
    """Handle background processing for better responsiveness."""
    
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.Queue()
        self.results = {}
        self.running = True
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
    
    def submit_task(self, task_id, func, *args, **kwargs):
        """Submit a task for background processing."""
        future = self.executor.submit(func, *args, **kwargs)
        self.results[task_id] = {
            'future': future,
            'status': 'running',
            'start_time': time.time()
        }
        return task_id
    
    def get_task_status(self, task_id):
        """Get the status of a background task."""
        if task_id not in self.results:
            return {'status': 'not_found'}
        
        task = self.results[task_id]
        future = task['future']
        
        if future.done():
            if future.exception():
                task['status'] = 'error'
                task['error'] = str(future.exception())
            else:
                task['status'] = 'completed'
                task['result'] = future.result()
            task['end_time'] = time.time()
            task['duration'] = task['end_time'] - task['start_time']
        
        return task
    
    def _worker(self):
        """Background worker thread."""
        while self.running:
            try:
                # Process any queued tasks
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error in background worker: {e}")
    
    def shutdown(self):
        """Shutdown the processor."""
        self.running = False
        self.executor.shutdown(wait=True)

# Global async processor instance
async_processor = AsyncProcessor(max_workers=PERFORMANCE_CONFIG['max_workers'])

def optimize_dataframe(df):
    """Optimize pandas DataFrame for better performance."""
    if df is None or df.empty:
        return df
    
    # Convert object columns to category if they have few unique values
    for col in df.columns:
        if df[col].dtype == 'object':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
    
    # Optimize numeric columns
    for col in df.select_dtypes(include=['int64']).columns:
        if df[col].min() >= 0:
            if df[col].max() < 255:
                df[col] = df[col].astype('uint8')
            elif df[col].max() < 65535:
                df[col] = df[col].astype('uint16')
            elif df[col].max() < 4294967295:
                df[col] = df[col].astype('uint32')
    
    return df

def get_memory_usage():
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0

def log_performance_stats():
    """Log current performance statistics."""
    memory_mb = get_memory_usage()
    cache_size = len(_memory_cache)
    
    logging.info(f"Performance Stats - Memory: {memory_mb:.1f}MB, Cache: {cache_size} entries")
    
    if memory_mb > 500:  # More than 500MB
        logging.warning(f"High memory usage: {memory_mb:.1f}MB")
        clear_cache()

# Initialize performance monitoring
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log_performance_stats()
