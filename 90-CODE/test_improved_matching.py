"""
Test the improved field matching with asterisks and normalized field names
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_field_normalization():
    """Test the new field normalization logic"""
    try:
        from field_matcher import normalize_field_name, core_string_match
        
        # Test cases that should match
        test_cases = [
            ("Opportunity ID*", "Opportunity ID"),
            ("Opportunity ID*", "Opportunity ID:"),
            ("Lead Engagement Partner*", "Lead Engagement Partner"),
            ("01. Client Name", "Client Name:"),
            ("A. Location", "Location"),
            ("What is the Working Hours Per Day (HPD) assumed for planning the solution and that will be charged to the client?*", "Working Hours Per Day (HPD)"),
        ]
        
        print("🧪 Testing Field Normalization:")
        for source, target in test_cases:
            source_norm = normalize_field_name(source)
            target_norm = normalize_field_name(target)
            similarity = core_string_match(source, target)
            
            print(f"  '{source}' → '{source_norm}'")
            print(f"  '{target}' → '{target_norm}'")
            print(f"  Similarity: {similarity:.2f} ({'✅ MATCH' if similarity >= 0.65 else '❌ NO MATCH'})")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constants_matching():
    """Test matching with real constants"""
    try:
        from excel_constants_reader import read_constants_data
        from field_matcher import core_string_match
        
        constants_dir = Path("00-CONSTANTS")
        filename = "lowcomplexity_const_KHv1.xlsx"
        constants = read_constants_data(constants_dir, filename)
        
        # Mock target fields that might be in Excel
        mock_target_fields = [
            "Opportunity ID:",
            "Lead Engagement Partner:",
            "Opportunity Owner:",
            "Client Name:",
            "Location:",
            "Service Type:",
            "Working Hours Per Day (HPD)",
        ]
        
        print("🎯 Testing Real Constants Matching:")
        matches_found = 0
        
        for const_field in list(constants.keys())[:7]:  # Test first 7
            best_match = ""
            best_score = 0.0
            
            for target_field in mock_target_fields:
                score = core_string_match(const_field, target_field)
                if score > best_score:
                    best_score = score
                    best_match = target_field
            
            match_status = "✅ MATCH" if best_score >= 0.65 else "❌ NO MATCH"
            print(f"  '{const_field}' → '{best_match}' ({best_score:.2f}) {match_status}")
            
            if best_score >= 0.65:
                matches_found += 1
        
        print(f"\n📊 Results: {matches_found}/7 constants would match with new logic")
        return matches_found > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Improved Field Matching Logic")
    print("=" * 50)
    
    tests = [
        ("Field Normalization", test_field_normalization),
        ("Constants Matching", test_constants_matching),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Improved matching should work better now!")
    else:
        print("⚠️ Still some issues to resolve.")