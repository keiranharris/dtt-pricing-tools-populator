"""
Debug script to test Pricing Setup sheet population workflow
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def debug_constants_reading():
    """Debug constants reading with hard-coded columns"""
    try:
        from excel_constants_reader import read_constants_data
        
        constants_dir = Path("00-CONSTANTS")
        filename = "lowcomplexity_const_KHv1.xlsx"
        
        print(f"📁 Reading constants from: {constants_dir / filename}")
        
        if not (constants_dir / filename).exists():
            print(f"❌ Constants file not found: {constants_dir / filename}")
            return False
            
        constants = read_constants_data(constants_dir, filename)
        
        print(f"✅ Loaded {len(constants)} constants:")
        for i, (field, value) in enumerate(constants.items()):
            if i < 3:  # Show first 3
                print(f"   '{field}' → '{value}'")
            elif i == 3:
                print(f"   ... and {len(constants)-3} more")
                break
        
        return len(constants) > 0
        
    except Exception as e:
        print(f"❌ Constants reading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_field_scanning():
    """Debug field scanning with mock worksheet"""
    try:
        from field_matcher import scan_worksheet_for_pricing_setup_fields_xlwings
        
        # Create a mock worksheet object
        class MockWorksheet:
            def __init__(self):
                self.name = "Pricing Setup"
                self.data = {
                    "E1": "Field Name Header",
                    "F1": "Field Value Header", 
                    "E5": "Client Name:",
                    "F5": "TEST CLIENT",
                    "E6": "Opportunity Name:",
                    "F6": "TEST OPP",
                    "E7": "Start Date:",
                    "F7": "17/11/25"
                }
            
            def range(self, cell_ref):
                class MockRange:
                    def __init__(self, value):
                        self.value = value
                return MockRange(self.data.get(cell_ref))
        
        mock_worksheet = MockWorksheet()
        print("🧪 Testing with mock Pricing Setup worksheet...")
        
        locations = scan_worksheet_for_pricing_setup_fields_xlwings(mock_worksheet)
        
        print(f"✅ Found {len(locations)} potential field locations:")
        for loc in locations[:5]:  # Show first 5
            print(f"   {loc}")
        
        return len(locations) > 0
        
    except Exception as e:
        print(f"❌ Field scanning failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging Pricing Setup Population Workflow")
    print("=" * 55)
    
    tests = [
        ("Constants Reading", debug_constants_reading),
        ("Field Scanning", debug_field_scanning),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Debug Results: {passed}/{len(tests)} components working")
    
    if passed == len(tests):
        print("🎉 All components working! Issue might be in Excel session management.")
    else:
        print("⚠️ Found issues in core components.")