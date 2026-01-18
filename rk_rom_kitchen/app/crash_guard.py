"""
Crash Guard - Global exception handler
Bắt tất cả unhandled exceptions, hiển thị dialog, ghi log, app không thoát
"""
import sys
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

# Try import Qt for dialog
try:
    from PyQt5.QtWidgets import QMessageBox, QApplication
    from PyQt5.QtCore import qInstallMessageHandler, QtMsgType
    HAS_QT = True
except ImportError:
    HAS_QT = False


def get_crash_log_path() -> Path:
    """Lấy đường dẫn crash log file"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    log_dir = Path(appdata) / 'rk_kitchen'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / 'crash.log'


def write_crash_log(exc_type, exc_value, exc_tb):
    """Ghi exception vào crash log"""
    crash_log = get_crash_log_path()
    
    timestamp = datetime.now().isoformat()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb_str = ''.join(tb_lines)
    
    log_entry = f"""
{'='*60}
CRASH REPORT - {timestamp}
{'='*60}
Exception Type: {exc_type.__name__}
Exception Message: {exc_value}

Traceback:
{tb_str}
{'='*60}

"""
    
    try:
        with open(crash_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write crash log: {e}", file=sys.stderr)


def show_crash_dialog(exc_type, exc_value, exc_tb):
    """Hiển thị dialog thông báo lỗi"""
    if not HAS_QT:
        return
    
    app = QApplication.instance()
    if not app:
        return
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Có lỗi xảy ra")
    msg.setText("Đã xảy ra lỗi không mong muốn.")
    msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
    msg.setDetailedText(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    
    crash_log = get_crash_log_path()
    msg.setInformativeText(
        f"{exc_type.__name__}: {exc_value}\n\n"
        f"Chi tiết đã được ghi vào:\n{crash_log}"
    )
    
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def global_exception_handler(exc_type, exc_value, exc_tb):
    """
    Global exception handler
    - Ghi log
    - Hiển thị dialog
    - KHÔNG thoát app
    """
    # Ignore KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    
    # Print to stderr
    print("="*60, file=sys.stderr)
    print("UNHANDLED EXCEPTION:", file=sys.stderr)
    traceback.print_exception(exc_type, exc_value, exc_tb, file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    # Write to crash log
    write_crash_log(exc_type, exc_value, exc_tb)
    
    # Show dialog (if Qt available and app running)
    try:
        show_crash_dialog(exc_type, exc_value, exc_tb)
    except Exception as e:
        print(f"Failed to show crash dialog: {e}", file=sys.stderr)
    
    # DO NOT call sys.exit() - app continues running


if HAS_QT:
    def qt_message_handler(msg_type, context, message):
        """Qt message handler để catch Qt warnings/errors"""
        if msg_type == QtMsgType.QtFatalMsg:
            # Log fatal errors
            crash_log = get_crash_log_path()
            timestamp = datetime.now().isoformat()
            with open(crash_log, 'a', encoding='utf-8') as f:
                f.write(f"\n[{timestamp}] Qt Fatal: {message}\n")
                f.write(f"  File: {context.file}, Line: {context.line}\n")
        
        # Print all Qt messages
        type_str = {
            QtMsgType.QtDebugMsg: "DEBUG",
            QtMsgType.QtInfoMsg: "INFO",
            QtMsgType.QtWarningMsg: "WARNING",
            QtMsgType.QtCriticalMsg: "CRITICAL",
            QtMsgType.QtFatalMsg: "FATAL",
        }.get(msg_type, "UNKNOWN")
        
        print(f"[Qt {type_str}] {message}", file=sys.stderr)


def install_crash_guard():
    """
    Cài đặt crash guard
    Gọi hàm này ở đầu main()
    """
    # Install Python exception handler
    sys.excepthook = global_exception_handler
    
    # Install Qt message handler
    if HAS_QT:
        qInstallMessageHandler(qt_message_handler)
    
    print("[CrashGuard] Installed successfully", file=sys.stderr)


def uninstall_crash_guard():
    """Gỡ crash guard (restore default handlers)"""
    sys.excepthook = sys.__excepthook__
    
    if HAS_QT:
        qInstallMessageHandler(None)


# Decorator để wrap functions với try-catch
def safe_call(func: Callable) -> Callable:
    """
    Decorator để wrap function với exception handling
    
    Usage:
        @safe_call
        def my_function():
            ...
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            global_exception_handler(exc_type, exc_value, exc_tb)
            return None
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
