"""
Pipeline - Demo pipeline cho Import, Extract, Patch, Build
Tạo marker files để verify
"""
import time
from pathlib import Path
from typing import Optional
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import ensure_dir, safe_copy, timestamp
from .detect import detect_rom_type, RomType


def _check_cancel(cancel_token: Optional[Event], step: str) -> bool:
    """Check if cancelled, return True if should stop"""
    if cancel_token and cancel_token.is_set():
        get_log_bus().warning(f"[{step}] Đã hủy bởi user")
        return True
    return False


def pipeline_import(project: Project, 
                    source_file: Path,
                    _cancel_token: Event = None) -> TaskResult:
    """
    Step 1: Import ROM file vào project
    Copy source_file -> project/in/
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[IMPORT] Bắt đầu import: {source_file.name}")
    
    if _check_cancel(_cancel_token, "IMPORT"):
        return TaskResult.cancelled()
    
    try:
        if not source_file.exists():
            return TaskResult.error(f"File không tồn tại: {source_file}")
        
        # Detect ROM type
        rom_type = detect_rom_type(source_file)
        log.info(f"[IMPORT] Loại ROM: {rom_type.value}")
        
        if rom_type == RomType.UNKNOWN:
            log.warning("[IMPORT] Không xác định được loại ROM, tiếp tục import...")
        
        # Copy to in/
        dest = project.in_dir / source_file.name
        log.info(f"[IMPORT] Copying to: {dest}")
        
        # Simulate copy progress
        for i in range(0, 101, 20):
            if _check_cancel(_cancel_token, "IMPORT"):
                return TaskResult.cancelled()
            time.sleep(0.1)  # Demo delay
            log.info(f"[IMPORT] Progress: {i}%")
        
        safe_copy(source_file, dest, overwrite=True)
        
        # Update project config
        project.update_config(
            imported=True,
            input_file=str(dest),
            rom_type=rom_type.value
        )
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[IMPORT] Hoàn thành trong {elapsed}ms")
        
        return TaskResult.success(
            message="Import thành công",
            artifacts=[str(dest)],
            elapsed_ms=elapsed
        )
    
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[IMPORT] Lỗi: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def pipeline_extract(project: Project,
                     _cancel_token: Event = None) -> TaskResult:
    """
    Step 2: Extract ROM (Auto) - DEMO
    Tạo thư mục out/Source và out/Image + UNPACK_OK.txt marker
    """
    log = get_log_bus()
    start = time.time()
    
    log.info("[EXTRACT] Bắt đầu Extract ROM (Auto)")
    
    if _check_cancel(_cancel_token, "EXTRACT"):
        return TaskResult.cancelled()
    
    try:
        # Check imported file
        if not project.config.imported:
            return TaskResult.error("Chưa import ROM file")
        
        input_file = Path(project.config.input_file)
        if not input_file.exists():
            return TaskResult.error(f"ROM file không tồn tại: {input_file}")
        
        log.info(f"[EXTRACT] ROM file: {input_file.name}")
        log.info(f"[EXTRACT] ROM type: {project.config.rom_type}")
        
        # Demo: Create output structure
        ensure_dir(project.source_dir)
        ensure_dir(project.image_dir)
        
        # Simulate extraction progress
        steps = [
            "Đang phân tích ROM header...",
            "Đang extract firmware...",
            "Đang extract partitions...",
            "Đang phân tích Android images...",
            "Đang tạo cấu trúc output...",
        ]
        
        for i, step in enumerate(steps):
            if _check_cancel(_cancel_token, "EXTRACT"):
                return TaskResult.cancelled()
            log.info(f"[EXTRACT] {step}")
            time.sleep(0.2)  # Demo delay
        
        # Create demo files
        demo_files = [
            project.source_dir / "firmware.img.demo",
            project.source_dir / "boot.img.demo",
            project.source_dir / "system.img.demo",
            project.image_dir / "partition_table.txt.demo",
        ]
        
        for f in demo_files:
            f.write_text(f"Demo file - Phase 2 will have real data\nCreated: {timestamp()}\n", encoding='utf-8')
            log.info(f"[EXTRACT] Created: {f.name}")
        
        # Create marker file
        marker = project.out_dir / "UNPACK_OK.txt"
        marker.write_text(f"Extracted at: {timestamp()}\nROM: {input_file.name}\n", encoding='utf-8')
        log.success(f"[EXTRACT] Marker: {marker}")
        
        # Update config
        project.update_config(extracted=True)
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[EXTRACT] Hoàn thành trong {elapsed}ms")
        
        return TaskResult.success(
            message="Extract thành công (Demo)",
            artifacts=[str(f) for f in demo_files] + [str(marker)],
            elapsed_ms=elapsed
        )
    
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[EXTRACT] Lỗi: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def pipeline_patch(project: Project,
                   patches: dict = None,
                   _cancel_token: Event = None) -> TaskResult:
    """
    Step 3: Apply patches - DEMO
    Lưu patch toggles vào project.json + tạo PATCH_OK.txt
    """
    log = get_log_bus()
    start = time.time()
    
    patches = patches or {}
    log.info(f"[PATCH] Bắt đầu apply patches: {len(patches)} toggles")
    
    if _check_cancel(_cancel_token, "PATCH"):
        return TaskResult.cancelled()
    
    try:
        # Check extracted
        if not project.config.extracted:
            return TaskResult.error("Chưa extract ROM")
        
        # Log patches to apply
        for name, enabled in patches.items():
            status = "BẬT" if enabled else "TẮT"
            log.info(f"[PATCH] {name}: {status}")
        
        # Simulate patching
        patch_steps = [
            "Đang backup original files...",
            "Đang phân tích system.img...",
            "Đang apply patches...",
            "Đang verify changes...",
        ]
        
        for step in patch_steps:
            if _check_cancel(_cancel_token, "PATCH"):
                return TaskResult.cancelled()
            log.info(f"[PATCH] {step}")
            time.sleep(0.15)
        
        # Update project config with patches
        project.update_config(
            patched=True,
            patches=patches
        )
        
        # Create marker
        marker = project.out_dir / "PATCH_OK.txt"
        lines = [f"Patched at: {timestamp()}", "Patches applied:"]
        for name, enabled in patches.items():
            lines.append(f"  - {name}: {'enabled' if enabled else 'disabled'}")
        marker.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        log.success(f"[PATCH] Marker: {marker}")
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[PATCH] Hoàn thành trong {elapsed}ms")
        
        return TaskResult.success(
            message="Apply patches thành công (Demo)",
            artifacts=[str(marker)],
            elapsed_ms=elapsed
        )
    
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[PATCH] Lỗi: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def pipeline_build(project: Project,
                   _cancel_token: Event = None) -> TaskResult:
    """
    Step 4: Build output ROM - DEMO
    Tạo out/update_patched.img dummy + BUILD_OK.txt
    """
    log = get_log_bus()
    start = time.time()
    
    log.info("[BUILD] Bắt đầu build output ROM")
    
    if _check_cancel(_cancel_token, "BUILD"):
        return TaskResult.cancelled()
    
    try:
        # Check patched (or at least extracted)
        if not project.config.extracted:
            return TaskResult.error("Chưa extract ROM")
        
        # Simulate build process
        build_steps = [
            "Đang chuẩn bị build environment...",
            "Đang pack partitions...",
            "Đang tạo firmware image...",
            "Đang tính checksum...",
            "Đang tạo output file...",
        ]
        
        for i, step in enumerate(build_steps):
            if _check_cancel(_cancel_token, "BUILD"):
                return TaskResult.cancelled()
            progress = int((i + 1) / len(build_steps) * 100)
            log.info(f"[BUILD] [{progress}%] {step}")
            time.sleep(0.2)
        
        # Create dummy output
        output_file = project.out_dir / "update_patched.img"
        output_content = f"""Demo output file - Phase 2 sẽ có ROM thật
