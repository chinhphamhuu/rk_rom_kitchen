"""
Log Panel - Panel cố định ở dưới để hiển thị logs
Height ~180px
"""
import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLineEdit, QPushButton, QCheckBox, QLabel
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat

from ...i18n import t
from ...core.logbus import get_log_bus, LogLevel, LogEntry


class LogPanel(QWidget):
    """
    Log panel với:
    - Search/filter
    - Copy/Clear/Open log file
    - Auto-scroll toggle
    """
    
    # Colors for log levels
    LEVEL_COLORS = {
        LogLevel.DEBUG: "#808080",
        LogLevel.INFO: "#cccccc",
        LogLevel.WARNING: "#dcdcaa",
        LogLevel.ERROR: "#f14c4c",
        LogLevel.SUCCESS: "#4ec9b0",
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LogPanel")
        self.setMinimumHeight(150)
        self.setMaximumHeight(250)
        
        self._log_bus = get_log_bus()
        self._auto_scroll = True
        self._all_entries: list[LogEntry] = []
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # Title
        title = QLabel(t("log_title"))
        title.setStyleSheet("font-weight: bold;")
        toolbar.addWidget(title)
        
        # Search
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(t("log_search"))
        self._search_input.setMaximumWidth(200)
        self._search_input.textChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self._search_input)
        
        toolbar.addStretch()
        
        # Auto-scroll checkbox
        self._auto_scroll_cb = QCheckBox(t("log_auto_scroll"))
        self._auto_scroll_cb.setChecked(True)
        self._auto_scroll_cb.stateChanged.connect(self._on_auto_scroll_changed)
        toolbar.addWidget(self._auto_scroll_cb)
        
        # Buttons
        self._btn_copy = QPushButton(t("log_copy"))
        self._btn_copy.setProperty("secondary", True)
        self._btn_copy.setMaximumWidth(60)
        self._btn_copy.clicked.connect(self._on_copy)
        toolbar.addWidget(self._btn_copy)
        
        self._btn_clear = QPushButton(t("log_clear"))
        self._btn_clear.setProperty("secondary", True)
        self._btn_clear.setMaximumWidth(60)
        self._btn_clear.clicked.connect(self._on_clear)
        toolbar.addWidget(self._btn_clear)
        
        self._btn_open = QPushButton(t("log_open_file"))
        self._btn_open.setProperty("secondary", True)
        self._btn_open.setMaximumWidth(100)
        self._btn_open.clicked.connect(self._on_open_log_file)
        toolbar.addWidget(self._btn_open)
        
        layout.addLayout(toolbar)
        
        # Log text area
        self._log_text = QPlainTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._log_text.setMaximumBlockCount(1000)  # Limit entries
        layout.addWidget(self._log_text)
    
    def _connect_signals(self):
        """Connect to log bus signals"""
        try:
            self._log_bus.log_signal.connect(self._on_log_entry)
            self._log_bus.clear_signal.connect(self._on_clear)
        except AttributeError:
            # Non-Qt fallback
            pass
    
    @pyqtSlot(object)
    def _on_log_entry(self, entry: LogEntry):
        """Handle new log entry"""
        self._all_entries.append(entry)
        
        # Check filter
        filter_text = self._search_input.text().lower()
        if filter_text and filter_text not in entry.message.lower():
            return
        
        self._append_entry(entry)
    
    def _append_entry(self, entry: LogEntry):
        """Append entry to text widget với color"""
        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format with color
        fmt = QTextCharFormat()
        color = self.LEVEL_COLORS.get(entry.level, "#cccccc")
        fmt.setForeground(QColor(color))
        
        cursor.insertText(entry.formatted() + "\n", fmt)
        
        # Auto-scroll
        if self._auto_scroll:
            self._log_text.setTextCursor(cursor)
            self._log_text.ensureCursorVisible()
    
    def _on_filter_changed(self, text: str):
        """Re-filter logs"""
        self._log_text.clear()
        filter_text = text.lower()
        
        for entry in self._all_entries:
            if not filter_text or filter_text in entry.message.lower():
                self._append_entry(entry)
    
    def _on_auto_scroll_changed(self, state: int):
        """Toggle auto-scroll"""
        self._auto_scroll = state == Qt.Checked
    
    def _on_copy(self):
        """Copy log to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self._log_text.toPlainText())
        self._log_bus.info("Log đã được copy vào clipboard")
    
    def _on_clear(self):
        """Clear log"""
        self._log_text.clear()
        self._all_entries.clear()
    
    def _on_open_log_file(self):
        """Open log file in default editor"""
        from ...core.settings_store import get_appdata_dir
        
        log_dir = get_appdata_dir()
        log_file = log_dir / 'app.log'
        
        if log_file.exists():
            if os.name == 'nt':
                os.startfile(str(log_file))
            else:
                subprocess.run(['xdg-open', str(log_file)])
        else:
            self._log_bus.warning(f"Log file không tồn tại: {log_file}")
    
    def add_message(self, level: str, message: str):
        """Manual add message (for testing)"""
        level_map = {
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "success": LogLevel.SUCCESS,
        }
        entry = LogEntry(level_map.get(level, LogLevel.INFO), message)
        self._on_log_entry(entry)
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._search_input.setPlaceholderText(t("log_search"))
        self._auto_scroll_cb.setText(t("log_auto_scroll"))
        self._btn_copy.setText(t("log_copy"))
        self._btn_clear.setText(t("log_clear"))
        self._btn_open.setText(t("log_open_file"))
