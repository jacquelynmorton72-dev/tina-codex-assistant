# 下载离线资源脚本
# 需要在有网络访问权限（VPN）的 Windows 环境下执行
# 执行后会下载 Codex GUI 和 Codex CLI 安装包到 resources 目录

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "========================================"
Write-Host "Tina-codex 助手 - 离线资源下载工具"
Write-Host "========================================"
Write-Host ""
Write-Host "此脚本需要在有网络访问（建议使用 VPN）的环境下运行"
Write-Host "将下载 Codex GUI 和 Codex CLI 安装包到 resources 目录"
Write-Host ""

# 确保 resources 目录存在
New-Item -ItemType Directory -Force -Path "resources" | Out-Null
New-Item -ItemType Directory -Force -Path "resources\codex-cli" | Out-Null

# ==================== 下载 Codex GUI ====================
Write-Host "[1/3] 下载 Codex GUI 安装包..."
Write-Host ""

try {
    Write-Host "正在查询 Microsoft Store 安装包链接..."
    $body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body -TimeoutSec 30

    $link = $response.Links |
        Where-Object { $_.href -match 'https?://.*\.(msixbundle|appxbundle)' } |
        Select-Object -ExpandProperty href -First 1

    if (-not $link) {
        throw "未找到 Codex GUI 安装包下载链接"
    }

    Write-Host "找到下载链接：$link"
    Write-Host ""

    $ext = [System.IO.Path]::GetExtension(($link -split '\?')[0])
    if (-not $ext) { $ext = '.msixbundle' }
    $outputPath = "resources\codex-gui$ext"

    Write-Host "正在下载到：$outputPath"
    Write-Host "（文件较大，预计 200-500MB，请耐心等待...）"
    Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile $outputPath

    $fileSize = [math]::Round((Get-Item $outputPath).Length / 1MB, 2)
    Write-Host "✓ Codex GUI 下载完成！文件大小：$fileSize MB"
} catch {
    Write-Host "✗ Codex GUI 下载失败：$_" -ForegroundColor Red
    Write-Host "  可能原因：网络问题或 store.rg-adguard.net 服务不可用"
    Write-Host "  影响：打包后的 exe 将使用在线安装模式（需要 VPN）"
}

Write-Host ""

# ==================== 下载 Codex CLI install.sh ====================
Write-Host "[2/3] 下载 Codex CLI 安装脚本..."
Write-Host ""

try {
    Write-Host "正在下载 install.sh..."
    Invoke-WebRequest -UseBasicParsing -Uri "https://chatgpt.com/codex/install.sh" -OutFile "resources\codex-cli\install.sh" -TimeoutSec 30
    Write-Host "✓ install.sh 下载完成"
} catch {
    Write-Host "✗ install.sh 下载失败：$_" -ForegroundColor Red
    Write-Host "  可能原因：无法访问 chatgpt.com（被墙）"
    Write-Host "  影响：打包后的 exe 将使用在线安装模式（需要 VPN）"
}

Write-Host ""

# ==================== 提取并下载 Codex CLI tarball ====================
Write-Host "[3/3] 下载 Codex CLI 安装包..."
Write-Host ""

if (Test-Path "resources\codex-cli\install.sh") {
    try {
        Write-Host "正在从 install.sh 中提取下载链接..."
        $installShContent = Get-Content "resources\codex-cli\install.sh" -Raw

        # 尝试提取 tarball URL（可能需要根据实际脚本调整正则表达式）
        # 常见模式: https://.../.../codex-linux-x64.tar.gz 或类似
        if ($installShContent -match '(https?://[^\s"'']+codex[^\s"'']*linux[^\s"'']*\.tar\.gz)') {
            $tarballUrl = $matches[1]
            Write-Host "找到下载链接：$tarballUrl"
            Write-Host ""

            Write-Host "正在下载 Codex CLI tarball..."
            Write-Host "（文件较大，预计 50-100MB，请耐心等待...）"
            Invoke-WebRequest -UseBasicParsing -Uri $tarballUrl -OutFile "resources\codex-cli\codex-linux-x64.tar.gz" -TimeoutSec 120

            $fileSize = [math]::Round((Get-Item "resources\codex-cli\codex-linux-x64.tar.gz").Length / 1MB, 2)
            Write-Host "✓ Codex CLI tarball 下载完成！文件大小：$fileSize MB"
        } else {
            Write-Host "✗ 无法从 install.sh 中提取 tarball 下载链接" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "请手动操作："
            Write-Host "1. 查看 resources\codex-cli\install.sh 找到 tarball 下载 URL"
            Write-Host "2. 运行以下命令下载："
            Write-Host '   Invoke-WebRequest -Uri "<URL>" -OutFile "resources\codex-cli\codex-linux-x64.tar.gz"'
        }
    } catch {
        Write-Host "✗ Codex CLI tarball 下载失败：$_" -ForegroundColor Red
        Write-Host "  可能原因：网络问题或下载链接已变更"
        Write-Host "  影响：打包后的 exe 将使用在线安装模式（需要 VPN）"
    }
} else {
    Write-Host "跳过（install.sh 未下载成功）"
}

Write-Host ""
Write-Host "========================================"
Write-Host "下载完成汇总"
Write-Host "========================================"
Write-Host ""

$guiExists = Test-Path "resources\codex-gui.*"
$cliInstallExists = Test-Path "resources\codex-cli\install.sh"
$cliTarballExists = Test-Path "resources\codex-cli\codex-linux-x64.tar.gz"

Write-Host "Codex GUI 安装包：" -NoNewline
if ($guiExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host "Codex CLI 安装脚本：" -NoNewline
if ($cliInstallExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host "Codex CLI 安装包：" -NoNewline
if ($cliTarballExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host ""

if ($guiExists -and $cliInstallExists -and $cliTarballExists) {
    Write-Host "✓ 所有离线资源已下载完成！" -ForegroundColor Green
    Write-Host "  现在可以运行 scripts\build-windows.ps1 进行打包"
    Write-Host "  打包后的 exe 将支持完全离线安装（无需 VPN）"
} else {
    Write-Host "⚠ 部分离线资源缺失" -ForegroundColor Yellow
    Write-Host "  仍可以进行打包，但缺失的组件将使用在线安装模式"
    Write-Host "  在国内无 VPN 环境下可能安装失败"
}

Write-Host ""
