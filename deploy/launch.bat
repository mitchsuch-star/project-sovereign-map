@echo off
setlocal enabledelayedexpansion

title Ink and Iron Launcher

echo ============================================================
echo   Ink and Iron - Launcher
echo ============================================================
echo.

:: Resolve directory (where this .bat lives)
cd /d "%~dp0"

:: Check config.txt exists
if not exist "config.txt" (
    echo [ERROR] config.txt not found!
    echo.
    echo Create a config.txt in this folder with your API key:
    echo   ANTHROPIC_API_KEY=sk-ant-...
    echo.
    pause
    exit /b 1
)

:: Read API key from config.txt using findstr
set "API_KEY="
for /f "tokens=1,* delims==" %%a in ('findstr /i "^ANTHROPIC_API_KEY=" config.txt') do (
    set "API_KEY=%%b"
)

:: Validate key
if not defined API_KEY (
    echo [ERROR] Could not find ANTHROPIC_API_KEY in config.txt
    echo.
    echo Make sure config.txt contains a line like:
    echo   ANTHROPIC_API_KEY=sk-ant-...
    echo.
    pause
    exit /b 1
)

if "!API_KEY!"=="your_key_here" (
    echo [ERROR] You need to set your API key in config.txt
    echo.
    echo Open config.txt and replace "your_key_here" with your
    echo actual Anthropic API key ^(starts with sk-ant-^).
    echo.
    pause
    exit /b 1
)

:: Check server executable exists
if not exist "ink_iron_server.exe" (
    echo [ERROR] ink_iron_server.exe not found!
    echo The build may be incomplete.
    pause
    exit /b 1
)

:: Check Godot export exists
if not exist "InkAndIron.exe" (
    echo [WARNING] InkAndIron.exe not found in this folder.
    echo The game client won't launch automatically.
    echo Starting server only...
    echo.
)

:: Set environment variables
set "ANTHROPIC_API_KEY=!API_KEY!"
set "LLM_MODE=anthropic"

:: Start server in a minimized window
echo [INFO] Starting server...
start "Ink and Iron Server" /min ink_iron_server.exe

:: Wait for server to start
echo [INFO] Waiting for server to initialize...
timeout /t 3 /nobreak >nul

:: Start Godot client if present
if exist "InkAndIron.exe" (
    echo [INFO] Starting game...
    echo.
    echo ============================================================
    echo   Game is running. Close the game window when done.
    echo   Do NOT close the server window manually.
    echo ============================================================
    echo.

    start /wait "" InkAndIron.exe

    echo.
    echo [INFO] Game closed. Shutting down server...

    :: Kill server by window title
    taskkill /fi "WINDOWTITLE eq Ink and Iron Server" /f >nul 2>&1

    echo [INFO] Done.
    timeout /t 2 /nobreak >nul
) else (
    echo.
    echo [INFO] Server running at http://127.0.0.1:8005
    echo [INFO] Press any key to stop the server.
    pause >nul
    taskkill /fi "WINDOWTITLE eq Ink and Iron Server" /f >nul 2>&1
)

endlocal
