import time
import numpy as np
import importlib.util
from pathlib import Path
"""
This test demonstrates use of imports and functions for simpletest.
 
## Installed libraries
Installed libraries are imported in the expected manner as shown above
using the 'import numpy as np' style.

## Declared inside test file
Functions declared inside of test files or inside of maintest will be
available to maintest.

## Import of a .py custom library (importlib method)
Due to the use of threads in managing test-execution, importing files 
via folder reference tends to be problematic. 
Use of importlib.util as a workaround rememdies this problem.
Example:

    # Create the 'spec' from the target import file 
    spec = importlib.util.spec_from_file_location(
        "threshold_methods.py", settings['test_directory'] + "/example_import.py")
    # Read the spec in as a module, and assing it to a variable
    module = importlib.util.module_from_spec(spec)
    # Execute the code in the target library, making it ready for use
    spec.loader.exec_module(module)
    # (Optional) Assign a function from the library to a separate variable
    assigned_exclaim = module.assigned_exclaim

## Import of a python project (Directory import with multiple .py files within)
I'm only aware of two methods to import full python projects as libraries.

Option 1: Typically the easier of the two is to build the project into a package and 
install it. Instructions on how to do this are readily available online.

Option 2: The alternative is to copy all the desired functions into a single file,
and import it explicitly using the importlib method. Not typically recommended.
"""

def locally_defined_exclaim():
    print("Wow, I was locally referenced!")
    return True

def maintest(settings, test_series, plot_function, *args, **kwargs):
    def locally_defined_exclaim():
        print("Wow, I was locally referenced!")
        return True

    def maintest_defined_exclaim():
        print('Wow, I was referenced within maintest!')
        return True

    # Create the 'spec' from the target import file 
    spec = importlib.util.spec_from_file_location(
        "threshold_methods.py", Path(settings['test_directory']) / 'utilities' / 'example_import.py')
    # Read the spec in as a module, and assing it to a variable
    module = importlib.util.module_from_spec(spec)
    # Execute the code in the target library, making it ready for use
    spec.loader.exec_module(module)

    # (Optional) Assign a function from the library to a separate variable
    assigned_exclaim = module.assigned_exclaim
    
    test_passes = True

    try:
        assigned_exclaim()
        module.referenced_exclaim()
        locally_defined_exclaim()
        maintest_defined_exclaim()
    except:
        test_passes = False

    result = 'pass' if test_passes else 'softfail'

    return result