@echo off
setlocal enabledelayedexpansion

title Ink and Iron Launcher

echo ============================================================
echo   Ink and Iron - Launcher
echo ============================================================
echo.

:: Resolve directory (where this .bat lives)
cd /d "%~dp0"

:: ------------------------------------------------------------
:: The game runs in FULL without any key or internet connection
:: (built-in parser, everything offline). config.txt is OPTIONAL:
:: if it contains an Anthropic key, unusually-phrased orders get
:: interpreted by Claude ("Smarter Parsing"). No key = mock mode.
:: ------------------------------------------------------------
set "API_KEY="
if exist "config.txt" (
    for /f "tokens=1,* delims==" %%a in ('findstr /i "^ANTHROPIC_API_KEY=" config.txt') do (
        set "API_KEY=%%b"
    )
)

:: Placeholder or blank counts as "no key"
if "!API_KEY!"=="your_key_here" set "API_KEY="

if defined API_KEY (
    set "ANTHROPIC_API_KEY=!API_KEY!"
    set "LLM_MODE=anthropic"
    echo [INFO] Smarter Parsing: ON ^(Anthropic key found in config.txt^)
) else (
    set "LLM_MODE=mock"
    echo [INFO] Smarter Parsing: off - using the built-in parser.
    echo        The full game works this way. To enable it later, add a
    echo        key to config.txt or use Settings in the game's main menu.
)
echo.

:: Check server executable exists
if not exist "ink_iron_server.exe" (
    echo [ERROR] ink_iron_server.exe not found!
    echo The build may be incomplete. Re-extract the zip and try again.
    pause
    exit /b 1
)

:: If a server is already answering on port 8005, reuse it rather than
:: silently starting a second one underneath it.
curl -s --fail -o nul http://127.0.0.1:8005/test 2>nul
if not errorlevel 1 (
    echo [WARN] A server is already running on port 8005 - reusing it.
    echo        ^(If the game acts stale, close everything and relaunch.^)
    goto server_up
)

:: Start server in a minimized window
echo [INFO] Starting server...
start "Ink and Iron Server" /min ink_iron_server.exe

:: Wait until the server actually answers (up to ~30s) instead of hoping
:: a fixed 3s was enough. curl ships with Windows 10/11.
echo [INFO] Waiting for the server to come up...
set /a TRIES=0
:wait_server
curl -s --fail -o nul http://127.0.0.1:8005/test 2>nul
if not errorlevel 1 goto server_up
set /a TRIES+=1
if !TRIES! geq 30 goto server_dead
timeout /t 1 /nobreak >nul
goto wait_server

:server_dead
echo.
echo [ERROR] The server did not come up after 30 seconds.
echo.
echo   - Check the "Ink and Iron Server" window in the taskbar for
echo     an error message ^(it stays open when something goes wrong^).
echo   - If it closed instantly, run ink_iron_server.exe from a
echo     command prompt to see the error.
echo   - Port 8005 may be blocked by another program or a firewall.
echo.
pause
exit /b 1

:server_up

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
    echo [WARNING] InkAndIron.exe not found in this folder.
    echo.
    echo [INFO] Server running at http://127.0.0.1:8005
    echo [INFO] Press any key to stop the server.
    pause >nul
    taskkill /fi "WINDOWTITLE eq Ink and Iron Server" /f >nul 2>&1
)

endlocal
