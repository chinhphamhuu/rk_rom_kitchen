"""
Boot Manager - Unpack/Repack boot images
"""
import time
from pathlib import Path
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import ensure_dir, timestamp


def unpack_boot_image(project: Project, boot_image: Path, _cancel_token: Event = None) -> TaskResult:
    """Unpack boot image (Phase 1: demo)"""
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BOOT] Unpacking: {boot_image.name}")
    
    try:
        output_dir = project.out_dir / "boot_unpacked" / boot_image.stem
        ensure_dir(output_dir)
        
        # Demo: create markers
        (output_dir / "kernel").write_bytes(b'\x00' * 1024)
        (output_dir / "ramdisk").write_bytes(b'\x00' * 1024)
        (output_dir / "UNPACK_BOOT_OK.txt").write_text(f"Demo for {boot_image.name}\n{timestamp()}", encoding='utf-8')
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BOOT] Unpacked to: {output_dir}")
        
        return TaskResult.success(message=f"Unpacked {boot_image.name}", artifacts=[str(output_dir)], elapsed_ms=elapsed)
    except Exception as e:
        log.error(f"[BOOT] Error: {e}")
        return TaskResult.error(str(e))


def repack_boot_image(project: Project, unpacked_dir: Path, output_name: str = None, _cancel_token: Event = None) -> TaskResult:
    """Repack boot image (Phase 1: demo)"""
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BOOT] Repacking: {unpacked_dir.name}")
    
    try:
        if not output_name:
            output_name = unpacked_dir.name + "_repacked.img"
        output_path = project.image_dir / output_name
        ensure_dir(project.image_dir)
        
        output_path.write_text(f"Demo repacked\n{timestamp()}", encoding='utf-8')
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BOOT] Repacked: {output_path}")
        
        return TaskResult.success(message=f"Repacked to {output_name}", artifacts=[str(output_path)], elapsed_ms=elapsed)
    except Exception as e:
        log.error(f"[BOOT] Error: {e}")
        return TaskResult.error(str(e))


def find_boot_images(project: Project) -> list:
    """Tìm boot images trong project"""
    names = ["boot.img", "boot_a.img", "vendor_boot.img", "vendor_boot_a.img", "init_boot.img", "init_boot_a.img"]
    found = []
    for d in [project.in_dir, project.source_dir, project.image_dir]:
        if d.exists():
            for n in names:
                if (d / n).exists():
                    found.append(d / n)
    return list(set(found))
