from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_build_script_documents_exe_output():
    script = ROOT / "scripts" / "build-windows.ps1"
    text = script.read_text(encoding="utf-8")

    assert "TinaCodexAssistant.spec" in text
    assert "pyinstaller" in text.lower()
    assert "dist\\Tina-codex助手.exe" in text
    assert "resources\\plugin.zip" in text


def test_windows_readme_contains_user_steps():
    readme = ROOT / "WINDOWS_USAGE.md"
    text = readme.read_text(encoding="utf-8")

    assert "Tina-codex助手.exe" in text
    assert "scripts\\build-windows.ps1" in text
    assert "快速注入/修复" in text
    assert "一键完整安装" in text
    assert "不会写入模型服务" in text
