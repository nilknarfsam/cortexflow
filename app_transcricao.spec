# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — CortexFlow Desktop (one-file).

Dados do usuário (settings, fila, cache) NÃO são empacotados: criados em
``<pasta_do_exe>/data/`` na primeira execução (ver settings_service.py).
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

project_root = Path(SPECPATH)

# Assets de UI — CustomTkinter (temas/fontes) e tkinterdnd2 (tkdnd + DLLs)
datas = collect_data_files("customtkinter") + collect_data_files("tkinterdnd2")

hiddenimports = [
    "customtkinter",
    "tkinterdnd2",
    "PIL",
    "PIL._tkinter_finder",
    "whisper",
    "torch",
    "torchaudio",
    "tiktoken",
    "tiktoken_ext",
    "tiktoken_ext.openai_public",
    "pdfplumber",
    "docx",
    "openpyxl",
    "pytesseract",
    "src",
    "src.core",
    "src.models",
    "src.ui",
    "src.ui.design",
    "src.ui.components",
    "src.ui.legacy_ui",
    "src.ai_ready",
    "src.cache",
    "src.library",
    "src.semantic",
    "src.study",
    "src.datasets",
    "src.knowledge_graph",
    "src.knowledge",
] + collect_submodules("src")

a = Analysis(
    [str(project_root / "app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "scipy",
        "pandas",
        "notebook",
        "pytest",
        "IPython",
        "tkinter.test",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="CortexFlow",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
