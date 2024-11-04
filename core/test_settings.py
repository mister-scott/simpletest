"""
Test file for Settings component.
"""

import os
import tempfile
from pathlib import Path
import yaml
from settings import Settings

def test_settings():
    """Run tests for Settings component."""
    # Setup
    settings = Settings()
    
    # Test 1: Default initialization
    assert len(settings.get_all()) == 0, "Settings should be empty on initialization"
    
    # Test 2: Basic get/set
    settings.set('test_key', 'test_value')
    assert settings.get('test_key') == 'test_value', "Basic get/set failed"
    
    # Test 3: Observer pattern
    changes = []
    def observer(key, value):
        changes.append((key, value))
    
    settings.add_observer(observer)
    settings.set('observed_key', 'observed_value')
    assert len(changes) == 1, "Observer not notified"
    assert changes[0] == ('observed_key', 'observed_value'), "Observer received wrong values"
    
    # Test 4: Settings file loading
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test settings file
        test_settings = {
            'key1': 'value1',
            'key2': 42,
            'test_directory': 'should_be_ignored'
        }
        
        with open(temp_path / 'test_settings.yaml', 'w') as f:
            yaml.dump(test_settings, f)
            
        settings.load_settings(temp_path)
        
        assert settings.get('key1') == 'value1', "Failed to load settings file"
        assert settings.get('key2') == 42, "Failed to load settings file"
        assert settings.get('test_directory') == str(temp_path), "test_directory not set correctly"
    
    print("All settings tests passed!")

if __name__ == "__main__":
    test_settings()
