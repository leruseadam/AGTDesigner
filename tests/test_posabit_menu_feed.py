from src.core.data.posabit_client import _is_active_item


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
