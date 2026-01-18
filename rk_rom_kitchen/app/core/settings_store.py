"""
Settings Store - Load/save settings từ %APPDATA%\rk_kitchen\settings.json
"""
import json
import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict


def get_appdata_dir() -> Path:
    """Lấy đường dẫn %APPDATA%\\rk_kitchen"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    return Path(appdata) / 'rk_kitchen'


def get_settings_path() -> Path:
    """Lấy đường dẫn settings.json"""
    return get_appdata_dir() / 'settings.json'


@dataclass
class Settings:
    """Settings data class"""
    language: str = "vi"  # vi hoặc en
    tool_dir: str = ""  # Custom tool directory
    recent_projects: list = field(default_factory=list)  # List of recent project names
    max_recent: int = 10
    theme: str = "dark"
    log_level: str = "INFO"
    auto_scroll_log: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        # Chỉ lấy các keys hợp lệ
        valid_keys = {'language', 'tool_dir', 'recent_projects', 'max_recent', 
                      'theme', 'log_level', 'auto_scroll_log'}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class SettingsStore:
    """Singleton store cho settings"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings: Settings = Settings()
        self._path = get_settings_path()
        self.load()
    
    @property
    def settings(self) -> Settings:
        return self._settings
    
    def load(self) -> Settings:
        """Load settings từ file"""
        if self._path.exists():
            try:
                with open(self._path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._settings = Settings.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                # Log error và dùng defaults
                print(f"[WARNING] Không thể load settings: {e}")
                self._settings = Settings()
        return self._settings
    
    def save(self) -> bool:
        """Save settings ra file"""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"[ERROR] Không thể save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key"""
        return getattr(self._settings, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set setting value và auto-save"""
        if hasattr(self._settings, key):
            setattr(self._settings, key, value)
            return self.save()
        return False
    
    def add_recent_project(self, project_name: str):
        """Thêm project vào recent list"""
        recent = self._settings.recent_projects
        # Remove nếu đã có
        if project_name in recent:
            recent.remove(project_name)
        # Thêm vào đầu
        recent.insert(0, project_name)
        # Giới hạn số lượng
        self._settings.recent_projects = recent[:self._settings.max_recent]
        self.save()
    
    def remove_recent_project(self, project_name: str):
        """Xóa project khỏi recent list"""
        if project_name in self._settings.recent_projects:
            self._settings.recent_projects.remove(project_name)
            self.save()


# Convenience function
def get_settings_store() -> SettingsStore:
    return SettingsStore()
