"""
CLI executor component for SimpleTest.
Handles command-line test execution.
"""

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
        
        # Add output handler
        self.output_manager.add_output_handler(self.handle_output)

    def handle_output(self, text: str) -> None:
        """
        Handle output text from OutputManager.
        
        Args:
            text: Text to display
        """
        print(text, end='')

    def on_tests_complete(self) -> None:
        """Handle test completion."""
        print("\nTests completed.")

    def run(self, test_series_file: str, selected_test: str = None) -> int:
        """
        Run tests in CLI mode.
        
        Args:
            test_series_file: Path to test series file
            selected_test: Name of specific test to run (optional)
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        if not self.file_manager.set_test_directory(test_series_file):
            print(f"Error: Failed to load test series from {test_series_file}")
            return 1

        self.test_runner.load_tests()
        
        if selected_test:
            # Find and run specific test
            for i, test_item in enumerate(self.test_runner.test_items):
                if test_item.name == selected_test:
                    print(f"Running test: {selected_test}")
                    self.test_runner.run_test(i)
                    return 0
            print(f"Error: Test '{selected_test}' not found in test series")
            return 1
        else:
            # Run all tests
            print("Running all tests...")
            self.test_runner.run_all_tests()
            return 0
