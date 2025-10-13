#!/usr/bin/env python3
"""
Debug xlwings .xlsb reading capabilities
"""

import xlwings as xw
from pathlib import Path

def debug_xlsb_reading():
    xlsb_file = Path('../10-LATEST-PRICING-TOOLS/FY26 Low Complexity Pricing Tool v1.2.xlsb')
    
    print(f'Testing xlwings with: {xlsb_file}')
    
    try:
        with xw.App(visible=False) as app:
            wb = app.books.open(xlsb_file)
            
            sheet_names = [ws.name for ws in wb.sheets]
            print(f'Available sheets: {sheet_names}')
            
            if 'Pricing Setup' in sheet_names:
                ws = wb.sheets['Pricing Setup']
                print(f'Pricing Setup sheet found')
                
                # Get the used range
                used_range = ws.used_range
                if used_range:
                    print(f'Used range: {used_range.address}')
                    print(f'Last cell: Row {used_range.last_cell.row}, Col {used_range.last_cell.column}')
                    
                    # Sample some cells to see if they have content
                    sample_cells = []
                    for row in range(1, min(21, used_range.last_cell.row + 1)):  # First 20 rows
                        for col in range(1, min(11, used_range.last_cell.column + 1)):  # First 10 cols
                            try:
                                cell_value = ws.range(row, col).value
                                if cell_value and isinstance(cell_value, str) and len(cell_value.strip()) > 3:
                                    cell_ref = ws.range(row, col).get_address(False, False)
                                    sample_cells.append((cell_ref, cell_value.strip()[:50]))  # Truncate long values
                                    
                            except Exception as e:
                                pass
                    
                    print(f'Found {len(sample_cells)} sample cells with string content:')
                    for cell_ref, content in sample_cells[:10]:  # Show first 10
                        print(f'  {cell_ref}: {content}')
                    
                else:
                    print('No used range found!')
                    
            wb.close()
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_xlsb_reading()