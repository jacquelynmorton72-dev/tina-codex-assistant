import json
import zipfile
from pathlib import Path

from tina_codex_assistant.injector import inject_plugins


def make_plugin_zip(path: Path) -> None:
    marketplace = {
        "name": "cooper-plugins",
        "plugins": [
            {
                "name": "browser",
                "source": {"source": "local", "path": "./plugins/browser"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            },
            {
                "name": "gmail",
                "source": {"source": "local", "path": "./plugins/gmail"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Communication",
            },
        ],
    }
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(".agents/plugins/marketplace.json", json.dumps(marketplace))
        archive.writestr("plugins/browser/.codex-plugin/plugin.json", "{}")
        archive.writestr("plugins/gmail/.codex-plugin/plugin.json", "{}")


def test_inject_plugins_copies_clean_marketplace_and_preserves_config(tmp_path):
    plugin_zip = tmp_path / "plugin.zip"
    make_plugin_zip(plugin_zip)
    codex_home = tmp_path / ".codex"
    agents_home = tmp_path / ".agents"
    config = codex_home / "config.toml"
    config.parent.mkdir()
    config.write_text('model_provider = "custom"\n', encoding="utf-8")

    result = inject_plugins(
        plugin_zip=plugin_zip,
        codex_home=codex_home,
        agents_home=agents_home,
        timestamp="20260630-120000",
    )

    marketplace_path = codex_home / "tina-codex-plugins" / ".agents" / "plugins" / "marketplace.json"
    personal_marketplace = agents_home / "plugins" / "marketplace.json"
    cleaned = json.loads(marketplace_path.read_text(encoding="utf-8"))

    assert result.marketplace_root == codex_home / "tina-codex-plugins"
    assert result.recommended_plugins == ["browser"]
    assert result.cooper_detected is False
    assert cleaned["name"] == "tina-codex-plugins"
    assert cleaned["interface"]["displayName"] == "Tina-codex 中文插件"
    assert personal_marketplace.read_text(encoding="utf-8") == marketplace_path.read_text(encoding="utf-8")
    config_text = config.read_text(encoding="utf-8")
    assert 'model_provider = "custom"' in config_text
    assert "[marketplaces.tina-codex-plugins]" in config_text
    assert f'path = "{(codex_home / "tina-codex-plugins").as_posix()}"' in config_text


def test_inject_plugins_backs_up_existing_marketplace_and_reports_cooper(tmp_path):
    plugin_zip = tmp_path / "plugin.zip"
    make_plugin_zip(plugin_zip)
    codex_home = tmp_path / ".codex"
    agents_home = tmp_path / ".agents"
    old_marketplace = agents_home / "plugins" / "marketplace.json"
    old_marketplace.parent.mkdir(parents=True)
    old_marketplace.write_text('{"name":"old"}', encoding="utf-8")
    codex_home.mkdir()
    (codex_home / "config.toml").write_text(
        'model_provider = "cooper"\n[model_providers.cooper]\nbase_url = "https://cooper-api.com/v1"\n',
        encoding="utf-8",
    )

    result = inject_plugins(
        plugin_zip=plugin_zip,
        codex_home=codex_home,
        agents_home=agents_home,
        timestamp="20260630-120000",
    )

    assert old_marketplace.with_name("marketplace.json.bak-20260630-120000") in result.backups
    assert (codex_home / "config.toml.bak-20260630-120000") in result.backups
    assert result.cooper_detected is True
    assert result.cooper_markers == ["model_provider = cooper", "model_providers.cooper", "cooper-api.com"]
