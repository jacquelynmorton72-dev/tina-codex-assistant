# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
root = Path.cwd()

# 构建 datas 列表，包含必需资源和可选的离线资源
datas = [
    (str(root / "resources" / "plugin.zip"), "resources"),
    (str(root / "resources" / "statsig-zh-CN-raw-snapshot.json"), "resources"),
    (str(root / "src" / "tina_codex_assistant" / "ui" / "index.html"), "src/tina_codex_assistant/ui"),
]

# 添加离线 Codex GUI 安装包（如果存在）
for ext in [".msixbundle", ".appxbundle", ".msix", ".appx"]:
    gui_pkg = root / "resources" / f"codex-gui{ext}"
    if gui_pkg.exists():
        datas.append((str(gui_pkg), "resources"))
        print(f"✓ 包含离线资源: {gui_pkg.name}")
        break

# 添加离线 Codex CLI 资源（如果存在）
cli_dir = root / "resources" / "codex-cli"
if cli_dir.exists():
    install_sh = cli_dir / "install.sh"
    tarball = cli_dir / "codex-linux-x64.tar.gz"
    if install_sh.exists() and tarball.exists():
        datas.append((str(cli_dir), "resources/codex-cli"))
        print(f"✓ 包含离线资源: codex-cli/")

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
