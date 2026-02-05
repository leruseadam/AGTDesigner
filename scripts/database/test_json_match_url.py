#!/usr/bin/env python3
"""
Test JSON match with a Cultivera URL. Ensures every inventory item gets a match.
Usage: python scripts/test_json_match_url.py [url]
Default URL: Cultivera_ORD-30063_422044.json
"""
import os
import sys
import requests

# Project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

# Default test URL from user
DEFAULT_URL = "https://files.cultivera.com/435553542D5753313835/Interop/26/04/1SYBBSFRY4J4WAK3/Cultivera_ORD-30063_422044.json"


def run_test(url: str) -> bool:
    """Run JSON match with URL; return True if every item has a match."""
    # Must run inside Flask app context so session/store and matcher work
    os.chdir(BASE)
    from app import app
    from app import get_session_json_matcher, get_current_store_name

    with app.app_context():
        # Force store so DB is consistent (e.g. Bothell)
        store = get_current_store_name(allow_fallback=True)
        print(f"Store: {store}")
        print(f"Fetching: {url[:80]}...")
        matcher = get_session_json_matcher()
        if not matcher:
            print("ERROR: Could not create JSON matcher")
            return False
        # Simplified matching (same as production)
        matched = matcher.fetch_and_match(url, deduplicate=False)
        if not matched:
            print("ERROR: No matched products returned")
            return False

        # Get item count from URL
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            payload = r.json()
            items = payload.get("inventory_transfer_items", []) if isinstance(payload, dict) else payload
            if isinstance(payload, list):
                items = payload
            item_count = len(items) if items else 0
        except Exception as e:
            print(f"Could not count items from URL: {e}")
            item_count = None

        match_count = len(matched)
        json_column_matches = sum(1 for p in matched if p.get("_match_type", "").startswith("json_column") or p.get("_source") == "JSON Column Match")
        fallbacks = sum(1 for p in matched if (p.get("Source") or "").lower().find("fallback") >= 0 or (p.get("Source") or "").lower().find("json") >= 0 and "Column" not in str(p.get("_source", "")))

        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"  Items in JSON:     {item_count or '?'}")
        print(f"  Matched products:  {match_count}")
        print(f"  JSON column match: {json_column_matches}")
        print("=" * 60)

        if item_count is not None and match_count < item_count:
            print(f"  FAIL: {item_count - match_count} items have no match")
            return False
        if item_count is not None and match_count >= item_count:
            print("  OK: All items have a match.")
        return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    ok = run_test(url)
    sys.exit(0 if ok else 1)
