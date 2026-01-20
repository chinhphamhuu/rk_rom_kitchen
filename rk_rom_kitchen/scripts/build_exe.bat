@echo off
setlocal
cd /d "%~dp0.."

echo [BUILD] Checking venv...
if not exist .venv (
    echo [BUILD] Creating .venv and installing dependencies...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.runtime.txt
    pip install pyinstaller
) else (
    call .venv\Scripts\activate
)

echo [BUILD] Cleaning dist...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [BUILD] Running PyInstaller...
pyinstaller rk_rom_kitchen.spec --clean --noconfirm

echo [BUILD] Complete!
if exist dist\RK_ROM_Kitchen\RK_ROM_Kitchen.exe (
    echo [SUCCESS] Build output: dist\RK_ROM_Kitchen
) else (
    echo [FAIL] Build failed to produce executable.
)
pause
