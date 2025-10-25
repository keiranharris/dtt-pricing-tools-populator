#!/usr/bin/env python3
"""
Comprehensive Resource Setup Debug Script

This script will actually attempt the resource setup copy operation
and show you exactly what happens at each step.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_full_resource_setup_copy():
    """Test the full resource setup copy operation with detailed logging."""
    print("🔍 Full Resource Setup Copy Test")
    print("=" * 60)
    
    try:
        from resource_setup_populator import copy_resource_setup_range
        
        # Test file paths
        constants_dir = Path(__file__).parent.parent / "00-CONSTANTS"
        constants_file = constants_dir / "lowcomplexity_const_KHv1.xlsx"
        
        # Look for a target file in the output directory
        output_dir = Path(__file__).parent.parent / "20-OUTPUT"
        print(f"📁 Looking for target files in: {output_dir}")
        
        if not output_dir.exists():
            print(f"❌ Output directory doesn't exist: {output_dir}")
            return False
            
        # Find the most recent .xlsb file
        xlsb_files = list(output_dir.glob("*.xlsb"))
        if not xlsb_files:
            print("❌ No .xlsb files found in output directory")
            print("💡 Run the main pricing tool accelerator first to create a target file")
            return False
            
        # Use the most recent file
        target_file = max(xlsb_files, key=lambda f: f.stat().st_mtime)
        print(f"🎯 Using target file: {target_file.name}")
        
        print(f"\n🚀 Attempting Resource Setup copy...")
        print(f"   Source: {constants_file}")
        print(f"   Target: {target_file}")
        
        # Perform the copy with detailed logging
        result = copy_resource_setup_range(
            source_file=constants_file,
            target_file=target_file,
            resource_row_count=7,
            worksheet_name="Resource Setup"
        )
        
        if result:
            print(f"\n📊 Copy Result:")
            print(f"   ✅ Success: {result.success}")
            print(f"   📋 Cells copied: {result.cells_copied}")
            print(f"   📍 Source range: {result.source_range}")
            print(f"   📍 Target range: {result.target_range}")
            print(f"   ⏱️ Execution time: {result.execution_time:.2f}s")
            
            if result.error_messages:
                print(f"   ⚠️ Errors: {result.error_messages}")
            
            if result.success:
                print(f"\n🎉 Resource Setup copy completed successfully!")
                print(f"💡 Check your target file - the 'Group 1' rows should now contain actual resource data")
            else:
                print(f"\n❌ Resource Setup copy failed")
                
            return result.success
        else:
            print(f"\n❌ No result returned from copy operation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_target_file_before_after():
    """Show the target file content before and after the operation."""
    print(f"\n🔍 Target File Analysis")
    print("=" * 40)
    
    try:
        import xlwings as xw
        
        # Find target file
        output_dir = Path(__file__).parent.parent / "20-OUTPUT"
        xlsb_files = list(output_dir.glob("*.xlsb"))
        if not xlsb_files:
            print("❌ No target files found")
            return
            
        target_file = max(xlsb_files, key=lambda f: f.stat().st_mtime)
        print(f"📄 Analyzing: {target_file.name}")
        
        with xw.App(visible=False) as app:
            wb = app.books.open(target_file)
            
            if "Resource Setup" not in [ws.name for ws in wb.sheets]:
                print("❌ No 'Resource Setup' worksheet in target file")
                wb.close()
                return
                
            ws = wb.sheets["Resource Setup"]
            
            # Show content in key areas
            print(f"\n📊 Current Resource Setup content:")
            
            # Check rows 1-10
            for row in range(1, 11):
                try:
                    row_data = ws.range(f"B{row}:H{row}").value
                    if row_data and any(cell for cell in row_data):
                        print(f"   Row {row:2d}: {row_data}")
                except:
                    pass
            
            # Check rows 25-35 (around the expected area)  
            print(f"\n📊 Rows 25-35 (expected target area):")
            for row in range(25, 36):
                try:
                    row_data = ws.range(f"B{row}:H{row}").value
                    if row_data and any(cell for cell in row_data):
                        content_preview = ' | '.join(str(cell)[:20] if cell else 'None' for cell in row_data)
                        print(f"   Row {row:2d}: {content_preview}")
                except:
                    pass
                    
            wb.close()
            
    except Exception as e:
        print(f"❌ Target file analysis failed: {e}")

if __name__ == "__main__":
    print("🚀 Resource Setup Comprehensive Debug Test")
    print()
    
    # First analyze the current target file
    debug_target_file_before_after()
    
    # Then test the copy operation
    success = test_full_resource_setup_copy()
    
    # Show updated target file if successful
    if success:
        print(f"\n" + "=" * 60)
        debug_target_file_before_after()
    
    print(f"\n🎯 Test completed {'successfully' if success else 'with issues'}")