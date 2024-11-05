# SimpleTest Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Core Components](#core-components)
4. [GUI Components](#gui-components)
5. [Adding Features](#adding-features)
6. [Testing](#testing)
7. [Best Practices](#best-practices)

## Architecture Overview

### Component Structure
```
simpletest/
├── core/               # Core functionality
│   ├── settings.py     # Settings management
│   ├── file_manager.py # File operations
│   ├── test_runner.py  # Test execution
│   ├── cli_executor.py # CLI interface
│   └── cli.py         # CLI entry point
├── gui/               # GUI components
│   ├── test_executor.py # Main GUI
│   └── components/     # GUI widgets
└── tests/             # Test files
```

### Design Principles
1. Separation of Concerns
   - Core logic independent of UI
   - GUI components focus on presentation
   - CLI components focus on automation

2. Observer Pattern
   - Components communicate via observers
   - Loose coupling between modules
   - Easy to extend functionality

3. Modular Architecture
   - Each component has a single responsibility
   - Clear interfaces between components
   - Easy to test individual parts

## Development Setup

### Requirements
- Python 3.6+
- Development packages:
  ```bash
  pip install -r requirements.txt
  pip install pytest pytest-cov mypy pylint
  ```

### Environment Setup
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Set up pre-commit hooks

## Core Components

### Settings Component
- Manages application configuration
- Handles user settings overrides
- Provides observer pattern for changes

```python
# Example: Adding a new setting
class Settings:
    def __init__(self):
        self._settings['new_feature'] = default_value
        
    def validate_new_feature(self, value):
        # Add validation logic
```

### FileManager Component
- Handles file operations
- Manages test series loading
- Supports ZIP archives

```python
# Example: Adding new file type support
class FileManager:
    def _handle_new_format(self, file_path):
        # Add handling logic
```

### TestRunner Component
- Manages test execution
- Handles test status updates
- Provides execution control

```python
# Example: Adding new test feature
class TestRunner:
    def run_test_with_feature(self, index):
        # Add feature implementation
```

## GUI Components

### Component Guidelines
1. Inherit from appropriate tk widget
2. Use consistent styling
3. Implement observer pattern
4. Handle cleanup properly

```python
# Example: New GUI component
class NewComponent(tk.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self._setup_ui()
        self._bind_events()
    
    def _setup_ui(self):
        # Create widgets
        
    def _bind_events(self):
        # Bind callbacks
```

### Adding New Controls
1. Create component class
2. Add to TestExecutor
3. Connect to core functionality
4. Update menu if needed

## Adding Features

### Process
1. Define the feature requirements
2. Update core components first
3. Add GUI support if needed
4. Add CLI support if needed
5. Write tests
6. Update documentation

### Example: Adding a Feature
```python
# 1. Core functionality
class TestRunner:
    def new_feature(self):
        # Implementation

# 2. GUI support
class FeatureWidget(tk.Frame):
    def __init__(self, master):
        # Widget implementation

# 3. CLI support
class CLIExecutor:
    def handle_feature(self):
        # CLI implementation
```

## Testing

### Test Structure
```python
# Example test file
def test_component():
    # Setup
    component = Component()
    
    # Test cases
    assert component.method() == expected
    
    # Cleanup
    component.cleanup()
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simpletest

# Run specific test
pytest test_file.py
```

### Test Guidelines
1. Test each component independently
2. Mock dependencies
3. Test edge cases
4. Verify cleanup
5. Check error handling

## Best Practices

### Code Style
1. Follow PEP 8
2. Use type hints
3. Document classes and methods
4. Keep methods focused
5. Use meaningful names

### Error Handling
1. Use specific exceptions
2. Provide helpful error messages
3. Log errors appropriately
4. Clean up resources

### Performance
1. Minimize GUI updates
2. Use appropriate data structures
3. Handle large datasets efficiently
4. Profile when needed

### Documentation
1. Keep API docs updated
2. Document complex logic
3. Include examples
4. Update guides for changes

### Version Control
1. Use meaningful commit messages
2. Create feature branches
3. Write good PR descriptions
4. Keep changes focused

## Contributing
1. Fork the repository
2. Create a feature branch
3. Follow coding standards
4. Add tests
5. Update documentation
6. Submit pull request

## Release Process
1. Update version number
2. Run full test suite
3. Update documentation
4. Create release notes
5. Tag release
6. Build distribution
