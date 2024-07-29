# SimpleTest

## Overview
Test Executor is a Python-based GUI application designed to manage and run a series of custom tests. It provides a user-friendly interface for executing tests, viewing results, and managing test settings. Designed with hardware testing in mind, but will support other uses.

## Features
- Graphical user interface for test management and execution
- Ability to run individual tests or a series of tests
- Real-time output display of test results
- Graphing capabilities for test data visualization
- Configurable settings via YAML files
- Status bar displaying program version and test execution timer
- Logging functionality for output preservation
- Structured as to support per-testfile unit-testing

## Program Structure

### Main Components
1. `main.py`: The main script that initializes and runs the application.
2. `tests/`: Directory containing test modules and configuration files.
   - `test_settings.yaml`: Default settings for the test environment.
   - `test_series.yaml`: Defines the order and composition of the test series.
   - Individual test modules (e.g., `test_sample.py`, `test_count_and_graph.py`, etc.)
3. `output/`: Directory for test output files and logs.
4. `data/`: Directory for storing data required by or generated during tests.

### Key Classes
- `TestExecutor`: Main class that handles the GUI and test execution logic.
- `TestListItem`: Custom widget for displaying individual tests in the GUI.

## Test Structure
Each test is a Python module placed in the `tests/` directory. Tests should follow this structure:

```python
def maintest(settings, test_series, plot_function):
    # Test logic here
    # Use settings for configuration
    # Use plot_function for graphing
    return "pass" or "fail" or "softfail" or "done"
```

## Configuration

test_settings.yaml: Contains default settings for the test environment.

test_series.yaml: Defines the tests to be run and their order.

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
* TEST_DIR: Specify the location of the tests directory.

### Adding New Tests

Create a new Python file in the tests/ directory.

Implement the maintest function as described in the Test Structure section.

Add the new test to test_series.yaml.

### Logging
When LOGGING_ENABLED is set to True, all console output is also written to output/log.txt. This feature helps in preserving test results and debugging.

## Notes

Ensure all required Python libraries are installed (tkinter, matplotlib, pyyaml).

The application is designed to be modular, allowing easy addition of new tests and features.