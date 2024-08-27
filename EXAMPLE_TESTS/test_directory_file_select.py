import tkinter as tk
from tkinter import filedialog

def maintest(settings, test_series, plot_function, *args, **kwargs):
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename()

    if file_path:
        print(f"Directory passed:{file_path}!")
        return "pass"
    else:
        dir_path = filedialog.askdirectory()
    
    
    if dir_path:
        print(f"Directory passed:{dir_path}!")
        return "pass"
    else:
        print("No name entered.")
        return "fail"