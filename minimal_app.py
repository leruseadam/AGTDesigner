#!/usr/bin/env python3
"""Minimal Flask app for testing database analytics"""

from flask import Flask, jsonify
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/database-analytics', methods=['GET'])
def database_analytics():
    """Get advanced analytics data for the database."""
    try:
        db_path = "product_database.db"
        
        with sqlite3.connect(db_path) as conn:
            # Get product type distribution
            product_types_df = pd.read_sql_query('''
                SELECT product_type, COUNT(*) as count
                FROM products
                WHERE product_type IS NOT NULL AND product_type != ''
                GROUP BY product_type
                ORDER BY count DESC
            ''', conn)
            
            # Get lineage distribution
            lineage_df = pd.read_sql_query('''
                SELECT canonical_lineage, COUNT(*) as count
                FROM strains
                WHERE canonical_lineage IS NOT NULL AND canonical_lineage != ''
                GROUP BY canonical_lineage
                ORDER BY count DESC
            ''', conn)
            
            # Get vendor performance
            vendor_performance_df = pd.read_sql_query('''
                SELECT vendor, COUNT(*) as product_count,
                       COUNT(DISTINCT brand) as unique_brands,
                       COUNT(DISTINCT product_type) as unique_types
                FROM products
                WHERE vendor IS NOT NULL AND vendor != ''
                GROUP BY vendor
                ORDER BY product_count DESC
                LIMIT 10
            ''', conn)
            
            # Get recent activity (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            recent_activity_df = pd.read_sql_query('''
                SELECT DATE(last_seen_date) as date, COUNT(*) as new_products
                FROM products
                WHERE last_seen_date >= ?
                GROUP BY DATE(last_seen_date)
                ORDER BY date DESC
            ''', conn, params=[thirty_days_ago])
            
            return jsonify({
                'product_type_distribution': dict(zip(product_types_df['product_type'], product_types_df['count'])),
                'lineage_distribution': dict(zip(lineage_df['canonical_lineage'], lineage_df['count'])),
                'vendor_performance': vendor_performance_df.to_dict('records'),
                'recent_activity': recent_activity_df.to_dict('records'),
                'analytics_generated': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting database analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Minimal Flask app running. Test /api/database-analytics endpoint."

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 8005))
    logger.info(f"Starting minimal Flask app on port {port}")
    app.run(host='127.0.0.1', port=port, debug=False)
