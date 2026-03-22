# POSaBit API client for Label Maker
# Replaces Excel product list and manifest with direct API data.
# Docs: https://developer.posabit.com/pos.html

import os
import re
import time
import logging
from typing import List, Dict, Any, Optional

from src.core.utils.product_weight_inference import (
    infer_weight_display_from_texts,
    is_generic_single_unit_weight,
)

logger = logging.getLogger(__name__)

# Explicit POSaBit / JSON keys only — no inference from product type. If the API omits these,
# DOH is filled later from the product database by _align_tags_with_db_lineage (actual DB columns).
# Prefer DOH Compliant (Yes/No) first (same as app._coalesce_doh_from_db_row).
_POSABIT_DOH_KEYS = (
    "DOH Compliant (Yes/No)",
    "DOH Yes/No",
    "DOH yes/no",
    "doh_yes_no",
    "doh_compliant_yes_no",
    "DOH",
    "doh",
    "doh_compliant",
    "DOH Compliant",
    "is_doh",
    "dohStatus",
    "doh_status",
    "compliance_type",
    "wa_doh_compliant",
    "medical_compliance",
)


def _raw_doh_to_compliant_yes_no(val: str) -> str:
    """Match app._doh_value_to_compliant_yes_no: Yes / No / empty for DOH Compliant (Yes/No) column."""
    if not val:
        return ""
    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "nan", "-", "n/a", "undefined"):
        return ""
    u = s.upper()
    if u in ("NO", "N", "FALSE", "F"):
        return "No"
    if ("NON" in u and "DOH" in u) or ("NOT" in u and "DOH" in u):
        return "No"
    if "NON" in u and "COMPLIANT" in u:
        return "No"
    return "Yes"


def _merge_manifest_fields_from_posabit(row: Dict[str, Any], src: Dict[str, Any]) -> None:
    """
    Populate Manifest Ref / Lot fields from POSaBit menu or venue inventory payloads.
    WA retail UIs often show a long numeric manifest ref as 'lot' or transfer id — include all for filtering.
    """
    if not isinstance(row, dict) or not isinstance(src, dict):
        return
    manifest_keys = (
        "manifest_ref_no",
        "manifest_number",
        "manifest_ref",
        "manifest_id",
        "vendor_manifest_id",
        "inventory_transfer_id",
        "transfer_id",
        "external_manifest_id",
        "manifest_number_external",
    )
    mref = None
    for k in manifest_keys:
        v = src.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s and s.lower() not in ("none", "null", "nan", "-", ""):
            mref = s
            break
    lot_raw = src.get("lot_number") or src.get("lot") or src.get("lotNumber") or src.get("lot_id")
    lot_s = str(lot_raw).strip() if lot_raw is not None else ""
    if lot_s and lot_s.lower() not in ("none", "null", "nan", "-"):
        row["Lot Number"] = lot_s
        row["lot_number"] = lot_s
    if mref:
        row["Manifest Ref No"] = mref
        row["manifest_ref_no"] = mref
    elif lot_s:
        # Lot is often the visible manifest ref when POSaBit omits a separate manifest field
        row["Manifest Ref No"] = lot_s
        row["manifest_ref_no"] = lot_s


def _merge_doh_from_posabit_sources(row: Dict[str, Any], *sources: Any) -> None:
    """Set DOH fields on row only when present on API payloads (menu_item, price variant, SKU)."""
    if not isinstance(row, dict):
        return
    for src in sources:
        if not isinstance(src, dict):
            continue
        for key in _POSABIT_DOH_KEYS:
            if key not in src:
                continue
            raw = src.get(key)
            if raw is None:
                continue
            val = str(raw).strip()
            if not val or val.lower() in ("none", "null", "nan"):
                continue
            row["DOH"] = val
            yn = _raw_doh_to_compliant_yes_no(val)
            row["DOH Compliant (Yes/No)"] = yn
            row["DOH Compliant"] = yn
            row["doh"] = val.lower()
            return


# Cache for product list (keyed by store so switching store uses correct feed key). TTL in seconds.
_posabit_product_rows_cache: Dict[str, List[Dict[str, Any]]] = {}
_posabit_product_rows_cache_time: Dict[str, float] = {}
POSABIT_PRODUCTS_CACHE_TTL = int(os.environ.get("POSABIT_PRODUCTS_CACHE_TTL", "300"))  # 5 min default

