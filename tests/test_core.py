import json
from pathlib import Path

import pytest

from tina_codex_assistant.core import (
    DEFAULT_RECOMMENDED_PLUGINS,
    CodexPaths,
    backup_file,
    clean_marketplace,
    detect_cooper_config,
    ensure_local_marketplace_config,
    resolve_codex_paths,
    select_recommended_plugins,
)


def test_resolve_codex_paths_uses_codex_home_env(tmp_path, monkeypatch):
    codex_home = tmp_path / "custom-codex"
    home = tmp_path / "home"
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("USERPROFILE", str(home))

    paths = resolve_codex_paths()

    assert paths == CodexPaths(
        codex_home=codex_home,
        agents_home=home / ".agents",
        config_toml=codex_home / "config.toml",
        personal_marketplace=home / ".agents" / "plugins" / "marketplace.json",
        tina_marketplace_root=codex_home / "tina-codex-plugins",
    )


def test_resolve_codex_paths_defaults_to_userprofile(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setenv("USERPROFILE", str(home))

    paths = resolve_codex_paths()

    assert paths.codex_home == home / ".codex"
    assert paths.agents_home == home / ".agents"


def test_detect_cooper_config_finds_legacy_provider():
    config = """
model = "gpt-5.5"
model_provider = "cooper"

[model_providers.cooper]
base_url = "https://cooper-api.com/v1"
"""

    result = detect_cooper_config(config)

    assert result.has_cooper is True
    assert result.markers == ["model_provider = cooper", "model_providers.cooper", "cooper-api.com"]


def test_detect_cooper_config_ignores_normal_custom_provider():
    config = """
model = "gpt-5"

[model_providers.proxy]
base_url = "https://example.invalid/v1"
env_key = "OPENAI_API_KEY"
"""

    result = detect_cooper_config(config)

    assert result.has_cooper is False
    assert result.markers == []


def test_backup_file_copies_existing_file_with_timestamp(tmp_path):
    source = tmp_path / "config.toml"
    source.write_text("model = \"gpt-5\"\n", encoding="utf-8")

    backup = backup_file(source, timestamp="20260630-120000")

    assert backup == tmp_path / "config.toml.bak-20260630-120000"
    assert backup.read_text(encoding="utf-8") == "model = \"gpt-5\"\n"
    assert source.read_text(encoding="utf-8") == "model = \"gpt-5\"\n"


def test_backup_file_returns_none_when_missing(tmp_path):
    assert backup_file(tmp_path / "missing.toml", timestamp="20260630-120000") is None


def test_clean_marketplace_renames_without_changing_plugin_rules():
    marketplace = {
        "name": "cooper-plugins",
        "plugins": [
            {
                "name": "browser",
                "source": {"source": "local", "path": "./plugins/browser"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            }
        ],
    }

    cleaned = clean_marketplace(marketplace)

    assert cleaned["name"] == "tina-codex-plugins"
    assert cleaned["interface"]["displayName"] == "Tina-codex 中文插件"
    assert cleaned["plugins"] == marketplace["plugins"]
    assert "cooper" not in json.dumps(cleaned, ensure_ascii=False).lower()


def test_select_recommended_plugins_returns_only_present_defaults():
    marketplace = {
        "plugins": [
            {"name": "browser"},
            {"name": "gmail"},
            {"name": "github"},
            {"name": "superpowers"},
            {"name": "stripe"},
        ]
    }

    selected = select_recommended_plugins(marketplace)

    assert selected == ["browser", "github", "superpowers"]
    assert "gmail" not in selected
    assert "stripe" not in selected
    assert set(selected).issubset(DEFAULT_RECOMMENDED_PLUGINS)


def test_select_recommended_plugins_can_use_custom_allowlist():
    marketplace = {"plugins": [{"name": "browser"}, {"name": "figma"}]}

    assert select_recommended_plugins(marketplace, allowlist={"figma"}) == ["figma"]


def test_ensure_local_marketplace_config_appends_without_changing_model_settings(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text(
        'model = "gpt-5"\nmodel_provider = "custom"\n\n[model_providers.custom]\nbase_url = "https://example.invalid/v1"\n',
        encoding="utf-8",
    )

    ensure_local_marketplace_config(config, tmp_path / ".codex" / "tina-codex-plugins")

    text = config.read_text(encoding="utf-8")
    assert 'model_provider = "custom"' in text
    assert "[model_providers.custom]" in text
    assert "[marketplaces.tina-codex-plugins]" in text
    assert 'source = "local"' in text
    assert f'path = "{(tmp_path / ".codex" / "tina-codex-plugins").as_posix()}"' in text


def test_ensure_local_marketplace_config_replaces_existing_tina_block(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text(
        '[marketplaces.tina-codex-plugins]\nsource = "local"\npath = "old"\n\n[features]\nplugins = true\n',
        encoding="utf-8",
    )

    ensure_local_marketplace_config(config, tmp_path / "new-root")

    text = config.read_text(encoding="utf-8")
    assert text.count("[marketplaces.tina-codex-plugins]") == 1
    assert 'path = "old"' not in text
    assert 'path = "' + (tmp_path / "new-root").as_posix() + '"' in text
    assert "[features]\nplugins = true" in text
