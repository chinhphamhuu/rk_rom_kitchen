"""
Stub – Phase 2
vbmeta disable script - Disable dm-verity và AVB

Điểm chèn:
- Thay thế bằng actual vbmeta patching
"""
from pathlib import Path

from app.core.logbus import get_log_bus
from app.core.task_defs import TaskResult


def disable_vbmeta(vbmeta_path: Path) -> TaskResult:
    """
    Stub – Phase 2
    Disable verification trong vbmeta.img
    
    Args:
        vbmeta_path: Đường dẫn đến vbmeta.img
        
    Returns:
        TaskResult
    """
    log = get_log_bus()
    log.info(f"[VBMETA] disable_vbmeta: {vbmeta_path}")
    log.warning("[VBMETA] Stub – Phase 2 sẽ implement")
    
    # Phase 2: Implement
    # Option 1: Patch flags byte trực tiếp
    # Option 2: Dùng avbtool để tạo lại vbmeta với --flags 2
    
    return TaskResult.success("disable_vbmeta: Stub – Coming in Phase 2")


def patch_fstab_verity(fstab_path: Path) -> TaskResult:
    """
    Stub – Phase 2
    Xóa verify flags từ fstab
    """
    log = get_log_bus()
    log.info(f"[VBMETA] patch_fstab_verity: {fstab_path}")
    log.warning("[VBMETA] Stub – Phase 2 sẽ implement")
    
    # Phase 2: Implement
    # - Parse fstab
    # - Remove 'verify' and 'avb' flags
    # - Write back
    
    return TaskResult.success("patch_fstab_verity: Stub – Coming in Phase 2")
