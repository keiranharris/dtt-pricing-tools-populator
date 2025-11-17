#!/usr/bin/env python3
"""Migration Logging Configuration.

Specialized logging setup for migration operations with audit trail support.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class MigrationLogger:
    """Logger specialized for migration operations."""
    
    def __init__(self, log_directory: str = "migration_logs", log_level: str = "INFO"):
        """Initialize migration logger.
        
        Args:
            log_directory: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_directory = log_directory
        self.log_level = getattr(logging, log_level.upper())
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger with file and console handlers."""
        # Ensure log directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('migration')
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_directory, f'migration_{timestamp}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_migration_start(self, context_summary: dict) -> None:
        """Log migration start with context summary."""
        self.logger.info("=== MIGRATION STARTED ===")
        self.logger.info(f"Old project name: {context_summary.get('old_project_name')}")
        self.logger.info(f"New project name: {context_summary.get('new_project_name')}")
        self.logger.info(f"Old OneDrive folder: {context_summary.get('old_onedrive_folder')}")
        self.logger.info(f"New OneDrive folder: {context_summary.get('new_onedrive_folder')}")
        self.logger.info("Migration context initialized successfully")
    
    def log_migration_complete(self, success: bool, summary: dict) -> None:
        """Log migration completion with summary."""
        if success:
            self.logger.info("=== MIGRATION COMPLETED SUCCESSFULLY ===")
            self.logger.info(f"Duration: {summary.get('duration', 'N/A')}")
            self.logger.info(f"Phases completed: {summary.get('phases_completed', [])}")
        else:
            self.logger.error("=== MIGRATION FAILED ===")
            self.logger.error(f"Failed phases: {summary.get('phases_failed', [])}")
            self.logger.error(f"Error messages: {summary.get('error_messages', [])}")
        
        self.logger.info(f"Total operations: {summary.get('total_operations', 0)}")
        self.logger.info(f"Successful operations: {summary.get('successful_operations', 0)}")
    
    def log_phase_start(self, phase_name: str, details: Optional[dict] = None) -> None:
        """Log phase start."""
        self.logger.info(f"--- Starting phase: {phase_name} ---")
        if details:
            for key, value in details.items():
                self.logger.info(f"{phase_name} {key}: {value}")
    
    def log_phase_complete(self, phase_name: str, success: bool, details: Optional[dict] = None) -> None:
        """Log phase completion."""
        status = "COMPLETED" if success else "FAILED"
        self.logger.info(f"--- Phase {phase_name}: {status} ---")
        if details:
            for key, value in details.items():
                self.logger.info(f"{phase_name} {key}: {value}")
    
    def log_operation(self, operation: str, success: bool, details: Optional[str] = None) -> None:
        """Log individual operation result."""
        if success:
            self.logger.info(f"✓ {operation}")
            if details:
                self.logger.debug(f"  Details: {details}")
        else:
            self.logger.error(f"✗ {operation}")
            if details:
                self.logger.error(f"  Error: {details}")
    
    def log_backup_created(self, backup_path: str, source_path: str) -> None:
        """Log backup creation."""
        self.logger.info(f"Backup created: {source_path} → {backup_path}")
    
    def log_file_operation(self, operation_type: str, source: str, target: str, success: bool) -> None:
        """Log file operation (rename, copy, etc.)."""
        if success:
            self.logger.info(f"{operation_type}: {source} → {target}")
        else:
            self.logger.error(f"{operation_type} FAILED: {source} → {target}")
    
    def log_github_operation(self, operation: str, repo_old: str, repo_new: str, success: bool) -> None:
        """Log GitHub repository operation."""
        if success:
            self.logger.info(f"GitHub {operation}: {repo_old} → {repo_new}")
        else:
            self.logger.error(f"GitHub {operation} FAILED: {repo_old} → {repo_new}")
    
    def log_onedrive_operation(self, operation: str, folder_old: str, folder_new: str, details: str = "") -> None:
        """Log OneDrive operation."""
        self.logger.info(f"OneDrive {operation}: {folder_old} → {folder_new}")
        if details:
            self.logger.info(f"  {details}")
    
    def log_user_config_update(self, user_id: str, config_path: str, success: bool) -> None:
        """Log user configuration update."""
        if success:
            self.logger.info(f"User config updated: {user_id} ({config_path})")
        else:
            self.logger.error(f"User config update FAILED: {user_id} ({config_path})")
    
    def log_validation_result(self, validation_type: str, success: bool, details: Optional[str] = None) -> None:
        """Log validation result."""
        status = "PASSED" if success else "FAILED"
        self.logger.info(f"Validation {validation_type}: {status}")
        if details:
            if success:
                self.logger.debug(f"  Details: {details}")
            else:
                self.logger.warning(f"  Issues: {details}")
    
    def log_rollback_operation(self, operation: str, success: bool, details: Optional[str] = None) -> None:
        """Log rollback operation."""
        if success:
            self.logger.warning(f"Rollback {operation}: SUCCESS")
        else:
            self.logger.error(f"Rollback {operation}: FAILED")
        
        if details:
            self.logger.info(f"  Details: {details}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message with optional exception."""
        self.logger.error(message)
        if exception:
            self.logger.error(f"Exception: {type(exception).__name__}: {str(exception)}")
    
    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def get_current_log_file(self) -> str:
        """Get path to current log file."""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return ""


# Global logger instance
_migration_logger: Optional[MigrationLogger] = None


def get_migration_logger() -> MigrationLogger:
    """Get global migration logger instance."""
    global _migration_logger
    if _migration_logger is None:
        _migration_logger = MigrationLogger()
    return _migration_logger


def configure_migration_logging(log_directory: str = "migration_logs", log_level: str = "INFO") -> MigrationLogger:
    """Configure global migration logging.
    
    Args:
        log_directory: Directory to store log files
        log_level: Logging level
        
    Returns:
        Configured migration logger
    """
    global _migration_logger
    _migration_logger = MigrationLogger(log_directory, log_level)
    return _migration_logger