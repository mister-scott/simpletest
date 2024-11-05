# SimpleTest

## Overview
SimpleTest is a Python-based application designed to manage and run a series of custom tests. It provides both a graphical user interface and command-line interface for executing tests, viewing results, and managing test settings. Designed with hardware testing in mind, but will support other uses.

## Core Philosophy
SimpleTest is designed in favor of enforcing maintainability of tests and SimpleTest itself.
It does this through:
- Preventing code spaghetti by enforced test segmentation
- Offering a minimal set of features
- Ensuring a full test series can be self contained
- Supporting both GUI and CLI workflows
- Maintaining a modular, maintainable architecture

## Features
- Dual interface support:
  - Graphical user interface for interactive test management
  - Command-line interface for automation and scripting
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
   - `cli_executor.py`: Command-line interface executor
   - `cli.py`: CLI argument parsing and entry point

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
python main_refactored.py
```

Optionally specify a test series to load:
```bash
python main_refactored.py --test-series path/to/test_series.yaml
```

### CLI Mode
Run tests from the command line:
```bash
# Run all tests in a series
python main_refactored.py --cli --test-series path/to/test_series.yaml

# Run a specific test
python main_refactored.py --cli --test-series path/to/test_series.yaml --test "Test Name"
```

### Command Line Arguments
- `--cli`: Run in command-line interface mode
- `--test-series`: Path to test series YAML file or ZIP archive
- `--test`: Name of specific test to run (optional)

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
- CLI components handle command-line operations

When adding new features:
1. Implement core functionality in appropriate core/ module
2. Add GUI support in gui/ if needed
3. Add CLI support in core/cli.py if needed
4. Update tests and documentation

## Requirements
- Python 3.6+
- Required packages:
  - tkinter (for GUI)
  - matplotlib
  - pyyaml

## Examples
See the EXAMPLE_TESTS directory for sample test implementations.
