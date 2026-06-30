from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


# Codex GUI：通过 store.rg-adguard.net 查询微软商店离线包，再走微软 CDN 下载。
# 微软 CDN 国内可达性较好，无需 VPN。
CODEX_GUI_INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
Write-Host "通过 Microsoft Store 包链路安装 Codex GUI"
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
Write-Host "Codex GUI 安装完成"
"""

# Git：通过 npmmirror 国内镜像下载 MinGit，无需 VPN。
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

# Codex CLI：Windows 原生方案。
# 1) 确保有 Node：检测不到就从 npmmirror 国内镜像下载便携版 Node 并加入用户 PATH。
# 2) 把 npm registry 指向 npmmirror。
# 3) npm install -g @openai/codex。
# 全程走国内镜像，不依赖 WSL，不依赖境外网络。
CODEX_CLI_NPM_INSTALL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$nodeMirror = 'https://registry.npmmirror.com/-/binary/node/'
$npmRegistry = 'https://registry.npmmirror.com'

function Get-NpmCommand {
  $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
  if (-not $npm) { $npm = Get-Command npm -ErrorAction SilentlyContinue }
  return $npm
}

$npm = Get-NpmCommand
if (-not $npm) {
  Write-Host "未检测到 Node.js，开始从 npmmirror 国内镜像安装便携版 Node..."
  $index = Invoke-RestMethod ($nodeMirror + 'index.json')
  $lts = $index |
    Where-Object { $_.lts -and ($_.files -contains 'win-x64-zip') } |
    Sort-Object { [version]($_.version.TrimStart('v')) } -Descending |
    Select-Object -First 1
  if (-not $lts) { throw '未找到可用的 Node.js LTS (win-x64) 版本' }
  $ver = $lts.version
  $zipName = "node-$ver-win-x64.zip"
  $zipUrl = "$nodeMirror$ver/$zipName"
  $zip = Join-Path $env:TEMP $zipName
  Write-Host "下载 Node.js $ver ..."
  Invoke-WebRequest -UseBasicParsing -Uri $zipUrl -OutFile $zip
  $nodeRoot = Join-Path $env:LOCALAPPDATA 'TinaCodex\Node'
  if (Test-Path $nodeRoot) { Remove-Item -Recurse -Force $nodeRoot }
  New-Item -ItemType Directory -Force -Path $nodeRoot | Out-Null
  Expand-Archive -Force -Path $zip -DestinationPath $nodeRoot
  $nodeDir = Join-Path $nodeRoot "node-$ver-win-x64"
  $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
  if (($currentPath -split ';') -notcontains $nodeDir) {
    $parts = @($currentPath, $nodeDir) | Where-Object { $_ }
    [Environment]::SetEnvironmentVariable('Path', ($parts -join ';'), 'User')
  }
  $env:Path = "$nodeDir;$env:Path"
  $npm = Get-NpmCommand
  if (-not $npm) { throw 'Node.js 安装后仍未找到 npm' }
}

Write-Host "配置 npm 使用 npmmirror 国内镜像..."
& $npm.Source config set registry $npmRegistry

Write-Host "安装 Codex CLI (@openai/codex)..."
& $npm.Source install -g '@openai/codex'

$codex = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codex) { $codex = Get-Command codex.cmd -ErrorAction SilentlyContinue }
if ($codex) {
  Write-Host "Codex CLI 安装完成"
  & $codex.Source --version
} else {
  Write-Host "Codex CLI 已安装，请重新打开终端使 PATH 生效"
}
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
) -> InstallPlan:
    """构建完整安装计划。

    所有组件均走国内可直连来源，无需 VPN：
    - Codex GUI：微软商店离线包（store.rg-adguard.net 查询 + 微软 CDN 下载）
    - Codex CLI：npm 原生安装（@openai/codex），Node/npm 走 npmmirror 镜像
    - Git：npmmirror 镜像下载 MinGit
    """
    actions: list[InstallAction] = []

    if codex_gui_found:
        actions.append(InstallAction("check_codex_gui", "Codex GUI 已检测到", []))
    else:
        actions.append(
            InstallAction(
                "install_codex_gui",
                "通过 Microsoft Store 包链路安装 Codex GUI",
                [CODEX_GUI_INSTALL_SCRIPT],
            )
        )

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

    if codex_cli_found:
        actions.append(InstallAction("check_codex_cli", "Codex CLI 已检测到", []))
    else:
        actions.append(
            InstallAction(
                "install_codex_cli",
                "通过 npm 安装 Codex CLI（Node/npm 走 npmmirror 国内镜像）",
                [CODEX_CLI_NPM_INSTALL_SCRIPT],
            )
        )

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
