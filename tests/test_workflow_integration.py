"""
End-to-end integration tests for complete Feature 006 workflow.

Tests the complete workflow integration including CLI collection,
rate calculation, and Excel integration following project constitution.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import functions to test
from data_population_orchestrator import (
    populate_rate_card_data,
    populate_spreadsheet_data_with_cli_resources_and_rates
)


class TestWorkflowIntegration(unittest.TestCase):
    """Test cases for end-to-end workflow integration."""
    
    @patch('data_population_orchestrator.perform_rate_card_calculation')
    def test_populate_rate_card_data_success(self, mock_perform_calc):
        """Test successful rate card data population."""
        # Mock successful rate calculation
        mock_result = {
            "success": True,
            "successful_calculations": 7,
            "rates_written": 7,
            "client_margin_percent": 45.0,
            "errors": []
        }
        mock_perform_calc.return_value = mock_result
        
        # Call function
        result = populate_rate_card_data(Path("test.xlsb"), 0.45)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["successful_calculations"], 7)
        self.assertEqual(result["rates_written"], 7)
        
        # Verify function was called with correct parameters
        mock_perform_calc.assert_called_once_with(
            excel_file_path=Path("test.xlsb"),
            client_margin_decimal=0.45,
            worksheet_name="Resource Setup"
        )
    
    @patch('data_population_orchestrator.perform_rate_card_calculation')
    def test_populate_rate_card_data_failure(self, mock_perform_calc):
        """Test rate card data population with calculation failure."""
        # Mock failed rate calculation
        mock_result = {
            "success": False,
            "successful_calculations": 0,
            "rates_written": 0,
            "errors": ["Excel access error"]
        }
        mock_perform_calc.return_value = mock_result
        
        # Call function
        result = populate_rate_card_data(Path("test.xlsb"), 0.45)
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertFalse(result["success"])
        self.assertEqual(result["successful_calculations"], 0)
        self.assertIn("Excel access error", result["errors"])
    
    @patch('data_population_orchestrator.logger')
    def test_populate_rate_card_data_import_error(self, mock_logger):
        """Test rate card data population when excel_rate_integration not available."""
        # This test simulates the ImportError that would occur if the module isn't available
        with patch('data_population_orchestrator.perform_rate_calculation', side_effect=ImportError("Module not found")):
            result = populate_rate_card_data(Path("test.xlsb"), 0.45)
        
        # Should return None when module not available
        self.assertIsNone(result)
        
        # Should log warning
        mock_logger.warning.assert_called()
    
    @patch('data_population_orchestrator.populate_spreadsheet_data_with_cli_and_resources')
    @patch('data_population_orchestrator.populate_rate_card_data')
    def test_complete_workflow_with_rate_card(self, mock_rate_card, mock_base_populate):
        """Test complete workflow with rate card enabled."""
        # Mock base population summary
        mock_summary = Mock()
        mock_summary.execution_time_seconds = 2.5
        mock_base_populate.return_value = mock_summary
        
        # Mock successful rate card
        mock_rate_result = {
            "success": True,
            "successful_calculations": 7,
            "rates_written": 7
        }
        mock_rate_card.return_value = mock_rate_result
        
        # Call complete workflow
        result = populate_spreadsheet_data_with_cli_resources_and_rates(
            target_file=Path("test.xlsb"),
            constants_filename="constants.xlsx",
            cli_data={"Client Name": "Test Client"},
            client_margin_decimal=0.45,
            enable_rate_card=True
        )
        
        # Verify base population was called
        mock_base_populate.assert_called_once()
        
        # Verify rate card was called with correct parameters
        mock_rate_card.assert_called_once_with(
            target_file=Path("test.xlsb"),
            client_margin_decimal=0.45
        )
        
        # Verify result is the base summary
        self.assertEqual(result, mock_summary)
    
    @patch('data_population_orchestrator.populate_spreadsheet_data_with_cli_and_resources')
    @patch('data_population_orchestrator.populate_rate_card_data')
    def test_complete_workflow_without_margin(self, mock_rate_card, mock_base_populate):
        """Test complete workflow with no margin provided."""
        # Mock base population summary
        mock_summary = Mock()
        mock_base_populate.return_value = mock_summary
        
        # Call complete workflow without margin
        result = populate_spreadsheet_data_with_cli_resources_and_rates(
            target_file=Path("test.xlsb"),
            constants_filename="constants.xlsx",
            client_margin_decimal=None,  # No margin provided
            enable_rate_card=True
        )
        
        # Verify base population was called
        mock_base_populate.assert_called_once()
        
        # Verify rate card was NOT called (no margin)
        mock_rate_card.assert_not_called()
        
        # Verify result is the base summary
        self.assertEqual(result, mock_summary)
    
    @patch('data_population_orchestrator.populate_spreadsheet_data_with_cli_and_resources')
    @patch('data_population_orchestrator.populate_rate_card_data')
    def test_complete_workflow_rate_card_disabled(self, mock_rate_card, mock_base_populate):
        """Test complete workflow with rate card disabled."""
        # Mock base population summary
        mock_summary = Mock()
        mock_base_populate.return_value = mock_summary
        
        # Call complete workflow with rate card disabled
        result = populate_spreadsheet_data_with_cli_resources_and_rates(
            target_file=Path("test.xlsb"),
            constants_filename="constants.xlsx",
            client_margin_decimal=0.45,
            enable_rate_card=False  # Rate card disabled
        )
        
        # Verify base population was called
        mock_base_populate.assert_called_once()
        
        # Verify rate card was NOT called (disabled)
        mock_rate_card.assert_not_called()
        
        # Verify result is the base summary
        self.assertEqual(result, mock_summary)
    
    @patch('data_population_orchestrator.populate_spreadsheet_data_with_cli_and_resources')
    @patch('data_population_orchestrator.populate_rate_card_data')
    def test_complete_workflow_rate_card_failure(self, mock_rate_card, mock_base_populate):
        """Test complete workflow when rate card fails."""
        # Mock base population summary
        mock_summary = Mock()
        mock_base_populate.return_value = mock_summary
        
        # Mock failed rate card
        mock_rate_result = {
            "success": False,
            "errors": ["Excel access failed"]
        }
        mock_rate_card.return_value = mock_rate_result
        
        # Call complete workflow
        result = populate_spreadsheet_data_with_cli_resources_and_rates(
            target_file=Path("test.xlsb"),
            constants_filename="constants.xlsx",
            client_margin_decimal=0.45,
            enable_rate_card=True
        )
        
        # Verify both functions were called
        mock_base_populate.assert_called_once()
        mock_rate_card.assert_called_once()
        
        # Verify workflow continues despite rate card failure
        self.assertEqual(result, mock_summary)


if __name__ == "__main__":
    unittest.main()