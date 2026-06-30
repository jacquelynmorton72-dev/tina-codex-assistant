from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


def codex_gui_install_cdn_script(cdn_urls: list[str]) -> str:
    """生成使用 CDN 下载并安装 Codex GUI 的脚本"""
    urls_ps = ", ".join([f"'{url}'" for url in cdn_urls])

    return f"""
$ErrorActionPreference = 'Stop'
Write-Host "使用 Hi-Codex CDN 下载 Codex GUI 安装包"

$cdnUrls = @({urls_ps})
$pkg = Join-Path $env:TEMP 'codex-gui.msixbundle'
$downloaded = $false

foreach ($url in $cdnUrls) {{
    try {{
        Write-Host "尝试从 CDN 下载：$url"
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $pkg -TimeoutSec 300

        if (Test-Path $pkg) {{
            $size = [math]::Round((Get-Item $pkg).Length / 1MB, 2)
            Write-Host "✓ 下载完成 ($size MB)"
            $downloaded = $true
            break
        }}
    }} catch {{
        Write-Host "✗ 下载失败：$_" -ForegroundColor Yellow
        Write-Host "尝试下一个 CDN..." -ForegroundColor Yellow
    }}
}}

if (-not $downloaded) {{
    throw "所有 CDN 下载均失败"
}}

Write-Host "正在安装 Codex GUI..."
Add-AppxPackage -Path $pkg -ForceApplicationShutdown
Write-Host "✓ Codex GUI 安装完成"

# 清理临时文件
Remove-Item $pkg -Force -ErrorAction SilentlyContinue
"""


def codex_cli_install_cdn_script(install_script_url: str, tarball_url: str) -> str:
    """生成使用 CDN 下载并在 WSL 中安装 Codex CLI 的脚本"""
    return f"""
$ErrorActionPreference = 'Stop'
Write-Host "使用 Hi-Codex CDN 安装 Codex CLI"

# 检查 WSL
Write-Host "检查 WSL 状态..."
wsl.exe --status | Out-Null
if ($LASTEXITCODE -ne 0) {{
    throw 'WSL 未安装或未启动。请先运行: wsl --install'
}}

$wslTmp = '/tmp/tina-codex-cdn'
wsl.exe sh -c "mkdir -p $wslTmp"

try {{
    # 下载安装脚本
    Write-Host "下载安装脚本..."
    $installSh = Join-Path $env:TEMP 'codex-install.sh'
    Invoke-WebRequest -UseBasicParsing -Uri '{install_script_url}' -OutFile $installSh -TimeoutSec 60

    # 下载 tarball
    Write-Host "下载 Codex CLI 安装包..."
    $tarball = Join-Path $env:TEMP 'codex-linux-x64.tar.gz'
    Invoke-WebRequest -UseBasicParsing -Uri '{tarball_url}' -OutFile $tarball -TimeoutSec 300

    $size = [math]::Round((Get-Item $tarball).Length / 1MB, 2)
    Write-Host "✓ 下载完成 ($size MB)"

    # 复制到 WSL
    Write-Host "复制到 WSL..."
    $wslInstallSh = wsl.exe wslpath -a $installSh
    $wslTarball = wsl.exe wslpath -a $tarball

    wsl.exe cp $wslInstallSh "$wslTmp/install.sh"
    wsl.exe cp $wslTarball "$wslTmp/codex-linux-x64.tar.gz"

    # 修改脚本使用本地 tarball
    Write-Host "配置安装脚本..."
    wsl.exe sh -c "cd $wslTmp && sed -i 's|curl.*codex.*tar.gz.*|cp $wslTmp/codex-linux-x64.tar.gz codex-linux-x64.tar.gz|g' install.sh"

    # 执行安装
    Write-Host "执行安装..."
    wsl.exe sh -lc "cd $wslTmp && sh install.sh"

    Write-Host "✓ Codex CLI 安装完成"
}} finally {{
    # 清理
    wsl.exe rm -rf $wslTmp
    Remove-Item $installSh -Force -ErrorAction SilentlyContinue
    Remove-Item $tarball -Force -ErrorAction SilentlyContinue
}}
"""


def codex_gui_install_offline_script(pkg_path: Path) -> str:
    """生成使用本地安装包安装 Codex GUI 的脚本"""
    pkg_win_path = pkg_path.as_posix().replace("/", "\\")
    return f"""
$ErrorActionPreference = 'Stop'
$pkg = '{pkg_win_path}'
if (-not (Test-Path $pkg)) {{ throw "未找到离线安装包：$pkg" }}
Write-Host "使用离线安装包安装 Codex GUI: $pkg"
Add-AppxPackage -Path $pkg -ForceApplicationShutdown
Write-Host "Codex GUI 安装完成"
"""


CODEX_GUI_INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
Write-Host "通过在线方式安装 Codex GUI（需要网络访问 store.rg-adguard.net）"
$body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
$response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body
$link = $response.Links |
  Where-Object { $_.href -match 'https?://.*\.(msixbundle|appxbundle|msix|appx)' } |
  Select-Object -ExpandProperty href -First 1
