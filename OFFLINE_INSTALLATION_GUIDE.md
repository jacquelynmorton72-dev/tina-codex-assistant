# 实现完全离线安装 Codex 的方案

## 🎯 目标
让 Tina-codex 助手能够在无网络/无 VPN 环境下完整安装 Codex GUI 和 CLI

## 📦 需要预先打包的资源

### 1. Codex GUI 安装包
**文件**: `codex-gui.msixbundle` 或 `codex-gui.appxbundle`
**大小**: ~200-500 MB
**获取方式**: 从 Microsoft Store 下载

#### 下载方法 A：使用 store.rg-adguard.net
```powershell
$body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
$response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body
$link = $response.Links | Where-Object { $_.href -match '\.(msixbundle|appxbundle)' } | Select-Object -ExpandProperty href -First 1
Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile "codex-gui.msixbundle"
```

#### 下载方法 B：从 Microsoft Store 缓存提取
如果你的 Windows 电脑已安装 Codex：
```powershell
# 查找已安装的 Codex 包
Get-AppxPackage | Where-Object { $_.Name -like "*codex*" }

# 导出安装包
$package = Get-AppxPackage -Name "openai.codex"
Export-AppxPackage -Package $package.PackageFullName -OutputPath "C:\temp\codex-export"
```

#### 下载方法 C：使用官方 CDN 直链
```
https://cdn.oaistatic.com/codex/windows/Codex-xxx.msixbundle
```
（需要找到具体版本号）

### 2. Codex CLI 安装资源
**文件**: 
- `install.sh` - 安装脚本
- `codex-linux-x64.tar.gz` - Linux 二进制文件

**大小**: ~50-100 MB

#### 下载方法：
```bash
# 下载安装脚本
curl -fsSL https://chatgpt.com/codex/install.sh -o install.sh

# 从脚本中提取 tarball URL
# 通常是类似：https://cdn.oaistatic.com/codex/linux/codex-linux-x64-xxx.tar.gz

# 手动下载 tarball
curl -fsSL <extracted-url> -o codex-linux-x64.tar.gz
```

---

## 🛠️ 实施方案

### 步骤 1：在有 VPN 的环境下载资源

创建一个增强版的下载脚本：

```powershell
# scripts/download-offline-resources-enhanced.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Codex 完全离线资源下载工具 ===" -ForegroundColor Cyan
Write-Host ""

$resourcesDir = "resources"
New-Item -ItemType Directory -Force -Path $resourcesDir | Out-Null

# 1. 下载 Codex GUI
Write-Host "[1/3] 下载 Codex GUI 安装包..." -ForegroundColor Yellow

try {
    # 方法 1: 尝试从 store.rg-adguard.net 获取
    Write-Host "  正在查询 Microsoft Store 链接..."
    $body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
    $response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body -TimeoutSec 30
    
    $link = $response.Links | Where-Object { $_.href -match '\.(msixbundle|appxbundle)' } | Select-Object -ExpandProperty href -First 1
    
    if ($link) {
        Write-Host "  找到下载链接：$link"
        $ext = if ($link -match '\.msixbundle') { '.msixbundle' } else { '.appxbundle' }
        $outputPath = Join-Path $resourcesDir "codex-gui$ext"
        
        Write-Host "  正在下载... (预计 200-500 MB，请耐心等待)"
        Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile $outputPath
        
        $size = [math]::Round((Get-Item $outputPath).Length / 1MB, 2)
        Write-Host "  ✓ Codex GUI 下载完成！($size MB)" -ForegroundColor Green
    } else {
        throw "未找到下载链接"
    }
} catch {
    Write-Host "  ✗ 自动下载失败：$_" -ForegroundColor Red
    Write-Host ""
    Write-Host "  请手动下载 Codex GUI：" -ForegroundColor Yellow
    Write-Host "  1. 访问 Microsoft Store 搜索 'Codex'" -ForegroundColor White
    Write-Host "  2. 或使用以下工具：" -ForegroundColor White
    Write-Host "     https://store.rg-adguard.net/" -ForegroundColor Cyan
    Write-Host "  3. 下载后放到：$resourcesDir\codex-gui.msixbundle" -ForegroundColor White
}

Write-Host ""

# 2. 下载 Codex CLI install.sh
Write-Host "[2/3] 下载 Codex CLI 安装脚本..." -ForegroundColor Yellow

$cliDir = Join-Path $resourcesDir "codex-cli"
New-Item -ItemType Directory -Force -Path $cliDir | Out-Null

try {
    Write-Host "  正在下载 install.sh..."
    Invoke-WebRequest -UseBasicParsing -Uri "https://chatgpt.com/codex/install.sh" -OutFile (Join-Path $cliDir "install.sh") -TimeoutSec 30
    Write-Host "  ✓ install.sh 下载完成！" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 下载失败：$_" -ForegroundColor Red
    Write-Host "  需要 VPN 访问 chatgpt.com" -ForegroundColor Yellow
}

Write-Host ""

# 3. 下载 Codex CLI tarball
Write-Host "[3/3] 下载 Codex CLI 安装包..." -ForegroundColor Yellow

$installShPath = Join-Path $cliDir "install.sh"
if (Test-Path $installShPath) {
    try {
        Write-Host "  正在解析 tarball 下载链接..."
        
        # 读取 install.sh 并提取下载 URL
        $installShContent = Get-Content $installShPath -Raw
        
        # 常见的 URL 模式
        $patterns = @(
            'https?://[^\s"'']+codex[^\s"'']*linux[^\s"'']*\.tar\.gz',
            'https?://cdn\.oaistatic\.com[^\s"'']+\.tar\.gz',
            'CODEX_URL=["'']([^"'']+)["'']'
        )
        
        $tarballUrl = $null
        foreach ($pattern in $patterns) {
            if ($installShContent -match $pattern) {
                $tarballUrl = $matches[0] -replace '["'']', ''
                break
            }
        }
        
        if ($tarballUrl) {
            Write-Host "  找到下载链接：$tarballUrl"
            Write-Host "  正在下载... (预计 50-100 MB，请耐心等待)"
            
            Invoke-WebRequest -UseBasicParsing -Uri $tarballUrl -OutFile (Join-Path $cliDir "codex-linux-x64.tar.gz") -TimeoutSec 120
            
            $size = [math]::Round((Get-Item (Join-Path $cliDir "codex-linux-x64.tar.gz")).Length / 1MB, 2)
            Write-Host "  ✓ Codex CLI tarball 下载完成！($size MB)" -ForegroundColor Green
        } else {
            throw "无法从 install.sh 中提取下载链接"
        }
    } catch {
        Write-Host "  ✗ 自动下载失败：$_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  请手动下载 Codex CLI：" -ForegroundColor Yellow
        Write-Host "  1. 查看 $installShPath" -ForegroundColor White
        Write-Host "  2. 找到 tarball 下载 URL（通常包含 'codex-linux-x64.tar.gz'）" -ForegroundColor White
        Write-Host "  3. 手动下载后放到：$cliDir\codex-linux-x64.tar.gz" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "下载完成汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查资源状态
$guiExists = Test-Path "$resourcesDir\codex-gui.*"
$cliInstallExists = Test-Path (Join-Path $cliDir "install.sh")
$cliTarballExists = Test-Path (Join-Path $cliDir "codex-linux-x64.tar.gz")

Write-Host "Codex GUI 安装包：" -NoNewline
if ($guiExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host "Codex CLI 安装脚本：" -NoNewline
if ($cliInstallExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host "Codex CLI 安装包：" -NoNewline
if ($cliTarballExists) { Write-Host "✓ 已就绪" -ForegroundColor Green } else { Write-Host "✗ 缺失" -ForegroundColor Red }

Write-Host ""

if ($guiExists -and $cliInstallExists -and $cliTarballExists) {
    Write-Host "✓ 所有离线资源已下载完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "  运行 scripts\build-windows.ps1 进行打包" -ForegroundColor White
    Write-Host "  打包后的 exe 将支持完全离线安装（无需 VPN）" -ForegroundColor White
    Write-Host ""
    
    # 计算总大小
    $totalSize = 0
    Get-ChildItem $resourcesDir -Recurse -File | ForEach-Object { $totalSize += $_.Length }
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host "资源总大小：$totalSizeMB MB" -ForegroundColor White
    Write-Host "预计最终 exe 大小：约 $([math]::Round($totalSizeMB + 70, 0)) MB" -ForegroundColor White
} else {
    Write-Host "⚠ 部分离线资源缺失" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "可以继续打包，但缺失的组件将使用在线安装模式" -ForegroundColor Yellow
    Write-Host "在国内无 VPN 环境下可能安装失败" -ForegroundColor Yellow
}

Write-Host ""
```

