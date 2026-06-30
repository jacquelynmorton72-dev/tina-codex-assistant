from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ZIP = ROOT / "resources" / "plugin.zip"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(PLUGIN_ZIP) as archive:
            archive.extractall(tmp_path)

        marketplace_path = tmp_path / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["name"] = "tina-codex-plugins"
        interface = dict(marketplace.get("interface") or {})
        interface["displayName"] = "Tina-codex 中文插件"
        marketplace["interface"] = interface
        marketplace_path.write_text(
            json.dumps(marketplace, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        replacements = {
            "Cooper 插件合集": "Tina-codex 中文插件",
            "cooper-plugins": "tina-codex-plugins",
            "cooperRoot": "tinaRoot",
        }
        for relative in [
            "README.md",
            "scripts/merge_and_localize.mjs",
            "scripts/merge_bundled_and_runtime.mjs",
        ]:
            text_path = tmp_path / relative
            text = text_path.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            text_path.write_text(text, encoding="utf-8")

        backup = PLUGIN_ZIP.with_suffix(".zip.bak")
        shutil.copy2(PLUGIN_ZIP, backup)
        with zipfile.ZipFile(PLUGIN_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(tmp_path.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp_path).as_posix())

    print(f"prepared {PLUGIN_ZIP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
