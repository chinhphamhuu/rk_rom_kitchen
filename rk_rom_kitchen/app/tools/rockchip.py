"""
Rockchip Tools - Wrappers cho các tools đặc thù Rockchip
Stub – Phase 2 sẽ implement logic thật

Điểm chèn tool thật:
- unpack_update_img(): Gọi img_unpack.exe để extract update.img
- pack_update_img(): Gọi rkImageMaker.exe để tạo update.img
- afp_unpack(): Gọi afptool.exe để unpack
- afp_pack(): Gọi afptool.exe để pack
"""
from pathlib import Path
from typing import Optional

from ..core.logbus import get_log_bus
from ..core.task_defs import TaskResult
from .runner import get_runner
from .registry import get_tool_registry


def unpack_update_img(update_img: Path, 
                      output_dir: Path) -> TaskResult:
    """
    Stub – Phase 2
    Unpack update.img sử dụng img_unpack.exe
    
    Args:
        update_img: Đường dẫn đến update.img
        output_dir: Thư mục output
        
    Returns:
        TaskResult
    """
    log = get_log_bus()
    log.info(f"[ROCKCHIP] unpack_update_img: {update_img}")
    log.warning("[ROCKCHIP] Stub – Phase 2 sẽ implement")
    
    # Phase 2: Uncomment và implement
    # registry = get_tool_registry()
    # tool_path = registry.get_tool_path("img_unpack.exe")
    # if not tool_path:
    #     return TaskResult.error("img_unpack.exe không tìm thấy")
    #
    # runner = get_runner()
    # result = runner.run_tool(tool_path, [str(update_img), str(output_dir)])
    # return TaskResult(ok=result.ok, message=result.stderr if not result.ok else "OK")
    
    return TaskResult.success("unpack_update_img: Stub – Coming in Phase 2")


def pack_update_img(source_dir: Path,
                    output_img: Path,
                    chip_type: str = "RK3568") -> TaskResult:
    """
    Stub – Phase 2
    Pack thư mục thành update.img sử dụng rkImageMaker.exe
    
    Args:
        source_dir: Thư mục chứa firmware đã unpack
        output_img: Đường dẫn output
        chip_type: Loại chip (RK3568, RK3399, etc.)
    """
    log = get_log_bus()
    log.info(f"[ROCKCHIP] pack_update_img: {source_dir} -> {output_img}")
    log.warning("[ROCKCHIP] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("pack_update_img: Stub – Coming in Phase 2")


def afp_unpack(firmware_img: Path,
               output_dir: Path) -> TaskResult:
    """
    Stub – Phase 2
    Unpack firmware sử dụng afptool.exe
    """
    log = get_log_bus()
    log.info(f"[ROCKCHIP] afp_unpack: {firmware_img}")
    log.warning("[ROCKCHIP] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("afp_unpack: Stub – Coming in Phase 2")


def afp_pack(source_dir: Path,
             output_img: Path) -> TaskResult:
    """
    Stub – Phase 2
    Pack thư mục thành firmware.img sử dụng afptool.exe
    """
    log = get_log_bus()
    log.info(f"[ROCKCHIP] afp_pack: {source_dir} -> {output_img}")
    log.warning("[ROCKCHIP] Stub – Phase 2 sẽ implement")
    
    return TaskResult.success("afp_pack: Stub – Coming in Phase 2")


def parse_parameter(parameter_file: Path) -> dict:
    """
    Parse Rockchip parameter file
    Returns dict với partition info
    
    Stub – Phase 2 sẽ implement parser thật
    """
    log = get_log_bus()
    log.info(f"[ROCKCHIP] parse_parameter: {parameter_file}")
    log.warning("[ROCKCHIP] Stub – Phase 2 sẽ implement")
    
    # Demo return
    return {
        "partitions": [
            {"name": "uboot", "start": "0x0", "size": "0x2000"},
            {"name": "boot", "start": "0x2000", "size": "0x8000"},
            {"name": "system", "start": "0xA000", "size": "0x100000"},
        ]
    }