---

## 📝 完整实施步骤

### 1. 在有 VPN 的 Windows 环境

```powershell
# 克隆项目
git clone https://github.com/jacquelynmorton72-dev/tina-codex-assistant.git
cd tina-codex-assistant

# 下载完全离线资源
powershell -ExecutionPolicy Bypass -File scripts\download-offline-resources-enhanced.ps1

# 确认资源已下载
ls resources\
# 应该看到：
# - codex-gui.msixbundle (~300 MB)
# - codex-cli\install.sh
# - codex-cli\codex-linux-x64.tar.gz (~80 MB)
```

### 2. 打包成完全离线版

```powershell
# 打包（会自动检测并包含离线资源）
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1

# 生成的 exe 位于：
# dist\Tina-codex助手.exe (~400-600 MB)
```

### 3. 分发给用户

用户拿到这个 400-600 MB 的 exe 后：
- ✅ 完全离线运行
- ✅ 无需 VPN
- ✅ 自动安装 Codex GUI（使用内置安装包）
- ✅ 自动安装 Codex CLI（使用内置资源）
- ✅ 自动注入中文插件市场

---

## 🎯 关键区别

### 当前轻量版 (66 MB)
```
exe 包含：
├── 插件和汉化 (56 MB)
└── Python + 脚本 (10 MB)

安装时：
├── Codex GUI → 在线下载 (需要网络)
├── Codex CLI → 在线下载 (需要 VPN)
└── 插件注入 → 使用内置资源 (离线)
```

### 完全离线版 (400-600 MB)
```
exe 包含：
├── 插件和汉化 (56 MB)
├── Python + 脚本 (10 MB)
├── Codex GUI 安装包 (300 MB)
└── Codex CLI 资源 (80 MB)

安装时：
├── Codex GUI → 使用内置安装包 (离线)
├── Codex CLI → 使用内置资源 (离线)
└── 插件注入 → 使用内置资源 (离线)
```

---

## ⚡ 立即行动

我现在可以帮你：

1. **更新下载脚本** - 创建增强版资源下载工具
2. **验证打包配置** - 确保离线资源正确打包
3. **准备使用指南** - 说明如何获取完全离线版

你需要做的是：
- 找一台有 VPN 的 Windows 电脑
- 运行下载脚本获取 Codex 安装包
- 重新打包

**要我现在更新项目代码吗？**
