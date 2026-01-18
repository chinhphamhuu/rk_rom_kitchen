"""
Icon Sidebar - Navigation sidebar bên trái với icons
Width ~56px, giống CRB layout
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QButtonGroup, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon

from ..qss import get_color
from ...i18n import t


class IconSidebar(QWidget):
    """
    Icon sidebar navigation
    Các items: Project, Folders, Extractor, Patches, Build, Settings, About
    """
    # Signal khi page được chọn
    page_changed = pyqtSignal(str)  # page_id
    
    # Page definitions
    PAGES = [
        ("project", "nav_project", "📁"),
        ("folders", "nav_folders", "📂"),
        ("extractor", "nav_extractor", "📦"),
        ("patches", "nav_patches", "🔧"),
        ("build", "nav_build", "🔨"),
    ]
    
    BOTTOM_PAGES = [
        ("settings", "nav_settings", "⚙️"),
        ("about", "nav_about", "ℹ️"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IconSidebar")
        self.setFixedWidth(56)
        
        self._buttons: dict[str, QPushButton] = {}
        self._current_page = "project"
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Button group cho exclusive selection
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        
        # Main pages
        for page_id, label_key, icon in self.PAGES:
            btn = self._create_nav_button(page_id, label_key, icon)
            layout.addWidget(btn)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Bottom pages (Settings, About)
        for page_id, label_key, icon in self.BOTTOM_PAGES:
            btn = self._create_nav_button(page_id, label_key, icon)
            layout.addWidget(btn)
        
        # Select first page
        if "project" in self._buttons:
            self._buttons["project"].setChecked(True)
    
    def _create_nav_button(self, page_id: str, label_key: str, icon: str) -> QPushButton:
        """Tạo navigation button"""
        btn = QPushButton(icon)
        btn.setCheckable(True)
        btn.setToolTip(t(label_key))
        btn.setFixedSize(56, 48)
        btn.setProperty("page_id", page_id)
        
        # Font size cho emoji icon
        btn.setStyleSheet("font-size: 20px;")
        
        btn.clicked.connect(lambda checked, pid=page_id: self._on_button_clicked(pid))
        
        self._button_group.addButton(btn)
        self._buttons[page_id] = btn
        
        return btn
    
    def _on_button_clicked(self, page_id: str):
        """Handle button click"""
        self._current_page = page_id
        self.page_changed.emit(page_id)
    
    def set_page(self, page_id: str):
        """Programmatically set current page"""
        if page_id in self._buttons:
            self._buttons[page_id].setChecked(True)
            self._current_page = page_id
    
    def get_current_page(self) -> str:
        """Lấy page hiện tại"""
        return self._current_page
    
    def update_translations(self):
        """Update tooltips khi đổi ngôn ngữ"""
        for page_id, label_key, _ in self.PAGES + self.BOTTOM_PAGES:
            if page_id in self._buttons:
                self._buttons[page_id].setToolTip(t(label_key))
