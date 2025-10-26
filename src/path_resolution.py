#!/usr/bin/env python3
"""
Path Resolution Utility - Smart path resolution for target script location.

This module provides intelligent path resolution to locate the pricing tool
script from various execution contexts and repository structures.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
from .shell_alias_constants import (
    DEFAULT_TARGET_SCRIPT,
    DEFAULT_CODE_DIRECTORY,
    SCRIPT_SEARCH_PATHS,
    ERROR_MESSAGES
)


class PathResolver:
    """Utility class for resolving script paths intelligently."""
    
    @staticmethod
    def resolve_target_script_path(
        script_name: str = DEFAULT_TARGET_SCRIPT,
        search_paths: Optional[List[str]] = None,
        current_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Resolve the target script path using intelligent search strategy.
        
        Args:
            script_name: Name of the target script file
            search_paths: Custom search paths (uses default if None)
            current_dir: Current directory context (uses cwd if None)
            
        Returns:
            Resolved absolute path to the script, or None if not found
        """
        if search_paths is None:
            search_paths = SCRIPT_SEARCH_PATHS
            
        if current_dir is None:
            current_dir = Path.cwd()
        
        # Strategy 1: Direct search in provided paths
        for search_path in search_paths:
            script_path = PathResolver._check_path_for_script(
                current_dir, search_path, script_name
            )
            if script_path:
                return script_path
        
        # Strategy 2: Repository-aware search
        repo_root = PathResolver._find_repository_root(current_dir)
        if repo_root:
            # Try code directory in repo root
            code_dir_script = repo_root / DEFAULT_CODE_DIRECTORY / script_name
            if code_dir_script.exists():
                return code_dir_script.resolve()
            
            # Try script in repo root
            root_script = repo_root / script_name
            if root_script.exists():
                return root_script.resolve()
        
        # Strategy 3: Recursive upward search
        recursive_path = PathResolver._recursive_upward_search(
            current_dir, script_name
        )
        if recursive_path:
            return recursive_path
        
        return None
    
    @staticmethod
    def _check_path_for_script(
        base_dir: Path, 
        relative_path: str, 
        script_name: str
    ) -> Optional[Path]:
        """Check a specific path for the target script."""
        try:
            if relative_path == ".":
                search_dir = base_dir
            else:
                search_dir = base_dir / relative_path
            
            script_path = search_dir / script_name
            
            if script_path.exists() and script_path.is_file():
                return script_path.resolve()
                
        except Exception:
            # Ignore path resolution errors and continue searching
            pass
        
        return None
    
    @staticmethod
    def _find_repository_root(start_path: Path) -> Optional[Path]:
        """
        Find the repository root by looking for .git directory.
        
        Args:
            start_path: Starting directory for the search
            
        Returns:
            Path to repository root, or None if not found
        """
        current = start_path.resolve()
        
        # Traverse up the directory tree
        while current != current.parent:
            # Check for .git directory
            if (current / ".git").exists():
                return current
            
            # Check for other repository indicators
            repo_indicators = [".git", ".hg", ".svn", "pyproject.toml", "setup.py"]
            for indicator in repo_indicators:
                if (current / indicator).exists():
                    return current
            
            current = current.parent
        
        return None
    
    @staticmethod
    def _recursive_upward_search(
        start_dir: Path, 
        script_name: str, 
        max_levels: int = 5
    ) -> Optional[Path]:
        """
        Recursively search upward for the target script.
        
        Args:
            start_dir: Starting directory
            script_name: Name of script to find
            max_levels: Maximum levels to search upward
            
        Returns:
            Path to script if found, None otherwise
        """
        current = start_dir.resolve()
        
        for _ in range(max_levels):
            # Check current directory
            script_path = current / script_name
            if script_path.exists():
                return script_path.resolve()
            
            # Check code directory
            code_dir_script = current / DEFAULT_CODE_DIRECTORY / script_name
            if code_dir_script.exists():
                return code_dir_script.resolve()
            
            # Move up one level
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        return None
    
    @staticmethod
    def validate_script_path(script_path: Path) -> Tuple[bool, str]:
        """
        Validate that a script path is usable for alias creation.
        
        Args:
            script_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if path exists
            if not script_path.exists():
                return False, ERROR_MESSAGES["script_not_found"].format(path=script_path)
            
            # Check if it's a file (not directory)
            if not script_path.is_file():
                return False, f"Path is not a file: {script_path}"
            
            # Check if it's readable
            if not os.access(script_path, os.R_OK):
                return False, f"No read permission for script: {script_path}"
            
            # Check if it's a Python script (basic heuristic)
            if not script_path.suffix.lower() == ".py":
                return False, f"Script does not appear to be a Python file: {script_path}"
            
            # Validate the script contains expected content (basic check)
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    first_lines = f.read(1000)  # Read first 1000 characters
                
                # Basic Python script validation
                if not (first_lines.startswith('#!') or 'python' in first_lines.lower() or 'import ' in first_lines):
                    return False, f"Script does not appear to be a valid Python script: {script_path}"
                    
            except Exception as e:
                return False, f"Could not read script content: {e}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating script path: {str(e)}"
    
    @staticmethod
    def get_script_directory(script_path: Path) -> Path:
        """
        Get the directory containing the script.
        
        Args:
            script_path: Path to the script
            
        Returns:
            Directory path containing the script
        """
        return script_path.parent.resolve()
    
    @staticmethod
    def create_portable_alias_command(
        script_path: Path, 
        alias_name: str = "priceup"
    ) -> str:
        """
        Create a portable alias command that works from any directory.
        
        Since the pricing tool script is designed to work from any directory,
        we only need to call it directly with python3.
        
        Args:
            script_path: Absolute path to the target script
            alias_name: Name of the alias to create
            
        Returns:
            Shell alias command string
        """
        import shlex
        
        # Create simple command that runs script directly (no cd needed)
        escaped_script_path = shlex.quote(str(script_path))
        
        return f"alias {alias_name}='python3 {escaped_script_path}'"
    
    @staticmethod
    def find_all_potential_scripts(
        script_name: str = DEFAULT_TARGET_SCRIPT,
        start_dir: Optional[Path] = None
    ) -> List[Path]:
        """
        Find all potential script locations for debugging purposes.
        
        Args:
            script_name: Name of script to search for
            start_dir: Starting directory (uses cwd if None)
            
        Returns:
            List of all found script paths
        """
        if start_dir is None:
            start_dir = Path.cwd()
        
        found_scripts = []
        
        # Search in standard paths
        for search_path in SCRIPT_SEARCH_PATHS:
            script_path = PathResolver._check_path_for_script(
                start_dir, search_path, script_name
            )
            if script_path and script_path not in found_scripts:
                found_scripts.append(script_path)
        
        # Repository-based search
        repo_root = PathResolver._find_repository_root(start_dir)
        if repo_root:
            code_dir_script = repo_root / DEFAULT_CODE_DIRECTORY / script_name
            if code_dir_script.exists() and code_dir_script not in found_scripts:
                found_scripts.append(code_dir_script.resolve())
            
            root_script = repo_root / script_name
            if root_script.exists() and root_script not in found_scripts:
                found_scripts.append(root_script.resolve())
        
        # Recursive search
        recursive_scripts = []
        current = start_dir.resolve()
        for _ in range(5):  # Search up to 5 levels
            script_path = current / script_name
            if script_path.exists() and script_path not in found_scripts and script_path not in recursive_scripts:
                recursive_scripts.append(script_path.resolve())
            
            code_dir_script = current / DEFAULT_CODE_DIRECTORY / script_name
            if code_dir_script.exists() and code_dir_script not in found_scripts and code_dir_script not in recursive_scripts:
                recursive_scripts.append(code_dir_script.resolve())
            
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        found_scripts.extend(recursive_scripts)
        return found_scripts