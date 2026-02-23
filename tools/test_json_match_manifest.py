#!/usr/bin/env python3
"""Test JSON match against a Bamboo manifest URL using UnifiedJSONMatcher."""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

URL = "https://api-trace.getbamboo.com/shared/manifests/json/4jtd4tktnbrv1mtxjzhh47rphbw25rjqgrdAysrllbkf4654j26A4A5bgrrhc9jsjy6f4wdfmzndgl6n4r2w455gnn7cwvcgnr7h3tb5h35A5nk3g8tA4Atwgr2w47cqjbwvgsdfjf32cpj8"

def main():
    from src.core.data.enhanced_json_matcher import UnifiedJSONMatcher
    from src.core.data.excel_processor import ExcelProcessor

    excel_processor = ExcelProcessor()
    matcher = UnifiedJSONMatcher(excel_processor)

    print(f"Fetching and matching: {URL[:80]}...")
    try:
        matched = matcher.fetch_and_match(URL)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if not matched:
        print("No products returned.")
        return 0

    db_like = sum(1 for p in matched if isinstance(p, dict) and (float(p.get("Match_Score") or 0) >= 0.5 or "database" in (p.get("Source") or "").lower()))
    json_fallback = len(matched) - db_like

    print(f"\nTotal returned: {len(matched)}")
    print(f"  DB-like match (score>=0.5): {db_like}")
    print(f"  JSON-derived / low confidence: {json_fallback}")

    print("\n--- First 5 ---")
    for i, p in enumerate(matched[:5]):
        if isinstance(p, dict):
            name = p.get("Product Name*") or p.get("JSON_Item_Name") or "?"
            score = p.get("Match_Score", 0)
            src = p.get("Source") or p.get("Match_Algorithm") or "?"
            print(f"  {i+1}. {str(name)[:55]} | Score={score} | {src}")

    print("\n--- Sample JSON-derived ---")
    n = 0
    for p in matched:
        if n >= 3:
            break
        if isinstance(p, dict) and float(p.get("Match_Score") or 0) < 0.5:
            print(f"  - {str(p.get('Product Name*') or p.get('JSON_Item_Name') or '?')[:55]} | Score={p.get('Match_Score')}")
            n += 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
