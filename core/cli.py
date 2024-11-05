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
    parser = argparse.ArgumentParser(description='SimpleTest - A test execution tool')
    
    # Test series and settings are required for headless mode
    parser.add_argument('--test-series', type=str, help='Path to test series file')
    parser.add_argument('--test-settings', type=str, help='Path to test settings file')
    
    # Optional arguments
    parser.add_argument('--working-dir', type=str, help='Working directory path (defaults to ./WORKING)')
    parser.add_argument('--output-dir', type=str, help='Output directory path (defaults to ./OUTPUT)')
    parser.add_argument('--test', type=str, help='Name of specific test to run')
    
    return parser.parse_args()

def main() -> None:
    """
    Main entry point.
    
    Uses sys.exit() to return OS-level exit codes:
    - 0: Success (all tests passed)
    - 1: Test failure (one or more tests failed)
    - 2: Error (exceptions, configuration issues)
    """
    args = parse_args()
    
    # If both test series and settings are provided, run in headless mode
    if args.test_series and args.test_settings:
        executor = CLIExecutor()
        executor.run_headless(
            test_series_file=args.test_series,
            test_settings_file=args.test_settings,
            working_dir=args.working_dir,
            output_dir=args.output_dir,
            selected_test=args.test
        )
        # Note: run_headless will call sys.exit() with appropriate code
    
    # Otherwise run in GUI mode
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
    sys.exit(0)

if __name__ == "__main__":
    main()
