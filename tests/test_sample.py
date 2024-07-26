import tkinter as tk
from tkinter import simpledialog

def maintest(settings, test_series):
    root = tk.Tk()
    root.withdraw()
    
    name = simpledialog.askstring("Input", "What is your name?", parent=root)
    
    if name:
        print(f"Hello, {name}!")
        return "pass"
    else:
        print("No name entered.")
        return "fail"