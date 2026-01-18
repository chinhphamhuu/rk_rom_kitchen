"""
Toggles Panel - Panel hiển thị các toggle switches cho patches
"""
import json
from pathlib import Path
from typing import Dict, Callable
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QGroupBox
)
from PyQt5.QtCore import pyqtSignal

from ...i18n import t, get_language


class TogglesPanel(QWidget):
    """
    Panel với các toggle checkboxes cho patches
    """
    toggles_changed = pyqtSignal(dict)  # Dict[patch_id, enabled]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._toggles: Dict[str, QCheckBox] = {}
        self._presets: list = []
        self._categories: dict = {}
        
        self._setup_ui()
        self._load_presets()
    
    def _setup_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        
        # Placeholder - will be populated by _load_presets
        self._placeholder = QLabel("Loading presets...")
        self._layout.addWidget(self._placeholder)
    
    def _load_presets(self):
        """Load patch presets từ JSON"""
        presets_file = Path(__file__).parent.parent.parent.parent / 'patches' / 'patch_presets.json'
        
        try:
            if presets_file.exists():
                with open(presets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._presets = data.get('presets', [])
                self._categories = data.get('categories', {})
                self._build_toggles()
            else:
                self._placeholder.setText("Không tìm thấy patch_presets.json")
        except Exception as e:
            self._placeholder.setText(f"Lỗi load presets: {e}")
    
    def _build_toggles(self):
        """Build toggle checkboxes từ presets"""
        # Remove placeholder
        self._placeholder.setParent(None)
        
        # Group by category
        by_category: Dict[str, list] = {}
        for preset in self._presets:
            cat = preset.get('category', 'other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(preset)
        
        # Build groups
        lang = get_language()
        
        for cat_id, presets in by_category.items():
            cat_info = self._categories.get(cat_id, {})
            cat_name = cat_info.get(f'name_{lang}', cat_info.get('name', cat_id))
            
            group = QGroupBox(cat_name)
            group_layout = QVBoxLayout(group)
            
            for preset in presets:
                preset_id = preset.get('id', '')
                name = preset.get('name' if lang == 'vi' else 'name_en', preset.get('name', preset_id))
                description = preset.get('description', '')
                default = preset.get('enabled_default', False)
                
                checkbox = QCheckBox(name)
                checkbox.setChecked(default)
                checkbox.setToolTip(description)
                checkbox.stateChanged.connect(self._on_toggle_changed)
                
                self._toggles[preset_id] = checkbox
                group_layout.addWidget(checkbox)
            
            self._layout.addWidget(group)
        
        self._layout.addStretch()
    
    def _on_toggle_changed(self, state: int):
        """Emit signal khi toggle changes"""
        self.toggles_changed.emit(self.get_values())
    
    def get_values(self) -> Dict[str, bool]:
        """Lấy giá trị tất cả toggles"""
        return {
            patch_id: cb.isChecked()
            for patch_id, cb in self._toggles.items()
        }
    
    def set_values(self, values: Dict[str, bool]):
        """Set giá trị toggles"""
        for patch_id, enabled in values.items():
            if patch_id in self._toggles:
                self._toggles[patch_id].blockSignals(True)
                self._toggles[patch_id].setChecked(enabled)
                self._toggles[patch_id].blockSignals(False)
    
    def get_enabled_patches(self) -> list:
        """Lấy list các patches đang enabled"""
        return [
            patch_id for patch_id, cb in self._toggles.items()
            if cb.isChecked()
        ]
