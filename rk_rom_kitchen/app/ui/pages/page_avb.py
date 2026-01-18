"""
AVB/DM-Verity Page - Disable dm-verity + patch fstab
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from pathlib import Path

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.avb_manager import find_vbmeta_files, find_fstab_files, disable_dm_verity_demo


class PageAVB(QWidget):
    """AVB/dm-verity disable page"""
    
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
        
        title = QLabel("AVB / DM-Verity / Forceencrypt")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel("Disable Android Verified Boot, dm-verity va forceencrypt.")
        desc.setStyleSheet("color: #888;")
        layout.addWidget(desc)
        
        # vbmeta section
        vbmeta_group = QGroupBox("A) vbmeta Files")
        vbmeta_layout = QVBoxLayout(vbmeta_group)
        self._vbmeta_list = QListWidget()
        self._vbmeta_list.setMaximumHeight(120)
        vbmeta_layout.addWidget(self._vbmeta_list)
        
        vbmeta_btn = QHBoxLayout()
        self._btn_scan_vbmeta = QPushButton("Scan")
        self._btn_scan_vbmeta.clicked.connect(self._scan_vbmeta)
        vbmeta_btn.addWidget(self._btn_scan_vbmeta)
        
        self._btn_add_vbmeta = QPushButton("Browse...")
        self._btn_add_vbmeta.clicked.connect(self._browse_vbmeta)
        vbmeta_btn.addWidget(self._btn_add_vbmeta)
        vbmeta_btn.addStretch()
        vbmeta_layout.addLayout(vbmeta_btn)
        layout.addWidget(vbmeta_group)
        
        # fstab section
        fstab_group = QGroupBox("B) fstab Files")
        fstab_layout = QVBoxLayout(fstab_group)
        self._fstab_list = QListWidget()
        self._fstab_list.setMaximumHeight(120)
        fstab_layout.addWidget(self._fstab_list)
        
        self._btn_scan_fstab = QPushButton("Scan")
        self._btn_scan_fstab.clicked.connect(self._scan_fstab)
        fstab_layout.addWidget(self._btn_scan_fstab)
        layout.addWidget(fstab_group)
        
        # Actions
        action_layout = QHBoxLayout()
        
        self._btn_disable_all = QPushButton("Disable All (A+B)")
        self._btn_disable_all.clicked.connect(self._on_disable_all)
        self._btn_disable_all.setStyleSheet("background: #c62828;")
        action_layout.addWidget(self._btn_disable_all)
        
        self._btn_vbmeta_only = QPushButton("vbmeta Only")
        self._btn_vbmeta_only.clicked.connect(self._on_vbmeta_only)
        action_layout.addWidget(self._btn_vbmeta_only)
        
        self._btn_fstab_only = QPushButton("fstab Only")
        self._btn_fstab_only.clicked.connect(self._on_fstab_only)
        action_layout.addWidget(self._btn_fstab_only)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _scan_vbmeta(self):
        project = self._projects.current
        if not project:
            return
        
        self._vbmeta_list.clear()
        files = find_vbmeta_files(project)
        for f in files:
            self._vbmeta_list.addItem(str(f))
        self._log.info(f"Found {len(files)} vbmeta files")
    
    def _browse_vbmeta(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select vbmeta", "", "Image Files (*.img)")
        if path:
            self._vbmeta_list.addItem(path)
    
    def _scan_fstab(self):
        project = self._projects.current
        if not project:
            return
        
        self._fstab_list.clear()
        files = find_fstab_files(project)
        for f in files:
            self._fstab_list.addItem(str(f))
        self._log.info(f"Found {len(files)} fstab files")
    
    def _on_disable_all(self):
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Dang chay task khac")
            return
        
        project = self._projects.current
        if not project:
            return
        
        self._log.info("Disabling dm-verity (A+B)...")
        self._tasks.submit(
            disable_dm_verity_demo,
            task_type=TaskType.PATCH,
            on_finished=lambda r: self._log.success("Done") if r.ok else self._log.error(r.message),
            project=project
        )
    
    def _on_vbmeta_only(self):
        self._log.info("Creating disabled vbmeta...")
        self._on_disable_all()  # Demo
    
    def _on_fstab_only(self):
        self._log.info("Patching fstab...")
        self._on_disable_all()  # Demo
    
    def refresh(self):
        self._scan_vbmeta()
        self._scan_fstab()
    
    def update_translations(self):
        pass
