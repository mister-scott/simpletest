"""
Test file for TestListItem component.
"""

import tkinter as tk
from test_list_item import TestListItem

def test_test_list_item():
    """Run tests for TestListItem component."""
    root = tk.Tk()
    
    # Test data
    test_info = {
        'name': 'Test 1',
        'args': {'param1': 'value1'}
    }
    
    selected_index = None
    def on_select(index):
        nonlocal selected_index
        selected_index = index
    
    # Create test item
    item = TestListItem(root, test_info, 0, on_select)
    item.pack()
    
    # Test 1: Initial state
    assert item.test_name == 'Test 1', "Wrong test name"
    assert item.status == 'pending', "Wrong initial status"
    assert item.optional_args == {'param1': 'value1'}, "Wrong optional args"
    
    # Test 2: Status changes
    item.set_status('pass')
    assert item.status == 'pass', "Status not updated"
    assert item.status_label.cget('text') == '✓', "Status icon not updated"
    
    # Test 3: Selection
    item.select()
    assert item.cget('bg') == 'lightblue', "Selection color not applied"
    
    item.deselect()
    assert item.cget('bg') == 'white', "Deselection color not applied"
    
    # Test 4: Click handling
    item._on_click(None)
    assert selected_index == 0, "Click handler not working"
    
    root.destroy()
    print("All test list item tests passed!")

if __name__ == "__main__":
    test_test_list_item()
