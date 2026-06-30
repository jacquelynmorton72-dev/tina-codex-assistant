from __future__ import annotations

import argparse
import json

from .app_service import TinaCodexService
from .resources import bundled_plugin_zip


def main() -> int:
    parser = argparse.ArgumentParser(prog="tina-codex")
    parser.add_argument("mode", choices=["quick-repair", "full-install", "ui"])
    parser.add_argument("--dry-run", action="store_true", help="Do not run Windows install commands.")
    args = parser.parse_args()

    if args.mode == "ui":
        from .ui_app import main as ui_main

        ui_main()
        return 0

    service = TinaCodexService(plugin_zip=bundled_plugin_zip())
    if args.mode == "quick-repair":
        result = service.quick_repair()
    else:
        result = service.full_install(execute_commands=not args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

