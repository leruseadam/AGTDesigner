"""
Lazy loading system for heavy components and background processing.
Implements lazy initialization, background loading, and resource management.
"""

import threading
import time
import logging
from typing import Any, Callable, Optional, Dict, TypeVar, Generic
from functools import wraps
import weakref
from concurrent.futures import ThreadPoolExecutor, Future
import queue

logger = logging.getLogger(__name__)

T = TypeVar('T')

class LazyLoader(Generic[T]):
    """Lazy loader with background initialization and caching."""
    
    def __init__(self, factory: Callable[[], T], name: str = None, background: bool = True):
        self.factory = factory
        self.name = name or factory.__name__
        self.background = background
        self._value: Optional[T] = None
        self._loading = False
        self._lock = threading.Lock()
        self._load_time = None
        self._error = None
        
        if background:
            self._start_background_load()
    
    def _start_background_load(self):
        """Start background loading in a separate thread."""
        def load():
            try:
                logger.info(f"Starting background load of {self.name}")
                start_time = time.time()
                self._value = self.factory()
                self._load_time = time.time() - start_time
                logger.info(f"Background load of {self.name} completed in {self._load_time:.3f}s")
            except Exception as e:
                self._error = e
                logger.error(f"Background load of {self.name} failed: {e}")
            finally:
                with self._lock:
                    self._loading = False
        
        with self._lock:
            if not self._loading and self._value is None:
                self._loading = True
                thread = threading.Thread(target=load, daemon=True, name=f"LazyLoader-{self.name}")
                thread.start()
    
    def get(self) -> T:
        """Get the loaded value, blocking if necessary."""
        with self._lock:
            if self._value is not None:
                return self._value
            
            if self._error is not None:
                raise self._error
            
            if self._loading:
                # Wait for background loading to complete
                self._lock.release()
                while True:
                    time.sleep(0.01)  # Small delay
                    with self._lock:
                        if self._value is not None:
                            return self._value
                        if self._error is not None:
                            raise self._error
            else:
                # Load immediately
                logger.info(f"Synchronous load of {self.name}")
                start_time = time.time()
                self._value = self.factory()
                self._load_time = time.time() - start_time
                logger.info(f"Synchronous load of {self.name} completed in {self._load_time:.3f}s")
                return self._value
    
    def is_loaded(self) -> bool:
        """Check if the value is loaded."""
        with self._lock:
            return self._value is not None
    
    def is_loading(self) -> bool:
        """Check if the value is currently loading."""
        with self._lock:
            return self._loading
    
    def get_load_time(self) -> Optional[float]:
        """Get the time taken to load the value."""
        return self._load_time
    
    def reset(self):
        """Reset the loader to allow reloading."""
        with self._lock:
            self._value = None
            self._loading = False
            self._load_time = None
            self._error = None
        
        if self.background:
            self._start_background_load()

