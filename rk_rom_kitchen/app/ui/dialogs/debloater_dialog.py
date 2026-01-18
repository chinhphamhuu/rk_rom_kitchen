"""
Debloater Dialog - Scan và xóa APK bloatware
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt

from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus
from ...core.debloater import scan_apks, delete_apks, ApkInfo


class DebloaterDialog(QDialog):
    """Debloater floating window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects = get_project_store()
        self._log = get_log_bus()
        self._apks = []
        self._filtered_apks = []
        self.setWindowTitle("Debloater")
        self.setMinimumSize(800, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self._info_label = QLabel("Loaded 0 APKs")
        header.addWidget(self._info_label)
        header.addStretch()
        self._btn_scan = QPushButton("Scan")
        self._btn_scan.clicked.connect(self._on_scan)
        header.addWidget(self._btn_scan)
        layout.addLayout(header)
        
        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Filename", "Package", "Internal Name", "Size", "Partition"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self._table)
        
        # Search
        search_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search...")
        self._search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self._search_input)
        layout.addLayout(search_layout)
        
        # Actions
        action_layout = QHBoxLayout()
        self._btn_select_all = QPushButton("Select All")
        self._btn_select_all.clicked.connect(lambda: self._table.selectAll())
        action_layout.addWidget(self._btn_select_all)
        
        self._btn_deselect = QPushButton("Deselect")
        self._btn_deselect.clicked.connect(lambda: self._table.clearSelection())
        action_layout.addWidget(self._btn_deselect)
        
        action_layout.addStretch()
        
        self._btn_delete = QPushButton("Delete Selected")
        self._btn_delete.setStyleSheet("background: #c62828;")
        self._btn_delete.clicked.connect(self._on_delete)
        action_layout.addWidget(self._btn_delete)
        
        layout.addLayout(action_layout)
    
    def _on_scan(self):
        project = self._projects.current
        if not project:
            QMessageBox.warning(self, "Warning", "Chua chon project")
            return
        
        self._log.info("[DEBLOAT] Scanning APKs...")
        self._apks = scan_apks(project)
        self._filtered_apks = self._apks[:]
        self._update_table()
        self._info_label.setText(f"Loaded {len(self._apks)} APKs")
    
    def _update_table(self):
        self._table.setRowCount(len(self._filtered_apks))
        for i, apk in enumerate(self._filtered_apks):
            self._table.setItem(i, 0, QTableWidgetItem(apk.filename))
            self._table.setItem(i, 1, QTableWidgetItem(apk.package_name))
            self._table.setItem(i, 2, QTableWidgetItem(apk.internal_name))
            self._table.setItem(i, 3, QTableWidgetItem(apk.size_str))
            self._table.setItem(i, 4, QTableWidgetItem(apk.partition))
    
    def _on_search(self, text):
        text = text.lower()
        if not text:
            self._filtered_apks = self._apks[:]
        else:
            self._filtered_apks = [a for a in self._apks if text in a.filename.lower() or text in a.partition.lower()]
        self._update_table()
    
    def _on_delete(self):
        selected = self._table.selectedItems()
        if not selected:
            return
        
        # Get unique rows
        rows = set()
        for item in selected:
            rows.add(item.row())
        
        apks_to_delete = [self._filtered_apks[r] for r in rows]
        
        # Confirm
        msg = f"Xoa {len(apks_to_delete)} APK vao Recycle Bin?\n\n"
        msg += "\n".join([a.filename for a in apks_to_delete[:10]])
        if len(apks_to_delete) > 10:
            msg += f"\n... va {len(apks_to_delete) - 10} file khac"
        
        reply = QMessageBox.question(self, "Confirm Delete", msg, QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        project = self._projects.current
        result = delete_apks(project, apks_to_delete, use_recycle_bin=True)
        
        if result.ok:
            self._log.success(result.message)
            self._on_scan()  # Refresh
        else:
            # Ask for permanent delete
            reply = QMessageBox.question(
                self, "Recycle Bin Failed",
                "Khong the di chuyen vao Recycle Bin. Xoa vinh vien?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                result = delete_apks(project, apks_to_delete, use_recycle_bin=False)
                if result.ok:
                    self._log.success(result.message)
                    self._on_scan()
                else:
                    self._log.error(result.message)
    
    def showEvent(self, event):
        super().showEvent(event)
        self._on_scan()
