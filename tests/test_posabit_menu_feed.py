import pytest
import sys
from pathlib import Path

import src.core.data.posabit_client as posabit_client
from src.core.data.posabit_client import _get_config, _is_active_item, get_menu_feed_as_product_rows


@pytest.fixture
def client():
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    import importlib

    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])

    from app import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    with app.test_client() as client:
        with app.app_context():
            yield client


def test_available_tags_prefers_live_posabit_feed_over_stale_cache(client, monkeypatch):
    with client.session_transaction() as sess:
        sess['data_source'] = 'posabit'
        sess['selected_store'] = 'AGT_Bothell'

    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_configured', lambda: True)
    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_products_enabled', lambda: False)
    monkeypatch.setattr('src.core.data.posabit_client.get_menu_feed_as_product_rows', lambda store_name=None: [{"Product Name*": "Fresh Item", "Product Type*": "Flower"}])
    monkeypatch.setattr('src.core.data.posabit_client.get_cached_product_rows', lambda store_name=None: [{"Product Name*": "Old Item", "Product Type*": "Flower"}])

    resp = client.get('/api/available-tags')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['source'] == 'posabit'
    assert data['tags'][0]['Product Name*'] == 'Fresh Item'


def test_posabit_prefers_menu_feed_over_venue_inventory_when_feed_key_exists(monkeypatch):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY_BOTHELL", "feed-bothell")
    monkeypatch.setenv("POSABIT_USE_VENUE_INVENTORIES", "1")
    monkeypatch.delenv("POSABIT_FORCE_VENUE_INVENTORIES", raising=False)

    def fake_http_get(url, token, timeout=30, query_params=None):
        assert url.endswith("/feed-bothell") or "/v2/venue/inventories" in url
        return {
            "menu_feed": {
                "menu_groups": [{
                    "name": "Featured",
                    "menu_items": [{
                        "name": "Menu item 1",
                        "state": "active",
                        "prices": [{"price": 1999}],
                    }],
                }]
            }
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    monkeypatch.setattr("src.core.data.posabit_client.get_venue_inventories_as_product_rows", lambda token=None: [{"Product Name*": "inventory item"}])

    rows = get_menu_feed_as_product_rows(store_name="AGT_Bothell")
    assert len(rows) == 1
    assert rows[0]["Product Name*"] == "Menu item 1"


def test_posabit_item_active_states_allow_common_live_states():
    assert _is_active_item({"state": "active"}) is True
    assert _is_active_item({"state": "published"}) is True
    assert _is_active_item({"state": "available"}) is True
    assert _is_active_item({"state": "live"}) is True
    assert _is_active_item({}) is True


def test_posabit_item_active_states_reject_known_inactive_values():
    assert _is_active_item({"state": "inactive"}) is False
    assert _is_active_item({"state": "archived"}) is False
    assert _is_active_item({"state": "paused"}) is False
    assert _is_active_item({"active": False}) is False


def test_posabit_store_feed_key_accepts_common_web_aliases(monkeypatch):
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.delenv("POSABIT_ORDER_PAD_TOKEN", raising=False)
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY_BOTHELL", "feed-bothell")
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY", raising=False)
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY_AGT_BOTHELL", raising=False)

    cfg = _get_config("AGT_Bothell")
    assert cfg["feed_key"] == "feed-bothell"
    assert cfg["effective_token"] == "demo-token"
