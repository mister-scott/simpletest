"""
Test list component for SimpleTest GUI.
Manages the scrollable list of test items.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Dict, Any
from gui.components.test_list_item import TestListItem

class TestList(tk.Frame):
    """
    A scrollable list of test items with selection handling.
    """
    
    def __init__(self, master: tk.Widget, on_select: Callable[[int], None]):
        """
        Initialize TestList.
        
        Args:
            master: Parent widget
            on_select: Callback for when a test is selected
        """
        super().__init__(master)
        self.on_select = on_select
        self.test_items: List[TestListItem] = []
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create inner frame for test items
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw"
        )
        
        # Configure canvas to expand with window
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Pack scrollbar and canvas
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """
        Handle canvas resize events.
        
        Args:
            event: Configure event
        """
        # Update the inner frame width to match canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """
        Handle mousewheel scrolling.
        
        Args:
            event: Mousewheel event
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self) -> None:
        """Clear all test items from the list."""
        for item in self.test_items:
            item.destroy()
        self.test_items.clear()

    def add_test(self, test_info: Dict[str, Any], index: int) -> TestListItem:
        """
        Add a test item to the list.
        
        Args:
            test_info: Dictionary containing test information
            index: Index of the test in the list
            
        Returns:
            TestListItem: The created test item
        """
        test_item = TestListItem(
            self.inner_frame,
            test_info,
            index,
            self.on_select
        )
        test_item.pack(fill=tk.X, padx=5, pady=2)
        self.test_items.append(test_item)
        return test_item

    def get_item(self, index: int) -> TestListItem:
        """
        Get a test item by index.
        
        Args:
            index: Index of the test item
            
        Returns:
            TestListItem: The test item at the specified index
        """
        return self.test_items[index]

    def deselect_all(self) -> None:
        """Deselect all test items."""
        for item in self.test_items:
            item.deselect()
