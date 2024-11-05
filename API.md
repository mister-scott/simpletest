# SimpleTest API Documentation

## Core Components

### Settings (core/settings.py)
```python
class Settings:
    def __init__(self)
    def load_settings(self, test_directory: Path) -> None
    def save_user_settings(self, test_directory: Path, settings: Dict[str, Any]) -> None
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def add_observer(self, observer: Callable[[str, Any], None]) -> None
    def remove_observer(self, observer: Callable[[str, Any], None]) -> None
    def get_all(self) -> Dict[str, Any]
```

### FileManager (core/file_manager.py)
```python
class FileManager:
    def __init__(self, settings)
    def set_test_directory(self, test_series_path: str) -> bool
    def load_test_series(self) -> bool
    def get_test_series(self) -> Dict[str, Any]
    def get_test_directory(self) -> Optional[Path]
    def get_test_series_file(self) -> Optional[str]
```

### OutputManager (core/output_manager.py)
```python
class OutputManager:
    def __init__(self, settings)
    def set_output_directory(self, directory: Path) -> None
    def add_output_handler(self, handler: Callable[[str], None]) -> None
    def remove_output_handler(self, handler: Callable[[str], None]) -> None
    def add_graph_handler(self, handler: Callable[[tuple, dict], None]) -> None
    def remove_graph_handler(self, handler: Callable[[tuple, dict], None]) -> None
    def write(self, text: str) -> None
    def plot(self, *args: Any, **kwargs: Any) -> None
```

### TestRunner (core/test_runner.py)
```python
class TestRunner:
    def __init__(self, settings, file_manager, output_manager)
    def load_tests(self) -> None
    def run_test(self, index: int) -> None
    def run_all_tests(self, starting_index: int = 0) -> None
    def stop_test_series(self) -> None
    def add_completion_observer(self, observer: Callable[[], None]) -> None
    def add_status_observer(self, observer: Callable[[str], None]) -> None
    def add_test_observer(self, observer: Callable[[int, str], None]) -> None
```

### CLIExecutor (core/cli_executor.py)
```python
class CLIExecutor:
    def __init__(self)
    def run(self, test_series_file: str, selected_test: str = None) -> int
```

## GUI Components

### TestExecutor (gui/test_executor.py)
```python
class TestExecutor:
    def __init__(self, master: tk.Tk, version: str)
    def load_test_series(self, test_series_file: str) -> None
    def run_all_tests(self) -> None
    def run_selected_test(self) -> None
    def run_selected_test_continue(self) -> None
    def stop_test_series(self) -> None
```

### TestList (gui/components/test_list.py)
```python
class TestList(tk.Frame):
    def __init__(self, master: tk.Widget, on_select: Callable[[int], None])
    def add_test(self, test_info: Dict[str, Any], index: int) -> TestListItem
    def clear(self) -> None
    def deselect_all(self) -> None
```

### GraphManager (gui/components/graph_manager.py)
```python
class GraphManager:
    def __init__(self, master: tk.Widget, output_manager: Any)
    def update_graph(self, args: Tuple[Any, ...], kwargs: dict) -> None
    def clear(self) -> None
```

### StatusBar (gui/components/status_bar.py)
```python
class StatusBar(tk.Frame):
    def __init__(self, master: tk.Widget, version: str)
    def set_test_series(self, test_series: Optional[str]) -> None
    def set_status(self, status: str) -> None
    def start_timer(self) -> None
    def stop_timer(self) -> None
```

### MenuManager (gui/components/menu_manager.py)
```python
class MenuManager:
    def __init__(self, master: tk.Tk, commands: Dict[str, Callable[[], None]])
    def enable_command(self, command_name: str) -> None
    def disable_command(self, command_name: str) -> None
```

### ControlPanel (gui/components/control_panel.py)
```python
class ControlPanel(tk.Frame):
    def __init__(self, master: tk.Widget, commands: Dict[str, Callable[[], None]])
    def enable_selected_buttons(self) -> None
    def disable_selected_buttons(self) -> None
    def set_running(self, is_running: bool) -> None
```

## Test Module Interface

Each test module must implement this interface:
```python
def maintest(settings: Dict[str, Any], test_items: List[Any], 
            plot_function: Callable, **kwargs: Any) -> str:
    """
    Execute test logic.
    
    Args:
        settings: Dictionary of test settings
        test_items: List of test items in series
        plot_function: Function for plotting graphs
        **kwargs: Additional arguments from test_series.yaml
        
    Returns:
        str: Test result ("pass", "fail", "softfail", or "done")
    """
```

## Command Line Interface

```bash
python main.py [-h] [--cli] [--test-series TEST_SERIES] [--test TEST]

options:
  -h, --help            Show this help message and exit
  --cli                 Run in CLI mode
  --test-series TEST_SERIES
                        Path to test series file
  --test TEST           Name of specific test to run
