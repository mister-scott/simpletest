"""
Graph manager component for SimpleTest GUI.
Handles matplotlib graph display and updates.
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Any, Optional, Tuple

class GraphManager:
    """
    Manages matplotlib graph display and updates in the GUI.
    """
    
    def __init__(self, master: tk.Widget, output_manager: Any):
        """
        Initialize GraphManager.
        
        Args:
            master: Parent widget
            output_manager: OutputManager instance for receiving plot data
        """
        self.master = master
        self.output_manager = output_manager
        
        # Create figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        
        # Get the canvas widget and pack it
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Register as graph handler
        self.output_manager.add_graph_handler(self.update_graph)

    def update_graph(self, args: Tuple[Any, ...], kwargs: dict) -> None:
        """
        Update the graph with new plot data.
        
        Args:
            args: Plot arguments
            kwargs: Plot keyword arguments
        """
        try:
            self.ax.clear()
            plot_args = args[0] if args and isinstance(args[0], tuple) else args
            self.ax.plot(*plot_args)
            
            # Set graph properties
            self.ax.set_title(kwargs.get('title', ''))
            self.ax.set_xlabel(kwargs.get('xlabel', ''))
            self.ax.set_ylabel(kwargs.get('ylabel', ''))
            self.ax.grid(kwargs.get('grid', False))
            
            # Update canvas
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating graph: {e}")

    def clear(self) -> None:
        """Clear the current graph."""
        self.ax.clear()
        self.canvas.draw()

    def destroy(self) -> None:
        """Clean up resources when destroying the component."""
        # Remove from output manager
        self.output_manager.remove_graph_handler(self.update_graph)
        
        # Close matplotlib figure
        plt.close(self.fig)
        
        # Destroy canvas widget
        if self.canvas_widget:
            self.canvas_widget.destroy()
