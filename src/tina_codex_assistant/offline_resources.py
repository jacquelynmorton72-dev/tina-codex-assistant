from __future__ import annotations

from pathlib import Path

from .resources import resource_path


def get_offline_codex_gui() -> Path | None:
    """获取离线 Codex GUI 安装包路径

    Returns:
        Path 或 None: 如果找到离线安装包返回路径，否则返回 None
    """
    candidates = [
        "codex-gui.msixbundle",
        "codex-gui.appxbundle",
        "codex-gui.msix",
        "codex-gui.appx",
    ]
    for name in candidates:
        path = resource_path(name)
        if path and path.exists():
            return path
    return None


def get_offline_codex_cli_dir() -> Path | None:
    """获取离线 Codex CLI 资源目录

    Returns:
        Path 或 None: 如果找到离线 CLI 资源返回目录路径，否则返回 None
    """
    cli_dir = resource_path("codex-cli")
    if cli_dir and cli_dir.exists():
        install_sh = cli_dir / "install.sh"
        tarball = cli_dir / "codex-linux-x64.tar.gz"
        if install_sh.exists() and tarball.exists():
            return cli_dir
    return None


def has_offline_resources() -> dict[str, bool]:
    """检查离线资源的可用性

    Returns:
        dict: {"gui": bool, "cli": bool}
    """
    return {
        "gui": get_offline_codex_gui() is not None,
        "cli": get_offline_codex_cli_dir() is not None,
    }
