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
set "_LIC=deploy\dist\ink_iron_server\licenses"
set "_ASSETS=godot-client\project-sovereign\assets"
if not exist "%_LIC%\fonts\" mkdir "%_LIC%\fonts"

copy /y "THIRD_PARTY_LICENSES.md" "deploy\dist\ink_iron_server\THIRD_PARTY_LICENSES.md" >nul
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