Project: {project.name}
ROM type: {project.config.rom_type}
Patches: {project.config.patches}
Built at: {timestamp()}
"""
        output_file.write_text(output_content, encoding='utf-8')
        log.success(f"[BUILD] Output: {output_file}")
        
        # Create marker
        marker = project.out_dir / "BUILD_OK.txt"
        marker.write_text(f"Built at: {timestamp()}\nOutput: {output_file.name}\n", encoding='utf-8')
        log.success(f"[BUILD] Marker: {marker}")
        
        # Update config
        project.update_config(built=True)
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BUILD] Hoàn thành trong {elapsed}ms")
        
        return TaskResult.success(
            message="Build thành công (Demo)",
            artifacts=[str(output_file), str(marker)],
            elapsed_ms=elapsed
        )
    
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[BUILD] Lỗi: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def run_full_pipeline(project: Project,
                      source_file: Path = None,
                      patches: dict = None,
                      _cancel_token: Event = None) -> TaskResult:
    """
    Chạy toàn bộ pipeline
    """
    log = get_log_bus()
    log.info("=" * 50)
    log.info("BẮT ĐẦU PIPELINE DEMO")
    log.info("=" * 50)
    
    start = time.time()
    
    # Step 1: Import (if source_file provided)
    if source_file:
        result = pipeline_import(project, source_file, _cancel_token)
        if not result.ok:
            return result
    
    # Step 2: Extract
    result = pipeline_extract(project, _cancel_token)
    if not result.ok:
        return result
    
    # Step 3: Patch
    result = pipeline_patch(project, patches or {}, _cancel_token)
    if not result.ok:
        return result
    
    # Step 4: Build
    result = pipeline_build(project, _cancel_token)
    
    elapsed = int((time.time() - start) * 1000)
    
    log.info("=" * 50)
    if result.ok:
        log.success(f"PIPELINE HOÀN THÀNH TRONG {elapsed}ms")
    else:
        log.error(f"PIPELINE THẤT BẠI SAU {elapsed}ms")
    log.info("=" * 50)
    
    return TaskResult(
        ok=result.ok,
        code=result.code,
        message=f"Pipeline {'thành công' if result.ok else 'thất bại'}",
        artifacts=result.artifacts,
        elapsed_ms=elapsed
    )
