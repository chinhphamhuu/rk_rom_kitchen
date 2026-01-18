"""
Magisk Patch Page - Patch boot với Magisk
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QCheckBox, QListWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from pathlib import Path

from ...i18n import t
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.state_machine import get_state_machine, TaskType
from ...core.task_manager import get_task_manager
from ...core.boot_manager import find_boot_images
from ...core.magisk_patcher import patch_boot_with_magisk


class PageMagisk(QWidget):
    """Magisk Patch page"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._state = get_state_machine()
        self._tasks = get_task_manager()
        self._magisk_apk = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Magisk Patch")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Boot images list
        boot_group = QGroupBox("Boot Images")
        boot_layout = QVBoxLayout(boot_group)
        self._boot_list = QListWidget()
        self._boot_list.setMaximumHeight(150)
        boot_layout.addWidget(self._boot_list)
        
        btn_row = QHBoxLayout()
        self._btn_scan = QPushButton("Scan")
        self._btn_scan.clicked.connect(self._scan_boot)
        btn_row.addWidget(self._btn_scan)
        self._btn_browse_boot = QPushButton("Browse...")
        self._btn_browse_boot.clicked.connect(self._browse_boot)
        btn_row.addWidget(self._btn_browse_boot)
        btn_row.addStretch()
        boot_layout.addLayout(btn_row)
        layout.addWidget(boot_group)
        
        # Options
        opt_group = QGroupBox("Options")
        opt_layout = QVBoxLayout(opt_group)
        
        opt_row1 = QHBoxLayout()
        self._keep_verity = QCheckBox("Keep Verity")
        self._keep_verity.setChecked(True)
        opt_row1.addWidget(self._keep_verity)
        self._keep_force = QCheckBox("Keep Force")
        self._keep_force.setChecked(True)
        opt_row1.addWidget(self._keep_force)
        opt_row1.addStretch()
        opt_layout.addLayout(opt_row1)
        
        opt_row2 = QHBoxLayout()
        self._patch_vbmeta = QCheckBox("Patch vbmeta")
        opt_row2.addWidget(self._patch_vbmeta)
        self._recovery_mode = QCheckBox("Recovery Mode")
        opt_row2.addWidget(self._recovery_mode)
        opt_row2.addStretch()
        opt_layout.addLayout(opt_row2)
        
        arch_row = QHBoxLayout()
        arch_row.addWidget(QLabel("Arch:"))
        self._arch_combo = QComboBox()
        self._arch_combo.addItems(["arm64", "arm", "x86_64", "x86"])
        arch_row.addWidget(self._arch_combo)
        arch_row.addStretch()
        opt_layout.addLayout(arch_row)
        
        layout.addWidget(opt_group)
        
        # Magisk APK
        magisk_group = QGroupBox("Magisk APK")
        magisk_layout = QHBoxLayout(magisk_group)
        self._magisk_label = QLabel("Chua chon Magisk.apk")
        magisk_layout.addWidget(self._magisk_label, 1)
        self._btn_browse_magisk = QPushButton("Browse...")
        self._btn_browse_magisk.clicked.connect(self._browse_magisk)
        magisk_layout.addWidget(self._btn_browse_magisk)
        layout.addWidget(magisk_group)
        
        # Action
        action_layout = QHBoxLayout()
        self._btn_patch = QPushButton("Patch")
        self._btn_patch.clicked.connect(self._on_patch)
        action_layout.addWidget(self._btn_patch)
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
    
    def _browse_boot(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select boot image", "", "*.img")
        if path:
            self._boot_list.addItem(path)
    
    def _browse_magisk(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Magisk.apk", "", "*.apk")
        if path:
            self._magisk_apk = Path(path)
            self._magisk_label.setText(path)
    
    def _on_patch(self):
        if not self._state.can_start_task():
            QMessageBox.warning(self, "Warning", "Dang chay task khac")
            return
        
        if not self._magisk_apk:
            QMessageBox.warning(self, "Warning", "Chua chon Magisk.apk")
            return
        
        item = self._boot_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Chua chon boot image")
            return
        
        project = self._projects.current
        boot_path = Path(item.text())
        
        self._log.info(f"Patching {boot_path.name} with Magisk...")
        self._tasks.submit(
            patch_boot_with_magisk,
            task_type=TaskType.PATCH,
            on_finished=lambda r: self._log.success("Done") if r.ok else self._log.error(r.message),
            project=project,
            boot_image=boot_path,
            magisk_apk=self._magisk_apk,
            keep_verity=self._keep_verity.isChecked(),
            keep_force=self._keep_force.isChecked(),
            patch_vbmeta=self._patch_vbmeta.isChecked(),
            recovery_mode=self._recovery_mode.isChecked(),
            arch=self._arch_combo.currentText()
        )
    
    def refresh(self):
        self._scan_boot()
    
    def update_translations(self):
        pass
