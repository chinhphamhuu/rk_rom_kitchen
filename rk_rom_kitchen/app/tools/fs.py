"""
Filesystem Utilities - Xử lý filesystem images
Stub – Phase 2 sẽ implement logic thật
"""
from pathlib import Path
from typing import List, Optional

from ..core.logbus import get_log_bus
from ..core.task_defs import TaskResult


def mount_ext4(image_path: Path,
               mount_point: Path) -> TaskResult:
    """
    Stub – Phase 2
    Mount ext4 image (cần quyền admin trên Windows)
    
    Note: Trên Windows, có thể cần dùng WSL hoặc 7-zip để extract
    """
    log = get_log_bus()
    log.info(f"[FS] mount_ext4: {image_path} -> {mount_point}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    log.warning("[FS] Trên Windows có thể cần quyền Admin hoặc dùng WSL")
    
    return TaskResult.success("mount_ext4: Stub – Coming in Phase 2")


def unmount(mount_point: Path) -> TaskResult:
    """
    Stub – Phase 2
    Unmount một mount point
    """
    log = get_log_bus()
    log.info(f"[FS] unmount: {mount_point}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("unmount: Stub – Coming in Phase 2")


def extract_ext4(image_path: Path,
                 output_dir: Path) -> TaskResult:
    """
    Stub – Phase 2
    Extract ext4 image mà không cần mount
    Sử dụng ext4_extractor hoặc 7-zip
    """
    log = get_log_bus()
    log.info(f"[FS] extract_ext4: {image_path} -> {output_dir}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("extract_ext4: Stub – Coming in Phase 2")


def make_ext4(source_dir: Path,
              output_img: Path,
              partition_size: int = 0,
              label: str = "system") -> TaskResult:
    """
    Stub – Phase 2
    Tạo ext4 image từ thư mục
    
    Args:
        source_dir: Thư mục nguồn
        output_img: Output image path
        partition_size: Partition size (0 = auto)
        label: Volume label
    """
    log = get_log_bus()
    log.info(f"[FS] make_ext4: {source_dir} -> {output_img}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("make_ext4: Stub – Coming in Phase 2")


def get_ext4_info(image_path: Path) -> dict:
    """
    Stub – Phase 2
    Lấy thông tin của ext4 image
    """
    log = get_log_bus()
    log.info(f"[FS] get_ext4_info: {image_path}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    
    # Demo
    return {
        "label": "system",
        "size": 0,
        "used": 0,
        "free": 0,
        "inode_count": 0,
    }


def list_files_in_image(image_path: Path,
                        path_filter: str = "/") -> List[str]:
    """
    Stub – Phase 2
    Liệt kê files trong một image mà không cần extract
    """
    log = get_log_bus()
    log.info(f"[FS] list_files_in_image: {image_path}")
    log.warning("[FS] Stub – Phase 2 sẽ implement")
    
    # Demo
    return [
        "/system/app/",
        "/system/priv-app/",
        "/system/framework/",
        "/system/lib/",
        "/system/lib64/",
    ]
