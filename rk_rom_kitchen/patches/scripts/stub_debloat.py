"""
Stub – Phase 2
Debloat script - Gỡ bỏ bloatware apps

Điểm chèn:
- Thay thế logic demo bằng actual removal từ system/app và system/priv-app
"""
from pathlib import Path
from typing import List

from app.core.logbus import get_log_bus
from app.core.task_defs import TaskResult


def debloat(source_dir: Path,
            packages: List[str]) -> TaskResult:
    """
    Stub – Phase 2
    Gỡ bỏ các packages khỏi ROM
    
    Args:
        source_dir: Thư mục chứa extracted ROM
        packages: List package names để gỡ
        
    Returns:
        TaskResult
    """
    log = get_log_bus()
    log.info(f"[DEBLOAT] debloat called with {len(packages)} packages")
    log.warning("[DEBLOAT] Stub – Phase 2 sẽ implement")
    
    for pkg in packages:
        log.info(f"[DEBLOAT] Would remove: {pkg}")
    
    # Phase 2: Implement
    # - Find APK in system/app/ and system/priv-app/
    # - Remove APK folder
    # - Update packages.xml if needed
    
    return TaskResult.success("debloat: Stub – Coming in Phase 2")


def list_installed_apps(source_dir: Path) -> List[dict]:
    """
    Stub – Phase 2
    Liệt kê các apps trong ROM
    """
    log = get_log_bus()
    log.info("[DEBLOAT] list_installed_apps called")
    log.warning("[DEBLOAT] Stub – Phase 2 sẽ implement")
    
    # Demo return
    return [
        {"package": "com.android.browser", "name": "Browser", "path": "system/app/Browser"},
        {"package": "com.android.email", "name": "Email", "path": "system/app/Email"},
    ]
