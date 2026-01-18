"""
Android Images Tools - Wrappers cho các tools xử lý Android images
Stub – Phase 2 sẽ implement logic thật

Điểm chèn tool thật:
- unpack_super(): Gọi lpunpack.exe để extract super.img
- pack_super(): Gọi lpmake.exe để tạo super.img
- sparse_to_raw(): Gọi simg2img.exe
- raw_to_sparse(): Gọi img2simg.exe
"""
from pathlib import Path
from typing import List, Optional

from ..core.logbus import get_log_bus
from ..core.task_defs import TaskResult
from .runner import get_runner
from .registry import get_tool_registry


def unpack_super(super_img: Path,
                 output_dir: Path,
                 slot: str = "a") -> TaskResult:
    """
    Stub – Phase 2
    Unpack super.img sử dụng lpunpack.exe
    
    Args:
        super_img: Đường dẫn đến super.img
        output_dir: Thư mục output
        slot: Slot (a hoặc b) cho A/B devices
    """
    log = get_log_bus()
    log.info(f"[ANDROID] unpack_super: {super_img}")
    log.info(f"[ANDROID] Slot: {slot}")
    log.warning("[ANDROID] Stub – Phase 2 sẽ implement")
    
    # Phase 2: Implement
    # tool_path = get_tool_registry().get_tool_path("lpunpack.exe")
    # if not tool_path:
    #     return TaskResult.error("lpunpack.exe không tìm thấy")
    #
    # runner = get_runner()
    # args = ["-S", slot, str(super_img), str(output_dir)]
    # result = runner.run_tool(tool_path, args)
    
    return TaskResult.success("unpack_super: Stub – Coming in Phase 2")


def pack_super(partitions: List[dict],
               output_img: Path,
               metadata_size: int = 65536,
               block_size: int = 4096) -> TaskResult:
    """
    Stub – Phase 2
    Pack partitions thành super.img sử dụng lpmake.exe
    
    Args:
        partitions: List of {"name": str, "image": Path, "size": int}
        output_img: Đường dẫn output
        metadata_size: Metadata size
        block_size: Block size
    """
    log = get_log_bus()
    log.info(f"[ANDROID] pack_super: -> {output_img}")
    log.info(f"[ANDROID] Partitions: {[p.get('name') for p in partitions]}")
    log.warning("[ANDROID] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("pack_super: Stub – Coming in Phase 2")


def sparse_to_raw(sparse_img: Path,
                  raw_img: Path) -> TaskResult:
    """
    Stub – Phase 2
    Chuyển đổi sparse image sang raw image sử dụng simg2img.exe
    
    Args:
        sparse_img: Input sparse image
        raw_img: Output raw image
    """
    log = get_log_bus()
    log.info(f"[ANDROID] sparse_to_raw: {sparse_img.name} -> {raw_img.name}")
    log.warning("[ANDROID] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("sparse_to_raw: Stub – Coming in Phase 2")


def raw_to_sparse(raw_img: Path,
                  sparse_img: Path,
                  block_size: int = 4096) -> TaskResult:
    """
    Stub – Phase 2
    Chuyển đổi raw image sang sparse image sử dụng img2simg.exe
    
    Args:
        raw_img: Input raw image
        sparse_img: Output sparse image
        block_size: Block size
    """
    log = get_log_bus()
    log.info(f"[ANDROID] raw_to_sparse: {raw_img.name} -> {sparse_img.name}")
    log.warning("[ANDROID] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("raw_to_sparse: Stub – Coming in Phase 2")


def is_sparse_image(img_path: Path) -> bool:
    """
    Kiểm tra xem image có phải sparse format không
    Dựa trên magic number 0x3aff26ed
    """
    log = get_log_bus()
    
    if not img_path.exists():
        return False
    
    try:
        with open(img_path, 'rb') as f:
            magic = f.read(4)
        
        # Sparse image magic: 0xed26ff3a (little endian)
        is_sparse = magic == b'\xed\x26\xff\x3a'
        log.debug(f"[ANDROID] {img_path.name} is{''}sparse: {is_sparse}")
        return is_sparse
        
    except Exception as e:
        log.error(f"[ANDROID] Lỗi đọc file: {e}")
        return False
