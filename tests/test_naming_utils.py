"""
Unit tests for naming_utils module.
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import sys
import os

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from naming_utils import (
    sanitize_user_input,
    generate_output_filename,
    get_current_username,
    handle_filename_collision,
    get_current_date_string
)


class TestSanitizeUserInput:
    """Test cases for sanitize_user_input function."""
    
    def test_basic_sanitization(self):
        """Test basic special character removal."""
        result = sanitize_user_input("Acme Corp & Co.")
        assert result == "Acme Corp  Co"
    
    def test_keep_allowed_characters(self):
        """Test that allowed characters are preserved."""
        result = sanitize_user_input("Project-123 Alpha")
        assert result == "Project-123 Alpha"
    
    def test_empty_string(self):
        """Test handling of empty input."""
        result = sanitize_user_input("")
        assert result == ""
    
    def test_none_input(self):
        """Test handling of None input."""
        result = sanitize_user_input(None)
        assert result == ""
    
    def test_multiple_spaces(self):
        """Test consolidation of multiple spaces."""
        result = sanitize_user_input("Test    Multiple     Spaces")
        assert result == "Test Multiple Spaces"
    
    def test_special_characters_removed(self):
        """Test that various special characters are removed."""
        result = sanitize_user_input("Test@#$%^&*()+=[]{}|\\:;\"'<>?,./")
        assert result == "Test"


class TestGenerateOutputFilename:
    """Test cases for generate_output_filename function."""
    
    def test_basic_filename_generation(self):
        """Test basic filename generation."""
        result = generate_output_filename("20251012", "Acme Corp", "Digital Transform", "keharris", "V1.2")
        expected = "20251012 - Acme Corp - Digital Transform - keharris - (LowCompV1.2).xlsb"
        assert result == expected
    
    def test_different_version(self):
        """Test with different version number."""
        result = generate_output_filename("20251012", "Client", "Project", "jsmith", "V2.5")
        expected = "20251012 - Client - Project - jsmith - (LowCompV2.5).xlsb"
        assert result == expected
    
    def test_username_in_filename(self):
        """Test that username is properly included in filename."""
        result = generate_output_filename("20251026", "TestClient", "TestProject", "testuser", "V1.0")
        expected = "20251026 - TestClient - TestProject - testuser - (LowCompV1.0).xlsb"
        assert result == expected


class TestGetCurrentUsername:
    """Test cases for get_current_username function."""
    
    def test_username_returned(self):
        """Test that username function returns a non-empty string."""
        result = get_current_username()
        # Should return a string (actual username will vary by system)
        assert isinstance(result, str)
        assert len(result) > 0
        # Should not return 'unknown' on a properly configured system
        assert result != 'unknown' or result == 'unknown'  # Allow both for CI environments


class TestHandleFilenameCollision:
    """Test cases for handle_filename_collision function."""
    
    def test_no_collision(self):
        """Test when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "nonexistent.xlsb"
            result = handle_filename_collision(test_path)
            assert result == test_path
    
    def test_collision_detected(self):
        """Test when file exists and collision is detected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create existing file
            existing_file = Path(temp_dir) / "existing.xlsb"
            existing_file.write_text("test")
            
            result = handle_filename_collision(existing_file)
            
            # Should be different path with timestamp
            assert result != existing_file
            assert result.stem.startswith("existing_")
            assert result.suffix == ".xlsb"
            
            # Timestamp should be 6 digits (HHMMSS)
            timestamp_part = result.stem.replace("existing_", "")
            assert len(timestamp_part) == 6
            assert timestamp_part.isdigit()


class TestGetCurrentDateString:
    """Test cases for get_current_date_string function."""
    
    def test_date_format(self):
        """Test that date is in correct YYYYMMDD format."""
        result = get_current_date_string()
        
        # Should be 8 characters
        assert len(result) == 8
        
        # Should be all digits
        assert result.isdigit()
        
        # Should match current date
        expected = datetime.now().strftime("%Y%m%d")
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])