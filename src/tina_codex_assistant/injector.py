from __future__ import annotations

import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .core import (
    MARKETPLACE_NAME,
    backup_file,
    clean_marketplace,
    detect_cooper_config,
    ensure_local_marketplace_config,
    select_recommended_plugins,
)


@dataclass(frozen=True)
class InjectionResult:
    marketplace_root: Path
    personal_marketplace: Path
    recommended_plugins: list[str]
    backups: list[Path]
    cooper_detected: bool
    cooper_markers: list[str]


def inject_plugins(
    plugin_zip: Path,
    codex_home: Path,
    agents_home: Path,
    timestamp: str,
) -> InjectionResult:
    codex_home.mkdir(parents=True, exist_ok=True)
    marketplace_root = codex_home / MARKETPLACE_NAME
    personal_marketplace = agents_home / "plugins" / "marketplace.json"
    backups: list[Path] = []

    config_path = codex_home / "config.toml"
    cooper_markers: list[str] = []
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8", errors="replace")
        detection = detect_cooper_config(config_text)
        cooper_markers = detection.markers
        config_backup = backup_file(config_path, timestamp)
        if config_backup:
            backups.append(config_backup)

    personal_backup = backup_file(personal_marketplace, timestamp)
    if personal_backup:
        backups.append(personal_backup)

    if marketplace_root.exists():
        marketplace_backup = marketplace_root.with_name(f"{marketplace_root.name}.bak-{timestamp}")
        if marketplace_backup.exists():
            shutil.rmtree(marketplace_backup)
        shutil.copytree(marketplace_root, marketplace_backup)
        backups.append(marketplace_backup)
        shutil.rmtree(marketplace_root)

    with zipfile.ZipFile(plugin_zip) as archive:
        archive.extractall(marketplace_root)

    marketplace_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    cleaned_marketplace = clean_marketplace(marketplace)
    marketplace_path.write_text(
        json.dumps(cleaned_marketplace, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    personal_marketplace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(marketplace_path, personal_marketplace)
    ensure_local_marketplace_config(config_path, marketplace_root)

    return InjectionResult(
        marketplace_root=marketplace_root,
        personal_marketplace=personal_marketplace,
        recommended_plugins=select_recommended_plugins(cleaned_marketplace),
        backups=backups,
        cooper_detected=bool(cooper_markers),
        cooper_markers=cooper_markers,
    )
