"""
Test file for StatusBar component.
"""

import tkinter as tk
import time
from status_bar import StatusBar

def test_status_bar():
    """Run tests for StatusBar component."""
    root = tk.Tk()
    
    # Setup
    status_bar = StatusBar(root, "1.2.3")
    status_bar.pack(fill=tk.X)
    
    # Test 1: Initial state
    assert status_bar.version_label.cget('text') == "v1.2.3", "Wrong version"
    assert status_bar.status_label.cget('text') == "Ready", "Wrong initial status"
    assert status_bar.timer_label.cget('text') == "", "Timer should be empty"
    
    # Test 2: Test series display
    status_bar.set_test_series("test_series.yaml")
    assert "test_series.yaml" in status_bar.test_series_label.cget('text'), "Test series not set"
    
    status_bar.set_test_series(None)
    assert status_bar.test_series_label.cget('text') == "", "Test series not cleared"
    
    # Test 3: Status updates
    status_bar.set_status("Running tests...")
    assert status_bar.status_label.cget('text') == "Running tests...", "Status not updated"
    
    # Test 4: Timer
    status_bar.start_timer()
    root.update()  # Process pending events
    time.sleep(1)  # Wait for timer update
    root.update()  # Process pending events
    assert "Runtime:" in status_bar.timer_label.cget('text'), "Timer not started"
    
    status_bar.stop_timer()
    assert status_bar.timer_label.cget('text') == "", "Timer not stopped"
    
    root.destroy()
    print("All status bar tests passed!")

if __name__ == "__main__":
    test_status_bar()
