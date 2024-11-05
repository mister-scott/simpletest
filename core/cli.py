"""
Command-line interface module for SimpleTest.
Handles argument parsing and program execution mode selection.
"""

import argparse
import sys
import tkinter as tk
from pathlib import Path
from core.cli_executor import CLIExecutor
from gui.test_executor import TestExecutor

VERSION = "1.2.1"

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='SimpleTest - A GUI/CLI test execution tool')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('--test-series', type=str, help='Path to test series file')
    parser.add_argument('--test', type=str, help='Name of specific test to run')
    return parser.parse_args()

def main() -> int:
    """
    Main entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_args()
    
    if args.cli:
        # CLI mode
        if not args.test_series:
            print("Error: --test-series is required in CLI mode")
            return 1
            
        executor = CLIExecutor()
        return executor.run(args.test_series, args.test)
    else:
        # GUI mode
        root = tk.Tk()
        app = TestExecutor(root, VERSION)
        
        # If test series specified, load it
        if args.test_series:
            app.load_test_series(args.test_series)
            
            # If specific test specified, select it
            if args.test:
                for i, test_item in enumerate(app.test_runner.test_items):
                    if test_item.name == args.test:
                        app.on_test_select(i)
                        break
        
        root.mainloop()
        return 0

if __name__ == "__main__":
    sys.exit(main())
