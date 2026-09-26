@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Ink ^& Iron - Release Build
echo ============================================================
echo.

:: Navigate to project root first (needed to find .venv)
cd /d "%~dp0.."
set "PYTHON=%cd%\.venv\Scripts\python.exe"
set "PIP=%cd%\.venv\Scripts\pip.exe"
set "DIST=%cd%\deploy\dist\ink_iron_server"
set "GODOT_PROJECT=%cd%\godot-client\project-sovereign"

:: The Godot editor binary that runs the export. Set GODOT_EXE to override.
if not defined GODOT_EXE set "GODOT_EXE=%USERPROFILE%\Downloads\Godot_v4.4.1-stable_win64.exe\Godot_v4.4.1-stable_win64.exe"

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

:: Check Godot (the export is part of the build - a zip without a fresh
:: client is the March 2026 mistake: a .pck of the deleted 19-region game).
if not exist "%GODOT_EXE%" (
    echo [ERROR] Godot editor not found at:
    echo         %GODOT_EXE%
    echo         Set GODOT_EXE to the Godot 4.4.1 editor exe and run again.
    pause
    exit /b 1
)

echo [INFO] Project root: %cd%
echo [INFO] Godot:        %GODOT_EXE%
echo.

:: ============================================================
:: PB-4: ONE build stamp. Written BEFORE PyInstaller so the spec ships it
:: inside the frozen server (_internal\build_stamp.json -> /test "version");
:: copied AFTER into the bundle root as build_stamp.txt for launch.bat.
:: ============================================================
echo [INFO] Stamping the build...
set "VERSION="
for /f "usebackq delims=" %%v in (`"%PYTHON%" tools\build_stamp.py`) do set "VERSION=%%v"
if not defined VERSION (
    echo [ERROR] Could not write the build stamp.
    pause
    exit /b 1
)
echo [INFO] Build version: %VERSION%
echo.

:: ============================================================
:: Run PyInstaller (--noconfirm: an existing dist folder is replaced without
:: a prompt this script cannot answer)
:: ============================================================
echo [INFO] Building server executable...
echo.
"%PYTHON%" -m PyInstaller deploy\ink_iron.spec --distpath deploy\dist --workpath deploy\build --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check errors above.
    pause
    exit /b 1
)

"%PYTHON%" tools\build_stamp.py --txt "%DIST%"
if errorlevel 1 (
    echo [ERROR] Could not write build_stamp.txt into the bundle.
    pause
    exit /b 1
)

echo.
echo [INFO] Copying config template...

:: Copy config.txt template
copy /y "deploy\dist_template\config.txt" "%DIST%\config.txt" >nul
if errorlevel 1 (
    echo [WARN] Could not copy config.txt template. Copy it manually.
)

:: Copy launch.bat
copy /y "deploy\launch.bat" "%DIST%\launch.bat" >nul

:: Copy README
copy /y "deploy\README_TESTER.txt" "%DIST%\README_TESTER.txt" >nul

:: ============================================================
:: FA-43 + FA-N84 (slice 13): the licences ship WITH the game.
::
:: The zip carried CC-BY icons (game-icons.net), CC-BY audio and 13
:: OFL font families, and shipped NONE of their notices - while two
:: surfaces in the product (the in-game Settings credits and this
:: README) named THIRD_PARTY_LICENSES.md as though it were there.
::
:: The per-family notices cannot ride the .pck either: Godot's
:: export_filter="all_resources" walks the EditorFileSystem and skips
:: entries it types TextFile, which is what every *-OFL.txt and
:: kenney-license.txt is in the project's own filesystem cache (the
:: .ttf are FontFile and the .json are JSON, which is why THOSE ride).
:: The two extension-less LICENSE files are not scanned at all, so they
:: are renamed on copy. Copying into the zip is the route; widening
:: include_filter to "*.txt" would sweep the whole project.
:: ============================================================
echo [INFO] Copying third-party licences...
set "_LIC=%DIST%\licenses"
set "_ASSETS=godot-client\project-sovereign\assets"
if not exist "%_LIC%\fonts\" mkdir "%_LIC%\fonts"

copy /y "THIRD_PARTY_LICENSES.md" "%DIST%\THIRD_PARTY_LICENSES.md" >nul
if errorlevel 1 echo [WARN] THIRD_PARTY_LICENSES.md not copied - the credits screen and README both name it.

