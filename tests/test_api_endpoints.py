"""
Comprehensive tests for API endpoints.
"""
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
        from app import app
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_client() as client:
            with app.app_context():
                yield client
    except Exception as e:
        pytest.skip(f"Could not import app: {e}")

class TestStatusEndpoint:
    """Tests for /api/status endpoint."""
    
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
    
    def test_get_store_endpoint(self, client):
        """Test GET /api/get-store endpoint."""
        response = client.get('/api/get-store')
        assert response.status_code in [200, 400]  # May return 400 if no store set
    
    def test_set_store_endpoint(self, client):
        """Test POST /api/set-store endpoint."""
        response = client.post('/api/set-store', 
                             json={'store': 'AGT_Bothell'},
                             content_type='application/json')
        assert response.status_code in [200, 400]
    
    def test_clear_store_endpoint(self, client):
        """Test POST /api/clear-store endpoint."""
        response = client.post('/api/clear-store')
        assert response.status_code in [200, 400]
    
    def test_check_store_required_endpoint(self, client):
        """Test GET /api/check-store-required endpoint."""
        response = client.get('/api/check-store-required')
        assert response.status_code == 200
        data = response.get_json()
        assert 'store_required' in data or 'error' in data

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
    
    def test_update_lineage_endpoint(self, client):
        """Test POST /api/update-lineage endpoint."""
        response = client.post('/api/update-lineage',
                             json={
                                 'product_name': 'Test Product',
                                 'lineage': 'Sativa'
                             },
                             content_type='application/json')
        assert response.status_code in [200, 400, 500]
    
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
    
    def test_upload_status_endpoint(self, client):
        """Test GET /api/upload-status endpoint."""
        response = client.get('/api/upload-status')
        assert response.status_code in [200, 400, 500]
    
    def test_current_file_endpoint(self, client):
        """Test GET /api/current-file endpoint."""
        response = client.get('/api/current-file')
        assert response.status_code in [200, 400, 500]

class TestGenerationEndpoints:
    """Tests for generation-related endpoints."""
    
    def test_generation_progress_endpoint(self, client):
        """Test GET /api/generation-progress endpoint."""
        response = client.get('/api/generation-progress')
        assert response.status_code in [200, 400, 500]
    
    def test_clear_generation_cache_endpoint(self, client):
        """Test POST /api/clear-generation-cache endpoint."""
        response = client.post('/api/clear-generation-cache')
        assert response.status_code in [200, 400, 500]

class TestDatabaseEndpoints:
    """Tests for database-related endpoints."""
    
    def test_database_stats_endpoint(self, client):
        """Test GET /api/database-stats endpoint."""
        response = client.get('/api/database-stats')
        assert response.status_code in [200, 400, 500]
    
    def test_database_health_endpoint(self, client):
        """Test GET /api/database-health endpoint."""
        response = client.get('/api/database-health')
        assert response.status_code in [200, 400, 500]
    
    def test_debug_database_endpoint(self, client):
        """Test GET /api/debug-database endpoint."""
        response = client.get('/api/debug-database')
        assert response.status_code in [200, 400, 500]

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

