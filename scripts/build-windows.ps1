$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "========================================"
Write-Host "Tina-codex 助手 - Windows 打包脚本"
Write-Host "========================================"
Write-Host ""

# 检查必需资源
if (-not (Test-Path "resources\plugin.zip")) {
  throw "缺少 resources\plugin.zip，请确认完整复制 tina-codex-assistant 目录。"
}

if (-not (Test-Path "resources\statsig-zh-CN-raw-snapshot.json")) {
  throw "缺少 resources\statsig-zh-CN-raw-snapshot.json，请确认完整复制 tina-codex-assistant 目录。"
}

# 检查离线资源
Write-Host "检查离线资源..."
$offlineGuiExists = $false
$offlineCliExists = $false

foreach ($ext in @(".msixbundle", ".appxbundle", ".msix", ".appx")) {
  if (Test-Path "resources\codex-gui$ext") {
    $offlineGuiExists = $true
    $guiFile = "codex-gui$ext"
    break
  }
}

if ((Test-Path "resources\codex-cli\install.sh") -and (Test-Path "resources\codex-cli\codex-linux-x64.tar.gz")) {
  $offlineCliExists = $true
}

Write-Host ""
Write-Host "离线资源状态："
Write-Host "  Codex GUI: " -NoNewline
if ($offlineGuiExists) {
  Write-Host "✓ 已包含 ($guiFile)" -ForegroundColor Green
} else {
  Write-Host "✗ 未包含" -ForegroundColor Yellow
}

Write-Host "  Codex CLI: " -NoNewline
if ($offlineCliExists) {
  Write-Host "✓ 已包含" -ForegroundColor Green
} else {
  Write-Host "✗ 未包含" -ForegroundColor Yellow
}

Write-Host ""

if (-not $offlineGuiExists -or -not $offlineCliExists) {
  Write-Host "提示：缺少离线资源，打包后的 exe 将使用在线安装模式" -ForegroundColor Yellow
  Write-Host "      在国内无 VPN 环境下可能安装失败" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "如需完全离线支持，请先运行：" -ForegroundColor Yellow
  Write-Host '  powershell -ExecutionPolicy Bypass -File scripts\download-offline-resources.ps1' -ForegroundColor Cyan
  Write-Host ""

  $response = Read-Host "是否继续打包？(y/n)"
  if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "已取消打包"
    exit 0
  }
  Write-Host ""
}

# 检查 Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "未检测到 Python。请先安装 Python 3.11+，或用 winget install Python.Python.3.12。"
}

Write-Host "安装/更新依赖..."
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller pywebview

Write-Host ""
Write-Host "清理旧的构建..."
if (Test-Path "build") {
  Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
  Remove-Item -Recurse -Force "dist"
}

Write-Host ""
Write-Host "开始打包..."
pyinstaller --clean --noconfirm TinaCodexAssistant.spec

$Exe = "dist\Tina-codex助手.exe"
if (-not (Test-Path $Exe)) {
  throw "打包完成但未找到 $Exe"
}

$exeSize = [math]::Round((Get-Item $Exe).Length / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ 打包完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "输出文件：$Exe"
Write-Host "文件大小：$exeSize MB"
Write-Host ""

if ($offlineGuiExists -and $offlineCliExists) {
  Write-Host "此版本包含完全离线资源，支持无 VPN 环境安装" -ForegroundColor Green
} else {
  Write-Host "此版本缺少部分离线资源，在无 VPN 环境下可能失败" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "把 dist\Tina-codex助手.exe 发给 Windows 用户即可运行。"
Write-Host ""

