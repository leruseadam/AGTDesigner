# POSaBit API client for Label Maker
# Replaces Excel product list and manifest with direct API data.
# Docs: https://developer.posabit.com/pos.html

import os
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Cache for product list (avoids refetching 20k+ products on every request). TTL in seconds.
_posabit_product_rows_cache: Optional[List[Dict[str, Any]]] = None
_posabit_product_rows_cache_time: float = 0
POSABIT_PRODUCTS_CACHE_TTL = int(os.environ.get("POSABIT_PRODUCTS_CACHE_TTL", "300"))  # 5 min default


class PosabitAuthError(Exception):
    """Raised when POSaBit API returns 401 Unauthorized or 403 Forbidden."""
    def __init__(self, status: int, message: str = ""):
        self.status = status
        self.message = message or f"HTTP {status}"
        super().__init__(self.message)

# Default base URLs (venue API uses venue token in path: /{venue_token}/v1/...)
POSABIT_STAGING_BASE = "https://staging-app.posabit.com/api"
POSABIT_PRODUCTION_BASE = "https://app.posabit.com/api"

# Menu feed is a single GET with Bearer token (no venue token in path)
MENU_FEED_STAGING = "https://staging-app.posabit.com/api/v1/menu_feeds"
MENU_FEED_PRODUCTION = "https://app.posabit.com/api/v1/menu_feeds"


def _get_config() -> Dict[str, str]:
    """Read POSaBit config from environment (and optional config file)."""
    base = os.environ.get("POSABIT_API_BASE_URL", POSABIT_PRODUCTION_BASE).rstrip("/")
    token = os.environ.get("POSABIT_API_TOKEN", "").strip()
    # Order Pad integration token (from POSaBit Settings > Integrations). When set, used for menu feed / products.
    order_pad_token = os.environ.get("POSABIT_ORDER_PAD_TOKEN", "").strip()
    effective_token = order_pad_token if order_pad_token else token
    feed_key = os.environ.get("POSABIT_MENU_FEED_KEY", "").strip()
    # Venue token may be required for venue-scoped endpoints (manifests, etc.)
    venue_token = os.environ.get("POSABIT_VENUE_TOKEN", effective_token).strip()
    return {
        "base_url": base,
        "token": token,
        "order_pad_token": order_pad_token,
        "effective_token": effective_token,
        "feed_key": feed_key,
        "venue_token": venue_token,
    }


def _http_get(url: str, token: str, timeout: int = 30, query_params: Optional[Dict[str, str]] = None) -> Optional[Dict]:
    """GET URL with Bearer token; return JSON or None. Raises PosabitAuthError on 401/403."""
    import urllib.error
    import urllib.parse
    import urllib.request
    try:
        if query_params:
            parsed = list(urllib.parse.urlparse(url))
            qs = urllib.parse.parse_qs(parsed[4], keep_blank_values=True)
            for k, v in query_params.items():
                if v:
                    qs[k] = [v]
            parsed[4] = urllib.parse.urlencode(qs, doseq=True)
            url = urllib.parse.urlunparse(parsed)
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                logger.warning(f"POSaBit GET {url} returned {resp.status}")
                return None
            import json
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        logger.warning(f"POSaBit request failed: HTTP {e.code} {e.reason}")
        if e.code in (401, 403):
            raise PosabitAuthError(e.code, f"HTTP {e.code}: Unauthorized — check your token and permissions in app.posabit.com")
        return None
    except Exception as e:
        logger.warning(f"POSaBit request failed: {e}")
        return None


