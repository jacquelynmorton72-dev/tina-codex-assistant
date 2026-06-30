# Codex 完全离线资源下载工具（增强版）
# 需要在有 VPN 的 Windows 环境下运行
# 下载 Codex GUI 和 CLI 安装包到 resources 目录

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Codex 完全离线资源下载工具（增强版）" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "此脚本将下载 Codex GUI 和 CLI 的完整安装包" -ForegroundColor White
Write-Host "下载后可打包成完全离线版，无需 VPN 即可安装" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  需要 VPN 访问以下服务：" -ForegroundColor Yellow
Write-Host "   • store.rg-adguard.net (获取 Codex GUI)" -ForegroundColor White
Write-Host "   • chatgpt.com (获取 Codex CLI)" -ForegroundColor White
Write-Host ""

$continue = Read-Host "是否继续？(y/n)"
if ($continue -ne 'y' -and $continue -ne 'Y') {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$resourcesDir = "resources"
$cliDir = Join-Path $resourcesDir "codex-cli"

# 确保目录存在
New-Item -ItemType Directory -Force -Path $resourcesDir | Out-Null
New-Item -ItemType Directory -Force -Path $cliDir | Out-Null

# ==================== 下载 Codex GUI ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "[1/3] 下载 Codex GUI 安装包" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$guiSuccess = $false

try {
    Write-Host "正在查询 Microsoft Store 安装包链接..." -ForegroundColor White
    Write-Host "（使用 store.rg-adguard.net 服务）" -ForegroundColor Gray
    Write-Host ""

    $body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body -TimeoutSec 30

    $link = $response.Links | Where-Object { $_.href -match 'https?://.*\.(msixbundle|appxbundle)' } | Select-Object -ExpandProperty href -First 1

    if (-not $link) {
        throw "未找到 Codex GUI 安装包下载链接"
    }

    Write-Host "✓ 找到下载链接" -ForegroundColor Green
    Write-Host "  URL: $($link.Substring(0, [Math]::Min(80, $link.Length)))..." -ForegroundColor Gray
    Write-Host ""

    $ext = if ($link -match '\.msixbundle') { '.msixbundle' } else { '.appxbundle' }
    $outputPath = Join-Path $resourcesDir "codex-gui$ext"

    Write-Host "开始下载 Codex GUI 安装包..." -ForegroundColor White
    Write-Host "保存到: $outputPath" -ForegroundColor Gray
    Write-Host "预计大小: 200-500 MB，请耐心等待..." -ForegroundColor Yellow
    Write-Host ""

    # 显示下载进度
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile $outputPath

    if (Test-Path $outputPath) {
        $fileSize = [math]::Round((Get-Item $outputPath).Length / 1MB, 2)
        Write-Host ""
        Write-Host "✓ Codex GUI 下载完成！" -ForegroundColor Green
        Write-Host "  文件: $outputPath" -ForegroundColor White
        Write-Host "  大小: $fileSize MB" -ForegroundColor White
        $guiSuccess = $true
    } else {
        throw "下载完成但文件不存在"
    }
} catch {
    Write-Host ""
    Write-Host "✗ Codex GUI 下载失败" -ForegroundColor Red
    Write-Host "  错误: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因：" -ForegroundColor Yellow
    Write-Host "  • 无法访问 store.rg-adguard.net（需要 VPN）" -ForegroundColor White
    Write-Host "  • 网络连接问题" -ForegroundColor White
    Write-Host "  • 服务暂时不可用" -ForegroundColor White
    Write-Host ""
    Write-Host "手动下载方法：" -ForegroundColor Cyan
    Write-Host "  1. 访问 https://store.rg-adguard.net/" -ForegroundColor White
    Write-Host "  2. 输入: openai.codex" -ForegroundColor White
    Write-Host "  3. 选择: Retail" -ForegroundColor White
    Write-Host "  4. 下载 .msixbundle 或 .appxbundle 文件" -ForegroundColor White
    Write-Host "  5. 保存到: $resourcesDir\codex-gui.msixbundle" -ForegroundColor White
}

Write-Host ""
Start-Sleep -Seconds 2

# ==================== 下载 Codex CLI install.sh ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "[2/3] 下载 Codex CLI 安装脚本" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$installShSuccess = $false

try {
    Write-Host "正在从 chatgpt.com 下载 install.sh..." -ForegroundColor White
    Write-Host ""

    $installShPath = Join-Path $cliDir "install.sh"
    Invoke-WebRequest -UseBasicParsing -Uri "https://chatgpt.com/codex/install.sh" -OutFile $installShPath -TimeoutSec 30

    if (Test-Path $installShPath) {
        $fileSize = [math]::Round((Get-Item $installShPath).Length / 1KB, 2)
        Write-Host "✓ install.sh 下载完成！" -ForegroundColor Green
        Write-Host "  文件: $installShPath" -ForegroundColor White
        Write-Host "  大小: $fileSize KB" -ForegroundColor White
        $installShSuccess = $true
    } else {
        throw "下载完成但文件不存在"
    }
} catch {
    Write-Host "✗ install.sh 下载失败" -ForegroundColor Red
    Write-Host "  错误: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因：" -ForegroundColor Yellow
    Write-Host "  • chatgpt.com 被墙（需要 VPN）" -ForegroundColor White
    Write-Host "  • 网络连接问题" -ForegroundColor White
    Write-Host ""
    Write-Host "手动下载方法：" -ForegroundColor Cyan
    Write-Host "  在有 VPN 的环境运行：" -ForegroundColor White
    Write-Host "  curl -fsSL https://chatgpt.com/codex/install.sh -o resources\codex-cli\install.sh" -ForegroundColor Gray
}

Write-Host ""
Start-Sleep -Seconds 2

# ==================== 下载 Codex CLI tarball ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "[3/3] 下载 Codex CLI 安装包" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$tarballSuccess = $false
$installShPath = Join-Path $cliDir "install.sh"

if ($installShSuccess -and (Test-Path $installShPath)) {
    try {
        Write-Host "正在解析 install.sh 中的下载链接..." -ForegroundColor White
        Write-Host ""

        $installShContent = Get-Content $installShPath -Raw

        # 尝试多种模式提取 URL
        $patterns = @(
            'https?://[^\s"''`]+codex[^\s"''`]*linux[^\s"''`]*\.tar\.gz',
            'https?://cdn\.oaistatic\.com[^\s"''`]+\.tar\.gz',
            'CODEX_URL=["'']([^"'']+\.tar\.gz)["'']',
            'TARBALL_URL=["'']([^"'']+\.tar\.gz)["'']'
        )

        $tarballUrl = $null
        foreach ($pattern in $patterns) {
            if ($installShContent -match $pattern) {
                $tarballUrl = $matches[0] -replace '["''`]', ''
                if ($tarballUrl -match '^https?://') {
                    Write-Host "✓ 找到下载链接" -ForegroundColor Green
                    Write-Host "  URL: $tarballUrl" -ForegroundColor Gray
                    break
                }
            }
        }

        if (-not $tarballUrl) {
            # 如果没找到，尝试通用 URL
            $commonUrls = @(
                "https://cdn.oaistatic.com/codex/linux/codex-linux-x64-latest.tar.gz",
                "https://cdn.oaistatic.com/codex/codex-linux-x64.tar.gz"
            )

            Write-Host "未能从脚本中提取 URL，尝试常见下载地址..." -ForegroundColor Yellow
            Write-Host ""

            foreach ($url in $commonUrls) {
                try {
                    Write-Host "尝试: $url" -ForegroundColor Gray
                    $testResponse = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -ErrorAction Stop
                    if ($testResponse.StatusCode -eq 200) {
                        $tarballUrl = $url
                        Write-Host "✓ 找到可用链接" -ForegroundColor Green
                        break
                    }
                } catch {
                    Write-Host "  无法访问" -ForegroundColor Gray
                }
            }
        }

        if ($tarballUrl) {
            Write-Host ""
            Write-Host "开始下载 Codex CLI 安装包..." -ForegroundColor White
            Write-Host "预计大小: 50-100 MB，请耐心等待..." -ForegroundColor Yellow
            Write-Host ""

            $tarballPath = Join-Path $cliDir "codex-linux-x64.tar.gz"
            $ProgressPreference = 'Continue'
            Invoke-WebRequest -UseBasicParsing -Uri $tarballUrl -OutFile $tarballPath -TimeoutSec 300

            if (Test-Path $tarballPath) {
                $fileSize = [math]::Round((Get-Item $tarballPath).Length / 1MB, 2)
                Write-Host ""
                Write-Host "✓ Codex CLI 安装包下载完成！" -ForegroundColor Green
                Write-Host "  文件: $tarballPath" -ForegroundColor White
                Write-Host "  大小: $fileSize MB" -ForegroundColor White
                $tarballSuccess = $true
            } else {
                throw "下载完成但文件不存在"
            }
        } else {
            throw "无法确定 tarball 下载链接"
        }
    } catch {
        Write-Host ""
        Write-Host "✗ Codex CLI 安装包下载失败" -ForegroundColor Red
        Write-Host "  错误: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "手动下载方法：" -ForegroundColor Cyan
        Write-Host "  1. 查看 $installShPath" -ForegroundColor White
        Write-Host "  2. 找到包含 'tar.gz' 的下载 URL" -ForegroundColor White
        Write-Host "  3. 使用浏览器或 curl 下载" -ForegroundColor White
        Write-Host "  4. 保存到: $cliDir\codex-linux-x64.tar.gz" -ForegroundColor White
    }
} else {
    Write-Host "跳过（install.sh 未下载成功）" -ForegroundColor Gray
}

Write-Host ""
Start-Sleep -Seconds 2

# ==================== 下载完成汇总 ====================
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "下载完成汇总" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$statusTable = @(
    @{Name="Codex GUI 安装包"; Success=$guiSuccess},
    @{Name="Codex CLI 安装脚本"; Success=$installShSuccess},
    @{Name="Codex CLI 安装包"; Success=$tarballSuccess}
)

foreach ($item in $statusTable) {
    Write-Host "$($item.Name): " -NoNewline
    if ($item.Success) {
        Write-Host "✓ 已就绪" -ForegroundColor Green
    } else {
        Write-Host "✗ 缺失" -ForegroundColor Red
    }
}

Write-Host ""

if ($guiSuccess -and $installShSuccess -and $tarballSuccess) {
    # 计算总大小
    $totalSize = 0
    Get-ChildItem $resourcesDir -Recurse -File | ForEach-Object { $totalSize += $_.Length }
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)

    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "✓ 所有离线资源已下载完成！" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "资源总大小: $totalSizeMB MB" -ForegroundColor White
    Write-Host "预计最终 exe 大小: 约 $([math]::Round($totalSizeMB + 70, 0)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "下一步操作：" -ForegroundColor Cyan
    Write-Host "  1. 运行打包脚本：" -ForegroundColor White
    Write-Host "     powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. 生成的 exe 将支持：" -ForegroundColor White
    Write-Host "     ✓ 完全离线安装 Codex GUI" -ForegroundColor Green
    Write-Host "     ✓ 完全离线安装 Codex CLI" -ForegroundColor Green
    Write-Host "     ✓ 无需 VPN" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "⚠ 部分离线资源缺失" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "仍可以进行打包，但：" -ForegroundColor White
    Write-Host "  • 缺失的组件将使用在线安装模式" -ForegroundColor Yellow
    Write-Host "  • 在国内无 VPN 环境下可能安装失败" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "建议：" -ForegroundColor Cyan
    Write-Host "  • 确保 VPN 连接正常" -ForegroundColor White
    Write-Host "  • 重新运行此脚本" -ForegroundColor White
    Write-Host "  • 或按照上方提示手动下载缺失资源" -ForegroundColor White
    Write-Host ""
}
