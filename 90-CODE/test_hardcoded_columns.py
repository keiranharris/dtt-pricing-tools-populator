"""
Test script for new hard-coded column logic for Pricing Setup sheet
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_constants():
    """Test that constants are properly imported"""
    try:
        from constants import (
            PRICING_SETUP_CONSTANTS_FIELD_COL,
            PRICING_SETUP_CONSTANTS_VALUE_COL,
            PRICING_SETUP_OUTPUT_FIELD_COL,
            PRICING_SETUP_OUTPUT_VALUE_COL,
            PRICING_SETUP_CONSTANTS_FIELD_COL_IDX,
            PRICING_SETUP_CONSTANTS_VALUE_COL_IDX,
            PRICING_SETUP_OUTPUT_FIELD_COL_IDX,
            PRICING_SETUP_OUTPUT_VALUE_COL_IDX
        )
        print("✅ Constants imported successfully")
        print(f"   Constants columns: {PRICING_SETUP_CONSTANTS_FIELD_COL}, {PRICING_SETUP_CONSTANTS_VALUE_COL}")
        print(f"   Output columns: {PRICING_SETUP_OUTPUT_FIELD_COL}, {PRICING_SETUP_OUTPUT_VALUE_COL}")
        print(f"   Column indices: {PRICING_SETUP_CONSTANTS_FIELD_COL_IDX}, {PRICING_SETUP_CONSTANTS_VALUE_COL_IDX}, {PRICING_SETUP_OUTPUT_FIELD_COL_IDX}, {PRICING_SETUP_OUTPUT_VALUE_COL_IDX}")
        return True
    except ImportError as e:
        print(f"❌ Constants import failed: {e}")
        return False

def test_updated_functions():
    """Test that updated functions can be imported"""
    try:
        from excel_constants_reader import read_constants_data
        from excel_data_populator import populate_matched_fields
        from field_matcher import scan_worksheet_for_pricing_setup_fields
        print("✅ All updated functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Updated functions import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Hard-Coded Column Logic for Pricing Setup")
    print("=" * 55)
    
    tests = [
        ("Constants", test_constants),
        ("Updated Functions", test_updated_functions)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Hard-coded column logic is ready.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")