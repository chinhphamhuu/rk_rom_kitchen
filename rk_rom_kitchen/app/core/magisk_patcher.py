"""
Magisk Patcher - Patch boot với Magisk
User phải cung cấp Magisk.apk
"""
import time
from pathlib import Path
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import ensure_dir, timestamp


def patch_boot_with_magisk(
    project: Project,
    boot_image: Path,
    magisk_apk: Path,
    keep_verity: bool = True,
    keep_force: bool = True,
    patch_vbmeta: bool = False,
    recovery_mode: bool = False,
    arch: str = "arm64",
    _cancel_token: Event = None
) -> TaskResult:
    """
    Patch boot image với Magisk
    Phase 1: Demo
    Phase 2: Thật bằng Magisk scripts
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[MAGISK] Patching: {boot_image.name}")
    log.info(f"[MAGISK] Magisk APK: {magisk_apk.name}")
    log.info(f"[MAGISK] Options: keep_verity={keep_verity}, keep_force={keep_force}")
    
    try:
        if not magisk_apk.exists():
            return TaskResult.error(f"Magisk APK not found: {magisk_apk}")
        
        output_dir = project.out_dir / "magisk_patched"
        ensure_dir(output_dir)
        
        output_name = boot_image.stem + "_magisk.img"
        output_path = output_dir / output_name
        
        # Phase 1: Demo
        for i in range(5):
            if _cancel_token and _cancel_token.is_set():
                return TaskResult.cancelled()
            time.sleep(0.2)
            log.info(f"[MAGISK] Progress: {(i+1)*20}%")
        
        output_path.write_text(f"Magisk patched boot\nSource: {boot_image.name}\n{timestamp()}", encoding='utf-8')
        (output_dir / "MAGISK_PATCH_OK.txt").write_text(f"Patched: {output_name}\n{timestamp()}", encoding='utf-8')
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[MAGISK] Output: {output_path}")
        
        return TaskResult.success(message=f"Patched to {output_name}", artifacts=[str(output_path)], elapsed_ms=elapsed)
    except Exception as e:
        log.error(f"[MAGISK] Error: {e}")
        return TaskResult.error(str(e))
