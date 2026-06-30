import json
import zipfile
from pathlib import Path

from tina_codex_assistant.app_service import TinaCodexService


def make_plugin_zip(path: Path) -> None:
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
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(".agents/plugins/marketplace.json", json.dumps(marketplace))
        archive.writestr("plugins/browser/.codex-plugin/plugin.json", "{}")


def test_quick_repair_returns_status_and_injection_result(tmp_path):
    plugin_zip = tmp_path / "plugin.zip"
    make_plugin_zip(plugin_zip)
    service = TinaCodexService(plugin_zip=plugin_zip, env={"USERPROFILE": str(tmp_path)})

    result = service.quick_repair(timestamp="20260630-120000")

    assert result["mode"] == "quick_repair"
    assert result["ok"] is True
    assert result["recommended_plugins"] == ["browser"]
    assert result["cooper_detected"] is False
    assert result["plan"][0]["key"] == "check_codex_gui"


def test_full_install_returns_dependency_plan_without_running_windows_commands(tmp_path):
    plugin_zip = tmp_path / "plugin.zip"
    make_plugin_zip(plugin_zip)
    service = TinaCodexService(
        plugin_zip=plugin_zip,
        env={"USERPROFILE": str(tmp_path)},
        codex_gui_found=False,
        codex_cli_found=False,
        git_found=False,
    )

    result = service.full_install(timestamp="20260630-120000", execute_commands=False)

    keys = [item["key"] for item in result["plan"]]
    assert result["mode"] == "full_install"
    assert result["ok"] is True
    assert "install_codex_gui" in keys
    assert "install_git" in keys
    assert "install_codex_cli" in keys
    assert result["recommended_plugins"] == ["browser"]
