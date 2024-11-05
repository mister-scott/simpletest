"""
Control panel component for SimpleTest GUI.
Manages test execution control buttons and running indicator.
"""

import tkinter as tk
from typing import Callable, Dict

class ControlPanel(tk.Frame):
    """
    Panel containing test control buttons and running indicator.
    """
    
    def __init__(self, master: tk.Widget, commands: Dict[str, Callable[[], None]]):
        """
        Initialize ControlPanel.
        
        Args:
            master: Parent widget
            commands: Dictionary of command names and their callback functions
        """
        super().__init__(master)
        
        # Create Run All button
        self.run_all_button = tk.Button(
            self,
            text="Run All",
            command=commands.get('run_all')
        )
        self.run_all_button.pack(side=tk.LEFT)
        
        # Create Run Selected button
        self.run_selected_button = tk.Button(
            self,
            text="Run Selected",
            command=commands.get('run_selected'),
            state=tk.DISABLED
        )
        self.run_selected_button.pack(side=tk.LEFT)
        
        # Create Run Selected Continue button
        self.run_selected_continue_button = tk.Button(
            self,
            text="Run Selected, Continue",
            command=commands.get('run_selected_continue'),
            state=tk.DISABLED
        )
        self.run_selected_continue_button.pack(side=tk.LEFT)
        
        # Create Stop button
        self.stop_button = tk.Button(
            self,
            text="Stop",
            command=commands.get('stop'),
            state=tk.DISABLED  # Initially disabled
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # Create running indicator
        self.running_indicator = tk.Label(
            self,
            text="●",
            fg="gray"
        )
        self.running_indicator.pack(side=tk.LEFT)

    def enable_selected_buttons(self) -> None:
        """Enable buttons that require test selection."""
        if not self.running_indicator.cget('fg') == "red":  # Only if not running
            self.run_selected_button.config(state=tk.NORMAL)
            self.run_selected_continue_button.config(state=tk.NORMAL)

    def disable_selected_buttons(self) -> None:
        """Disable buttons that require test selection."""
        self.run_selected_button.config(state=tk.DISABLED)
        self.run_selected_continue_button.config(state=tk.DISABLED)

    def set_running(self, is_running: bool) -> None:
        """
        Set the running state of the control panel.
        
        Args:
            is_running: True if tests are running, False otherwise
        """
        self.running_indicator.config(fg="red" if is_running else "gray")
        
        if is_running:
            # When running, disable all buttons except stop
            self.run_all_button.config(state=tk.DISABLED)
            self.run_selected_button.config(state=tk.DISABLED)
            self.run_selected_continue_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)  # Enable stop button
        else:
            # When not running, enable run all and disable stop
            self.run_all_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Only enable selected buttons if they were previously enabled
            if self.run_selected_button.cget('state') == 'normal':
                self.run_selected_button.config(state=tk.NORMAL)
                self.run_selected_continue_button.config(state=tk.NORMAL)
            else:
                self.run_selected_button.config(state=tk.DISABLED)
                self.run_selected_continue_button.config(state=tk.DISABLED)
