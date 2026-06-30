import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_bundled_plugin_zip_has_tina_marketplace_name():
    with zipfile.ZipFile(ROOT / "resources" / "plugin.zip") as archive:
        marketplace = json.loads(archive.read(".agents/plugins/marketplace.json"))

    assert marketplace["name"] == "tina-codex-plugins"
    assert marketplace["interface"]["displayName"] == "Tina-codex 中文插件"


def test_bundled_resources_do_not_include_cooper_config():
    with zipfile.ZipFile(ROOT / "resources" / "plugin.zip") as archive:
        names = archive.namelist()
        marketplace_text = archive.read(".agents/plugins/marketplace.json").decode("utf-8")

    assert "fixed_config.toml" not in names
    assert "model_provider = \"cooper\"" not in marketplace_text
    assert "https://cooper-api.com/v1" not in marketplace_text


def test_bundled_resource_metadata_uses_tina_brand():
    with zipfile.ZipFile(ROOT / "resources" / "plugin.zip") as archive:
        readme = archive.read("README.md").decode("utf-8")
        merge_script = archive.read("scripts/merge_and_localize.mjs").decode("utf-8")
        runtime_script = archive.read("scripts/merge_bundled_and_runtime.mjs").decode("utf-8")

    metadata = "\n".join([readme, merge_script, runtime_script])
    assert "Cooper 插件合集" not in metadata
    assert "cooper-plugins" not in metadata
    assert "Tina-codex 中文插件" in metadata
    assert "tina-codex-plugins" in metadata
