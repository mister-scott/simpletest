# SimpleTest Headless Mode Feature Specification

## High level instructions:
After each change:
1) Inform the user on what the change is expected to do
2) Test your change
3) Update your progress to HEADLESS_PROGRESS.md

## Overview
Add a non-interactive "headless" mode to SimpleTest that allows running a test series without GUI elements or user interaction. This mode will bypass configuration loading and exit automatically upon completion.

## Command-Line Interface

### New Arguments
```bash
python main.py --headless \
    --test-series path/to/test_series.yaml \
    --test-settings path/to/test_settings.yaml \
    [--working-dir path/to/working] \
    [--output-dir path/to/output]
```

### Required Arguments
- `--headless`: Enable headless mode
- `--test-series`: Path to test series YAML file
- `--test-settings`: Path to test settings YAML file

### Optional Arguments
- `--working-dir`: Working directory path (defaults to ./WORKING)
- `--output-dir`: Output directory path (defaults to ./OUTPUT)

## Behavior

### Initialization
1. Skip loading .lastrun.yaml
2. Skip loading user_test_settings_override.yaml
3. Use only provided test settings file
4. Create working/output directories if they don't exist

### Execution
1. Load and validate test series file
2. Load and validate test settings file
3. Initialize core components with provided settings
4. Start test series execution immediately
5. Run all tests in sequence
6. Exit program after completion

### Output
1. Write test output to console
2. Write logs to output directory
3. Save any test-generated files to working directory
4. Report final test status before exit

### Exit Codes
- 0: All tests passed
- 1: One or more tests failed
- 2: Test series execution error
- 3: Configuration error

## Implementation Requirements

### Core Component Changes

#### Settings Component
```python
class Settings:
    def load_headless(self, settings_file: Path, working_dir: Path, output_dir: Path) -> None:
        """Load settings in headless mode."""
```

#### FileManager Component
```python
class FileManager:
    def load_headless(self, test_series_file: Path) -> bool:
        """Load test series in headless mode."""
```

#### TestRunner Component
```python
class TestRunner:
    def run_headless(self) -> int:
        """Run tests in headless mode and return exit code."""
```

### CLI Changes
```python
def parse_args():
    # Add new arguments:
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--test-settings', type=str)
    parser.add_argument('--working-dir', type=str)
    parser.add_argument('--output-dir', type=str)
```

## Questions for Clarification

1. Error Handling:
   - Should test failures stop execution or continue to next test?
      - Test failures already have two modes; 'softfail', which is effectively a fail and continue, and 'fail', which tells the program to halt execution. If the program stops due to 'fail', but not due to exception errors, the windows return code should be 1. If the test series completes without a 'fail', a return code of 0 should be issued.
   - How should setup errors (missing files, invalid YAML) be handled?
      - Setup errors should result in the error being reported in the logfile, printed in terminal, and a return code of 2.

2. Output Format:
   - Should console output be machine-readable (e.g., JSON) or human-readable?
      - The output should be the text visible in the terminal, for which a copy should be redirected to the log.txt file. In the gui, the terminal output of tests is typically redirected to a  within the gui. In headless mode, the output goes to the executing window instead.
   - Should test timing information be included?
      - No.

3. Resource Cleanup:
   - Should working directory be cleaned up after execution?
      - No.
   - How should existing files in output directory be handled?
      - They should be ignored.

4. Test Results:
   - Should a summary file be generated?
      - No.
   - What format should test results be saved in?
      - That will be handled by the test files themselves.

5. Logging:
   - Should log levels be configurable?
      - No.
   - Should logs go to stdout, file, or both?
      - Both.

## Example Usage

### Basic Usage
```bash
python main.py --headless \
    --test-series tests/my_series.yaml \
    --test-settings tests/settings.yaml
```

### Custom Directories
```bash
python main.py --headless \
    --test-series tests/my_series.yaml \
    --test-settings tests/settings.yaml \
    --working-dir /tmp/work \
    --output-dir /var/log/tests
```

## Implementation Steps

1. Core Changes:
   - Add headless mode support to Settings
   - Add headless loading to FileManager
   - Add headless execution to TestRunner
   - Update OutputManager for non-GUI operation

2. CLI Changes:
   - Add new command-line arguments
   - Add headless mode execution path
   - Add exit code handling

3. Testing:
   - Add unit tests for headless mode
   - Add integration tests
   - Add command-line argument tests

4. Documentation:
   - Update README.md
   - Update API documentation
   - Add headless mode examples

## Success Criteria

1. Can run test series without GUI or user interaction
2. Properly loads specified configuration files
3. Executes all tests in series
4. Provides appropriate exit codes
5. Generates expected output and logs
6. Handles errors appropriately
7. Cleans up resources properly
