"""
App Integration for Optimized Database
Add this to your main app.py file
"""

# Add this import at the top of app.py
from optimized_database import db, search_products, get_all_products, get_database_type, get_database_stats

# Replace your existing product search routes with these optimized versions:

@app.route('/api/search-products')
def api_search_products():
    """Optimized product search endpoint"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Use optimized search
        products = search_products(query, limit)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products),
            'database_type': get_database_type(),
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database-stats')
def api_database_stats():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add this to your existing product matching logic:
def optimized_product_matching(product_name, product_type=None):
    """Optimized product matching using the best available database"""
    try:
        # Search for exact matches first
        exact_matches = search_products(product_name, limit=10)
        
        if exact_matches:
            # Return the best match
            return exact_matches[0]
        
        # Search for partial matches
        partial_matches = search_products(product_name.split()[0] if product_name else "", limit=5)
        
        if partial_matches:
            return partial_matches[0]
        
        return None
        
    except Exception as e:
        logging.error(f"Product matching failed: {e}")
        return None
