"""
Quick test for JSON sibling strain matching (same product line, different strain).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_get_product_line_signature():
    """_get_product_line_signature groups items by vendor, weight, price, type."""
    try:
        from src.core.data.json_matcher import JSONMatcher
    except ImportError:
        from core.data.json_matcher import JSONMatcher
    mock_proc = MagicMock()
    mock_proc.df = None
    matcher = JSONMatcher(mock_proc)
    # Same line: same vendor, weight, price, type
    item1 = {
        "product_name": "Blue Dream 1g Cartridge",
        "vendor": "Acme Cannabis",
        "unit_weight": "1",
        "line_price": "25",
        "inventory_type": "vape cartridge",
    }
    item2 = {
        "product_name": "Wedding Cake 1g Cartridge",
        "vendor": "Acme Cannabis",
        "unit_weight": "1",
        "line_price": "25",
        "inventory_type": "vape cartridge",
    }
    sig1 = matcher._get_product_line_signature(item1)
    sig2 = matcher._get_product_line_signature(item2)
    assert sig1 == sig2, f"Same line should have same signature: {sig1} vs {sig2}"
    print("✓ _get_product_line_signature: same vendor/weight/price/type => same signature")
    # Different weight => different signature
    item3 = {**item1, "unit_weight": "0.5"}
    sig3 = matcher._get_product_line_signature(item3)
    assert sig1 != sig3
    print("✓ _get_product_line_signature: different weight => different signature")


def test_find_cache_product_by_strain_variant():
    """_find_cache_product_by_strain_variant finds same line with given strain in cache."""
    try:
        from src.core.data.json_matcher import JSONMatcher
    except ImportError:
        from core.data.json_matcher import JSONMatcher
    mock_proc = MagicMock()
    mock_proc.df = None
    matcher = JSONMatcher(mock_proc)
    # Mock _sheet_cache with two products: Blue Dream and Wedding Cake (same vendor/weight/type)
    matcher._sheet_cache = [
        {
            "original_name": "blue dream 1g cartridge",
            "vendor": "acme cannabis",
            "Weight*": "1",
            "product_type": "vape cartridge",
            "Description": "Blue Dream 1g Cartridge",
        },
        {
            "original_name": "wedding cake 1g cartridge",
            "vendor": "acme cannabis",
            "Weight*": "1",
            "product_type": "vape cartridge",
            "Description": "Wedding Cake 1g Cartridge",
        },
    ]
    matcher._is_vendor_match = lambda a, b: (a or "").lower() in (b or "").lower() or (b or "").lower() in (a or "").lower()
    template = {"Vendor/Supplier*": "acme cannabis", "Weight*": "1", "Product Type*": "vape cartridge"}
    found = matcher._find_cache_product_by_strain_variant(
        template, "Wedding Cake", "acme cannabis", "1", "vape cartridge"
    )
    assert found is not None
    name_or_desc = (found.get("original_name") or found.get("Description") or "").lower()
    assert "wedding" in name_or_desc and "cake" in name_or_desc
    print("✓ _find_cache_product_by_strain_variant: found Wedding Cake in cache from Blue Dream template")


def test_find_db_product_by_strain_variant():
    """_find_db_product_by_strain_variant queries DB by vendor + strain + weight."""
    try:
        from src.core.data.json_matcher import JSONMatcher
    except ImportError:
        from core.data.json_matcher import JSONMatcher
    mock_proc = MagicMock()
    mock_proc.df = None
    matcher = JSONMatcher(mock_proc)
    # Mock product_db with cursor returning one row
    class MockCursor:
        description = [("id",), ("Product Name*",), ("Vendor/Supplier*",), ("Weight*",), ("Product Type*",), ("Description",)]
        def execute(self, sql, params):
            pass
        def fetchall(self):
            return [(1, "Wedding Cake 1g Cartridge", "Acme Cannabis", "1 g", "Vape Cartridge", "Wedding Cake 1g Cartridge")]
    class MockConn:
        def cursor(self):
            return MockCursor()
    class MockDb:
        def _get_connection(self):
            return MockConn()
    template = {"Vendor/Supplier*": "Acme Cannabis", "Weight*": "1 g", "Product Type*": "Vape Cartridge"}
    found = matcher._find_db_product_by_strain_variant(template, "Wedding Cake", MockDb())
    assert found is not None
    assert "Wedding Cake" in (found.get("Product Name*") or found.get("Description") or "")
    print("✓ _find_db_product_by_strain_variant: found Wedding Cake row from template + strain")


if __name__ == "__main__":
    test_get_product_line_signature()
    test_find_cache_product_by_strain_variant()
    test_find_db_product_by_strain_variant()
    print("\nAll sibling matching tests passed.")
