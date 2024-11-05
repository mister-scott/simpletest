# SimpleTest

## Overview
SimpleTest is a Python-based application designed to manage and run a series of custom tests. It provides both a graphical user interface and headless mode for executing tests, viewing results, and managing test settings. Designed with hardware testing in mind, but will support other uses.

## Core Philosophy
SimpleTest is designed in favor of enforcing maintainability of tests and SimpleTest itself.
It does this through:
- Preventing code spaghetti by enforced test segmentation
- Offering a minimal set of features
- Ensuring a full test series can be self contained
- Supporting both GUI and headless workflows
- Maintaining a modular, maintainable architecture

## Features
- Dual interface support:
  - Graphical user interface for interactive test management
  - Headless mode for automation and scripting
- Ability to run individual tests or a series of tests
- Real-time output display of test results
- Graphing capabilities for test data visualization
- Configurable settings via YAML files
- Status bar displaying program version and test execution timer
- Logging functionality for output preservation
- Structured to support per-testfile unit-testing
- Supported handling of test-series when packaged as a zip
- Memory of last test executed

## Program Structure

### Core Components
1. `core/`: Core functionality modules
   - `settings.py`: Settings management
   - `file_manager.py`: File and test series handling
   - `output_manager.py`: Output and logging management
   - `test_runner.py`: Test execution engine
   - `cli_executor.py`: Headless mode executor
   - `cli.py`: Command-line argument parsing and entry point

### GUI Components
1. `gui/`: GUI-related modules
   - `test_executor.py`: Main GUI application
   - `components/`: Individual GUI components
     - `test_list.py`: Test list display
     - `graph_manager.py`: Graph visualization
     - `status_bar.py`: Status and timing display
     - `menu_manager.py`: Menu system
     - `control_panel.py`: Test control buttons

### Data Directories
1. `TESTS/`: Directory containing test modules and configuration files
   - `test_settings.yaml`: Default settings for the test environment
   - `test_series.yaml`: Defines the order and composition of the test series
   - Individual test modules (e.g., `test_sample.py`, `test_count_and_graph.py`, etc.)
2. `OUTPUT/`: Directory for test output files and logs
3. `WORKING/`: Directory for storing intermediary data

## Usage

### GUI Mode
Run the application without arguments to start in GUI mode:
```bash
python main.py
```

Optionally specify a test series to load:
```bash
python main.py --test-series path/to/test_series.yaml
```

### Headless Mode
Run tests without GUI for automation and scripting:
```bash
# Run all tests in a series
python main.py \
    --test-series path/to/test_series.yaml \
    --test-settings path/to/test_settings.yaml

# Run a specific test
python main.py \
    --test-series path/to/test_series.yaml \
    --test-settings path/to/test_settings.yaml \
    --test "Test Name"

# Specify custom directories
python main.py \
    --test-series path/to/test_series.yaml \
    --test-settings path/to/test_settings.yaml \
    --working-dir /path/to/working \
    --output-dir /path/to/output
```

### Command Line Arguments
- `--test-series`: Path to test series YAML file or ZIP archive
- `--test-settings`: Path to test settings file (required for headless mode)
- `--test`: Name of specific test to run (optional)
- `--working-dir`: Working directory path (optional, defaults to ./WORKING)
- `--output-dir`: Output directory path (optional, defaults to ./OUTPUT)

### Exit Codes (Headless Mode)
- 0: All tests passed
- 1: One or more tests failed
- 2: Configuration error (missing files, invalid YAML, etc.)

## Test Structure
Each test is a Python module that must implement this interface:

```python
def maintest(settings, test_series, plot_function, *args, **kwargs):
    # Test logic here
    # Use settings for configuration
    # Use plot_function for graphing
    return "pass" or "fail" or "softfail" or "done"
```

## Configuration

### test_series.yaml: Defines the tests to be run and their order.
Test series must:
- Be named test_series.yaml
- Be stored in the same directory as the test scripts
- Follow the structure shown below

```yaml
tests:
  - name: Your desired testname
    file: python_test_file_with_dot_py_omitted
  - name: Another testname
    file: another_python_testfile
    args:
      max_count: 3
```

### test_settings.yaml: Contains default settings for the test environment.
```yaml
max_runtime: 60
verbose_output: true
debug_mode: false
```

## Settings Access
Each test script can access settings via the settings dictionary:
```python
settings['output_directory']  # Path to output directory
settings['test_directory']    # Path to test directory
settings['working_directory'] # Path to working directory
```

## Importing Custom Libraries
Due to the threaded execution model, use importlib for custom imports:
```python
import importlib.util

# Import a custom module
spec = importlib.util.spec_from_file_location(
    "threshold_methods.py", settings['test_directory'] + "/example_import.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Use imported functions
assigned_function = module.some_function
```

## Development
The project follows a modular architecture:
- Core components handle business logic
- GUI components handle user interface
- Headless mode components handle automated execution

When adding new features:
1. Implement core functionality in appropriate core/ module
2. Add GUI support in gui/ if needed
3. Add headless mode support in core/cli_executor.py if needed
4. Update tests and documentation

## Requirements
- Python 3.6+
- Required packages:
  - tkinter (for GUI)
  - matplotlib
  - pyyaml

## Examples
See the EXAMPLE_TESTS directory for sample test implementations.

## Missing features
Presently there is no handling for graphs returned from tests in headless mode.