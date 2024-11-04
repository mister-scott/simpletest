"""
SimpleTest - A GUI application for running test series.
This is the refactored version using the new modular architecture.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from core.settings import Settings
from core.file_manager import FileManager
from core.output_manager import OutputManager
from core.test_runner import TestRunner
from gui.components.test_list_item import TestListItem
from gui.components.graph_manager import GraphManager
from gui.components.status_bar import StatusBar
from gui.components.menu_manager import MenuManager
from gui.components.control_panel import ControlPanel

VERSION = "1.2.1"

class TestExecutor:
    """
    Main application class for SimpleTest.
    """
    
    def __init__(self, master: tk.Tk):
        """
        Initialize TestExecutor.
        
        Args:
            master: Root Tkinter window
        """
        self.master = master
        self.master.title("SimpleTest")
        self.master.geometry("1000x800")
        
        # Initialize core components
        self.settings = Settings()
        self.file_manager = FileManager(self.settings)
        self.output_manager = OutputManager(self.settings)
        self.test_runner = TestRunner(self.settings, self.file_manager, self.output_manager)
        
        # Add completion observer
        self.test_runner.add_completion_observer(self.on_tests_complete)
        
        # Configure window
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create menu first
        self.create_menu()
        
        # Create main GUI
        self.create_gui()
        
        # Load last run if available
        self.load_last_run()
        
        # Redirect stdout
        self.redirect_output()

    def create_menu(self) -> None:
        """Create the application menu."""
        menu_commands = {
            'open_test_series': self.open_test_series,
            'exit': self.on_closing,
            'settings': self.open_settings
        }
        self.menu_manager = MenuManager(self.master, menu_commands)

    def create_gui(self) -> None:
        """Create the main GUI elements."""
        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for test list and controls
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Test list section
        self.test_frame = tk.Frame(left_frame)
        self.test_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.test_canvas = tk.Canvas(self.test_frame)
        self.test_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.test_scrollbar = tk.Scrollbar(
            self.test_frame,
            orient=tk.VERTICAL,
            command=self.test_canvas.yview
        )
        self.test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.test_canvas.configure(yscrollcommand=self.test_scrollbar.set)
        self.test_canvas.bind(
            '<Configure>',
            lambda e: self.test_canvas.configure(scrollregion=self.test_canvas.bbox("all"))
        )
        
        self.test_inner_frame = tk.Frame(self.test_canvas)
        self.test_canvas.create_window((0, 0), window=self.test_inner_frame, anchor="nw")
        
        # Control panel
        control_commands = {
            'run_all': self.run_all_tests,
            'run_selected': self.run_selected_test,
            'run_selected_continue': self.run_selected_test_continue,
            'stop': self.stop_test_series
        }
        self.control_panel = ControlPanel(left_frame, control_commands)
        self.control_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Right frame for output and graph
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Text output section
        self.output_text = tk.Text(right_frame, height=20)
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Graph section
        self.graph_manager = GraphManager(right_frame, self.output_manager)
        
        # Add output handler
        self.output_manager.add_output_handler(self.handle_output)
        
        # Status bar
        self.status_bar = StatusBar(self.master, VERSION)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def handle_output(self, text: str) -> None:
        """
        Handle output text from OutputManager.
        
        Args:
            text: Text to display
        """
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def open_test_series(self) -> None:
        """Open a dialog to select a test series file."""
        file_path = filedialog.askopenfilename(
            title="Select Test Series",
            filetypes=[
                ("Test Series Files", "*.yaml;*.yml;*.zip"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            if self.file_manager.set_test_directory(file_path):
                self.test_runner.load_tests()
                self.update_test_list()
                self.status_bar.set_test_series(self.file_manager.get_test_series_file())
            else:
                messagebox.showerror("Error", "Failed to load test series")

    def open_settings(self) -> None:
        """Open the settings dialog."""
        # Create settings window
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.grab_set()  # Make window modal
        
        # Create settings widgets
        current_settings = self.settings.get_all()
        settings_vars = {}
        
        row = 0
        for key, value in current_settings.items():
            if key != 'test_directory':  # Skip test_directory as it's managed internally
                tk.Label(settings_window, text=key).grid(row=row, column=0, sticky="w", padx=5, pady=2)
                
                if isinstance(value, bool):
                    var = tk.BooleanVar(value=value)
                    tk.Checkbutton(settings_window, variable=var).grid(row=row, column=1, padx=5, pady=2)
                else:
                    var = tk.StringVar(value=str(value))
                    tk.Entry(settings_window, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
                
                settings_vars[key] = var
                row += 1
        
        # Create buttons
        button_frame = tk.Frame(settings_window)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        def save_settings():
            new_settings = {k: v.get() for k, v in settings_vars.items()}
            if self.file_manager.get_test_directory():
                self.settings.save_user_settings(self.file_manager.get_test_directory(), new_settings)
            settings_window.destroy()
        
        tk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)

    def update_test_list(self) -> None:
        """Update the test list display."""
        # Clear existing test items
        for widget in self.test_inner_frame.winfo_children():
            widget.destroy()
        
        # Store test items for selection management
        self.test_list_items = []
        
        # Create new test items
        for i, test_item in enumerate(self.test_runner.test_items):
            list_item = TestListItem(
                self.test_inner_frame,
                {'name': test_item.name, 'args': test_item.args},
                i,
                self.on_test_select
            )
            list_item.pack(fill=tk.X, padx=5, pady=2)
            self.test_list_items.append(list_item)
            
            # Add as observer for status updates
            test_item.add_observer(list_item.set_status)

    def on_test_select(self, index: int) -> None:
        """
        Handle test selection.
        
        Args:
            index: Index of selected test
        """
        # Deselect previously selected item
        if hasattr(self, 'selected_test_index'):
            if self.selected_test_index is not None and 0 <= self.selected_test_index < len(self.test_list_items):
                self.test_list_items[self.selected_test_index].deselect()
        
        self.selected_test_index = index
        self.control_panel.enable_selected_buttons()

    def on_tests_complete(self) -> None:
        """Handle test completion."""
        self.control_panel.set_running(False)
        self.status_bar.set_status("Tests completed")
        self.status_bar.stop_timer()

    def load_last_run(self) -> None:
        """Load the last run configuration."""
        # TODO: Implement last run loading
        pass

    def redirect_output(self) -> None:
        """Redirect stdout to the GUI output."""
        redirector = self.output_manager.create_stdout_redirector()
        import sys
        sys.stdout = redirector

    def run_all_tests(self) -> None:
        """Run all tests in the series."""
        if not self.test_runner.is_running_tests:
            self.test_runner.run_all_tests()
            self.control_panel.set_running(True)
            self.status_bar.set_status("Running tests...")
            self.status_bar.start_timer()

    def run_selected_test(self) -> None:
        """Run the currently selected test."""
        if hasattr(self, 'selected_test_index') and not self.test_runner.is_running_tests:
            self.test_runner.run_test(self.selected_test_index)
            self.control_panel.set_running(True)
            self.status_bar.set_status("Running selected test...")
            self.status_bar.start_timer()

    def run_selected_test_continue(self) -> None:
        """Run from selected test and continue with remaining tests."""
        if hasattr(self, 'selected_test_index') and not self.test_runner.is_running_tests:
            self.test_runner.run_all_tests(self.selected_test_index)
            self.control_panel.set_running(True)
            self.status_bar.set_status("Running tests from selection...")
            self.status_bar.start_timer()

    def stop_test_series(self) -> None:
        """Stop the test series."""
        self.test_runner.stop_test_series()
        self.control_panel.set_running(False)
        self.status_bar.set_status("Test series stopped")
        self.status_bar.stop_timer()

    def on_closing(self) -> None:
        """Handle window closing."""
        if self.test_runner.is_running_tests:
            if messagebox.askokcancel("Quit", "Tests are still running. Do you want to quit?"):
                self.test_runner.stop_test_series()
                self.master.quit()
        else:
            self.master.quit()

def main():
    """Main entry point."""
    root = tk.Tk()
    app = TestExecutor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
