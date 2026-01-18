"""
Patches Page - Trang áp dụng patches
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QScrollArea
)

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.pipeline import pipeline_patch
from ..widgets.toggles_panel import TogglesPanel


class PagePatches(QWidget):
    """
    Patches page:
    - Toggle các patch options
    - Apply patches
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
        title = QLabel(t("page_patches_title"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Patches toggles (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        self._toggles_panel = TogglesPanel()
        scroll.setWidget(self._toggles_panel)
        layout.addWidget(scroll, 1)
        
        # Actions
        btn_row = QHBoxLayout()
        
        self._btn_apply = QPushButton(t("btn_apply"))
        self._btn_apply.clicked.connect(self._on_apply)
        btn_row.addWidget(self._btn_apply)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Status
        self._lbl_status = QLabel("Chưa áp dụng patches")
        self._lbl_status.setStyleSheet("color: #969696;")
        layout.addWidget(self._lbl_status)
        
        # Connect state changes
        try:
            self._state.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
    
    def _on_apply(self):
        """Handle apply patches"""
        if not self._state.can_start_task():
            QMessageBox.warning(self, t("dialog_warning"), t("status_busy"))
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn project")
            return
        
        if not project.config.extracted:
            QMessageBox.warning(self, t("dialog_warning"), "Chưa extract ROM. Vui lòng extract trước.")
            return
        
        patches = self._toggles_panel.get_values()
        enabled_count = sum(1 for v in patches.values() if v)
        
        self._log.info(f"Áp dụng {enabled_count} patches...")
        
        self._tasks.submit(
            pipeline_patch,
            task_type=TaskType.PATCH,
            on_finished=self._on_apply_finished,
            project=project,
            patches=patches
        )
    
    def _on_apply_finished(self, result):
        """Handle apply completion"""
        if result.ok:
            self._log.success(f"Apply patches thành công trong {result.elapsed_ms}ms")
            self._lbl_status.setText("✓ Đã áp dụng patches")
            self._lbl_status.setStyleSheet("color: #4ec9b0;")
            self.refresh()
        else:
            self._log.error(f"Apply patches thất bại: {result.message}")
            QMessageBox.critical(self, t("dialog_error"), result.message)
    
    def _on_state_changed(self, state: str):
        """Update UI based on state"""
        is_busy = state == "running"
        self._btn_apply.setEnabled(not is_busy)
    
    def refresh(self):
        """Refresh page content"""
        project = self._projects.current
        if project and project.config.patched:
            self._lbl_status.setText("✓ Đã áp dụng patches")
            self._lbl_status.setStyleSheet("color: #4ec9b0;")
            
            # Load saved patch values
            saved_patches = project.config.patches
            if saved_patches:
                self._toggles_panel.set_values(saved_patches)
        else:
            self._lbl_status.setText("Chưa áp dụng patches")
            self._lbl_status.setStyleSheet("color: #969696;")
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_apply.setText(t("btn_apply"))
