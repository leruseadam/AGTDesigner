# ultra_lightweight_performance.py
"""
Ultra-Lightweight Performance Optimizer for Maximum Responsiveness

This module provides minimal-overhead performance optimizations specifically
designed for web applications with high CPU/memory usage.
"""

import gc
import time
import threading
from typing import Dict, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class UltraLightweightOptimizer:
    """Ultra-lightweight performance optimizer with minimal overhead."""
    
    def __init__(self):
        self._enabled = True
        self._last_cleanup = time.time()
        self._cleanup_interval = 30  # seconds
        self._memory_threshold = 80  # percent
        self._cpu_threshold = 70  # percent
        self._operation_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Minimal monitoring
        self._last_memory_check = 0
        self._last_cpu_check = 0
        self._check_interval = 60  # Check every 60 seconds
        
        logger.info("Ultra-lightweight performance optimizer initialized")
    
    def optimize_memory(self):
        """Ultra-lightweight memory optimization."""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Clear operation cache if it's getting large
            if len(self._operation_cache) > 1000:
                self._operation_cache.clear()
                logger.debug("Cleared operation cache")
            
            logger.debug(f"Memory optimization: collected {collected} objects")
            return True
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
            return False
    
    def optimize_cpu(self):
        """Ultra-lightweight CPU optimization."""
        try:
            # Clear any pending operations
            self._operation_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            logger.debug("CPU optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"CPU optimization failed: {e}")
            return False
    
    def should_optimize(self) -> bool:
        """Check if optimization is needed."""
        current_time = time.time()
        
        # Only check every 60 seconds to minimize overhead
        if current_time - self._last_memory_check < self._check_interval:
            return False
        
        self._last_memory_check = current_time
        
        try:
            # Minimal memory check
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > self._memory_threshold:
                logger.warning(f"High memory usage detected: {memory.percent}%")
                return True
                
        except ImportError:
            # psutil not available, skip check
            pass
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
        
        return False
    
    def auto_optimize(self):
        """Automatic optimization when needed."""
        if not self._enabled:
            return
        
        current_time = time.time()
        
        # Only run cleanup every 30 seconds
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        
        if self.should_optimize():
            logger.info("Running automatic optimization")
            self.optimize_memory()
            self.optimize_cpu()
    
    def cache_operation(self, key: str, operation_func, *args, **kwargs):
        """Cache operation results with minimal overhead."""
        if not self._enabled:
            return operation_func(*args, **kwargs)
        
        # Check cache first
        if key in self._operation_cache:
            self._cache_hits += 1
            return self._operation_cache[key]
        
        # Execute operation
        result = operation_func(*args, **kwargs)
        
        # Cache result (limit cache size)
        if len(self._operation_cache) < 500:
            self._operation_cache[key] = result
        
        self._cache_misses += 1
        return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get minimal performance statistics."""
        cache_hit_rate = 0
        total_requests = self._cache_hits + self._cache_misses
        if total_requests > 0:
            cache_hit_rate = (self._cache_hits / total_requests) * 100
        
        return {
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._operation_cache),
            'enabled': self._enabled,
            'last_cleanup': self._last_cleanup
        }
    
    def disable(self):
        """Disable optimizer to reduce overhead."""
        self._enabled = False
        self._operation_cache.clear()
        logger.info("Ultra-lightweight optimizer disabled")
    
    def enable(self):
        """Enable optimizer."""
        self._enabled = True
        logger.info("Ultra-lightweight optimizer enabled")

# Global optimizer instance
_optimizer = None

def get_optimizer() -> UltraLightweightOptimizer:
    """Get global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = UltraLightweightOptimizer()
    return _optimizer

def optimize_performance():
    """Run performance optimization."""
    optimizer = get_optimizer()
    optimizer.auto_optimize()

def cache_operation(key: str, operation_func, *args, **kwargs):
    """Cache operation with minimal overhead."""
    optimizer = get_optimizer()
    return optimizer.cache_operation(key, operation_func, *args, **kwargs)

def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics."""
    optimizer = get_optimizer()
    return optimizer.get_performance_stats()

def disable_optimizer():
    """Disable optimizer to reduce overhead."""
    optimizer = get_optimizer()
    optimizer.disable()

def enable_optimizer():
    """Enable optimizer."""
    optimizer = get_optimizer()
    optimizer.enable()

# Auto-optimization thread
_optimization_thread = None
_optimization_running = False

def start_auto_optimization():
    """Start background auto-optimization."""
    global _optimization_thread, _optimization_running
    
    if _optimization_running:
        return
    
    _optimization_running = True
    
    def optimization_loop():
        while _optimization_running:
            try:
                optimize_performance()
                time.sleep(30)  # Run every 30 seconds
            except Exception as e:
                logger.error(f"Auto-optimization error: {e}")
                time.sleep(60)  # Wait longer on error
    
    _optimization_thread = threading.Thread(target=optimization_loop, daemon=True)
    _optimization_thread.start()
    logger.info("Auto-optimization started")

def stop_auto_optimization():
    """Stop background auto-optimization."""
    global _optimization_running
    _optimization_running = False
    logger.info("Auto-optimization stopped")

# Initialize on import
try:
    start_auto_optimization()
except Exception as e:
    logger.error(f"Failed to start auto-optimization: {e}")
