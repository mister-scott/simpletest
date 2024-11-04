"""
Test file for MenuManager component.
"""

import tkinter as tk
from menu_manager import MenuManager

def test_menu_manager():
    """Run tests for MenuManager component."""
    root = tk.Tk()
    
    # Setup command tracking
    commands_called = []
    
    def make_command(name):
        def command():
            commands_called.append(name)
        return command
    
    # Create test commands
    commands = {
        'open_test_series': make_command('open_test_series'),
        'exit': make_command('exit'),
        'settings': make_command('settings')
    }
    
    # Create menu manager
    menu_manager = MenuManager(root, commands)
    
    # Test 1: Menu structure
    assert isinstance(menu_manager.menubar, tk.Menu), "Menu bar not created"
    assert isinstance(menu_manager.file_menu, tk.Menu), "File menu not created"
    assert isinstance(menu_manager.edit_menu, tk.Menu), "Edit menu not created"
    
    # Test 2: Command execution
    menu_manager.file_menu.invoke("Open Test Series")
    assert 'open_test_series' in commands_called, "Open command not called"
    
    menu_manager.edit_menu.invoke("Settings")
    assert 'settings' in commands_called, "Settings command not called"
    
    root.destroy()
    print("All menu manager tests passed!")

if __name__ == "__main__":
    test_menu_manager()
