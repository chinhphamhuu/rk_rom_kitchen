"""
Build Page - Trang build output ROM
OUTPUT CONTRACT: out/Image/... (dựa vào result.artifacts)
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QMessageBox, QComboBox, QCheckBox
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
    - Partition repack dropdown + Repack All (only for partition_image mode)
    - Show build status and output artifacts
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        
        # Track artifacts separately to avoid refresh() overwrite
        self._last_artifacts = []
        
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
        
        # Partition Repack section (ONLY for partition_image mode)
        self._partition_group = QGroupBox("Partition Repack")
        partition_layout = QVBoxLayout(self._partition_group)
        
        # Mode hint label
        self._lbl_partition_mode_hint = QLabel("")
        self._lbl_partition_mode_hint.setStyleSheet("color: #969696; font-style: italic;")
        self._lbl_partition_mode_hint.setWordWrap(True)
        partition_layout.addWidget(self._lbl_partition_mode_hint)
        
        # Dropdown + buttons row
        dropdown_row = QHBoxLayout()
        
        dropdown_row.addWidget(QLabel("Chọn partition:"))
        self._combo_partition = QComboBox()
        self._combo_partition.setMinimumWidth(150)
        dropdown_row.addWidget(self._combo_partition)
        
        self._btn_repack_one = QPushButton("Repack Partition")
        self._btn_repack_one.clicked.connect(self._on_repack_one)
        dropdown_row.addWidget(self._btn_repack_one)
        
        self._btn_repack_all = QPushButton("Repack All")
        self._btn_repack_all.clicked.connect(self._on_repack_all)
        dropdown_row.addWidget(self._btn_repack_all)
        
        dropdown_row.addStretch()
        partition_layout.addLayout(dropdown_row)
        
        # Output format
        format_row = QHBoxLayout()
        self._chk_sparse = QCheckBox("Output sparse (thay vì raw)")
        format_row.addWidget(self._chk_sparse)
        format_row.addStretch()
        partition_layout.addLayout(format_row)
        
        layout.addWidget(self._partition_group)
        
        # Build actions
        build_group = QGroupBox("Build ROM")
        build_layout = QVBoxLayout(build_group)
        
        self._btn_build = QPushButton(t("btn_build"))
        self._btn_build.clicked.connect(self._on_build)
        build_layout.addWidget(self._btn_build)
        
        desc = QLabel(
            "Build sẽ tạo file ROM output từ các files đã extract và patch.\n"
            "Output: out/Image/... (theo loại ROM)"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #969696;")
        build_layout.addWidget(desc)
        
        layout.addWidget(build_group)
        
        # Output section - split into summary and artifacts
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        # Summary line (can be updated by refresh)
        self._lbl_output_summary = QLabel("—")
        output_layout.addWidget(self._lbl_output_summary)
        
        # Artifacts list (NEVER overwritten by refresh)
        self._lbl_output_artifacts = QLabel("")
        self._lbl_output_artifacts.setWordWrap(True)
        output_layout.addWidget(self._lbl_output_artifacts)
        
        # Open output button
        btn_row = QHBoxLayout()
        self._btn_open_output = QPushButton("Mở out/Image")
        self._btn_open_output.clicked.connect(self._on_open_output)
        btn_row.addWidget(self._btn_open_output)
        btn_row.addStretch()
        output_layout.addLayout(btn_row)
        
        layout.addWidget(output_group)
        
        # Stretch
        layout.addStretch()
        
        # Connect state changes
        try:
            self._state.state_changed.connect(self._on_state_changed)
        except AttributeError:
            pass
        
        self.refresh()
    
    def _get_partition_list(self):
        """Get list of partitions from extract/partition_index.json"""
        project = self._projects.current
        if not project:
            return []
        
        try:
            from ...core.partition_image_engine import get_partition_list
            partitions = get_partition_list(project)
            return [p.get("partition_name", "") for p in partitions if p.get("partition_name")]
        except Exception:
            return []
    
    def _update_partition_repack_state(self):
        """Enable/disable Partition Repack group based on input_type"""
        project = self._projects.current
        
        if not project:
            self._partition_group.setEnabled(False)
            self._lbl_partition_mode_hint.setText("Vui lòng chọn project")
            return
        
        input_type = getattr(project.config, 'input_type', '')
        
        if input_type == "partition_image":
            self._partition_group.setEnabled(True)
            self._lbl_partition_mode_hint.setText("")
        else:
            self._partition_group.setEnabled(False)
            self._lbl_partition_mode_hint.setText(
                "Chức năng này chỉ dùng cho chế độ partition image (system.img/vendor.img/...). "
                "Với update.img/super.img, hãy dùng Extract/Build theo pipeline."
            )
    
    def _on_repack_one(self):
        """Repack selected partition"""
        if not self._state.can_start_task():
            QMessageBox.warning(self, t("dialog_warning"), t("status_busy"))
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn project")
            return
        
        partition_name = self._combo_partition.currentText()
        if not partition_name:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn partition từ dropdown")
            return
        
        # Update output_sparse config
        project.update_config(output_sparse=self._chk_sparse.isChecked())
        
        self._log.info(f"Repack Partition: {partition_name}...")
        self._clear_artifacts()
        
        self._tasks.submit(
            pipeline_build,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project,
            selected_partition=partition_name
        )
    
    def _on_repack_all(self):
        """Repack all partitions"""
        if not self._state.can_start_task():
            QMessageBox.warning(self, t("dialog_warning"), t("status_busy"))
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, t("dialog_warning"), "Vui lòng chọn project")
            return
        
        partitions = self._get_partition_list()
        if not partitions:
            QMessageBox.warning(self, t("dialog_warning"), "Chưa có partition nào. Hãy Extract trước.")
            return
        
        # Update output_sparse config
        project.update_config(output_sparse=self._chk_sparse.isChecked())
        
        self._log.info(f"Repack All: {len(partitions)} partitions...")
        self._clear_artifacts()
        
        self._tasks.submit(
            pipeline_build,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project
        )
    
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
        self._clear_artifacts()
        
        self._tasks.submit(
            pipeline_build,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project
        )
    
    def _clear_artifacts(self):
        """Clear artifacts display before build"""
        self._last_artifacts = []
        self._lbl_output_artifacts.setText("")
        self._lbl_output_summary.setText("Đang build...")
        self._lbl_output_summary.setStyleSheet("color: #969696;")
    
    def _on_build_finished(self, result):
        """Handle build completion - show artifacts from result, NOT overwritten by refresh"""
        if result.ok:
            self._log.success(f"Build thành công trong {result.elapsed_ms}ms")
            
            if result.artifacts:
                # Store artifacts to prevent refresh overwrite
                self._last_artifacts = result.artifacts[:]
                
                # Display artifacts list
                artifacts_text = "\n".join([f"✓ {a}" for a in result.artifacts[:5]])
                if len(result.artifacts) > 5:
                    artifacts_text += f"\n... và {len(result.artifacts) - 5} files khác"
                self._lbl_output_artifacts.setText(artifacts_text)
                self._lbl_output_artifacts.setStyleSheet("color: #4ec9b0;")
                
                # Summary
                self._lbl_output_summary.setText(f"✓ Hoàn tất: {len(result.artifacts)} files")
                self._lbl_output_summary.setStyleSheet("color: #4ec9b0;")
            else:
                # WARNING: OK but no artifacts
                self._lbl_output_artifacts.setText("")
                self._lbl_output_summary.setText(
                    "⚠️ Hoàn tất nhưng không nhận được artifacts. "
                    "Vui lòng mở logs/ để kiểm tra."
                )
                self._lbl_output_summary.setStyleSheet("color: #ffa500;")  # Orange warning
            
            self.refresh()
        else:
            self._log.error(f"Build thất bại: {result.message}")
            self._lbl_output_artifacts.setText("")
            self._lbl_output_summary.setText(f"✗ {result.message}")
            self._lbl_output_summary.setStyleSheet("color: #f14c4c;")
            QMessageBox.critical(self, t("dialog_error"), result.message)
    
    def _on_open_output(self):
        """Open out/Image folder"""
        import os
        project = self._projects.current
        if not project:
            return
        
        output_dir = project.out_image_dir
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        if os.name == 'nt':
            os.startfile(str(output_dir))
        else:
            import subprocess
            subprocess.run(['xdg-open', str(output_dir)])
        
        self._log.info(f"Mở thư mục: {output_dir}")
    
    def _on_state_changed(self, state: str):
        """Update UI based on state"""
        is_busy = state == "running"
        self._btn_build.setEnabled(not is_busy)
        self._btn_repack_one.setEnabled(not is_busy and self._partition_group.isEnabled())
        self._btn_repack_all.setEnabled(not is_busy and self._partition_group.isEnabled())
    
    def refresh(self):
        """Refresh page content - DOES NOT overwrite artifacts"""
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
            
            # Update partition repack state based on input_type
            self._update_partition_repack_state()
            
            # Populate partition dropdown
            self._combo_partition.clear()
            partitions = self._get_partition_list()
            if partitions:
                self._combo_partition.addItems(partitions)
            
            # Update summary ONLY if no artifacts stored
            if not self._last_artifacts:
                output_imgs = list(project.out_image_dir.rglob("*.img"))
                if output_imgs:
                    self._lbl_output_summary.setText(f"{len(output_imgs)} images trong out/Image/")
                    self._lbl_output_summary.setStyleSheet("color: #969696;")
                else:
                    self._lbl_output_summary.setText("—")
                    self._lbl_output_summary.setStyleSheet("")
        else:
            self._lbl_imported.setText("Imported: —")
            self._lbl_extracted.setText("Extracted: —")
            self._lbl_patched.setText("Patched: —")
            self._lbl_built.setText("Built: —")
            self._lbl_output_summary.setText("—")
            self._lbl_output_artifacts.setText("")
            self._combo_partition.clear()
            self._partition_group.setEnabled(False)
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_build.setText(t("btn_build"))
