#!/usr/bin/env python3
"""
Unit tests for logging configuration module.

Tests the production logging system including message categorization,
verbose toggle functionality, and custom handler behavior.

Feature 007: Validates logging configuration and message filtering.
"""

import logging
import sys
import unittest
from io import StringIO
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, 'src')

from logging_config import (
    MessageCategory,
    LoggingConfig,
    configure_logging,
    is_verbose_enabled,
    toggle_verbose_logging,
    categorize_message,
    should_display_message,
    ProductionOutputHandler,
    ConfigurationError
)


class TestMessageCategorization(unittest.TestCase):
    """Test message categorization functionality."""
    
    def test_essential_user_messages(self):
        """Test that error messages are classified as essential user."""
        test_cases = [
            "Error: File not found",
            "Failed to connect to database",
            "Invalid user input provided",
            "Cannot access the resource",
            "Missing required parameter"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                category = categorize_message(message)
                self.assertEqual(category, MessageCategory.ESSENTIAL_USER)
    
    def test_operation_status_messages(self):
        """Test that operation messages are classified as status."""
        test_cases = [
            "Starting data population...",
            "Population complete: 5 fields updated",
            "Step 1: Reading constants data...",
            "Opening file in Finder...",
            "Copying file with rename..."
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                category = categorize_message(message)
                self.assertEqual(category, MessageCategory.OPERATION_STATUS)
    
    def test_technical_diagnostic_messages(self):
        """Test that detailed messages are classified as technical diagnostic."""
        test_cases = [
            "Field matching score: 0.85",
            "Found 12 constants in worksheet",
            "Creating temporary .xlsx for field matching",
            "Detailed field analysis results"
        ]
        
        for message in test_cases:
            with self.subTest(message=message):
                category = categorize_message(message)
                self.assertEqual(category, MessageCategory.TECHNICAL_DIAGNOSTIC)


class TestMessageDisplayLogic(unittest.TestCase):
    """Test message display decision logic."""
    
    def test_essential_user_always_displayed(self):
        """Essential user messages should always display regardless of verbose setting."""
        self.assertTrue(should_display_message(MessageCategory.ESSENTIAL_USER, True))
        self.assertTrue(should_display_message(MessageCategory.ESSENTIAL_USER, False))
    
    def test_operation_status_always_displayed(self):
        """Operation status messages should always display regardless of verbose setting."""
        self.assertTrue(should_display_message(MessageCategory.OPERATION_STATUS, True))
        self.assertTrue(should_display_message(MessageCategory.OPERATION_STATUS, False))
    
    def test_technical_diagnostic_verbose_only(self):
        """Technical diagnostic messages should only display in verbose mode."""
        self.assertTrue(should_display_message(MessageCategory.TECHNICAL_DIAGNOSTIC, True))
        self.assertFalse(should_display_message(MessageCategory.TECHNICAL_DIAGNOSTIC, False))


class TestLoggingConfiguration(unittest.TestCase):
    """Test logging configuration functionality."""
    
    def setUp(self):
        """Reset logging configuration before each test."""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_configure_logging_success(self):
        """Test successful logging configuration."""
        configure_logging(verbose_enabled=True)
        self.assertTrue(is_verbose_enabled())
        
        configure_logging(verbose_enabled=False)
        self.assertFalse(is_verbose_enabled())
    
    def test_toggle_verbose_logging(self):
        """Test verbose logging toggle functionality."""
        # Start with verbose disabled
        configure_logging(verbose_enabled=False)
        self.assertFalse(is_verbose_enabled())
        
        # Toggle to enabled
        result = toggle_verbose_logging()
        self.assertTrue(result)
        self.assertTrue(is_verbose_enabled())
        
        # Toggle back to disabled
        result = toggle_verbose_logging()
        self.assertFalse(result)
        self.assertFalse(is_verbose_enabled())


class TestProductionOutputHandler(unittest.TestCase):
    """Test custom production output handler."""
    
    def setUp(self):
        """Setup test handler."""
        self.handler = ProductionOutputHandler(verbose_enabled=False)
        
    @patch('builtins.print')
    def test_error_messages_always_displayed(self, mock_print):
        """Error messages should always be displayed."""
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Test error message",
            args=(),
            exc_info=None
        )
        
        self.handler.emit(record)
        mock_print.assert_called_once()
    
    @patch('builtins.print')  
    def test_warning_messages_always_displayed(self, mock_print):
        """Warning messages should always be displayed."""
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Test warning message",
            args=(),
            exc_info=None
        )
        
        self.handler.emit(record)
        mock_print.assert_called_once()
    
    @patch('builtins.print')
    def test_info_messages_filtered_by_category(self, mock_print):
        """INFO messages should be filtered based on categorization."""
        # Test essential user message (should display)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Error: Something went wrong",
            args=(),
            exc_info=None
        )
        
        self.handler.emit(record)
        mock_print.assert_called_once()
        
        mock_print.reset_mock()
        
        # Test technical diagnostic message in production mode (should not display)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Field matching score: 0.85",
            args=(),
            exc_info=None
        )
        
        self.handler.emit(record)
        mock_print.assert_not_called()
    
    def test_update_verbose_setting(self):
        """Test runtime verbose setting update."""
        handler = ProductionOutputHandler(verbose_enabled=False)
        self.assertFalse(handler.verbose_enabled)
        
        handler.update_verbose_setting(True)
        self.assertTrue(handler.verbose_enabled)


class TestLoggingConfigDataClass(unittest.TestCase):
    """Test LoggingConfig dataclass."""
    
    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = LoggingConfig()
        
        self.assertFalse(config.verbose_enabled)
        self.assertEqual(config.base_log_level, "INFO")
        self.assertIn(MessageCategory.ESSENTIAL_USER, config.message_categories)
        self.assertTrue(config.message_categories[MessageCategory.ESSENTIAL_USER])
        self.assertTrue(config.message_categories[MessageCategory.OPERATION_STATUS])
        self.assertFalse(config.message_categories[MessageCategory.TECHNICAL_DIAGNOSTIC])
    
    def test_verbose_initialization(self):
        """Test configuration with verbose enabled."""
        config = LoggingConfig(verbose_enabled=True)
        
        self.assertTrue(config.verbose_enabled)
        self.assertTrue(config.message_categories[MessageCategory.TECHNICAL_DIAGNOSTIC])


if __name__ == '__main__':
    unittest.main()