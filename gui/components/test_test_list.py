"""
Test file for TestList component.
"""

import tkinter as tk
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from gui.components.test_list import TestList

def test_test_list():
    """Run tests for TestList component."""
    root = tk.Tk()
    
    # Setup
    selected_index = None
    def on_select(index):
        nonlocal selected_index
        selected_index = index
    
    test_list = TestList(root, on_select)
    test_list.pack(fill=tk.BOTH, expand=True)
    
    # Test 1: Add test items
    test_items = [
        {'name': 'Test 1', 'args': {'param1': 'value1'}},
        {'name': 'Test 2', 'args': {'param2': 'value2'}},
        {'name': 'Test 3', 'args': {'param3': 'value3'}}
    ]
    
    for i, test_info in enumerate(test_items):
        test_list.add_test(test_info, i)
    
    assert len(test_list.test_items) == 3, "Wrong number of test items"
    
    # Test 2: Selection
    test_list.test_items[0]._on_click(None)
    assert selected_index == 0, "Selection not working"
    
    # Test 3: Clear items
    test_list.clear()
    assert len(test_list.test_items) == 0, "Items not cleared"
    
    # Test 4: Get item
    test_item = test_list.add_test(test_items[0], 0)
    assert test_list.get_item(0) == test_item, "Get item not working"
    
    # Test 5: Deselect all
    test_item._on_click(None)  # Select the item
    test_list.deselect_all()
    assert not test_item.selected, "Deselect all not working"
    
    root.destroy()
    print("All test list tests passed!")

if __name__ == "__main__":
    test_test_list()
