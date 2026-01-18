"""
State Machine - Quản lý trạng thái ứng dụng để chống double-run
"""
from enum import Enum
from typing import Optional, Callable
from threading import Lock

try:
    from PyQt5.QtCore import QObject, pyqtSignal
    HAS_QT = True
except ImportError:
    HAS_QT = False
    class QObject:
        pass
    def pyqtSignal(*args, **kwargs):
        return None


class AppState(Enum):
    """Trạng thái của ứng dụng"""
    IDLE = "idle"           # Sẵn sàng nhận lệnh
    RUNNING = "running"     # Đang chạy task
    DONE = "done"          # Task hoàn thành
    ERROR = "error"        # Task lỗi


class TaskType(Enum):
    """Các loại task"""
    IMPORT = "import"
    EXTRACT = "extract"
    PATCH = "patch"
    BUILD = "build"
    TOOL_CHECK = "tool_check"
    OTHER = "other"


if HAS_QT:
    class StateMachine(QObject):
        """
        State machine với Qt signals để notify UI về state changes
        Thread-safe với Lock
        """
        # Signals
        state_changed = pyqtSignal(str)  # Emit state name
        task_started = pyqtSignal(str)   # Emit task type
        task_finished = pyqtSignal(str, bool, str)  # type, success, message
        
        _instance = None
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
        
        def __init__(self):
            if self._initialized:
                return
            super().__init__()
            self._initialized = True
            self._state = AppState.IDLE
            self._current_task: Optional[TaskType] = None
            self._lock = Lock()
        
        @property
        def state(self) -> AppState:
            with self._lock:
                return self._state
        
        @property
        def is_idle(self) -> bool:
            return self.state == AppState.IDLE
        
        @property
        def is_running(self) -> bool:
            return self.state == AppState.RUNNING
        
        @property
        def current_task(self) -> Optional[TaskType]:
            with self._lock:
                return self._current_task
        
        def can_start_task(self) -> bool:
            """Kiểm tra có thể start task mới không"""
            return self.state in [AppState.IDLE, AppState.DONE, AppState.ERROR]
        
        def start_task(self, task_type: TaskType) -> bool:
            """
            Bắt đầu task mới
            
            Returns:
                True nếu có thể start, False nếu đang busy
            """
            with self._lock:
                if self._state == AppState.RUNNING:
                    return False
                
                self._state = AppState.RUNNING
                self._current_task = task_type
            
            self.state_changed.emit(AppState.RUNNING.value)
            self.task_started.emit(task_type.value)
            return True
        
        def finish_task(self, success: bool = True, message: str = ""):
            """Kết thúc task hiện tại"""
            with self._lock:
                task_type = self._current_task
                self._state = AppState.DONE if success else AppState.ERROR
                self._current_task = None
            
            self.state_changed.emit(self._state.value)
            if task_type:
                self.task_finished.emit(task_type.value, success, message)
        
        def reset(self):
            """Reset về IDLE state"""
            with self._lock:
                self._state = AppState.IDLE
                self._current_task = None
            self.state_changed.emit(AppState.IDLE.value)

else:
    # Fallback cho non-Qt
    class StateMachine:
        _instance = None
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
        
        def __init__(self):
            if self._initialized:
                return
            self._initialized = True
            self._state = AppState.IDLE
            self._current_task: Optional[TaskType] = None
            self._lock = Lock()
        
        @property
        def state(self) -> AppState:
            with self._lock:
                return self._state
        
        @property
        def is_idle(self) -> bool:
            return self.state == AppState.IDLE
        
        @property
        def is_running(self) -> bool:
            return self.state == AppState.RUNNING
        
        @property
        def current_task(self) -> Optional[TaskType]:
            with self._lock:
                return self._current_task
        
        def can_start_task(self) -> bool:
            return self.state in [AppState.IDLE, AppState.DONE, AppState.ERROR]
        
        def start_task(self, task_type: TaskType) -> bool:
            with self._lock:
                if self._state == AppState.RUNNING:
                    return False
                self._state = AppState.RUNNING
                self._current_task = task_type
            return True
        
        def finish_task(self, success: bool = True, message: str = ""):
            with self._lock:
                self._state = AppState.DONE if success else AppState.ERROR
                self._current_task = None
        
        def reset(self):
            with self._lock:
                self._state = AppState.IDLE
                self._current_task = None


def get_state_machine() -> StateMachine:
    """Lấy singleton StateMachine instance"""
    return StateMachine()