def _menu_item_to_product_row(item: Dict, price_variant: Optional[Dict], category_name: str) -> Dict[str, Any]:
    """
    Map one POSaBit menu_item (and optional price variant) to app column names
    (same shape as Excel: Product Name*, Product Type*, Lineage, Product Brand, Price*, etc.).
    """
    name = (item.get("name") or "").strip()
    if price_variant:
        variant_name = (price_variant.get("name") or "").strip()
        if variant_name:
            name = variant_name
    brand = (item.get("brand") or "").strip()
    strain = (item.get("strain") or "").strip()
    product_type = (item.get("product_type") or "").strip()
    flower_type = (item.get("flower_type") or "").strip()

    # Lineage: POSaBit uses flower_type (e.g. Sativa, Indica, Hybrid)
    lineage = flower_type.upper() if flower_type else "HYBRID"
    if lineage and lineage not in ("SATIVA", "INDICA", "HYBRID", "CBD", "MIXED"):
        if "SATIVA" in lineage or "SATIVA" in lineage.upper():
            lineage = "HYBRID/SATIVA"
        elif "INDICA" in lineage or "INDICA" in lineage.upper():
            lineage = "HYBRID/INDICA"
        else:
            lineage = "HYBRID"

    price_val = ""
    weight_val = ""
    unit_type = ""
    if price_variant:
        cents = price_variant.get("price_cents")
        if cents is not None:
            price_val = str(cents / 100.0)
        unit = price_variant.get("unit")
        if unit is not None:
            weight_val = str(unit)
        unit_type = (price_variant.get("unit_type") or "").strip()

    thc_low = (item.get("thc") or {}).get("low") or ""
    thc_high = (item.get("thc") or {}).get("high") or ""
    thc_unit = (item.get("thc") or {}).get("unit_type") or "%"
    cbd_low = (item.get("cbd") or {}).get("low") or ""
    cbd_high = (item.get("cbd") or {}).get("high") or ""
    cbd_unit = (item.get("cbd") or {}).get("unit_type") or "%"

    thc_str = ""
    if thc_low or thc_high:
        thc_str = f"{thc_low or thc_high}-{thc_high or thc_low}".strip("-") + (thc_unit or "")
    cbd_str = ""
    if cbd_low or cbd_high:
        cbd_str = f"{cbd_low or cbd_high}-{cbd_high or cbd_low}".strip("-") + (cbd_unit or "")

    row = {
        "Product Name*": name or "Unknown",
        "ProductName": name or "Unknown",
        "Product Type*": product_type or category_name,
        "Lineage": lineage,
        "Product Brand": brand,
        "Product Strain": strain,
        "Price*": price_val,
        "Price": price_val,
        "Weight*": weight_val,
        "Weight": weight_val,
        "Units": unit_type,
        "THC test result": thc_str,
        "CBD test result": cbd_str,
        "Description": (item.get("description") or "").strip(),
    }
    return row


