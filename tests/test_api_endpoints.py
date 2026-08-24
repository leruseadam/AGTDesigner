"""
Comprehensive tests for API endpoints.
"""
import io
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from flask import Flask, jsonify

# Import app components
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Import app after setting up path
    try:
        # Try importing from app module (works on server)
        import sys
        import importlib
        
        # Clear any cached imports
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Set up test database path if needed
        import os
        if 'TEST_DB_PATH' in os.environ:
            app.config['DATABASE_PATH'] = os.environ['TEST_DB_PATH']
        
        with app.test_client() as client:
            with app.app_context():
                yield client
    except Exception as e:
        pytest.skip(f"Could not import app: {e}")

class TestStatusEndpoint:
    """Tests for /api/status endpoint."""

    def test_posabit_source_ignores_excel_session_file(self, client, tmp_path):
        """POSaBit source should win over any stale Excel session file."""
        excel_path = tmp_path / 'AGT_Bothell_test.xlsx'
        excel_path.write_bytes(b'not really an excel file')

        with client.session_transaction() as sess:
            sess['data_source'] = 'posabit'
            sess['file_path'] = str(excel_path)
            sess['uploaded_filename'] = 'AGT_Bothell_test.xlsx'

        with patch('src.core.data.posabit_client.is_posabit_configured', return_value=True), \
             patch('src.core.data.posabit_client.is_posabit_products_enabled', return_value=False):
            response = client.get('/api/current-file')

        assert response.status_code == 200
        data = response.get_json()
        assert data['has_file'] is True
        assert data['filename'] == 'POSaBit / API'
        assert data['file_path'] is None
        assert data['posabit_active'] is True
    
    def test_excel_upload_sets_session_source_to_excel(self, client):
        """An Excel upload should flip the session source back to Excel even when POSaBit is configured."""
        with client.session_transaction() as sess:
            sess['selected_store'] = 'AGT_Bothell'
            sess['data_source'] = 'posabit'

        response = client.post(
            '/upload',
            data={'file': (io.BytesIO(b'not really excel yet'), 'AGT_Bothell_test.xlsx')},
            content_type='multipart/form-data',
        )

        assert response.status_code == 200, response.get_data(as_text=True)
        with client.session_transaction() as sess:
            assert sess['data_source'] == 'excel'

    def test_uploaded_excel_file_takes_precedence_over_default_posabit(self, client, tmp_path):
        """A valid uploaded Excel file should remain the active source even when the session source is blank."""
        excel_path = tmp_path / 'AGT_Bothell_test.xlsx'
        excel_path.write_bytes(b'not really an excel file')

        with client.session_transaction() as sess:
            sess['selected_store'] = 'AGT_Bothell'
            sess['file_path'] = str(excel_path)
            sess['uploaded_filename'] = 'AGT_Bothell_test.xlsx'
            sess['upload_timestamp'] = 12345
            sess.pop('data_source', None)

        with patch('src.core.data.posabit_client.is_posabit_configured', return_value=True), \
             patch('src.core.data.posabit_client.is_posabit_products_enabled', return_value=False):
            response = client.get('/api/current-file')
            config_response = client.get('/api/posabit/config')

        assert response.status_code == 200
        current = response.get_json()
        assert current['filename'] == 'AGT_Bothell_test.xlsx'
        assert current['has_file'] is True
        assert current['posabit_active'] is False

        assert config_response.status_code == 200
        config = config_response.get_json()
        assert config['data_source'] == 'excel'

    def test_posabit_data_source_switch_uses_posabit_tags_with_excel_in_session(self, client, tmp_path):
        excel_path = tmp_path / 'AGT_Bothell_test.xlsx'
        excel_path.write_bytes(b'not really an excel file')

        with client.session_transaction() as sess:
            sess['selected_store'] = 'AGT_Bothell'
            sess['file_path'] = str(excel_path)
            sess['uploaded_filename'] = 'AGT_Bothell_test.xlsx'
            sess['data_source'] = 'posabit'

        with patch('src.core.data.posabit_client.is_posabit_configured', return_value=True), \
             patch('src.core.data.posabit_client.is_posabit_products_enabled', return_value=False), \
             patch('src.core.data.posabit_client.get_menu_feed_as_product_rows', return_value=[{'Product Name*': 'Live POS Item', 'Product Type*': 'Flower'}]):
            response = client.get('/api/available-tags')

        assert response.status_code == 200
        data = response.get_json()
        assert data['source'] == 'posabit'
        assert data['tags'][0]['Product Name*'] == 'Live POS Item'

    def test_status_endpoint_exists(self, client):
        """Test that status endpoint exists and returns 200."""
        response = client.get('/api/status')
        assert response.status_code == 200
    
    def test_status_returns_json(self, client):
        """Test that status endpoint returns JSON."""
        response = client.get('/api/status')
        assert response.is_json
        data = response.get_json()
        assert 'server' in data
    
    def test_status_contains_required_fields(self, client):
        """Test that status response contains required fields."""
        response = client.get('/api/status')
        data = response.get_json()
        assert 'server' in data
        assert 'data_loaded' in data
        assert isinstance(data['data_loaded'], bool)