if (-not $link) { throw '未找到 openai.codex 的 Microsoft Store 安装包链接' }
$ext = [System.IO.Path]::GetExtension(($link -split '\?')[0])
if (-not $ext) { $ext = '.msixbundle' }
$pkg = Join-Path $env:TEMP ('Codex' + $ext)
Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile $pkg
Add-AppxPackage -Path $pkg -ForceApplicationShutdown
"""

MIN_GIT_INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
Write-Host "通过 npmmirror 国内镜像安装 Git for Windows"
$root = 'https://registry.npmmirror.com/-/binary/git-for-windows/'
$entries = Invoke-RestMethod $root
$latest = $entries |
  Where-Object { $_.name -match '^\d+\.\d+\.\d+\.windows\.\d+/$' -or $_.name -match '^v?\d' } |
  Sort-Object name -Descending |
  Select-Object -First 1
if (-not $latest) { throw '未找到 Git for Windows 镜像版本' }
$versionUrl = if ($latest.url) { $latest.url } else { $root + $latest.name }
$assets = Invoke-RestMethod $versionUrl
$asset = $assets |
  Where-Object { $_.name -match '^MinGit-.*64-bit\.zip$' -and $_.name -notmatch 'busybox' } |
  Select-Object -First 1
if (-not $asset) { throw '未找到 64-bit MinGit zip' }
$assetUrl = if ($asset.url) { $asset.url } else { $versionUrl + $asset.name }
$zip = Join-Path $env:TEMP $asset.name
$gitRoot = Join-Path $env:LOCALAPPDATA 'TinaCodex\MinGit'
Invoke-WebRequest -UseBasicParsing -Uri $assetUrl -OutFile $zip
if (Test-Path $gitRoot) { Remove-Item -Recurse -Force $gitRoot }
New-Item -ItemType Directory -Force -Path $gitRoot | Out-Null
Expand-Archive -Force -Path $zip -DestinationPath $gitRoot
$gitCmd = Join-Path $gitRoot 'cmd'
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($currentPath -split ';') -notcontains $gitCmd) {
  $parts = @($currentPath, $gitCmd) | Where-Object { $_ }
  [Environment]::SetEnvironmentVariable('Path', ($parts -join ';'), 'User')
}
& (Join-Path $gitCmd 'git.exe') --version
"""


def codex_cli_install_offline_script(cli_dir: Path) -> str:
    """生成使用本地资源在 WSL 中安装 Codex CLI 的脚本"""
    install_sh = cli_dir / "install.sh"
    tarball = cli_dir / "codex-linux-x64.tar.gz"
    install_sh_win = install_sh.as_posix().replace("/", "\\")
    tarball_win = tarball.as_posix().replace("/", "\\")

    return f"""
$ErrorActionPreference = 'Stop'
Write-Host "使用离线资源安装 Codex CLI"

# 检查 WSL
Write-Host "检查 WSL 状态..."
wsl.exe --status | Out-Null
if ($LASTEXITCODE -ne 0) {{
    throw 'WSL 未安装或未启动。请先运行: wsl --install'
}}

# 准备资源
$installSh = '{install_sh_win}'
$tarball = '{tarball_win}'

if (-not (Test-Path $installSh)) {{ throw "未找到安装脚本: $installSh" }}
if (-not (Test-Path $tarball)) {{ throw "未找到 CLI 安装包: $tarball" }}

Write-Host "复制资源到 WSL..."
$wslTmp = '/tmp/tina-codex-install'
wsl.exe sh -c "mkdir -p $wslTmp"

# 转换为 WSL 路径并复制
$wslInstallSh = wsl.exe wslpath -a $installSh
$wslTarball = wsl.exe wslpath -a $tarball

wsl.exe cp $wslInstallSh "$wslTmp/install.sh"
wsl.exe cp $wslTarball "$wslTmp/codex-linux-x64.tar.gz"

Write-Host "修改安装脚本使用本地资源..."
wsl.exe sh -c "cd $wslTmp && sed -i 's|curl.*codex.*tar.gz.*|cp $wslTmp/codex-linux-x64.tar.gz codex-linux-x64.tar.gz|g' install.sh"

Write-Host "执行安装..."
wsl.exe sh -lc "cd $wslTmp && sh install.sh"

Write-Host "清理临时文件..."
wsl.exe rm -rf $wslTmp

Write-Host "Codex CLI 安装完成"
"""


