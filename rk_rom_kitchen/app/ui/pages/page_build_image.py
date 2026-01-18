"""
Build Image Page - Clone CRB layout với 3 groups settings
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QLineEdit, QCheckBox, QSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.build_image import (
    BuildImageConfig, DEFAULT_PARTITION_CONFIGS, build_image_demo,
    find_file_contexts, find_fs_config, get_folder_size, estimate_image_size
)


class BuildImagePage(QWidget):
    """Build Image page với settings table giống CRB"""
    
    PARTITIONS = ["system_a", "vendor_a", "product_a", "odm_a", "system_ext_a"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        self._config = BuildImageConfig()
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
        self._add_setting_row(make_layout, "block_size", "Block Size", "4096", "Block size in bytes (1024/2048/4096)")
        self._add_setting_row(make_layout, "hash_algorithm", "Hash Algorithm", "half_md4", "Hash algo for ext4")
        self._add_setting_row(make_layout, "has_journal", "Has Journal", True, "Enable journal")
        self._add_setting_row(make_layout, "image_size", "Image Size", "0", "Image size in bytes (0=auto)")
        self._add_setting_row(make_layout, "inode_size", "Inode Size", "256", "Inode size")
        settings_layout.addWidget(make_group)
        
        # 2) Android Settings
        android_group = QGroupBox("2) Android Settings")
        android_layout = QVBoxLayout(android_group)
        self._add_setting_row(android_layout, "ext4_share", "Share Duplicated Blocks", True, "ext4 dedup")
        self._add_setting_row(android_layout, "file_contexts", "File Contexts", "", "Path to file_contexts")
        self._add_setting_row(android_layout, "fs_config", "FS Config", "", "Path to fs_config")
        self._add_setting_row(android_layout, "mount_point", "Mount Point", "/system", "Mount point")
        self._add_setting_row(android_layout, "source_dir", "Source Dir", "", "Source folder (read-only)")
        settings_layout.addWidget(android_group)
        
        # 3) Common Settings
        common_group = QGroupBox("3) Common Settings")
        common_layout = QVBoxLayout(common_group)
        self._add_combo_row(common_layout, "filesystem", "File System", ["ext4", "erofs"])
        self._add_setting_row(common_layout, "output", "Output", "system_a.img", "Output filename")
        self._add_combo_row(common_layout, "output_type", "Output Type", ["raw", "sparse"])
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
        bottom.addWidget(self._btn_build)
        
        layout.addLayout(bottom)
        
        self._on_partition_changed(self.PARTITIONS[0])
    
    def _add_setting_row(self, layout, key, label, default, help_text=""):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(150)
        row.addWidget(lbl)
        
        if isinstance(default, bool):
            widget = QCheckBox()
            widget.setChecked(default)
        else:
            widget = QLineEdit(str(default))
            widget.setProperty("help", help_text)
        
        widget.setProperty("config_key", key)
        row.addWidget(widget)
        layout.addLayout(row)
    
    def _add_combo_row(self, layout, key, label, options):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(150)
        row.addWidget(lbl)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setProperty("config_key", key)
        row.addWidget(combo)
        layout.addLayout(row)
    
    def _on_partition_changed(self, partition):
        """Load config for partition"""
        project = self._projects.current
        if not project:
            return
        
        # Get default config
        if partition in DEFAULT_PARTITION_CONFIGS:
            self._config = DEFAULT_PARTITION_CONFIGS[partition]
        else:
            self._config = BuildImageConfig()
        
        # Set source dir
        source_dir = project.source_dir / partition
        self._config.source_dir = str(source_dir)
        
        # Auto-detect files
        fc = find_file_contexts(project, partition)
        if fc:
            self._config.file_contexts = str(fc)
        
        fsc = find_fs_config(project, partition)
        if fsc:
            self._config.fs_config = str(fsc)
        
        # Auto-calc image size
        if source_dir.exists():
            folder_size = get_folder_size(source_dir)
            self._config.image_size = estimate_image_size(folder_size)
    
    def _on_build(self):
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Dang chay task khac")
            return
        
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, "Warning", "Chua chon project")
            return
        
        partition = self._partition_combo.currentText()
        self._log.info(f"Building {partition}...")
        
        self._tasks.submit(
            build_image_demo,
            task_type=TaskType.BUILD,
            on_finished=self._on_build_finished,
            project=project,
            partition=partition,
            config=self._config
        )
    
    def _on_build_finished(self, result):
        if result.ok:
            self._log.success(f"Build completed: {result.message}")
        else:
            self._log.error(f"Build failed: {result.message}")
    
    def refresh(self):
        self._on_partition_changed(self._partition_combo.currentText())
    
    def update_translations(self):
        pass
