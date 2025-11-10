"""
Pagination and Lazy Loading Support
Implements efficient pagination for large datasets
"""

import math
from typing import Dict, List, Any, Optional
from flask import request


class Paginator:
    """Handles pagination for large datasets"""
    
    def __init__(self, items: List[Any], page: int = 1, per_page: int = 100):
        """
        Initialize paginator
        
        Args:
            items: List of items to paginate
            page: Current page number (1-indexed)
            per_page: Number of items per page
        """
        self.items = items
        self.total_items = len(items)
        self.per_page = max(1, per_page)  # Ensure at least 1 item per page
        self.page = max(1, page)  # Ensure at least page 1
        self.total_pages = math.ceil(self.total_items / self.per_page) if self.total_items > 0 else 1
        
        # Adjust page if it exceeds total pages
        if self.page > self.total_pages:
            self.page = self.total_pages
    
    def get_page_items(self) -> List[Any]:
        """Get items for the current page"""
        start_idx = (self.page - 1) * self.per_page
        end_idx = start_idx + self.per_page
        return self.items[start_idx:end_idx]
    
    def has_next(self) -> bool:
        """Check if there's a next page"""
        return self.page < self.total_pages
    
    def has_prev(self) -> bool:
        """Check if there's a previous page"""
        return self.page > 1
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get pagination metadata"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'has_next': self.has_next(),
            'has_prev': self.has_prev(),
            'next_page': self.page + 1 if self.has_next() else None,
            'prev_page': self.page - 1 if self.has_prev() else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert paginator to dictionary with items and metadata"""
        return {
            'items': self.get_page_items(),
            'pagination': self.get_metadata()
        }


def paginate_from_request(items: List[Any], default_per_page: int = 100) -> Dict[str, Any]:
    """
    Paginate items based on request parameters
    
    Args:
        items: List of items to paginate
        default_per_page: Default items per page
    
    Returns:
        Dictionary with paginated items and metadata
    """
    # Get pagination parameters from request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 1000)  # Max 1000 items per page
    
    # Create paginator
    paginator = Paginator(items, page=page, per_page=per_page)
    
    return paginator.to_dict()


class LazyLoader:
    """Implements lazy loading for large datasets"""
    
    def __init__(self, data_source: callable, chunk_size: int = 50):
        """
        Initialize lazy loader
        
        Args:
            data_source: Callable that returns data when called
            chunk_size: Size of each chunk to load
        """
        self.data_source = data_source
        self.chunk_size = chunk_size
        self._cache = []
        self._total_loaded = 0
        self._all_loaded = False
    
    def load_next_chunk(self) -> List[Any]:
        """Load the next chunk of data"""
        if self._all_loaded:
            return []
        
        try:
            # Get data from source
            data = self.data_source()
            
            # Get next chunk
            start_idx = self._total_loaded
            end_idx = start_idx + self.chunk_size
            chunk = data[start_idx:end_idx]
            
            # Update state
            self._cache.extend(chunk)
            self._total_loaded += len(chunk)
            
            # Check if all data loaded
            if len(chunk) < self.chunk_size or end_idx >= len(data):
                self._all_loaded = True
            
            return chunk
        except Exception:
            self._all_loaded = True
            return []
    
    def get_loaded_data(self) -> List[Any]:
        """Get all loaded data so far"""
        return self._cache
    
    def is_complete(self) -> bool:
        """Check if all data has been loaded"""
        return self._all_loaded


def create_paginated_response(
    items: List[Any],
    page: int = 1,
    per_page: int = 100,
    additional_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create a standardized paginated response
    
    Args:
        items: List of items to paginate
        page: Current page number
        per_page: Items per page
        additional_data: Additional data to include in response
    
    Returns:
        Standardized paginated response dictionary
    """
    paginator = Paginator(items, page=page, per_page=per_page)
    
    response = {
        'success': True,
        'data': paginator.get_page_items(),
        'pagination': paginator.get_metadata()
    }
    
    # Add any additional data
    if additional_data:
        response.update(additional_data)
    
    return response


def get_pagination_params(default_per_page: int = 100) -> tuple:
    """
    Extract and validate pagination parameters from request
    
    Args:
        default_per_page: Default number of items per page
    
    Returns:
        Tuple of (page, per_page)
    """
    page = max(1, request.args.get('page', 1, type=int))
    per_page = request.args.get('per_page', default_per_page, type=int)
    
    # Validate and limit per_page
    per_page = max(1, min(per_page, 1000))  # Between 1 and 1000
    
    return page, per_page

