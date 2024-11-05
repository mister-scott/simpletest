"""
Test runner component for SimpleTest.
Handles test execution and result management.
"""

import importlib.util
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Dict, List, Any, Optional, Callable

class TestItem:
    """
    Represents a single test in the test series.
    """
    
    def __init__(self, name: str, file: str, args: Dict[str, Any] = None):
        """
        Initialize TestItem.
        
        Args:
            name: Name of the test
            file: Python file containing the test
            args: Optional arguments for the test
        """
        self.name = name
        self.file = file
        self.args = args or {}
        self.status = "pending"
        self._observers: List[Callable[[str], None]] = []

    def set_status(self, status: str) -> None:
        """
        Set the test status and notify observers.
        
        Args:
            status: New status value
        """
        self.status = status
        for observer in self._observers:
            observer(status)

    def add_observer(self, observer: Callable[[str], None]) -> None:
        """
        Add a status observer.
        
        Args:
            observer: Callback function taking status parameter
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable[[str], None]) -> None:
        """
        Remove a status observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

class TestRunner:
    """
    Manages test execution and results.
    """
    
    def __init__(self, settings, file_manager, output_manager):
        """
        Initialize TestRunner.
        
        Args:
            settings: Settings instance
            file_manager: FileManager instance
            output_manager: OutputManager instance
        """
        self.settings = settings
        self.file_manager = file_manager
        self.output_manager = output_manager
        self.test_items: List[TestItem] = []
        self.current_test_index: int = 0
        self.is_running_tests: bool = False
        self.stop_requested: bool = False
        self.single_test_mode: bool = False
        self.current_test_thread: Optional[Thread] = None
        self.start_time: Optional[datetime] = None
        self._status_observers: List[Callable[[str], None]] = []
        self._test_observers: List[Callable[[int, str], None]] = []
        self._completion_observers: List[Callable[[], None]] = []

    def load_tests(self) -> None:
        """Load tests from the current test series."""
        self.test_items.clear()
        test_series = self.file_manager.get_test_series()
        
        if not test_series or 'tests' not in test_series:
            return
            
        for test in test_series['tests']:
            test_item = TestItem(test['name'], test['file'], test.get('args', {}))
            self.test_items.append(test_item)

    def run_test(self, index: int) -> None:
        """
        Run a specific test by index.
        
        Args:
            index: Index of the test to run
        """
        if not 0 <= index < len(self.test_items):
            raise ValueError("Invalid test index")
            
        self.single_test_mode = True
        self.is_running_tests = True
        self.stop_requested = False
        self.current_test_index = index
        self.start_time = datetime.now()
            
        test_item = self.test_items[index]
        self._notify_status(f"Running test: {test_item.name}")
        
        try:
            # Import test module
            test_file = test_item.file
            if test_file.endswith('.py'):
                test_file = test_file[:-3]
                
            module_path = self.file_manager.get_test_directory() / f"{test_file}.py"
            spec = importlib.util.spec_from_file_location(f"tests.{test_file}", module_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Start test thread
            self.current_test_thread = Thread(
                target=self._run_test_thread,
                args=(test_module, test_item, index)
            )
            self.current_test_thread.daemon = True
            self.current_test_thread.start()
            
        except Exception as e:
            self.output_manager.write(f"Error running test: {str(e)}\n")
            test_item.set_status("fail")
            self._notify_test_complete(index, "fail")
            self.stop_test_series()

    def _run_test_thread(self, test_module: Any, test_item: TestItem, index: int) -> None:
        """
        Execute test in a separate thread.
        
        Args:
            test_module: Loaded test module
            test_item: TestItem instance
            index: Test index
        """
        try:
            result = test_module.maintest(
                self.settings.get_all(),
                self.test_items,
                self.output_manager.plot,
                **test_item.args
            )
        except Exception as e:
            self.output_manager.write(f"Test encountered an exception: {e}\n")
            result = "fail"
            
        test_item.set_status(result)
        self._notify_test_complete(index, result)

    def run_all_tests(self, starting_index: int = 0) -> None:
        """
        Run all tests starting from the specified index.
        
        Args:
            starting_index: Index to start from
        """
        if not self.is_running_tests:
            self.stop_requested = False
            self.is_running_tests = True
            self.single_test_mode = False
            self.current_test_index = starting_index
            self.start_time = datetime.now()
            self._notify_status("Starting test run")
            self.run_next_test()

    def run_next_test(self) -> None:
        """Run the next test in the series."""
        if self.current_test_index < len(self.test_items):
            self.run_test(self.current_test_index)
        else:
            self.stop_test_series()
            self._notify_status("All tests completed")
            self._notify_completion()

    def stop_test_series(self) -> None:
        """Stop the test series after current test completes."""
        self.stop_requested = True
        self.is_running_tests = False
        self.single_test_mode = False
        self.start_time = None
        self._notify_status("Test series stopped")
        self._notify_completion()

    def add_completion_observer(self, observer: Callable[[], None]) -> None:
        """
        Add a completion observer.
        
        Args:
            observer: Callback function for test completion
        """
        if observer not in self._completion_observers:
            self._completion_observers.append(observer)

    def remove_completion_observer(self, observer: Callable[[], None]) -> None:
        """
        Remove a completion observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._completion_observers:
            self._completion_observers.remove(observer)

    def _notify_completion(self) -> None:
        """Notify observers that testing has completed."""
        for observer in self._completion_observers:
            observer()

    def add_status_observer(self, observer: Callable[[str], None]) -> None:
        """
        Add a status observer.
        
        Args:
            observer: Callback function taking status parameter
        """
        if observer not in self._status_observers:
            self._status_observers.append(observer)

    def add_test_observer(self, observer: Callable[[int, str], None]) -> None:
        """
        Add a test observer.
        
        Args:
            observer: Callback function taking index and status parameters
        """
        if observer not in self._test_observers:
            self._test_observers.append(observer)

    def remove_status_observer(self, observer: Callable[[str], None]) -> None:
        """
        Remove a status observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._status_observers:
            self._status_observers.remove(observer)

    def remove_test_observer(self, observer: Callable[[int, str], None]) -> None:
        """
        Remove a test observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._test_observers:
            self._test_observers.remove(observer)

    def _notify_status(self, status: str) -> None:
        """
        Notify status observers of a status change.
        
        Args:
            status: New status
        """
        for observer in self._status_observers:
            observer(status)

    def _notify_test_complete(self, index: int, status: str) -> None:
        """
        Notify test observers of a test completion.
        
        Args:
            index: Test index
            status: Test status
        """
        for observer in self._test_observers:
            observer(index, status)
        
        if self.single_test_mode:
            # In single test mode, stop after the test completes
            self.is_running_tests = False
            self._notify_completion()
        elif not self.stop_requested:
            # In run all mode, continue to next test if not stopped
            if self.current_test_index < len(self.test_items) - 1:
                self.current_test_index += 1
                self.run_next_test()
            else:
                # If this was the last test
                self.is_running_tests = False
                self._notify_completion()
        else:
            # If stop was requested
            self.is_running_tests = False
            self._notify_completion()
