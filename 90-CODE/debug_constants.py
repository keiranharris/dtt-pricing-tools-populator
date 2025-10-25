#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from excel_constants_reader import read_constants_data
from logging_config import configure_logging

configure_logging(verbose_enabled=True)

# Test reading constants from OneDrive location
onedrive_constants = Path("~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/00-CONSTANTS").expanduser()

print(f"📁 Constants directory: {onedrive_constants}")
print(f"📁 Directory exists: {onedrive_constants.exists()}")

if onedrive_constants.exists():
    constants_file = onedrive_constants / "lowcomplexity_const_KHv1.xlsx"
    print(f"📄 Constants file: {constants_file}")
    print(f"📄 File exists: {constants_file.exists()}")
    
    if constants_file.exists():
        print("🔍 Reading constants...")
        try:
            constants = read_constants_data(onedrive_constants, "lowcomplexity_const_KHv1.xlsx")
            print(f"✅ Successfully read {len(constants)} constants")
            print("📋 Sample constants:")
            for i, (key, value) in enumerate(constants.items()):
                if i < 5:  # Show first 5
                    print(f"   {key}: {value}")
                if i >= 4:
                    print(f"   ... and {len(constants) - 5} more")
                    break
        except Exception as e:
            print(f"❌ Error reading constants: {e}")
            import traceback
            traceback.print_exc()
