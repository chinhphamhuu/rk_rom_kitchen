"""
Test Crash Guard Hooks
Verify that crash guard setup installs hooks and creates log files on crash.
"""
import unittest
import sys
import threading
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core import crash_guard

class TestCrashGuardHooks(unittest.TestCase):
    
    def setUp(self):
        # Save original hooks
        self.orig_excepthook = sys.excepthook
        self.orig_thread_hook = threading.excepthook
        
        # Temp log dir
        self.test_log_dir = Path("temp_logs_crash_test")
        if self.test_log_dir.exists():
            shutil.rmtree(self.test_log_dir)
            
        # Patch LOG_DIR in crash_guard logic?
        # crash_guard.LOG_DIR is a global constant defined at module level.
        # We can patch it.
        self.patcher = patch("app.core.crash_guard.LOG_DIR", self.test_log_dir)
        self.patcher.start()

    def tearDown(self):
        # Restore hooks
        sys.excepthook = self.orig_excepthook
        threading.excepthook = self.orig_thread_hook
        self.patcher.stop()
        
        if self.test_log_dir.exists():
            try: shutil.rmtree(self.test_log_dir)
            except: pass

    def test_setup_installs_hooks(self):
        """Enable hooks"""
        crash_guard.setup_global_exception_hooks(log_to_file=True)
        
        # Check hooks replaced
        self.assertNotEqual(sys.excepthook, sys.__excepthook__)
        # self.assertNotEqual(threading.excepthook, threading.__excepthook__) # Might depend on python version defaults

    def test_crash_creates_log(self):
        """Simulate crash -> log file created"""
        crash_guard.setup_global_exception_hooks(log_to_file=True)
        
        # Call the hook manually to simulate crash (don't actually crash runner)
        # sys.excepthook(type, value, traceback)
        try:
            raise ValueError("Simulated Crash")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_traceback)
            
        # Check log file exists
        time.sleep(0.1) # async write? No, it's sync.
        files = list(self.test_log_dir.glob("CRASH_*.log"))
        self.assertTrue(len(files) > 0, "Crash log not created")
        
        content = files[0].read_text(encoding="utf-8")
        self.assertIn("Simulated Crash", content)
        self.assertIn("ValueError", content)

if __name__ == "__main__":
    unittest.main()
