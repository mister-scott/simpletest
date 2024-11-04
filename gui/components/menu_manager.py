"""
Menu manager component for SimpleTest GUI.
Handles menu creation and command routing.
"""

import tkinter as tk
from tkinter import Menu
from typing import Any, Callable, Dict

class MenuManager:
    """
    Manages application menus and their commands.
    """
    
    def __init__(self, master: tk.Tk, commands: Dict[str, Callable[[], None]]):
        """
        Initialize MenuManager.
        
        Args:
            master: Root Tkinter window
            commands: Dictionary of command names and their callback functions
        """
        self.master = master
        self.commands = commands
        
        # Create main menu bar
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)
        
        # Create File menu
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open Test Series",
            command=self.commands.get('open_test_series')
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Exit",
            command=self.commands.get('exit')
        )
        
        # Create Edit menu
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(
            label="Settings",
            command=self.commands.get('settings')
        )

    def enable_command(self, command_name: str) -> None:
        """
        Enable a menu command.
        
        Args:
            command_name: Name of command to enable
        """
        if command_name in self.commands:
            menu_item = self._find_menu_item(command_name)
            if menu_item:
                menu_item.entryconfig(command_name, state=tk.NORMAL)

    def disable_command(self, command_name: str) -> None:
        """
        Disable a menu command.
        
        Args:
            command_name: Name of command to disable
        """
        if command_name in self.commands:
            menu_item = self._find_menu_item(command_name)
            if menu_item:
                menu_item.entryconfig(command_name, state=tk.DISABLED)

    def _find_menu_item(self, command_name: str) -> Menu:
        """
        Find which menu contains the given command.
        
        Args:
            command_name: Name of command to find
            
        Returns:
            Menu containing the command or None if not found
        """
        menus = {
            'open_test_series': self.file_menu,
            'exit': self.file_menu,
            'settings': self.edit_menu
        }
        return menus.get(command_name)
