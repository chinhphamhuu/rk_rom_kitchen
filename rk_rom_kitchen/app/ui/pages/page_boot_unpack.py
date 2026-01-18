"""
Boot Unpack/Repack Page
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QListWidget, QFileDialog, QMessageBox
)
from pathlib import Path

from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.boot_manager import find_boot_images, unpack_boot_image, repack_boot_image


class PageBootUnpack(QWidget):
    """Boot Unpack/Repack page"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Unpack/Repack Boot")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Boot images
        boot_group = QGroupBox("Boot Images")
        boot_layout = QVBoxLayout(boot_group)
        self._boot_list = QListWidget()
        boot_layout.addWidget(self._boot_list)
        
        btn_row = QHBoxLayout()
        self._btn_scan = QPushButton("Scan")
        self._btn_scan.clicked.connect(self._scan_boot)
        btn_row.addWidget(self._btn_scan)
        self._btn_browse = QPushButton("Browse...")
        self._btn_browse.clicked.connect(self._browse_boot)
        btn_row.addWidget(self._btn_browse)
        btn_row.addStretch()
        boot_layout.addLayout(btn_row)
        layout.addWidget(boot_group)
        
        # Actions
        action_layout = QHBoxLayout()
        self._btn_unpack = QPushButton("Unpack")
        self._btn_unpack.clicked.connect(self._on_unpack)
        action_layout.addWidget(self._btn_unpack)
        
        self._btn_repack = QPushButton("Repack")
        self._btn_repack.clicked.connect(self._on_repack)
        action_layout.addWidget(self._btn_repack)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _scan_boot(self):
        project = self._projects.current
        if not project:
            return
        self._boot_list.clear()
        for f in find_boot_images(project):
            self._boot_list.addItem(str(f))
        # Also add unpacked folders
        unpacked_dir = project.out_dir / "boot_unpacked"
        if unpacked_dir.exists():
            for d in unpacked_dir.iterdir():
                if d.is_dir():
                    self._boot_list.addItem(f"[UNPACKED] {d}")
    
    def _browse_boot(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select boot image", "", "*.img")
        if path:
            self._boot_list.addItem(path)
    
    def _on_unpack(self):
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Dang chay task khac")
            return
        
        item = self._boot_list.currentItem()
        if not item or "[UNPACKED]" in item.text():
            QMessageBox.warning(self, "Warning", "Chon boot image de unpack")
            return
        
        project = self._projects.current
        boot_path = Path(item.text())
        
        self._log.info(f"Unpacking {boot_path.name}...")
        self._tasks.submit(
            unpack_boot_image,
            task_type=TaskType.EXTRACT,
            on_finished=lambda r: (self._log.success("Done"), self._scan_boot()) if r.ok else self._log.error(r.message),
            project=project,
            boot_image=boot_path
        )
    
    def _on_repack(self):
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Dang chay task khac")
            return
        
        item = self._boot_list.currentItem()
        if not item or "[UNPACKED]" not in item.text():
            QMessageBox.warning(self, "Warning", "Chon folder da unpack de repack")
            return
        
        project = self._projects.current
        unpacked_path = Path(item.text().replace("[UNPACKED] ", ""))
        
        self._log.info(f"Repacking {unpacked_path.name}...")
        self._tasks.submit(
            repack_boot_image,
            task_type=TaskType.BUILD,
            on_finished=lambda r: self._log.success("Done") if r.ok else self._log.error(r.message),
            project=project,
            unpacked_dir=unpacked_path
        )
    
    def refresh(self):
        self._scan_boot()
    
    def update_translations(self):
        pass
