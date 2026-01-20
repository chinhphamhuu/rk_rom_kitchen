"""
Test Smoke Import Policy
Verify that smoke_test skips UI imports gracefully when missing, unless strict mode is on.
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Import the function to test
from app.tests.smoke_test import test_imports

class TestSmokeImportPolicy(unittest.TestCase):
    
    def setUp(self):
        # Clean up any existing UI modules from cache to force re-import logic
        self.ui_modules = [m for m in sys.modules if m.startswith('app.ui')]
        for m in self.ui_modules:
            del sys.modules[m]

    def tearDown(self):
        # Restore (optional, but good practice if feasible. 
        # Here we just deleted them, reloading happens naturally or valid tests won't care)
        pass

    def test_missing_ui_skipped_by_default(self):
        """Default (no env): Missing UI -> Pass (Skip)"""
        # Clean env but keep system vars, just remove RK_SMOKE_REQUIRE_UI if present
        new_env = os.environ.copy()
        if "RK_SMOKE_REQUIRE_UI" in new_env:
            del new_env["RK_SMOKE_REQUIRE_UI"]

        # Mock import failure for app.ui.main_window
        with patch.dict(sys.modules, {'app.ui.main_window': None}):
            with patch.dict(os.environ, new_env, clear=True): 
                # verify test_imports returns True
                result = test_imports()
                self.assertTrue(result, "Should pass (skip) when UI missing by default")

    def test_missing_ui_fails_strict_mode(self):
        """Strict mode (RK_SMOKE_REQUIRE_UI=1): Missing UI -> Fail"""
        with patch.dict(sys.modules, {'app.ui.main_window': None}):
            with patch.dict(os.environ, {"RK_SMOKE_REQUIRE_UI": "1"}):
                # test_imports catches ImportError and returns False/print failure
                # BUT logic says "raise e" inside the except block?
                # Wait, my logic in smoke_test.py:
                # except ImportError as e: if env==1: raise e
                # Then outer try/except catches it and returns False?
                # Outer block: except ImportError as e: print... return False
                
                # So result should be False.
                result = test_imports()
                self.assertFalse(result, "Should fail when strict mode enabled and UI missing")

if __name__ == "__main__":
    unittest.main()
