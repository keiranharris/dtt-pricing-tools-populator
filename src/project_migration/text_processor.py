#!/usr/bin/env python3
"""Text Processing for Project Migration.

Handles content replacement operations across files with pattern matching.
"""

import re
import os
from typing import List, Dict, Any, Tuple
from .migration_logging import get_migration_logger


class TextProcessor:
    """Handles text replacement operations during migration."""
    
    def __init__(self):
        """Initialize text processor."""
        self.logger = get_migration_logger()
    
    def create_replacement_patterns(self, old_name: str, new_name: str) -> List[Tuple[str, str]]:
        """Create comprehensive replacement patterns for project renaming.
        
        Args:
            old_name: Old project name
            new_name: New project name
            
        Returns:
            List of (pattern, replacement) tuples
        """
        patterns = []
        
        # Direct name replacements
        patterns.append((old_name, new_name))
        
        # Underscore versions (for Python modules)
        old_underscore = old_name.replace('-', '_')
        new_underscore = new_name.replace('-', '_')
        if old_underscore != old_name:
            patterns.append((old_underscore, new_underscore))
        
        # CamelCase versions
        old_camel = ''.join(word.capitalize() for word in old_name.split('-'))
        new_camel = ''.join(word.capitalize() for word in new_name.split('-'))
        if old_camel != old_name:
            patterns.append((old_camel, new_camel))
        
        # All uppercase versions (for constants)
        old_upper = old_name.upper().replace('-', '_')
        new_upper = new_name.upper().replace('-', '_')
        if old_upper != old_name.upper():
            patterns.append((old_upper, new_upper))
        
        # URL-safe versions
        patterns.append((old_name.lower(), new_name.lower()))
        
        return patterns
    
    def process_file_content(self, file_path: str, patterns: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Process file content with replacement patterns.
        
        Args:
            file_path: Path to file to process
            patterns: List of (old, new) replacement patterns
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'success': False,
            'changes_made': [],
            'error_message': None,
            'original_content': '',
            'updated_content': ''
        }
        
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            result['original_content'] = original_content
            updated_content = original_content
            
            # Apply each pattern
            for old_pattern, new_pattern in patterns:
                if old_pattern in updated_content:
                    # Count occurrences
                    count = updated_content.count(old_pattern)
                    
                    # Perform replacement
                    updated_content = updated_content.replace(old_pattern, new_pattern)
                    
                    # Record change
                    result['changes_made'].append({
                        'pattern': old_pattern,
                        'replacement': new_pattern,
                        'occurrences': count
                    })
            
            result['updated_content'] = updated_content
            result['success'] = True
            
            # Log changes
            if result['changes_made']:
                total_changes = sum(change['occurrences'] for change in result['changes_made'])
                self.logger.log_debug(f"Text processing for {file_path}: {total_changes} changes")
            
        except Exception as e:
            result['error_message'] = f"Failed to process {file_path}: {str(e)}"
            self.logger.log_error(result['error_message'], e)
        
        return result
    
    def update_readme_file(self, readme_path: str, old_name: str, new_name: str) -> bool:
        """Update README file with new project name and references.
        
        Args:
            readme_path: Path to README file
            old_name: Old project name
            new_name: New project name
            
        Returns:
            True if update successful
        """
        try:
            patterns = self.create_replacement_patterns(old_name, new_name)
            
            # Add specific README patterns
            readme_patterns = [
                # Repository URLs
                (f"https://github.com/keiranharris/{old_name}", 
                 f"https://github.com/keiranharris/{new_name}"),
                # Clone commands
                (f"git clone https://github.com/keiranharris/{old_name}.git",
                 f"git clone https://github.com/keiranharris/{new_name}.git"),
                # Markdown titles
                (f"# {old_name}", f"# {new_name}"),
                (f"## {old_name}", f"## {new_name}"),
            ]
            
            patterns.extend(readme_patterns)
            
            result = self.process_file_content(readme_path, patterns)
            
            if result['success'] and result['changes_made']:
                # Write updated content
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(result['updated_content'])
                
                changes_summary = ', '.join([
                    f"{change['pattern']}({change['occurrences']})" 
                    for change in result['changes_made']
                ])
                
                self.logger.log_operation("README update", True, changes_summary)
                return True
            elif result['success']:
                self.logger.log_debug(f"No changes needed in {readme_path}")
                return True
            else:
                self.logger.log_operation("README update", False, result['error_message'])
                return False
                
        except Exception as e:
            self.logger.log_error(f"README update failed: {str(e)}", e)
            return False
    
    def update_documentation_files(self, docs_dir: str, old_name: str, new_name: str) -> List[str]:
        """Update all documentation files in directory.
        
        Args:
            docs_dir: Documentation directory path
            old_name: Old project name
            new_name: New project name
            
        Returns:
            List of successfully updated files
        """
        updated_files = []
        
        if not os.path.exists(docs_dir):
            self.logger.log_debug(f"Documentation directory not found: {docs_dir}")
            return updated_files
        
        patterns = self.create_replacement_patterns(old_name, new_name)
        
        # Find all documentation files
        doc_extensions = ['.md', '.rst', '.txt']
        for root, dirs, files in os.walk(docs_dir):
            for file in files:
                if any(file.endswith(ext) for ext in doc_extensions):
                    file_path = os.path.join(root, file)
                    
                    try:
                        result = self.process_file_content(file_path, patterns)
                        
                        if result['success'] and result['changes_made']:
                            # Write updated content
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(result['updated_content'])
                            
                            updated_files.append(file_path)
                            self.logger.log_operation("Doc file update", True, 
                                                    os.path.relpath(file_path, docs_dir))
                    
                    except Exception as e:
                        self.logger.log_error(f"Failed to update {file_path}: {str(e)}", e)
        
        self.logger.log_operation("Documentation updates", True, 
                                f"Updated {len(updated_files)} files")
        return updated_files
    
    def update_python_imports(self, src_dir: str, old_module: str, new_module: str) -> List[str]:
        """Update Python import statements.
        
        Args:
            src_dir: Source code directory
            old_module: Old module name
            new_module: New module name
            
        Returns:
            List of successfully updated files
        """
        updated_files = []
        
        if not os.path.exists(src_dir):
            return updated_files
        
        # Python import patterns
        import_patterns = [
            # Direct imports
            (f"import {old_module}", f"import {new_module}"),
            (f"from {old_module}", f"from {new_module}"),
            # String literals in imports
            (f"'{old_module}'", f"'{new_module}'"),
            (f'"{old_module}"', f'"{new_module}"'),
        ]
        
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        result = self.process_file_content(file_path, import_patterns)
                        
                        if result['success'] and result['changes_made']:
                            # Write updated content
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(result['updated_content'])
                            
                            updated_files.append(file_path)
                            self.logger.log_operation("Python imports update", True, 
                                                    os.path.relpath(file_path, src_dir))
                    
                    except Exception as e:
                        self.logger.log_error(f"Failed to update imports in {file_path}: {str(e)}", e)
        
        return updated_files
    
    def validate_text_replacements(self, file_path: str, old_name: str) -> Dict[str, Any]:
        """Validate that text replacements were successful.
        
        Args:
            file_path: Path to file to validate
            old_name: Old name that should no longer exist
            
        Returns:
            Validation results dictionary
        """
        result = {
            'valid': True,
            'remaining_references': [],
            'error_message': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for remaining references to old name
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                if old_name in line:
                    result['remaining_references'].append({
                        'line_number': line_num,
                        'line_content': line.strip()
                    })
            
            result['valid'] = len(result['remaining_references']) == 0
            
        except Exception as e:
            result['error_message'] = f"Validation failed: {str(e)}"
            result['valid'] = False
        
        return result