@echo off
setlocal

echo ============================================================
echo   Ink ^& Iron - Build Script
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

:: Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

:: Navigate to project root
cd /d "%~dp0.."
echo [INFO] Project root: %cd%
echo.

:: Run PyInstaller
echo [INFO] Building server executable...
echo.
python -m PyInstaller deploy\ink_iron.spec --distpath deploy\dist --workpath deploy\build --clean
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check errors above.
    pause
    exit /b 1
)

echo.
echo [INFO] Copying config template...

:: Copy config.txt template
copy /y "deploy\dist_template\config.txt" "deploy\dist\ink_iron_server\config.txt" >nul
if errorlevel 1 (
    echo [WARN] Could not copy config.txt template. Copy it manually.
)

:: Copy launch.bat
copy /y "deploy\launch.bat" "deploy\dist\ink_iron_server\launch.bat" >nul

:: Copy README
copy /y "deploy\README_TESTER.txt" "deploy\dist\ink_iron_server\README_TESTER.txt" >nul

echo.
echo ============================================================
echo   BUILD COMPLETE
echo ============================================================
echo.
echo Output: deploy\dist\ink_iron_server\
echo.
echo Next steps:
echo   1. Export the Godot project as InkAndIron.exe
echo   2. Copy InkAndIron.exe + .pck into deploy\dist\ink_iron_server\
echo   3. Edit config.txt with the tester's Anthropic API key
echo   4. Zip the ink_iron_server folder and send to tester
echo   5. Tester unzips, edits config.txt, runs launch.bat
echo.
pause
