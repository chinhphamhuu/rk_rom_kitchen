"""
File Picker - Widget để chọn file ROM
"""
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
)
from PyQt5.QtCore import pyqtSignal

from ...i18n import t


class FilePicker(QWidget):
    """
    File picker với text field và browse button
    """
    file_selected = pyqtSignal(str)  # file path
    
    def __init__(self, 
                 placeholder: str = "",
                 file_filter: str = "All Files (*.*)",
                 parent=None):
        super().__init__(parent)
        self._file_filter = file_filter
        self._placeholder = placeholder
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Path input
        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText(self._placeholder)
        self._path_input.setReadOnly(True)
        layout.addWidget(self._path_input, 1)
        
        # Browse button
        self._btn_browse = QPushButton(t("btn_browse"))
        self._btn_browse.setProperty("secondary", True)
        self._btn_browse.clicked.connect(self._on_browse)
        layout.addWidget(self._btn_browse)
    
    def _on_browse(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("dialog_select_rom"),
            "",
            self._file_filter
        )
        
        if file_path:
            self._path_input.setText(file_path)
            self.file_selected.emit(file_path)
    
    def get_path(self) -> str:
        """Lấy đường dẫn đã chọn"""
        return self._path_input.text()
    
    def set_path(self, path: str):
        """Set đường dẫn"""
        self._path_input.setText(path)
    
    def clear(self):
        """Clear selection"""
        self._path_input.clear()
    
    def set_filter(self, file_filter: str):
        """Set file filter"""
        self._file_filter = file_filter


class FolderPicker(QWidget):
    """
    Folder picker với text field và browse button
    """
    folder_selected = pyqtSignal(str)  # folder path
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Path input
        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText(self._placeholder)
        layout.addWidget(self._path_input, 1)
        
        # Browse button
        self._btn_browse = QPushButton(t("btn_browse"))
        self._btn_browse.setProperty("secondary", True)
        self._btn_browse.clicked.connect(self._on_browse)
        layout.addWidget(self._btn_browse)
    
    def _on_browse(self):
        """Open folder dialog"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            t("settings_tool_dir"),
            "",
        )
        
        if folder_path:
            self._path_input.setText(folder_path)
            self.folder_selected.emit(folder_path)
    
    def get_path(self) -> str:
        """Lấy đường dẫn đã chọn"""
        return self._path_input.text()
    
    def set_path(self, path: str):
        """Set đường dẫn"""
        self._path_input.setText(path)
