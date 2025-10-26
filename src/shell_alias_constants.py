#!/usr/bin/env python3
"""
Shell Alias Constants - Configuration constants for shell alias auto-setup.

This module contains all the constants used throughout the shell alias system
including file paths, command templates, error messages, and configuration values.
"""

from pathlib import Path


# === SHELL CONFIGURATION ===
DEFAULT_ALIAS_NAME = "priceup"
DEFAULT_TARGET_SCRIPT = "pricing_tool_accelerator.py"
DEFAULT_CODE_DIRECTORY = "."

# Shell support
SUPPORTED_SHELLS = ["zsh"]
SHELL_CONFIG_FILES = {
    "zsh": Path.home() / ".zshrc"
}

# === FILE MARKERS ===
ALIAS_START_MARKER = "# DTT Pricing Tool Alias - START"
ALIAS_END_MARKER = "# DTT Pricing Tool Alias - END"

# === COMMAND TEMPLATES ===
ALIAS_COMMAND_TEMPLATE = "alias {alias_name}='cd {script_dir} && python3 {script_path}'"

# === ERROR MESSAGES ===
ERROR_MESSAGES = {
    "shell_unsupported": "Only zsh is currently supported. Please use zsh shell.",
    "script_not_found": "Target script not found: {path}",
    "alias_exists": "Alias '{alias}' already exists. Use --force to overwrite.",
    "file_write_error": "Failed to write alias configuration: {error}",
    "validation_error": "Validation error: {error}",
    "empty_alias_name": "Alias name cannot be empty",
    "path_resolution_failed": "Could not determine target script path"
}

# === SUCCESS MESSAGES ===
SUCCESS_MESSAGES = {
    "alias_created": "Successfully set up '{alias}' alias. Restart your terminal or run 'source ~/.zshrc' to use it.",
    "backup_created": "Backup created: {backup_path}",
}

# === INFORMATIONAL MESSAGES ===
INFO_MESSAGES = {
    "checking_shell": "Checking current shell environment...",
    "detecting_script": "Detecting target script location...",
    "creating_backup": "Creating backup of existing configuration...",
    "writing_alias": "Writing alias configuration...",
    "setup_complete": "Shell alias setup complete!"
}

# === VALIDATION CONSTANTS ===
MAX_ALIAS_NAME_LENGTH = 50
MIN_ALIAS_NAME_LENGTH = 1
VALID_ALIAS_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

# === PATH RESOLUTION ===
SCRIPT_SEARCH_PATHS = [
    ".",  # Current directory
]

# === TIMEOUT SETTINGS ===
SETUP_TIMEOUT_SECONDS = 60
FILE_OPERATION_TIMEOUT_SECONDS = 30

# === BACKUP SETTINGS ===
BACKUP_EXTENSION = ".backup"
MAX_BACKUP_FILES = 5  # Keep up to 5 backup files

# === LOGGING CONFIGURATION ===
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"