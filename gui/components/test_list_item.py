"""
Test list item component for SimpleTest GUI.
Represents a single test in the test list.
"""

import tkinter as tk
from typing import Callable, Dict, Any

class TestListItem(tk.Frame):
    """
    A GUI component representing a single test in the test list.
    """
    
    STATUS_ICONS = {
        "pass": "✓",
        "softfail": "⚠",
        "fail": "✗",
        "done": "•",
        "pending": "►"
    }
    
    def __init__(self, master: tk.Widget, test_info: Dict[str, Any], index: int, 
                 on_select: Callable[[int], None], font: tuple = ("TkDefaultFont", 12, "normal")):
        """
        Initialize TestListItem.
        
        Args:
            master: Parent widget
            test_info: Dictionary containing test information
            index: Index of this test in the list
            on_select: Callback for when this item is selected
            font: Font configuration tuple
        """
        super().__init__(master)
        
        self.test_name = test_info['name']
        self.index = index
        self.on_select = on_select
        self.status = "pending"
        self.optional_args = test_info.get('args', {})
        self.selected = False
        
        # Create status label
        self.status_label = tk.Label(
            self,
            text=self.STATUS_ICONS["pending"],
            width=2,
            font=font
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Create name label
        self.name_label = tk.Label(
            self,
            text=self.test_name,
            anchor="w",
            font=font
        )
        self.name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind click events
        for widget in [self, self.status_label, self.name_label]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
        
        # Set initial state
        self.deselect()
    
    def set_status(self, status: str) -> None:
        """
        Set the status of the test item.
        
        Args:
            status: New status value
        """
        self.status = status
        self.status_label.config(text=self.STATUS_ICONS.get(status, "•"))
    
    def _on_click(self, event: tk.Event) -> None:
        """
        Handle click events.
        
        Args:
            event: Tkinter event object
        """
        self.on_select(self.index)
        self.select()
    
    def _on_enter(self, event: tk.Event) -> None:
        """
        Handle mouse enter events.
        
        Args:
            event: Tkinter event object
        """
        if not self.selected:
            self._set_hover_state()
    
    def _on_leave(self, event: tk.Event) -> None:
        """
        Handle mouse leave events.
        
        Args:
            event: Tkinter event object
        """
        if not self.selected:
            self.deselect()
    
    def _set_hover_state(self) -> None:
        """Set the hover state appearance."""
        self.config(bg="#e6e6e6")
        self.name_label.config(bg="#e6e6e6")
        self.status_label.config(bg="#e6e6e6")
    
    def select(self) -> None:
        """Visually select this test item."""
        self.selected = True
        self.config(bg="lightblue")
        self.name_label.config(bg="lightblue")
        self.status_label.config(bg="lightblue")
    
    def deselect(self) -> None:
        """Visually deselect this test item."""
        self.selected = False
        self.config(bg="white")
        self.name_label.config(bg="white")
        self.status_label.config(bg="white")
