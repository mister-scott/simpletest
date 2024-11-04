"""
Output management component for SimpleTest.
Handles logging, output redirection, and graph data management.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Any, Callable, Optional
from queue import Queue

class OutputManager:
    """
    Manages application output, logging, and graph data.
    """
    
    def __init__(self, settings):
        """
        Initialize OutputManager.
        
        Args:
            settings: Settings instance for configuration
        """
        self.settings = settings
        self._output_handlers: List[Callable[[str], None]] = []
        self._graph_handlers: List[Callable[[tuple, dict], None]] = []
        self._graph_queue: Queue = Queue()
        self.logging_enabled = True
        self._output_directory: Optional[Path] = None

    def set_output_directory(self, directory: Path) -> None:
        """
        Set the output directory for logs.
        
        Args:
            directory: Path to output directory
        """
        self._output_directory = directory
        if directory:
            directory.mkdir(parents=True, exist_ok=True)

    def add_output_handler(self, handler: Callable[[str], None]) -> None:
        """
        Add an output handler for receiving output text.
        
        Args:
            handler: Callback function taking a string parameter
        """
        if handler not in self._output_handlers:
            self._output_handlers.append(handler)

    def remove_output_handler(self, handler: Callable[[str], None]) -> None:
        """
        Remove an output handler.
        
        Args:
            handler: Handler to remove
        """
        if handler in self._output_handlers:
            self._output_handlers.remove(handler)

    def add_graph_handler(self, handler: Callable[[tuple, dict], None]) -> None:
        """
        Add a graph handler for receiving plot data.
        
        Args:
            handler: Callback function taking args and kwargs parameters
        """
        if handler not in self._graph_handlers:
            self._graph_handlers.append(handler)

    def remove_graph_handler(self, handler: Callable[[tuple, dict], None]) -> None:
        """
        Remove a graph handler.
        
        Args:
            handler: Handler to remove
        """
        if handler in self._graph_handlers:
            self._graph_handlers.remove(handler)

    def write(self, text: str) -> None:
        """
        Write text to all output handlers and log file.
        
        Args:
            text: Text to output
        """
        # Notify output handlers
        for handler in self._output_handlers:
            handler(text)
        
        # Log to file if enabled
        if self.logging_enabled and self._output_directory:
            self._log_to_file(text)

    def _log_to_file(self, text: str) -> None:
        """
        Write text to log file.
        
        Args:
            text: Text to log
        """
        if not self._output_directory:
            return
            
        log_text = text.replace("\n", "").replace("\r", "").replace("\t", "")
        if len(log_text.strip()) > 1:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_text = f"{timestamp}: {log_text}\n"
            log_file = self._output_directory / 'log.txt'
            try:
                writemode = 'a' if Path(log_file).exists() else 'w'
                print(writemode)
                with open(log_file, writemode, encoding='utf-8') as f:
                    f.write(log_text)
            except Exception as e:
                print(f"Error writing to log file: {e}")

    def plot(self, *args: Any, **kwargs: Any) -> None:
        """
        Send plot data to graph handlers.
        
        Args:
            *args: Plot arguments
            **kwargs: Plot keyword arguments
        """
        self._graph_queue.put((args, kwargs))
        self._process_graph_queue()

    def _process_graph_queue(self) -> None:
        """Process queued graph data."""
        try:
            while not self._graph_queue.empty():
                args, kwargs = self._graph_queue.get_nowait()
                for handler in self._graph_handlers:
                    handler(args, kwargs)
        except Exception as e:
            print(f"Error processing graph data: {e}")

    def create_stdout_redirector(self) -> 'StdoutRedirector':
        """
        Create a stdout redirector for capturing print output.
        
        Returns:
            StdoutRedirector: Redirector instance
        """
        return StdoutRedirector(self)

class StdoutRedirector:
    """
    Redirects stdout to the OutputManager.
    """
    
    def __init__(self, output_manager: OutputManager):
        """
        Initialize StdoutRedirector.
        
        Args:
            output_manager: OutputManager instance
        """
        self.output_manager = output_manager

    def write(self, string: str) -> None:
        """
        Write string to output manager.
        
        Args:
            string: String to write
        """
        self.output_manager.write(string)

    def flush(self) -> None:
        """Flush output (no-op for compatibility)."""
        pass
