"""
Test file for OutputManager component.
"""

import tempfile
from pathlib import Path
from settings import Settings
from output_manager import OutputManager

def test_output_manager():
    """Run tests for OutputManager component."""
    # Setup
    settings = Settings()
    output_manager = OutputManager(settings)
    
    # Test 1: Output handlers
    outputs = []
    def test_handler(text):
        outputs.append(text)
    
    output_manager.add_output_handler(test_handler)
    test_text = "Test output"
    output_manager.write(test_text)
    assert len(outputs) == 1, "Output handler not called"
    assert outputs[0] == test_text, "Wrong output text"
    
    # Test 2: Graph handlers
    graphs = []
    def graph_handler(args, kwargs):
        graphs.append((args, kwargs))
    
    output_manager.add_graph_handler(graph_handler)
    test_args = ([1, 2, 3], [4, 5, 6])
    test_kwargs = {'title': 'Test Graph'}
    output_manager.plot(test_args, **test_kwargs)
    assert len(graphs) == 1, "Graph handler not called"
    assert graphs[0] == ((test_args,), test_kwargs), "Wrong graph data"
    
    # Test 3: Logging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_manager.set_output_directory(temp_path)
        
        test_log = "Test log message"
        output_manager.write(test_log)
        
        log_file = temp_path / 'log.txt'
        assert log_file.exists(), "Log file not created"
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        assert test_log in log_content, "Log message not written"
    
    # Test 4: Stdout redirector
    redirector = output_manager.create_stdout_redirector()
    outputs.clear()  # Clear previous outputs
    
    redirector.write("Redirected output")
    assert len(outputs) == 1, "Redirector not working"
    assert "Redirected output" in outputs[0], "Wrong redirected output"
    
    print("All output manager tests passed!")

if __name__ == "__main__":
    test_output_manager()
