#!/usr/bin/env python3
"""
Add Product Sheet Endpoint
Adds an endpoint that returns full product data for the Product Sheet
"""

import sqlite3
import pandas as pd
from flask import jsonify

def add_product_sheet_endpoint(app):
    """Add the product sheet endpoint to the Flask app."""
    
    @app.route('/api/product-sheet', methods=['GET'])
    def get_product_sheet():
        """Get full product data for the Product Sheet display."""
        try:
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            vendor = request.args.get('vendor', '')
            search = request.args.get('search', '')
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Connect to database
            product_db = get_product_database()
            
            with sqlite3.connect(product_db.db_path) as conn:
                # Build query with filters
                where_conditions = []
                params = []
                
                if vendor:
                    where_conditions.append('"Vendor/Supplier*" = ?')
                    params.append(vendor)
                
                if search:
                    where_conditions.append('("Product Name*" LIKE ? OR "Product Brand" LIKE ? OR "Vendor/Supplier*" LIKE ?)')
                    search_term = f'%{search}%'
                    params.extend([search_term, search_term, search_term])
                
                where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
                
                # Get total count
                count_query = f'SELECT COUNT(*) FROM products WHERE {where_clause}'
                total_count = conn.execute(count_query, params).fetchone()[0]
                
                # Get products with all columns
                products_query = f'''
                    SELECT 
                        "Product Name*",
                        "Product Brand",
                        "Product Type*",
                        "Vendor/Supplier*",
                        "Lineage",
                        "THC%",
                        "CBD%",
                        "Weight*",
                        "WeightUnits",
                        "Quantity*",
                        "Price",
                        "Description"
                    FROM products 
                    WHERE {where_clause}
                    ORDER BY "Product Name*"
                    LIMIT ? OFFSET ?
                '''
                
                params.extend([per_page, offset])
                products_df = pd.read_sql_query(products_query, conn, params=params)
                
                # Convert to list of dictionaries
                products = products_df.to_dict('records')
                
                # Get unique vendors for filter
                vendors_query = '''
                    SELECT DISTINCT "Vendor/Supplier*" as vendor, COUNT(*) as count
                    FROM products 
                    WHERE "Vendor/Supplier*" IS NOT NULL AND "Vendor/Supplier*" != ''
                    GROUP BY "Vendor/Supplier*"
                    ORDER BY count DESC
                '''
                vendors_df = pd.read_sql_query(vendors_query, conn)
                vendors = vendors_df.to_dict('records')
                
                return jsonify({
                    'success': True,
                    'products': products,
                    'total_count': total_count,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'vendors': vendors,
                    'filters': {
                        'vendor': vendor,
                        'search': search
                    }
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Add this to your app.py file
if __name__ == "__main__":
    print("Product Sheet endpoint code ready to add to app.py")
