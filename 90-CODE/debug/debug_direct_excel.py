#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
import xlwings as xw
from pathlib import Path

# Test direct Excel manipulation
print("🔧 Testing direct Excel access...")

file_path = Path("~/Library/CloudStorage/OneDrive-SharedLibraries-Deloitte(O365D)/AU CBO Practice - MO - Cloud Network & Security/_PRESALES/_PROPOSALS/_PricingToolAccel/20-OUTPUT/20251025 - FINALTest - FinalOneDriveTest - (LowCompV1.2).xlsb").expanduser()

print(f"📄 File: {file_path}")
print(f"📄 Exists: {file_path.exists()}")

if file_path.exists():
    try:
        print("🔍 Opening Excel file...")
        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(str(file_path))
        
        # Check Pricing Setup worksheet
        print("\n📋 Pricing Setup worksheet:")
        pricing_ws = wb.sheets['Pricing Setup']
        
        # Check a few key fields we know should be populated
        test_cells = [
            ('I18', 'Client Name'),
            ('I19', 'Opportunity Name'), 
            ('I20', 'Start Date'),
            ('I21', 'Duration'),
        ]
        
        for cell, description in test_cells:
            try:
                value = pricing_ws.range(cell).value
                print(f"  {cell} ({description}): '{value}'")
            except Exception as e:
                print(f"  {cell} ({description}): ERROR - {e}")
        
        # Check some constants fields
        print("\n📊 Constants fields:")
        constants_cells = [
            ('I30', 'Opportunity ID'),
            ('I31', 'Lead Engagement Partner'),
            ('I32', 'Opportunity Owner'),
        ]
        
        for cell, description in constants_cells:
            try:
                value = pricing_ws.range(cell).value
                print(f"  {cell} ({description}): '{value}'")
            except Exception as e:
                print(f"  {cell} ({description}): ERROR - {e}")
        
        wb.close()
        app.quit()
        print("✅ Excel inspection complete")
        
    except Exception as e:
        print(f"❌ Error inspecting Excel file: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ File not found!")