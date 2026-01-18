"""
Build Image - Build ext4/erofs images từ source folder
Hỗ trợ output raw hoặc sparse
"""
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from threading import Event

from .task_defs import TaskResult
from .project_store import Project
from .logbus import get_log_bus
from .utils import ensure_dir, timestamp


@dataclass
class BuildImageConfig:
    """Cấu hình build image"""
    # Make Settings
    block_size: int = 4096
    hash_algorithm: str = "half_md4"
    hash_seed: str = ""
    has_journal: bool = True
    image_size: int = 0  # bytes, 0 = auto
    inode_size: int = 256
    number_of_inodes: int = 0  # 0 = auto
    reserved_blocks_percentage: int = 0
    uuid: str = ""
    volume_label: str = ""
    
    # Android Settings
    ext4_share_duplicated_blocks: bool = True
    file_contexts: str = ""  # path to file_contexts
    fs_config: str = ""  # path to fs_config
    mount_point: str = ""  # e.g., /system, /vendor
    source_dir: str = ""
    
    # Common Settings
    filesystem: str = "ext4"  # ext4 or erofs
    output_filename: str = ""
    output_type: str = "raw"  # raw or sparse
    timestamp_value: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_size": self.block_size,
            "hash_algorithm": self.hash_algorithm,
            "hash_seed": self.hash_seed,
            "has_journal": self.has_journal,
            "image_size": self.image_size,
            "inode_size": self.inode_size,
            "number_of_inodes": self.number_of_inodes,
            "reserved_blocks_percentage": self.reserved_blocks_percentage,
            "uuid": self.uuid,
            "volume_label": self.volume_label,
            "ext4_share_duplicated_blocks": self.ext4_share_duplicated_blocks,
            "file_contexts": self.file_contexts,
            "fs_config": self.fs_config,
            "mount_point": self.mount_point,
            "source_dir": self.source_dir,
            "filesystem": self.filesystem,
            "output_filename": self.output_filename,
            "output_type": self.output_type,
            "timestamp_value": self.timestamp_value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BuildImageConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Default configs for partitions
DEFAULT_PARTITION_CONFIGS = {
    "system_a": BuildImageConfig(
        mount_point="/system",
        volume_label="system",
        output_filename="system_a.img",
    ),
    "vendor_a": BuildImageConfig(
        mount_point="/vendor",
        volume_label="vendor",
        output_filename="vendor_a.img",
    ),
    "product_a": BuildImageConfig(
        mount_point="/product",
        volume_label="product",
        output_filename="product_a.img",
    ),
    "odm_a": BuildImageConfig(
        mount_point="/odm",
        volume_label="odm",
        output_filename="odm_a.img",
    ),
    "system_ext_a": BuildImageConfig(
        mount_point="/system_ext",
        volume_label="system_ext",
        output_filename="system_ext_a.img",
    ),
}