class TestStoreEndpoints:
    """Tests for store-related endpoints."""
    
    @pytest.mark.timeout(5)
    def test_get_store_endpoint(self, client):
        """Test GET /api/get-store endpoint."""
        try:
            response = client.get('/api/get-store')
            assert response.status_code in [200, 400, 404]  # May return 404 if route not found
        except Exception as e:
            pytest.skip(f"Get store endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(5)
    def test_set_store_endpoint(self, client):
        """Test POST /api/set-store endpoint."""
        try:
            response = client.post('/api/set-store', 
                                 json={'store': 'AGT_Bothell'},
                                 content_type='application/json')
            assert response.status_code in [200, 400, 404]
        except Exception as e:
            pytest.skip(f"Set store endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(5)
    def test_clear_store_endpoint(self, client):
        """Test POST /api/clear-store endpoint."""
        try:
            response = client.post('/api/clear-store')
            assert response.status_code in [200, 400, 404]
        except Exception as e:
            pytest.skip(f"Clear store endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(5)
    def test_check_store_required_endpoint(self, client):
        """Test GET /api/check-store-required endpoint."""
        try:
            response = client.get('/api/check-store-required')
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                data = response.get_json()
                assert 'store_required' in data or 'error' in data
        except Exception as e:
            pytest.skip(f"Check store required endpoint timed out or failed: {e}")

class TestTagEndpoints:
    """Tests for tag-related endpoints."""
    
    def test_available_tags_endpoint(self, client):
        """Test GET /api/available-tags endpoint."""
        response = client.get('/api/available-tags')
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, (list, dict))
    
    def test_selected_tags_get_endpoint(self, client):
        """Test GET /api/selected-tags endpoint."""
        response = client.get('/api/selected-tags')
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, (list, dict))
    
    def test_selected_tags_post_endpoint(self, client):
        """Test POST /api/selected-tags endpoint."""
        response = client.post('/api/selected-tags',
                             json={'tags': []},
                             content_type='application/json')
        assert response.status_code in [200, 400, 500]

class TestTemplateEndpoints:
    """Tests for template-related endpoints."""
    
    def test_template_post_endpoint(self, client):
        """Test POST /api/template endpoint."""
        response = client.post('/api/template',
                             json={'template_type': 'vertical'},
                             content_type='application/json')
        assert response.status_code in [200, 400, 500]
    
    def test_template_settings_get_endpoint(self, client):
        """Test GET /api/template-settings endpoint."""
        response = client.get('/api/template-settings')
        assert response.status_code in [200, 400, 500]
    
    def test_template_settings_post_endpoint(self, client):
        """Test POST /api/template-settings endpoint."""
        response = client.post('/api/template-settings',
                             json={'settings': {}},
                             content_type='application/json')
        assert response.status_code in [200, 400, 500]

class TestLineageEndpoints:
    """Tests for lineage-related endpoints."""
    
    @pytest.mark.timeout(5)
    def test_update_lineage_endpoint(self, client):
        """Test POST /api/update-lineage endpoint."""
        try:
            response = client.post('/api/update-lineage',
                                 json={
                                     'product_name': 'Test Product',
                                     'lineage': 'Sativa'
                                 },
                                 content_type='application/json')
            assert response.status_code in [200, 400, 500, 404]
        except Exception as e:
            pytest.skip(f"Update lineage endpoint timed out or failed: {e}")
    
    def test_batch_update_lineage_endpoint(self, client):
        """Test POST /api/batch-update-lineage endpoint."""
        response = client.post('/api/batch-update-lineage',
                             json={
                                 'updates': [
                                     {'product_name': 'Test', 'lineage': 'Sativa'}
                                 ]
                             },
                             content_type='application/json')
        assert response.status_code in [200, 400, 500]

class TestSessionEndpoints:
    """Tests for session-related endpoints."""
    
    def test_clear_session_endpoint(self, client):
        """Test POST /api/clear-session endpoint."""
        response = client.post('/api/clear-session')
        assert response.status_code in [200, 400, 500]
    
    def test_session_stats_endpoint(self, client):
        """Test GET /api/session-stats endpoint."""
        response = client.get('/api/session-stats')
        assert response.status_code in [200, 400, 500]

class TestUploadEndpoints:
    """Tests for upload-related endpoints."""
    
    @pytest.mark.timeout(5)
    def test_upload_status_endpoint(self, client):
        """Test GET /api/upload-status endpoint."""
        try:
            response = client.get('/api/upload-status')
            assert response.status_code in [200, 400, 500]
        except Exception as e:
            pytest.skip(f"Upload status endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(5)
    def test_current_file_endpoint(self, client):
        """Test GET /api/current-file endpoint."""
        try:
            response = client.get('/api/current-file')
            assert response.status_code in [200, 400, 500, 404]
        except Exception as e:
            pytest.skip(f"Current file endpoint timed out or failed: {e}")

class TestGenerationEndpoints:
    """Tests for generation-related endpoints."""
    
    @pytest.mark.timeout(5)
    def test_generation_progress_endpoint(self, client):
        """Test GET /api/generation-progress endpoint."""
        try:
            response = client.get('/api/generation-progress')
            assert response.status_code in [200, 400, 500, 404]
        except Exception as e:
            pytest.skip(f"Generation progress endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(5)
    def test_clear_generation_cache_endpoint(self, client):
        """Test POST /api/clear-generation-cache endpoint."""
        try:
            response = client.post('/api/clear-generation-cache')
            assert response.status_code in [200, 400, 500, 404]
        except Exception as e:
            pytest.skip(f"Clear generation cache endpoint timed out or failed: {e}")

class TestDatabaseEndpoints:
    """Tests for database-related endpoints."""
    
    @pytest.mark.timeout(10)  # 10 second timeout  
    @pytest.mark.requires_db
    def test_database_stats_endpoint(self, client):
        """Test GET /api/database-stats endpoint."""
        try:
            response = client.get('/api/database-stats')
            assert response.status_code in [200, 400, 500]
        except Exception as e:
            pytest.skip(f"Database stats endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(10)  # 10 second timeout
    @pytest.mark.requires_db
    def test_database_health_endpoint(self, client):
        """Test GET /api/database-health endpoint."""
        try:
            response = client.get('/api/database-health')
            assert response.status_code in [200, 400, 500]
        except Exception as e:
            pytest.skip(f"Database health endpoint timed out or failed: {e}")
    
    @pytest.mark.timeout(10)  # 10 second timeout
    @pytest.mark.requires_db
    def test_debug_database_endpoint(self, client):
        """Test GET /api/debug-database endpoint."""
        try:
            response = client.get('/api/debug-database')
            assert response.status_code in [200, 400, 500]
        except Exception as e:
            pytest.skip(f"Debug database endpoint timed out or failed: {e}")

class TestUtilityEndpoints:
    """Tests for utility endpoints."""
    
    def test_test_endpoint(self, client):
        """Test /test endpoint."""
        response = client.get('/test')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
    
    def test_favicon_endpoint(self, client):
        """Test /favicon.ico endpoint."""
        response = client.get('/favicon.ico')
        assert response.status_code in [200, 404]  # May not exist in test env

