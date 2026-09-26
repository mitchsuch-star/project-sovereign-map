# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the Ink & Iron backend server (the release build,
# regenerated September 25, 2026 — it had predated the July-18 SDK migration).
#
# Build with (deploy/build.bat does all of this, plus the export and the smoke):
#   pyinstaller deploy/ink_iron.spec --distpath deploy/dist --workpath deploy/build --clean --noconfirm
#
# What the frozen server needs beyond what a static import scan finds:
#   - the three map JSONs the boot HARD-REQUIRES (see the datas block);
#   - the build stamp (PB-4) — written by tools/build_stamp.py before the
#     build, shipped at the bundle's _MEIPASS root (= _internal\), read by
#     backend/build_info.py;
#   - uvicorn / fastapi / starlette submodules, which are imported by name at
#     runtime (collect_all);
#   - the Anthropic SDK (July-18 migration: the live parser goes through the
#     official `anthropic` package, not raw HTTP) and its transport stack —
#     httpx / httpcore / h11 / anyio / sniffio / jiter / distro — all static
#     imports, listed as hidden imports anyway so a lazy import inside the SDK
#     cannot drop one.

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Project root (one level up from deploy/)
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect full packages that have dynamic imports
uvicorn_datas, uvicorn_binaries, uvicorn_hiddenimports = collect_all('uvicorn')
fastapi_datas, fastapi_binaries, fastapi_hiddenimports = collect_all('fastapi')
starlette_datas, starlette_binaries, starlette_hiddenimports = collect_all('starlette')
anthropic_datas, anthropic_binaries, anthropic_hiddenimports = collect_all('anthropic')

# Hidden imports PyInstaller commonly misses
hidden_imports = [
    # Uvicorn internals
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    # FastAPI / Starlette
    'fastapi',
    'starlette',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
    # Async
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'sniffio',
    # Pydantic v2
    'pydantic',
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'pydantic_core',
    # HTTP / the Anthropic SDK's transport
    'httpx',
    'httpx._transports',
    'httpx._transports.default',
    'httpcore',
    'h11',
    'certifi',
    'jiter',
    'distro',
    'anthropic',
    'anthropic.types',
    # Dotenv
    'dotenv',
    # Fuzzy matching
    'fuzzywuzzy',
    'fuzzywuzzy.fuzz',
    'fuzzywuzzy.process',
    'Levenshtein',
    # The backend package — every submodule, collected below as well
    'backend',
    'backend.main',
    'backend.build_info',
    'backend.runtime_log',
    'backend.save_manager',
    'backend.campaign_log',
    'backend.intel_report',
    'backend.notifications',
    'backend.display_names',
]

# Merge all collected hidden imports
all_hidden = list(set(
    hidden_imports
    + uvicorn_hiddenimports
    + fastapi_hiddenimports
    + starlette_hiddenimports
    + anthropic_hiddenimports
    + collect_submodules('backend')
    + collect_submodules('anthropic')
    + collect_submodules('httpx')
    + collect_submodules('pydantic')
))

# Data files
all_datas = uvicorn_datas + fastapi_datas + starlette_datas + anthropic_datas

# Aug 2026 health-check audit (shippable-build P0-1): since the July-2 map
# cutover the backend HARD-REQUIRES three JSONs at repo-relative paths —
# europe.json (the region registry, backend/models/region.py) plus the
# europe_1805.json default scenario and tutorial_1805.json (backend/main.py).
# Under PyInstaller they resolve inside _internal/ from region.py's own
# __file__ (PB-1: main.py is the ENTRY script, whose __file__ is
# _internal\main.py, so the maps folder is derived from region.py, an
# IMPORTED module whose __file__ mirrors the repo layout in both worlds).
_MAPS_SRC = os.path.join(
    PROJECT_ROOT, 'godot-client', 'project-sovereign', 'assets', 'maps')
_MAPS_DST = os.path.join(
    'godot-client', 'project-sovereign', 'assets', 'maps')
for _map_file in ('europe.json', 'europe_1805.json', 'tutorial_1805.json'):
    all_datas.append((os.path.join(_MAPS_SRC, _map_file), _MAPS_DST))

# PB-4: the build stamp, at the _MEIPASS root. Absent in a hand-run
# PyInstaller (build_info then reports "unknown" and the smoke refuses it) —
# deploy/build.bat writes it first.
_STAMP = os.path.join(PROJECT_ROOT, 'deploy', 'build_stamp.json')
if os.path.exists(_STAMP):
    all_datas.append((_STAMP, '.'))

all_binaries = (uvicorn_binaries + fastapi_binaries + starlette_binaries
                + anthropic_binaries)

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'backend', 'main.py')],
    pathex=[PROJECT_ROOT],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest', 'pytest_cov', 'ruff',
        'tkinter', 'matplotlib', 'numpy', 'pandas',
        'PIL', 'scipy', 'IPython', 'notebook',
        'tests', 'tools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ink_iron_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ink_iron_server',
)
