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
    monkeypatch.setattr('src.core.data.posabit_client.get_menu_feed_as_product_rows', lambda store_name=None, force_refresh=False: [{"Product Name*": "Fresh Item", "Product Type*": "Flower"}])
    monkeypatch.setattr('src.core.data.posabit_client.get_cached_product_rows', lambda store_name=None: [{"Product Name*": "Old Item", "Product Type*": "Flower"}])

    resp = client.get('/api/available-tags')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['source'] == 'posabit'
    assert data['tags'][0]['Product Name*'] == 'Fresh Item'


def test_posabit_use_venue_inventories_when_env_set(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY_BOTHELL", "feed-bothell")
    monkeypatch.setenv("POSABIT_USE_VENUE_INVENTORIES", "1")
    monkeypatch.delenv("POSABIT_FORCE_VENUE_INVENTORIES", raising=False)
    monkeypatch.delenv("POSABIT_PREFER_MENU_FEED", raising=False)
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: [{"Product Name*": "inventory item"}],
    )
    monkeypatch.setattr(
        "src.core.data.posabit_client._http_get",
        lambda *args, **kwargs: {"menu_feed": {"menu_groups": []}},
    )

    rows = get_menu_feed_as_product_rows(store_name="AGT_Bothell")
    assert len(rows) == 1
    assert rows[0]["Product Name*"] == "inventory item"


def test_posabit_upgrades_small_menu_feed_to_venue_inventory(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.delenv("POSABIT_USE_VENUE_INVENTORIES", raising=False)
    monkeypatch.delenv("POSABIT_PREFER_MENU_FEED", raising=False)
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    def fake_http_get(url, token, timeout=30, query_params=None):
        return {
            "menu_feed": {
                "menu_groups": [{
                    "name": "Featured",
                    "menu_items": [{
                        "name": "Menu item 1",
                        "state": "active",
                        "prices": [{"price_cents": 1999, "unit": "1", "unit_type": "g"}],
                    }],
                }]
            }
        }

    venue_rows = [{"Product Name*": f"SKU {i}", "Product Type*": "Flower"} for i in range(300)]
    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: venue_rows,
    )

    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 300
    assert rows[0]["Product Name*"] == "SKU 0"


