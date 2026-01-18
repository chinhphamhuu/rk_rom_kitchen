"""
AVB Tools - Android Verified Boot handling
Stub – Phase 2 sẽ implement logic thật

Điểm chèn tool thật:
- disable_verification(): Patch vbmeta để disable dm-verity và AVB
- verify_image(): Verify AVB signature của boot/vbmeta image
"""
from pathlib import Path
from typing import Optional

from ..core.logbus import get_log_bus
from ..core.task_defs import TaskResult
from .runner import get_runner
from .registry import get_tool_registry


def disable_verification(vbmeta_img: Path,
                        output_img: Optional[Path] = None) -> TaskResult:
    """
    Stub – Phase 2
    Disable dm-verity và AVB verification trong vbmeta.img
    
    Args:
        vbmeta_img: Đường dẫn đến vbmeta.img
        output_img: Output path (nếu None, patch in-place)
    """
    log = get_log_bus()
    log.info(f"[AVB] disable_verification: {vbmeta_img}")
    log.warning("[AVB] Stub – Phase 2 sẽ implement")
    
    # Phase 2: Implement
    # Có 2 cách:
    # 1. Dùng avbtool make_vbmeta_image với --flag 2
    # 2. Patch byte trực tiếp trong vbmeta.img header
    
    return TaskResult.success("disable_verification: Stub – Coming in Phase 2")


def patch_vbmeta_flags(vbmeta_img: Path,
                       flags: int = 2) -> TaskResult:
    """
    Stub – Phase 2
    Patch vbmeta flags trực tiếp
    
    Flags:
        0 = Normal (verification enabled)
        1 = Hashtree disabled
        2 = Verification disabled
        3 = Both disabled
    """
    log = get_log_bus()
    log.info(f"[AVB] patch_vbmeta_flags: {vbmeta_img} -> flags={flags}")
    log.warning("[AVB] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("patch_vbmeta_flags: Stub – Coming in Phase 2")


def verify_image(image_path: Path) -> TaskResult:
    """
    Stub – Phase 2
    Verify AVB signature của một image
    
    Args:
        image_path: Image để verify (boot.img, vbmeta.img, etc.)
    """
    log = get_log_bus()
    log.info(f"[AVB] verify_image: {image_path}")
    log.warning("[AVB] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success(
        "verify_image: Stub – Coming in Phase 2",
        data={"verified": True, "info": "Demo verification result"}
    )


def extract_avb_info(image_path: Path) -> dict:
    """
    Stub – Phase 2
    Extract AVB metadata từ image
    
    Returns:
        Dict với AVB info (algorithm, hash, etc.)
    """
    log = get_log_bus()
    log.info(f"[AVB] extract_avb_info: {image_path}")
    log.warning("[AVB] Stub – Phase 2 sẽ implement")
    
    # Demo return
    return {
        "has_avb": True,
        "algorithm": "SHA256_RSA4096",
        "flags": 0,
        "rollback_index": 0,
    }


def make_vbmeta(output_img: Path,
                algorithm: str = "SHA256_RSA4096",
                flags: int = 2) -> TaskResult:
    """
    Stub – Phase 2
    Tạo vbmeta.img mới với flags disabled
    """
    log = get_log_bus()
    log.info(f"[AVB] make_vbmeta: {output_img}")
    log.warning("[AVB] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("make_vbmeta: Stub – Coming in Phase 2")
