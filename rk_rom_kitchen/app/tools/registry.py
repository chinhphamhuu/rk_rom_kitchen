"""
Tool Registry - Quản lý và auto-detect các tools cần thiết
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..core.logbus import get_log_bus
from ..core.settings_store import get_settings_store
from .runner import get_runner


# Danh sách tools cần thiết cho Rockchip ROM Kitchen
REQUIRED_TOOLS = [
    "img_unpack.exe",      # Rockchip image unpacker
    "afptool.exe",         # Rockchip AFPTool
    "rkImageMaker.exe",    # Rockchip image maker
    "lpunpack.exe",        # Super partition unpacker
    "lpmake.exe",          # Super partition maker
    "simg2img.exe",        # Sparse image to raw
    "img2simg.exe",        # Raw to sparse image
    "avbtool.exe",         # Android Verified Boot tool
]


@dataclass
class ToolInfo:
    """Thông tin về một tool"""
    name: str
    path: Optional[Path] = None
    available: bool = False
    version: str = ""
    error: str = ""


class ToolRegistry:
    """
    Registry để quản lý tools
    Auto-detect theo order:
    1. settings.tool_dir
    2. third_party/tools/win64
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
        
        self._tools: Dict[str, ToolInfo] = {}
        self._log = get_log_bus()
        self._settings = get_settings_store()
        self._runner = get_runner()
        
        # Initialize tool info
        for tool_name in REQUIRED_TOOLS:
            self._tools[tool_name] = ToolInfo(name=tool_name)
    
    def _get_search_paths(self) -> List[Path]:
        """Lấy danh sách paths để search tools"""
        paths = []
        
        # 1. Custom tool_dir từ settings
        custom_dir = self._settings.get('tool_dir', '')
        if custom_dir and Path(custom_dir).is_dir():
            paths.append(Path(custom_dir))
        
        # 2. third_party/tools/win64 (relative to app)
        app_root = Path(__file__).parent.parent.parent  # rk_rom_kitchen/
        third_party = app_root / 'third_party' / 'tools' / 'win64'
        if third_party.is_dir():
            paths.append(third_party)
        
        # 3. Current directory
        paths.append(Path.cwd())
        
        # 4. PATH environment
        env_path = os.environ.get('PATH', '')
        for p in env_path.split(os.pathsep):
            if p and Path(p).is_dir():
                paths.append(Path(p))
        
        return paths
    
    def detect_all(self) -> Dict[str, ToolInfo]:
        """
        Detect tất cả tools
        
        Returns:
            Dict mapping tool_name -> ToolInfo
        """
        self._log.info("[REGISTRY] Bắt đầu detect tools...")
        
        search_paths = self._get_search_paths()
        self._log.debug(f"[REGISTRY] Search paths: {[str(p) for p in search_paths]}")
        
        for tool_name in REQUIRED_TOOLS:
            self._tools[tool_name] = self._detect_tool(tool_name, search_paths)
        
        # Summary
        available = sum(1 for t in self._tools.values() if t.available)
        total = len(self._tools)
        self._log.info(f"[REGISTRY] Tìm thấy {available}/{total} tools")
        
        return self._tools.copy()
    
    def _detect_tool(self, tool_name: str, search_paths: List[Path]) -> ToolInfo:
        """Detect một tool cụ thể"""
        for search_path in search_paths:
            tool_path = search_path / tool_name
            if tool_path.exists() and tool_path.is_file():
                # Found! Check if it works
                available, version = self._runner.check_tool(tool_path)
                if available:
                    self._log.debug(f"[REGISTRY] Found {tool_name}: {tool_path}")
                    return ToolInfo(
                        name=tool_name,
                        path=tool_path,
                        available=True,
                        version=version
                    )
        
        # Not found
        return ToolInfo(
            name=tool_name,
            available=False,
            error="Không tìm thấy"
        )
    
    def get_tool(self, name: str) -> Optional[ToolInfo]:
        """Lấy tool info by name"""
        return self._tools.get(name)
    
    def get_tool_path(self, name: str) -> Optional[Path]:
        """Lấy path của tool, None nếu không available"""
        tool = self._tools.get(name)
        if tool and tool.available:
            return tool.path
        return None
    
    def is_available(self, name: str) -> bool:
        """Check tool có available không"""
        tool = self._tools.get(name)
        return tool.available if tool else False
    
    def get_all_tools(self) -> List[ToolInfo]:
        """Lấy list tất cả tools"""
        return list(self._tools.values())
    
    def get_missing_tools(self) -> List[str]:
        """Lấy list tools đang thiếu"""
        return [t.name for t in self._tools.values() if not t.available]
    
    def set_custom_tool_dir(self, path: Path):
        """Set custom tool directory và re-detect"""
        if path.is_dir():
            self._settings.set('tool_dir', str(path))
            self.detect_all()


def get_tool_registry() -> ToolRegistry:
    """Lấy singleton ToolRegistry"""
    return ToolRegistry()
