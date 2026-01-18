"""
Project Sidebar - Sidebar thứ 2 hiển thị project info và actions
Width ~280px
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QMenu, QAction, QInputDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor

from ...i18n import t
from ...core.app_context import get_app_context
from ...core.project_store import get_project_store
from ...core.logbus import get_log_bus


class InfoBox(QFrame):
    """Box hiển thị thông tin project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoBox")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title
        title = QLabel(t("project_info"))
        title.setProperty("heading", True)
        layout.addWidget(title)
        
        # Info rows
        self._info_labels = {}
        info_keys = ["build_id", "android_version", "brand", "model", "product"]
        
        for key in info_keys:
            row = QHBoxLayout()
            label = QLabel(t(key) + ":")
            label.setStyleSheet("color: #969696;")
            value = QLabel(t("placeholder"))
            value.setStyleSheet("color: #cccccc;")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)
            self._info_labels[key] = value
    
    def update_info(self, info: dict):
        """Update thông tin hiển thị"""
        mapping = {
            "build_id": "build_id",
            "android_version": "android_version", 
            "brand": "brand",
            "model": "model",
            "product": "product"
        }
        for key, label in self._info_labels.items():
            value = info.get(mapping.get(key, key), "")
            label.setText(value if value else t("placeholder"))


class ProjectSidebar(QWidget):
    """
    Project sidebar với:
    - Info box
    - Project selector
    - Context actions
    """
    # Signals
    project_changed = pyqtSignal(str)  # project_name
    action_triggered = pyqtSignal(str)  # action_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectSidebar")
        self.setFixedWidth(280)
        
        self._ctx = get_app_context()
        self._projects = get_project_store()
        self._log = get_log_bus()
        
        self._setup_ui()
        self._refresh_projects()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Info Box
        self._info_box = InfoBox()
        layout.addWidget(self._info_box)
        
        # Project Selector
        selector_layout = QVBoxLayout()
        selector_label = QLabel(t("select_project"))
        self._project_combo = QComboBox()
        self._project_combo.currentTextChanged.connect(self._on_project_selected)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self._project_combo)
        layout.addLayout(selector_layout)
        
        # Action buttons
        self._btn_create = QPushButton(t("menu_create_project"))
        self._btn_create.clicked.connect(self._on_create_project)
        layout.addWidget(self._btn_create)
        
        self._btn_delete = QPushButton(t("menu_delete_project"))
        self._btn_delete.setProperty("danger", True)
        self._btn_delete.clicked.connect(self._on_delete_project)
        layout.addWidget(self._btn_delete)
        
        # Stretch
        layout.addStretch()
        
        # Context menu buttons
        self._btn_folders = QPushButton(t("nav_folders") + " ▾")
        self._btn_folders.setProperty("secondary", True)
        self._btn_folders.clicked.connect(self._show_folders_menu)
        layout.addWidget(self._btn_folders)
        
        self._btn_build_menu = QPushButton(t("nav_build") + " ▾")
        self._btn_build_menu.setProperty("secondary", True)
        self._btn_build_menu.clicked.connect(self._show_build_menu)
        layout.addWidget(self._btn_build_menu)
        
        # Tools menu - Kernel/Decrypt/Boot
        self._btn_tools_menu = QPushButton("Kernel / Decrypt / Boot ▾")
        self._btn_tools_menu.setProperty("secondary", True)
        self._btn_tools_menu.clicked.connect(self._show_tools_menu)
        layout.addWidget(self._btn_tools_menu)
        
        # Other menu
        self._btn_other_menu = QPushButton("Other ▾")
        self._btn_other_menu.setProperty("secondary", True)
        self._btn_other_menu.clicked.connect(self._show_other_menu)
        layout.addWidget(self._btn_other_menu)
    
    def _refresh_projects(self):
        """Refresh danh sách projects"""
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        
        projects = self._projects.list_projects()
        if projects:
            self._project_combo.addItems(projects)
            # Select current if any
            current = self._projects.current
            if current and current.name in projects:
                self._project_combo.setCurrentText(current.name)
        else:
            self._project_combo.addItem(t("no_project"))
        
        self._project_combo.blockSignals(False)
        self._update_info()
    
    def _update_info(self):
        """Update info box từ current project"""
        project = self._projects.current
        if project:
            config = project.config
            self._info_box.update_info({
                "build_id": config.build_id,
                "android_version": config.android_version,
                "brand": config.brand,
                "model": config.model,
                "product": config.product,
            })
        else:
            self._info_box.update_info({})
    
    def _on_project_selected(self, name: str):
        """Handle project selection"""
        if name and name != t("no_project"):
            self._ctx.set_current_project(name)
            self._update_info()
            self.project_changed.emit(name)
    
    def _on_create_project(self):
        """Handle create project"""
        name, ok = QInputDialog.getText(
            self, 
            t("dialog_create_project"),
            t("dialog_project_name")
        )
        
        if ok and name:
            try:
                self._projects.create(name)
                self._ctx.set_current_project(name)
                self._log.success(f"Đã tạo project: {name}")
                self._refresh_projects()
                self.project_changed.emit(name)
                self.action_triggered.emit("project_created")
            except Exception as e:
                QMessageBox.warning(self, t("dialog_error"), str(e))
                self._log.error(f"Lỗi tạo project: {e}")
    
    def _on_delete_project(self):
        """Handle delete project"""
        current = self._projects.current
        if not current:
            return
        
        reply = QMessageBox.question(
            self,
            t("dialog_confirm"),
            t("dialog_delete_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            name = current.name
            if self._projects.delete(name):
                self._log.success(f"Đã xóa project: {name}")
                self._refresh_projects()
                self.action_triggered.emit("project_deleted")
            else:
                self._log.error(f"Không thể xóa project: {name}")
    
    def _show_folders_menu(self):
        """Show folders context menu"""
        menu = QMenu(self)
        
        actions = [
            ("menu_open_rom", "open_rom"),
            ("menu_open_build", "open_build"),
            ("menu_open_source", "open_source"),
            ("menu_open_output", "open_output"),
            ("menu_open_config", "open_config"),
            None,  # Separator
            ("menu_open_log", "open_log"),
        ]
        
        for item in actions:
            if item is None:
                menu.addSeparator()
            else:
                label_key, action_id = item
                action = QAction(t(label_key), self)
                action.triggered.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
                menu.addAction(action)
        
        menu.exec_(QCursor.pos())
    
    def _show_build_menu(self):
        """Show build context menu"""
        menu = QMenu(self)
        
        actions = [
            ("menu_build_image", "build_image"),
            ("menu_build_bulk", "build_bulk"),
            ("menu_build_super", "build_super"),
        ]
        
        for label_key, action_id in actions:
            action = QAction(t(label_key), self)
            action.triggered.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
            menu.addAction(action)
        
        menu.exec_(QCursor.pos())
    
    def refresh(self):
        """Public method để refresh"""
        self._refresh_projects()
    
    def _show_tools_menu(self):
        """Show Kernel/Decrypt/Boot menu giống CRB"""
        menu = QMenu(self)
        
        actions = [
            ("Android Boot Editor", "boot_editor"),
            ("Android Verified Boot (vbmeta)", "avb_page"),
            ("Patch Boot", "patch_boot"),
            ("Magisk Patch", "magisk_patch"),
        ]
        
        for label, action_id in actions:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
            menu.addAction(action)
        
        menu.exec_(QCursor.pos())
    
    def _show_other_menu(self):
        """Show Other menu giống CRB"""
        menu = QMenu(self)
        
        actions = [
            ("AVB/DM-Verity/Forceencrypt", "avb_page"),
            ("Make disabled vbmeta image", "make_vbmeta_disabled"),
            ("Force Encryption Disabler", "force_encryption"),
            None,  # Separator
            ("Debloater", "debloater"),
            None,
            ("Unpack/Repack boot", "boot_unpack"),
        ]
        
        for item in actions:
            if item is None:
                menu.addSeparator()
            else:
                label, action_id = item
                action = QAction(label, self)
                action.triggered.connect(lambda checked, aid=action_id: self.action_triggered.emit(aid))
                menu.addAction(action)
        
        menu.exec_(QCursor.pos())
    
    def update_translations(self):
        """Update UI khi đổi ngôn ngữ"""
        self._btn_create.setText(t("menu_create_project"))
        self._btn_delete.setText(t("menu_delete_project"))
        self._btn_folders.setText(t("nav_folders") + " ▾")
        self._btn_build_menu.setText(t("nav_build") + " ▾")
