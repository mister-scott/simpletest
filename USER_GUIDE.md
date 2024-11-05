# SimpleTest User Guide

## Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Using the GUI](#using-the-gui)
4. [Using the CLI](#using-the-cli)
5. [Creating Tests](#creating-tests)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Installation

1. Ensure Python 3.6+ is installed
2. Install required packages:
   ```bash
   pip install tkinter matplotlib pyyaml
   ```
3. Clone or download the SimpleTest repository
4. Navigate to the SimpleTest directory

## Getting Started

SimpleTest can be run in two modes:
- GUI mode (default) for interactive use
- CLI mode for automation and scripting

### Basic Usage
```bash
# Start GUI mode
python main.py

# Start CLI mode
python main.py --cli --test-series path/to/test_series.yaml
```

## Using the GUI

### Main Window
The GUI consists of several sections:
- Left panel: Test list and control buttons
- Right panel: Output display and graph
- Status bar: Program status and timer

### Test List
- Lists all tests in the current test series
- Click a test to select it
- Status icons show test state:
  - ► (pending)
  - ✓ (pass)
  - ✗ (fail)
  - ⚠ (softfail)
  - • (done)

### Control Buttons
- Run All: Execute all tests in series
- Run Selected: Run only the selected test
- Run Selected, Continue: Run from selected test to end
- Stop: Stop after current test completes

### Output Display
- Shows real-time test output
- Automatically scrolls to show new content
- Logs are saved to OUTPUT/log.txt

### Graph Display
- Shows plots created by tests
- Updates in real-time
- Supports multiple plot types

### Menu Options
- File > Open Test Series: Load a test series
- File > Exit: Close the application
- Edit > Settings: Configure test settings

## Using the CLI

### Basic Commands
```bash
# Run all tests
python main.py --cli --test-series tests/test_series.yaml

# Run specific test
python main.py --cli --test-series tests/test_series.yaml --test "Test Name"

# Show help
python main.py --help
```

### Output
- Test progress is printed to stdout
- Logs are saved to OUTPUT/log.txt
- Graphs are not displayed but data is saved

## Creating Tests

### Basic Test Structure
```python
def maintest(settings, test_items, plot_function, **kwargs):
    # Your test logic here
    
    # Example: Plot some data
    plot_function([1,2,3], [4,5,6], title="My Plot")
    
    # Return test result
    return "pass"  # or "fail", "softfail", "done"
```

### Test Series Configuration
```yaml
tests:
  - name: First Test
    file: test_one
  - name: Second Test
    file: test_two
    args:
      param1: value1
```

## Configuration

### test_settings.yaml
```yaml
# Example settings
max_runtime: 60
verbose_output: true
debug_mode: false
```

### Directory Structure
- TESTS/: Test files and configurations
- OUTPUT/: Test results and logs
- WORKING/: Temporary files and data

## Troubleshooting

### Common Issues

1. Test series not loading
   - Check file path
   - Verify YAML syntax
   - Ensure test files exist

2. Graphs not displaying
   - Check matplotlib installation
   - Verify plot_function arguments
   - Check for plot errors in output

3. Test execution errors
   - Check test return values
   - Verify required modules are imported
   - Check settings configuration

### Getting Help
- Check the error messages in the output
- Review the log file in OUTPUT/log.txt
- Consult the API documentation
- File an issue on the project repository

### Best Practices
1. Always use settings for configuration
2. Handle exceptions in test code
3. Use meaningful test names
4. Document test requirements
5. Keep tests independent
6. Use appropriate status returns
