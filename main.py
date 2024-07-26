import os
import sys
import yaml
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib
import time
from datetime import datetime, timedelta
from threading import Thread
import queue
from pathlib import Path

VERSION = "1.0.0"  # Update this as needed
FONT_SIZE = 12 
LOGGING_ENABLED = True
TEST_DIR = Path('tests')

# Create necessary directories if they don't exist
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("output"):
    os.makedirs("output")

def get_font(size_adjustment=0, weight="normal"):
    return ("TkDefaultFont", FONT_SIZE + size_adjustment, weight)

class TestListItem(tk.Frame):
    def __init__(self, master, test_name, index, on_select_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.test_name = test_name
        self.index = index
        self.on_select_callback = on_select_callback
        self.status = "pending"

        self.status_label = tk.Label(self, text="⃝", width=2, font=get_font())
        self.status_label.pack(side=tk.LEFT)
        self.name_label = tk.Label(self, text=test_name, anchor="w",  font=get_font())
        self.name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.bind("<Button-1>", self.on_click)
        self.name_label.bind("<Button-1>", self.on_click)
        
        # Initialize with deselected state
        self.deselect()
        
    def set_status(self, status):
        self.status = status
        status_icons = {"pass": "✓", "softfail": "⚠", "fail": "✗", "done": "•", "pending": "-"}
        self.status_label.config(text=status_icons.get(status, "•"))
        
    def on_click(self, event):
        self.on_select_callback(self.index)
        
    def select(self):
        self.config(bg="lightblue")
        self.name_label.config(bg="lightblue")
        self.status_label.config(bg="lightblue")
        
    def deselect(self):
        self.config(bg="white")
        self.name_label.config(bg="white")
        self.status_label.config(bg="white")

class TestExecutor:
    def __init__(self, master):
        self.master = master
        self.master.title("SimpleTest")
        self.master.geometry("1000x800")
        
        # Apply default font to the root window
        default_font = get_font()
        self.master.option_add("*Font", default_font)
        
        # Create a custom style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TButton", font=get_font())
        self.style.configure("TLabel", font=get_font())


        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_menu()
        self.create_gui()
        self.load_settings()
        self.load_test_series()
        
        self.graph_queue = queue.Queue()
        self.master.after(100, self.check_graph_queue)
        
        self.current_test_index = 0
        self.is_running_tests = False
        self.stop_test_series = False
        self.current_test_thread = None
        self.selected_test_index = None

        # self.create_status_bar()
        self.start_time = None


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

        self.test_canvas = tk.Canvas(self.test_frame)
        self.test_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.test_scrollbar = ttk.Scrollbar(self.test_frame, orient=tk.VERTICAL, command=self.test_canvas.yview)
        self.test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.test_canvas.configure(yscrollcommand=self.test_scrollbar.set)
        self.test_canvas.bind('<Configure>', lambda e: self.test_canvas.configure(scrollregion=self.test_canvas.bbox("all")))

        self.test_inner_frame = ttk.Frame(self.test_canvas)
        self.test_canvas.create_window((0, 0), window=self.test_inner_frame, anchor="nw")

        # Controls section
        self.control_frame = ttk.Frame(left_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.run_all_button = ttk.Button(self.control_frame, text="Run All", command=self.run_all_tests, style="TButton")
        self.run_all_button.pack(side=tk.LEFT)

        self.run_selected_button = ttk.Button(self.control_frame, text="Run Selected", command=self.run_selected_test, style="TButton")
        self.run_selected_button.pack(side=tk.LEFT)

        self.run_selected_continue_button = ttk.Button(self.control_frame, text="Run Selected, Continue", command=self.run_selected_test_continue, style="TButton")
        self.run_selected_continue_button.pack(side=tk.LEFT)

        self.stop_test_series_button = ttk.Button(self.control_frame, text="Stop", command=self.set_stop_test_series,style="TButton")
        self.stop_test_series_button.pack(side=tk.LEFT)

        # Test running indicator
        self.test_running_indicator = tk.Label(self.control_frame, text="●", fg="gray")
        self.test_running_indicator.pack(side=tk.LEFT)

        # Right frame for output and graph
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Text output section
        # Example of using custom font sizes
        self.output_text = ScrolledText(right_frame, height=20, font=get_font())
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib section
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.create_status_bar()

    def create_status_bar(self):
        self.status_bar = tk.Frame(self.master)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.version_label = tk.Label(self.status_bar, text=f"v{VERSION}", font=get_font(-1))  # Slightly smaller font
        self.version_label.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.status_bar, text="Ready", font=get_font())
        self.status_label.pack(side=tk.RIGHT, padx=5)

        self.timer_label = tk.Label(self.status_bar, text="", font=get_font())
        self.timer_label.pack(side=tk.RIGHT, padx=5)

    def update_status(self, status):
        self.status_label.config(text=status)

    def update_timer(self):
        if self.start_time and self.is_running_tests:
            elapsed_time = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
            self.timer_label.config(text=f"Runtime: {time_str}")
            self.master.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="")

    def load_settings(self):
        with open(TEST_DIR/'test_settings.yaml', 'r') as f:
            self.settings = yaml.safe_load(f)

        if os.path.exists(TEST_DIR/'user_test_settings.yaml'):
            with open(TEST_DIR/'user_test_settings.yaml', 'r') as f:
                user_settings = yaml.safe_load(f)
                self.settings.update(user_settings)

    def set_stop_test_series(self):
        if self.is_running_tests:
            self.stop_test_series = True
            self.output_text.insert(tk.END, f"\n! Discontinuing test progression !\n - Test series will stop at conclusion of present test.\n\n")
            self.output_text.see(tk.END)


    def load_test_series(self):
        with open(TEST_DIR/'test_series.yaml', 'r') as f:
            self.test_series = yaml.safe_load(f)

        self.test_items = []
        for index, test in enumerate(self.test_series['tests']):
            item = TestListItem(self.test_inner_frame, test['name'], index, self.on_test_select)
            item.pack(fill=tk.X, padx=5, pady=2)
            self.test_items.append(item)

        self.test_canvas.configure(scrollregion=self.test_canvas.bbox("all"))

    def on_test_select(self, index):
        if self.selected_test_index is not None:
            self.test_items[self.selected_test_index].deselect()
        
        self.selected_test_index = index
        self.test_items[index].select()
        
        self.run_selected_button.config(state=tk.NORMAL)
        self.run_selected_continue_button.config(state=tk.NORMAL)

    def run_selected_test(self):
        if self.selected_test_index is not None and not self.is_running_tests:
            self.current_test_index = self.selected_test_index
            self.is_running_tests = True
            self.start_time = datetime.now()
            self.update_timer()
            self.test_running_indicator.config(fg="red")
            self.output_text.insert(tk.END, f"\n--- Running selected test: {self.test_items[self.current_test_index].test_name} ---\n\n")
            self.output_text.see(tk.END)
            try:
                self.stop_test_series = True
                self.run_test(self.current_test_index)
            except Exception as e:
                self.output_text.insert(tk.END, f"Error running test: {str(e)}\n")
                self.output_text.see(tk.END)
                self.is_running_tests = False
                self.stop_test_series = False
                self.test_running_indicator.config(fg="gray")
                self.update_status("Test error")
                self.start_time = None

    def run_selected_test_continue(self):
        if self.selected_test_index is not None and not self.is_running_tests:
            self.stop_test_series = False
            self.output_text.insert(tk.END, "\n--- Starting new test run from selected test ---\n\n")
            self.output_text.see(tk.END)
            self.run_all_tests(starting_index=self.selected_test_index)

    def run_all_tests(self, starting_index=0):
        if not self.is_running_tests:
            self.stop_test_series = False
            self.is_running_tests = True
            self.current_test_index = starting_index
            self.start_time = datetime.now()
            self.update_timer()
            if starting_index == 0:
                self.output_text.insert(tk.END, "\n--- Starting new test run ---\n\n")
            self.output_text.see(tk.END)
            self.test_running_indicator.config(fg="red")
            self.run_next_test()

    def curselection(self):
        return (self.selected_test_index,) if self.selected_test_index is not None else ()

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")

        row = 0
        entries = {}
        for key, value in self.settings.items():
            ttk.Label(settings_window, text=key, font=get_font()).grid(row=row, column=0, sticky="w")
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(settings_window, variable=var).grid(row=row, column=1)
                entries[key] = var
            else:
                var = tk.StringVar(value=str(value))
                ttk.Entry(settings_window, textvariable=var, font=get_font()).grid(row=row, column=1)
                entries[key] = var
            row += 1

        button_frame = ttk.Frame(settings_window)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Save", command=lambda: self.save_settings(entries, settings_window), style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy, style="TButton").pack(side=tk.LEFT, padx=5)

        # Make the window modal
        settings_window.transient(self.master)
        settings_window.grab_set()
        self.master.wait_window(settings_window)

    def save_settings(self, entries, settings_window):
        user_settings = {k: v.get() for k, v in entries.items()}
        with open('tests/user_test_settings.yaml', 'w') as f:
            yaml.dump(user_settings, f)
        self.settings.update(user_settings)
        settings_window.destroy()

    def run_next_test(self):
        if self.current_test_index < len(self.test_items):
            try:
                self.run_test(self.current_test_index)
            except Exception as e:
                self.output_text.insert(tk.END, f"Error running test: {str(e)}\n")
                self.output_text.see(tk.END)
                self.is_running_tests = False
                self.test_running_indicator.config(fg="gray")
        else:
            self.output_text.insert(tk.END, "All tests completed.\n")
            self.output_text.see(tk.END)
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")

    def run_test(self, index):
        test_item = self.test_items[index]
        test_name = test_item.test_name
        self.update_status(f"Test [{test_name}] running")
        
        if self.start_time is None:
            self.start_time = datetime.now()
            self.update_timer()

        try:
            test_info = next(test for test in self.test_series['tests'] if test['name'] == test_name)
        except StopIteration:
            raise Exception(f"Test '{test_name}' not found in test series.")

        self.output_text.insert(tk.END, f"Running test: {test_name}\n")
        self.output_text.see(tk.END)

        try:
            test_module = importlib.import_module(f"tests.{test_info['file']}")
        except ImportError:
            raise Exception(f"Failed to import test module for '{test_name}'.")
        
        def plot_function(*args, **kwargs):
            self.graph_queue.put((args, kwargs))
        
        self.current_test_thread = Thread(target=self.run_test_thread, args=(test_module, plot_function, index))
        self.current_test_thread.daemon = True
        self.current_test_thread.start()

    def run_test_thread(self, test_module, plot_function, index):
        result = test_module.maintest(self.settings, self.test_series, plot_function)
        self.master.after(0, self.update_test_result, result, index)

    def update_test_result(self, result, index):
        test_item = self.test_items[index]
        test_item.set_status(result)

        self.output_text.insert(tk.END, f"Test result: {result}\n\n")
        self.output_text.see(tk.END)

        if result == "fail":
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")
            self.update_status("Test failed")
            self.start_time = None
            messagebox.showerror("Test Failed", f"The test '{test_item.test_name}' has failed. Test series stopped.")
        elif self.stop_test_series:
            self.stop_test_series=False
            self.is_running_tests = False
            self.test_running_indicator.config(fg="gray")
            self.output_text.insert(tk.END, f"Test series stopped.\n\n")
            self.output_text.see(tk.END)
            self.update_status("Test series stopped")
            self.start_time = None
        else:
            self.current_test_index += 1
            if self.current_test_index < len(self.test_items):
                self.run_next_test()
            else:
                self.is_running_tests = False
                self.test_running_indicator.config(fg="gray")
                self.update_status("All tests completed")
                self.start_time = None

    def check_graph_queue(self):
        try:
            args, kwargs = self.graph_queue.get_nowait()
            self.update_graph(*args, **kwargs)
        except queue.Empty:
            pass
        self.master.after(100, self.check_graph_queue)

    def update_graph(self, *args, **kwargs):
        self.ax.clear()
        plot_args = args[0] if args and isinstance(args[0], tuple) else args
        self.ax.plot(*plot_args)
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
                if LOGGING_ENABLED:
                    logstring = string.replace("\n", "").replace("\r", "").replace("\t", "")
                    if len(logstring.strip()) > 1:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        logstring = f"{timestamp}: {logstring}\n"
                        with open('output/log.txt', 'a') as f:
                            f.write(logstring)

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.output_text)

    def on_closing(self):
        if self.is_running_tests:
            if tk.messagebox.askokcancel("Quit", "Tests are still running. Do you want to quit?"):
                self.is_running_tests = False
                self.start_time = None
                self.master.quit()
        else:
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TestExecutor(root)
    app.redirect_output()
    root.mainloop()
    sys.exit()