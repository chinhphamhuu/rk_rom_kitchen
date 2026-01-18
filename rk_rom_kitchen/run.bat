@echo off
:: RK ROM Kitchen - Run Script
:: Chạy ứng dụng trong development mode

echo ========================================
echo  RK ROM Kitchen - Development Mode
echo ========================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong duoc cai dat!
    echo Vui long cai dat Python 3.10+ tu https://python.org
    pause
    exit /b 1
)

:: Check pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip khong hoat dong!
    echo Thu: python -m ensurepip --upgrade
    pause
    exit /b 1
)

:: Check dependencies
echo [INFO] Kiem tra dependencies...
python -m pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Cai dat dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Cai dat dependencies that bai!
        echo Vui long chay: python -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

:: Run app
echo [INFO] Khoi dong RK ROM Kitchen...
echo.
python -m app.main

if errorlevel 1 (
    echo.
    echo [ERROR] Ung dung bi loi!
    pause
)
