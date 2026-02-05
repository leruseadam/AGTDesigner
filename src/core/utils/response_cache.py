"""
Aggressive Response Caching for API Endpoints
Implements smart caching with ETags, compression, and TTL
"""

import hashlib
import json
import gzip
import time
import logging
from functools import wraps
from flask import request, make_response, jsonify
from typing import Any, Dict, Optional, Callable
import pickle

logger = logging.getLogger(__name__)


class ResponseCache:
    """High-performance response cache with compression and ETags"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.timestamps = {}
        self.etags = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_cache_key(self, route: str, args: Dict, data: Any = None) -> str:
        """Generate unique cache key from route, args, and request data"""
        key_parts = [route]
        
        # Add query parameters
        if args:
            key_parts.append(json.dumps(sorted(args.items()), default=str))
        
        # Add request data for POST requests
        if data:
            try:
                key_parts.append(json.dumps(data, sort_keys=True, default=str))
            except Exception:
                key_parts.append(str(data))
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_etag(self, data: Any) -> str:
        """Generate ETag for response data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached response"""
        if key in self.cache:
            # Check if expired
            if time.time() - self.timestamps[key] < self.default_ttl:
                self.hit_count += 1
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
                if key in self.etags:
                    del self.etags[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key: str, response_data: Any, etag: str, ttl: Optional[int] = None):
        """Cache response data"""
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
            if oldest_key in self.etags:
                del self.etags[oldest_key]
        
        self.cache[key] = response_data
        self.timestamps[key] = time.time()
        self.etags[key] = etag
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries matching pattern"""
        if pattern is None:
            # Clear all
            self.cache.clear()
            self.timestamps.clear()
            self.etags.clear()
        else:
            # Clear matching keys
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
                del self.timestamps[key]
                if key in self.etags:
                    del self.etags[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total
        }


# Global cache instances
response_cache = ResponseCache(max_size=10000, default_ttl=300)  # 5 minutes
aggressive_cache = ResponseCache(max_size=5000, default_ttl=600)  # 10 minutes for stable data


def cached_route(ttl: int = 300, cache_type: str = 'normal', vary_by: list = None):
    """
    Decorator for caching route responses with ETags and compression
    
    Args:
        ttl: Time to live in seconds
        cache_type: 'normal' or 'aggressive' for different cache strategies
        vary_by: List of request attributes to vary cache by (e.g., ['user_id', 'store'])
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Select cache
            cache = aggressive_cache if cache_type == 'aggressive' else response_cache
            
            # Generate cache key
            route = request.path
            query_args = dict(request.args)
            
            # Add vary_by parameters to cache key
            if vary_by:
                from flask import session
                for param in vary_by:
                    if param in session:
                        query_args[f'_vary_{param}'] = session[param]
            
            # Include POST data for POST requests
            request_data = None
            if request.method == 'POST':
                try:
                    request_data = request.get_json()
                except Exception:
                    pass
            
            cache_key = cache._generate_cache_key(route, query_args, request_data)
            
            # Check if client sent If-None-Match header
            client_etag = request.headers.get('If-None-Match')
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                cached_etag = cache.etags.get(cache_key)
                
                # If client has matching ETag, return 304 Not Modified
                if client_etag and client_etag == cached_etag:
                    response = make_response('', 304)
                    response.headers['ETag'] = cached_etag
                    return response
                
                # Check if cached response is a Flask Response object (file download, etc.)
                from flask import Response as FlaskResponse
                if isinstance(cached_response, FlaskResponse):
                    # Can't cache file responses - return the response directly
                    cached_response.headers['ETag'] = cached_etag
                    cached_response.headers['X-Cache'] = 'HIT'
                    cached_response.headers['Cache-Control'] = f'max-age={ttl}'
                    return cached_response
                
                # Return cached JSON response
                response = make_response(jsonify(cached_response))
                response.headers['ETag'] = cached_etag
                response.headers['X-Cache'] = 'HIT'
                response.headers['Cache-Control'] = f'max-age={ttl}'
                
                # Add compression if client supports it
                if 'gzip' in request.headers.get('Accept-Encoding', ''):
                    response.headers['Content-Encoding'] = 'gzip'
                
                return response
            
            # Execute the route function
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Check if result is a Flask Response object (file download, etc.)
            from flask import Response as FlaskResponse
            if isinstance(result, FlaskResponse):
                # Don't cache file responses - return immediately
                result.headers['X-Response-Time'] = f"{elapsed*1000:.1f}ms"
                return result
            
            # Extract response data
            if isinstance(result, tuple):
                response_data, status_code = result[0], result[1] if len(result) > 1 else 200
            else:
                response_data = result
                status_code = 200
            
            # Check if response_data is a Flask Response object
            if isinstance(response_data, FlaskResponse):
                # Don't cache file responses - return immediately
                response_data.headers['X-Response-Time'] = f"{elapsed*1000:.1f}ms"
                return response_data
            
            # Only cache successful JSON responses
            if status_code == 200:
                try:
                    # Generate ETag
                    etag = cache._generate_etag(response_data)
                    
                    # Cache the response (only if it's JSON-serializable)
                    cache.set(cache_key, response_data, etag, ttl)
                    
                    # Create response
                    response = make_response(jsonify(response_data))
                    response.headers['ETag'] = etag
                    response.headers['X-Cache'] = 'MISS'
                    response.headers['X-Response-Time'] = f"{elapsed*1000:.1f}ms"
                    response.headers['Cache-Control'] = f'max-age={ttl}'
                    
                    return response
                except (TypeError, ValueError) as cache_error:
                    # If response can't be cached (e.g., contains non-serializable objects), skip caching
                    logger.warning(f"Response not cacheable: {cache_error}. Returning without cache.")
                    if isinstance(response_data, dict):
                        response = make_response(jsonify(response_data))
                    else:
                        response = make_response(str(response_data), status_code)
                    response.headers['X-Cache'] = 'SKIP'
                    response.headers['X-Response-Time'] = f"{elapsed*1000:.1f}ms"
                    return response
            else:
                # Don't cache errors
                return result
        
        # Add cache management methods
        wrapper.clear_cache = lambda: cache.invalidate()
        wrapper.get_cache_stats = lambda: cache.get_stats()
        
        return wrapper
    return decorator


def compress_response(response):
    """Compress response data with gzip"""
    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        return response
    
    # Get response data
    data = response.get_data()
    
    # Only compress if larger than 1KB
    if len(data) < 1024:
        return response
    
    # Compress
    compressed = gzip.compress(data, compresslevel=6)
    
    # Update response
    response.set_data(compressed)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers['Content-Length'] = len(compressed)
    
    # Calculate compression ratio
    ratio = (1 - len(compressed) / len(data)) * 100
    response.headers['X-Compression-Ratio'] = f"{ratio:.1f}%"
    
    return response


def invalidate_cache_on_change(patterns: list):
    """
    Decorator to invalidate cache when data changes
    Use on POST/PUT/DELETE routes that modify data
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate matching cache entries
            for pattern in patterns:
                response_cache.invalidate(pattern)
                aggressive_cache.invalidate(pattern)
                logger.info(f"Cache invalidated for pattern: {pattern}")
            
            return result
        return wrapper
    return decorator


# Convenience function to get all cache stats
def get_all_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches"""
    return {
        'response_cache': response_cache.get_stats(),
        'aggressive_cache': aggressive_cache.get_stats()
    }

