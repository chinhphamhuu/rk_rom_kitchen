"""
Debloater - Scan và xóa APK bloatware
Hỗ trợ delete to Recycle Bin
"""
import os
import time
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import human_size

# Try import send2trash for Recycle Bin support
try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False


@dataclass
class ApkInfo:
    """Thông tin một APK file"""
    filename: str
    path: Path
    size: int
    partition: str
    package_name: str = "Unknown"  # Phase 2: parse từ APK
    internal_name: str = "Unknown"  # Phase 2: parse từ APK
    
    @property
    def size_str(self) -> str:
        return human_size(self.size)
    
    @property
    def relative_path(self) -> str:
        return str(self.path)


def scan_apks(project: Project, _cancel_token: Event = None) -> List[ApkInfo]:
    """
    Scan tất cả APK files trong extracted tree
    
    Tìm trong:
    - system_a/app, system_a/priv-app
    - product_a/app, product_a/priv-app
    - vendor_a/app, vendor_a/priv-app
    - odm_a/app
    """
    log = get_log_bus()
    log.info("[DEBLOAT] Scanning APK files...")
    
    apks = []
    
    # Define search paths
    partitions = ["system_a", "product_a", "vendor_a", "odm_a", "system_ext_a"]
    app_dirs = ["app", "priv-app"]
    
    for partition in partitions:
        if _cancel_token and _cancel_token.is_set():
            break
        
        partition_dir = project.source_dir / partition
        if not partition_dir.exists():
            continue
        
        for app_dir in app_dirs:
            search_dir = partition_dir / app_dir
            if not search_dir.exists():
                continue
            
            # Scan for APKs
            for apk_path in search_dir.rglob("*.apk"):
                if _cancel_token and _cancel_token.is_set():
                    break
                
                try:
                    stat = apk_path.stat()
                    rel_path = apk_path.relative_to(project.source_dir)
                    
                    apk_info = ApkInfo(
                        filename=apk_path.name,
                        path=apk_path,
                        size=stat.st_size,
                        partition=f"{partition}/{app_dir}",
                    )
                    apks.append(apk_info)
                    
                except Exception as e:
                    log.warning(f"[DEBLOAT] Error scanning {apk_path}: {e}")
    
    log.info(f"[DEBLOAT] Found {len(apks)} APK files")
    return apks


def delete_to_recycle_bin(path: Path) -> bool:
    """
    Move file to Recycle Bin
    Returns True if successful
    """
    if HAS_SEND2TRASH:
        try:
            send2trash(str(path))
            return True
        except Exception:
            pass
    return False


def delete_file(path: Path, use_recycle_bin: bool = True) -> bool:
    """
    Delete file - try Recycle Bin first, then permanent delete
    """
    if use_recycle_bin:
        if delete_to_recycle_bin(path):
            return True
    
    # Fallback to permanent delete
    try:
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
        else:
            path.unlink()
        return True
    except Exception:
        return False


def delete_apks(
    project: Project,
    apks: List[ApkInfo],
    use_recycle_bin: bool = True,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Delete selected APK files
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[DEBLOAT] Deleting {len(apks)} APK files")
    
    deleted = []
    failed = []
    
    for apk in apks:
        if _cancel_token and _cancel_token.is_set():
            log.warning("[DEBLOAT] Cancelled")
            break
        
        try:
            # Delete APK file
            if delete_file(apk.path, use_recycle_bin):
                deleted.append(apk.filename)
                log.info(f"[DEBLOAT] Deleted: {apk.filename}")
                
                # Also try to delete parent folder if empty
                parent = apk.path.parent
                if parent.exists() and parent != project.source_dir:
                    try:
                        if not any(parent.iterdir()):
                            parent.rmdir()
                            log.info(f"[DEBLOAT] Removed empty folder: {parent.name}")
                    except Exception:
                        pass
            else:
                failed.append(apk.filename)
                log.error(f"[DEBLOAT] Failed: {apk.filename}")
                
        except Exception as e:
            failed.append(apk.filename)
            log.error(f"[DEBLOAT] Error deleting {apk.filename}: {e}")
    
    # Save to project config
    config_update = {
        "debloated_apps": project.config.debloated_apps + deleted
        if hasattr(project.config, 'debloated_apps') and project.config.debloated_apps
        else deleted
    }
    project.update_config(**config_update)
    
    elapsed = int((time.time() - start) * 1000)
    
    if failed:
        log.warning(f"[DEBLOAT] Deleted {len(deleted)}, Failed {len(failed)}")
        return TaskResult.error(
            f"Deleted {len(deleted)}, Failed {len(failed)}",
            elapsed_ms=elapsed
        )
    
    log.success(f"[DEBLOAT] Deleted {len(deleted)} APKs in {elapsed}ms")
    return TaskResult.success(
        message=f"Deleted {len(deleted)} APKs",
        elapsed_ms=elapsed
    )


def get_apk_metadata(apk_path: Path) -> dict:
    """
    Get APK metadata (Phase 2: sử dụng aapt2 hoặc androguard)
    Phase 1: trả về placeholder
    """
    # Phase 2 implementation:
    # try:
    #     from androguard.core.bytecodes.apk import APK
    #     apk = APK(str(apk_path))
    #     return {
    #         "package": apk.get_package(),
    #         "name": apk.get_app_name(),
    #         "version": apk.get_androidversion_name(),
    #         # ...
    #     }
    # except Exception:
    #     pass
    
    return {
        "package": "Unknown",
        "name": "Unknown",
        "version": "Unknown",
    }
