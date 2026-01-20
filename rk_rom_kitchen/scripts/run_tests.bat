@echo off
setlocal
cd /d "%~dp0.."
set PYTHONPATH=%CD%

echo [TEST] Running Compilation Check...
python -m compileall -q app
if errorlevel 1 goto fail

echo [TEST] Running Unit Tests...
python -m unittest discover -s app/tests -p "test_*.py"
if errorlevel 1 goto fail

echo [TEST] Running Smoke Test...
python -m app.tests.smoke_test
if errorlevel 1 goto fail

echo.
echo ==================================================
echo [SUCCESS] ALL TESTS PASSED - RELEASE READY
echo ==================================================
exit /b 0

:fail
echo.
echo ==================================================
echo [FAIL] TESTS FAILED - DO NOT RELEASE
echo ==================================================
exit /b 1
