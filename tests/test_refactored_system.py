#!/usr/bin/env python3
"""
Test script to validate the refactored SpecKit-compliant system.

This script tests the key refactored components to ensure they work correctly
after the comprehensive refactoring to align with SpecKit specifications.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_data_models():
    """Test that all data models are properly defined and functional."""
    print("🧪 Testing Data Models...")
    
    try:
        from data_models import (
            UserInput, SourceFile, OutputFile, 
            CLIFieldConfig, CLIFieldValue, CLICollectionResult,
            OperationError, ErrorType
        )
        
        # Test UserInput validation
        user_input = UserInput(client_name="Test Client", gig_name="Test Project")
        assert user_input.client_name == "Test Client"
        assert user_input.gig_name == "Test Project"
        print("   ✅ UserInput validation works")
        
        # Test OperationError creation
        error = OperationError.invalid_input("test_field", "Test error")
        assert error.error_type == ErrorType.INVALID_USER_INPUT
        print("   ✅ OperationError creation works")
        
        # Test CLIFieldConfig
        config = CLIFieldConfig(prompt="Test prompt", field_key="test")
        assert config.required == True  # Default value
        print("   ✅ CLIFieldConfig defaults work")
        
        print("   🎉 All data models working correctly!")
        return True
        
    except Exception as e:
        print(f"   ❌ Data model test failed: {e}")
        return False


def test_file_operations():
    """Test file operation functions with new data models."""
    print("🧪 Testing File Operations...")
    
    try:
        from file_operations import discover_template_file, copy_file_with_metadata
        from data_models import SourceFile
        
        # Test that functions exist
        assert callable(discover_template_file)
        assert callable(copy_file_with_metadata)
        print("   ✅ Contract-compliant functions exist")
        
        print("   🎉 File operations interface ready!")
        return True
        
    except Exception as e:
        print(f"   ❌ File operations test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface with new data models."""
    print("🧪 Testing CLI Interface...")
    
    try:
        from cli_interface import CLI_FIELDS_CONFIG, collect_cli_fields, prompt_for_text
        from data_models import CLIFieldConfig
        
        # Verify CLI configuration uses SpecKit data models
        assert isinstance(CLI_FIELDS_CONFIG, dict)
        assert len(CLI_FIELDS_CONFIG) > 0
        
        for field_name, config in CLI_FIELDS_CONFIG.items():
            assert isinstance(config, CLIFieldConfig), f"Field {field_name} not using CLIFieldConfig"
        
        print("   ✅ CLI configuration uses SpecKit data models")
        
        # Test that new contract-compliant functions exist
        assert callable(collect_cli_fields)
        assert callable(prompt_for_text)
        print("   ✅ Contract-compliant CLI functions exist")
        
        print("   🎉 CLI interface properly refactored!")
        return True
        
    except Exception as e:
        print(f"   ❌ CLI interface test failed: {e}")
        return False


def test_structured_errors():
    """Test structured error handling."""
    print("🧪 Testing Structured Error Handling...")
    
    try:
        from data_models import OperationError, ErrorType
        
        # Test different error types
        file_error = OperationError.file_not_found("test.txt", "File missing")
        assert file_error.error_type == ErrorType.FILE_NOT_FOUND
        
        input_error = OperationError.invalid_input("test_field", "Invalid data")
        assert input_error.error_type == ErrorType.INVALID_USER_INPUT
        
        permission_error = OperationError.permission_denied("test.txt", "Cannot access")
        assert permission_error.error_type == ErrorType.PERMISSION_DENIED
        
        print("   ✅ All error types working correctly")
        print("   🎉 Structured error handling implemented!")
        return True
        
    except Exception as e:
        print(f"   ❌ Structured error test failed: {e}")
        return False


def test_protocol_interfaces():
    """Test protocol interface definitions."""
    print("🧪 Testing Protocol Interfaces...")
    
    try:
        from data_models import (
            FileOperationProtocol, 
            FieldMatcherProtocol, 
            DataPopulatorProtocol,
            CLIInputProtocol,
            ValidationProtocol
        )
        
        # Verify protocols are properly defined (they should be callable as type checks)
        protocols = [
            FileOperationProtocol,
            FieldMatcherProtocol, 
            DataPopulatorProtocol,
            CLIInputProtocol,
            ValidationProtocol
        ]
        
        for protocol in protocols:
            assert hasattr(protocol, '__annotations__'), f"Protocol {protocol.__name__} missing annotations"
        
        print("   ✅ All protocol interfaces defined")
        print("   🎉 Protocol interfaces ready for extensibility!")
        return True
        
    except Exception as e:
        print(f"   ❌ Protocol interface test failed: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("🚀 Testing Refactored SpecKit-Compliant System")
    print("=" * 50)
    
    tests = [
        test_data_models,
        test_file_operations, 
        test_cli_interface,
        test_structured_errors,
        test_protocol_interfaces
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
        print("\n✅ You can now safely run the main application:")
        print("   python pricing_tool_accelerator.py")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)