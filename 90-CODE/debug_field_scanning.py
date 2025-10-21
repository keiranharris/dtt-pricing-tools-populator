#!/usr/bin/env python3
"""
Debug script to test field scanning with detailed logging
"""

import logging
import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import xlwings as xw
from excel_constants_reader import read_constants_data
from field_matcher import scan_worksheet_for_pricing_setup_fields_xlwings, find_matching_fields_in_worksheet

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_field_scanning():
    """Test the optimized field scanning to see what it finds"""
    
    # Load constants
    print("\n=== LOADING CONSTANTS ===")
    constants_file = Path('../10-LATEST-PRICING-TOOLS/FY26 Low Complexity Pricing Tool v1.2.xlsb')
    constants = read_constants_data(constants_file.parent, constants_file.name)
    print(f"Loaded {len(constants)} constants")
    for i, (key, value) in enumerate(list(constants.items())[:5]):
        print(f"  {key} = {value}")
    
    # Open Excel file
    print("\n=== OPENING EXCEL FILE ===")
    app = xw.App(visible=False)
    try:
        workbook = app.books.open('../10-LATEST-PRICING-TOOLS/FY26 Low Complexity Pricing Tool v1.2.xlsb')
        worksheet = workbook.sheets['Pricing Setup']
        
        print("\n=== SCANNING WORKSHEET ===")
        # Test our optimized scanning
        cell_locations = scan_worksheet_for_pricing_setup_fields_xlwings(worksheet)
        print(f"Found {len(cell_locations)} potential field locations")
        
        if cell_locations:
            print("\n=== FOUND CELL LOCATIONS ===")
            for i, loc in enumerate(cell_locations[:10]):  # Show first 10
                print(f"  {i+1}. {loc.cell_reference}: '{loc.content}'")
        
        print("\n=== TESTING FIELD MATCHING ===")
        # Test field matching
        matches = find_matching_fields_in_worksheet(constants, worksheet, threshold=0.65)
        print(f"Field matching result: {len(matches)} matches found")
        
        if matches:
            print("\n=== MATCHED FIELDS ===")
            for field, location in matches.items():
                print(f"  {field} -> {location.cell_reference}: '{location.content}'")
    
    finally:
        try:
            workbook.close()
            app.quit()
        except:
            pass

if __name__ == "__main__":
    test_field_scanning()