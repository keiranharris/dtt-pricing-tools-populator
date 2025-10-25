"""
Debug script to inspect actual content in columns E and F of the target Excel file
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def inspect_excel_file():
    """Inspect the actual Excel file to see what's in columns E and F"""
    try:
        # Find the latest created file
        output_dir = Path("20-OUTPUT")
        if not output_dir.exists():
            print("❌ Output directory not found")
            return False
            
        # Get the most recent .xlsb file
        xlsb_files = list(output_dir.glob("*.xlsb"))
        if not xlsb_files:
            print("❌ No .xlsb files found in output directory")
            return False
            
        latest_file = max(xlsb_files, key=lambda f: f.stat().st_mtime)
        print(f"📁 Inspecting: {latest_file.name}")
        
        # Use xlwings to open and inspect the file
        try:
            import xlwings as xw
            
            print("📊 Opening Excel file...")
            app = xw.App(visible=False, add_book=False)
            wb = app.books.open(str(latest_file))
            
            # Check for Pricing Setup worksheet
            if "Pricing Setup" not in [ws.name for ws in wb.sheets]:
                print("❌ 'Pricing Setup' worksheet not found")
                print(f"Available sheets: {[ws.name for ws in wb.sheets]}")
                wb.close()
                app.quit()
                return False
            
            ws = wb.sheets["Pricing Setup"]
            print("✅ Found 'Pricing Setup' worksheet")
            
            # Inspect columns E and F
            print("\n🔍 Inspecting Column E (Field Names):")
            for row in range(1, 21):  # Check first 20 rows
                try:
                    cell_value = ws.range(f"E{row}").value
                    if cell_value:
                        print(f"   E{row}: '{cell_value}'")
                except:
                    continue
            
            print("\n🔍 Inspecting Column F (Field Values):")
            for row in range(1, 21):  # Check first 20 rows
                try:
                    cell_value = ws.range(f"F{row}").value
                    if cell_value:
                        print(f"   F{row}: '{cell_value}'")
                except:
                    continue
                    
            wb.close()
            app.quit()
            return True
            
        except Exception as e:
            print(f"❌ Error inspecting Excel file: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def inspect_constants():
    """Show what constants we're trying to match"""
    try:
        from excel_constants_reader import read_constants_data
        
        constants_dir = Path("00-CONSTANTS")
        filename = "lowcomplexity_const_KHv1.xlsx"
        
        constants = read_constants_data(constants_dir, filename)
        
        print(f"\n📋 Constants we're trying to match ({len(constants)} total):")
        for i, (field, value) in enumerate(constants.items()):
            print(f"   '{field}' → '{value[:50]}{'...' if len(value) > 50 else ''}'")
            if i >= 10:  # Show first 10
                print(f"   ... and {len(constants)-10} more")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading constants: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Inspecting Excel File Content for Field Matching Debug")
    print("=" * 65)
    
    inspect_constants()
    inspect_excel_file()
    
    print("\n💡 Tips:")
    print("   - Look for similar field names between constants and Excel columns")
    print("   - Check if field names have different formatting/punctuation")
    print("   - Consider lowering the similarity threshold if close matches exist")