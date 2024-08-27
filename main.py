import os
import sys
import yaml
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib
import importlib.util
from datetime import datetime
from threading import Thread
import queue
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple
import tempfile
import zipfile
import shutil

VERSION = "1.2.0"  # Updated version number
FONT_SIZE = 12 
LOGGING_ENABLED = True

def get_font(size_adjustment: int = 0, weight: str = "normal") -> Tuple[str, int, str]:
    """
    Return a font tuple for Tkinter widgets.
    
    :param size_adjustment: Adjustment to the base font size
    :param weight: Font weight (e.g., "normal", "bold")
    :return: Font tuple
    """
    return ("TkDefaultFont", FONT_SIZE + size_adjustment, weight)

class TestListItem(tk.Frame):
    """
    Represents a single test item in the test list GUI.
    """

    def __init__(self, master: tk.Widget, test_name: str, index: int, on_select_callback: Callable[[int], None], **kwargs: Any):
        """
        Initialize a TestListItem.

        :param master: Parent widget
        :param test_name: Name of the test
        :param index: Index of the test in the list
        :param on_select_callback: Function to call when this item is selected
        :param kwargs: Additional keyword arguments for the Frame
        """
        super().__init__(master, **kwargs)
        self.test_name: str = test_name
        self.index: int = index
        self.on_select_callback: Callable[[int], None] = on_select_callback
        self.status: str = "pending"
        self.optional_args: Dict[str, Any] = {}
        self.status_label: tk.Label = tk.Label(self, text="⃝", width=2, font=get_font())
        self.status_label.pack(side=tk.LEFT)
        self.name_label: tk.Label = tk.Label(self, text=test_name, anchor="w",  font=get_font())
        self.name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)
        
        self.deselect()
        
    def set_status(self, status: str) -> None:
        """
        Set the status of the test item and update the status icon.

        :param status: New status of the test item
        """
        self.status = status
        status_icons = {"pass": "✓", "softfail": "⚠", "fail": "✗", "done": "•", "pending": "-"}
        self.status_label.config(text=status_icons.get(status, "•"))
        
    def on_click(self, event: tk.Event) -> None:
        """
        Handle click events on the test item.

        :param event: Tkinter event object
        """
        self.on_select_callback(self.index)
        
    def select(self) -> None:
        """
        Visually select this test item.
        """
        self.config(bg="lightblue")
        self.name_label.config(bg="lightblue")
        self.status_label.config(bg="lightblue")
        
    def deselect(self) -> None:
        """
        Visually deselect this test item.
        """
        self.config(bg="white")
        self.name_label.config(bg="white")
        self.status_label.config(bg="white")

