import os
import sys
import yaml
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib
import time
from threading import Thread

class TestExecutor:
    def __init__(self, master):
        self.master = master
        self.master.title("Test Executor")
        self.master.geometry("800x600")

        self.create_menu()
        self.create_gui()
        self.load_settings()
        self.load_test_series()

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.open_settings)
        menubar.add_cascade(label="File", menu=file_menu)

    def create_gui(self):
        # Test list section
        self.test_frame = ttk.Frame(self.master)
        self.test_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.test_listbox = tk.Listbox(self.test_frame, width=50)
        self.test_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Text output section
        self.output_frame = ttk.Frame(self.master)
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.output_text = ScrolledText(self.output_frame)
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib section
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.output_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Controls section
        self.control_frame = ttk.Frame(self.master)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.run_all_button = ttk.Button(self.control_frame, text="Run All Tests", command=self.run_all_tests)
        self.run_all_button.pack(side=tk.LEFT)

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
        for i in range(self.test_listbox.size()):
            self.run_test(i)

    def run_test(self, index):
        test_name = self.test_listbox.get(index)
        test_info = next(test for test in self.test_series['tests'] if test['name'] == test_name)

        self.output_text.insert(tk.END, f"Running test: {test_name}\n")
        self.output_text.see(tk.END)

        test_module = importlib.import_module(f"tests.{test_info['file']}")
        result = test_module.maintest(self.settings, self.test_series)

        self.output_text.insert(tk.END, f"Test result: {result}\n\n")
        self.output_text.see(tk.END)

        # Update test status in the listbox
        status_icon = "✓" if result == "pass" else "✗" if result == "fail" else "•"
        self.test_listbox.delete(index)
        self.test_listbox.insert(index, f"{status_icon} {test_name}")

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