def test_posabit_prefers_menu_feed_when_explicitly_requested(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY_BOTHELL", "feed-bothell")
    monkeypatch.setenv("POSABIT_PREFER_MENU_FEED", "1")
    monkeypatch.delenv("POSABIT_USE_VENUE_INVENTORIES", raising=False)
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    def fake_http_get(url, token, timeout=30, query_params=None):
        return {
            "menu_feed": {
                "menu_groups": [{
                    "name": "Featured",
                    "menu_items": [{
                        "name": "Menu item 1",
                        "state": "active",
                        "prices": [{"price_cents": 1999}],
                    }],
                }]
            }
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: [{"Product Name*": "inventory item"}],
    )

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


def test_posabit_falls_back_to_disk_when_live_api_fails(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    import json
    disk_path = tmp_path / "posabit_products.json"
    disk_path.write_text(
        json.dumps([{"Product Name*": "Cached Item", "Product Type*": "Flower"}] * 300),
        encoding="utf-8",
    )

    def failing_http_get(url, token, timeout=30, query_params=None):
        raise ConnectionError("POSaBit unreachable")

    monkeypatch.setattr("src.core.data.posabit_client._http_get", failing_http_get)

    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 300
    assert rows[0]["Product Name*"] == "Cached Item"


def test_posabit_prefers_live_api_over_disk_cache(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    disk_path = tmp_path / "posabit_products.json"
    disk_path.write_text('[{"Product Name*": "Stale Item", "Product Type*": "Flower"}]', encoding="utf-8")

    def fake_http_get(url, token, timeout=30, query_params=None):
        return {
            "menu_feed": {
                "menu_groups": [{
                    "name": "Featured",
                    "menu_items": [{
                        "name": "Fresh Item",
                        "state": "active",
                        "prices": [{"price_cents": 1999, "unit": "1", "unit_type": "g"}],
                    }],
                }]
            }
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)

    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 1
    assert rows[0]["Product Name*"] == "Fresh Item"


def test_posabit_venue_inventory_requests_in_stock_items(monkeypatch):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.delenv("POSABIT_VENUE_INVENTORY_INCLUDE_ZERO_QUANTITY", raising=False)

    seen_urls = []

    def fake_http_get(url, token, timeout=30, query_params=None):
        seen_urls.append(url)
        return {
            "total_records": 2,
            "current_page": 1,
            "total_pages": 1,
            "per_page": 100,
            "inventory": [
                {"name": "In Stock Flower", "active": True, "quantity_on_hand": "4.0", "product_family": "Flower"},
                {"name": "Also In Stock", "active": True, "quantity_on_hand": "1.0", "product_family": "Edible Solid"},
            ],
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    rows = posabit_client.get_venue_inventories_as_product_rows()
    assert any("quantity_on_hand_gt" in url for url in seen_urls)
    assert len(rows) == 2
    assert rows[0]["Product Name*"] == "In Stock Flower"


def test_posabit_keeps_large_cache_when_live_catalog_is_menu_sized(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    import json
    disk_path = tmp_path / "posabit_products.json"
    disk_path.write_text(
        json.dumps([{"Product Name*": f"Cached SKU {i}", "Product Type*": "Flower"} for i in range(400)]),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: [],
    )

    def fake_http_get(url, token, timeout=30, query_params=None):
        return {
            "menu_feed": {
                "menu_groups": [{
                    "name": "Featured",
                    "menu_items": [{
                        "name": "Tiny menu item",
                        "state": "active",
                        "prices": [{"price_cents": 1999}],
                    }],
                }]
            }
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 400
    assert rows[0]["Product Name*"] == "Cached SKU 0"


def test_posabit_ignores_small_disk_cache(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    import json
    disk_path = tmp_path / "posabit_products.json"
    small_cache = [{"Product Name*": f"Old Menu Item {i}", "Product Type*": "Flower"} for i in range(127)]
    disk_path.write_text(json.dumps(small_cache), encoding="utf-8")

    venue_rows = [{"Product Name*": f"SKU {i}", "Product Type*": "Flower"} for i in range(400)]
    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: venue_rows,
    )

    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 400


def test_posabit_store_feed_key_accepts_common_web_aliases(monkeypatch):
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.delenv("POSABIT_ORDER_PAD_TOKEN", raising=False)
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY_BOTHELL", "feed-bothell")
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY", raising=False)
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY_AGT_BOTHELL", raising=False)

    cfg = _get_config("AGT_Bothell")
    assert cfg["feed_key"] == "feed-bothell"
    assert cfg["effective_token"] == "demo-token"


def test_posabit_configured_when_token_present_without_menu_feed_key(monkeypatch):
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY", raising=False)
    monkeypatch.delenv("POSABIT_MENU_FEED_KEY_BOTHELL", raising=False)
    monkeypatch.delenv("POSABIT_PREFER_MENU_FEED", raising=False)
    monkeypatch.delenv("POSABIT_USE_VENUE_INVENTORIES", raising=False)
    assert posabit_client.is_posabit_configured() is True


def test_posabit_disk_cache_save_is_atomic(tmp_path, monkeypatch):
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)
    rows = [{"Product Name*": f"SKU {i}", "Product Type*": "Flower"} for i in range(300)]
    posabit_client._save_disk_cache(rows)
    path = tmp_path / "posabit_products.json"
    assert path.exists()
    assert not (tmp_path / "posabit_products.json.tmp").exists()
    loaded = posabit_client._json.loads(path.read_text(encoding="utf-8"))
    assert len(loaded) == 300


def test_posabit_venue_inventory_fetches_all_pages(monkeypatch):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.delenv("POSABIT_VENUE_INVENTORY_INCLUDE_ZERO_QUANTITY", raising=False)

    from urllib.parse import parse_qs, urlparse

    def fake_http_get(url, token, timeout=30, query_params=None):
        page = int(parse_qs(urlparse(url).query).get("page", ["1"])[0])
        pages = {
            1: {"name": "Page One", "active": True, "quantity_on_hand": "1.0", "product_family": "Flower"},
            2: {"name": "Page Two", "active": True, "quantity_on_hand": "2.0", "product_family": "Flower"},
            3: {"name": "Page Three", "active": True, "quantity_on_hand": "3.0", "product_family": "Flower"},
        }
        sku = pages[page]
        return {
            "total_records": 3,
            "current_page": page,
            "total_pages": 3,
            "per_page": 1,
            "inventory": [sku],
        }

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fake_http_get)
    rows = posabit_client.get_venue_inventories_as_product_rows()
    names = {row["Product Name*"] for row in rows}
    assert names == {"Page One", "Page Two", "Page Three"}


def test_posabit_serves_complete_disk_cache_without_live_fetch(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    import json
    disk_path = tmp_path / "posabit_products.json"
    disk_path.write_text(
        json.dumps([{"Product Name*": f"Cached SKU {i}", "Product Type*": "Flower"} for i in range(400)]),
        encoding="utf-8",
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("live POSaBit fetch should not run when a complete disk cache exists")

    monkeypatch.setattr("src.core.data.posabit_client._http_get", fail_if_called)
    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        fail_if_called,
    )

    rows = get_menu_feed_as_product_rows(force_refresh=False)
    assert len(rows) == 400
    assert rows[0]["Product Name*"] == "Cached SKU 0"


def test_posabit_keeps_larger_cache_when_live_fetch_is_partial(monkeypatch, tmp_path):
    posabit_client._posabit_product_rows_cache.clear()
    posabit_client._posabit_product_rows_cache_time.clear()
    monkeypatch.setenv("POSABIT_API_TOKEN", "demo-token")
    monkeypatch.setenv("POSABIT_MENU_FEED_KEY", "feed-default")
    monkeypatch.setattr(posabit_client, "_DISK_CACHE_DIR", tmp_path)

    import json
    disk_path = tmp_path / "posabit_products.json"
    disk_path.write_text(
        json.dumps([{"Product Name*": f"Cached SKU {i}", "Product Type*": "Flower"} for i in range(400)]),
        encoding="utf-8",
    )

    live_rows = [{"Product Name*": f"Partial SKU {i}", "Product Type*": "Flower"} for i in range(260)]
    monkeypatch.setattr(
        "src.core.data.posabit_client.get_venue_inventories_as_product_rows",
        lambda token=None: live_rows,
    )

    rows = get_menu_feed_as_product_rows(force_refresh=True)
    assert len(rows) == 400
    assert rows[0]["Product Name*"] == "Cached SKU 0"


def test_web_available_tags_slims_posabit_payload(client, monkeypatch):
    with client.session_transaction() as sess:
        sess['data_source'] = 'posabit'
        sess['selected_store'] = 'AGT_Bothell'
        sess.pop('file_path', None)
        sess.pop('default_file_loaded', None)

    fat_row = {
        "Product Name*": "Live POS Item",
        "Product Type*": "Flower",
        "unused_api_blob": "x" * 50,
        "internal_debug": {"nested": True},
    }
    class _EmptyExcel:
        df = None

    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_configured', lambda: True)
    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_products_enabled', lambda: False)
    monkeypatch.setattr(
        'src.core.data.posabit_client.get_menu_feed_as_product_rows',
        lambda store_name=None, force_refresh=False: [fat_row],
    )
    monkeypatch.setattr('src.core.data.posabit_client.get_cached_product_rows', lambda store_name=None: None)
    monkeypatch.setattr('src.core.data.posabit_client.is_incomplete_posabit_catalog', lambda rows: False)
    monkeypatch.setattr('app.get_session_excel_processor', lambda: _EmptyExcel())
    monkeypatch.setattr('app.get_excel_processor', lambda: _EmptyExcel())

    resp = client.get('/api/web/available-tags?nocache=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['source'] == 'posabit'
    assert data['tags'][0]['Product Name*'] == 'Live POS Item'
    assert 'unused_api_blob' not in data['tags'][0]
    assert 'internal_debug' not in data['tags'][0]


def test_web_available_tags_uses_posabit_even_when_excel_is_loaded(client, monkeypatch):
    with client.session_transaction() as sess:
        sess['data_source'] = 'posabit'
        sess['selected_store'] = 'AGT_Bothell'
        sess['file_path'] = '/tmp/old.xlsx'

    class _LoadedExcel:
        df = type('DF', (), {'empty': False})()
        def get_available_tags(self):
            return [{"Product Name*": "Excel Item", "Product Type*": "Flower"}]

    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_configured', lambda: True)
    monkeypatch.setattr('src.core.data.posabit_client.is_posabit_products_enabled', lambda: False)
    monkeypatch.setattr(
        'src.core.data.posabit_client.get_menu_feed_as_product_rows',
        lambda store_name=None, force_refresh=False: [{"Product Name*": "POS Item", "Product Type*": "Flower"}] * 300,
    )
    monkeypatch.setattr('src.core.data.posabit_client.get_cached_product_rows', lambda store_name=None: None)
    monkeypatch.setattr('app.get_session_excel_processor', lambda: _LoadedExcel())
    monkeypatch.setattr('app.get_excel_processor', lambda: _LoadedExcel())

    resp = client.get('/api/web/available-tags?nocache=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['source'] == 'posabit'
    assert data['total_count'] == 300
    assert data['tags'][0]['Product Name*'] == 'POS Item'
