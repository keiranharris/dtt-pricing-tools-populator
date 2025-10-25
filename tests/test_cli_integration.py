"""
Integration tests for CLI interface with margin collection.

Tests the complete CLI workflow including margin input validation
following the project constitution principles.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import unittest
from unittest.mock import patch, call
from io import StringIO
import sys

from cli_interface import collect_margin_percentage


class TestCLIIntegration(unittest.TestCase):
    """Test cases for CLI margin collection integration."""
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_margin_percentage_valid_first_try(self, mock_stdout, mock_input):
        """Test successful margin collection on first try."""
        # Mock user input: valid margin percentage
        mock_input.return_value = "45%"
        
        # Call function
        result = collect_margin_percentage()
        
        # Verify return value
        self.assertAlmostEqual(result, 0.45, places=3)
        
        # Verify input was called once
        mock_input.assert_called_once()
        
        # Verify output contains confirmation
        output = mock_stdout.getvalue()
        self.assertIn("Client Margin Configuration", output)
        self.assertIn("✅ Confirmed: 45.0% client margin", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_margin_percentage_retry_on_invalid(self, mock_stdout, mock_input):
        """Test margin collection with retry on invalid input."""
        # Mock user input: first invalid, then valid
        mock_input.side_effect = ["invalid", "42.5%"]
        
        # Call function
        result = collect_margin_percentage()
        
        # Verify return value
        self.assertAlmostEqual(result, 0.425, places=3)
        
        # Verify input was called twice
        self.assertEqual(mock_input.call_count, 2)
        
        # Verify output contains error and retry messages
        output = mock_stdout.getvalue()
        self.assertIn("Invalid margin", output)
        self.assertIn("Please try again", output)
        self.assertIn("✅ Confirmed: 42.5% client margin", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_margin_percentage_out_of_range_retry(self, mock_stdout, mock_input):
        """Test margin collection with out-of-range retry."""
        # Mock user input: out of range, then valid
        mock_input.side_effect = ["70%", "50"]
        
        # Call function
        result = collect_margin_percentage()
        
        # Verify return value
        self.assertAlmostEqual(result, 0.50, places=3)
        
        # Verify input was called twice
        self.assertEqual(mock_input.call_count, 2)
        
        # Verify output contains range error
        output = mock_stdout.getvalue()
        self.assertIn("Invalid margin input", output)
        self.assertIn("✅ Confirmed: 50.0% client margin", output)
    
    @patch('builtins.input')
    def test_collect_margin_percentage_keyboard_interrupt(self, mock_input):
        """Test keyboard interrupt handling during margin collection."""
        # Mock keyboard interrupt
        mock_input.side_effect = KeyboardInterrupt()
        
        # Verify KeyboardInterrupt is re-raised
        with self.assertRaises(KeyboardInterrupt):
            collect_margin_percentage()
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_collect_margin_percentage_multiple_formats(self, mock_stdout, mock_input):
        """Test margin collection accepts various valid formats."""
        test_cases = [
            ("35", 0.35),
            ("65%", 0.65),
            ("42.5", 0.425),
            ("  45  ", 0.45),  # With whitespace
        ]
        
        for input_value, expected_decimal in test_cases:
            with self.subTest(input_value=input_value):
                mock_input.reset_mock()
                mock_stdout.truncate(0)
                mock_stdout.seek(0)
                
                mock_input.return_value = input_value
                result = collect_margin_percentage()
                
                self.assertAlmostEqual(result, expected_decimal, places=3)
                output = mock_stdout.getvalue()
                expected_pct = expected_decimal * 100
                self.assertIn(f"✅ Confirmed: {expected_pct:.1f}% client margin", output)


if __name__ == "__main__":
    unittest.main()