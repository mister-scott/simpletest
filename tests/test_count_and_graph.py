import time
import numpy as np
import matplotlib.pyplot as plt

def maintest(settings, test_series):
    # Count up from 1 to 5
    for i in range(1, 6):
        print(f"Counting up: {i}")
        time.sleep(1)

    # Create and display sine graph
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y)
    plt.title("Sine Function")
    plt.xlabel("x")
    plt.ylabel("sin(x)")
    plt.grid(True)
    plt.show()  # This will display the graph in the matplotlib section of the GUI

    # Count down from 5 to 1
    for i in range(5, 0, -1):
        print(f"Counting down: {i}")
        time.sleep(1)

    return "done"