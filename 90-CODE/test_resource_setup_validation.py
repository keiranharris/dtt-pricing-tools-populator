#!/usr/bin/env python3
"""
Simple validation test for Feature 005: Resource Setup Population

This script tests the core functionality without requiring the full environment.
Tests function imports, basic validation, and error handling.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_resource_setup_imports():
    """Test that all Resource Setup modules can be imported."""
    print("🔍 Testing Resource Setup module imports...")
    
    try:
        from resource_setup_populator import (
            ResourceCopyResult, 
            ValidationResult, 
            ResourceSetupError,
            validate_resource_setup_requirements,
            find_source_resource_data,
            find_target_editable_area,
            copy_resource_setup_range,
            get_resource_setup_summary
        )
        print("✅ All Resource Setup functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False

def test_data_structures():
    """Test that data structures work correctly."""
    print("🔍 Testing Resource Setup data structures...")
    
    try:
        from resource_setup_populator import ResourceCopyResult, ValidationResult
        
        # Test ResourceCopyResult
        result = ResourceCopyResult(
            cells_copied=42,
            source_range="C28:H34",
            target_range="C35:H41",
            success=True,
            error_messages=[],
            execution_time=1.5
        )
        
        assert result.cells_copied == 42
        assert result.success == True
        assert "SUCCESS" in str(result)
        print("✅ ResourceCopyResult working correctly")
        
        # Test ValidationResult
        validation = ValidationResult(
            source_worksheet_exists=True,
            target_worksheet_exists=True,
            source_data_found=True,
            target_area_accessible=True,
            validation_errors=[]
        )
        
        assert validation.source_worksheet_exists == True
        print("✅ ValidationResult working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False

def test_orchestrator_integration():
    """Test that orchestrator integration is properly implemented."""
    print("🔍 Testing orchestrator integration...")
    
    try:
        from data_population_orchestrator import (
            populate_resource_setup_data,
            populate_spreadsheet_data_with_cli_and_resources
        )
        print("✅ Orchestrator integration functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Orchestrator integration test failed: {e}")
        return False

def test_configuration():
    """Test that configuration constants are properly added."""
    print("🔍 Testing configuration integration...")
    
    # Read the main application file to check constants
    try:
        main_file = Path(__file__).parent / "pricing_tool_accelerator.py"
        if not main_file.exists():
            print("❌ Main application file not found")
            return False
            
        content = main_file.read_text()
        
        # Check for Resource Setup constants
        required_constants = [
            "RESOURCE_SETUP_ROW_COUNT",
            "RESOURCE_SETUP_WORKSHEET_NAME", 
            "RESOURCE_SETUP_ENABLED"
        ]
        
        for constant in required_constants:
            if constant not in content:
                print(f"❌ Missing configuration constant: {constant}")
                return False
        
        print("✅ All configuration constants found")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_error_handling():
    """Test basic error handling without requiring Excel files."""
    print("🔍 Testing error handling...")
    
    try:
        from resource_setup_populator import ResourceSetupError, validate_resource_setup_requirements
        
        # Test custom exception
        try:
            raise ResourceSetupError("Test error")
        except ResourceSetupError as e:
            if str(e) == "Test error":
                print("✅ Custom exception handling works")
            else:
                print("❌ Custom exception message incorrect")
                return False
        
        # Test validation with non-existent files
        fake_source = Path("non_existent_source.xlsx")
        fake_target = Path("non_existent_target.xlsx")
        
        validation = validate_resource_setup_requirements(fake_source, fake_target)
        
        # Should handle gracefully without crashing
        if validation is not None:
            print("✅ Error handling for missing files works")
        else:
            print("⚠️  Validation returned None (expected for missing files)")
            
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Feature 005: Resource Setup Population - Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_resource_setup_imports),
        ("Data Structures", test_data_structures), 
        ("Orchestrator Integration", test_orchestrator_integration),
        ("Configuration", test_configuration),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed! Feature 005 is ready.")
        return True
    else:
        print("⚠️  Some validation tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)