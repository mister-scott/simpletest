"""
Settings management component for SimpleTest.
Handles loading, saving, and updating application settings with observer pattern support.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Callable, Optional

class Settings:
    """
    Manages application settings with observer pattern for change notifications.
    """
    
    def __init__(self):
        """Initialize Settings with empty configuration and observers list."""
        self._settings: Dict[str, Any] = {}
        self._observers: List[Callable[[str, Any], None]] = []
        
        # Define default directories
        self._default_output_directory = Path('OUTPUT')
        self._default_working_directory = Path('WORKING')
        self._default_test_directory = Path('TESTS')
        
        # Create default directories and set initial settings
        self._create_default_directories()
        self._initialize_default_settings()

    def _create_default_directories(self) -> None:
        """Create default directories if they don't exist."""
        try:
            self._default_output_directory.mkdir(exist_ok=True)
            self._default_working_directory.mkdir(exist_ok=True)
            self._default_test_directory.mkdir(exist_ok=True)
            print(f"Created default directories: {self._default_output_directory}, {self._default_working_directory}, {self._default_test_directory}")
        except Exception as e:
            print(f"Error creating default directories: {e}")

    def _initialize_default_settings(self) -> None:
        """Initialize settings with default values."""
        self._settings = {
            'output_directory': str(self._default_output_directory.absolute()),
            'working_directory': str(self._default_working_directory.absolute()),
            'test_directory': str(self._default_test_directory.absolute())
        }

    def load_settings(self, test_directory: Path) -> None:
        """
        Load settings from test_settings.yaml and user_test_settings_override.yaml.
        
        Args:
            test_directory: Path to the test directory containing settings files
        """
        # Update test directory first
        self._settings['test_directory'] = str(test_directory.absolute())
        
        # Load main settings file
        settings_file = test_directory / 'test_settings.yaml'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = yaml.safe_load(f)
                    if settings:  # Check if settings is not None
                        if settings.get('test_directory', False):
                            del settings['test_directory']
                            print('Setting "test_directory" is a reserved parameter, and was ignored.')
                        self._settings.update(settings)
            except Exception as e:
                print(f"WARNING: Error loading test_settings.yaml: {e}")
                print(f"Tests which depend on test_settings.yaml may misbehave!")
        
        # Load user override settings
        user_settings_file = test_directory / 'user_test_settings_override.yaml'
        if user_settings_file.exists():
            try:
                with open(user_settings_file, 'r') as f:
                    user_settings = yaml.safe_load(f)
                    if user_settings:  # Check if user_settings is not None
                        if user_settings.get('test_directory', False):
                            del user_settings['test_directory']
                        self._settings.update(user_settings)
            except Exception as e:
                print(f"WARNING: Error loading user_test_settings_override.yaml: {e}")
        
        # Ensure directory settings are absolute paths and strings
        self._settings['output_directory'] = str(Path(self._settings.get('output_directory', self._default_output_directory)).absolute())
        self._settings['working_directory'] = str(Path(self._settings.get('working_directory', self._default_working_directory)).absolute())
        
        # Create directories if they don't exist
        Path(self._settings['output_directory']).mkdir(exist_ok=True)
        Path(self._settings['working_directory']).mkdir(exist_ok=True)
        
        # Notify observers of settings load
        self._notify_observers('all', None)

    def save_user_settings(self, test_directory: Path, settings: Dict[str, Any]) -> None:
        """
        Save user settings override to file.
        
        Args:
            test_directory: Path to the test directory
            settings: Dictionary of settings to save
        """
        if settings.get('test_directory', False):
            del settings['test_directory']
        
        # Convert any Path objects to strings
        settings_to_save = {}
        for key, value in settings.items():
            if isinstance(value, Path):
                settings_to_save[key] = str(value.absolute())
            else:
                settings_to_save[key] = value
        
        user_settings_file = test_directory / 'user_test_settings_override.yaml'
        with open(user_settings_file, 'w') as f:
            yaml.dump(settings_to_save, f)
        
        self._settings.update(settings_to_save)
        self._notify_observers('all', None)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default if not found
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value and notify observers.
        
        Args:
            key: Setting key to set
            value: Value to set
        """
        # Convert Path objects to strings for directory settings
        if isinstance(value, Path):
            value = str(value.absolute())
        self._settings[key] = value
        self._notify_observers(key, value)

    def add_observer(self, observer: Callable[[str, Any], None]) -> None:
        """
        Add an observer to be notified of setting changes.
        
        Args:
            observer: Callback function taking key and value parameters
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable[[str, Any], None]) -> None:
        """
        Remove an observer from notifications.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, key: str, value: Any) -> None:
        """
        Notify all observers of a setting change.
        
        Args:
            key: Setting key that changed
            value: New value
        """
        for observer in self._observers:
            observer(key, value)

    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.
        
        Returns:
            Dictionary of all settings
        """
        return self._settings.copy()