class LazyManager:
    """Manager for multiple lazy loaders with resource cleanup."""
    
    def __init__(self):
        self._loaders: Dict[str, LazyLoader] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="LazyManager")
    
    def register(self, name: str, factory: Callable[[], Any], background: bool = True) -> LazyLoader:
        """Register a lazy loader."""
        with self._lock:
            if name in self._loaders:
                return self._loaders[name]
            
            loader = LazyLoader(factory, name, background)
            self._loaders[name] = loader
            return loader
    
    def get(self, name: str) -> Any:
        """Get a loaded value by name."""
        with self._lock:
            if name not in self._loaders:
                raise KeyError(f"No lazy loader registered for '{name}'")
            return self._loaders[name].get()
    
    def get_loader(self, name: str) -> Optional[LazyLoader]:
        """Get a lazy loader by name."""
        with self._lock:
            return self._loaders.get(name)
    
    def is_loaded(self, name: str) -> bool:
        """Check if a loader is loaded."""
        with self._lock:
            if name not in self._loaders:
                return False
            return self._loaders[name].is_loaded()
    
    def preload_all(self):
        """Preload all registered loaders."""
        futures = []
        with self._lock:
            for name, loader in self._loaders.items():
                if not loader.is_loaded() and not loader.is_loading():
                    future = self._executor.submit(loader.get)
                    futures.append((name, future))
        
        # Wait for all to complete
        for name, future in futures:
            try:
                future.result(timeout=30)  # 30 second timeout
                logger.info(f"Preloaded {name}")
            except Exception as e:
                logger.error(f"Failed to preload {name}: {e}")
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all loaders."""
        stats = {}
        with self._lock:
            for name, loader in self._loaders.items():
                stats[name] = {
                    'loaded': loader.is_loaded(),
                    'loading': loader.is_loading(),
                    'load_time': loader.get_load_time(),
                    'has_error': loader._error is not None
                }
        return stats
    
    def cleanup(self):
        """Cleanup all loaders and resources."""
        with self._lock:
            self._loaders.clear()
        self._executor.shutdown(wait=True)

# Global lazy manager
_lazy_manager = LazyManager()

def lazy_loaded(name: str, background: bool = True):
    """Decorator for lazy loading functions."""
    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        def wrapper():
            loader = _lazy_manager.register(name, func, background)
            return loader.get()
        return wrapper
    return decorator

def register_lazy(name: str, factory: Callable[[], Any], background: bool = True) -> LazyLoader:
    """Register a lazy loader with the global manager."""
    return _lazy_manager.register(name, factory, background)

def get_lazy(name: str) -> Any:
    """Get a lazy loaded value."""
    return _lazy_manager.get(name)

def preload_all():
    """Preload all lazy components."""
    _lazy_manager.preload_all()

def get_lazy_stats() -> Dict[str, Dict[str, Any]]:
    """Get lazy loading statistics."""
    return _lazy_manager.get_stats()

class BackgroundProcessor:
    """Background processor for heavy operations."""
    
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="BackgroundProcessor")
        self._tasks = {}
        self._lock = threading.Lock()
    
    def submit(self, name: str, func: Callable, *args, **kwargs) -> Future:
        """Submit a background task."""
        with self._lock:
            if name in self._tasks:
                # Cancel previous task if still running
                future = self._tasks[name]
                if not future.done():
                    future.cancel()
            
            future = self.executor.submit(func, *args, **kwargs)
            self._tasks[name] = future
            return future
    
    def get_result(self, name: str, timeout: Optional[float] = None) -> Any:
        """Get result of a background task."""
        with self._lock:
            if name not in self._tasks:
                raise KeyError(f"No task found for '{name}'")
            
            future = self._tasks[name]
            return future.result(timeout=timeout)
    
    def is_done(self, name: str) -> bool:
        """Check if a task is done."""
        with self._lock:
            if name not in self._tasks:
                return True
            
            return self._tasks[name].done()
    
    def cancel(self, name: str):
        """Cancel a background task."""
        with self._lock:
            if name in self._tasks:
                self._tasks[name].cancel()
    
    def cleanup(self):
        """Cleanup background processor."""
        self.executor.shutdown(wait=True)

# Global background processor
_background_processor = BackgroundProcessor()

def submit_background(name: str, func: Callable, *args, **kwargs) -> Future:
    """Submit a background task."""
    return _background_processor.submit(name, func, *args, **kwargs)

def get_background_result(name: str, timeout: Optional[float] = None) -> Any:
    """Get background task result."""
    return _background_processor.get_result(name, timeout)

def is_background_done(name: str) -> bool:
    """Check if background task is done."""
    return _background_processor.is_done(name)

def cancel_background(name: str):
    """Cancel background task."""
    _background_processor.cancel(name)

class ResourceManager:
    """Resource manager for cleanup and memory management."""
    
    def __init__(self):
        self._resources = []
        self._cleanup_functions = []
        self._lock = threading.Lock()
    
    def register_resource(self, resource: Any, cleanup_func: Callable[[Any], None] = None):
        """Register a resource for cleanup."""
        with self._lock:
            self._resources.append(weakref.ref(resource))
            if cleanup_func:
                self._cleanup_functions.append((weakref.ref(resource), cleanup_func))
    
    def register_cleanup(self, cleanup_func: Callable[[], None]):
        """Register a cleanup function."""
        with self._lock:
            self._cleanup_functions.append((None, cleanup_func))
    
    def cleanup(self):
        """Cleanup all registered resources."""
        with self._lock:
            # Cleanup resources
            for resource_ref in self._resources[:]:
                resource = resource_ref()
                if resource is None:  # Resource was garbage collected
                    self._resources.remove(resource_ref)
            
            # Run cleanup functions
            for resource_ref, cleanup_func in self._cleanup_functions[:]:
                if resource_ref is None:
                    # Global cleanup function
                    try:
                        cleanup_func()
                    except Exception as e:
                        logger.error(f"Cleanup function failed: {e}")
                else:
                    resource = resource_ref()
                    if resource is not None:
                        try:
                            cleanup_func(resource)
                        except Exception as e:
                            logger.error(f"Resource cleanup failed: {e}")
                    self._cleanup_functions.remove((resource_ref, cleanup_func))
    
    def get_resource_count(self) -> int:
        """Get number of registered resources."""
        with self._lock:
            return len(self._resources)

# Global resource manager
_resource_manager = ResourceManager()

def register_resource(resource: Any, cleanup_func: Callable[[Any], None] = None):
    """Register a resource for cleanup."""
    _resource_manager.register_resource(resource, cleanup_func)

def register_cleanup(cleanup_func: Callable[[], None]):
    """Register a cleanup function."""
    _resource_manager.register_cleanup(cleanup_func)

def cleanup_resources():
    """Cleanup all registered resources."""
    _resource_manager.cleanup()

# Performance monitoring
class PerformanceMonitor:
    """Monitor performance of lazy loading and background operations."""
    
    def __init__(self):
        self._metrics = {
            'lazy_loads': 0,
            'lazy_load_time': 0.0,
            'background_tasks': 0,
            'background_task_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._lock = threading.Lock()
    
    def record_lazy_load(self, load_time: float):
        """Record lazy load metrics."""
        with self._lock:
            self._metrics['lazy_loads'] += 1
            self._metrics['lazy_load_time'] += load_time
    
    def record_background_task(self, task_time: float):
        """Record background task metrics."""
        with self._lock:
            self._metrics['background_tasks'] += 1
            self._metrics['background_task_time'] += task_time
    
    def record_cache_hit(self):
        """Record cache hit."""
        with self._lock:
            self._metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        with self._lock:
            self._metrics['cache_misses'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            stats = self._metrics.copy()
            
            if stats['lazy_loads'] > 0:
                stats['avg_lazy_load_time'] = stats['lazy_load_time'] / stats['lazy_loads']
            
            if stats['background_tasks'] > 0:
                stats['avg_background_task_time'] = stats['background_task_time'] / stats['background_tasks']
            
            total_cache_requests = stats['cache_hits'] + stats['cache_misses']
            if total_cache_requests > 0:
                stats['cache_hit_rate'] = stats['cache_hits'] / total_cache_requests * 100
            
            return stats

# Global performance monitor
_performance_monitor = PerformanceMonitor()

def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics."""
    return _performance_monitor.get_stats()
