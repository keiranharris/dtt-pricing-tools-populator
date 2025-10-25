"""
Unit tests for rate_card_calculator module.

Tests rate calculation, Excel integration, and error handling
following the project constitution principles.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import unittest
from unittest.mock import Mock, patch
from rate_card_calculator import (
    calculate_engineering_rate,
    calculate_engineering_rates,
    StandardCostRate,
    EngineeringRate,
    RateCalculationResult
)


class TestRateCardCalculator(unittest.TestCase):
    """Test cases for rate card calculation functionality."""
    
    def test_calculate_engineering_rate_valid(self):
        """Test valid engineering rate calculations with whole-integer rounding."""
        test_cases = [
            (100.0, 0.45, 182),  # Standard case: 181.82 -> 182
            (120.0, 0.50, 240),  # 50% margin: 240.0 -> 240
            (80.0, 0.35, 123),   # 35% margin: 123.08 -> 123
            (150.0, 0.65, 429),  # 65% margin: 428.57 -> 429
            (50.0, 0.40, 83),    # Lower cost rate: 83.33 -> 83
        ]
        
        for cost_rate, margin, expected in test_cases:
            with self.subTest(cost_rate=cost_rate, margin=margin):
                result = calculate_engineering_rate(cost_rate, margin)
                self.assertEqual(result, expected)
    
    def test_calculate_engineering_rate_invalid_inputs(self):
        """Test engineering rate calculation with invalid inputs."""
        # Invalid cost rates
        with self.assertRaises(ValueError):
            calculate_engineering_rate(-100.0, 0.45)  # Negative cost rate
        
        with self.assertRaises(ValueError):
            calculate_engineering_rate(0, 0.45)  # Zero cost rate
            
        with self.assertRaises(ValueError):
            calculate_engineering_rate("abc", 0.45)  # Non-numeric cost rate
        
        # Invalid margins
        with self.assertRaises(ValueError):
            calculate_engineering_rate(100.0, -0.1)  # Negative margin
            
        with self.assertRaises(ValueError):
            calculate_engineering_rate(100.0, 1.0)  # 100% margin
            
        with self.assertRaises(ValueError):
            calculate_engineering_rate(100.0, 1.5)  # Over 100% margin
    
    def test_standard_cost_rate_str_representation(self):
        """Test string representation of StandardCostRate."""
        # Valid rate
        valid_rate = StandardCostRate(
            staff_level="Level 1", 
            cost_rate=100.0, 
            is_valid=True
        )
        self.assertIn("Level 1", str(valid_rate))
        self.assertIn("$100.00", str(valid_rate))
        
        # Invalid rate
        invalid_rate = StandardCostRate(
            staff_level="Level 2",
            is_valid=False,
            error_message="Empty cell"
        )
        self.assertIn("Level 2", str(invalid_rate))
        self.assertIn("Empty cell", str(invalid_rate))
    
    def test_engineering_rate_str_representation(self):
        """Test string representation of EngineeringRate."""
        # Valid rate
        valid_rate = EngineeringRate(
            staff_level="Level 1",
            standard_cost_rate=100.0,
            client_margin=0.45,
            engineering_rate=182,
            is_valid=True
        )
        self.assertIn("Level 1", str(valid_rate))
        self.assertIn("$182", str(valid_rate))
        self.assertIn("45.0%", str(valid_rate))
        
        # Invalid rate
        invalid_rate = EngineeringRate(
            staff_level="Level 2",
            is_valid=False,
            error_message="Calculation failed"
        )
        self.assertIn("Level 2", str(invalid_rate))
        self.assertIn("Calculation failed", str(invalid_rate))
    
    def test_calculate_engineering_rates_mixed_validity(self):
        """Test rate calculation with mix of valid and invalid standard rates."""
        standard_rates = [
            StandardCostRate("Level 1", 100.0, 1, True),
            StandardCostRate("Level 2", None, 2, False, "Empty cell"),
            StandardCostRate("Level 3", 120.0, 3, True),
            StandardCostRate("Level 4", None, 4, False, "Non-numeric"),
        ]
        
        result = calculate_engineering_rates(standard_rates, 0.45)
        
        # Check overall statistics
        self.assertEqual(result.total_processed, 4)
        self.assertEqual(result.successful_calculations, 2)
        self.assertEqual(result.skipped_invalid, 2)
        
        # Check individual results
        self.assertTrue(result.calculated_rates[0].is_valid)
        self.assertEqual(result.calculated_rates[0].engineering_rate, 182)
        
        self.assertFalse(result.calculated_rates[1].is_valid)
        self.assertEqual(result.calculated_rates[1].error_message, "Empty cell")
        
        self.assertTrue(result.calculated_rates[2].is_valid)  
        self.assertEqual(result.calculated_rates[2].engineering_rate, 218)
        
        self.assertFalse(result.calculated_rates[3].is_valid)
        self.assertEqual(result.calculated_rates[3].error_message, "Non-numeric")
    
    def test_rate_calculation_result_str_representation(self):
        """Test string representation of RateCalculationResult."""
        result = RateCalculationResult(
            calculated_rates=[],
            total_processed=10,
            successful_calculations=8,
            skipped_invalid=2,
            errors=[]
        )
        
        str_repr = str(result)
        self.assertIn("8/10 successful", str_repr)
        self.assertIn("80.0%", str_repr)
    
    @patch('rate_card_calculator.XLWINGS_AVAILABLE', False)
    def test_xlwings_not_available(self):
        """Test graceful handling when xlwings is not available."""
        from rate_card_calculator import read_standard_cost_rates, write_engineering_rates
        
        # Should return empty list when xlwings not available
        rates = read_standard_cost_rates(None)
        self.assertEqual(len(rates), 0)
        
        # Should return error result when xlwings not available
        result = write_engineering_rates(None, [])
        self.assertFalse(result["success"])
        self.assertIn("xlwings not available", result["error"])


if __name__ == "__main__":
    unittest.main()