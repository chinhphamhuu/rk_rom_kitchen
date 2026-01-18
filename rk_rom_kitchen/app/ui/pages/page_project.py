"""
Project Page - Trang quản lý project
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from pathlib import Path

from ...i18n import t
from ...core.app_context import get_app_context
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.pipeline import pipeline_import
from ..widgets.file_picker import FilePicker


class PageProject(QWidget):
    """
    Project page:
    - Import ROM file
    - Project overview
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ctx = get_app_context()
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title = QLabel(t("page_project_title"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Import ROM section
        import_group = QGroupBox(t("btn_import"))
        import_layout = QVBoxLayout(import_group)
        
        # File picker
        self._file_picker = FilePicker(
            placeholder="Chọn file ROM (update.img, release_update.img, super.img)",
            file_filter="ROM Files (*.img);;All Files (*.*)"
        )
        import_layout.addWidget(self._file_picker)
        
        # Import button
        btn_row = QHBoxLayout()
        self._btn_import = QPushButton(t("btn_import"))
        self._btn_import.clicked.connect(self._on_import)
        btn_row.addWidget(self._btn_import)
        btn_row.addStretch()
        import_layout.addLayout(btn_row)
        
        layout.addWidget(import_group)
        
        # Project status section
        status_group = QGroupBox("Trạng thái Project")
        status_layout = QVBoxLayout(status_group)
        
        self._lbl_status = QLabel("Chưa có project được chọn")
        status_layout.addWidget(self._lbl_status)
        
        layout.addWidget(status_group)
        
        # Stretch
        layout.addStretch()
        
        # Connect state changes
        try:
            self._state.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
    
    def _on_import(self):
        """Handle import button click"""
        # Check state
        if not self._state.can_start_task():
            self._log.warning(t("status_busy"))
            QMessageBox.warning(self, t("dialog_warning"), t("status_busy"))
            return
        
        # Check project
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn hoặc tạo project trước")
            return
        
        # Check file
        file_path = self._file_picker.get_path()
        if not file_path:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn file ROM")
            return
        
        source_file = Path(file_path)
        if not source_file.exists():
            QMessageBox.warning(self, t("dialog_warning"), f"File không tồn tại: {file_path}")
            return
        
        # Run import task
        self._log.info(f"Bắt đầu import: {source_file.name}")
        
        self._tasks.submit(
            pipeline_import,
            task_type=TaskType.IMPORT,
            on_finished=self._on_import_finished,
            project=project,
            source_file=source_file
        )
    
    def _on_import_finished(self, result):
        """Handle import completion"""
        if result.ok:
            self._log.success(f"Import thành công: {result.message}")
            self.refresh()
        else:
            self._log.error(f"Import thất bại: {result.message}")
            QMessageBox.critical(self, t("dialog_error"), result.message)
    
    def _on_state_changed(self, state: str):
        """Update UI based on state"""
        is_busy = state == "running"
        self._btn_import.setEnabled(not is_busy)
    
    def refresh(self):
        """Refresh page content"""
        project = self._projects.current
        if project:
            config = project.config
            status_lines = [
                f"Project: {project.name}",
                f"ROM type: {config.rom_type or '—'}",
                f"Imported: {'✓' if config.imported else '✗'}",
                f"Extracted: {'✓' if config.extracted else '✗'}",
                f"Patched: {'✓' if config.patched else '✗'}",
                f"Built: {'✓' if config.built else '✗'}",
            ]
            self._lbl_status.setText('\n'.join(status_lines))
        else:
            self._lbl_status.setText("Chưa có project được chọn")
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_import.setText(t("btn_import"))
