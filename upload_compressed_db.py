#!/usr/bin/env python3
"""
Upload compressed database file to PythonAnywhere
"""

import requests
import os
import time

def upload_database():
    """Upload the database file"""
    base_url = 'https://www.agtpricetags.com'
    
    # Try small test database first, then compressed file
    files_to_try = [
        ('test_database.db', 'application/octet-stream'),
        ('product_database.db.gz', 'application/gzip'),
        ('product_database.db', 'application/octet-stream')
    ]
    
    print('🔧 UPLOADING DATABASE')
    print('=' * 50)
    
    for db_file, content_type in files_to_try:
        if not os.path.exists(db_file):
            print(f"⚠️  File not found: {db_file}")
            continue
            
        file_size = os.path.getsize(db_file)
        print(f"📊 Trying {db_file}: {file_size / (1024 * 1024):.1f} MB")
        
        # Upload the database file
        print(f'📤 Uploading {db_file}...')
        try:
            with open(db_file, 'rb') as f:
                files = {'file': (db_file, f, content_type)}
                response = requests.post(f'{base_url}/api/upload-database-file', files=files, timeout=300)
            
            print(f'📤 Upload status: {response.status_code}')
            if response.status_code == 200:
                result = response.json()
                print(f'✅ Database upload successful!')
                print(f'📋 Message: {result.get("message", "Unknown")}')
                return True
            else:
                print(f'❌ Upload failed: {response.status_code}')
                print(f'Response: {response.text[:300]}')
                continue
        except requests.exceptions.Timeout:
            print(f'⏰ Timeout uploading {db_file}')
            continue
        except Exception as e:
            print(f'❌ Error uploading {db_file}: {e}')
            continue
    
    print("❌ All upload attempts failed")
    return False

def create_decompress_endpoint():
    """Create an endpoint to decompress the database on PythonAnywhere"""
    decompress_code = '''
@app.route('/api/decompress-database', methods=['POST'])
def decompress_database():
    """Decompress the uploaded database file"""
    try:
        import gzip
        import os
        
        # Paths
        compressed_file = os.path.join(current_dir, 'uploads', 'product_database', 'product_database.db.gz')
        db_file = os.path.join(current_dir, 'uploads', 'product_database', 'product_database.db')
        
        if not os.path.exists(compressed_file):
            return jsonify({'error': 'Compressed database file not found'}), 404
        
        # Decompress the file
        with gzip.open(compressed_file, 'rb') as f_in:
            with open(db_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Verify the decompressed file
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file)
            
            # Test the database
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM products')
            products_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM strains')
            strains_count = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Database decompressed successfully',
                'file_size': file_size,
                'products': products_count,
                'strains': strains_count
            })
        else:
            return jsonify({'error': 'Failed to decompress database'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
    
    print("📝 Add this code to your app.py file:")
    print(decompress_code)

if __name__ == "__main__":
    print("🔧 DATABASE UPLOAD")
    print("=" * 50)
    
    # Upload the database file
    if upload_database():
        print(f"\\n✅ DATABASE UPLOADED!")
        print(f"📋 Next steps:")
        print(f"1. Test with /api/database-status")
        print(f"2. Verify the database is working on the website")
    else:
        print(f"\\n❌ UPLOAD FAILED!")
        print(f"📋 Try the manual upload methods in manual_upload_guide.md")
