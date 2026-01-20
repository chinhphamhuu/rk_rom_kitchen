"""
Test Restart Utility
Verify app.core.utils.restart_application calls QProcess.startDetached and QApplication.quit
"""
import unittest
import sys
from unittest.mock import patch, MagicMock

from app.core import utils

class TestRestartUtils(unittest.TestCase):
    
    @patch("PyQt5.QtCore.QProcess")
    @patch("PyQt5.QtWidgets.QApplication")
    def test_restart_application(self, mock_qapp, mock_qprocess):
        """Test restart trigger"""
        # Call function
        utils.restart_application()
        
        # Verify startDetached called with sys.executable and sys.argv
        mock_qprocess.startDetached.assert_called_once_with(sys.executable, sys.argv)
        
        # Verify quit called
        mock_qapp.quit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
