"""
Internationalization (i18n) module
Hỗ trợ VI/EN với default VI
Technical terms giữ nguyên English
"""
from typing import Dict

# Ngôn ngữ mặc định
DEFAULT_LANG = "vi"

# Translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ===== Main Window =====
    "app_title": {
        "vi": "RK ROM Kitchen - Công cụ mod ROM Rockchip",
        "en": "RK ROM Kitchen - Rockchip ROM Modding Tool"
    },
    
    # ===== Icon Sidebar =====
    "nav_project": {"vi": "Project", "en": "Project"},
    "nav_folders": {"vi": "Thư mục", "en": "Folders"},
    "nav_extractor": {"vi": "Extractor", "en": "Extractor"},
    "nav_patches": {"vi": "Patches", "en": "Patches"},
    "nav_build": {"vi": "Build", "en": "Build"},
    "nav_settings": {"vi": "Cài đặt", "en": "Settings"},
    "nav_about": {"vi": "Giới thiệu", "en": "About"},
    
    # ===== Project Sidebar =====
    "project_info": {"vi": "Thông tin Project", "en": "Project Info"},
    "build_id": {"vi": "Build ID", "en": "Build ID"},
    "android_version": {"vi": "Android", "en": "Android"},
    "brand": {"vi": "Thương hiệu", "en": "Brand"},
    "model": {"vi": "Model", "en": "Model"},
    "product": {"vi": "Product", "en": "Product"},
    "select_project": {"vi": "Chọn Project", "en": "Select Project"},
    "no_project": {"vi": "Chưa có project", "en": "No project"},
    
    # ===== Context Menu =====
    "menu_create_project": {"vi": "Tạo project mới", "en": "Create new project"},
    "menu_delete_project": {"vi": "Xoá project", "en": "Delete project"},
    "menu_delete_partition": {"vi": "Xoá partition (stub)", "en": "Delete partition (stub)"},
    "menu_extract_auto": {"vi": "Extract ROM (Auto)", "en": "Extract ROM (Auto)"},
    
    "menu_open_rom": {"vi": "Thư mục ROM", "en": "ROM Folder"},
    "menu_open_build": {"vi": "Thư mục Build", "en": "Build Folder"},
    "menu_open_source": {"vi": "Thư mục Source", "en": "Source Folder"},
    "menu_open_output": {"vi": "Thư mục Output", "en": "Output Folder"},
    "menu_open_config": {"vi": "Thư mục Config", "en": "Config Folder"},
    "menu_open_log": {"vi": "Xem Log", "en": "View Log"},
    
    "menu_build_image": {"vi": "Build Image (stub)", "en": "Build Image (stub)"},
    "menu_build_bulk": {"vi": "Build Image Bulk (stub)", "en": "Build Image Bulk (stub)"},
    "menu_build_super": {"vi": "Build Super Image (stub)", "en": "Build Super Image (stub)"},
    
    # ===== Pages =====
    "page_project_title": {"vi": "Quản lý Project", "en": "Project Management"},
    "page_folders_title": {"vi": "Thư mục Project", "en": "Project Folders"},
    "page_extractor_title": {"vi": "Extract ROM", "en": "Extract ROM"},
    "page_patches_title": {"vi": "Áp dụng Patches", "en": "Apply Patches"},
    "page_build_title": {"vi": "Build ROM", "en": "Build ROM"},
    "page_settings_title": {"vi": "Cài đặt", "en": "Settings"},
    
    # ===== Buttons =====
    "btn_create": {"vi": "Tạo mới", "en": "Create"},
    "btn_delete": {"vi": "Xoá", "en": "Delete"},
    "btn_open": {"vi": "Mở", "en": "Open"},
    "btn_import": {"vi": "Import ROM", "en": "Import ROM"},
    "btn_extract": {"vi": "Extract", "en": "Extract"},
    "btn_apply": {"vi": "Áp dụng", "en": "Apply"},
    "btn_build": {"vi": "Build", "en": "Build"},
    "btn_save": {"vi": "Lưu", "en": "Save"},
    "btn_cancel": {"vi": "Hủy", "en": "Cancel"},
    "btn_browse": {"vi": "Duyệt...", "en": "Browse..."},
    "btn_refresh": {"vi": "Làm mới", "en": "Refresh"},
    "btn_check_tools": {"vi": "Kiểm tra tools", "en": "Check tools"},
    "btn_download_tools": {"vi": "Tải tools (Phase 2)", "en": "Download tools (Phase 2)"},
    
    # ===== Log Panel =====
    "log_title": {"vi": "Log", "en": "Log"},
    "log_search": {"vi": "Tìm kiếm...", "en": "Search..."},
    "log_copy": {"vi": "Copy", "en": "Copy"},
    "log_clear": {"vi": "Xóa", "en": "Clear"},
    "log_open_file": {"vi": "Mở file log", "en": "Open log file"},
    "log_auto_scroll": {"vi": "Tự động cuộn", "en": "Auto-scroll"},
    
    # ===== Status =====
    "status_idle": {"vi": "Sẵn sàng", "en": "Ready"},
    "status_running": {"vi": "Đang chạy...", "en": "Running..."},
    "status_done": {"vi": "Hoàn thành", "en": "Done"},
    "status_error": {"vi": "Lỗi", "en": "Error"},
    "status_busy": {"vi": "Đang chạy, vui lòng chờ...", "en": "Busy, please wait..."},
    
    # ===== Settings =====
    "settings_language": {"vi": "Ngôn ngữ", "en": "Language"},
    "settings_language_vi": {"vi": "Tiếng Việt", "en": "Vietnamese"},
    "settings_language_en": {"vi": "English", "en": "English"},
    "settings_tool_dir": {"vi": "Thư mục Tools", "en": "Tools Directory"},
    "settings_theme": {"vi": "Giao diện", "en": "Theme"},
    "settings_tools_table": {"vi": "Trạng thái Tools", "en": "Tools Status"},
    "settings_tool_name": {"vi": "Tool", "en": "Tool"},
    "settings_tool_path": {"vi": "Đường dẫn", "en": "Path"},
    "settings_tool_status": {"vi": "Trạng thái", "en": "Status"},
    "settings_available": {"vi": "Sẵn sàng", "en": "Available"},
    "settings_not_found": {"vi": "Không tìm thấy", "en": "Not found"},
    
    # ===== Dialogs =====
    "dialog_error": {"vi": "Lỗi", "en": "Error"},
    "dialog_warning": {"vi": "Cảnh báo", "en": "Warning"},
    "dialog_info": {"vi": "Thông tin", "en": "Information"},
    "dialog_confirm": {"vi": "Xác nhận", "en": "Confirm"},
    "dialog_coming_soon": {"vi": "Tính năng này sẽ có trong Phase 2", "en": "This feature is coming in Phase 2"},
    "dialog_crash_title": {"vi": "Có lỗi xảy ra", "en": "An error occurred"},
    "dialog_crash_message": {"vi": "Đã xảy ra lỗi không mong muốn. Chi tiết đã được ghi vào log.", 
                             "en": "An unexpected error occurred. Details have been logged."},
    
    "dialog_create_project": {"vi": "Tạo Project mới", "en": "Create New Project"},
    "dialog_project_name": {"vi": "Tên Project:", "en": "Project Name:"},
    "dialog_delete_confirm": {"vi": "Bạn có chắc muốn xóa project này?", "en": "Are you sure you want to delete this project?"},
    "dialog_select_rom": {"vi": "Chọn file ROM", "en": "Select ROM file"},
    
    # ===== Patches =====
    "patches_category_security": {"vi": "Bảo mật", "en": "Security"},
    "patches_category_debug": {"vi": "Debug", "en": "Debug"},
    "patches_category_apps": {"vi": "Ứng dụng", "en": "Apps"},
    
    # ===== About =====
    "about_title": {"vi": "Giới thiệu RK ROM Kitchen", "en": "About RK ROM Kitchen"},
    "about_description": {"vi": "Công cụ mod ROM dành cho thiết bị Rockchip", 
                          "en": "ROM modding tool for Rockchip devices"},
    "about_version": {"vi": "Phiên bản", "en": "Version"},
    
    # ===== Misc =====
    "workspace": {"vi": "Workspace", "en": "Workspace"},
    "filter": {"vi": "Lọc", "en": "Filter"},
    "all": {"vi": "Tất cả", "en": "All"},
    "none": {"vi": "Không có", "en": "None"},
    "yes": {"vi": "Có", "en": "Yes"},
    "no": {"vi": "Không", "en": "No"},
    "ok": {"vi": "OK", "en": "OK"},
    "unknown": {"vi": "Không xác định", "en": "Unknown"},
    "placeholder": {"vi": "—", "en": "—"},
}

# Current language
_current_lang = DEFAULT_LANG


def set_language(lang: str):
    """Set ngôn ngữ hiện tại"""
    global _current_lang
    if lang in ("vi", "en"):
        _current_lang = lang


def get_language() -> str:
    """Lấy ngôn ngữ hiện tại"""
    return _current_lang


def t(key: str, **kwargs) -> str:
    """
    Translate một key sang ngôn ngữ hiện tại
    
    Args:
        key: Translation key
        **kwargs: Format arguments
        
    Returns:
        Translated string hoặc key nếu không tìm thấy
    """
    trans = TRANSLATIONS.get(key, {})
    text = trans.get(_current_lang, trans.get("en", key))
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def tr(key: str, **kwargs) -> str:
    """Alias cho t()"""
    return t(key, **kwargs)
