"""
Debug the field matching logic with hard-coded columns
"""

import sys
from pathlib import Path

# Add src to path  
sys.path.append(str(Path(__file__).parent / 'src'))

def test_field_matching():
    """Test field matching with sample data"""
    try:
        from data_models import CellLocation, FieldMatch
        from field_matcher import core_string_match, _is_potential_field_name
        
        print("✅ Imports successful")
        
        # Test CellLocation creation
        location = CellLocation(row=5, column=6, cell_reference="F5", content="Client Name:")
        print(f"✅ CellLocation created: {location}")
        
        # Test field matching
        score = core_string_match("Client Name", "Client Name:")
        print(f"✅ String matching works: {score:.2f}")
        
        # Test potential field detection
        is_field = _is_potential_field_name("Client Name:")
        print(f"✅ Field detection works: {is_field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constants_import():
    """Test constants import"""
    try:
        from constants import (
            PRICING_SETUP_OUTPUT_FIELD_COL_IDX,
            PRICING_SETUP_OUTPUT_VALUE_COL_IDX
        )
        print(f"✅ Constants imported: {PRICING_SETUP_OUTPUT_FIELD_COL_IDX}, {PRICING_SETUP_OUTPUT_VALUE_COL_IDX}")
        return True
    except Exception as e:
        print(f"❌ Constants import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Field Matching Logic")
    print("=" * 40)
    
    tests = [
        ("Constants Import", test_constants_import),
        ("Field Matching", test_field_matching),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed.")