def _parse_quantity(val: Any) -> Optional[float]:
    """Parse quantity from API (may be int, float, or string like '369.7'). Return None if missing/invalid."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if not (val != val) else None  # reject NaN
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return None


def _inventory_sku_to_product_row(sku: Dict) -> Dict[str, Any]:
    """
    Map one POSaBit venue inventory SKU (from GET /v2/venue/inventories) to app column names.
    Same shape as Excel / menu feed rows.
    """
    name = (sku.get("name") or "").strip() or "Unknown"
    brand = (sku.get("brand") or "").strip()
    vendor = (sku.get("vendor") or "").strip()
    strain = (sku.get("strain") or "").strip()
    product_type = (sku.get("product_type") or sku.get("product_family") or sku.get("category") or "").strip()
    flower_type = (sku.get("flower_type") or "").strip()
    lineage = flower_type.upper() if flower_type else "HYBRID"
    if lineage and lineage not in ("SATIVA", "INDICA", "HYBRID", "CBD", "MIXED"):
        if "SATIVA" in lineage.upper():
            lineage = "HYBRID/SATIVA"
        elif "INDICA" in lineage.upper():
            lineage = "HYBRID/INDICA"
        else:
            lineage = "HYBRID"
    price_cents = sku.get("price") or sku.get("last_price")
    price_val = str(price_cents / 100.0) if price_cents is not None else ""
    unit = sku.get("unit") or ""
    if isinstance(unit, (int, float)):
        unit = str(unit)
    unit = (unit or "").strip()
    thc_str = (sku.get("thc_measure") or "").strip()
    cbd_str = (sku.get("cbd_measure") or "").strip()
    return {
        "Product Name*": name,
        "ProductName": name,
        "Product Type*": product_type or "Uncategorized",
        "Lineage": lineage,
        "Product Brand": brand,
        # Map POSaBit vendor to all common vendor fields used in Excel/database and templates
        "Vendor": vendor,
        "Vendor/Supplier*": vendor,
        "Vendor/Supplier": vendor,
        "ProductVendor": vendor,
        "Product Strain": strain,
        "Price*": price_val,
        "Price": price_val,
        "Weight*": unit,
        "Weight": unit,
        "Units": "",
        "THC test result": thc_str,
        "CBD test result": cbd_str,
        "Description": (sku.get("description") or "").strip(),
    }


def get_venue_inventories_as_product_rows(token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch POSaBit venue inventories (GET /v2/venue/inventories) and return product rows.
    No menu feed key required — uses venue API token only. Use when menu feed returns 0 products
    or set POSABIT_USE_VENUE_INVENTORIES=1 to use this as the product source.
    """
    cfg = _get_config()
    tok = (token or cfg.get("effective_token") or cfg["token"] or cfg["venue_token"]).strip()
    if not tok:
        logger.warning("POSaBit venue inventories: missing POSABIT_API_TOKEN, POSABIT_ORDER_PAD_TOKEN, or POSABIT_VENUE_TOKEN")
        return []
    base = cfg["base_url"].rstrip("/")
    url_template = f"{base}/v2/venue/inventories"
    rows: List[Dict[str, Any]] = []
    page = 1
    per_page = 1000
    max_pages = 50
    include_inactive = os.environ.get("POSABIT_VENUE_INVENTORY_INCLUDE_INACTIVE", "").strip().lower() in ("1", "true", "yes")
    include_zero_qty = os.environ.get("POSABIT_VENUE_INVENTORY_INCLUDE_ZERO_QUANTITY", "").strip().lower() in ("1", "true", "yes")
    while page <= max_pages:
        url = f"{url_template}?page={page}&per_page={per_page}"
        data = _http_get(url, tok)
        if not data:
            break
        inventory = data.get("inventory") or []
        for sku in inventory:
            if not include_inactive and sku.get("active") is False:
                continue
            if not include_zero_qty:
                qty = _parse_quantity(sku.get("quantity_on_hand") or sku.get("sellable_quantity") or sku.get("ecomm_quantity"))
                if qty is None or qty <= 0:
                    continue
            rows.append(_inventory_sku_to_product_row(sku))
        total_pages = data.get("total_pages") or 1
        if page >= total_pages or not inventory:
            break
        page += 1
    logger.info(f"POSaBit venue inventories: loaded {len(rows)} product rows")
    return rows