:: No /s: the OFL files are all at one level, and xcopy /s /i succeeds
:: silently on an empty match, which would leave the folder empty at
:: errorlevel 0 if the files were ever renamed.
copy /y "%_ASSETS%\fonts\*-OFL.txt" "%_LIC%\fonts\" >nul
if errorlevel 1 echo [WARN] OFL font licences not copied - 13 families ship without their notice.

copy /y "%_ASSETS%\ui\bars\kenney-license.txt" "%_LIC%\kenney-license.txt" >nul
if errorlevel 1 echo [WARN] kenney-license.txt not copied.

copy /y "%_ASSETS%\ui\icons\phosphor\LICENSE" "%_LIC%\phosphor-LICENSE.txt" >nul
if errorlevel 1 echo [WARN] phosphor LICENSE not copied.

copy /y "%_ASSETS%\ui\icons\game-icons\LICENSE" "%_LIC%\game-icons-LICENSE.txt" >nul
if errorlevel 1 echo [WARN] game-icons LICENSE not copied - the CC-BY attribution obligation is LIVE.

:: ============================================================
:: PB-1's done-when: boot the FROZEN server before anything is zipped.
:: The March pipeline never ran the exe it built, which is how a server
:: that died at import shipped. On a spare port, a throw-away save folder.
:: ============================================================
echo.
echo [INFO] Smoke: booting the frozen server...
"%PYTHON%" tools\release_smoke.py --dist "%DIST%" --port 8099 --expect-version "%VERSION%"
if errorlevel 1 (
    echo.
    echo [ERROR] The frozen server failed its smoke. Nothing was zipped.
    pause
    exit /b 1
)

:: ============================================================
:: The Godot client: a FRESH export, release template, of the CURRENT game
:: (PB-6: the March build was a debug export of the pre-cutover world). The
:: import pass first, so every asset is in the editor's cache before the
:: export.
:: ============================================================
echo.
echo [INFO] Importing the Godot project (first run can take a few minutes)...
"%GODOT_EXE%" --headless --path "%GODOT_PROJECT%" --import >nul 2>&1
echo [INFO] Exporting the Godot client (release)...
"%GODOT_EXE%" --headless --path "%GODOT_PROJECT%" --export-release "Windows Desktop" "%DIST%\InkAndIron.exe"
if errorlevel 1 (
    echo.
    echo [ERROR] The Godot export failed. Check errors above.
    pause
    exit /b 1
)
if not exist "%DIST%\InkAndIron.exe" (
    echo [ERROR] The export produced no InkAndIron.exe.
    pause
    exit /b 1
)
if not exist "%DIST%\InkAndIron.pck" (
    echo [ERROR] The export produced no InkAndIron.pck.
    pause
    exit /b 1
)

:: The .pck must carry every JSON the boot reads (the row's done-when).
echo [INFO] Verifying the exported pack...
"%PYTHON%" tools\list_pck.py "%DIST%\InkAndIron.pck" --quiet --require res://assets/maps/europe.json res://assets/maps/europe_1805.json res://assets/maps/tutorial_1805.json res://scenes/main_menu.tscn res://scenes/main.tscn
if errorlevel 1 (
    echo.
    echo [ERROR] The exported .pck is missing files the game reads. Nothing was zipped.
    pause
    exit /b 1
)

:: ============================================================
:: The zip. PB-6: the stale March zip sat under the new zip's name; every
:: old zip is removed first and the new one carries the build version.
:: ============================================================
echo.
echo [INFO] Zipping...
del /q "deploy\dist\ink_iron_*.zip" >nul 2>&1
del /q "deploy\dist\ink_iron_server.zip" >nul 2>&1
set "ZIP=%cd%\deploy\dist\ink_iron_%VERSION%.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%DIST%' -DestinationPath '%ZIP%' -CompressionLevel Optimal -Force"
if errorlevel 1 (
    echo [ERROR] Zipping failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETE - %VERSION%
echo ============================================================
echo.
echo Bundle: %DIST%\
echo Zip:    %ZIP%
echo.
echo Verified: the frozen server booted, played a turn and logged; the
echo .pck carries the maps and the scenes; the licences are in licenses\.
echo.
echo Next steps:
echo   1. Smoke it yourself: unzip the zip somewhere else and run launch.bat
echo      WITHOUT editing config.txt - the game must boot and play in
echo      mock mode with no key
echo   2. Upload the zip to itch.io (public or restricted - your call)
echo   3. The first outside player's launch is the no-Python confirmation
echo.
pause
