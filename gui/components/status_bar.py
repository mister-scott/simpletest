"""
Status bar component for SimpleTest GUI.
Displays application status, timer, and version information.
"""

import tkinter as tk
from datetime import datetime
from typing import Optional

class StatusBar(tk.Frame):
    """
    Status bar widget showing application status and information.
    """
    
    def __init__(self, master: tk.Widget, version: str, font: tuple = ("TkDefaultFont", 12, "normal")):
        """
        Initialize StatusBar.
        
        Args:
            master: Parent widget
            version: Application version string
            font: Font configuration tuple
        """
        super().__init__(master)
        self.small_font = (font[0], font[1]-1, font[2])
        
        # Version label
        self.version_label = tk.Label(
            self,
            text=f"v{version}",
            font=self.small_font
        )
        self.version_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Test series label
        self.test_series_label = tk.Label(
            self,
            text="",
            font=self.small_font
        )
        self.test_series_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status label
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=font
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Timer label
        self.timer_label = tk.Label(
            self,
            text="",
            font=font
        )
        self.timer_label.pack(side=tk.RIGHT, padx=5)
        
        self.start_time: Optional[datetime] = None
        self.timer_running = False

    def set_test_series(self, test_series: Optional[str]) -> None:
        """
        Set the test series text.
        
        Args:
            test_series: Test series name or None
        """
        if test_series:
            self.test_series_label.config(text=f"Test Series: {test_series}")
        else:
            self.test_series_label.config(text="")

    def set_status(self, status: str) -> None:
        """
        Set the status text.
        
        Args:
            status: Status text to display
        """
        self.status_label.config(text=status)

    def start_timer(self) -> None:
        """Start the timer."""
        self.start_time = datetime.now()
        self.timer_running = True
        self._update_timer()

    def stop_timer(self) -> None:
        """Stop the timer."""
        self.timer_running = False
        self.timer_label.config(text="")
        self.start_time = None

    def _update_timer(self) -> None:
        """Update the timer display."""
        if self.timer_running and self.start_time:
            elapsed_time = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
            self.timer_label.config(text=f"Runtime: {time_str}")
            
            if self.timer_running:
                self.after(1000, self._update_timer)
