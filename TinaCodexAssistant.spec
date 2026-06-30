# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
root = Path.cwd()

datas = [
    (str(root / "resources" / "plugin.zip"), "resources"),
    (str(root / "resources" / "statsig-zh-CN-raw-snapshot.json"), "resources"),
    (str(root / "src" / "tina_codex_assistant" / "ui" / "index.html"), "src/tina_codex_assistant/ui"),
]

a = Analysis(
    ["src/tina_codex_assistant/cli.py"],
    pathex=[str(root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=["webview"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="Tina-codex助手",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
