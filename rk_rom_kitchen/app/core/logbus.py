"""
Log Bus - Thread-safe logging với Qt signals
Cho phép stream log từ background threads về UI
"""
import logging
import sys
from datetime import datetime
from typing import Optional, Callable
from enum import Enum
from pathlib import Path

try:
    from PyQt5.QtCore import QObject, pyqtSignal
    HAS_QT = True
except ImportError:
    HAS_QT = False
    # Fallback cho non-Qt environments (testing)
    class QObject:
        pass
    def pyqtSignal(*args, **kwargs):
        return None


def safe_print(text: str):
    """Print với handling encoding errors cho Windows console"""
    try:
        print(text, file=sys.stderr)
    except UnicodeEncodeError:
        # Fallback: encode với errors='replace'
        encoded = text.encode(sys.stderr.encoding or 'utf-8', errors='replace')
        print(encoded.decode(sys.stderr.encoding or 'utf-8', errors='replace'), file=sys.stderr)


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"  # Custom level cho operations thành công


class LogEntry:
    """Represents một log entry"""
    def __init__(self, level: LogLevel, message: str, source: str = None):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.source = source or "app"
    
    def formatted(self) -> str:
        ts = self.timestamp.strftime("%H:%M:%S")
        return f"[{ts}] [{self.level.value}] {self.message}"
    
    def __str__(self):
        return self.formatted()


if HAS_QT:
    class LogBus(QObject):
        """
        Central log bus sử dụng Qt signals để thread-safe communication
        """
        # Signal emit log entries
        log_signal = pyqtSignal(object)  # LogEntry
        clear_signal = pyqtSignal()
        
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
            self._handlers: list[Callable[[LogEntry], None]] = []
            self._file_handler: Optional[logging.FileHandler] = None
            self._log_file: Optional[Path] = None
        
        def set_log_file(self, path: Path):
            """Set file để ghi log"""
            self._log_file = path
            path.parent.mkdir(parents=True, exist_ok=True)
        
        def _emit(self, entry: LogEntry):
            """Internal: emit log entry"""
            # Emit qua Qt signal (thread-safe)
            self.log_signal.emit(entry)
            
            # Ghi ra file nếu có
            if self._log_file:
                try:
                    with open(self._log_file, 'a', encoding='utf-8') as f:
                        f.write(entry.formatted() + '\n')
                except Exception:
                    pass  # Silent fail nếu không ghi được
            
            # Print ra console cho dev
            safe_print(entry.formatted())
        
        def debug(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.DEBUG, message, source))
        
        def info(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.INFO, message, source))
        
        def warning(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.WARNING, message, source))
        
        def error(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.ERROR, message, source))
        
        def success(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.SUCCESS, message, source))
        
        def log(self, level: LogLevel, message: str, source: str = None):
            self._emit(LogEntry(level, message, source))
        
        def clear(self):
            """Signal để clear log panel"""
            self.clear_signal.emit()

else:
    # Fallback cho non-Qt (testing)
    class LogBus:
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
            self._log_file: Optional[Path] = None
        
        def set_log_file(self, path: Path):
            self._log_file = path
            path.parent.mkdir(parents=True, exist_ok=True)
        
        def _emit(self, entry: LogEntry):
            if self._log_file:
                try:
                    with open(self._log_file, 'a', encoding='utf-8') as f:
                        f.write(entry.formatted() + '\n')
                except Exception:
                    pass
            safe_print(entry.formatted())
        
        def debug(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.DEBUG, message, source))
        
        def info(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.INFO, message, source))
        
        def warning(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.WARNING, message, source))
        
        def error(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.ERROR, message, source))
        
        def success(self, message: str, source: str = None):
            self._emit(LogEntry(LogLevel.SUCCESS, message, source))
        
        def log(self, level: LogLevel, message: str, source: str = None):
            self._emit(LogEntry(level, message, source))
        
        def clear(self):
            pass


# Global instance
def get_log_bus() -> LogBus:
    """Lấy singleton LogBus instance"""
    return LogBus()
