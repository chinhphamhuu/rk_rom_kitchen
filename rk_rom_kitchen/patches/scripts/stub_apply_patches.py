"""
Stub – Phase 2
Apply patches script

Điểm chèn:
- Thay thế logic demo bằng actual patching của build.prop, fstab, etc.
"""
from pathlib import Path
from typing import Dict

from app.core.logbus import get_log_bus
from app.core.task_defs import TaskResult


def apply_patches(source_dir: Path, 
                  patches: Dict[str, bool]) -> TaskResult:
    """
    Stub – Phase 2
    Apply các patches đã chọn vào source
    
    Args:
        source_dir: Thư mục chứa extracted ROM
        patches: Dict mapping patch_id -> enabled
        
    Returns:
        TaskResult
    """
    log = get_log_bus()
    log.info("[PATCHES] apply_patches called")
    log.warning("[PATCHES] Stub – Phase 2 sẽ implement")
    
    for patch_id, enabled in patches.items():
        status = "APPLYING" if enabled else "SKIPPING"
        log.info(f"[PATCHES] {status}: {patch_id}")
    
    # Phase 2: Implement actual patching
    # - build.prop modifications
    # - fstab modifications
    # - init.rc modifications
    # - etc.
    
    return TaskResult.success("apply_patches: Stub – Coming in Phase 2")


def apply_single_patch(source_dir: Path,
                       patch_id: str) -> TaskResult:
    """
    Stub – Phase 2
    Apply một patch cụ thể
    """
    log = get_log_bus()
    log.info(f"[PATCHES] apply_single_patch: {patch_id}")
    log.warning("[PATCHES] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success(f"apply_single_patch({patch_id}): Stub")
