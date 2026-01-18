"""
Extractor Page - Trang extract ROM
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QTextEdit
)

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.pipeline import pipeline_extract


class PageExtractor(QWidget):
    """
    Extractor page:
    - Extract ROM (Auto)
    - Show extraction status
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        title = QLabel(t("page_extractor_title"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Info
        info_group = QGroupBox("Thông tin")
        info_layout = QVBoxLayout(info_group)
        
        self._lbl_rom = QLabel("ROM: —")
        info_layout.addWidget(self._lbl_rom)
        
        self._lbl_type = QLabel("Type: —")
        info_layout.addWidget(self._lbl_type)
        
        self._lbl_status = QLabel("Status: Chưa extract")
        info_layout.addWidget(self._lbl_status)
        
        layout.addWidget(info_group)
        
        # Actions
        action_group = QGroupBox("Thao tác")
        action_layout = QVBoxLayout(action_group)
        
        self._btn_extract = QPushButton(t("menu_extract_auto"))
        self._btn_extract.clicked.connect(self._on_extract)
        action_layout.addWidget(self._btn_extract)
        
        # Description
        desc = QLabel(
            "Extract ROM (Auto) sẽ tự động detect loại ROM và extract tất cả partitions.\n"
            "Output sẽ được lưu vào thư mục out/Source và out/Image."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #969696;")
        action_layout.addWidget(desc)
        
        layout.addWidget(action_group)
        
        # Stretch
        layout.addStretch()
        
        # Connect state changes
        try:
            self._state.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
        
        self.refresh()
    
    def _on_extract(self):
        """Handle extract button"""
        if not self._state.can_start_task():
            QMessageBox.warning(self, t("dialog_warning"), t("status_busy"))
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn project")
            return
        
        if not project.config.imported:
            QMessageBox.warning(self, t("dialog_warning"), "Chưa import ROM. Vui lòng import ROM trước.")
            return
        
        self._log.info("Bắt đầu Extract ROM (Auto)")
        
        self._tasks.submit(
            pipeline_extract,
            task_type=TaskType.EXTRACT,
            on_finished=self._on_extract_finished,
            project=project
        )
    
    def _on_extract_finished(self, result):
        """Handle extract completion"""
        if result.ok:
            self._log.success(f"Extract thành công trong {result.elapsed_ms}ms")
            self.refresh()
        else:
            self._log.error(f"Extract thất bại: {result.message}")
            QMessageBox.critical(self, t("dialog_error"), result.message)
    
    def _on_state_changed(self, state: str):
        """Update UI based on state"""
        is_busy = state == "running"
        self._btn_extract.setEnabled(not is_busy)
    
    def refresh(self):
        """Refresh page content"""
        project = self._projects.current
        if project:
            config = project.config
            self._lbl_rom.setText(f"ROM: {config.input_file or '—'}")
            self._lbl_type.setText(f"Type: {config.rom_type or '—'}")
            
            if config.extracted:
                self._lbl_status.setText("Status: ✓ Đã extract")
                self._lbl_status.setStyleSheet("color: #4ec9b0;")
            else:
                self._lbl_status.setText("Status: Chưa extract")
                self._lbl_status.setStyleSheet("color: #969696;")
        else:
            self._lbl_rom.setText("ROM: —")
            self._lbl_type.setText("Type: —")
            self._lbl_status.setText("Status: Chưa có project")
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_extract.setText(t("menu_extract_auto"))
