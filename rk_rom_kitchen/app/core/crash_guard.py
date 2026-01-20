"""
Crash Guard - Global Exception Handler
Logs unhandled exceptions to file and displays user-friendly dialog.
"""
import sys
import threading
import datetime
import traceback
from pathlib import Path

# Adjust paths relative to this file
# This assumes app/core/crash_guard.py
# Log dir: project_root/logs
APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = APP_DIR.parent
LOG_DIR = PROJECT_ROOT / "logs"

def setup_global_exception_hooks(log_to_file: bool = True):
    """Install global exception hooks for sys and threading"""
    
    if log_to_file:
        if not LOG_DIR.exists():
            LOG_DIR.mkdir(parents=True, exist_ok=True)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        log_crash(exc_type, exc_value, exc_traceback, thread_name="MainThread")
        
        # Try to show UI dialog if possible
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance()
            if app:
                msg = f"An unexpected error occurred:\n{exc_value}\n\nA crash log has been saved to logs/."
                QMessageBox.critical(None, "Critical Error", msg)
        except:
            pass
            
    def handle_thread_exception(args):
        log_crash(args.exc_type, args.exc_value, args.exc_traceback, thread_name=threading.current_thread().name)

    sys.excepthook = handle_exception
    threading.excepthook = handle_thread_exception

def log_crash(exc_type, exc_value, tb, thread_name="Unknown"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = LOG_DIR / f"CRASH_{timestamp}.log"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"RK ROM Kitchen Crash Report\n")
            f.write(f"Time: {timestamp}\n")
            f.write(f"Thread: {thread_name}\n")
            f.write(f"{'-'*40}\n")
            f.write("".join(traceback.format_exception(exc_type, exc_value, tb)))
            f.write(f"{'-'*40}\n")
        print(f"[CRASH] Log saved to: {filename}", file=sys.stderr)
    except Exception as e:
        print(f"[CRASH] Failed to write crash log: {e}", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, tb)

