"""
Unit tests for margin_validator module.

Tests margin input validation, decimal conversion, and error handling
following the project constitution principles.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import unittest
from margin_validator import (
    validate_margin_input, 
    convert_margin_to_decimal,
    get_margin_prompt_text,
    get_margin_error_help,
    MarginValidationResult
)


class TestMarginValidator(unittest.TestCase):
    """Test cases for margin validation functionality."""
    
    def test_validate_margin_input_valid_cases(self):
        """Test valid margin input cases."""
        # Test various valid formats
        test_cases = [
            ("35", 0.35),
            ("65", 0.65),
            ("45", 0.45),
            ("35%", 0.35),
            ("65%", 0.65),
            ("45%", 0.45),
            ("35.0", 0.35),
            ("45.5", 0.455),
            ("45.5%", 0.455),
            ("  45  ", 0.45),  # Whitespace
            ("  45%  ", 0.45),  # Whitespace with %
        ]
        
        for input_value, expected_decimal in test_cases:
            with self.subTest(input_value=input_value):
                result = validate_margin_input(input_value)
                self.assertTrue(result.is_valid, f"Expected {input_value} to be valid")
                self.assertAlmostEqual(result.decimal_value, expected_decimal, places=3)
                self.assertIsNone(result.error_message)
    
    def test_validate_margin_input_invalid_cases(self):
        """Test invalid margin input cases."""
        invalid_cases = [
            "",  # Empty
            "   ",  # Whitespace only
            "abc",  # Non-numeric
            "34",  # Below range
            "34.9",  # Just below range
            "66",  # Above range
            "65.1",  # Just above range
            "100",  # Way above range
            "0",  # Zero
            "-45",  # Negative
            "45.5.5",  # Invalid format
            "45%%",  # Double %
        ]
        
        for input_value in invalid_cases:
            with self.subTest(input_value=input_value):
                result = validate_margin_input(input_value)
                self.assertFalse(result.is_valid, f"Expected {input_value} to be invalid")
                self.assertIsNone(result.decimal_value)
                self.assertIsNotNone(result.error_message)
    
    def test_validate_margin_input_type_error(self):
        """Test non-string input handling."""
        result = validate_margin_input(45)  # Pass number instead of string
        self.assertFalse(result.is_valid)
        self.assertIn("must be a string", result.error_message)
    
    def test_convert_margin_to_decimal_valid(self):
        """Test successful margin to decimal conversion."""
        test_cases = [
            ("45", 0.45),
            ("45%", 0.45),
            (45, 0.45),
            (45.5, 0.455),
            ("35", 0.35),
            ("65", 0.65),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = convert_margin_to_decimal(input_value)
                self.assertAlmostEqual(result, expected, places=3)
    
    def test_convert_margin_to_decimal_invalid(self):
        """Test margin to decimal conversion with invalid inputs."""
        invalid_cases = [
            "34",  # Below range
            "66",  # Above range
            "abc",  # Non-numeric
            "",  # Empty
        ]
        
        for input_value in invalid_cases:
            with self.subTest(input_value=input_value):
                with self.assertRaises(ValueError):
                    convert_margin_to_decimal(input_value)
    
    def test_margin_validation_result_str(self):
        """Test string representation of MarginValidationResult."""
        # Valid result
        valid_result = MarginValidationResult(is_valid=True, decimal_value=0.45)
        self.assertIn("Valid margin", str(valid_result))
        self.assertIn("0.450", str(valid_result))
        self.assertIn("45.0%", str(valid_result))
        
        # Invalid result  
        invalid_result = MarginValidationResult(is_valid=False, error_message="Test error")
        self.assertIn("Invalid margin", str(invalid_result))
        self.assertIn("Test error", str(invalid_result))
    
    def test_get_margin_prompt_text(self):
        """Test margin prompt text generation."""
        prompt = get_margin_prompt_text()
        self.assertIn("35-65%", prompt)
        self.assertIn("Examples:", prompt)
        self.assertIn("Margin:", prompt)
    
    def test_get_margin_error_help(self):
        """Test margin error help text generation."""
        help_text = get_margin_error_help()
        self.assertIn("Invalid margin", help_text)
        self.assertIn("35 and 65", help_text)
        self.assertIn("Examples:", help_text)


if __name__ == "__main__":
    unittest.main()