def get_folder_size(path: Path) -> int:
    """Tính tổng size folder (bytes)"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception:
        pass
    return total


def estimate_image_size(folder_size: int, overhead: float = 1.15) -> int:
    """Ước tính image size từ folder size (thêm overhead)"""
    # Thêm 15% overhead cho metadata và alignment
    estimated = int(folder_size * overhead)
    # Align to 4KB
    aligned = ((estimated + 4095) // 4096) * 4096
    return aligned


def find_file_contexts(project: Project, partition: str) -> Optional[Path]:
    """Tìm file_contexts cho partition"""
    # Check config folder first
    config_dir = project.config_dir
    patterns = [
        f"file_contexts.txt.{partition}_file_contexts.txt",
        f"{partition}_file_contexts.txt",
        "file_contexts.txt",
    ]
    
    for pattern in patterns:
        path = config_dir / pattern
        if path.exists():
            return path
    
    # Check source folder
    source_dir = project.source_dir / partition
    etc_paths = [
        source_dir / "etc" / "selinux" / "plat_file_contexts",
        source_dir / "etc" / "selinux" / "file_contexts",
    ]
    
    for path in etc_paths:
        if path.exists():
            return path
    
    return None


def find_fs_config(project: Project, partition: str) -> Optional[Path]:
    """Tìm fs_config cho partition"""
    config_dir = project.config_dir
    patterns = [
        f"{partition}_filesystem_config.txt",
        f"{partition}_fs_config.txt",
        "filesystem_config.txt",
    ]
    
    for pattern in patterns:
        path = config_dir / pattern
        if path.exists():
            return path
    
    return None


def build_ext4_image(
    config: BuildImageConfig,
    output_path: Path,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Build ext4 image using make_ext4fs
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BUILD_EXT4] Building {output_path.name}")
    log.info(f"[BUILD_EXT4] Source: {config.source_dir}")
    log.info(f"[BUILD_EXT4] Mount point: {config.mount_point}")
    log.info(f"[BUILD_EXT4] Image size: {config.image_size} bytes")
    
    try:
        from ..tools.registry import get_tool_registry
        registry = get_tool_registry()
        
        make_ext4fs = registry.get_tool_path("make_ext4fs")
        if not make_ext4fs:
            return TaskResult.error("Tool make_ext4fs.exe not found")
        
        # Build command
        args = [
            str(make_ext4fs),
            "-l", str(config.image_size),
            "-a", config.mount_point.lstrip('/'),
        ]
        
        if config.file_contexts:
            args.extend(["-S", config.file_contexts])
        
        if config.fs_config:
            args.extend(["-C", config.fs_config])
        
        if config.ext4_share_duplicated_blocks:
            args.append("-c")
        
        if config.has_journal:
            args.append("-J")
        
        if config.timestamp_value:
            args.extend(["-T", str(config.timestamp_value)])
        
        args.extend([str(output_path), config.source_dir])
        
        # Run command
        from ..tools.runner import run_tool
        result = run_tool(args, _cancel_token=_cancel_token)
        
        if result.returncode != 0:
            return TaskResult.error(f"make_ext4fs failed: {result.stderr}")
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BUILD_EXT4] Completed in {elapsed}ms")
        
        return TaskResult.success(
            message=f"Built {output_path.name}",
            artifacts=[str(output_path)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[BUILD_EXT4] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def build_erofs_image(
    config: BuildImageConfig,
    output_path: Path,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Build erofs image using mkfs.erofs
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BUILD_EROFS] Building {output_path.name}")
    log.info(f"[BUILD_EROFS] Source: {config.source_dir}")
    
    try:
        from ..tools.registry import get_tool_registry
        registry = get_tool_registry()
        
        mkfs_erofs = registry.get_tool_path("mkfs.erofs")
        if not mkfs_erofs:
            return TaskResult.error("Tool mkfs.erofs.exe not found")
        
        # Build command
        args = [
            str(mkfs_erofs),
            "-z", "lz4hc",
        ]
        
        if config.file_contexts:
            args.extend(["--file-contexts", config.file_contexts])
        
        if config.mount_point:
            args.extend(["--mount-point", config.mount_point])
        
        args.extend([str(output_path), config.source_dir])
        
        # Run command
        from ..tools.runner import run_tool
        result = run_tool(args, _cancel_token=_cancel_token)
        
        if result.returncode != 0:
            return TaskResult.error(f"mkfs.erofs failed: {result.stderr}")
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BUILD_EROFS] Completed in {elapsed}ms")
        
        return TaskResult.success(
            message=f"Built {output_path.name}",
            artifacts=[str(output_path)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[BUILD_EROFS] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def convert_to_sparse(
    raw_image: Path,
    sparse_image: Path,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Convert raw image to sparse using img2simg
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[SPARSE] Converting {raw_image.name} to sparse")
    
    try:
        from ..tools.registry import get_tool_registry
        registry = get_tool_registry()
        
        img2simg = registry.get_tool_path("img2simg")
        if not img2simg:
            return TaskResult.error("Tool img2simg.exe not found")
        
        args = [str(img2simg), str(raw_image), str(sparse_image)]
        
        from ..tools.runner import run_tool
        result = run_tool(args, _cancel_token=_cancel_token)
        
        if result.returncode != 0:
            return TaskResult.error(f"img2simg failed: {result.stderr}")
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[SPARSE] Completed in {elapsed}ms")
        
        return TaskResult.success(
            message=f"Converted to {sparse_image.name}",
            artifacts=[str(sparse_image)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[SPARSE] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def build_image(
    project: Project,
    partition: str,
    config: BuildImageConfig,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Main function to build image (ext4 or erofs, raw or sparse)
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BUILD] Building {partition} image")
    log.info(f"[BUILD] Filesystem: {config.filesystem}")
    log.info(f"[BUILD] Output type: {config.output_type}")
    
    try:
        # Validate source dir
        source_dir = Path(config.source_dir)
        if not source_dir.exists():
            return TaskResult.error(f"Source folder not found: {source_dir}")
        
        # Prepare output paths
        output_dir = project.image_dir
        ensure_dir(output_dir)
        
        raw_filename = config.output_filename or f"{partition}.img"
        raw_path = output_dir / raw_filename
        
        # Auto-calculate image size if not set
        if config.image_size <= 0:
            folder_size = get_folder_size(source_dir)
            config.image_size = estimate_image_size(folder_size)
            log.info(f"[BUILD] Auto image size: {config.image_size} bytes ({config.image_size // (1024*1024)} MB)")
        
        # Build raw image
        if config.filesystem == "ext4":
            result = build_ext4_image(config, raw_path, _cancel_token)
        elif config.filesystem == "erofs":
            result = build_erofs_image(config, raw_path, _cancel_token)
        else:
            return TaskResult.error(f"Unknown filesystem: {config.filesystem}")
        
        if not result.ok:
            return result
        
        # Convert to sparse if requested
        final_path = raw_path
        if config.output_type == "sparse":
            sparse_filename = raw_filename.replace(".img", "_sparse.img")
            sparse_path = output_dir / sparse_filename
            
            sparse_result = convert_to_sparse(raw_path, sparse_path, _cancel_token)
            if not sparse_result.ok:
                return sparse_result
            
            # Delete raw, keep sparse
            raw_path.unlink(missing_ok=True)
            final_path = sparse_path
        
        # Save config to project
        project.update_config(
            build_presets={partition: config.to_dict()}
        )
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BUILD] Completed {partition} in {elapsed}ms")
        
        return TaskResult.success(
            message=f"Built {final_path.name}",
            artifacts=[str(final_path)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[BUILD] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)


def build_image_bulk(
    project: Project,
    partitions: list = None,
    configs: Dict[str, BuildImageConfig] = None,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Build multiple partition images in sequence
    """
    log = get_log_bus()
    start = time.time()
    
    partitions = partitions or ["system_a", "vendor_a", "product_a"]
    configs = configs or {}
    
    log.info(f"[BUILD_BULK] Building {len(partitions)} partitions")
    
    results = []
    failed = []
    
    for partition in partitions:
        if _cancel_token and _cancel_token.is_set():
            log.warning("[BUILD_BULK] Cancelled by user")
            break
        
        # Get config or use default
        if partition in configs:
            config = configs[partition]
        elif partition in DEFAULT_PARTITION_CONFIGS:
            config = DEFAULT_PARTITION_CONFIGS[partition]
        else:
            config = BuildImageConfig()
        
        # Set source dir
        source_dir = project.source_dir / partition
        if not source_dir.exists():
            log.warning(f"[BUILD_BULK] Skipping {partition}: source folder not found")
            continue
        
        config.source_dir = str(source_dir)
        
        # Auto-detect file_contexts and fs_config
        fc = find_file_contexts(project, partition)
        if fc:
            config.file_contexts = str(fc)
        
        fsc = find_fs_config(project, partition)
        if fsc:
            config.fs_config = str(fsc)
        
        # Build
        result = build_image(project, partition, config, _cancel_token)
        results.append((partition, result))
        
        if not result.ok:
            failed.append(partition)
    
    elapsed = int((time.time() - start) * 1000)
    
    if failed:
        log.error(f"[BUILD_BULK] Failed partitions: {', '.join(failed)}")
        return TaskResult.error(
            f"Failed: {', '.join(failed)}",
            elapsed_ms=elapsed
        )
    
    log.success(f"[BUILD_BULK] Completed in {elapsed}ms")
    return TaskResult.success(
        message=f"Built {len(partitions)} partitions",
        elapsed_ms=elapsed
    )