CODEX_WSL_INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
Write-Host "通过在线方式安装 Codex CLI（需要网络访问 chatgpt.com）"
wsl.exe --status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'WSL 未安装或未启动。请先运行: wsl --install'
}
wsl.exe sh -lc "curl -fsSL https://chatgpt.com/codex/install.sh | sh"
"""


@dataclass(frozen=True)
class InstallAction:
    key: str
    description: str
    commands: list[str]


@dataclass(frozen=True)
class InstallPlan:
    actions: list[InstallAction]


def build_quick_repair_plan(codex_cli_found: bool, codex_gui_found: bool) -> InstallPlan:
    return InstallPlan(
        actions=[
            InstallAction(
                "check_codex_gui",
                "Codex GUI 已检测到" if codex_gui_found else "Codex GUI 未检测到，请使用一键完整安装",
                [],
            ),
            InstallAction(
                "check_codex_cli",
                "Codex CLI 已检测到" if codex_cli_found else "Codex CLI 未检测到，请使用一键完整安装",
                [],
            ),
            InstallAction("inject_plugins", "注入 Tina-codex 中文插件市场", []),
            InstallAction("install_recommended_plugins", "安装推荐基础插件组", []),
        ]
    )


def build_full_install_plan(
    codex_cli_found: bool,
    codex_gui_found: bool,
    git_found: bool,
    offline_gui_pkg: Path | None = None,
    offline_cli_dir: Path | None = None,
    cdn_gui_urls: list[str] | None = None,
    cdn_cli_urls: dict[str, str] | None = None,
) -> InstallPlan:
    """构建完整安装计划

    Args:
        codex_cli_found: 是否检测到 Codex CLI
        codex_gui_found: 是否检测到 Codex GUI
        git_found: 是否检测到 Git
        offline_gui_pkg: 离线 GUI 安装包路径
        offline_cli_dir: 离线 CLI 资源目录路径
        cdn_gui_urls: Hi-Codex CDN GUI 下载地址列表
        cdn_cli_urls: Hi-Codex CDN CLI 下载地址字典

    Returns:
        InstallPlan: 安装计划
    """
    actions: list[InstallAction] = []

    # Codex GUI - 优先级：离线 > CDN > 在线
    if codex_gui_found:
        actions.append(InstallAction("check_codex_gui", "Codex GUI 已检测到", []))
    else:
        # 优先使用离线安装包
        if offline_gui_pkg and offline_gui_pkg.exists():
            actions.append(
                InstallAction(
                    "install_codex_gui_offline",
                    "使用离线安装包安装 Codex GUI（无需网络）",
                    [codex_gui_install_offline_script(offline_gui_pkg)],
                )
            )
        # 其次使用 Hi-Codex CDN
        elif cdn_gui_urls and len(cdn_gui_urls) > 0:
            actions.append(
                InstallAction(
                    "install_codex_gui_cdn",
                    "使用 Hi-Codex CDN 安装 Codex GUI（国内高速，无需 VPN）",
                    [codex_gui_install_cdn_script(cdn_gui_urls)],
                )
            )
        # 最后回退到在线下载
        else:
            actions.append(
                InstallAction(
                    "install_codex_gui",
                    "通过 Microsoft Store 包链路安装 Codex GUI（需要网络）",
                    [CODEX_GUI_INSTALL_SCRIPT],
                )
            )

    # Git
    if git_found:
        actions.append(InstallAction("check_git", "Git 已检测到", []))
    else:
        actions.append(
            InstallAction(
                "install_git",
                "通过 npmmirror 国内镜像安装 Git for Windows / MinGit",
                [MIN_GIT_INSTALL_SCRIPT],
            )
        )

    # Codex CLI - 优先级：离线 > CDN > 在线
    if codex_cli_found:
        actions.append(InstallAction("check_codex_cli", "Codex CLI 已检测到", []))
    else:
        # 优先使用离线资源
        if offline_cli_dir and offline_cli_dir.exists():
            actions.append(
                InstallAction(
                    "install_codex_cli_offline",
                    "使用离线资源安装 Codex CLI（无需网络）",
                    [codex_cli_install_offline_script(offline_cli_dir)],
                )
            )
        # 其次使用 Hi-Codex CDN
        elif cdn_cli_urls and "install_script" in cdn_cli_urls and "tarball" in cdn_cli_urls:
            actions.append(
                InstallAction(
                    "install_codex_cli_cdn",
                    "使用 Hi-Codex CDN 安装 Codex CLI（国内高速，无需 VPN）",
                    [codex_cli_install_cdn_script(cdn_cli_urls["install_script"], cdn_cli_urls["tarball"])],
                )
            )
        # 最后回退到在线下载
        else:
            actions.append(
                InstallAction(
                    "install_codex_cli",
                    "通过官方 WSL 安装脚本安装 Codex CLI（需要网络）",
                    [CODEX_WSL_INSTALL_SCRIPT],
                )
            )
                    "通过官方 WSL 安装脚本安装 Codex CLI（需要网络）",
                    [CODEX_WSL_INSTALL_SCRIPT],
                )
            )

    # 插件注入和推荐插件
    actions.extend(
        [
            InstallAction("inject_plugins", "注入 Tina-codex 中文插件市场", []),
            InstallAction("install_recommended_plugins", "安装推荐基础插件组", []),
        ]
    )
    return InstallPlan(actions=actions)


def detect_codex_cli() -> bool:
    return shutil.which("codex") is not None or shutil.which("codex.exe") is not None


def detect_git() -> bool:
    return shutil.which("git") is not None or shutil.which("git.exe") is not None


def detect_codex_gui() -> bool:
    candidates = [
        Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "Codex.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Codex" / "Codex.exe",
    ]
    return any(path.exists() for path in candidates) or shutil.which("Codex.exe") is not None


def run_powershell(command: str, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
