"""
ROM Detection - Detect loại ROM dựa trên filename/extension
Priority: update.img > release_update.img > super.img
"""
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum

from .errors import RomDetectError


class RomType(Enum):
    """Các loại ROM được hỗ trợ"""
    UPDATE_IMG = "update.img"
    RELEASE_UPDATE_IMG = "release_update.img"
    SUPER_IMG = "super.img"
    UNKNOWN = "unknown"


# Priority order for detection
ROM_PRIORITY = [
    RomType.UPDATE_IMG,
    RomType.RELEASE_UPDATE_IMG,
    RomType.SUPER_IMG,
]

# Filename patterns for each type
ROM_PATTERNS = {
    RomType.UPDATE_IMG: [
        "update.img",
    ],
    RomType.RELEASE_UPDATE_IMG: [
        "release_update.img",
    ],
    RomType.SUPER_IMG: [
        "super.img",
    ],
}


def detect_rom_type(file_path: Path) -> RomType:
    """
    Detect loại ROM từ file path
    
    Args:
        file_path: Đường dẫn đến ROM file
        
    Returns:
        RomType enum
    """
    if not file_path.exists():
        return RomType.UNKNOWN
    
    filename = file_path.name.lower()
    
    # Check exact matches first
    for rom_type in ROM_PRIORITY:
        patterns = ROM_PATTERNS.get(rom_type, [])
        for pattern in patterns:
            if filename == pattern.lower():
                return rom_type
    
    # Fallback: check contains
    if 'update' in filename and filename.endswith('.img'):
        if 'release' in filename:
            return RomType.RELEASE_UPDATE_IMG
        return RomType.UPDATE_IMG
    
    if 'super' in filename and filename.endswith('.img'):
        return RomType.SUPER_IMG
    
    return RomType.UNKNOWN


def detect_rom_in_folder(folder: Path) -> Optional[Tuple[Path, RomType]]:
    """
    Tìm ROM file trong folder theo priority
    
    Args:
        folder: Folder để search
        
    Returns:
        Tuple (file_path, rom_type) hoặc None
    """
    if not folder.is_dir():
        return None
    
    # Search theo priority
    for rom_type in ROM_PRIORITY:
        patterns = ROM_PATTERNS.get(rom_type, [])
        for pattern in patterns:
            matches = list(folder.glob(pattern))
            if matches:
                return (matches[0], rom_type)
    
    # Fallback: search all .img files
    for img_file in folder.glob("*.img"):
        rom_type = detect_rom_type(img_file)
        if rom_type != RomType.UNKNOWN:
            return (img_file, rom_type)
    
    return None


def get_rom_info(file_path: Path) -> dict:
    """
    Lấy thông tin cơ bản của ROM file
    
    Returns:
        Dict với các keys: path, name, size, type
    """
    if not file_path.exists():
        return {"exists": False}
    
    stat = file_path.stat()
    rom_type = detect_rom_type(file_path)
    
    return {
        "exists": True,
        "path": str(file_path),
        "name": file_path.name,
        "size": stat.st_size,
        "type": rom_type.value,
        "type_enum": rom_type,
    }


def is_rockchip_rom(file_path: Path) -> bool:
    """
    Kiểm tra xem có phải Rockchip ROM không (heuristic)
    
    Note: Để detect chính xác cần parse header của file,
    hiện tại chỉ dựa vào filename pattern
    """
    rom_type = detect_rom_type(file_path)
    # update.img và release_update.img thường là Rockchip
    # super.img có thể là bất kỳ Android device nào
    return rom_type in [RomType.UPDATE_IMG, RomType.RELEASE_UPDATE_IMG]
