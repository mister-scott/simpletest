"""
File management component for SimpleTest.
Handles file operations, test series loading, and directory management.
"""

import os
import yaml
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any

class FileManager:
    """
    Manages file operations and test series loading.
    """
    
    def __init__(self, settings):
        """
        Initialize FileManager.
        
        Args:
            settings: Settings instance for configuration
        """
        self.settings = settings
        self.test_directory: Optional[Path] = None
        self.test_series_file: Optional[str] = None
        self.test_series: Dict[str, Any] = {}
        
        # Ensure test series directory exists
        self._ensure_test_series_directory()

    def _ensure_test_series_directory(self) -> None:
        """Create the test series directory if it doesn't exist."""
        test_series_dir = Path('TESTS/test_series')
        test_series_dir.mkdir(parents=True, exist_ok=True)

    def set_test_directory(self, test_series_path: str) -> bool:
        """
        Set the test directory from a test series file or archive.
        
        Args:
            test_series_path: Path to test series YAML or ZIP file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if test_series_path.endswith('.zip'):
                success = self._handle_zip_file(test_series_path)
            else:
                success = self._handle_yaml_file(test_series_path)
            
            if success:
                # Update settings with the new test directory
                self.settings.set('test_directory', str(self.test_directory.absolute()))
                return True
            return False
            
        except Exception as e:
            print(f"Error setting test directory: {e}")
            self.test_directory = None
            self.test_series_file = None
            return False

    def _handle_zip_file(self, zip_path: str) -> bool:
        """
        Handle loading a test series from a ZIP archive.
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            bool: True if successful, False otherwise
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            yaml_file = self._find_test_series_yaml(temp_dir)
            if yaml_file:
                zip_name = Path(zip_path).stem
                new_test_dir = Path('TESTS') / zip_name
                if new_test_dir.exists():
                    shutil.rmtree(new_test_dir)
                shutil.copytree(Path(yaml_file).parent, new_test_dir)
                self.test_directory = new_test_dir
                self.test_series_file = Path(yaml_file).name
                return self.load_test_series()
        return False

    def _handle_yaml_file(self, yaml_path: str) -> bool:
        """
        Handle loading a test series from a YAML file.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        test_dir = Path(yaml_path).parent
        if self._validate_test_series(test_dir):
            self.test_directory = test_dir
            self.test_series_file = Path(yaml_path).name
            return self.load_test_series()
        return False

    def _find_test_series_yaml(self, directory: str) -> Optional[str]:
        """
        Find the first YAML file in a directory or its subdirectories.
        
        Args:
            directory: Directory to search
            
        Returns:
            Optional[str]: Path to YAML file if found, None otherwise
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    return os.path.join(root, file)
        return None

    def _validate_test_series(self, directory: Path) -> bool:
        """
        Validate if a directory contains a valid test series YAML file.
        
        Args:
            directory: Directory to validate
            
        Returns:
            bool: True if valid test series found, False otherwise
        """
        yaml_files = [f for f in directory.glob('*.yaml') if f.is_file()]
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, dict) and 'tests' in content:
                        self.test_series_file = yaml_file.name
                        return True
            except yaml.YAMLError:
                continue
        return False

    def load_test_series(self) -> bool:
        """
        Load the test series from the current test directory.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.test_directory or not self.test_series_file:
                return False
                
            with open(self.test_directory / self.test_series_file, 'r') as f:
                self.test_series = yaml.safe_load(f)
            
            # Load settings from the test directory
            self.settings.load_settings(self.test_directory)
            return True
            
        except Exception as e:
            print(f"Error loading test series: {e}")
            return False

    def get_test_series(self) -> Dict[str, Any]:
        """
        Get the current test series.
        
        Returns:
            Dict[str, Any]: Current test series or empty dict if none loaded
        """
        return self.test_series

    def get_test_directory(self) -> Optional[Path]:
        """
        Get the current test directory.
        
        Returns:
            Optional[Path]: Current test directory or None if not set
        """
        return self.test_directory

    def get_test_series_file(self) -> Optional[str]:
        """
        Get the current test series file name.
        
        Returns:
            Optional[str]: Current test series file name or None if not set
        """
        return self.test_series_file
