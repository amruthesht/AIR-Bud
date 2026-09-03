# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AIR-Bud.
Builds a standalone executable for Windows/Mac/Linux.
"""
import sys
from pathlib import Path

block_cipher = None

# Collect all system prompts
system_prompts = []
prompts_dir = Path("system_prompts")
if prompts_dir.exists():
    for f in prompts_dir.glob("*.txt"):
        system_prompts.append(str(f))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('system_prompts/', 'system_prompts/'),
        ('utils/', 'utils/'),
        ('assets/', 'assets/'),
    ],
    hiddenimports=[
        'streamlit',
        'openai',
        'PyPDF2',
        'icalendar',
        'dateutil',
        'cryptography',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'setuptools',
        'tkinter',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AIR-Bud',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
