#!/usr/bin/env python3
"""
Logging configuration module for the DTT Pricing Tool Accelerator.

This module provides centralized logging configuration and message categorization
to enable clean production CLI output while preserving detailed diagnostics for
development and debugging.

Feature 007: Implements global verbose logging toggle with message classification.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class MessageCategory(Enum):
    """
    Message categorization for selective display control.
    
    Supports three-tier output classification:
    - ESSENTIAL_USER: Always displayed (input prompts, final results, errors)
    - OPERATION_STATUS: Always displayed (major operation progress indicators)
    - TECHNICAL_DIAGNOSTIC: Controlled by verbose toggle (field matching, internal details)
    """
    ESSENTIAL_USER = "essential_user"
    OPERATION_STATUS = "operation_status"  
    TECHNICAL_DIAGNOSTIC = "technical_diagnostic"


@dataclass
class LoggingConfig:
    """
    Configuration data for logging system.
    
    Attributes:
        verbose_enabled: Whether to display technical diagnostic messages
        base_log_level: Base logging level (INFO, WARNING, ERROR)
        message_categories: Controls which message types display
    """
    verbose_enabled: bool = False
    base_log_level: str = "INFO"
    message_categories: Dict[MessageCategory, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default message category settings."""
        if not self.message_categories:
            self.message_categories = {
                MessageCategory.ESSENTIAL_USER: True,
                MessageCategory.OPERATION_STATUS: True,
                MessageCategory.TECHNICAL_DIAGNOSTIC: self.verbose_enabled
            }


class ConfigurationError(Exception):
    """Raised when logging configuration fails."""
    pass


class MessageCategorizationError(Exception):
    """Raised when message categorization fails."""
    pass


# Global logging configuration instance
_current_config: Optional[LoggingConfig] = None


def configure_logging(verbose_enabled: bool = False) -> None:
    """
    Configure global logging behavior for the application.
    
    Args:
        verbose_enabled: Whether to display technical diagnostic messages
        
    Returns:
        None
        
    Raises:
        ConfigurationError: If logging setup fails
        
    Constitutional Compliance:
    - Atomic function: Single responsibility for logging configuration
    - No side effects: Only affects logging system
    - Explicit error handling: Raises specific exception types
    """
    global _current_config
    
    try:
        # Create logging configuration
        _current_config = LoggingConfig(
            verbose_enabled=verbose_enabled,
            base_log_level="INFO"
        )
        
        # Remove existing handlers to avoid duplicates
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create and configure custom handler
        handler = ProductionOutputHandler(verbose_enabled=verbose_enabled)
        handler.setLevel(logging.INFO)
        
        # Set formatter for consistent output
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
    except Exception as e:
        raise ConfigurationError(f"Failed to configure logging: {e}")


def is_verbose_enabled() -> bool:
    """
    Check current verbose logging status.
    
    Returns:
        Current verbose logging state
        
    Constitutional Compliance:
    - Atomic function: Single query operation
    - No side effects: Read-only operation
    """
    global _current_config
    return _current_config.verbose_enabled if _current_config else False


def toggle_verbose_logging() -> bool:
    """
    Toggle verbose logging mode and return new state.
    
    Returns:
        New verbose logging state after toggle
        
    Constitutional Compliance:
    - Atomic function: Single toggle operation
    - Clear return value: New state for verification
    """
    global _current_config
    
    if _current_config is None:
        configure_logging(verbose_enabled=True)
        return True
    
    new_state = not _current_config.verbose_enabled
    configure_logging(verbose_enabled=new_state)
    return new_state


