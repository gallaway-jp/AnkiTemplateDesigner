"""
Progress indicators for long-running operations.

Provides progress dialogs and status updates for template operations.
"""

from PyQt6.QtWidgets import QProgressDialog, QProgressBar, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from typing import Callable, Any, Optional
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ProgressDialog(QProgressDialog):
    """
    Enhanced progress dialog with cancellation support.
    
    Displays progress for long-running operations with cancel button.
    """
    
    def __init__(self, title: str, message: str, parent=None, minimum: int = 0, maximum: int = 100):
        """
        Initialize progress dialog.
        
        Args:
            title: Dialog window title
            message: Progress message to display
            parent: Parent widget
            minimum: Minimum progress value
            maximum: Maximum progress value
        """
        super().__init__(message, "Cancel", minimum, maximum, parent)
        
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumDuration(500)  # Show after 500ms
        self.setAutoClose(True)
        self.setAutoReset(True)
        
        # Styling
        self.setStyleSheet("""
            QProgressDialog {
                min-width: 400px;
                min-height: 100px;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
    
    def update_message(self, message: str):
        """
        Update the progress message.
        
        Args:
            message: New message to display
        """
        self.setLabelText(message)
    
    def set_progress(self, value: int, message: str = None):
        """
        Set progress value and optionally update message.
        
        Args:
            value: Progress value
            message: Optional new message
        """
        self.setValue(value)
        
        if message:
            self.update_message(message)


class BackgroundTask(QThread):
    """
    Background thread for long-running tasks.
    
    Runs tasks in background and emits progress signals.
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # (value, message)
    finished = pyqtSignal(object)     # (result)
    error = pyqtSignal(Exception)     # (exception)
    
    def __init__(self, task_func: Callable, *args, **kwargs):
        """
        Initialize background task.
        
        Args:
            task_func: Function to run in background
            *args: Positional arguments for task function
            **kwargs: Keyword arguments for task function
        """
        super().__init__()
        
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False
    
    def run(self):
        """Run the task in background thread."""
        try:
            # Run task
            result = self.task_func(*self.args, **self.kwargs)
            
            # Emit result
            if not self._is_cancelled:
                self.finished.emit(result)
        
        except Exception as e:
            logger.error(f"Background task error: {e}")
            self.error.emit(e)
    
    def cancel(self):
        """Cancel the running task."""
        self._is_cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if task was cancelled."""
        return self._is_cancelled
    
    def emit_progress(self, value: int, message: str = ""):
        """
        Emit progress update.
        
        Args:
            value: Progress value (0-100)
            message: Progress message
        """
        if not self._is_cancelled:
            self.progress.emit(value, message)


class ProgressTracker:
    """
    Track progress for multi-step operations.
    
    Automatically calculates progress based on completed steps.
    """
    
    def __init__(self, total_steps: int, callback: Optional[Callable] = None):
        """
        Initialize progress tracker.
        
        Args:
            total_steps: Total number of steps
            callback: Optional callback function(progress, message)
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
    
    def step(self, message: str = ""):
        """
        Mark a step as completed.
        
        Args:
            message: Optional progress message
        """
        self.current_step += 1
        progress = int((self.current_step / self.total_steps) * 100)
        
        if self.callback:
            self.callback(progress, message)
    
    def set_step(self, step: int, message: str = ""):
        """
        Set current step directly.
        
        Args:
            step: Step number (0-based)
            message: Optional progress message
        """
        self.current_step = step
        progress = int((self.current_step / self.total_steps) * 100)
        
        if self.callback:
            self.callback(progress, message)
    
    def reset(self):
        """Reset progress to 0."""
        self.current_step = 0
    
    def get_progress(self) -> int:
        """
        Get current progress percentage.
        
        Returns:
            int: Progress (0-100)
        """
        return int((self.current_step / self.total_steps) * 100)


class TaskRunner:
    """
    Utility for running long tasks with progress indication.
    
    Combines background tasks with progress dialogs.
    """
    
    @staticmethod
    def run_with_progress(
        parent,
        title: str,
        message: str,
        task_func: Callable,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        *args,
        **kwargs
    ):
        """
        Run a task with progress dialog.
        
        Args:
            parent: Parent widget for dialog
            title: Dialog title
            message: Initial progress message
            task_func: Function to run
            on_success: Callback for successful completion
            on_error: Callback for errors
            *args: Task function arguments
            **kwargs: Task function keyword arguments
        """
        # Create progress dialog
        progress = ProgressDialog(title, message, parent, 0, 0)  # Indeterminate
        
        # Create background task
        task = BackgroundTask(task_func, *args, **kwargs)
        
        # Connect signals
        def on_task_finished(result):
            progress.close()
            if on_success:
                on_success(result)
        
        def on_task_error(error):
            progress.close()
            if on_error:
                on_error(error)
        
        def on_task_progress(value, msg):
            progress.setMaximum(100)  # Switch from indeterminate
            progress.set_progress(value, msg)
        
        task.finished.connect(on_task_finished)
        task.error.connect(on_task_error)
        task.progress.connect(on_task_progress)
        
        # Handle cancellation
        progress.canceled.connect(task.cancel)
        
        # Start task
        task.start()
        
        # Show dialog
        progress.exec()
        
        return task


class StatusBarProgress(QWidget):
    """
    Progress indicator for status bar.
    
    Compact progress bar with label for status bar display.
    """
    
    def __init__(self, parent=None):
        """Initialize status bar progress widget."""
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Label
        self.label = QLabel("")
        self.label.setStyleSheet("font-size: 10px;")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 2px;
                background: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        
        self.hide()
    
    def start(self, message: str = "", maximum: int = 100):
        """
        Start showing progress.
        
        Args:
            message: Progress message
            maximum: Maximum progress value (0 for indeterminate)
        """
        self.label.setText(message)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        self.show()
    
    def update_progress(self, value: int, message: str = None):
        """
        Update progress.
        
        Args:
            value: Progress value
            message: Optional new message
        """
        self.progress_bar.setValue(value)
        
        if message:
            self.label.setText(message)
    
    def finish(self):
        """Finish and hide progress."""
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.hide()


def create_indeterminate_progress(parent, title: str, message: str) -> ProgressDialog:
    """
    Create an indeterminate progress dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Progress message
        
    Returns:
        ProgressDialog: Configured progress dialog
    """
    progress = ProgressDialog(title, message, parent, 0, 0)
    return progress


def create_determinate_progress(parent, title: str, message: str, maximum: int) -> ProgressDialog:
    """
    Create a determinate progress dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Progress message
        maximum: Maximum progress value
        
    Returns:
        ProgressDialog: Configured progress dialog
    """
    progress = ProgressDialog(title, message, parent, 0, maximum)
    return progress
