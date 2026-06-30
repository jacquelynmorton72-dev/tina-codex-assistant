from tina_codex_assistant.windows_installer import (
    InstallAction,
    build_full_install_plan,
    build_quick_repair_plan,
)


def test_quick_repair_plan_only_injects_plugins_when_codex_exists():
    plan = build_quick_repair_plan(codex_cli_found=True, codex_gui_found=True)

    assert plan.actions == [
        InstallAction("check_codex_gui", "Codex GUI 已检测到", []),
        InstallAction("check_codex_cli", "Codex CLI 已检测到", []),
        InstallAction("inject_plugins", "注入 Tina-codex 中文插件市场", []),
        InstallAction("install_recommended_plugins", "安装推荐基础插件组", []),
    ]


def test_quick_repair_plan_reports_missing_codex_without_installing():
    plan = build_quick_repair_plan(codex_cli_found=False, codex_gui_found=False)

    assert [action.key for action in plan.actions] == [
        "check_codex_gui",
        "check_codex_cli",
        "inject_plugins",
        "install_recommended_plugins",
    ]
    assert "未检测到" in plan.actions[0].description
    assert "未检测到" in plan.actions[1].description


def test_full_install_plan_uses_store_codex_and_npmmirror_git():
    plan = build_full_install_plan(codex_cli_found=False, codex_gui_found=False, git_found=False)

    action_map = {action.key: action for action in plan.actions}

    assert "install_codex_gui" in action_map
    assert "install_git" in action_map
    assert "install_codex_cli" in action_map
    assert any("openai.codex" in command for command in action_map["install_codex_gui"].commands)
    assert any("store.rg-adguard.net" in command for command in action_map["install_codex_gui"].commands)
    assert any("registry.npmmirror.com/-/binary/git-for-windows" in command for command in action_map["install_git"].commands)
    assert any("@openai/codex" in command for command in action_map["install_codex_cli"].commands)
    assert any("registry.npmmirror.com" in command for command in action_map["install_codex_cli"].commands)
    assert not any("chatgpt.com" in command for command in action_map["install_codex_cli"].commands)


def test_full_install_plan_skips_installed_dependencies():
    plan = build_full_install_plan(codex_cli_found=True, codex_gui_found=True, git_found=True)

    keys = [action.key for action in plan.actions]

    assert "install_codex_gui" not in keys
    assert "install_git" not in keys
    assert "install_codex_cli" not in keys
    assert keys[-2:] == ["inject_plugins", "install_recommended_plugins"]
