"""
Test file for FileManager component.
"""

import os
import tempfile
import zipfile
from pathlib import Path
import yaml
from settings import Settings
from file_manager import FileManager

def create_test_series_yaml(directory: Path) -> None:
    """Create a test series YAML file for testing."""
    test_series = {
        'tests': [
            {
                'name': 'Test 1',
                'file': 'test1.py'
            }
        ]
    }
    with open(directory / 'test_series.yaml', 'w') as f:
        yaml.dump(test_series, f)

def test_file_manager():
    """Run tests for FileManager component."""
    # Setup
    settings = Settings()
    file_manager = FileManager(settings)
    
    # Test 1: Basic YAML file handling
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        create_test_series_yaml(temp_path)
        
        # Test loading YAML file
        result = file_manager.set_test_directory(str(temp_path / 'test_series.yaml'))
        assert result, "Failed to load YAML file"
        assert file_manager.get_test_series_file() == 'test_series.yaml', "Wrong test series file"
        
        # Test test series content
        test_series = file_manager.get_test_series()
        assert 'tests' in test_series, "Test series not loaded correctly"
        assert len(test_series['tests']) == 1, "Wrong number of tests"
    
    # Test 2: ZIP file handling
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / 'test_series.zip'
        
        # Create ZIP file with test series
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            create_test_series_yaml(temp_path)
            zip_file.write(temp_path / 'test_series.yaml', 'test_series.yaml')
        
        # Test loading ZIP file
        result = file_manager.set_test_directory(str(zip_path))
        assert result, "Failed to load ZIP file"
        assert file_manager.get_test_series_file() == 'test_series.yaml', "Wrong test series file from ZIP"
        
        # Test extracted content
        test_series = file_manager.get_test_series()
        assert 'tests' in test_series, "Test series not loaded correctly from ZIP"
        assert len(test_series['tests']) == 1, "Wrong number of tests from ZIP"
    
    print("All file manager tests passed!")

if __name__ == "__main__":
    test_file_manager()
