"""
App Context - Singleton chứa tất cả shared resources
"""
from pathlib import Path
from typing import Optional

from .settings_store import SettingsStore, get_settings_store
from .project_store import ProjectStore, Project, get_project_store
from .workspace import Workspace, get_workspace
from .state_machine import StateMachine, get_state_machine
from .task_manager import TaskManager, get_task_manager
from .logbus import LogBus, get_log_bus


class AppContext:
    """
    Central app context chứa tất cả shared resources
    Singleton pattern
    """
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
        
        # Initialize all singletons
        self._settings = get_settings_store()
        self._project_store = get_project_store()
        self._workspace = get_workspace()
        self._state = get_state_machine()
        self._task_manager = get_task_manager()
        self._log = get_log_bus()
        
        # Current project reference
        self._current_project: Optional[Project] = None
    
    @property
    def settings(self) -> SettingsStore:
        return self._settings
    
    @property
    def projects(self) -> ProjectStore:
        return self._project_store
    
    @property
    def workspace(self) -> Workspace:
        return self._workspace
    
    @property
    def state(self) -> StateMachine:
        return self._state
    
    @property
    def tasks(self) -> TaskManager:
        return self._task_manager
    
    @property
    def log(self) -> LogBus:
        return self._log
    
    @property
    def current_project(self) -> Optional[Project]:
        return self._project_store.current
    
    def set_current_project(self, name: str) -> Optional[Project]:
        """Set current project by name"""
        project = self._project_store.set_current(name)
        if project:
            self._settings.add_recent_project(name)
            self._log.info(f"Đã chọn project: {name}")
        return project
    
    def get_language(self) -> str:
        """Lấy ngôn ngữ hiện tại (vi/en)"""
        return self._settings.get('language', 'vi')
    
    def set_language(self, lang: str):
        """Set ngôn ngữ"""
        self._settings.set('language', lang)
    
    def is_busy(self) -> bool:
        """Check xem có đang chạy task không"""
        return self._state.is_running


def get_app_context() -> AppContext:
    """Lấy singleton AppContext"""
    return AppContext()
