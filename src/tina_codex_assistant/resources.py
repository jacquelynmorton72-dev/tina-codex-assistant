from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def bundled_plugin_zip() -> Path:
    return app_root() / "resources" / "plugin.zip"


def bundled_ui_html() -> Path:
    return app_root() / "src" / "tina_codex_assistant" / "ui" / "index.html"

