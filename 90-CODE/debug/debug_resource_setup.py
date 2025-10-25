#!/usr/bin/env python3
"""
Debug script for Resource Setup Population

This script helps diagnose what the Resource Setup function is finding
in your constants file and target file.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_resource_setup():
    """Debug the Resource Setup functionality."""
    print("🔍 Resource Setup Debug Analysis")
    print("=" * 50)
    
    try:
        from resource_setup_populator import (
            find_source_resource_data, 
            find_target_editable_area,
            validate_resource_setup_requirements,
            _has_meaningful_resource_data,
            _is_suitable_target_area
        )
        
        # Test constants file path (adjust as needed)
        constants_dir = Path(__file__).parent.parent / "00-CONSTANTS"
        constants_file = constants_dir / "lowcomplexity_const_KHv1.xlsx"
        
        print(f"📁 Looking for constants file: {constants_file}")
        print(f"📁 Exists: {constants_file.exists()}")
        
        if not constants_file.exists():
            print("❌ Constants file not found. Please check the path.")
            print("💡 Make sure the constants file is in the correct location:")
            print(f"   Expected: {constants_file}")
            return False
        
        # Test with xlwings if available
        try:
            import xlwings as xw
            print("✅ xlwings is available")
            
            print(f"\n🔍 Analyzing constants file...")
            with xw.App(visible=False) as app:
                wb = app.books.open(constants_file)
                
                # Check if Resource Setup worksheet exists
                worksheet_names = [ws.name for ws in wb.sheets]
                print(f"📋 Available worksheets: {worksheet_names}")
                
                if "Resource Setup" not in worksheet_names:
                    print("❌ 'Resource Setup' worksheet not found in constants file")
                    print("💡 Available worksheets listed above")
                    wb.close()
                    return False
                
                # Analyze the Resource Setup worksheet
                ws = wb.sheets["Resource Setup"]
                print(f"\n📊 Analyzing 'Resource Setup' worksheet...")
                
                # Check used range
                used_range = ws.used_range
                if used_range:
                    print(f"📏 Used range: {used_range.address}")
                    print(f"📏 Last row: {used_range.last_cell.row}")
                    print(f"📏 Last column: {used_range.last_cell.column}")
                else:
                    print("❌ No used range found in Resource Setup worksheet")
                
                # Test our source detection function
                print(f"\n🔍 Testing source data detection...")
                source_range = find_source_resource_data(ws, expected_rows=7)
                if source_range:
                    print(f"✅ Found source data range: {source_range}")
                    
                    # Show what data was found
                    try:
                        data = ws.range(source_range).value
                        print(f"📊 Source data preview:")
                        if isinstance(data[0], list):
                            for i, row in enumerate(data[:3]):  # Show first 3 rows
                                print(f"   Row {i+1}: {row}")
                        else:
                            print(f"   Single row: {data}")
                    except Exception as e:
                        print(f"⚠️ Could not read source data: {e}")
                else:
                    print("❌ No source data found by detection function")
                    
                    # Manual inspection of common ranges (focus on C28:H34 per user requirement)
                    print("\n🔍 Manual inspection of common ranges:")
                    test_ranges = ["C28:H34", "B28:H34", "C25:H31", "C30:H36", "D28:I34", "A28:H34"]
                    for range_addr in test_ranges:
                        try:
                            data = ws.range(range_addr).value
                            has_data = _has_meaningful_resource_data(data)
                            print(f"   {range_addr}: {'✅ Has meaningful data' if has_data else '❌ No meaningful data'}")
                            if has_data:
                                print(f"      Preview: {data[0] if data else 'None'}")
                        except Exception as e:
                            print(f"   {range_addr}: ❌ Error reading: {e}")
                
                wb.close()
                
        except ImportError:
            print("❌ xlwings not available - cannot analyze Excel files")
            return False
        except Exception as e:
            print(f"❌ Error analyzing constants file: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the Resource Setup feature."""
    print(f"\n" + "=" * 50)
    print("💡 RESOURCE SETUP USAGE INSTRUCTIONS")
    print("=" * 50)
    print()
    print("1. 📁 Ensure your constants file exists:")
    print("   Location: /00-CONSTANTS/lowcomplexity_const_KHv1.xlsx")
    print("   Worksheet: 'Resource Setup'")
    print()
    print("2. 📊 Resource data should be at the TOP of the Resource Setup worksheet")
    print("   Expected: Rows 1-7 with actual staff/role information")
    print("   NOT: Rows with just 'Group 1', 'Group 2', etc.")
    print()
    print("3. 🚀 Run the main pricing tool accelerator:")
    print("   python3 pricing_tool_accelerator.py")
    print()
    print("4. 🔍 The Resource Setup data will be copied to empty rows in target file")
    print("   Look for: Resource data in rows that previously had 'Group 1' placeholders")
    print()
    print("💡 If it's still not working:")
    print("   - Check that your constants file has a 'Resource Setup' tab")
    print("   - Verify the resource data is at the top of that tab (rows 1-7)")  
    print("   - Make sure the data contains actual names/roles, not just 'Group' text")

if __name__ == "__main__":
    print("🚀 DTT Pricing Tool - Resource Setup Debugger")
    print()
    
    success = debug_resource_setup()
    
    show_usage_instructions()
    
    if success:
        print(f"\n🎉 Debug completed! Check the analysis above.")
    else:
        print(f"\n⚠️ Debug found issues. Please address them and try again.")