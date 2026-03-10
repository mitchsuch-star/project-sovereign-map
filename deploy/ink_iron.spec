# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Ink & Iron backend server
# Build with: pyinstaller deploy/ink_iron.spec --distpath deploy/dist --workpath deploy/build --clean

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Project root (one level up from deploy/)
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

# Collect full packages that have dynamic imports
uvicorn_datas, uvicorn_binaries, uvicorn_hiddenimports = collect_all('uvicorn')
fastapi_datas, fastapi_binaries, fastapi_hiddenimports = collect_all('fastapi')
starlette_datas, starlette_binaries, starlette_hiddenimports = collect_all('starlette')

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
    # Pydantic v2
    'pydantic',
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'pydantic_core',
    # HTTP / API clients
    'httpx',
    'httpx._transports',
    'httpx._transports.default',
    'httpcore',
    'h11',
    'anthropic',
    # Dotenv
    'dotenv',
    # Fuzzy matching
    'fuzzywuzzy',
    'fuzzywuzzy.fuzz',
    'fuzzywuzzy.process',
    'Levenshtein',
    # Backend package (ensure all submodules found)
    'backend',
    'backend.main',
    'backend.commands',
    'backend.commands.parser',
    'backend.commands.executor',
    'backend.commands.disobedience',
    'backend.commands.objection_v2',
    'backend.commands.defiance',
    'backend.commands.strategic',
    'backend.commands.vindication',
    'backend.commands.diplomatic_defiance',
    'backend.models',
    'backend.models.marshal',
    'backend.models.world_state',
    'backend.models.region',
    'backend.models.personality',
    'backend.models.personality_modifiers',
    'backend.models.diplomat',
    'backend.models.intel',
    'backend.game_logic',
    'backend.game_logic.combat',
    'backend.game_logic.battle_report',
    'backend.game_logic.relationship',
    'backend.game_logic.turn_manager',
    'backend.game_logic.diplomacy',
    'backend.game_logic.ai_diplomacy',
    'backend.game_logic.diplomatic_advisory',
    'backend.game_logic.coalition',
    'backend.game_logic.diplomatic_ledger',
    'backend.game_logic.vassal',
    'backend.game_logic.dispatch',
    'backend.game_logic.ledger',
    'backend.game_logic.marshal_overview',
    'backend.ai',
    'backend.ai.llm_client',
    'backend.ai.enemy_ai',
    'backend.ai.strategic_parser',
    'backend.ai.validation',
    'backend.ai.prompt_builder',
    'backend.campaign_log',
    'backend.intel_report',
    'backend.notifications',
    'backend.save_manager',
]

# Merge all collected hidden imports
all_hidden = list(set(
    hidden_imports
    + uvicorn_hiddenimports
    + fastapi_hiddenimports
    + starlette_hiddenimports
    + collect_submodules('backend')
    + collect_submodules('anthropic')
    + collect_submodules('httpx')
    + collect_submodules('pydantic')
))

# Data files
all_datas = uvicorn_datas + fastapi_datas + starlette_datas
all_binaries = uvicorn_binaries + fastapi_binaries + starlette_binaries

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
