"""
Test file for TestRunner component.
"""

import tempfile
from pathlib import Path
import yaml
from settings import Settings
from file_manager import FileManager
from output_manager import OutputManager
from test_runner import TestRunner

def create_test_module(directory: Path) -> None:
    """Create a test module file for testing."""
    test_code = """
def maintest(settings, test_items, plot_function, **kwargs):
    return "pass"
"""
    with open(directory / 'test1.py', 'w') as f:
        f.write(test_code)

def create_test_series(directory: Path) -> None:
    """Create a test series file for testing."""
    test_series = {
        'tests': [
            {
                'name': 'Test 1',
                'file': 'test1.py',
                'args': {'param1': 'value1'}
            }
        ]
    }
    with open(directory / 'test_series.yaml', 'w') as f:
        yaml.dump(test_series, f)

def test_test_runner():
    """Run tests for TestRunner component."""
    # Setup
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        create_test_module(temp_path)
        create_test_series(temp_path)
        
        settings = Settings()
        file_manager = FileManager(settings)
        output_manager = OutputManager(settings)
        test_runner = TestRunner(settings, file_manager, output_manager)
        
        # Set up test directory
        file_manager.set_test_directory(str(temp_path / 'test_series.yaml'))
        
        # Test 1: Load tests
        test_runner.load_tests()
        assert len(test_runner.test_items) == 1, "Wrong number of tests loaded"
        assert test_runner.test_items[0].name == "Test 1", "Wrong test name"
        
        # Test 2: Status observer
        statuses = []
        def status_observer(status):
            statuses.append(status)
        
        test_runner.add_status_observer(status_observer)
        
        # Test 3: Test observer
        test_results = []
        def test_observer(index, status):
            test_results.append((index, status))
        
        test_runner.add_test_observer(test_observer)
        
        # Test 4: Run single test
        test_runner.run_test(0)
        test_runner.current_test_thread.join()  # Wait for test to complete
        
        assert len(test_results) == 1, "Test observer not called"
        assert test_results[0][1] == "pass", "Test did not pass"
        
        print("All test runner tests passed!")

if __name__ == "__main__":
    test_test_runner()