# Demo functions for Phase 1 compatibility
def build_image_demo(
    project: Project,
    partition: str,
    config: BuildImageConfig = None,
    _cancel_token: Event = None
) -> TaskResult:
    """
    Demo build image - tạo marker file thay vì build thật
    """
    log = get_log_bus()
    start = time.time()
    
    log.info(f"[BUILD_DEMO] Demo building {partition}")
    
    try:
        # Simulate progress
        for i in range(5):
            if _cancel_token and _cancel_token.is_set():
                return TaskResult.cancelled()
            time.sleep(0.2)
            log.info(f"[BUILD_DEMO] Progress: {(i+1)*20}%")
        
        # Create marker
        ensure_dir(project.image_dir)
        marker = project.image_dir / f"BUILD_{partition.upper()}_OK.txt"
        marker.write_text(
            f"Demo build for {partition}\n"
            f"Created: {timestamp()}\n"
            f"Filesystem: {config.filesystem if config else 'ext4'}\n",
            encoding='utf-8'
        )
        
        elapsed = int((time.time() - start) * 1000)
        log.success(f"[BUILD_DEMO] Completed in {elapsed}ms")
        
        return TaskResult.success(
            message=f"Demo built {partition}",
            artifacts=[str(marker)],
            elapsed_ms=elapsed
        )
        
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        log.error(f"[BUILD_DEMO] Error: {e}")
        return TaskResult.error(str(e), elapsed_ms=elapsed)