class TestExecutor:
    """
    Main class for the test execution GUI application.
    """

    def __init__(self, master: tk.Tk):
        """
        Initialize the TestExecutor.

        :param master: Root Tkinter window
        """
        self.master: tk.Tk = master
        self.master.title("SimpleTest")
        self.master.geometry("1000x800")
        
        default_font = get_font()
        self.master.option_add("*Font", default_font)
        self.loaded_modules: Dict[str, Any] = {}
        
        self.style: ttk.Style = ttk.Style()
        self.style.configure("TButton", font=get_font())
        self.style.configure("TLabel", font=get_font())

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.default_test_directory: Path = Path('TESTS')
        self.default_output_directory: Path = Path('WORKING')
        self.default_working_directory: Path = Path('OUTPUT')
        self.test_directory: Optional[Path] = None
        self.output_directory: Optional[Path] = None
        self.working_directory: Optional[Path] = None
        
        self.lastrun_path: Path = Path('.lastrun.yaml')
        self.lastrun: Dict[str, Any] = {}

        self.load_lastrun()
        self.create_menu()
        self.create_gui()
        
        self.graph_queue: queue.Queue = queue.Queue()
        self.master.after(100, self.check_graph_queue)
        
        self.current_test_index: int = 0
        self.is_running_tests: bool = False
        self.stop_test_series: bool = False
        self.current_test_thread: Optional[Thread] = None
        self.selected_test_index: Optional[int] = None

        self.start_time: Optional[datetime] = None

        # If there's a test series file in the last run, load it
        if self.lastrun.get('test_series_file'):
            self.set_test_directory(self.lastrun['test_series_file'])
        else:
            # Prompt the user to open a test series
            self.open_test_series()

    def create_menu(self) -> None:
        """
        Create the application menu.
        """
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Test Series", command=self.open_test_series)
        file_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_gui(self) -> None:
        """
        Create the main GUI elements.
        """
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for test list and controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Test list section
        self.test_frame = ttk.Frame(left_frame)
        self.test_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.test_canvas = tk.Canvas(self.test_frame)
        self.test_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.test_scrollbar = ttk.Scrollbar(self.test_frame, orient=tk.VERTICAL, command=self.test_canvas.yview)
        self.test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.test_canvas.configure(yscrollcommand=self.test_scrollbar.set)
        self.test_canvas.bind('<Configure>', lambda e: self.test_canvas.configure(scrollregion=self.test_canvas.bbox("all")))

        self.test_inner_frame = ttk.Frame(self.test_canvas)
        self.test_canvas.create_window((0, 0), window=self.test_inner_frame, anchor="nw")

        # Controls section
        self.control_frame = ttk.Frame(left_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.run_all_button = ttk.Button(self.control_frame, text="Run All", command=self.run_all_tests, style="TButton")
        self.run_all_button.pack(side=tk.LEFT)

        self.run_selected_button = ttk.Button(self.control_frame, text="Run Selected", command=self.run_selected_test, style="TButton")
        self.run_selected_button.pack(side=tk.LEFT)

        self.run_selected_continue_button = ttk.Button(self.control_frame, text="Run Selected, Continue", command=self.run_selected_test_continue, style="TButton")
        self.run_selected_continue_button.pack(side=tk.LEFT)

        self.stop_test_series_button = ttk.Button(self.control_frame, text="Stop", command=self.set_stop_test_series,style="TButton")
        self.stop_test_series_button.pack(side=tk.LEFT)

        # Test running indicator
        self.test_running_indicator = tk.Label(self.control_frame, text="●", fg="gray")
        self.test_running_indicator.pack(side=tk.LEFT)

        # Right frame for output and graph
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Text output section
        self.output_text = ScrolledText(right_frame, height=20, font=get_font())
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib section
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.create_status_bar()

    def create_status_bar(self) -> None:
        """
        Create the status bar at the bottom of the window.
        """
        self.status_bar = tk.Frame(self.master)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.version_label = tk.Label(self.status_bar, text=f"v{VERSION}", font=get_font(-1))
        self.version_label.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.status_bar, text="Ready", font=get_font())
        self.status_label.pack(side=tk.RIGHT, padx=5)

        self.timer_label = tk.Label(self.status_bar, text="", font=get_font())
        self.timer_label.pack(side=tk.RIGHT, padx=5)

    def update_status(self, status: str) -> None:
        """
        Update the status text in the status bar.

        :param status: New status text
        """
        self.status_label.config(text=status)

    def update_timer(self) -> None:
        """
        Update the timer display in the status bar.
        """
        if self.start_time and self.is_running_tests:
            elapsed_time = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
            self.timer_label.config(text=f"Runtime: {time_str}")
            self.master.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="")

    def save_lastrun(self, **kwargs: Any) -> None:
        """
        Save the last run configuration to a file.

        :param kwargs: Configuration key-value pairs to save
        """
        self.lastrun.update(kwargs)
        with open(self.lastrun_path, 'w') as f:
            yaml.dump(self.lastrun, f)

    def load_lastrun(self) -> None:
        """
        Load the last run configuration from a file.
        """
        if self.lastrun_path.exists():
            with open(self.lastrun_path, 'r') as f:
                    self.lastrun = yaml.safe_load(f)
        else:
            self.lastrun = {}
            self.save_lastrun()

    def set_working_directory(self, directory: Optional[str] = None) -> None:
        """
        Set the working directory for the test execution.

        :param directory: Directory path to set as working directory
        """
        specified_working_directory = directory if directory else self.settings.get('working_directory',False)
        self.working_directory = False
        if bool(specified_working_directory):
            try:
                os.makedirs(self.settings['working_directory'],exist_ok=True)
                if Path(self.settings['working_directory']).exists():
                    self.working_directory = Path(self.settings['working_directory'])
                    print(f'Working directory: {self.working_directory.absolute()}')
                else:
                    raise Exception(f'Unable to open {specified_working_directory}.')
            except Exception as e:
                print(e)
        if not self.working_directory:
            print(f'Unable to access working directory!')
    
    def set_output_directory(self, directory: Optional[str] = None) -> None:
        """
        Set the output directory for test results.

        :param directory: Directory path to set as output directory
        """
        specified_output_directory = directory if directory else self.settings.get('output_directory',False)
        self.output_directory = False
        if bool(specified_output_directory):
            try:
                os.makedirs(self.settings['output_directory'],exist_ok=True)
                if Path(self.settings['output_directory']).exists():
                    self.output_directory = Path(self.settings['output_directory'])
                    print(f'Output directory: {self.output_directory.absolute()}')
                else:
                    raise Exception(f'Unable to open {specified_output_directory}.')
            except Exception as e:
                print(e)
        if not self.output_directory:
            print(f'Unable to access output directory!')

    def set_test_directory(self, test_series_file: Optional[str] = None) -> None:
        """
        Set the test directory containing the test series.

        :param test_series_file: Path to the test_series.yaml file or zip archive
        """
        if test_series_file:
            self.clear_module_cache()
            specified_test_series_file = test_series_file
        elif self.lastrun.get('test_series_file', False):
            specified_test_series_file = self.lastrun['test_series_file']
        else:
            specified_test_series_file = None
        
        self.test_directory = None
        
        if specified_test_series_file:
            try:
                if specified_test_series_file.endswith('.zip'):
                    # Handle zip file
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with zipfile.ZipFile(specified_test_series_file, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        
                        test_series_yaml = self.find_test_series_yaml(temp_dir)
                        if test_series_yaml:
                            zip_name = os.path.splitext(os.path.basename(specified_test_series_file))[0]
                            new_test_dir = os.path.join(self.default_test_directory, zip_name)
                            if os.path.exists(new_test_dir):
                                shutil.rmtree(new_test_dir)
                            shutil.copytree(os.path.dirname(test_series_yaml), new_test_dir)
                            self.test_directory = Path(new_test_dir)
                        else:
                            raise Exception(f'The ZIP file does not contain a valid test series.')
                else:
                    # Handle YAML file
                    test_dir = os.path.dirname(specified_test_series_file)
                    if self.validate_test_series(test_dir):
                        self.test_directory = Path(test_dir)
                    else:
                        raise Exception(f'The directory does not contain a valid test series.')
                
                if self.test_directory:
                    print(f'Test directory: {self.test_directory.absolute()}')
                    print(f'Initializing Test Series...')
                    self.initialize_test()
                    self.save_lastrun(test_series_file=str(specified_test_series_file))
            except Exception as e:
                print(f'Unable to open test series: {e}')
                self.test_directory = None

        if not self.test_directory:
            self.open_test_series()

    def find_test_series_yaml(self, directory: str) -> Optional[str]:
        """
        Find the test_series.yaml file in the given directory or its subdirectories.

        :param directory: Directory to search in
        :return: Path to test_series.yaml if found, None otherwise
        """
        for root, dirs, files in os.walk(directory):
            if 'test_series.yaml' in files:
                return os.path.join(root, 'test_series.yaml')
        return None

    def validate_test_series(self, directory: str) -> bool:
        """
        Validate if a directory contains a valid test series.

        :param directory: Directory to validate
        :return: True if the directory contains a valid test series, False otherwise
        """
        return os.path.isfile(os.path.join(directory, 'test_series.yaml'))       
    
    def clear_module_cache(self) -> None:
        """
        Clear the cache of loaded test modules.
        """
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('tests.'):
                del sys.modules[module_name]
        self.loaded_modules.clear()

    def load_settings(self) -> None:
        """
        Load test settings from configuration files.
        """
        if (self.test_directory/'test_settings.yaml').exists():
            with open(self.test_directory/'test_settings.yaml', 'r') as f:
                try: 
                    _settings = yaml.safe_load(f)
                    if _settings.get('test_directory',False):
                        del _settings['test_directory']
                        print('Setting "test_directory" is a reserved parameter, and was ignored.')
                    self.settings = _settings
                except:
                    message=f"WARNING: Unable to locate test_settings.yaml! Tests which depend on test_settings.yaml may misbehave!"
                    message+= f"\n{Path(self.test_directory/'test_settings.yaml').absolute()}"
                    print(message)

        user_test_settings_override = self.test_directory/'user_test_settings_override.yaml'
        if user_test_settings_override.exists():
            with open(user_test_settings_override, 'r') as f:
                user_settings = yaml.safe_load(f)
                self.settings.update(user_settings)

        self.settings['output_directory'] = self.settings.get('output_directory',self.default_output_directory)
        self.settings['working_directory'] = self.settings.get('working_directory',self.default_working_directory)
        self.settings['test_directory'] = str(self.test_directory)
        
        self.set_output_directory()
        self.set_working_directory()

    def initialize_test(self) -> None:
        """
        Initialize the test series by loading settings and test series.
        """
        self.load_settings()
        self.load_test_series()

    def set_stop_test_series(self) -> None:
        """
        Set the flag to stop the test series after the current test.
        """
        if self.is_running_tests:
            self.stop_test_series = True
            self.output_text.insert(tk.END, f"\n! Discontinuing test progression !\n - Test series will stop at conclusion of present test.\n\n")
            self.output_text.see(tk.END)

    def load_test_series(self) -> None:
        """
        Load the test series from the test_series.yaml file.
        """
        self.test_series_loaded = False

        with open(self.test_directory/'test_series.yaml', 'r') as f:
            self.test_series = yaml.safe_load(f)

        # Clear existing test items
        for item in self.test_items if hasattr(self, 'test_items') else []:
            item.destroy()

        self.test_items = []
        for index, test in enumerate(self.test_series['tests']):
            item = TestListItem(self.test_inner_frame, test['name'], index, self.on_test_select)
            item.optional_args = test.get('args',{})
            item.pack(fill=tk.X, padx=5, pady=2)
            self.test_items.append(item)
            
        self.test_canvas.configure(scrollregion=self.test_canvas.bbox("all"))

    def on_test_select(self, index: int) -> None:
        """
        Handle the selection of a test item in the GUI.

        :param index: Index of the selected test item
        """
        if self.selected_test_index is not None:
            self.test_items[self.selected_test_index].deselect()
        
        self.selected_test_index = index
        self.test_items[index].select()
        
        self.run_selected_button.config(state=tk.NORMAL)
        self.run_selected_continue_button.config(state=tk.NORMAL)

    def run_selected_test(self) -> None:
        """
        Run the currently selected test.
        """
        if self.selected_test_index is not None and not self.is_running_tests:
            self.current_test_index = self.selected_test_index
            self.is_running_tests = True
            self.start_time = datetime.now()
            self.update_timer()
            self.test_running_indicator.config(fg="red")
            self.output_text.insert(tk.END, f"\n--- Running selected test: {self.test_items[self.current_test_index].test_name} ---\n\n")
            self.output_text.see(tk.END)
            try:
                self.stop_test_series = True
                self.run_test(self.current_test_index)
            except Exception as e:
                self.output_text.insert(tk.END, f"Error running test: {str(e)}\n")
                self.output_text.see(tk.END)
                self.is_running_tests = False
                self.stop_test_series = False
                self.test_running_indicator.config(fg="gray")
                self.update_status("Test error")
                self.start_time = None

    def run_selected_test_continue(self) -> None:
        """
        Run the selected test and continue with the remaining tests in the series.
        """
        if self.selected_test_index is not None and not self.is_running_tests:
            self.stop_test_series = False
            self.output_text.insert(tk.END, "\n--- Starting new test run from selected test ---\n\n")
            self.output_text.see(tk.END)
            self.run_all_tests(starting_index=self.selected_test_index)

    def run_all_tests(self, starting_index: int = 0) -> None:
        """
        Run all tests in the series, starting from the specified index.

        :param starting_index: Index of the first test to run
        """
        if not self.is_running_tests:
            self.stop_test_series = False
            self.is_running_tests = True
            self.current_test_index = starting_index
            self.start_time = datetime.now()
            self.update_timer()
            if starting_index == 0:
                self.output_text.insert(tk.END, "\n--- Starting new test run ---\n\n")
            self.output_text.see(tk.END)
            self.test_running_indicator.config(fg="red")
            self.run_next_test()

    def curselection(self) -> Tuple[int, ...]:
        """
        Get the currently selected test index.

        :return: Tuple containing the selected test index, or an empty tuple if no test is selected
        """
        return (self.selected_test_index,) if self.selected_test_index is not None else ()


    def open_settings(self) -> None:
        """
        Open the settings dialog.
        """
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")

        row = 0
        entries = {}
        for key, value in self.settings.items():
            ttk.Label(settings_window, text=key, font=get_font()).grid(row=row, column=0, sticky="w")
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(settings_window, variable=var).grid(row=row, column=1)
                entries[key] = var
            else:
                var = tk.StringVar(value=str(value))
                ttk.Entry(settings_window, textvariable=var, font=get_font()).grid(row=row, column=1)
                entries[key] = var
            row += 1

        button_frame = ttk.Frame(settings_window)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Save", command=lambda: self.save_settings(entries, settings_window), style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy, style="TButton").pack(side=tk.LEFT, padx=5)

        # Make the window modal
        settings_window.transient(self.master)
        settings_window.grab_set()
        self.master.wait_window(settings_window)

    def save_settings(self, entries: Dict[str, tk.Variable], settings_window: tk.Toplevel) -> None:
        """
        Save the settings from the settings dialog.

        :param entries: Dictionary of setting names and their corresponding Tkinter variables
        :param settings_window: The settings dialog window to close after saving
        """
        user_settings = {k: v.get() for k, v in entries.items()}
        with open(self.test_directory/'user_test_settings_override.yaml', 'w') as f:
            yaml.dump(user_settings, f)
        self.settings.update(user_settings)
        settings_window.destroy()

    def run_next_test(self) -> None:
        """
        Run the next test in the series.
        """
        if self.current_test_index < len(self.test_items):
            try:
                self.run_test(self.current_test_index)
            except Exception as e:
                self.output_text.insert(tk.END, f"Error running test: {str(e)}\n")
                self.output_text.see(tk.END)
                self.is_running_tests = False
                self.test_running_indicator.config(fg="gray")
        else:
            self.output_text.insert(tk.END, "All tests completed.\n")
            self.output_text.see(tk.END)
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")

    def run_test(self, index: int) -> None:
        """
        Run a specific test by its index.

        :param index: Index of the test to run
        """
        test_item = self.test_items[index]
        test_name = test_item.test_name
        test_args = test_item.optional_args
        self.update_status(f"Test [{test_name}] running")
        
        if self.start_time is None:
            self.start_time = datetime.now()
            self.update_timer()

        try:
            test_info = next(test for test in self.test_series['tests'] if test['name'] == test_name)
        except StopIteration:
            raise Exception(f"Test '{test_name}' not found in test series.")

        self.output_text.insert(tk.END, f"Running test: {test_name}\n")
        self.output_text.see(tk.END)

        try:
            # Strip out .py if added into test file to prevent error when trying to call the file
            if test_info['file'][-3:] == '.py':
                test_info['file'] = test_info['file'][:-3]

            module_path = self.test_directory / f"{test_info['file']}.py"
            spec = importlib.util.spec_from_file_location(f"tests.{test_info['file']}", module_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
        except Exception as e:
            raise Exception(f"Failed to import test module for '{test_name}': {e}")
        
        def plot_function(*args, **kwargs):
            self.graph_queue.put((args, kwargs))
        
        self.current_test_thread = Thread(target=self.run_test_thread, args=(test_module, plot_function, index, test_args))
        self.current_test_thread.daemon = True
        self.current_test_thread.start()

    def run_test_thread(self, test_module: Any, plot_function: Callable, index: int, test_args: Dict[str, Any]) -> None:
        """
        Run a test in a separate thread.

        :param test_module: The loaded test module
        :param plot_function: Function to use for plotting
        :param index: Index of the test
        :param test_args: Additional arguments for the test
        """
        result = test_module.maintest(self.settings, self.test_items, plot_function, **test_args)
        self.master.after(0, self.update_test_result, result, index)

    def update_test_result(self, result: str, index: int) -> None:
        """
        Update the GUI with the result of a test.

        :param result: Result of the test
        :param index: Index of the test
        """
        test_item = self.test_items[index]
        test_item.set_status(result)

        self.output_text.insert(tk.END, f"Test result: {result}\n\n")
        self.output_text.see(tk.END)

        if result == "fail":
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")
            self.update_status("Test failed")
            self.start_time = None
            messagebox.showerror("Test Failed", f"The test '{test_item.test_name}' has failed. Test series stopped.")
        elif self.stop_test_series:
            self.stop_test_series = False
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")
            self.output_text.insert(tk.END, f"Test series stopped.\n\n")
            self.output_text.see(tk.END)
            self.update_status("Test series stopped")
            self.start_time = None
        else:
            self.current_test_index += 1
            if self.current_test_index < len(self.test_items):
                self.run_next_test()
            else:
                self.is_running_tests = False
                self.test_running_indicator.config(fg="gray")
                self.update_status("All tests completed")
                self.start_time = None

    def check_graph_queue(self) -> None:
        """
        Check the graph queue for new plot data and update the graph.
        """        
        try:
            args, kwargs = self.graph_queue.get_nowait()
            self.update_graph(*args, **kwargs)
        except queue.Empty:
            pass
        self.master.after(100, self.check_graph_queue)

    def update_graph(self, *args: Any, **kwargs: Any) -> None:
        """
        Update the graph with new plot data.

        :param args: Positional arguments for plotting
        :param kwargs: Keyword arguments for plotting
        """
        self.ax.clear()
        plot_args = args[0] if args and isinstance(args[0], tuple) else args
        self.ax.plot(*plot_args)
        self.ax.set_title(kwargs.get('title', ''))
        self.ax.set_xlabel(kwargs.get('xlabel', ''))
        self.ax.set_ylabel(kwargs.get('ylabel', ''))
        self.ax.grid(kwargs.get('grid', False))
        self.canvas.draw()

    def redirect_output(self) -> None:
        """
        Redirect stdout to the GUI output text widget and log file.
        """
        class StdoutRedirector:
            def __init__(self, text_widget, output_directory):
                self.text_widget = text_widget
                self.output_directory = output_directory

            def write(self, string):
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)
                if LOGGING_ENABLED:
                    logstring = string.replace("\n", "").replace("\r", "").replace("\t", "")
                    if len(logstring.strip()) > 1:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        logstring = f"{timestamp}: {logstring}\n"
                        with open(self.output_directory/'log.txt', 'a') as f:
                            f.write(logstring)

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.output_text, self.output_directory)

    def on_closing(self) -> None:
        """
        Handle the closing of the application window.
        """
        if self.is_running_tests:
            if tk.messagebox.askokcancel("Quit", "Tests are still running. Do you want to quit?"):
                self.is_running_tests = False
                self.start_time = None
                self.master.quit()
        else:
            self.master.quit()

    def open_test_series(self) -> None:
        """
        Open a dialog to select a new test series YAML file or archive.
        """
        new_test_series_file = filedialog.askopenfilename(
            title="Select Test Series YAML or Archive",
            filetypes=[("Test Series YAML or Archives", "*.yaml *.yml *.zip"), ("All files", "*.*")]
        )
        if new_test_series_file:
            self.set_test_directory(new_test_series_file)

    def reinitialize_test_series(self, new_test_directory: str) -> None:
        """
        Reinitialize the application with a new test series.

        :param new_test_directory: Path to the new test series directory
        """
        # Clear existing data
        self.output_text.delete('1.0', tk.END)
        self.ax.clear()
        self.canvas.draw()

        # Clear module cache
        self.clear_module_cache()

        # Clear sys.modules of test modules
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('tests.'):
                del sys.modules[module_name]

        # Set new test directory and reinitialize
        self.set_test_directory(new_test_directory)

        # Update status
        self.update_status("New test series loaded")



if __name__ == "__main__":
    root = tk.Tk()
    app = TestExecutor(root)
    app.redirect_output()
    root.mainloop()
    sys.exit()