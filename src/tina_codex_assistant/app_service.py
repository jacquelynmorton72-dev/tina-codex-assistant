from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .core import resolve_codex_paths
from .injector import inject_plugins
from .offline_resources import get_offline_codex_cli_dir, get_offline_codex_gui, has_offline_resources
from .windows_installer import (
    InstallPlan,
    build_full_install_plan,
    build_quick_repair_plan,
    detect_codex_cli,
    detect_codex_gui,
    detect_git,
    run_powershell,
)


class TinaCodexService:
    def __init__(
        self,
        plugin_zip: Path,
        env: dict[str, str] | None = None,
        codex_gui_found: bool | None = None,
        codex_cli_found: bool | None = None,
        git_found: bool | None = None,
    ) -> None:
        self.plugin_zip = plugin_zip
        self.env = env
        self._codex_gui_found = codex_gui_found
        self._codex_cli_found = codex_cli_found
        self._git_found = git_found

    def quick_repair(self, timestamp: str | None = None) -> dict:
        paths = resolve_codex_paths(self.env)
        plan = build_quick_repair_plan(
            codex_cli_found=self._detect_codex_cli(),
            codex_gui_found=self._detect_codex_gui(),
        )
        injection = inject_plugins(
            plugin_zip=self.plugin_zip,
            codex_home=paths.codex_home,
            agents_home=paths.agents_home,
            timestamp=timestamp or current_timestamp(),
        )
        return self._result("quick_repair", plan, injection)

    def full_install(self, timestamp: str | None = None, execute_commands: bool = True) -> dict:
        paths = resolve_codex_paths(self.env)

        # 检测离线资源
        offline_gui = get_offline_codex_gui()
        offline_cli_dir = get_offline_codex_cli_dir()
        offline_status = has_offline_resources()

        plan = build_full_install_plan(
            codex_cli_found=self._detect_codex_cli(),
            codex_gui_found=self._detect_codex_gui(),
            git_found=self._detect_git(),
            offline_gui_pkg=offline_gui,
            offline_cli_dir=offline_cli_dir,
        )
        command_results: list[dict] = []
        if execute_commands:
            command_results = execute_plan_commands(plan)
        injection = inject_plugins(
            plugin_zip=self.plugin_zip,
            codex_home=paths.codex_home,
            agents_home=paths.agents_home,
            timestamp=timestamp or current_timestamp(),
        )
        result = self._result("full_install", plan, injection)
        result["command_results"] = command_results
        result["offline_resources"] = offline_status
        return result

    def _detect_codex_gui(self) -> bool:
        return detect_codex_gui() if self._codex_gui_found is None else self._codex_gui_found

    def _detect_codex_cli(self) -> bool:
        return detect_codex_cli() if self._codex_cli_found is None else self._codex_cli_found

    def _detect_git(self) -> bool:
        return detect_git() if self._git_found is None else self._git_found

    @staticmethod
    def _result(mode: str, plan: InstallPlan, injection) -> dict:
        return {
            "mode": mode,
            "ok": True,
            "plan": [action.__dict__ for action in plan.actions],
            "marketplace_root": str(injection.marketplace_root),
            "personal_marketplace": str(injection.personal_marketplace),
            "recommended_plugins": injection.recommended_plugins,
            "backups": [str(path) for path in injection.backups],
            "cooper_detected": injection.cooper_detected,
            "cooper_markers": injection.cooper_markers,
            "message": "模型服务未被写入，请在 Codex 设置中自行配置 OpenAI 登录、API Key 或自定义 provider。",
        }


def current_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def execute_plan_commands(plan: InstallPlan) -> list[dict]:
    results: list[dict] = []
    for action in plan.actions:
        for command in action.commands:
            completed = run_powershell(command)
            results.append(
                {
                    "action": action.key,
                    "command": command,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            )
            if completed.returncode != 0:
                return results
    return results
