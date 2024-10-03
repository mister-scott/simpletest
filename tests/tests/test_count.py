import time
import numpy as np

def maintest(settings, test_series, plot_function):
    # Count up from 1 to 5
    for i in range(1, 6):
        print(f"Counting up: {i}")
        time.sleep(1)

    # Count down from 5 to 1
    for i in range(5, 2, -1):
        print(f"Counting down: {i}")
        time.sleep(1)
    print("Whoops...")
    return "softfail"