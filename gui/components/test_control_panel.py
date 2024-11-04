"""
Test file for ControlPanel component.
"""

import tkinter as tk
from control_panel import ControlPanel

def test_control_panel():
    """Run tests for ControlPanel component."""
    root = tk.Tk()
    
    # Setup command tracking
    commands_called = []
    
    def make_command(name):
        def command():
            commands_called.append(name)
        return command
    
    # Create test commands
    commands = {
        'run_all': make_command('run_all'),
        'run_selected': make_command('run_selected'),
        'run_selected_continue': make_command('run_selected_continue'),
        'stop': make_command('stop')
    }
    
    # Create control panel
    control_panel = ControlPanel(root, commands)
    control_panel.pack()
    
    # Test 1: Initial state
    assert control_panel.run_selected_button.cget('state') == 'disabled', "Selected button should be disabled initially"
    assert control_panel.run_selected_continue_button.cget('state') == 'disabled', "Selected continue button should be disabled initially"
    assert control_panel.running_indicator.cget('fg') == 'gray', "Indicator should be gray initially"
    
    # Test 2: Enable selected buttons
    control_panel.enable_selected_buttons()
    assert control_panel.run_selected_button.cget('state') == 'normal', "Selected button not enabled"
    assert control_panel.run_selected_continue_button.cget('state') == 'normal', "Selected continue button not enabled"
    
    # Test 3: Set running state
    control_panel.set_running(True)
    assert control_panel.running_indicator.cget('fg') == 'red', "Indicator not red when running"
    assert control_panel.run_all_button.cget('state') == 'disabled', "Run all button not disabled when running"
    
    control_panel.set_running(False)
    assert control_panel.running_indicator.cget('fg') == 'gray', "Indicator not gray when stopped"
    assert control_panel.run_all_button.cget('state') == 'normal', "Run all button not enabled when stopped"
    
    # Test 4: Command execution
    control_panel.run_all_button.invoke()
    assert 'run_all' in commands_called, "Run all command not called"
    
    control_panel.enable_selected_buttons()
    control_panel.run_selected_button.invoke()
    assert 'run_selected' in commands_called, "Run selected command not called"
    
    root.destroy()
    print("All control panel tests passed!")

if __name__ == "__main__":
    test_control_panel()
