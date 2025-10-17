"""
Lightweight performance optimizations for PythonAnywhere.
Minimal CPU overhead while providing essential performance improvements.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from functools import wraps

logger = logging.getLogger(__name__)

class LightweightCache:
    """Lightweight cache with minimal overhead."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                # Check if expired
                if time.time() - self._timestamps[key] > self.default_ttl:
                    del self._cache[key]
                    del self._timestamps[key]
                    self._misses += 1
                    return None
                
                self._hits += 1
                return self._cache[key]
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self._lock:
            ttl = ttl or self.default_ttl
            
            # Remove oldest entries if at capacity
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), key=self._timestamps.get)
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2)
            }

class LightweightPerformanceMonitor:
    """Lightweight performance monitoring with minimal CPU overhead."""
    
    def __init__(self):
        self._operation_times = defaultdict(list)
        self._lock = threading.Lock()
        self._enabled = True
    
    def record_operation_time(self, operation: str, duration: float):
        """Record operation time."""
        if not self._enabled:
            return
        
        with self._lock:
            # Keep only last 10 measurements to reduce memory
            if len(self._operation_times[operation]) >= 10:
                self._operation_times[operation] = self._operation_times[operation][-5:]
            
            self._operation_times[operation].append(duration)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            stats = {}
            for operation, times in self._operation_times.items():
                if times:
                    stats[operation] = {
                        'count': len(times),
                        'avg_time': sum(times) / len(times),
                        'max_time': max(times)
                    }
            return stats
    
    def disable(self):
        """Disable monitoring to save CPU."""
        self._enabled = False
    
    def enable(self):
        """Enable monitoring."""
        self._enabled = True

# Global lightweight instances
_lightweight_cache = LightweightCache(max_size=5000, default_ttl=600)
_lightweight_monitor = LightweightPerformanceMonitor()

def lightweight_cached(ttl: int = 300):
    """Lightweight caching decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simple key generation
            cache_key = f"{func.__name__}:{hash(str(args))}:{hash(str(sorted(kwargs.items())))}"
            
            # Try cache first
            cached_result = _lightweight_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute and cache
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            _lightweight_cache.set(cache_key, result, ttl)
            _lightweight_monitor.record_operation_time(func.__name__, duration)
            
            return result
        return wrapper
    return decorator

def performance_timer_lightweight(operation_name: str):
    """Lightweight performance timer decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                _lightweight_monitor.record_operation_time(operation_name, duration)
        return wrapper
    return decorator

def get_lightweight_stats() -> Dict[str, Any]:
    """Get lightweight performance statistics."""
    return {
        'cache': _lightweight_cache.get_stats(),
        'operations': _lightweight_monitor.get_stats(),
        'timestamp': time.time()
    }

def clear_lightweight_cache():
    """Clear lightweight cache."""
    _lightweight_cache.clear()

def disable_monitoring():
    """Disable performance monitoring to save CPU."""
    _lightweight_monitor.disable()
    logger.info("Lightweight performance monitoring disabled")

def enable_monitoring():
    """Enable performance monitoring."""
    _lightweight_monitor.enable()
    logger.info("Lightweight performance monitoring enabled")

# Auto-disable heavy monitoring on import to prevent CPU issues
try:
    import psutil
    # If CPU usage is high, disable monitoring
    cpu_usage = psutil.cpu_percent(interval=0.1)
    if cpu_usage > 70:
        disable_monitoring()
        logger.warning(f"High CPU usage detected ({cpu_usage}%), disabling performance monitoring")
except ImportError:
    # psutil not available, use lightweight monitoring
    logger.info("psutil not available, using lightweight monitoring only")
except Exception as e:
    logger.warning(f"Failed to check CPU usage: {e}, using lightweight monitoring")