# Disk cache for POSaBit products — survives server restarts; per-store file when store_name provided.
import json as _json
import pathlib as _pathlib

_DISK_CACHE_DIR = _pathlib.Path(__file__).parent.parent.parent.parent / "uploads" / "cache"
_DISK_CACHE_TTL = int(os.environ.get("POSABIT_DISK_CACHE_TTL", "86400"))  # 24 hour default


def _store_slug(store_name: Optional[str]) -> str:
    """Normalize store name for cache key and filenames (e.g. Bothell -> BOTHELL, None -> _default_)."""
    if not (store_name or "").strip():
        return "_default_"
    return (store_name or "").strip().upper().replace(" ", "_")


def _disk_cache_path(store_name: Optional[str]) -> _pathlib.Path:
    """Path to disk cache file for this store (posabit_products.json or posabit_products_BOTHELL.json)."""
    slug = _store_slug(store_name)
    name = "posabit_products.json" if slug == "_default_" else f"posabit_products_{slug}.json"
    return _DISK_CACHE_DIR / name


def _load_disk_cache(store_name: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Load POSaBit products from disk cache for this store if it exists and is fresh."""
    path = _disk_cache_path(store_name)
    try:
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > _DISK_CACHE_TTL:
            logger.info(f"POSaBit disk cache expired ({path.name}, {age:.0f}s old, TTL={_DISK_CACHE_TTL}s)")
            return None
        rows = _json.loads(path.read_text(encoding="utf-8"))
        logger.info(f"POSaBit disk cache hit: {len(rows)} products for {_store_slug(store_name)} ({age:.0f}s old)")
        return rows
    except Exception as e:
        logger.warning(f"POSaBit disk cache load failed: {e}")
        return None


def _save_disk_cache(rows: List[Dict[str, Any]], store_name: Optional[str] = None) -> None:
    """Persist POSaBit products to disk cache for this store. Never overwrites a larger cache with fewer products."""
    path = _disk_cache_path(store_name)
    try:
        if path.exists():
            try:
                existing = _json.loads(path.read_text(encoding="utf-8"))
                if isinstance(existing, list) and len(existing) > len(rows):
                    logger.info(f"POSaBit disk cache: keeping {len(existing)} products (not overwriting with {len(rows)})")
                    return
            except Exception:
                pass
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(rows, default=str), encoding="utf-8")
        logger.info(f"POSaBit disk cache saved: {len(rows)} products for {_store_slug(store_name)}")
    except Exception as e:
        logger.warning(f"POSaBit disk cache save failed: {e}")


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


def _normalize_posabit_product_type(raw_product_type: str, item_name: str, fallback_category: str) -> str:
    """
    Normalize POSaBit's product_type/category into the app's expected display headers.
    Priority: API type/category fields first, then name only for format-specific indicators
    (pre-roll hyphen format, disposable/AIO branding) that POSaBit stores inconsistently.
    """
    raw = (raw_product_type or "").strip()
    name = (item_name or "").strip()
    cat = (fallback_category or "").strip()

    lower_name = name.lower()
    lower_raw = raw.lower()
    lower_cat = cat.lower()

    # --- API type/category fields first (authoritative) ---
    for s in (lower_raw, lower_cat):
        if not s:
            continue
        if "infused pre-roll" in s or "terp infused pre-roll" in s:
            return "Infused Pre-Roll"
        if "pre-roll" in s or "preroll" in s or "pre roll" in s:
            return "Pre-Roll"
        if "disposable" in s:
            return "Disposable"
        if "vape cartridge" in s or "cartridge" in s or "vape" in s:
            return "Vape Cartridge"
        # RSO must be checked BEFORE generic "extract"/"concentrate" to avoid misclassification
        if (
            "rso" in s
            or "alcohol/ethanol" in s
            or "alcohol ethanol" in s
            or "co2/ethanol" in s
            or "co2 ethanol" in s
            or "co2 tanker" in s
            or "co2 concentrate" in s
        ):
            return "RSO/CO2 Tankers"
        if "concentrate" in s or "extract" in s or "wax" in s or "shatter" in s or "rosin" in s or "resin" in s or "hash" in s or "kief" in s or "distillate" in s:
            return "Concentrate"
        if "capsule" in s:
            return "Capsule"
        if "tincture" in s or "sublingual" in s:
            return "Tincture"
        # Liquid edibles BEFORE generic "edible" — POSaBit often uses "Edible" for oils & drinks
        if (
            "liquid edible" in s
            or "edible liquid" in s
            or "beverage" in s
            or "drink" in s
            or "shot" in s
            or "soda" in s
            or "elixir" in s
            or "syrup" in s
        ):
            return "Edible (Liquid)"
        if "edible" in s or "gummy" in s or "gummi" in s or "candy" in s or "chocolate" in s or "cookie" in s or "brownie" in s:
            return "Edible (Solid)"
        if "topical" in s or "lotion" in s or "salve" in s or "balm" in s or "cream" in s or "patch" in s:
            return "Topical"
        if "flower" in s or "bud" in s or "nug" in s:
            return "Flower"
        if "pre-roll" in s or "preroll" in s:
            return "Pre-Roll"

    # --- Name-based detection only for format indicators POSaBit stores inconsistently ---
    # (pre-roll hyphenation, disposable/AIO branding in product name)
    if "infused pre-roll" in lower_name or ("infused" in lower_name and ("pre-roll" in lower_name or "preroll" in lower_name)):
        return "Infused Pre-Roll"
    if "pre-roll" in lower_name or "preroll" in lower_name or "pre roll" in lower_name:
        return "Pre-Roll"
    if "disposable" in lower_name or " aio" in lower_name or lower_name.endswith(" aio"):
        return "Disposable"
    if "cartridge" in lower_name or " cart " in lower_name or lower_name.endswith(" cart"):
        return "Vape Cartridge"
    if "tincture" in lower_name or "sublingual" in lower_name or " elixir" in lower_name or lower_name.endswith("elixir"):
        return "Tincture"
    if "capsule" in lower_name:
        return "Capsule"
    if re.search(r"\bshot\b|wildside|fizz|beverage|soda|smoothie", lower_name):
        return "Edible (Liquid)"

    # Pass through the raw type if it's meaningful
    return raw or cat or "Uncategorized"


def _get_config(store_name: Optional[str] = None) -> Dict[str, str]:
    """Read POSaBit config from environment. When store_name is set, use that store's menu feed key (POSABIT_MENU_FEED_KEY_<STORE>)."""
    base = os.environ.get("POSABIT_API_BASE_URL", POSABIT_PRODUCTION_BASE).rstrip("/")
    token = os.environ.get("POSABIT_API_TOKEN", "").strip()
    order_pad_token = os.environ.get("POSABIT_ORDER_PAD_TOKEN", "").strip()
    effective_token = order_pad_token if order_pad_token else token
    feed_key = os.environ.get("POSABIT_MENU_FEED_KEY", "").strip()
    # Per-store key: when user selects a store, switch to that store's menu key (no display of key).
    if store_name:
        slug = (store_name or "").upper().replace(" ", "_")
        if slug:
            store_key = os.environ.get(f"POSABIT_MENU_FEED_KEY_{slug}", "").strip()
            if store_key and not store_key.lower().startswith("your_") and "-" in store_key:
                feed_key = store_key
    # If still no feed_key, pick first non-placeholder per-venue key.
    if not feed_key:
        try:
            candidates = []
            for k, v in os.environ.items():
                if not k.startswith("POSABIT_MENU_FEED_KEY_"):
                    continue
                vv = (v or "").strip()
                if not vv or vv.lower().startswith("your_"):
                    continue
                if "-" not in vv:
                    continue
                candidates.append((k, vv))
            if candidates:
                candidates.sort(key=lambda kv: kv[0])
                feed_key = candidates[0][1]
        except Exception:
            pass
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
        # Allow global timeout override to keep UI responsive when POSaBit is slow/unreachable.
        # Default remains 30s unless POSABIT_HTTP_TIMEOUT is set.
        try:
            env_timeout = os.environ.get("POSABIT_HTTP_TIMEOUT", "").strip()
            if env_timeout:
                timeout = int(float(env_timeout))
        except Exception:
            pass
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

    # Lineage defaults should match Excel rules:
    # - Classic types: default to HYBRID when missing/invalid
    # - Non-classic types: default to MIXED when missing/invalid
    # - Normalize SATIVA/INDICA/HYBRID and hybrids
    try:
        from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES
        pt_lower = (product_type or category_name or "").strip().lower()
        is_classic = pt_lower in CLASSIC_TYPES or any(ct in pt_lower for ct in CLASSIC_TYPES)
    except Exception:
        VALID_CLASSIC_LINEAGES = {"SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"}  # fallback
        pt_lower = (product_type or category_name or "").strip().lower()
        is_classic = False

    lineage_raw = (flower_type or "").strip().upper()
    lineage = lineage_raw
    if lineage and lineage not in VALID_CLASSIC_LINEAGES and lineage != "MIXED":
        if "SATIVA" in lineage:
            lineage = "HYBRID/SATIVA"
        elif "INDICA" in lineage:
            lineage = "HYBRID/INDICA"
        elif "CBD" in lineage:
            lineage = "CBD"
        else:
            lineage = ""
    if not lineage:
        lineage = "HYBRID" if is_classic else "MIXED"

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

    # Combine weight + unit_type into a display string (e.g. "1" + "g" -> "1g")
    _unit_display_map = {"g": "g", "gram": "g", "grams": "g", "oz": "oz", "mg": "mg", "ml": "ml", "each": "each"}
    _unit_norm = _unit_display_map.get(unit_type.lower(), unit_type)
    if weight_val and _unit_norm:
        weight_val = f"{weight_val}{_unit_norm}"

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

    normalized_product_type = _normalize_posabit_product_type(product_type, name, category_name)

    row = {
        "Product Name*": name or "Unknown",
        "ProductName": name or "Unknown",
        "Product Type*": normalized_product_type,
        "Lineage": lineage,
        "canonical_lineage": lineage,
        "Product Brand": brand,
        "ProductBrand": brand,
        "productBrand": brand,
        "Product Strain": strain,
        "Price*": price_val,
        "Price": price_val,
        "Weight*": weight_val,
        "Weight": weight_val,
        "CombinedWeight": weight_val,
        "weight_with_units": weight_val,
        "Units": unit_type,
        "THC test result": thc_str,
        "CBD test result": cbd_str,
        "Description": (item.get("description") or "").strip(),
    }
    # Parent menu name + variant name often carry real grams; variant price unit is frequently "1".
    hint = f"{(item.get('name') or '').strip()} {name}".strip()
    if is_generic_single_unit_weight(weight_val):
        inferred = infer_weight_display_from_texts(
            hint, row["Description"], normalized_product_type
        )
        if inferred:
            row["Weight*"] = inferred
            row["Weight"] = inferred
            row["CombinedWeight"] = inferred
            row["weight_with_units"] = inferred
            logger.debug("POSaBit inferred weight for %r: %r -> %r", name, weight_val, inferred)
    _merge_doh_from_posabit_sources(row, item, price_variant or {})
    _merge_manifest_fields_from_posabit(row, item)
    if price_variant and isinstance(price_variant, dict):
        _merge_manifest_fields_from_posabit(row, price_variant)
    # Only infer DOH from product type when the API didn't provide it — and only for
    # High THC / High CBD types where the type name itself signals compliance flavor.
    if not row.get("DOH"):
        pt = normalized_product_type.lower()
        if "high thc" in pt:
            row["DOH"] = "THC"
            row["DOH Compliant (Yes/No)"] = "Yes"
            row["DOH Compliant"] = "Yes"
            row["doh"] = "thc"
        elif "high cbd" in pt:
            row["DOH"] = "CBD"
            row["DOH Compliant (Yes/No)"] = "Yes"
            row["DOH Compliant"] = "Yes"
            row["doh"] = "cbd"
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
    # POSaBit venue API: product_type is often the lineage ("indica","sativa","hybrid").
    # product_family and category have the real type ("Cartridge", "Edible Solid", "Flower", etc.).
    # Prefer product_family > category > product_type for type classification.
    _LINEAGE_AS_TYPE = {"hybrid", "indica", "sativa", "indica_hybrid", "sativa_hybrid",
                        "hybrid_indica", "hybrid_sativa", "cbd"}
    raw_product_type = (sku.get("product_type") or "").strip()
    product_family = (sku.get("product_family") or "").strip()
    category = (sku.get("category") or "").strip()

    if product_family:
        product_type = product_family
    elif category:
        product_type = category
    elif raw_product_type.lower() not in _LINEAGE_AS_TYPE:
        product_type = raw_product_type
    else:
        product_type = "Flower"  # lineage-as-type with no better info → must be flower

    flower_type = (sku.get("flower_type") or raw_product_type or "").strip()

    # Same lineage behavior as Excel (see _menu_item_to_product_row above)
    try:
        from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES
        pt_lower = (product_type or "").strip().lower()
        is_classic = pt_lower in CLASSIC_TYPES or any(ct in pt_lower for ct in CLASSIC_TYPES)
    except Exception:
        VALID_CLASSIC_LINEAGES = {"SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"}  # fallback
        pt_lower = (product_type or "").strip().lower()
        is_classic = False

    lineage_raw = (flower_type or "").strip().upper()
    lineage = lineage_raw
    if lineage and lineage not in VALID_CLASSIC_LINEAGES and lineage != "MIXED":
        if "SATIVA" in lineage:
            lineage = "HYBRID/SATIVA"
        elif "INDICA" in lineage:
            lineage = "HYBRID/INDICA"
        elif "CBD" in lineage:
            lineage = "CBD"
        else:
            lineage = ""
    if not lineage:
        lineage = "HYBRID" if is_classic else "MIXED"

    normalized_product_type = _normalize_posabit_product_type(product_type, name, sku.get("category") or "")
    price_cents = sku.get("price") or sku.get("last_price")
    price_val = str(price_cents / 100.0) if price_cents is not None else ""
    unit = sku.get("unit") or ""
    if isinstance(unit, (int, float)):
        unit = str(unit)
    unit = (unit or "").strip()
    thc_str = (sku.get("thc_measure") or "").strip()
    cbd_str = (sku.get("cbd_measure") or "").strip()
    desc = (sku.get("description") or "").strip()
    row = {
        "Product Name*": name,
        "ProductName": name,
        "Product Type*": normalized_product_type,
        "Lineage": lineage,
        "canonical_lineage": lineage,
        "Product Brand": brand,
        "ProductBrand": brand,
        "productBrand": brand,
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
        "CombinedWeight": unit,
        "weight_with_units": unit,
        "Units": "",
        "THC test result": thc_str,
        "CBD test result": cbd_str,
        "Description": desc,
    }
    if is_generic_single_unit_weight(unit):
        inferred = infer_weight_display_from_texts(name, desc, normalized_product_type)
        if inferred:
            row["Weight*"] = inferred
            row["Weight"] = inferred
            row["CombinedWeight"] = inferred
            row["weight_with_units"] = inferred
            logger.debug("POSaBit venue inferred weight for %r: %r -> %r", name, unit, inferred)
    _merge_doh_from_posabit_sources(row, sku)
    _merge_manifest_fields_from_posabit(row, sku)
    # Only infer DOH from product type for High THC / High CBD names.
    if not row.get("DOH"):
        pt = normalized_product_type.lower()
        if "high thc" in pt:
            row["DOH"] = "THC"
            row["DOH Compliant (Yes/No)"] = "Yes"
            row["DOH Compliant"] = "Yes"
            row["doh"] = "thc"
        elif "high cbd" in pt:
            row["DOH"] = "CBD"
            row["DOH Compliant (Yes/No)"] = "Yes"
            row["DOH Compliant"] = "Yes"
            row["doh"] = "cbd"
    return row


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
    try:
        max_pages = int(float(os.environ.get("POSABIT_MAX_PAGES", "50") or "50"))
    except Exception:
        max_pages = 50
    # Safety/perf guard: venue inventories can be extremely large (tens of thousands of SKUs).
    # To keep the UI responsive, stop once we've collected enough filtered rows.
    try:
        max_rows = int(float(os.environ.get("POSABIT_MAX_PRODUCTS", "3500") or "3500"))
    except Exception:
        max_rows = 3500
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
            if max_rows and len(rows) >= max_rows:
                logger.info(f"POSaBit venue inventories: reached max_rows={max_rows}; stopping early")
                logger.info(f"POSaBit venue inventories: loaded {len(rows)} product rows")
                return rows
        total_pages = data.get("total_pages") or 1
        if page >= total_pages or not inventory:
            break
        page += 1
    logger.info(f"POSaBit venue inventories: loaded {len(rows)} product rows")
    return rows


def get_menu_feed_as_product_rows(
    feed_key: Optional[str] = None,
    token: Optional[str] = None,
    store_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch POSaBit product list and return rows with app column names.
    When store_name is set, uses that store's menu key (POSABIT_MENU_FEED_KEY_<STORE>) — no key displayed in UI.
    Uses one of two API connections:
    - Menu feed (default): GET /v1/menu_feeds/{feed_key} — requires POSABIT_MENU_FEED_KEY or per-store key.
    - Venue inventories: GET /v2/venue/inventories — no feed key; uses venue API token only.
    Set POSABIT_USE_VENUE_INVENTORIES=1 to use venue inventories instead of menu feed.
    If menu feed returns 0 products, falls back to venue inventories automatically.
    Result is cached per store for POSABIT_PRODUCTS_CACHE_TTL seconds (default 300).
    """
    global _posabit_product_rows_cache, _posabit_product_rows_cache_time
    cache_key = _store_slug(store_name)
    now = time.time()
    if cache_key in _posabit_product_rows_cache and (now - _posabit_product_rows_cache_time.get(cache_key, 0)) < POSABIT_PRODUCTS_CACHE_TTL:
        cached = _posabit_product_rows_cache[cache_key]
        logger.info("POSaBit product list: serving %d rows from in-process cache (store=%s)", len(cached), cache_key)
        return cached

    disk_rows = _load_disk_cache(store_name)
    if disk_rows:
        _posabit_product_rows_cache[cache_key] = disk_rows
        _posabit_product_rows_cache_time[cache_key] = now
        return disk_rows

    cfg = _get_config(store_name)
    tok = (token or cfg.get("effective_token") or cfg["token"]).strip()
    use_venue_inventories = os.environ.get("POSABIT_USE_VENUE_INVENTORIES", "").strip().lower() in ("1", "true", "yes")

    if use_venue_inventories:
        rows = get_venue_inventories_as_product_rows(token)
        if rows:
            _posabit_product_rows_cache[cache_key] = rows
            _posabit_product_rows_cache_time[cache_key] = time.time()
            _save_disk_cache(rows, store_name)
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
    _posabit_product_rows_cache[cache_key] = rows
    _posabit_product_rows_cache_time[cache_key] = time.time()
    if rows:
        _save_disk_cache(rows, store_name)
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
        manifest_ref = (
            m.get("reference_number")
            or m.get("ref_no")
            or m.get("ref")
            or m.get("manifest_ref_no")
            or m.get("manifest_number")
            or m.get("number")
            or m.get("id")
            or ""
        )
        for mi in m.get("manifest_items") or []:
            # Map to inventory_transfer_items-like keys (see ENHANCED_JSON_FIELD_MAP)
            out.append({
                "product_name": _manifest_item_display_name(mi, m),
                "product_brand": "",  # POSaBit manifest_items don't include brand; can be enriched later
                "brand": "",
                "Manifest Ref No": str(manifest_ref) if manifest_ref is not None else "",
                "manifest_ref_no": str(manifest_ref) if manifest_ref is not None else "",
                "manifest_id": m.get("id"),
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


def get_cached_product_rows(store_name: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Return cached product rows for this store without triggering a network fetch. None if cache is empty/stale."""
    global _posabit_product_rows_cache, _posabit_product_rows_cache_time
    cache_key = _store_slug(store_name)
    now = time.time()
    if cache_key in _posabit_product_rows_cache and (now - _posabit_product_rows_cache_time.get(cache_key, 0)) < POSABIT_PRODUCTS_CACHE_TTL:
        return _posabit_product_rows_cache[cache_key]
    disk_rows = _load_disk_cache(store_name)
    if disk_rows:
        _posabit_product_rows_cache[cache_key] = disk_rows
        _posabit_product_rows_cache_time[cache_key] = now
        return disk_rows
    return None


def clear_cache(store_name: Optional[str] = None) -> None:
    """Flush in-memory and disk caches for this store (or all stores if store_name is None)."""
    global _posabit_product_rows_cache, _posabit_product_rows_cache_time
    if store_name is None:
        _posabit_product_rows_cache.clear()
        _posabit_product_rows_cache_time.clear()
        # Delete all disk cache files
        try:
            for f in _DISK_CACHE_DIR.glob("posabit_products*.json"):
                try:
                    f.unlink()
                    logger.info(f"POSaBit cache cleared: deleted {f.name}")
                except Exception as e:
                    logger.warning(f"Could not delete {f}: {e}")
        except Exception as e:
            logger.warning(f"POSaBit disk cache clear failed: {e}")
    else:
        cache_key = _store_slug(store_name)
        _posabit_product_rows_cache.pop(cache_key, None)
        _posabit_product_rows_cache_time.pop(cache_key, None)
        path = _disk_cache_path(store_name)
        try:
            if path.exists():
                path.unlink()
                logger.info(f"POSaBit cache cleared: deleted {path.name}")
        except Exception as e:
            logger.warning(f"Could not delete {path}: {e}")
