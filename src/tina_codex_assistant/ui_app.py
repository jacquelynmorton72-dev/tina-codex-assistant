from __future__ import annotations

import json

from .app_service import TinaCodexService
from .resources import bundled_plugin_zip, bundled_ui_html


class Api:
    def __init__(self) -> None:
        self.service = TinaCodexService(plugin_zip=bundled_plugin_zip())

    def quick_repair(self) -> str:
        return json.dumps(self.service.quick_repair(), ensure_ascii=False)

    def full_install(self) -> str:
        return json.dumps(self.service.full_install(execute_commands=True), ensure_ascii=False)

    def full_install_dry_run(self) -> str:
        return json.dumps(self.service.full_install(execute_commands=False), ensure_ascii=False)


def main() -> None:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("pywebview 未安装。请运行 `pip install pywebview` 或使用 PyInstaller 打包版本。") from exc

    html_path = bundled_ui_html()
    webview.create_window(
        "Tina-codex助手",
        html_path.as_uri(),
        js_api=Api(),
        width=980,
        height=720,
        min_size=(760, 560),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()