def categorize_message(message: str, context: str = "") -> MessageCategory:
    """
    Classify a log message into appropriate display category.
    
    Args:
        message: The log message content
        context: Optional context (module name, operation type)
        
    Returns:
        MessageCategory enum value for display control
        
    Constitutional Compliance:
    - Atomic function: Single classification responsibility
    - Well-defined arguments: Clear input specification
    - Explicit return type: Enum for type safety
    """
    try:
        message_lower = message.lower()
        
        # Operation status messages (always show) - major workflow steps
        # Check step messages FIRST to ensure they always show regardless of other keywords
        high_level_status = [
            'step 1:', 'step 2:', 'step 3:',  # Step messages have highest priority
            'starting spreadsheet', 'starting consolidated', 'starting enhanced', 
            'population complete', 'excel operations completed', 'consolidated workflow completed',
            'populating data', 'copying template', 'resource setup completed', 'rate card', 'opening in finder'
        ]
        if any(keyword in message_lower for keyword in high_level_status):
            return MessageCategory.OPERATION_STATUS
        
        # Essential user messages (always show) - errors and critical failures
        essential_keywords = ['error', 'failed', 'cannot', 'invalid', 'missing', 'cancelled']
        if any(keyword in message_lower for keyword in essential_keywords):
            return MessageCategory.ESSENTIAL_USER
        
        # Technical diagnostic messages (verbose mode only) - detailed internal operations
        technical_keywords = [
            'debug:', 'found potential field', 'successfully wrote', 'worksheet field matching',
            'session opened', 'opening consolidated', 'copying resource', 'rate card calculation',
            'field at', 'verification failed', 'value verification', 'operations:', 'copied', 'cells',
            'c28:h34', 'existing session', 'workflow completed', 'constants directory',
            'target file:', 'loaded', 'constants', 'found', 'field matches', 'creating temporary',
            'xlsx for field matching', 'total data for population', 'data population had issues',
            'starting consolidated excel operations', 'excel operations completed'
        ]
        if any(keyword in message_lower for keyword in technical_keywords):
            return MessageCategory.TECHNICAL_DIAGNOSTIC
            
        # Default: anything else should be technical diagnostic (verbose only)
        return MessageCategory.TECHNICAL_DIAGNOSTIC
        
    except Exception as e:
        # If categorization fails, err on the side of showing the message
        return MessageCategory.OPERATION_STATUS


def should_display_message(category: MessageCategory, verbose_enabled: bool) -> bool:
    """
    Determine if message should be displayed based on category and verbose setting.
    
    Args:
        category: Message category from categorize_message()
        verbose_enabled: Current verbose logging state
        
    Returns:
        True if message should be displayed, False otherwise
        
    Constitutional Compliance:
    - Atomic function: Single decision responsibility
    - No side effects: Pure function for display decision
    """
    if category == MessageCategory.ESSENTIAL_USER:
        return True
    elif category == MessageCategory.OPERATION_STATUS:
        return True
    elif category == MessageCategory.TECHNICAL_DIAGNOSTIC:
        return verbose_enabled
    else:
        # Unknown category, default to showing in verbose mode only
        return verbose_enabled


class ProductionOutputHandler(logging.Handler):
    """
    Custom logging handler that implements message categorization and filtering.
    Extends Python standard library following constitutional best practices.
    """
    
    def __init__(self, verbose_enabled: bool = False):
        """
        Initialize handler with verbose setting.
        
        Args:
            verbose_enabled: Whether to display technical diagnostic messages
            
        Constitutional Compliance:
        - Clear initialization: Explicit configuration parameter
        - Follows Python best practices: Proper inheritance
        """
        super().__init__()
        self.verbose_enabled = verbose_enabled
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Process and optionally display log record based on categorization.
        
        Args:
            record: Standard logging record from Python logging system
            
        Constitutional Compliance:
        - Standard interface: Follows logging.Handler contract
        - Atomic function: Single emission responsibility
        """
        try:
            # Always show ERROR messages regardless of verbose setting
            if record.levelno >= logging.ERROR:
                self._output_message(record)
                return
            
            # For WARNING and INFO level messages, apply categorization
            if record.levelno >= logging.INFO:
                message = record.getMessage()
                context = record.name
                
                category = categorize_message(message, context)
                
                if should_display_message(category, self.verbose_enabled):
                    self._output_message(record)
                # Otherwise, suppress the message
                
        except Exception:
            # If anything goes wrong, default to showing the message
            # to avoid losing critical information
            self._output_message(record)
    
    def _output_message(self, record: logging.LogRecord) -> None:
        """Output the log message to stdout."""
        try:
            message = self.format(record)
            print(message)
        except Exception:
            # Last resort: output raw message
            print(record.getMessage())
    
    def update_verbose_setting(self, verbose_enabled: bool) -> None:
        """
        Update verbose setting for runtime configuration changes.
        
        Args:
            verbose_enabled: New verbose logging state
            
        Constitutional Compliance:
        - Atomic function: Single configuration update
        - Runtime flexibility: Enables toggle without restart
        """
        self.verbose_enabled = verbose_enabled