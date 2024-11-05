"""
CLI executor component for SimpleTest.
Handles command-line test execution in headless mode.
"""

import sys
from datetime import datetime
from pathlib import Path
from core.settings import Settings
from core.file_manager import FileManager
from core.output_manager import OutputManager
from core.test_runner import TestRunner

class CLIExecutor:
    """
    Command-line interface for SimpleTest.
    """
    
    def __init__(self):
        """Initialize CLIExecutor."""
        self.settings = Settings()
        self.file_manager = FileManager(self.settings)
        self.output_manager = OutputManager(self.settings)
        self.test_runner = TestRunner(self.settings, self.file_manager, self.output_manager)
        
        # Add completion observer
        self.test_runner.add_completion_observer(self.on_tests_complete)
        
        # Add test observer for tracking failures
        self.test_runner.add_test_observer(self.on_test_complete)
        
        # Track test failures
        self.had_failures = False

    def redirect_output(self) -> None:
        """
        Redirect stdout to both terminal and log file.
        """
        class StdoutRedirector:
            def __init__(self, output_directory):
                self.output_directory = output_directory
                self.terminal = sys.__stdout__

            def write(self, string):
                # Write to terminal
                self.terminal.write(string)
                self.terminal.flush()
                
                # Write to log file
                if self.output_directory:
                    logstring = string.replace("\n", "").replace("\r", "").replace("\t", "")
                    if len(logstring.strip()) > 1:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        logstring = f"{timestamp}: {logstring}\n"
                        with open(self.output_directory/'log.txt', 'a') as f:
                            f.write(logstring)

            def flush(self):
                self.terminal.flush()

        # Get output directory from settings
        output_dir = self.settings.get('output_directory')
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
        # Set up redirection
        sys.stdout = StdoutRedirector(output_dir)

    def restore_output(self) -> None:
        """Restore original stdout."""
        sys.stdout = sys.__stdout__

    def on_tests_complete(self) -> None:
        """Handle test completion."""
        print("\nTests completed.")

    def on_test_complete(self, index: int, status: str) -> None:
        """
        Handle individual test completion.
        
        Args:
            index: Test index
            status: Test status
        """
        if status == "fail":
            self.had_failures = True

    def run_headless(self, test_series_file: str, test_settings_file: str,
                    working_dir: str = None, output_dir: str = None,
                    selected_test: str = None) -> int:
        """
        Run tests in headless mode.
        
        Args:
            test_series_file: Path to test series file
            test_settings_file: Path to test settings file
            working_dir: Optional working directory path
            output_dir: Optional output directory path
            selected_test: Optional name of specific test to run
            
        Returns:
            int: Exit code (0 for success, 1 for test failure, 2 for configuration error)
        """
        try:
            # Set directories if provided
            if working_dir:
                self.settings.set('working_directory', Path(working_dir))
            if output_dir:
                self.settings.set('output_directory', Path(output_dir))
            
            # Load test settings
            if not self.settings.load_headless(Path(test_settings_file)):
                print(f"Error: Failed to load test settings from {test_settings_file}")
                return 2
            
            # Load test series
            if not self.file_manager.set_test_directory(test_series_file):
                print(f"Error: Failed to load test series from {test_series_file}")
                return 2
            
            # Set up output redirection
            self.redirect_output()
            
            self.test_runner.load_tests()
            
            if selected_test:
                # Find and run specific test
                for i, test_item in enumerate(self.test_runner.test_items):
                    if test_item.name == selected_test:
                        print(f"Running test: {selected_test}")
                        self.test_runner.run_test(i)
                        # Wait for test to complete
                        while self.test_runner.is_running_tests:
                            pass
                        return 1 if self.had_failures else 0
                print(f"Error: Test '{selected_test}' not found in test series")
                return 2
            else:
                # Run all tests
                print("Running all tests...")
                self.test_runner.run_all_tests()
                # Wait for tests to complete
                while self.test_runner.is_running_tests:
                    pass
                return 1 if self.had_failures else 0
                
        except Exception as e:
            print(f"Error in headless execution: {e}")
            return 2
        finally:
            # Restore original stdout
            self.restore_output()
