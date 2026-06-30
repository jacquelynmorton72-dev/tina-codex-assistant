"""
Hi-Codex CDN 配置模块

此模块管理 Hi-Codex 团队的 CDN 资源地址
"""

from __future__ import annotations

# ============================================
# Hi-Codex CDN 配置
# ============================================

# TODO: 填入 Hi-Codex 团队的实际 CDN 地址
HI_CODEX_CDN_CONFIG = {
    # Codex GUI 安装包 CDN 地址
    "gui": {
        "primary": "https://填入主CDN地址/codex-gui.msixbundle",
        "backup": "https://填入备用CDN地址/codex-gui.msixbundle",  # 可选
    },

    # Codex CLI 资源 CDN 地址
    "cli": {
        "install_script": "https://填入CDN地址/codex-install.sh",
        "tarball": "https://填入CDN地址/codex-linux-x64.tar.gz",
    },

    # 配置选项
    "options": {
        "timeout": 300,  # 下载超时时间（秒）
        "retry_times": 3,  # 重试次数
        "use_backup_on_failure": True,  # 主CDN失败时使用备用
    }
}


def get_codex_gui_cdn() -> list[str]:
    """获取 Codex GUI 安装包的 CDN 地址列表

    Returns:
        list[str]: CDN 地址列表，按优先级排序
    """
    urls = []

    primary = HI_CODEX_CDN_CONFIG["gui"]["primary"]
    backup = HI_CODEX_CDN_CONFIG["gui"].get("backup")

    if primary and not primary.startswith("https://填入"):
        urls.append(primary)

    if backup and not backup.startswith("https://填入"):
        urls.append(backup)

    return urls


def get_codex_cli_cdn() -> dict[str, str]:
    """获取 Codex CLI 资源的 CDN 地址

    Returns:
        dict: {"install_script": str, "tarball": str}
    """
    cli_config = HI_CODEX_CDN_CONFIG["cli"]

    result = {}

    install_script = cli_config.get("install_script", "")
    if install_script and not install_script.startswith("https://填入"):
        result["install_script"] = install_script

    tarball = cli_config.get("tarball", "")
    if tarball and not tarball.startswith("https://填入"):
        result["tarball"] = tarball

    return result


def has_cdn_configured() -> bool:
    """检查是否已配置 CDN 地址

    Returns:
        bool: True 如果已配置，False 如果未配置
    """
    gui_urls = get_codex_gui_cdn()
    cli_urls = get_codex_cli_cdn()

    return len(gui_urls) > 0 or len(cli_urls) > 0


def get_cdn_options() -> dict:
    """获取 CDN 配置选项

    Returns:
        dict: CDN 配置选项
    """
    return HI_CODEX_CDN_CONFIG["options"].copy()
