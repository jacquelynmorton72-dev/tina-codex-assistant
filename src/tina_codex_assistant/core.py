from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MARKETPLACE_NAME = "tina-codex-plugins"
MARKETPLACE_DISPLAY_NAME = "Tina-codex 中文插件"

DEFAULT_RECOMMENDED_PLUGINS = {
    "browser",
    "chrome",
    "github",
    "superpowers",
    "openai-developers",
    "codex-security",
    "data-analytics",
    "documents",
    "pdf",
    "spreadsheets",
    "presentations",
}


@dataclass(frozen=True)
class CodexPaths:
    codex_home: Path
    agents_home: Path
    config_toml: Path
    personal_marketplace: Path
    tina_marketplace_root: Path


@dataclass(frozen=True)
class CooperDetection:
    has_cooper: bool
    markers: list[str]


def resolve_codex_paths(env: dict[str, str] | None = None) -> CodexPaths:
    source = env or os.environ
    user_home = Path(source.get("USERPROFILE") or source.get("HOME") or Path.home()).expanduser()
    codex_home = Path(source.get("CODEX_HOME", user_home / ".codex")).expanduser()
    agents_home = user_home / ".agents"
    return CodexPaths(
        codex_home=codex_home,
        agents_home=agents_home,
        config_toml=codex_home / "config.toml",
        personal_marketplace=agents_home / "plugins" / "marketplace.json",
        tina_marketplace_root=codex_home / MARKETPLACE_NAME,
    )


def detect_cooper_config(config_text: str) -> CooperDetection:
    markers: list[str] = []
    if re.search(r'(?m)^\s*model_provider\s*=\s*["\']?cooper["\']?\s*$', config_text):
        markers.append("model_provider = cooper")
    if re.search(r"(?m)^\s*\[model_providers\.cooper\]\s*$", config_text):
        markers.append("model_providers.cooper")
    if "cooper-api.com" in config_text.lower():
        markers.append("cooper-api.com")
    return CooperDetection(has_cooper=bool(markers), markers=markers)


def backup_file(path: Path, timestamp: str) -> Path | None:
    if not path.exists():
        return None
    backup_path = path.with_name(f"{path.name}.bak-{timestamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def clean_marketplace(marketplace: dict) -> dict:
    cleaned = dict(marketplace)
    cleaned["name"] = MARKETPLACE_NAME
    interface = dict(cleaned.get("interface") or {})
    interface["displayName"] = MARKETPLACE_DISPLAY_NAME
    cleaned["interface"] = interface
    return cleaned


def select_recommended_plugins(
    marketplace: dict,
    allowlist: Iterable[str] = DEFAULT_RECOMMENDED_PLUGINS,
) -> list[str]:
    allowed = set(allowlist)
    return [plugin["name"] for plugin in marketplace.get("plugins", []) if plugin.get("name") in allowed]


def ensure_local_marketplace_config(config_path: Path, marketplace_root: Path) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text(encoding="utf-8", errors="replace") if config_path.exists() else ""
    cleaned = _remove_tina_marketplace_block(existing).rstrip()
    block = "\n".join(
        [
            f"[marketplaces.{MARKETPLACE_NAME}]",
            'source = "local"',
            f'path = "{marketplace_root.as_posix()}"',
        ]
    )
    new_text = f"{cleaned}\n\n{block}\n" if cleaned else f"{block}\n"
    config_path.write_text(new_text, encoding="utf-8")


def _remove_tina_marketplace_block(config_text: str) -> str:
    header = f"[marketplaces.{MARKETPLACE_NAME}]"
    lines = config_text.splitlines()
    result: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            skipping = True
            continue
        if skipping and stripped.startswith("[") and stripped.endswith("]"):
            skipping = False
        if not skipping:
            result.append(line)
    return "\n".join(result)
