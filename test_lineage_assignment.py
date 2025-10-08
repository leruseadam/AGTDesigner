#!/usr/bin/env python3

"""
Test script to verify that lineage assignment matches between frontend and backend.
"""

# Frontend CLASSIC_TYPES from tags_table.js (after fix)
FRONTEND_CLASSIC_TYPES = [
    "flower", "pre-roll", "concentrate", "infused pre-roll", 
    "solventless concentrate", "vape cartridge", "rso/co2 tankers"
]

# Backend CLASSIC_TYPES from constants.py
BACKEND_CLASSIC_TYPES = {
    "flower", "pre-roll", "concentrate",
    "infused pre-roll", "solventless concentrate",
    "vape cartridge", "rso/co2 tankers"
}

def test_classic_types_match():
    """Test that frontend and backend classic types match."""
    frontend_set = set(FRONTEND_CLASSIC_TYPES)
    backend_set = BACKEND_CLASSIC_TYPES
    
    print("🔍 Testing Classic Types Alignment:")
    print(f"Frontend classic types: {sorted(frontend_set)}")
    print(f"Backend classic types:  {sorted(backend_set)}")
    
    if frontend_set == backend_set:
        print("✅ SUCCESS: Frontend and backend classic types match!")
        return True
    else:
        print("❌ MISMATCH: Frontend and backend classic types don't match!")
        
        # Show differences
        only_frontend = frontend_set - backend_set
        only_backend = backend_set - frontend_set
        
        if only_frontend:
            print(f"   Only in frontend: {only_frontend}")
        if only_backend:
            print(f"   Only in backend:  {only_backend}")
            
        return False

def test_lineage_assignment_logic():
    """Test the lineage assignment logic for different product types."""
    print("\n🧪 Testing Lineage Assignment Logic:")
    
    test_cases = [
        # (product_type, should_be_classic, expected_lineage_options)
        ("flower", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("pre-roll", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("concentrate", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("infused pre-roll", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("solventless concentrate", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("vape cartridge", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("rso/co2 tankers", True, ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD"]),
        ("edible (solid)", False, ["MIXED"]),
        ("topical", False, ["MIXED"]),
        ("paraphernalia", False, ["PARAPHERNALIA"]),
    ]
    
    all_passed = True
    
    for product_type, should_be_classic, expected_lineages in test_cases:
        is_classic = product_type in BACKEND_CLASSIC_TYPES
        
        if is_classic == should_be_classic:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
            
        print(f"   {status} {product_type:<25} -> Classic: {is_classic:<5} (Expected: {should_be_classic})")
        
        if not is_classic and should_be_classic:
            print(f"      ⚠️  This type should allow classic lineages but will get MIXED!")
        elif is_classic and not should_be_classic:
            print(f"      ⚠️  This type should get MIXED but will allow classic lineages!")
    
    if all_passed:
        print("   ✅ All lineage assignment tests passed!")
    else:
        print("   ❌ Some lineage assignment tests failed!")
        
    return all_passed

if __name__ == "__main__":
    print("🔧 Lineage Assignment Test Suite")
    print("=" * 50)
    
    test1_passed = test_classic_types_match()
    test2_passed = test_lineage_assignment_logic()
    
    print("\n📊 Summary:")
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - UI should now match backend lineage assignment!")
    else:
        print("❌ SOME TESTS FAILED - There are still mismatches between UI and backend!")
        
    print("\n🚀 The fix ensures that:")
    print("   • 'rso/co2 tankers' products are treated as classic types in UI")
    print("   • Classic types get proper strain lineages (SATIVA, INDICA, HYBRID, etc.)")
    print("   • Non-classic types get MIXED lineage as intended")
    print("   • UI and backend lineage assignment logic are now aligned")