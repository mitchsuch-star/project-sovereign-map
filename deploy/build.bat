@echo off
setlocal

echo ============================================================
echo   Ink ^& Iron - Build Script
echo ============================================================
echo.

:: Navigate to project root first (needed to find .venv)
cd /d "%~dp0.."
set "PYTHON=%cd%\.venv\Scripts\python.exe"
set "PIP=%cd%\.venv\Scripts\pip.exe"

:: Check Python
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] .venv not found. Run from the project root with a venv set up.
    pause
    exit /b 1
)

:: Check PyInstaller
"%PYTHON%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    "%PIP%" install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

echo [INFO] Project root: %cd%
echo.

:: Run PyInstaller
echo [INFO] Building server executable...
echo.
"%PYTHON%" -m PyInstaller deploy\ink_iron.spec --distpath deploy\dist --workpath deploy\build --clean
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
echo   1. Export the Godot project as InkAndIron.exe (FRESH export -
echo      the March 2026 .pck predates the 126-province map cutover;
echo      verify europe_1805.json is inside the new .pck)
echo   2. Copy InkAndIron.exe + .pck into deploy\dist\ink_iron_server\
echo   3. Smoke it: run launch.bat WITHOUT editing config.txt - the
echo      game must boot and play in mock mode with no key
echo   4. Zip the ink_iron_server folder and send to tester
echo   5. Tester unzips and runs launch.bat (no key needed; a key in
echo      config.txt or the in-game Settings enables Smarter Parsing)
echo.
pause
