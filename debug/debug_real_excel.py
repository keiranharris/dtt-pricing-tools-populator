"""
Debug script to add logging to see what's happening during field matching
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def debug_with_real_excel():
    """Debug using real Excel file - add logging to see field matching details"""
    try:
        # Test the field matching with debug output
        output_dir = Path("20-OUTPUT")
        xlsb_files = list(output_dir.glob("*.xlsb"))
        if not xlsb_files:
            print("❌ No .xlsb files found. Run the main application first.")
            return False
            
        latest_file = max(xlsb_files, key=lambda f: f.stat().st_mtime)
        print(f"📁 Testing with: {latest_file.name}")
        
        # Get the constants
        from excel_constants_reader import read_constants_data
        constants_dir = Path("00-CONSTANTS")
        filename = "lowcomplexity_const_KHv1.xlsx"
        constants = read_constants_data(constants_dir, filename)
        
        print(f"📋 Constants loaded (showing field names only):")
        for i, field_name in enumerate(constants.keys()):
            print(f"   {i+1}. '{field_name}'")
            
        # Mock CLI data
        cli_data = {
            "Client Name": "TEST",
            "Opportunity Name": "TEST2", 
            "Start Date (DD/MM/YY)": "18/11/25",
            "No of Periods (in Weeks)": "4"
        }
        
        # Merge the data like the real system does
        merged_data = {**constants, **cli_data}
        print(f"\n📊 Total fields to match: {len(merged_data)}")
        
        # Try xlwings approach to see what's in the Excel
        import xlwings as xw
        
        print("\n🔍 Opening Excel to debug field scanning...")
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(str(latest_file))
        ws = wb.sheets["Pricing Setup"]
        
        print("\n📋 Scanning columns E and F for content:")
        found_fields = []
        for row in range(1, 21):  # Check first 20 rows
            e_val = ws.range(f"E{row}").value
            f_val = ws.range(f"F{row}").value
            
            if e_val:
                print(f"   E{row}: '{e_val}'")
                found_fields.append(str(e_val).strip())
            if f_val and f_val != e_val:  # Don't duplicate if same
                print(f"   F{row}: '{f_val}'")
                found_fields.append(str(f_val).strip())
        
        wb.close()
        app.quit()
        
        print(f"\n🎯 Testing field matching manually:")
        from field_matcher import core_string_match, normalize_field_name
        
        # Test a few key fields
        test_fields = ["Opportunity ID", "Client Name", "Location"]
        
        for test_field in test_fields:
            if test_field in merged_data:
                print(f"\n  Testing '{test_field}':")
                test_norm = normalize_field_name(test_field)
                print(f"    Normalized: '{test_norm}'")
                
                best_match = ""
                best_score = 0.0
                
                for found_field in found_fields[:10]:  # Test against first 10 found fields
                    score = core_string_match(test_field, found_field)
                    if score > best_score:
                        best_score = score
                        best_match = found_field
                    if score > 0.1:  # Show any reasonable matches
                        print(f"    vs '{found_field}': {score:.2f}")
                
                print(f"    BEST: '{best_match}' ({best_score:.2f}) {'✅' if best_score >= 0.65 else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging Real Excel Field Matching")
    print("=" * 45)
    
    debug_with_real_excel()