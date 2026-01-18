"""
Build Image Page - Clone CRB layout với 3 groups settings
Phase 2.1: Proper UI ↔ config binding
"""
from copy import deepcopy
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QLineEdit, QCheckBox, QSpinBox, QMessageBox, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.build_image import (
    BuildImageConfig, DEFAULT_PARTITION_CONFIGS, build_image,
    find_file_contexts, find_fs_config, get_folder_size, estimate_image_size
)


class BuildImagePage(QWidget):
    """Build Image page với settings table giống CRB"""
    
    PARTITIONS = ["system_a", "vendor_a", "product_a", "odm_a", "system_ext_a"]
    OUTPUT_TYPES = ["both", "raw", "sparse"]  # Both is default
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        
        # Store widget references for binding
        self._widgets = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Build Image")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Splitter for settings and help
        splitter = QSplitter(Qt.Horizontal)
        
        # Settings panel
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1) Make Settings
        make_group = QGroupBox("1) Make Settings")
        make_layout = QVBoxLayout(make_group)
        self._add_line_edit(make_layout, "block_size", "Block Size", "4096", "Block size (1024/2048/4096)")
        self._add_line_edit(make_layout, "hash_algorithm", "Hash Algorithm", "half_md4", "Hash algo for ext4")
        self._add_checkbox(make_layout, "has_journal", "Has Journal", True, "Enable ext4 journal")
        self._add_line_edit(make_layout, "image_size", "Image Size", "0", "Size in bytes (0=auto)")
        self._add_line_edit(make_layout, "inode_size", "Inode Size", "256", "Inode size")
        settings_layout.addWidget(make_group)
        
        # 2) Android Settings
        android_group = QGroupBox("2) Android Settings")
        android_layout = QVBoxLayout(android_group)
        self._add_checkbox(android_layout, "ext4_share_duplicated_blocks", "Share Duplicated Blocks", True, "ext4 dedup")
        self._add_line_edit(android_layout, "file_contexts", "File Contexts", "", "Path to file_contexts")
        self._add_line_edit(android_layout, "fs_config", "FS Config", "", "Path to fs_config")
        self._add_line_edit(android_layout, "mount_point", "Mount Point", "/system", "Mount point")
        self._add_line_edit(android_layout, "source_dir", "Source Dir", "", "Source folder")
        settings_layout.addWidget(android_group)
        
        # 3) Common Settings
        common_group = QGroupBox("3) Common Settings")
        common_layout = QVBoxLayout(common_group)
        self._add_combo(common_layout, "filesystem", "File System", ["ext4", "erofs"], "Filesystem type")
        self._add_line_edit(common_layout, "output_filename", "Output", "system_a.img", "Output filename")
        self._add_combo(common_layout, "output_type", "Output Type", self.OUTPUT_TYPES, "raw/sparse/both")
        settings_layout.addWidget(common_group)
        
        splitter.addWidget(settings_widget)
        
        # Help panel
        self._help_panel = QTextEdit()
        self._help_panel.setReadOnly(True)
        self._help_panel.setMaximumWidth(300)
        self._help_panel.setPlaceholderText("Di chuyen vao field de xem mo ta")
        splitter.addWidget(self._help_panel)
        
        layout.addWidget(splitter, 1)
        
        # Bottom controls
        bottom = QHBoxLayout()
        
        self._partition_combo = QComboBox()
        self._partition_combo.addItems(self.PARTITIONS)
        self._partition_combo.currentTextChanged.connect(self._on_partition_changed)
        bottom.addWidget(QLabel("Partition:"))
        bottom.addWidget(self._partition_combo)
        
        bottom.addStretch()
        
        self._btn_build = QPushButton("Build")
        self._btn_build.clicked.connect(self._on_build)
        self._btn_build.setStyleSheet("background: #1976d2; padding: 8px 24px;")
        bottom.addWidget(self._btn_build)
        
        layout.addLayout(bottom)
        
        # Initial load
        self._on_partition_changed(self.PARTITIONS[0])
    
    def _add_line_edit(self, layout, key: str, label: str, default: str, help_text: str):
        """Add line edit with binding"""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(160)
        row.addWidget(lbl)
        
        widget = QLineEdit(default)
        widget.setToolTip(help_text)
        widget.focusInEvent = lambda e, h=help_text: self._show_help(h) or QLineEdit.focusInEvent(widget, e)
        row.addWidget(widget)
        
        self._widgets[key] = widget
        layout.addLayout(row)
    
    def _add_checkbox(self, layout, key: str, label: str, default: bool, help_text: str):
        """Add checkbox with binding"""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(160)
        row.addWidget(lbl)
        
        widget = QCheckBox()
        widget.setChecked(default)
        widget.setToolTip(help_text)
        row.addWidget(widget)
        row.addStretch()
        
        self._widgets[key] = widget
        layout.addLayout(row)
    
    def _add_combo(self, layout, key: str, label: str, options: list, help_text: str):
        """Add combo box with binding"""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(160)
        row.addWidget(lbl)
        
        widget = QComboBox()
        widget.addItems(options)
        widget.setToolTip(help_text)
        row.addWidget(widget)
        row.addStretch()
        
        self._widgets[key] = widget
        layout.addLayout(row)
    
    def _show_help(self, text: str):
        """Show help text in panel"""
        self._help_panel.setText(text)
    
    def _load_config_to_ui(self, config: BuildImageConfig):
        """Load config values into UI widgets"""
        mapping = {
            "block_size": str(config.block_size),
            "hash_algorithm": config.hash_algorithm,
            "has_journal": config.has_journal,
            "image_size": str(config.image_size),
            "inode_size": str(config.inode_size),
            "ext4_share_duplicated_blocks": config.ext4_share_duplicated_blocks,
            "file_contexts": config.file_contexts,
            "fs_config": config.fs_config,
            "mount_point": config.mount_point,
            "source_dir": config.source_dir,
            "filesystem": config.filesystem,
            "output_filename": config.output_filename,
            "output_type": config.output_type,
        }
        
        for key, value in mapping.items():
            widget = self._widgets.get(key)
            if widget is None:
                continue
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QComboBox):
                idx = widget.findText(str(value))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
    
    def _read_config_from_ui(self) -> BuildImageConfig:
        """Read UI widget values into a new config"""
        config = BuildImageConfig()
        
        # Read each widget
        config.block_size = int(self._widgets["block_size"].text() or "4096")
        config.hash_algorithm = self._widgets["hash_algorithm"].text()
        config.has_journal = self._widgets["has_journal"].isChecked()
        config.image_size = int(self._widgets["image_size"].text() or "0")
        config.inode_size = int(self._widgets["inode_size"].text() or "256")
        config.ext4_share_duplicated_blocks = self._widgets["ext4_share_duplicated_blocks"].isChecked()
        config.file_contexts = self._widgets["file_contexts"].text()
        config.fs_config = self._widgets["fs_config"].text()
        config.mount_point = self._widgets["mount_point"].text()
        config.source_dir = self._widgets["source_dir"].text()
        config.filesystem = self._widgets["filesystem"].currentText()
        config.output_filename = self._widgets["output_filename"].text()
        config.output_type = self._widgets["output_type"].currentText()
        
        return config
    
    def _on_partition_changed(self, partition: str):
        """Load config for partition - creates NEW config instance"""
        project = self._projects.current
        if not project:
            self._log.warning("[BUILD_IMAGE] No project selected")
            return
        
        # Create NEW config instance (deepcopy to avoid mutable reference)
        if partition in DEFAULT_PARTITION_CONFIGS:
            config = deepcopy(DEFAULT_PARTITION_CONFIGS[partition])
        else:
            config = BuildImageConfig()
            config.mount_point = f"/{partition.replace('_a', '')}"
            config.output_filename = f"{partition}.img"
        
        # Set source dir
        source_dir = project.source_dir / partition
        config.source_dir = str(source_dir)
        
        # Auto-detect file_contexts and fs_config
        fc = find_file_contexts(project, partition)
        if fc:
            config.file_contexts = str(fc)
        
        fsc = find_fs_config(project, partition)
        if fsc:
            config.fs_config = str(fsc)
        
        # Auto-calc image size if source exists
        if source_dir.exists():
            folder_size = get_folder_size(source_dir)
            config.image_size = estimate_image_size(folder_size)
        
        # Load project preset if exists
        try:
            presets = project.config.build_presets or {}
            if partition in presets:
                saved = presets[partition]
                # Merge saved values
                for key, value in saved.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        except Exception as e:
            self._log.debug(f"[BUILD_IMAGE] Could not load preset: {e}")
        
        # Load config values into UI
        self._load_config_to_ui(config)
    
    def _on_build(self):
        """Build button clicked - validate and submit task"""
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Đang chạy task khác. Vui lòng đợi.")
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, "Warning", "Chưa chọn project. Hãy tạo hoặc mở project trước.")
            self._log.error("[BUILD_IMAGE] No project selected")
            return
        
        # Read config from UI
        config = self._read_config_from_ui()
        partition = self._partition_combo.currentText()
        
        # Validate source dir
        source_path = Path(config.source_dir)
        if not source_path.exists():
            QMessageBox.warning(
                self, "Warning",
                f"Source folder không tồn tại:\n{config.source_dir}\n\nHãy extract ROM trước."
            )
            self._log.error(f"[BUILD_IMAGE] Source not found: {config.source_dir}")
            return
        
        # Validate output filename
        if not config.output_filename:
            config.output_filename = f"{partition}.img"
        
        self._log.info(f"[BUILD_IMAGE] Building {partition}...")
        self._log.info(f"[BUILD_IMAGE] Source: {config.source_dir}")
        self._log.info(f"[BUILD_IMAGE] Output type: {config.output_type}")
        
        self._tasks.submit(
            build_image,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project,
            partition=partition,
            config=config
        )
    
    def _on_build_finished(self, result):
        if result.ok:
            self._log.success(f"[BUILD_IMAGE] Completed: {result.message}")
            QMessageBox.information(self, "Success", f"Build hoàn thành!\n{result.message}")
        else:
            self._log.error(f"[BUILD_IMAGE] Failed: {result.message}")
            QMessageBox.critical(self, "Error", f"Build thất bại:\n{result.message}")
    
    def refresh(self):
        """Refresh page when shown"""
        self._on_partition_changed(self._partition_combo.currentText())
    
    def update_translations(self):
        pass
