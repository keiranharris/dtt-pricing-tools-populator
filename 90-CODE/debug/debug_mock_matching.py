#!/usr/bin/env python3
"""
Simple debug script to test field matching with mock constants
"""

import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import xlwings as xw
from field_matcher import scan_worksheet_for_pricing_setup_fields_xlwings, find_matching_fields_in_worksheet

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_field_matching_with_mock_constants():
    """Test field matching with mock constants to isolate the issue"""
    
    # Mock constants - based on what we expect
    mock_constants = {
        'Opportunity ID': 'JO-TBAAAAAAAAAAAAAA',
        'Lead Engagement Partner': 'John Doe',
        'Opportunity Owner': 'Jane Smith', 
        'Engagement Manager': 'Bob Johnson',
        'Location': 'Melbourne',
        'Client Name': 'Test Client',
        'Market Offering': 'Advisory',
        'Service Type': 'Consulting',
        'Product / Material': 'Financial Services',
        'Cost Centre': 'CC123',
        'Estimate Type': 'Fixed Price',
        'Start Date (DD/MM/YY)': '01/01/25',
        'No of Periods (in Weeks)': '12',
        'Opportunity Name': 'Test Opportunity'
    }
    
    print(f"=== MOCK CONSTANTS ({len(mock_constants)} items) ===")
    for key, value in list(mock_constants.items())[:5]:
        print(f"  {key} = {value}")
    
    # Open Excel file  
    print("\n=== OPENING EXCEL FILE ===")
    app = xw.App(visible=False)
    try:
        workbook = app.books.open('../10-LATEST-PRICING-TOOLS/FY26 Low Complexity Pricing Tool v1.2.xlsb')
        worksheet = workbook.sheets['Pricing Setup']
        
        print("\n=== SCANNING WORKSHEET ===")
        cell_locations = scan_worksheet_for_pricing_setup_fields_xlwings(worksheet)
        print(f"Found {len(cell_locations)} potential field locations")
        
        print("\n=== TESTING FIELD MATCHING ===")
        matches = find_matching_fields_in_worksheet(mock_constants, worksheet, threshold=0.65)
        print(f"Field matching result: {len(matches)} matches found")
        
        if matches:
            print("\n=== MATCHED FIELDS ===")
            for field, location in matches.items():
                print(f"  {field} -> {location.cell_reference}: '{location.content}'")
        else:
            print("\n=== NO MATCHES - DEBUGGING ===")
            print("Let's check if any of our mock constants should match what we found:")
            for loc in cell_locations[:10]:
                print(f"\nExcel field: '{loc.content}' at {loc.cell_reference}")
                # Test each mock constant against this cell
                for const_name in mock_constants.keys():
                    from field_matcher import normalize_field_name
                    normalized_const = normalize_field_name(const_name)
                    normalized_excel = normalize_field_name(loc.content)
                    
                    from difflib import SequenceMatcher
                    similarity = SequenceMatcher(None, normalized_const, normalized_excel).ratio()
                    if similarity >= 0.65:
                        print(f"  ✅ SHOULD MATCH '{const_name}' (similarity: {similarity:.2f})")
                        print(f"     Normalized const: '{normalized_const}'")
                        print(f"     Normalized excel: '{normalized_excel}'")
                    elif similarity >= 0.5:  # Show near misses
                        print(f"  ⚠️  Near miss '{const_name}' (similarity: {similarity:.2f})")
    
    finally:
        try:
            workbook.close()
            app.quit()
        except:
            pass

if __name__ == "__main__":
    test_field_matching_with_mock_constants()