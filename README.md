# SimpleTest

## Overview
Simpletest is a Python-based GUI application designed to manage and run a series of custom tests. It provides a user-friendly interface for executing tests, viewing results, and managing test settings. Designed with hardware testing in mind, but will support other uses.

## Core Philosophy
Simpletest is designed in favor of enforcing maintainability of tests and simpletest itself.
It does this through:
- Preventing code spaghetti by enforced test segmentation
- Offering a minimal set of features
- Ensuring a full test series can be self contained

## Features
- Graphical user interface for test management and execution
- Ability to run individual tests or a series of tests
- Real-time output display of test results
- Graphing capabilities for test data visualization
- Configurable settings via YAML files
- Status bar displaying program version and test execution timer
- Logging functionality for output preservation
- Structured as to support per-testfile unit-testing
- Supported handling of test-series when packaged as a zip
- Memory of last test executed

## Program Structure

### Main Components
1. `main.py`: The main script that initializes and runs the application.
2. `TESTS/`: Directory containing test modules and configuration files. Accessible in any test script by ```settings['test_directory']```.
   - `test_settings.yaml`: Default settings for the test environment.
   - `test_series.yaml`: Defines the order and composition of the test series.
   - Individual test modules (e.g., `test_sample.py`, `test_count_and_graph.py`, etc.)
3. `OUTPUT/`: Directory for test output files and logs. Accessible in any test script by ```settings['output_directory']```.
4. `WORKING/`: Directory for storing intermediary data required for ongoing and subsequent tests, or for generating output. Accessible in any test script by  ```settings['output_directory']```.

## Test Structure
Each test is a Python module placed in the `tests/` directory. Tests should follow this structure:

```python
def maintest(settings, test_series, plot_function, *args, **kwargs):
    # Test logic here
    # Use settings for configuration
    # Use plot_function for graphing
    return "pass" or "fail" or "softfail" or "done"
```

## Access to settings and test paths
Each test script may access settings from the passed dictionary settings.
The keys 'output_directory', 'working_directory', and 'test_directory' are reserved,
as they are called to direct where the script may find each location.

```python
settings['output_directory']
settings['test_directory']
settings['working_directory']
```
## Configuration

### test_series.yaml: Defines the tests to be run and their order.
Test series must:
- Be named test_series.yaml
- Be stored in the same directory as the test scripts
- The contents must be structured like that illustrated below

The same python test file may be called multiple times with different names and
arguments to permit more flexible execution.

Any args will be passed by the kwargs dictionary-like object to the test.

```yaml
tests:
  - name: Your desired testname
    file: python_test_file_with_dot_py_omitted
  - name: Another testname
    file: another_python_testfile
    args:
      max_count: 3
```
Review the examples availabe in the provided EXAMPLE_TESTS folder for further details.

### test_settings.yaml: Contains default settings for the test environment.
Test settings are a collection of operator-configurable parameters.
These permit things like test-station specific configuration of hardware (IP address, etc).

If a user modifies the values from the interface, a user-override file is created called 'user_test_settings_override.yaml'.
This override file is loaded on run if present.

Test settings must:
- Be named test_settings.yaml
- Be stored in the same directory as the test scripts
- The contents must be structured like that illustrated below
```yaml
max_runtime: 60
verbose_output: true
debug_mode: false
```

## Features

* Test Execution: Run individual tests or the entire series.
* Real-time Output: View test progress and results in real-time.
* Graphing: Tests can generate graphs using the provided plot_function.
* Settings Management: Modify test settings through a GUI interface.
* Status Tracking: Visual indicators for test status (pass, fail, running, etc.).
* Logging: Option to save console output to output/log.txt.


## Usage

Run main.py to start the application.

Use the GUI to select and run tests.

View results in the output pane and any generated graphs.

Adjust settings as needed through the settings menu.

### Global Variables

* VERSION: Current version of the application.
* FONT_SIZE: Global font size for the GUI.
* LOGGING_ENABLED: When True, writes console output to output/log.txt.

### Adding New Tests

Create a new Python file in the tests/ directory.

Implement the maintest function as described in the Test Structure section.

Add the new test to test_series.yaml.

### Logging
When LOGGING_ENABLED is set to True, all console output is also written to output/log.txt. This feature helps in preserving test results and debugging.

### Imports
This test demonstrates use of imports and functions for simpletest.
 
#### Installed libraries
Installed libraries are imported in the expected manner as shown above
using the 'import numpy as np' style.

#### Declared inside test file
Functions declared inside of test files or inside of maintest will be
available to maintest.

#### Import of a .py custom library (importlib method)
Due to the use of threads in managing test-execution, importing files 
via folder reference tends to be problematic. 
Use of importlib.util as a workaround rememdies this problem.
Example:
```python
# Create the 'spec' from the target import file 
spec = importlib.util.spec_from_file_location(
    "threshold_methods.py", settings['test_directory'] + "/example_import.py")
# Read the spec in as a module, and assing it to a variable
module = importlib.util.module_from_spec(spec)
# Execute the code in the target library, making it ready for use
spec.loader.exec_module(module)
# (Optional) Assign a function from the library to a separate variable
assigned_exclaim = module.assigned_exclaim
```

#### Import of a python project (Directory import with multiple .py files within)
I'm only aware of two methods to import full python projects as libraries.

Option 1: Typically the easier of the two is to build the project into a package and 
install it. Instructions on how to do this are readily available online.

Option 2: The alternative is to copy all the desired functions into a single file,
and import it explicitly using the importlib method. Not typically recommended.

## Notes

Ensure all required Python libraries are installed (tkinter, matplotlib, pyyaml).