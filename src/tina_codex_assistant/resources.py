from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: str) -> Path | None:
    """获取资源文件路径

    Args:
        relative_path: 相对于 resources/ 的路径，如 "plugin.zip" 或 "codex-cli/install.sh"

    Returns:
        Path 或 None: 资源路径，如果不存在返回 None
    """
    base = app_root() / "resources"
    path = base / relative_path
    return path if path.exists() else None


def bundled_plugin_zip() -> Path:
    return app_root() / "resources" / "plugin.zip"


def bundled_ui_html() -> Path:
    return app_root() / "src" / "tina_codex_assistant" / "ui" / "index.html"

