import os
import sys
import yaml
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib
import time
from threading import Thread
import queue

class TestExecutor:
    def __init__(self, master):
        self.master = master
        self.master.title("Test Executor")
        self.master.geometry("1000x800")

        self.create_menu()
        self.create_gui()
        self.load_settings()
        self.load_test_series()
        
        self.graph_queue = queue.Queue()
        self.master.after(100, self.check_graph_queue)
        
        self.current_test_index = 0
        self.is_running_tests = False

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for test list and controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Test list section
        self.test_frame = ttk.Frame(left_frame)
        self.test_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.test_listbox = tk.Listbox(self.test_frame, width=50)
        self.test_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Controls section
        self.control_frame = ttk.Frame(left_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.run_all_button = ttk.Button(self.control_frame, text="Run All Tests", command=self.run_all_tests)
        self.run_all_button.pack(side=tk.LEFT)

        # Right frame for output and graph
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Text output section
        self.output_text = ScrolledText(right_frame, height=20)
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib section
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def load_settings(self):
        with open('test_settings.yaml', 'r') as f:
            self.settings = yaml.safe_load(f)

        if os.path.exists('user_test_settings.yaml'):
            with open('user_test_settings.yaml', 'r') as f:
                user_settings = yaml.safe_load(f)
                self.settings.update(user_settings)

    def load_test_series(self):
        with open('test_series.yaml', 'r') as f:
            self.test_series = yaml.safe_load(f)

        for test in self.test_series['tests']:
            self.test_listbox.insert(tk.END, test['name'])

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")

        row = 0
        entries = {}
        for key, value in self.settings.items():
            ttk.Label(settings_window, text=key).grid(row=row, column=0, sticky="w")
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(settings_window, variable=var).grid(row=row, column=1)
                entries[key] = var
            else:
                var = tk.StringVar(value=str(value))
                ttk.Entry(settings_window, textvariable=var).grid(row=row, column=1)
                entries[key] = var
            row += 1

        ttk.Button(settings_window, text="Save", command=lambda: self.save_settings(entries)).grid(row=row, column=0, columnspan=2)

    def save_settings(self, entries):
        user_settings = {k: v.get() for k, v in entries.items()}
        with open('user_test_settings.yaml', 'w') as f:
            yaml.dump(user_settings, f)
        self.settings.update(user_settings)

    def run_all_tests(self):
        if not self.is_running_tests:
            self.is_running_tests = True
            self.current_test_index = 0
            self.run_next_test()

    def run_next_test(self):
        if self.current_test_index < self.test_listbox.size():
            self.run_test(self.current_test_index)
        else:
            self.is_running_tests = False

    def run_test(self, index):
        test_name = self.test_listbox.get(index)
        test_info = next(test for test in self.test_series['tests'] if test['name'] == test_name)

        self.output_text.insert(tk.END, f"Running test: {test_name}\n")
        self.output_text.see(tk.END)
        if test_info['file'][-3:] == ".py":
            test_module = importlib.import_module(f"tests.{test_info['file'][:-3]}")
        test_module = importlib.import_module(f"tests.{test_info['file']}")
        
        # Create a custom plot function for the test to use
        def plot_function(*args, **kwargs):
            self.graph_queue.put((args, kwargs))
        
        # Run the test in a separate thread
        thread = Thread(target=self.run_test_thread, args=(test_module, plot_function, index))
        thread.start()

    def run_test_thread(self, test_module, plot_function, index):
        result = test_module.maintest(self.settings, self.test_series, plot_function)
        self.master.after(0, self.update_test_result, result, index)

    def update_test_result(self, result, index):
        self.output_text.insert(tk.END, f"Test result: {result}\n\n")
        self.output_text.see(tk.END)

        # Update test status in the listbox
        test_name = self.test_listbox.get(index)
        status_icon = "✓" if result == "pass" else "✗" if result == "fail" else "•"
        self.test_listbox.delete(index)
        self.test_listbox.insert(index, f"{status_icon} {test_name}")

        # Move to the next test
        self.current_test_index += 1
        self.run_next_test()

    # ... [keep all other methods unchanged] ...
    def check_graph_queue(self):
        try:
            args, kwargs = self.graph_queue.get_nowait()
            self.update_graph(*args, **kwargs)
        except queue.Empty:
            pass
        self.master.after(100, self.check_graph_queue)

    def update_graph(self, *args, **kwargs):
        self.ax.clear()
        self.ax.plot(*args, **kwargs)
        self.ax.set_title(kwargs.get('title', ''))
        self.ax.set_xlabel(kwargs.get('xlabel', ''))
        self.ax.set_ylabel(kwargs.get('ylabel', ''))
        self.ax.grid(kwargs.get('grid', False))
        self.canvas.draw()

    def redirect_output(self):
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, string):
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.output_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TestExecutor(root)
    app.redirect_output()
    root.mainloop()