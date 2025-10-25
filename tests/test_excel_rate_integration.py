"""
Unit tests for Excel rate integration module.

Tests Excel file access, worksheet validation, and error handling
following the project constitution principles.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from excel_rate_integration import (
    validate_excel_environment,
    open_excel_file_safely,
    get_worksheet_safely,
    perform_rate_card_calculation,
    validate_rate_card_data,
    ExcelAccessError,
    WorksheetNotFoundError
)


class TestExcelRateIntegration(unittest.TestCase):
    """Test cases for Excel rate integration functionality."""
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', True)
    @patch('excel_rate_integration.xw')
    def test_validate_excel_environment_success(self, mock_xw):
        """Test successful Excel environment validation."""
        # Mock Excel app creation and cleanup
        mock_app = Mock()
        mock_xw.App.return_value = mock_app
        
        result = validate_excel_environment()
        
        self.assertTrue(result)
        mock_xw.App.assert_called_once_with(visible=False, add_book=False)
        mock_app.quit.assert_called_once()
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', False)
    def test_validate_excel_environment_xlwings_unavailable(self):
        """Test Excel environment validation when xlwings unavailable."""
        result = validate_excel_environment()
        
        self.assertFalse(result)
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', True)
    @patch('excel_rate_integration.xw')
    def test_validate_excel_environment_excel_not_available(self, mock_xw):
        """Test Excel environment validation when Excel not installed."""
        # Mock Excel unavailable
        mock_xw.App.side_effect = Exception("Excel not installed")
        
        result = validate_excel_environment()
        
        self.assertFalse(result)
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', False)
    def test_open_excel_file_safely_xlwings_unavailable(self):
        """Test Excel file opening when xlwings unavailable."""
        file_path = Path("test.xlsx")
        
        with self.assertRaises(ExcelAccessError) as context:
            open_excel_file_safely(file_path)
        
        self.assertIn("xlwings is not available", str(context.exception))
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', True)
    def test_open_excel_file_safely_file_not_found(self):
        """Test Excel file opening when file doesn't exist."""
        file_path = Path("nonexistent.xlsx")
        
        with self.assertRaises(ExcelAccessError) as context:
            open_excel_file_safely(file_path)
        
        self.assertIn("Excel file not found", str(context.exception))
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', True)
    @patch('excel_rate_integration.xw')
    def test_open_excel_file_safely_permission_error(self, mock_xw):
        """Test Excel file opening with permission error."""
        file_path = Path("test.xlsx")
        
        # Mock file exists
        with patch.object(file_path, 'exists', return_value=True):
            # Mock permission error
            mock_app = Mock()
            mock_xw.App.return_value = mock_app
            mock_app.books.open.side_effect = PermissionError("Access denied")
            
            with self.assertRaises(ExcelAccessError) as context:
                open_excel_file_safely(file_path)
            
            self.assertIn("Permission denied", str(context.exception))
    
    @patch('excel_rate_integration.XLWINGS_AVAILABLE', True)
    @patch('excel_rate_integration.xw')
    def test_open_excel_file_safely_success(self, mock_xw):
        """Test successful Excel file opening."""
        file_path = Path("test.xlsx")
        mock_workbook = Mock()
        
        # Mock file exists
        with patch.object(file_path, 'exists', return_value=True):
            # Mock successful opening
            mock_app = Mock()
            mock_xw.App.return_value = mock_app
            mock_app.books.open.return_value = mock_workbook
            
            result = open_excel_file_safely(file_path)
            
            self.assertEqual(result, mock_workbook)
            mock_app.books.open.assert_called_once_with(file_path)
    
    def test_get_worksheet_safely_success(self):
        """Test successful worksheet retrieval."""
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.sheets = {"Resource Setup": mock_worksheet}
        
        result = get_worksheet_safely(mock_workbook, "Resource Setup")
        
        self.assertEqual(result, mock_worksheet)
    
    def test_get_worksheet_safely_not_found(self):
        """Test worksheet retrieval when worksheet not found."""
        mock_workbook = Mock()
        mock_sheet1 = Mock()
        mock_sheet1.name = "Sheet1"
        mock_sheet2 = Mock()  
        mock_sheet2.name = "Sheet2"
        mock_workbook.sheets = {"Sheet1": mock_sheet1, "Sheet2": mock_sheet2}
        mock_workbook.sheets.__getitem__.side_effect = KeyError("Resource Setup")
        mock_workbook.sheets.__iter__.return_value = [mock_sheet1, mock_sheet2]
        
        with self.assertRaises(WorksheetNotFoundError) as context:
            get_worksheet_safely(mock_workbook, "Resource Setup")
        
        self.assertIn("Worksheet 'Resource Setup' not found", str(context.exception))
        self.assertIn("Sheet1, Sheet2", str(context.exception))
    
    @patch('excel_rate_integration.validate_excel_environment')
    @patch('excel_rate_integration.open_excel_file_safely')  
    @patch('excel_rate_integration.get_worksheet_safely')
    @patch('excel_rate_integration.read_standard_cost_rates')
    @patch('excel_rate_integration.calculate_engineering_rates')
    @patch('excel_rate_integration.write_engineering_rates')
    def test_perform_rate_card_calculation_success(
        self, mock_write_rates, mock_calc_rates, mock_read_rates,
        mock_get_worksheet, mock_open_file, mock_validate_env
    ):
        """Test successful rate card calculation."""
        # Setup mocks
        mock_validate_env.return_value = True
        mock_workbook = Mock()
        mock_open_file.return_value = mock_workbook
        mock_worksheet = Mock()
        mock_get_worksheet.return_value = mock_worksheet
        
        # Mock standard rates
        from rate_card_calculator import StandardCostRate, EngineeringRate, RateCalculationResult
        mock_standard_rates = [
            StandardCostRate("Level 1", 100.0, 28, True, None, "Q28"),
            StandardCostRate("Level 2", 120.0, 29, True, None, "Q29")
        ]
        mock_read_rates.return_value = mock_standard_rates
        
        # Mock calculation results
        mock_engineering_rates = [
            EngineeringRate("Level 1", 100.0, 0.45, 182, 28, True, None, "O28"),
            EngineeringRate("Level 2", 120.0, 0.45, 218, 29, True, None, "O29")
        ]
        mock_calc_result = RateCalculationResult(mock_engineering_rates, 2, 2, 0, [])
        mock_calc_rates.return_value = mock_calc_result
        
        # Mock write results
        mock_write_rates.return_value = {
            "success": True,
            "written_count": 2,
            "skipped_count": 0,
            "errors": []
        }
        
        # Call function
        result = perform_rate_card_calculation(Path("test.xlsx"), 0.45)
        
        # Verify results
        self.assertTrue(result["success"])
        self.assertEqual(result["standard_rates_found"], 2)
        self.assertEqual(result["successful_calculations"], 2)
        self.assertEqual(result["rates_written"], 2)
        self.assertEqual(len(result["errors"]), 0)
        
        # Verify Excel cleanup
        mock_workbook.save.assert_called_once()
        mock_workbook.close.assert_called_once()
    
    @patch('excel_rate_integration.validate_excel_environment')
    def test_perform_rate_card_calculation_environment_validation_failed(self, mock_validate_env):
        """Test rate card calculation when environment validation fails."""
        mock_validate_env.return_value = False
        
        result = perform_rate_card_calculation(Path("test.xlsx"), 0.45)
        
        self.assertFalse(result["success"])
        self.assertIn("Excel environment validation failed", result["errors"])
    
    @patch('excel_rate_integration.validate_excel_environment')
    @patch('excel_rate_integration.open_excel_file_safely')
    def test_perform_rate_card_calculation_file_access_error(self, mock_open_file, mock_validate_env):
        """Test rate card calculation with file access error."""
        mock_validate_env.return_value = True
        mock_open_file.side_effect = ExcelAccessError("File access denied")
        
        result = perform_rate_card_calculation(Path("test.xlsx"), 0.45)
        
        self.assertFalse(result["success"])
        self.assertIn("Excel access error: File access denied", result["errors"])


if __name__ == "__main__":
    unittest.main()