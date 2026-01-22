"""
Request batching and async processing system for high-performance API operations.
"""

import asyncio
import threading
import time
import logging
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass
from queue import Queue, Empty
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref

logger = logging.getLogger(__name__)

@dataclass
class BatchedRequest:
    """Represents a batched request."""
    id: str
    method: str
    endpoint: str
    data: Any
    callback: Optional[Callable] = None
    timeout: float = 5.0
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class BatchResponse:
    """Represents a batch response."""
    id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0

class RequestBatcher:
    """Batches requests for efficient processing."""
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 0.1, max_workers: int = 4):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_workers = max_workers
        
        self._request_queue = Queue()
        self._response_callbacks = {}
        self._batch_lock = threading.Lock()
        self._running = False
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="RequestBatcher")
        
        # Performance metrics
        self._metrics = {
            'batches_processed': 0,
            'requests_processed': 0,
            'total_batch_time': 0.0,
            'avg_batch_size': 0.0,
            'queue_size': 0
        }
        
        # Start batch processor
        self._start_batch_processor()
    
    def _start_batch_processor(self):
        """Start the background batch processor."""
        self._running = True
        processor_thread = threading.Thread(target=self._process_batches, daemon=True)
        processor_thread.start()
    
    def submit_request(self, request: BatchedRequest) -> str:
        """Submit a request for batching."""
        self._request_queue.put(request)
        
        # Store callback for response
        if request.callback:
            self._response_callbacks[request.id] = request.callback
        
        self._metrics['queue_size'] = self._request_queue.qsize()
        return request.id
    
    def _process_batches(self):
        """Process batches of requests."""
        batch = []
        last_batch_time = time.time()
        
        while self._running:
            try:
                # Try to get a request with timeout
                try:
                    request = self._request_queue.get(timeout=0.01)
                    batch.append(request)
                except Empty:
                    # Check if we should process current batch
                    if batch and (time.time() - last_batch_time) >= self.batch_timeout:
                        self._process_batch(batch)
                        batch = []
                        last_batch_time = time.time()
                    continue
                
                # Process batch if full
                if len(batch) >= self.batch_size:
                    self._process_batch(batch)
                    batch = []
                    last_batch_time = time.time()
                
                # Update queue size
                self._metrics['queue_size'] = self._request_queue.qsize()
                
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                time.sleep(0.1)
        
        # Process remaining requests
        if batch:
            self._process_batch(batch)
    
    def _process_batch(self, batch: List[BatchedRequest]):
        """Process a batch of requests."""
        if not batch:
            return
        
        start_time = time.time()
        
        # Group requests by endpoint for optimization
        endpoint_groups = {}
        for request in batch:
            if request.endpoint not in endpoint_groups:
                endpoint_groups[request.endpoint] = []
            endpoint_groups[request.endpoint].append(request)
        
        # Process each endpoint group
        futures = []
        for endpoint, requests in endpoint_groups.items():
            future = self._executor.submit(self._process_endpoint_batch, endpoint, requests)
            futures.append(future)
        
        # Wait for all batches to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Endpoint batch processing failed: {e}")
        
        # Update metrics
        processing_time = time.time() - start_time
        self._metrics['batches_processed'] += 1
        self._metrics['requests_processed'] += len(batch)
        self._metrics['total_batch_time'] += processing_time
        self._metrics['avg_batch_size'] = self._metrics['requests_processed'] / self._metrics['batches_processed']
        
        logger.debug(f"Processed batch of {len(batch)} requests in {processing_time:.3f}s")
    
    def _process_endpoint_batch(self, endpoint: str, requests: List[BatchedRequest]):
        """Process a batch of requests for a specific endpoint."""
        # This would be implemented based on the specific endpoint
        # For now, process each request individually
        for request in requests:
            try:
                response = self._process_single_request(request)
                self._deliver_response(response)
            except Exception as e:
                error_response = BatchResponse(
                    id=request.id,
                    success=False,
                    error=str(e)
                )
                self._deliver_response(error_response)
    
    def _process_single_request(self, request: BatchedRequest) -> BatchResponse:
        """Process a single request."""
        start_time = time.time()
        
        try:
            # This would route to the appropriate handler based on endpoint
            result = self._route_request(request)
            
            response = BatchResponse(
                id=request.id,
                success=True,
                data=result,
                processing_time=time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            response = BatchResponse(
                id=request.id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
            return response
    
    def _route_request(self, request: BatchedRequest) -> Any:
        """Route request to appropriate handler."""
        # This would be implemented based on your specific endpoints
        # For now, return a placeholder
        return {"message": f"Processed {request.endpoint}", "data": request.data}
    
    def _deliver_response(self, response: BatchResponse):
        """Deliver response to callback."""
        if response.id in self._response_callbacks:
            callback = self._response_callbacks.pop(response.id)
            try:
                callback(response)
            except Exception as e:
                logger.error(f"Response callback failed: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self._metrics.copy()
    
    def shutdown(self):
        """Shutdown the batcher."""
        self._running = False
        self._executor.shutdown(wait=True)

class AsyncRequestProcessor:
    """Async request processor for high-performance operations."""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_requests = {}
        self._metrics = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'avg_processing_time': 0.0,
            'active_requests': 0
        }
    
    async def process_request(self, request_id: str, coro_func: Callable, *args, **kwargs) -> Any:
        """Process a request asynchronously."""
        async with self._semaphore:
            self._metrics['total_requests'] += 1
            self._metrics['active_requests'] = len(self._active_requests)
            
            start_time = time.time()
            self._active_requests[request_id] = start_time
            
            try:
                result = await coro_func(*args, **kwargs)
                self._metrics['completed_requests'] += 1
                return result
            except Exception as e:
                self._metrics['failed_requests'] += 1
                logger.error(f"Async request {request_id} failed: {e}")
                raise
            finally:
                processing_time = time.time() - start_time
                self._metrics['avg_processing_time'] = (
                    (self._metrics['avg_processing_time'] * (self._metrics['completed_requests'] - 1) + processing_time) /
                    self._metrics['completed_requests']
                )
                
                if request_id in self._active_requests:
                    del self._active_requests[request_id]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get async processing metrics."""
        metrics = self._metrics.copy()
        metrics['active_requests'] = len(self._active_requests)
        return metrics

class RequestCache:
    """Cache for request results with TTL."""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached result."""
        with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps[key] < self.default_ttl:
                    return self._cache[key]
                else:
                    # Expired
                    del self._cache[key]
                    del self._timestamps[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set cached result."""
        with self._lock:
            # Remove oldest entries if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), key=self._timestamps.get)
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def clear(self):
        """Clear cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

class SmartRequestRouter:
    """Smart router that optimizes request handling."""
    
    def __init__(self):
        self._routes = {}
        self._middleware = []
        self._batcher = RequestBatcher()
        self._async_processor = AsyncRequestProcessor()
        self._cache = RequestCache()
        
        # Performance monitoring
        self._route_metrics = {}
    
    def register_route(self, endpoint: str, handler: Callable, batchable: bool = True, cacheable: bool = False):
        """Register a route handler."""
        self._routes[endpoint] = {
            'handler': handler,
            'batchable': batchable,
            'cacheable': cacheable
        }
        self._route_metrics[endpoint] = {
            'requests': 0,
            'avg_time': 0.0,
            'cache_hits': 0
        }
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for request processing."""
        self._middleware.append(middleware)
    
    async def process_request(self, endpoint: str, data: Any, request_id: str = None) -> Any:
        """Process a request with optimizations."""
        if request_id is None:
            request_id = f"{endpoint}_{int(time.time() * 1000)}"
        
        # Check cache first
        cache_key = f"{endpoint}:{hash(str(data))}"
        cached_result = self._cache.get(cache_key)
        if cached_result:
            self._route_metrics[endpoint]['cache_hits'] += 1
            return cached_result
        
        # Apply middleware
        for middleware in self._middleware:
            data = await middleware(data)
        
        # Route to handler
        if endpoint not in self._routes:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        route_info = self._routes[endpoint]
        handler = route_info['handler']
        
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await self._async_processor.process_request(
                    request_id, handler, data
                )
            else:
                # Run sync handler in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, handler, data)
            
            # Cache result if cacheable
            if route_info['cacheable']:
                self._cache.set(cache_key, result)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_route_metrics(endpoint, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Request processing failed for {endpoint}: {e}")
            raise
    
    def _update_route_metrics(self, endpoint: str, processing_time: float):
        """Update route performance metrics."""
        metrics = self._route_metrics[endpoint]
        metrics['requests'] += 1
        metrics['avg_time'] = (metrics['avg_time'] * (metrics['requests'] - 1) + processing_time) / metrics['requests']
    
    def get_route_stats(self) -> Dict[str, Any]:
        """Get route performance statistics."""
        return {
            'routes': self._route_metrics,
            'batcher_metrics': self._batcher.get_metrics(),
            'async_metrics': self._async_processor.get_metrics(),
            'cache_size': len(self._cache._cache)
        }
    
    def shutdown(self):
        """Shutdown the router."""
        self._batcher.shutdown()

# Global instances
_global_router = SmartRequestRouter()
_global_batcher = RequestBatcher()

def register_route(endpoint: str, handler: Callable, batchable: bool = True, cacheable: bool = False):
    """Register a global route."""
    _global_router.register_route(endpoint, handler, batchable, cacheable)

def process_request_async(endpoint: str, data: Any, request_id: str = None) -> Any:
    """Process a request asynchronously."""
    return _global_router.process_request(endpoint, data, request_id)

def submit_batched_request(request: BatchedRequest) -> str:
    """Submit a batched request."""
    return _global_batcher.submit_request(request)

def get_request_stats() -> Dict[str, Any]:
    """Get request processing statistics."""
    return _global_router.get_route_stats()
