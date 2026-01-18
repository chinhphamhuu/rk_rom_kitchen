"""
Build Page - Trang build output ROM
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox
)

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.pipeline import pipeline_build


class PageBuild(QWidget):
    """
    Build page:
    - Build output ROM
    - Show build status
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
        title = QLabel(t("page_build_title"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Status
        status_group = QGroupBox("Trạng thái")
        status_layout = QVBoxLayout(status_group)
        
        self._lbl_imported = QLabel("Imported: —")
        status_layout.addWidget(self._lbl_imported)
        
        self._lbl_extracted = QLabel("Extracted: —")
        status_layout.addWidget(self._lbl_extracted)
        
        self._lbl_patched = QLabel("Patched: —")
        status_layout.addWidget(self._lbl_patched)
        
        self._lbl_built = QLabel("Built: —")
        status_layout.addWidget(self._lbl_built)
        
        layout.addWidget(status_group)
        
        # Build actions
        build_group = QGroupBox("Build")
        build_layout = QVBoxLayout(build_group)
        
        self._btn_build = QPushButton(t("btn_build"))
        self._btn_build.clicked.connect(self._on_build)
        build_layout.addWidget(self._btn_build)
        
        desc = QLabel(
            "Build sẽ tạo file ROM output từ các files đã extract và patch.\n"
            "Output: out/update_patched.img"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #969696;")
        build_layout.addWidget(desc)
        
        layout.addWidget(build_group)
        
        # Output
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        self._lbl_output = QLabel("—")
        output_layout.addWidget(self._lbl_output)
        
        layout.addWidget(output_group)
        
        # Stretch
        layout.addStretch()
        
        # Connect state changes
        try:
            self._state.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
        
        self.refresh()
    
    def _on_build(self):
        """Handle build button"""
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
        
        self._log.info("Bắt đầu Build ROM...")
        
        self._tasks.submit(
            pipeline_build,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project
        )
    
    def _on_build_finished(self, result):
        """Handle build completion"""
        if result.ok:
            self._log.success(f"Build thành công trong {result.elapsed_ms}ms")
            if result.artifacts:
                self._lbl_output.setText(f"✓ {result.artifacts[0]}")
                self._lbl_output.setStyleSheet("color: #4ec9b0;")
            self.refresh()
        else:
            self._log.error(f"Build thất bại: {result.message}")
            QMessageBox.critical(self, t("dialog_error"), result.message)
    
    def _on_state_changed(self, state: str):
        """Update UI based on state"""
        is_busy = state == "running"
        self._btn_build.setEnabled(not is_busy)
    
    def refresh(self):
        """Refresh page content"""
        project = self._projects.current
        if project:
            config = project.config
            
            self._lbl_imported.setText(f"Imported: {'✓' if config.imported else '✗'}")
            self._lbl_extracted.setText(f"Extracted: {'✓' if config.extracted else '✗'}")
            self._lbl_patched.setText(f"Patched: {'✓' if config.patched else '✗'}")
            self._lbl_built.setText(f"Built: {'✓' if config.built else '✗'}")
            
            # Color coding
            for lbl, flag in [
                (self._lbl_imported, config.imported),
                (self._lbl_extracted, config.extracted),
                (self._lbl_patched, config.patched),
                (self._lbl_built, config.built),
            ]:
                color = "#4ec9b0" if flag else "#969696"
                lbl.setStyleSheet(f"color: {color};")
            
            # Check output file
            output_file = project.out_dir / "update_patched.img"
            if output_file.exists():
                self._lbl_output.setText(f"✓ {output_file}")
                self._lbl_output.setStyleSheet("color: #4ec9b0;")
            else:
                self._lbl_output.setText("—")
                self._lbl_output.setStyleSheet("")
        else:
            self._lbl_imported.setText("Imported: —")
            self._lbl_extracted.setText("Extracted: —")
            self._lbl_patched.setText("Patched: —")
            self._lbl_built.setText("Built: —")
            self._lbl_output.setText("—")
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_build.setText(t("btn_build"))
