"""
AVB Manager - Quản lý Android Verified Boot
- Tạo vbmeta_disabled.img
- Patch fstab (dm-verity, AVB, forceencrypt, fileencryption)
"""
import os
import re
import time
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import ensure_dir, timestamp


# Fstab patterns to patch
FSTAB_PATTERNS = {
    # dm-verity related
    "verify": (r'\bverify\b', ''),
    "avb": (r'\bavb[=,]?[^,\s]*', ''),
    "avb_keys": (r'\bavb_keys=[^,\s]*', ''),
    
    # Verity related
    "verity": (r'\bverity\b', ''),
    "support_scfs": (r'\bsupport_scfs\b', ''),
    
    # Force encryption related (B2)
    "forceencrypt": (r'\bforceencrypt=[^,\s]*', 'encryptable=footer'),
    "forcefdeorfbe": (r'\bforcefdeorfbe=[^,\s]*', 'encryptable=footer'),
    "fileencryption": (r'\bfileencryption=[^,\s]*', ''),
    "metadata_encryption": (r'\bmetadata_encryption=[^,\s]*', ''),
}


def find_vbmeta_files(project: Project) -> List[Path]:
    """
    Tìm tất cả vbmeta files trong project
    Ưu tiên: in/ -> out/Source -> out/Image
    """
    vbmeta_names = [
        "vbmeta.img",
        "vbmeta_system.img", 
        "vbmeta_vendor.img",
    ]
    
    found = []
    search_dirs = [
        project.in_dir,
        project.source_dir,
        project.image_dir,
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for name in vbmeta_names:
            path = search_dir / name
            if path.exists():
                found.append(path)
            # Also check subdirs
            for sub in search_dir.iterdir():
                if sub.is_dir():
                    sub_path = sub / name
                    if sub_path.exists():
                        found.append(sub_path)
    
    # Remove duplicates
    return list(set(found))


def find_fstab_files(project: Project) -> List[Path]:
    """
    Tìm fstab files theo ưu tiên:
    1. vendor/etc/fstab*
    2. system/etc/fstab*
    3. product/etc/fstab*
    """
    found = []
    
    search_paths = [
        (project.source_dir / "vendor_a" / "etc", "fstab*"),
        (project.source_dir / "vendor_a" / "etc", "*fstab*"),
        (project.source_dir / "system_a" / "etc", "fstab*"),
        (project.source_dir / "system_a" / "etc", "*fstab*"),
        (project.source_dir / "product_a" / "etc", "fstab*"),
    ]
    
    for search_dir, pattern in search_paths:
        if search_dir.exists():
            for path in search_dir.glob(pattern):
                if path.is_file() and path not in found:
                    found.append(path)
    
    return found


def create_disabled_vbmeta(
    input_vbmeta: Path,
    output_path: Path,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Tạo vbmeta_disabled.img bằng avbtool
    avbtool make_vbmeta_image --flags 2 --padding_size 4096 --output <output>
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[AVB] Creating disabled vbmeta: {input_vbmeta.name}")
    
    try:
        from ..tools.registry import get_tool_registry
        registry = get_tool_registry()
        
        avbtool = registry.get_tool_path("avbtool")
        if not avbtool:
            # Try avbtool.py
            avbtool = registry.get_tool_path("avbtool.py")
        
        if not avbtool:
            return TaskResult.error("Tool avbtool not found")
        
        # Determine if it's Python script or executable
        is_python = str(avbtool).endswith('.py')
        
        if is_python:
            args = ["python", str(avbtool)]
        else:
            args = [str(avbtool)]
        
        args.extend([
            "make_vbmeta_image",
            "--flags", "2",  # AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED
            "--padding_size", "4096",
            "--output", str(output_path),
        ])
        
        from ..tools.runner import run_tool
        result = run_tool(args, _cancel_token=_cancel_token)
        
        if result.returncode != 0:
            # Fallback: create minimal disabled vbmeta
            log.warning("[AVB] avbtool failed, creating minimal disabled vbmeta")
            
            # Minimal vbmeta header with flags=2
            vbmeta_header = bytearray(4096)
            # Magic: "AVB0"
            vbmeta_header[0:4] = b'AVB0'
            # Required version: 1.0
            vbmeta_header[4:8] = (1).to_bytes(4, 'big')
            vbmeta_header[8:12] = (0).to_bytes(4, 'big')
            # Flags: 2 (disable verification)
            vbmeta_header[120:124] = (2).to_bytes(4, 'big')
            
            output_path.write_bytes(vbmeta_header)
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[AVB] Created: {output_path}")
        
        return TaskResult.success(
            message=f"Created {output_path.name}",
            artifacts=[str(output_path)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[AVB] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def patch_fstab_line(line: str) -> Tuple[str, List[str]]:
    """
    Patch một dòng fstab
    Returns: (patched_line, list_of_changes)
    """
    changes = []
    result = line
    
    for name, (pattern, replacement) in FSTAB_PATTERNS.items():
        if re.search(pattern, result):
            result = re.sub(pattern, replacement, result)
            changes.append(name)
    
    # Clean up multiple commas and trailing commas
    result = re.sub(r',+', ',', result)
    result = re.sub(r',(\s)', r'\1', result)
    result = re.sub(r'\s+', ' ', result)
    
    return result, changes


def patch_fstab_file(
    fstab_path: Path,
    backup: bool = True,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Patch fstab file để disable dm-verity, AVB, forceencrypt
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[FSTAB] Patching: {fstab_path}")
    
    try:
        # Read original
        content = fstab_path.read_text(encoding='utf-8', errors='replace')
        lines = content.splitlines()
        
        # Backup
        if backup:
            backup_path = fstab_path.with_suffix('.bak')
            if not backup_path.exists():
                shutil.copy2(fstab_path, backup_path)
                log.info(f"[FSTAB] Backup: {backup_path}")
        
        # Patch lines
        patched_lines = []
        total_changes = []
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                patched_lines.append(line)
                continue
            
            patched, changes = patch_fstab_line(line)
            patched_lines.append(patched)
            
            if changes:
                total_changes.append(f"Line {i+1}: {', '.join(changes)}")
        
        # Write patched
        fstab_path.write_text('\n'.join(patched_lines) + '\n', encoding='utf-8')
        
        elapsed = int((time.time() - start) * 1000)
        
        if total_changes:
            log.success(f"[FSTAB] Patched {len(total_changes)} lines")
            for change in total_changes[:5]:  # Log first 5
                log.info(f"[FSTAB] {change}")
            if len(total_changes) > 5:
                log.info(f"[FSTAB] ... and {len(total_changes)-5} more")
        else:
            log.info("[FSTAB] No changes needed")
        
        return TaskResult.success(
            message=f"Patched {fstab_path.name}",
            artifacts=[str(fstab_path)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[FSTAB] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def disable_dm_verity_full(
    project: Project,
    vbmeta_input: Path = None,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Full dm-verity disable (A+B):
    A) Create vbmeta_disabled.img
    B) Patch all fstab files
    """
    log = get_log_bus()
    start = time.time()
    
    log.info("[DM-VERITY] Starting full disable (A+B)")
    
    results = []
    
    try:
        # Part A: vbmeta
        if vbmeta_input and vbmeta_input.exists():
            vbmeta_list = [vbmeta_input]
        else:
            vbmeta_list = find_vbmeta_files(project)
        
        if vbmeta_list:
            for vbmeta in vbmeta_list:
                if _cancel_token and _cancel_token.is_set():
                    return TaskResult.cancelled()
                
                output_name = vbmeta.stem + "_disabled.img"
                output_path = project.out_dir / output_name
                
                result = create_disabled_vbmeta(vbmeta, output_path, _cancel_token)
                results.append(("vbmeta", result))
        else:
            log.warning("[DM-VERITY] No vbmeta files found")
        
        # Part B: fstab
        fstab_list = find_fstab_files(project)
        
        if fstab_list:
            for fstab in fstab_list:
                if _cancel_token and _cancel_token.is_set():
                    return TaskResult.cancelled()
                
                result = patch_fstab_file(fstab, backup=True, _cancel_token=_cancel_token)
                results.append(("fstab", result))
        else:
            log.warning("[DM-VERITY] No fstab files found")
        
        elapsed = int((time.time() - start) * 1000)
        
        # Summary
        ok_count = sum(1 for _, r in results if r.ok)
        fail_count = sum(1 for _, r in results if not r.ok)
        
        if fail_count > 0:
            log.warning(f"[DM-VERITY] {ok_count} OK, {fail_count} failed")
            return TaskResult.error(
                f"Completed with {fail_count} errors",
                elapsed_ms=elapsed
            )
        
        log.success(f"[DM-VERITY] All done ({ok_count} files)")
        
        return TaskResult.success(
            message=f"Disabled dm-verity ({ok_count} files)",
            artifacts=[r.artifacts[0] for _, r in results if r.ok and r.artifacts],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[DM-VERITY] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


# Demo function
def disable_dm_verity_demo(
    project: Project,
    _cancel_token: Event = None
) -> TaskResult:
    """Demo disable dm-verity - tạo markers"""
    log = get_log_bus()
    start = time.time()
    
    log.info("[DM-VERITY-DEMO] Demo disable")
    
    try:
        ensure_dir(project.out_dir)
        
        # Create demo markers
        markers = [
            project.out_dir / "vbmeta_disabled.img",
            project.out_dir / "DMVERITY_DISABLED_OK.txt",
        ]
        
        for marker in markers:
            marker.write_text(f"Demo file\nCreated: {timestamp()}\n", encoding='utf-8')
            log.info(f"[DM-VERITY-DEMO] Created: {marker.name}")
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[DM-VERITY-DEMO] Done in {elapsed}ms")
        
        return TaskResult.success(
            message="Demo dm-verity disabled",
            artifacts=[str(m) for m in markers],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        log.error(f"[DM-VERITY-DEMO] Error: {e}")
        return TaskResult.error(str(e))
