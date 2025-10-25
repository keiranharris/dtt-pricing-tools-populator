"""
Feature 006 Final Validation Script

Comprehensive validation of all Feature 006 components to ensure
complete functionality before deployment.

Author: DTT Pricing Tool Accelerator
Feature: 006-populate-rate
"""

import sys
from pathlib import Path
import unittest
from io import StringIO
from typing import List, Dict, Any

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import all Feature 006 modules
try:
    from margin_validator import (
        validate_margin_input, 
        convert_margin_to_decimal,
        get_margin_prompt_text,
        get_margin_error_help
    )
    from rate_card_calculator import (
        calculate_engineering_rate,
        StandardCostRate,
        EngineeringRate,
        RateCalculationResult
    )
    from cli_interface import collect_margin_percentage
    from excel_rate_integration import (
        validate_excel_environment,
        ExcelAccessError,
        WorksheetNotFoundError
    )
    IMPORTS_SUCCESS = True
except ImportError as e:
    print(f"❌ Import Error: {e}")
    IMPORTS_SUCCESS = False


class Feature006Validator:
    """Comprehensive validator for Feature 006 functionality."""
    
    def __init__(self):
        self.results = {
            "imports": False,
            "margin_validation": False,
            "rate_calculation": False,
            "cli_integration": False,
            "excel_environment": False,
            "error_handling": False,
            "data_models": False,
            "total_tests": 0,
            "passed_tests": 0,
            "errors": []
        }
    
    def validate_imports(self) -> bool:
        """Validate all required imports are available."""
        try:
            print("🔍 Testing imports...")
            self.results["imports"] = IMPORTS_SUCCESS
            if IMPORTS_SUCCESS:
                print("✅ All imports successful")
            else:
                print("❌ Import failures detected")
            return IMPORTS_SUCCESS
        except Exception as e:
            self.results["errors"].append(f"Import validation error: {e}")
            return False
    
    def validate_margin_validation(self) -> bool:
        """Validate margin validation functionality."""
        try:
            print("🔍 Testing margin validation...")
            
            # Test valid cases
            valid_cases = [
                ("35", 0.35),
                ("65%", 0.65),
                ("45.5", 0.455),
                ("  50  ", 0.50)
            ]
            
            for input_val, expected in valid_cases:
                result = validate_margin_input(input_val)
                if not result.is_valid or abs(result.decimal_value - expected) > 0.001:
                    raise AssertionError(f"Valid case failed: {input_val}")
            
            # Test invalid cases
            invalid_cases = ["34", "66", "abc", ""]
            for input_val in invalid_cases:
                result = validate_margin_input(input_val)
                if result.is_valid:
                    raise AssertionError(f"Invalid case passed: {input_val}")
            
            # Test conversion function
            if abs(convert_margin_to_decimal("45%") - 0.45) > 0.001:
                raise AssertionError("Decimal conversion failed")
            
            # Test prompt text generation
            prompt_text = get_margin_prompt_text()
            if "35-65%" not in prompt_text or "Margin:" not in prompt_text:
                raise AssertionError("Prompt text missing required elements")
            
            self.results["margin_validation"] = True
            print("✅ Margin validation tests passed")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Margin validation error: {e}")
            print(f"❌ Margin validation failed: {e}")
            return False
    
    def validate_rate_calculation(self) -> bool:
        """Validate rate calculation functionality."""
        try:
            print("🔍 Testing rate calculation...")
            
            # Test basic calculation formula
            rate = calculate_engineering_rate(100.0, 0.45)
            expected = 100.0 / (1 - 0.45)  # Should be ~181.82
            if abs(rate - expected) > 0.01:
                raise AssertionError(f"Rate calculation incorrect: got {rate}, expected {expected}")
            
            # Test edge cases
            try:
                calculate_engineering_rate(-100, 0.45)  # Should raise error
                raise AssertionError("Negative rate should raise error")
            except ValueError:
                pass  # Expected
            
            try:
                calculate_engineering_rate(100, 1.0)  # Should raise error
                raise AssertionError("100% margin should raise error")
            except ValueError:
                pass  # Expected
            
            # Test data model creation
            std_rate = StandardCostRate("Level 1", 100.0, 28, True, None, "Q28")
            if std_rate.staff_level != "Level 1" or std_rate.cost_rate != 100.0:
                raise AssertionError("StandardCostRate model creation failed")
            
            eng_rate = EngineeringRate("Level 1", 100.0, 0.45, 181.82, 28, True, None, "O28")
            if eng_rate.engineering_rate != 181.82 or eng_rate.client_margin != 0.45:
                raise AssertionError("EngineeringRate model creation failed")
            
            self.results["rate_calculation"] = True
            print("✅ Rate calculation tests passed")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Rate calculation error: {e}")
            print(f"❌ Rate calculation failed: {e}")
            return False
    
    def validate_data_models(self) -> bool:
        """Validate data model string representations and properties."""
        try:
            print("🔍 Testing data models...")
            
            # Test StandardCostRate string representation
            std_rate = StandardCostRate("Level 1", 100.0, 28, True, None, "Q28")
            str_repr = str(std_rate)
            if "Level 1" not in str_repr or "$100.00" not in str_repr:
                raise AssertionError("StandardCostRate string representation incorrect")
            
            # Test EngineeringRate string representation
            eng_rate = EngineeringRate("Level 1", 100.0, 0.45, 181.82, 28, True, None, "O28")
            str_repr = str(eng_rate)
            if "Level 1" not in str_repr or "181.82" not in str_repr or "45.0%" not in str_repr:
                raise AssertionError("EngineeringRate string representation incorrect")
            
            # Test invalid models
            invalid_std = StandardCostRate("Level 2", None, 29, False, "Empty cell", "Q29")
            str_repr = str(invalid_std)
            if "Level 2" not in str_repr or "Empty cell" not in str_repr:
                raise AssertionError("Invalid StandardCostRate string representation incorrect")
            
            self.results["data_models"] = True
            print("✅ Data model tests passed")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Data model error: {e}")
            print(f"❌ Data model tests failed: {e}")
            return False
    
    def validate_excel_environment(self) -> bool:
        """Validate Excel integration environment."""
        try:
            print("🔍 Testing Excel environment...")
            
            # Test environment validation
            env_valid = validate_excel_environment()
            
            # Test error class creation
            try:
                raise ExcelAccessError("Test error")
            except ExcelAccessError as e:
                if str(e) != "Test error":
                    raise AssertionError("ExcelAccessError creation failed")
            
            try:
                raise WorksheetNotFoundError("Test worksheet error")
            except WorksheetNotFoundError as e:
                if str(e) != "Test worksheet error":
                    raise AssertionError("WorksheetNotFoundError creation failed")
            
            self.results["excel_environment"] = True
            print(f"✅ Excel environment tests passed (xlwings available: {env_valid})")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Excel environment error: {e}")
            print(f"❌ Excel environment tests failed: {e}")
            return False
    
    def validate_error_handling(self) -> bool:
        """Validate comprehensive error handling."""
        try:
            print("🔍 Testing error handling...")
            
            # Test margin validation errors
            result = validate_margin_input("invalid")
            if result.is_valid or not result.error_message:
                raise AssertionError("Invalid margin should return error")
            
            # Test rate calculation errors
            try:
                convert_margin_to_decimal("70%")  # Out of range
                raise AssertionError("Out of range margin should raise error")
            except ValueError:
                pass  # Expected
            
            # Test error message generation
            help_text = get_margin_error_help()
            if "Invalid margin" not in help_text or "35 and 65" not in help_text:
                raise AssertionError("Error help text missing required elements")
            
            self.results["error_handling"] = True
            print("✅ Error handling tests passed")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Error handling validation error: {e}")
            print(f"❌ Error handling tests failed: {e}")
            return False
    
    def validate_cli_integration(self) -> bool:
        """Validate CLI integration exists and is importable."""
        try:
            print("🔍 Testing CLI integration...")
            
            # Test function exists and is callable
            if not callable(collect_margin_percentage):
                raise AssertionError("collect_margin_percentage is not callable")
            
            # Test prompt text functions
            prompt = get_margin_prompt_text()
            help_text = get_margin_error_help()
            
            if not prompt or not help_text:
                raise AssertionError("CLI text functions returned empty results")
            
            self.results["cli_integration"] = True
            print("✅ CLI integration tests passed")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"CLI integration error: {e}")
            print(f"❌ CLI integration tests failed: {e}")
            return False
    
    def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all Feature 006 components."""
        print("🚀 Feature 006 Comprehensive Validation")
        print("=" * 50)
        
        # Count total tests
        validation_methods = [
            self.validate_imports,
            self.validate_margin_validation, 
            self.validate_rate_calculation,
            self.validate_data_models,
            self.validate_excel_environment,
            self.validate_error_handling,
            self.validate_cli_integration
        ]
        
        self.results["total_tests"] = len(validation_methods)
        
        # Run all validation methods
        for method in validation_methods:
            if method():
                self.results["passed_tests"] += 1
        
        # Generate summary
        print("\n" + "=" * 50)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 50)
        
        success_rate = (self.results["passed_tests"] / self.results["total_tests"]) * 100
        
        print(f"Tests Passed: {self.results['passed_tests']}/{self.results['total_tests']} ({success_rate:.1f}%)")
        
        if self.results["passed_tests"] == self.results["total_tests"]:
            print("🎉 ALL TESTS PASSED - Feature 006 is ready for deployment!")
            self.results["overall_status"] = "PASS"
        else:
            print("⚠️  Some tests failed - review errors before deployment")
            self.results["overall_status"] = "FAIL"
        
        # Show individual results
        print("\n📊 Detailed Results:")
        for key, value in self.results.items():
            if key.endswith("_tests") or key in ["imports", "margin_validation", "rate_calculation", 
                                               "cli_integration", "excel_environment", "error_handling", "data_models"]:
                status = "✅ PASS" if value else "❌ FAIL"
                print(f"  {key.replace('_', ' ').title()}: {status}")
        
        # Show errors if any
        if self.results["errors"]:
            print("\n❌ Errors Encountered:")
            for i, error in enumerate(self.results["errors"], 1):
                print(f"  {i}. {error}")
        
        return self.results


def main():
    """Main entry point for validation script."""
    validator = Feature006Validator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results["overall_status"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()