def get_menu_feed_as_product_rows(feed_key: Optional[str] = None, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch POSaBit product list and return rows with app column names.
    Uses one of two API connections:
    - Menu feed (default): GET /v1/menu_feeds/{feed_key} — requires POSABIT_MENU_FEED_KEY.
    - Venue inventories: GET /v2/venue/inventories — no feed key; uses venue API token only.
    Set POSABIT_USE_VENUE_INVENTORIES=1 to use venue inventories instead of menu feed.
    If menu feed returns 0 products, falls back to venue inventories automatically.
    Result is cached for POSABIT_PRODUCTS_CACHE_TTL seconds (default 300) to avoid refetching 20k+ products.
    """
    global _posabit_product_rows_cache, _posabit_product_rows_cache_time
    now = time.time()
    if _posabit_product_rows_cache is not None and (now - _posabit_product_rows_cache_time) < POSABIT_PRODUCTS_CACHE_TTL:
        logger.info("POSaBit product list: serving %d rows from cache", len(_posabit_product_rows_cache))
        return _posabit_product_rows_cache

    cfg = _get_config()
    tok = (token or cfg.get("effective_token") or cfg["token"]).strip()
    use_venue_inventories = os.environ.get("POSABIT_USE_VENUE_INVENTORIES", "").strip().lower() in ("1", "true", "yes")

    if use_venue_inventories:
        rows = get_venue_inventories_as_product_rows(token)
        if rows:
            _posabit_product_rows_cache = rows
            _posabit_product_rows_cache_time = time.time()
            return rows
        logger.warning("POSaBit venue inventories returned 0 products; trying menu feed as fallback")

    key = (feed_key or cfg["feed_key"]).strip()
    if not key or not tok:
        if use_venue_inventories:
            logger.warning("POSaBit: venue inventories had 0 products and menu feed key/token missing")
            return []
        logger.warning("POSaBit menu feed: missing POSABIT_MENU_FEED_KEY or POSABIT_API_TOKEN/POSABIT_ORDER_PAD_TOKEN")
        return []

    base = MENU_FEED_PRODUCTION if "posabit.com" in cfg["base_url"] and "staging" not in cfg["base_url"] else MENU_FEED_STAGING
    url = f"{base.rstrip('/')}/{key}"
    # Request "Active" product list (app.posabit.com product list filter) so feed returns only active products
    product_list = (os.environ.get("POSABIT_MENU_FEED_PRODUCT_LIST", "Active") or "Active").strip()
    query_params = {"product_list": product_list}
    logger.info("POSaBit menu feed: requesting product_list=%r (Active = active products only)", product_list)
    data = None
    try:
        data = _http_get(url, tok, query_params=query_params)
    except PosabitAuthError:
        # v1 menu feed often rejects venue-scoped tokens (401). Try v2 venue-scoped endpoint.
        api_base = cfg["base_url"].rstrip("/")
        v2_url = f"{api_base}/{tok}/v2/menu_feeds/{key}"
        logger.info("POSaBit v1 menu feed returned 401; trying v2 venue-scoped menu feed")
        data = _http_get(v2_url, tok, query_params=query_params)
    if not data:
        return []

    menu = data.get("menu_feed") or data
    groups = menu.get("menu_groups") or []
    if not groups and isinstance(menu, dict):
        logger.warning(
            "POSaBit menu feed: no menu_groups in response; top-level keys: %s; "
            "ensure the menu feed in app.posabit.com uses the 'Active' product list and has categories with items.",
            list(menu.keys())[:20],
        )
    def _is_active_item(item: Dict) -> bool:
        """Include only items from the Active product list: skip when explicitly inactive."""
        if "active" in item and item.get("active") is False:
            return False
        if "state" in item and (item.get("state") or "").strip().lower() not in ("active", ""):
            return False
        return True

    rows: List[Dict[str, Any]] = []
    for group in groups:
        category_name = (group.get("name") or "").strip() or "Uncategorized"
        items = group.get("menu_items") or []
        for item in items:
            if not _is_active_item(item):
                continue
            prices = item.get("prices") or []
            if not prices:
                rows.append(_menu_item_to_product_row(item, None, category_name))
            else:
                for p in prices:
                    rows.append(_menu_item_to_product_row(item, p, category_name))
    logger.info(f"POSaBit menu feed: loaded {len(rows)} product rows")
    if len(rows) == 0:
        fallback = get_venue_inventories_as_product_rows(token)
        if fallback:
            logger.info("POSaBit: using venue inventories as fallback (menu feed had 0 products)")
            rows = fallback
    _posabit_product_rows_cache = rows
    _posabit_product_rows_cache_time = time.time()
    return rows


def get_manifests_as_inventory_transfer_items(token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch POSaBit manifests and return a single list of items in the same shape as
    inventory_transfer_items (product_name, product_brand, thc_measure, etc.)
    so existing extract_products_from_manifest / JSON matcher can consume them.
    """
    cfg = _get_config()
    tok = (token or cfg["token"] or cfg["venue_token"]).strip()
    if not tok:
        logger.warning("POSaBit manifests: missing POSABIT_API_TOKEN or POSABIT_VENUE_TOKEN")
        return []

    base = cfg["base_url"].rstrip("/")
    # Venue API: GET /v2/venue/manifests (Bearer token identifies venue)
    url = f"{base}/v2/venue/manifests?per_page=100"
    data = _http_get(url, tok)
    if not data:
        return []

    manifests = data.get("manifests") or []
    out: List[Dict[str, Any]] = []
    for m in manifests:
        for mi in m.get("manifest_items") or []:
            # Map to inventory_transfer_items-like keys (see ENHANCED_JSON_FIELD_MAP)
            out.append({
                "product_name": _manifest_item_display_name(mi, m),
                "product_brand": "",  # POSaBit manifest_items don't include brand; can be enriched later
                "brand": "",
                "Quantity*": mi.get("quantity_on_hand") or mi.get("accepted_quantity") or mi.get("supplier_quantity") or "",
                "quantity": mi.get("quantity_on_hand") or mi.get("accepted_quantity") or mi.get("supplier_quantity") or "",
                "THC test result": mi.get("thc_measure") or "",
                "thc_percentage": _parse_thc_cbd(mi.get("thc_measure")),
                "CBD test result": mi.get("cbd_measure") or "",
                "cbd_percentage": _parse_thc_cbd(mi.get("cbd_measure")),
                "Lot Number": mi.get("lot_number") or "",
                "lot_number": mi.get("lot_number") or "",
                "Batch Number": mi.get("batch_number") or "",
                "batch_number": mi.get("batch_number") or "",
                "Room*": mi.get("venue_room") or "",
                "room": mi.get("venue_room") or "",
                "Internal Product Identifier": str(mi.get("inventory_id") or ""),
                "inventory_id": mi.get("inventory_id"),
                "manifest_item_id": mi.get("id"),
            })
    logger.info(f"POSaBit manifests: loaded {len(out)} manifest items")
    return out


def _manifest_item_display_name(mi: Dict, manifest: Dict) -> str:
    """Build a display name for a manifest item (POSaBit doesn't always include product_name)."""
    # If API adds product_name to manifest_items later, use it
    name = (mi.get("product_name") or mi.get("inventory_name") or "").strip()
    if name:
        return name
    inv_id = mi.get("inventory_id")
    return f"Inventory {inv_id}" if inv_id else "Unknown"


def _parse_thc_cbd(measure: Any) -> str:
    """Extract numeric part from e.g. '19.2%' or '0.0%'."""
    if measure is None:
        return ""
    s = str(measure).strip()
    for i, c in enumerate(s):
        if c in "0123456789.":
            continue
        return s[:i] if i else s
    return s


def is_posabit_configured() -> bool:
    """True if POSaBit API token (or Order Pad token) is set and either menu feed key or venue-inventories mode (can use as product source)."""
    cfg = _get_config()
    if not cfg.get("effective_token"):
        return False
    if cfg.get("feed_key"):
        return True
    if os.environ.get("POSABIT_USE_VENUE_INVENTORIES", "").strip().lower() in ("1", "true", "yes"):
        return True
    return False


def is_posabit_products_enabled() -> bool:
    """True if app should use POSaBit for product list instead of Excel (env override)."""
    return os.environ.get("USE_POSABIT_PRODUCTS", "").strip().lower() in ("1", "true", "yes")


def is_posabit_manifests_enabled() -> bool:
    """True if app should use POSaBit for manifest data when no JSON uploaded."""
    return os.environ.get("USE_POSABIT_MANIFESTS", "").strip().lower() in ("1", "true", "yes")
