"""
High-performance caching system for the application.
Implements in-memory caching with TTL, LRU eviction, and thread safety.
"""

import time
import threading
import hashlib
import json
import logging
from typing import Any, Dict, Optional, Callable, Union
from collections import OrderedDict
from functools import wraps
import weakref

logger = logging.getLogger(__name__)

class HighPerformanceCache:
    """High-performance in-memory cache with TTL and LRU eviction."""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._timestamps = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                # Check if expired
                if self._is_expired(key):
                    self._remove_key(key)
                    self._misses += 1
                    return None
                
                # Move to end (LRU)
                value = self._cache.pop(key)
                self._cache[key] = value
                self._hits += 1
                return value
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        with self._lock:
            ttl = ttl or self.default_ttl
            expire_time = time.time() + ttl
            
            # Remove if exists
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
            
            # Add new entry
            self._cache[key] = value
            self._timestamps[key] = expire_time
            
            # Evict if over limit
            while len(self._cache) > self.max_size:
                oldest_key, _ = self._cache.popitem(last=False)
                del self._timestamps[oldest_key]
                self._evictions += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        return time.time() > self._timestamps.get(key, 0)
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache."""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
    
    def _cleanup_expired(self) -> None:
        """Background thread to clean up expired entries."""
        while True:
            try:
                time.sleep(60)  # Cleanup every minute
                with self._lock:
                    expired_keys = [k for k, v in self._timestamps.items() if time.time() > v]
                    for key in expired_keys:
                        self._remove_key(key)
                        self._evictions += 1
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'evictions': self._evictions
            }

# Global cache instance
_performance_cache = HighPerformanceCache(max_size=50000, default_ttl=600)  # 10 minutes default TTL

def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom key generation function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = _performance_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _performance_cache.set(cache_key, result, ttl)
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: _performance_cache.clear()
        wrapper.cache_delete = lambda key: _performance_cache.delete(key)
        
        return wrapper
    return decorator

def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics."""
    return _performance_cache.get_stats()

def clear_cache() -> None:
    """Clear global cache."""
    _performance_cache.clear()

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = f"{str(args)}:{str(sorted(kwargs.items()))}"
    return hashlib.md5(key_data.encode()).hexdigest()

class CacheManager:
    """Advanced cache manager with namespaced caches."""
    
    def __init__(self):
        self._caches = {}
        self._default_ttl = 300
    
    def get_cache(self, namespace: str, max_size: int = 10000, ttl: int = None) -> HighPerformanceCache:
        """Get or create a namespaced cache."""
        if namespace not in self._caches:
            self._caches[namespace] = HighPerformanceCache(
                max_size=max_size,
                default_ttl=ttl or self._default_ttl
            )
        return self._caches[namespace]
    
    def clear_namespace(self, namespace: str) -> None:
        """Clear a specific cache namespace."""
        if namespace in self._caches:
            self._caches[namespace].clear()
    
    def clear_all(self) -> None:
        """Clear all caches."""
        for cache in self._caches.values():
            cache.clear()
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        return {
            namespace: cache.get_stats()
            for namespace, cache in self._caches.items()
        }

# Global cache manager
cache_manager = CacheManager()

# Predefined cache namespaces
EXCEL_CACHE = cache_manager.get_cache('excel', max_size=20000, ttl=1800)  # 30 minutes
DATABASE_CACHE = cache_manager.get_cache('database', max_size=15000, ttl=3600)  # 1 hour
TEMPLATE_CACHE = cache_manager.get_cache('template', max_size=5000, ttl=7200)  # 2 hours
UI_CACHE = cache_manager.get_cache('ui', max_size=10000, ttl=600)  # 10 minutes

def excel_cached(ttl: int = 1800):
    """Cache decorator for Excel operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            cached_result = EXCEL_CACHE.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            EXCEL_CACHE.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def database_cached(ttl: int = 3600):
    """Cache decorator for database operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            cached_result = DATABASE_CACHE.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            DATABASE_CACHE.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def template_cached(ttl: int = 7200):
    """Cache decorator for template operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            cached_result = TEMPLATE_CACHE.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            TEMPLATE_CACHE.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
