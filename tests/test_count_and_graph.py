import time
import numpy as np

def maintest(settings, test_series, plot_function):
    # Count up from 1 to 5
    for i in range(1, 6):
        print(f"Counting up: {i}")
        time.sleep(1)

    # Create and display sine graph
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    
    plot_function(x, y)#, title="Sine Function", xlabel="x", ylabel="sin(x)", grid=True)

    # Count down from 5 to 1
    for i in range(5, 0, -1):
        print(f"Counting down: {i}")
        time.sleep(1)
    plot_function(y, x)#, title="Sine Function", xlabel="x", ylabel="sin(x)", grid=True)

    return "done"