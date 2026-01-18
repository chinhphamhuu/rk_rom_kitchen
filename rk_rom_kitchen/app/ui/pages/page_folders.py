"""
Folders Page - Trang quản lý thư mục project
"""
import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus


class PageFolders(QWidget):
    """
    Folders page:
    - Navigate project folders
    - Open in explorer
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel(t("page_folders_title"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Folder list
        self._folder_list = QListWidget()
        self._folder_list.itemDoubleClicked.connect(self._on_folder_double_clicked)
        layout.addWidget(self._folder_list)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self._btn_open = QPushButton(t("btn_open"))
        self._btn_open.clicked.connect(self._on_open_folder)
        btn_row.addWidget(self._btn_open)
        
        self._btn_refresh = QPushButton(t("btn_refresh"))
        self._btn_refresh.clicked.connect(self.refresh)
        btn_row.addWidget(self._btn_refresh)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        self.refresh()
    
    def refresh(self):
        """Refresh folder list"""
        self._folder_list.clear()
        
        project = self._projects.current
        if not project:
            self._folder_list.addItem("Chưa có project được chọn")
            return
        
        # Add folder items
        folders = [
            ("📁 in/ (Input ROM)", project.in_dir),
            ("📁 out/ (Output)", project.out_dir),
            ("  📁 Source/", project.source_dir),
            ("  📁 Image/", project.image_dir),
            ("📁 temp/", project.temp_dir),
            ("📁 logs/", project.logs_dir),
            ("📁 config/", project.config_dir),
        ]
        
        for label, path in folders:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, str(path))
            
            # Gray out if doesn't exist
            if not path.exists():
                item.setForeground(Qt.gray)
            
            self._folder_list.addItem(item)
    
    def _on_folder_double_clicked(self, item: QListWidgetItem):
        """Open folder on double click"""
        self._open_path(item)
    
    def _on_open_folder(self):
        """Open selected folder"""
        item = self._folder_list.currentItem()
        if item:
            self._open_path(item)
    
    def _open_path(self, item: QListWidgetItem):
        """Open path in file explorer"""
        path_str = item.data(Qt.UserRole)
        if not path_str:
            return
        
        path = Path(path_str)
        
        if not path.exists():
            # Create if doesn't exist
            path.mkdir(parents=True, exist_ok=True)
            self._log.info(f"Đã tạo thư mục: {path}")
        
        # Open in explorer
        if os.name == 'nt':
            os.startfile(str(path))
        else:
            subprocess.run(['xdg-open', str(path)])
        
        self._log.info(f"Mở thư mục: {path}")
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_open.setText(t("btn_open"))
        self._btn_refresh.setText(t("btn_refresh"))
