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
Write-Host "打包完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "输出文件：$Exe"
Write-Host "文件大小：$exeSize MB"
Write-Host ""
Write-Host "把 dist\Tina-codex助手.exe 发给 Windows 用户即可运行。"
Write-Host ""
