"""
Status Panel - Panel góc trái dưới hiển thị progress và status
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar
)
from PyQt5.QtCore import pyqtSlot

from ...i18n import t
from ...core.state_machine import get_state_machine, AppState
from ... import __version__


class StatusPanel(QWidget):
    """
    Status panel với:
    - Progress bar
    - Status text
    - Version
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state_machine = get_state_machine()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)
        
        # Progress bar
        self._progress = QProgressBar()
        self._progress.setMaximumWidth(150)
        self._progress.setMaximumHeight(16)
        self._progress.setValue(0)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)
        
        # Status label
        self._status_label = QLabel(t("status_idle"))
        self._status_label.setStyleSheet("color: #969696;")
        layout.addWidget(self._status_label)
        
        # Stretch
        layout.addStretch()
        
        # Version
        self._version_label = QLabel(f"v{__version__}")
        self._version_label.setStyleSheet("color: #5a5a5a;")
        layout.addWidget(self._version_label)
    
    def _connect_signals(self):
        """Connect to state machine signals"""
        try:
            self._state_machine.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
    
    @pyqtSlot(str)
    def _on_state_changed(self, state: str):
        """Handle state change"""
        state_map = {
            "idle": ("status_idle", False),
            "running": ("status_running", True),
            "done": ("status_done", False),
            "error": ("status_error", False),
        }
        
        label_key, show_progress = state_map.get(state, ("status_idle", False))
        self._status_label.setText(t(label_key))
        self._progress.setVisible(show_progress)
        
        if show_progress:
            self._progress.setRange(0, 0)  # Indeterminate
        
        # Color based on state
        colors = {
            "idle": "#969696",
            "running": "#3794ff",
            "done": "#4ec9b0",
            "error": "#f14c4c",
        }
        color = colors.get(state, "#969696")
        self._status_label.setStyleSheet(f"color: {color};")
    
    def set_status(self, text: str):
        """Set custom status text"""
        self._status_label.setText(text)
    
    def set_progress(self, value: int, maximum: int = 100):
        """Set progress value"""
        self._progress.setVisible(True)
        self._progress.setRange(0, maximum)
        self._progress.setValue(value)
    
    def hide_progress(self):
        """Hide progress bar"""
        self._progress.setVisible(False)
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        state = self._state_machine.state
        state_labels = {
            AppState.IDLE: "status_idle",
            AppState.RUNNING: "status_running",
            AppState.DONE: "status_done",
            AppState.ERROR: "status_error",
        }
        label_key = state_labels.get(state, "status_idle")
        self._status_label.setText(t(label_key))
