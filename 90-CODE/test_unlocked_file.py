#!/usr/bin/env python3
"""
Test Resource Setup on an available (unlocked) file.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_unlocked_file():
    """Test Resource Setup copy on an unlocked file."""
    print("🔍 Testing Resource Setup on Unlocked File")
    print("=" * 50)
    
    try:
        from resource_setup_populator import copy_resource_setup_range
        
        # Use constants file  
        constants_dir = Path(__file__).parent.parent / "00-CONSTANTS"
        constants_file = constants_dir / "lowcomplexity_const_KHv1.xlsx"
        
        # Find an available target file (not locked)
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from constants import OUTPUT_DIRECTORY
        output_dir = Path(OUTPUT_DIRECTORY).expanduser()
        available_files = [f for f in output_dir.glob("*.xlsb") if not f.name.startswith("~$")]
        
        if not available_files:
            print("❌ No unlocked files available")
            return False
            
        # Use the first available file
        target_file = available_files[0]
        print(f"🎯 Testing with: {target_file.name}")
        
        print(f"\n🚀 Attempting Resource Setup copy...")
        
        # Perform the copy
        result = copy_resource_setup_range(
            source_file=constants_file,
            target_file=target_file,
            resource_row_count=7,
            worksheet_name="Resource Setup"
        )
        
        print(f"\n📊 Result:")
        print(f"   Success: {result.success}")
        print(f"   Cells copied: {result.cells_copied}")
        print(f"   Source range: {result.source_range}")
        print(f"   Target range: {result.target_range}")
        print(f"   Time: {result.execution_time:.2f}s")
        
        if result.error_messages:
            print(f"   Errors: {result.error_messages}")
            
        if result.success:
            print(f"\n🎉 SUCCESS! Resource Setup worked correctly!")
            print(f"💡 Open {target_file.name} to see the copied resource data")
        else:
            print(f"\n❌ Copy failed - check errors above")
            
        return result.success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Resource Setup Test on Unlocked File")
    print()
    
    success = test_unlocked_file()
    
    if success:
        print(f"\n✅ Resource Setup is working correctly!")
        print(f"💡 The issue was just the Excel file lock.")
        print(f"💡 Close Excel and try again on your desired file.")
    else:
        print(f"\n❌ There may be other issues to investigate.")
        
    print(f"\n🎯 Test completed")