#!/usr/bin/env python3
"""
Hi-Codex CDN 配置测试脚本
用于验证 CDN 配置是否正确
"""

from src.tina_codex_assistant.cdn_config import (
    get_codex_cli_cdn,
    get_codex_gui_cdn,
    has_cdn_configured,
    HI_CODEX_CDN_CONFIG,
)


def test_cdn_config():
    """测试 CDN 配置"""

    print("=" * 60)
    print("Hi-Codex CDN 配置测试")
    print("=" * 60)
    print()

    # 检查是否已配置
    configured = has_cdn_configured()
    print(f"CDN 配置状态: {'✅ 已配置' if configured else '❌ 未配置'}")
    print()

    # 检查 GUI CDN
    print("Codex GUI CDN 地址:")
    gui_urls = get_codex_gui_cdn()
    if gui_urls:
        for i, url in enumerate(gui_urls, 1):
            print(f"  {i}. {url}")
    else:
        print("  ❌ 未配置")
    print()

    # 检查 CLI CDN
    print("Codex CLI CDN 地址:")
    cli_urls = get_codex_cli_cdn()
    if cli_urls:
        if "install_script" in cli_urls:
            print(f"  install.sh: {cli_urls['install_script']}")
        if "tarball" in cli_urls:
            print(f"  tarball:    {cli_urls['tarball']}")
    else:
        print("  ❌ 未配置")
    print()

    # 显示配置选项
    print("配置选项:")
    options = HI_CODEX_CDN_CONFIG["options"]
    print(f"  超时时间: {options['timeout']} 秒")
    print(f"  重试次数: {options['retry_times']} 次")
    print(f"  使用备用 CDN: {'是' if options['use_backup_on_failure'] else '否'}")
    print()

    # 检查配置完整性
    print("=" * 60)
    print("配置完整性检查")
    print("=" * 60)
    print()

    all_ok = True

    # 检查 GUI 主 CDN
    gui_primary = HI_CODEX_CDN_CONFIG["gui"]["primary"]
    if gui_primary.startswith("https://填入"):
        print("❌ Codex GUI 主 CDN 未配置")
        all_ok = False
    else:
        print(f"✅ Codex GUI 主 CDN 已配置")

    # 检查 CLI install.sh
    cli_script = HI_CODEX_CDN_CONFIG["cli"]["install_script"]
    if cli_script.startswith("https://填入"):
        print("❌ Codex CLI install.sh 未配置")
        all_ok = False
    else:
        print(f"✅ Codex CLI install.sh 已配置")

    # 检查 CLI tarball
    cli_tarball = HI_CODEX_CDN_CONFIG["cli"]["tarball"]
    if cli_tarball.startswith("https://填入"):
        print("❌ Codex CLI tarball 未配置")
        all_ok = False
    else:
        print(f"✅ Codex CLI tarball 已配置")

    print()
    print("=" * 60)

    if all_ok:
        print("✅ 所有 CDN 地址已正确配置！")
        print()
        print("下一步:")
        print("  1. 提交代码: git add . && git commit -m 'config: Hi-Codex CDN'")
        print("  2. 推送: git push")
        print("  3. GitHub Actions 会自动打包")
    else:
        print("⚠️  请完成 CDN 配置")
        print()
        print("配置文件位置:")
        print("  src/tina_codex_assistant/cdn_config.py")
        print()
        print("需要填入的信息:")
        print("  1. Codex GUI 主 CDN 地址")
        print("  2. Codex CLI install.sh 地址")
        print("  3. Codex CLI tarball 地址")

    print("=" * 60)
    print()

    return all_ok


if __name__ == "__main__":
    test_cdn_config()
