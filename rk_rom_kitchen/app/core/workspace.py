"""
Workspace Manager
Quản lý workspace root tại %USERPROFILE%\Documents\RK_Kitchen\Projects
"""
import os
from pathlib import Path
from typing import List, Optional

from .utils import ensure_dir


def get_workspace_root() -> Path:
    """
    Lấy đường dẫn workspace root
    Default: %USERPROFILE%\Documents\RK_Kitchen\Projects
    """
    user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    return Path(user_profile) / 'Documents' / 'RK_Kitchen' / 'Projects'


class Workspace:
    """Quản lý workspace và projects"""
    
    def __init__(self, root: Optional[Path] = None):
        """
        Args:
            root: Custom workspace root, nếu None sẽ dùng default
        """
        self._root = root or get_workspace_root()
        self._ensure_workspace()
    
    def _ensure_workspace(self):
        """Đảm bảo workspace folder tồn tại"""
        ensure_dir(self._root)
    
    @property
    def root(self) -> Path:
        """Đường dẫn workspace root"""
        return self._root
    
    def list_projects(self) -> List[str]:
        """Liệt kê tất cả projects trong workspace"""
        if not self._root.exists():
            return []
        
        projects = []
        for item in self._root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it's a valid project (has config folder)
                if (item / 'config').exists() or (item / 'in').exists():
                    projects.append(item.name)
        
        return sorted(projects)
    
    def project_exists(self, name: str) -> bool:
        """Kiểm tra project có tồn tại không"""
        return (self._root / name).is_dir()
    
    def get_project_path(self, name: str) -> Path:
        """Lấy đường dẫn project"""
        return self._root / name
    
    def create_project_structure(self, name: str) -> Path:
        """
        Tạo cấu trúc thư mục chuẩn cho project mới
        
        Structure:
            <project>/
                in/           - Input ROM files
                out/
                    Source/   - Extracted source
                    Image/    - Extracted images
                temp/         - Temporary files
                logs/         - Log files
                config/       - Project configuration
        
        Returns:
            Path đến project root
        """
        project_path = self._root / name
        
        # Tạo các thư mục con
        dirs = [
            project_path / 'in',
            project_path / 'out' / 'Source',
            project_path / 'out' / 'Image',
            project_path / 'temp',
            project_path / 'logs',
            project_path / 'config',
        ]
        
        for d in dirs:
            ensure_dir(d)
        
        return project_path
    
    def delete_project(self, name: str) -> bool:
        """
        Xóa project
        
        Returns:
            True nếu xóa thành công
        """
        import shutil
        
        project_path = self._root / name
        if not project_path.exists():
            return False
        
        try:
            shutil.rmtree(project_path)
            return True
        except OSError:
            return False
    
    def get_project_size(self, name: str) -> int:
        """Tính tổng size của project (bytes)"""
        project_path = self._root / name
        if not project_path.exists():
            return 0
        
        total = 0
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total


# Singleton instance
_workspace: Optional[Workspace] = None


def get_workspace(root: Optional[Path] = None) -> Workspace:
    """Lấy singleton Workspace instance"""
    global _workspace
    if _workspace is None or (root is not None and _workspace.root != root):
        _workspace = Workspace(root)
    return _workspace
