"""
RK ROM Kitchen - Entry Point
Công cụ mod ROM cho thiết bị Rockchip
"""
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from app.core.crash_guard import setup_global_exception_hooks
from app.i18n import set_language
from app.core.settings_store import get_settings_store
from app.core.logbus import get_log_bus
from app.ui.main_window import MainWindow


def main():
    """Main entry point"""
    # Install crash guard FIRST
    setup_global_exception_hooks(log_to_file=True)
    
    # Load settings
    settings = get_settings_store()
    
    # Set language from settings
    lang = settings.get('language', 'vi')
    set_language(lang)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("RK ROM Kitchen")
    app.setApplicationVersion("1.0.0")
    
    # Enable high DPI
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Setup log bus
    log = get_log_bus()
    from app.core.settings_store import get_appdata_dir
    log_file = get_appdata_dir() / 'app.log'
    log.set_log_file(log_file)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
