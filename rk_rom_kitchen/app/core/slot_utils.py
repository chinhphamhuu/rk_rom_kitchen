"""
Slot Utils - Helpers for A/B partition slot suffix handling
Tránh unsafe replace('_a','').replace('_b','') có thể cắt nhầm tên partition
"""


def strip_slot_suffix(name: str) -> str:
    """
    Strip slot suffix (_a/_b) from end of partition name only
    
    Examples:
        "system_a" -> "system"
        "vendor_b" -> "vendor"
        "data_backup" -> "data_backup" (không cắt vì không phải suffix)
        "camera" -> "camera"
    """
    if name.endswith("_a") or name.endswith("_b"):
        return name[:-2]
    return name


def normalize_mount_base(name: str) -> str:
    """
    Normalize partition name to mount base (no slot, no leading slash)
    
    Examples:
        "system_a" -> "system"
        "/vendor_b" -> "vendor"
        "product" -> "product"
    """
    base = name.lstrip("/")
    return strip_slot_suffix(base)


def get_mount_point(partition_name: str) -> str:
    """
    Get Android mount point for partition
    
    Examples:
        "system_a" -> "/system"
        "vendor_b" -> "/vendor"
    """
    base = normalize_mount_base(partition_name)
    return f"/{base}"
