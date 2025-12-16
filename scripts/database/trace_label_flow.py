#!/usr/bin/env python3
"""
Diagnostic to trace exactly what happens during label generation
"""

def diagnose_label_generation_flow():
    """Check the entire label generation flow to see where the bottleneck is."""
    
    print("=" * 80)
    print("DIAGNOSTIC: TRACING LABEL GENERATION FLOW")
    print("=" * 80)
    
    # Check if app.py has the right detection logic
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Look for key patterns
    patterns_to_check = [
        ('JSON session detection', r'json_matched_cache_key.*session\.get'),
        ('Fuzzy matching call', r'get_products_by_names_with_fuzzy'),
        ('Session check logging', r'SESSION CHECK.*json_matched_cache_key'),
        ('Fuzzy matching condition', r'if is_json_matched_session.*fuzzy'),
        ('Database validation', r'VALIDATION DEBUG.*validate.*normalized tags'),
    ]
    
    print("🔍 CHECKING APP.PY FOR KEY COMPONENTS:")
    print("-" * 50)
    
    import re
    for name, pattern in patterns_to_check:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        status = "✅ FOUND" if matches else "❌ MISSING"
        print(f"{status} {name}")
        if matches and len(matches) == 1:
            print(f"    Sample: {matches[0][:100]}...")
    
    print("\n🔍 CHECKING FOR POTENTIAL BOTTLENECKS:")
    print("-" * 50)
    
    # Look for potential issues
    bottleneck_patterns = [
        ('Early return for JSON sessions', r'if is_json_matched_session.*return'),
        ('Template processor limits', r'CHUNK_SIZE.*=.*\d+'),
        ('Database record filtering', r'valid_db_records.*=.*\[.*record.*for.*record'),
        ('Label generation limits', r'valid_selected_tags.*=.*normalized_tags'),
    ]
    
    for name, pattern in bottleneck_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"⚠️  POTENTIAL ISSUE: {name}")
            for match in matches[:2]:  # Show first 2 matches
                print(f"    {match[:100]}...")
        else:
            print(f"✅ OK: No {name}")
    
    print("\n🔧 WHAT TO CHECK NEXT:")
    print("-" * 50)
    print("""
1. CHECK SESSION DETECTION:
   - Look for "SESSION CHECK: json_matched_cache_key" in your logs
   - Should show: is_json_matched_session = True

2. CHECK FUZZY MATCHING TRIGGER:
   - Look for "JSON SESSION: Using fuzzy matching"
   - Look for "FUZZY MATCHING: Only X/49 exact matches found"

3. CHECK DATABASE RESULTS:
   - Look for "VALIDATION DEBUG: Found X valid records, Y placeholders"
   - Should show more than 18 valid records

4. CHECK LABEL GENERATION:
   - Count actual labels generated vs valid database records
   - Check if template processor is limiting output

MOST LIKELY ISSUES:
- Session not detected as JSON matched (check cache_key)
- Fuzzy matching not being called (check logs)
- Database validation still filtering out results
- Template processor chunking issues
    """)

if __name__ == "__main__":
    diagnose_label_generation_flow()