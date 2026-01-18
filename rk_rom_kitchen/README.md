# RK ROM Kitchen

Công cụ mod ROM dành riêng cho thiết bị **Rockchip** với giao diện hiện đại.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-orange.svg)

> Giao diện lấy cảm hứng từ CRB Android Kitchen.

## Tính năng

### Phase 1 (Đã hoàn thành)
- 🔧 **Extract ROM (Auto)**: Tự động detect và extract update.img, release_update.img, super.img
- 📦 **Patches**: Disable dm-verity, AVB, enable ADB root, debloat apps
- 🔨 **Build ROM**: Đóng gói ROM đã mod thành file output
- 🌐 **Đa ngôn ngữ**: Hỗ trợ Tiếng Việt và English
- 💾 **Workspace**: Quản lý nhiều projects

### Phase 2 (Mới)
- 🏗️ **Build Image**: Build ext4/erofs image từ source folder (raw hoặc sparse)
- 🔓 **Disable dm-verity/AVB**: Tạo vbmeta_disabled.img + patch fstab (B2)
- 🗑️ **Debloater**: Scan và xóa APK bloatware (move to Recycle Bin)
- 🔧 **Magisk Patch**: Patch boot/init_boot với Magisk
- 📦 **Unpack/Repack Boot**: Xử lý boot.img, vendor_boot.img, init_boot.img

## Yêu cầu hệ thống

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.10 trở lên
- **RAM**: 4GB+ (khuyến nghị 8GB)
- **Disk**: 10GB trống cho workspace

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/chinhphamhuu/chinh.git
cd chinh/rk_rom_kitchen
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
run.bat
```

Hoặc:

```bash
python -m app.main
```

## Cấu trúc Workspace

Workspace root: `%USERPROFILE%\Documents\RK_Kitchen\Projects`

```
Projects/
├── project_1/
│   ├── in/                    # Input ROM files
│   ├── out/
│   │   ├── Source/            # Extracted source tree
│   │   │   ├── system_a/      # System partition
│   │   │   ├── vendor_a/      # Vendor partition
│   │   │   └── product_a/     # Product partition
│   │   └── Image/             # Built images
│   ├── temp/                  # Temporary files
│   ├── logs/                  # Project logs
│   └── config/                # project.json + presets
└── project_2/
    └── ...
```

## Cách đặt Tools

### Tùy chọn 1: Thư mục third_party

Đặt các tool vào `rk_rom_kitchen/third_party/tools/win64/`:

```
third_party/tools/win64/
├── make_ext4fs.exe      # Build ext4 images
├── mkfs.erofs.exe       # Build erofs images
├── img2simg.exe         # Convert raw to sparse
├── simg2img.exe         # Convert sparse to raw
├── lpunpack.exe         # Unpack super.img
├── lpmake.exe           # Build super.img
├── avbtool.py           # Android Verified Boot tool
└── ...
```

### Tùy chọn 2: Custom tool_dir

Trong Settings > Tool Directory, chỉ định đường dẫn thư mục chứa tools.

### Tùy chọn 3: System PATH

Thêm thư mục tools vào biến môi trường PATH của Windows.

## Các loại ROM được hỗ trợ

| Priority | File | Mô tả |
|----------|------|-------|
| 1 | `update.img` | Rockchip full firmware |
| 2 | `release_update.img` | Rockchip release firmware |
| 3 | `super.img` | Android super partition |

## Log files

- **App log**: `%APPDATA%\rk_kitchen\app.log`
- **Crash log**: `%APPDATA%\rk_kitchen\crash.log`
- **Settings**: `%APPDATA%\rk_kitchen\settings.json`
- **Project log**: `<workspace>/<project>/logs/project.log`

## Build Portable EXE

```bash
cd build
build.bat
```

Output: `dist/RK_ROM_Kitchen/`

## Smoke Test

```bash
cd rk_rom_kitchen
python -m app.tests.smoke_test
```

## Phase 1 vs Phase 2

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Build Image | Demo | Thật (ext4/erofs) |
| vbmeta disabled | Stub | Thật (avbtool) |
| fstab patch | Stub | Thật (B2 rules) |
| Debloater | - | Scan + Delete |
| Magisk patch | - | UI + Demo |
| Boot unpack | - | UI + Demo |

## Cấu trúc source code

```
rk_rom_kitchen/
├── app/
│   ├── main.py              # Entry point
│   ├── i18n.py              # Đa ngôn ngữ VI/EN
│   ├── crash_guard.py       # Exception handler
│   ├── core/                # Business logic
│   │   ├── build_image.py   # Build ext4/erofs
│   │   ├── avb_manager.py   # vbmeta + fstab
│   │   ├── debloater.py     # APK scanner
│   │   └── ...
│   ├── tools/               # CLI wrappers
│   └── ui/                  # PyQt5 UI
├── patches/                 # Patch configs
├── assets/                  # Icons/themes
└── third_party/tools/       # CLI tools
```

## License

MIT License
