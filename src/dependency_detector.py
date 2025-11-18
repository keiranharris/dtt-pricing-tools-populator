#!/usr/bin/env python3
"""
Automatic dependency detection from codebase analysis.

This module provides functionality to:
- Scan Python files for import statements
- Map import names to PyPI package names
- Generate dependency requirements automatically
- Support manual override configurations
"""

import ast
import pathlib
import logging
from typing import Dict, List, Set, Optional, Tuple
import re


class DependencyDetector:
    """Automatically detects Python dependencies from codebase analysis."""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize dependency detector.
        
        Args:
            project_root: Root directory of the project to analyze
        """
        self.project_root = pathlib.Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # Known mappings from import names to PyPI package names
        self.import_to_package_map = {
            'xlwings': 'xlwings',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'requests': 'requests',
            'openpyxl': 'openpyxl',
            'xlrd': 'xlrd',
            'xlsxwriter': 'xlsxwriter',
            'psutil': 'psutil',
            'dateutil': 'python-dateutil',
            'PIL': 'Pillow',
            'cv2': 'opencv-python',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'markdown': 'Markdown',
        }
        
    def detect_dependencies(self, scan_paths: Optional[List[str]] = None) -> Set[str]:
        """
        Detect all external dependencies used in the codebase.
        
        Args:
            scan_paths: List of paths to scan (defaults to ['src/', './'])
            
        Returns:
            Set of package names that need to be installed
        """
        if scan_paths is None:
            scan_paths = ['src/', './']
            
        all_imports = set()
        
        for scan_path in scan_paths:
            path = self.project_root / scan_path
            if path.exists():
                imports = self._scan_directory_for_imports(path)
                all_imports.update(imports)
                
        # Filter to external packages only
        external_packages = self._filter_external_packages(all_imports)
        
        self.logger.info(f"Detected {len(external_packages)} external dependencies: {external_packages}")
        return external_packages
        
    def get_package_name_for_import(self, import_name: str) -> str:
        """
        Get the PyPI package name for a given import name.
        
        Args:
            import_name: The name used in import statements
            
        Returns:
            PyPI package name (same as import_name if no mapping exists)
        """
        return self.import_to_package_map.get(import_name, import_name)
        
    def analyze_file_imports(self, file_path: pathlib.Path) -> Set[str]:
        """
        Extract all import statements from a Python file.
        
        Args:
            file_path: Path to Python file to analyze
            
        Returns:
            Set of imported module names
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse with AST for robust import extraction
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                        
        except SyntaxError:
            # If AST parsing fails, fall back to regex
            imports.update(self._regex_extract_imports(file_path))
        except Exception as e:
            self.logger.warning(f"Error analyzing {file_path}: {e}")
            
        return imports
        
    def _scan_directory_for_imports(self, directory: pathlib.Path) -> Set[str]:
        """
        Recursively scan directory for all Python imports.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Set of all imported module names
        """
        all_imports = set()
        
        if not directory.exists():
            return all_imports
            
        # Find all Python files
        python_files = list(directory.rglob('*.py'))
        
        for file_path in python_files:
            # Skip __pycache__ and hidden files
            if '__pycache__' in str(file_path) or file_path.name.startswith('.'):
                continue
                
            file_imports = self.analyze_file_imports(file_path)
            all_imports.update(file_imports)
            
        return all_imports
        
    def _filter_external_packages(self, imports: Set[str]) -> Set[str]:
        """
        Filter import set to only external packages (not standard library or local).
        
        Args:
            imports: Set of all imported module names
            
        Returns:
            Set of external package names that need installation
        """
        # Standard library modules (Python 3.11+)
        stdlib_modules = {
            'os', 'sys', 'pathlib', 'json', 'csv', 'datetime', 'time', 'random',
            'math', 'statistics', 'collections', 'itertools', 'functools',
            'typing', 'dataclasses', 'enum', 'abc', 'contextlib',
            'logging', 'argparse', 'configparser', 'subprocess', 'shutil',
            'tempfile', 'glob', 'fnmatch', 're', 'string', 'textwrap',
            'unicodedata', 'urllib', 'http', 'email', 'base64', 'hashlib',
            'hmac', 'uuid', 'sqlite3', 'pickle', 'copyreg', 'copy', 'pprint',
            'unittest', 'doctest', 'trace', 'traceback', 'warnings', 'inspect',
            'ast', 'dis', 'importlib', 'pkgutil', 'platform', 'socket',
            'ssl', 'threading', 'multiprocessing', 'queue', 'asyncio',
            'concurrent', 'io', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile'
        }
        
        external_packages = set()
        
        for import_name in imports:
            # Skip standard library modules
            if import_name in stdlib_modules:
                continue
                
            # Skip relative imports and local modules
            if import_name.startswith('.') or import_name == '':
                continue
                
            # Skip modules that look like local packages (heuristic)
            if self._looks_like_local_package(import_name):
                continue
                
            external_packages.add(import_name)
            
        return external_packages
        
    def _looks_like_local_package(self, import_name: str) -> bool:
        """
        Heuristic to determine if an import name refers to a local package.
        
        Args:
            import_name: Module name to check
            
        Returns:
            True if the module appears to be local
        """
        # Check if there's a local directory with this name
        local_paths = [
            self.project_root / 'src' / import_name,
            self.project_root / import_name,
        ]
        
        for path in local_paths:
            if path.exists() and (path.is_dir() or path.with_suffix('.py').exists()):
                return True
                
        return False
        
    def _regex_extract_imports(self, file_path: pathlib.Path) -> Set[str]:
        """
        Fallback regex-based import extraction for files that can't be parsed with AST.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Set of imported module names
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Regex patterns for import statements
            import_patterns = [
                r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    imports.add(match.split('.')[0])
                    
        except Exception as e:
            self.logger.warning(f"Regex extraction failed for {file_path}: {e}")
            
        return imports