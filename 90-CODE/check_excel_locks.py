#!/usr/bin/env python3
"""
Check for Excel file lock issues and show available target files.
"""

from pathlib import Path

def check_target_files() -> None:
    """Check for target files and Excel lock issues."""
    print("🔍 Checking Target Files")
    print("=" * 40)
    
    output_dir = Path(__file__).parent.parent / "20-OUTPUT"
    print(f"📁 Output directory: {output_dir}")
    print(f"📁 Directory exists: {output_dir.exists()}")
    
    if not output_dir.exists():
        print("❌ Output directory not found")
        return
    
    # Check all Excel files
    excel_files = list(output_dir.glob("*.xlsx")) + list(output_dir.glob("*.xlsb"))
    
    print(f"\n📊 Found {len(excel_files)} Excel files:")
    
    locked_files = []
    available_files = []
    
    for file in excel_files:
        if file.name.startswith("~$"):
            locked_files.append(file)
            print(f"🔒 LOCKED: {file.name}")
        else:
            available_files.append(file)
            print(f"✅ Available: {file.name}")
    
    if locked_files:
        print(f"\n⚠️  ISSUE DETECTED:")
        print(f"Found {len(locked_files)} locked Excel files (starting with ~$)")
        print(f"These indicate Excel files are currently OPEN.")
        print(f"\n💡 SOLUTION:")
        print(f"1. Close Excel completely")
        print(f"2. The ~$ files should disappear automatically") 
        print(f"3. Then run the pricing tool accelerator again")
        print(f"\nLocked files to close:")
        for file in locked_files:
            original_name = file.name[2:]  # Remove ~$ prefix
            print(f"   📄 Close: {original_name}")
    
    if available_files:
        print(f"\n✅ Available files for Resource Setup:")
        for file in available_files:
            print(f"   📄 {file.name}")
    else:
        print(f"\n❌ No available Excel files found")
        print(f"💡 Run the main pricing tool accelerator first to create a target file")

if __name__ == "__main__":
    print("🚀 Excel File Lock Checker")
    print()
    check_target_files()
    print(f"\n🎯 Check complete")