# Tina-codex 助手无 VPN 环境改进方案

## 问题诊断

当前工具在国内无 VPN 环境下存在以下阻塞点：

1. **Codex GUI 安装**：依赖 `store.rg-adguard.net`（境外服务，可能被墙）
2. **Codex CLI 安装**：依赖 `chatgpt.com`（已被墙，100% 失败）

## 方案 A：预打包离线资源（推荐）

### 架构设计

```
resources/
├── plugin.zip                          # 已有
├── statsig-zh-CN-raw-snapshot.json     # 已有
├── codex-gui.msixbundle               # 新增：Codex GUI 安装包（~200-500MB）
└── codex-cli/                          # 新增：Codex CLI 离线安装
    ├── install.sh
    ├── codex-linux-x64.tar.gz
    └── README.md
```

### 实现清单

#### 1. 下载并打包 Codex GUI

**手动步骤**（在有 VPN 的环境下执行一次）：

```powershell
# 获取最新版本的直链
$body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
$response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body
$link = $response.Links | Where-Object { $_.href -match '\.(msixbundle|appxbundle)' } | Select-Object -ExpandProperty href -First 1

# 下载到 resources/
Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile "resources\codex-gui.msixbundle"
```

**更新 `windows_installer.py`**：

```python
# 新增函数
def install_codex_gui_offline(pkg_path: Path) -> str:
    """使用预打包的安装包安装 Codex GUI"""
    return f"""
$ErrorActionPreference = 'Stop'
$pkg = '{pkg_path.as_posix()}'
if (-not (Test-Path $pkg)) {{ throw '未找到离线安装包：$pkg' }}
Add-AppxPackage -Path $pkg -ForceApplicationShutdown
"""

# 修改 build_full_install_plan
def build_full_install_plan(
    codex_cli_found: bool, 
    codex_gui_found: bool, 
    git_found: bool,
    offline_gui_pkg: Path | None = None,  # 新增参数
) -> InstallPlan:
    actions: list[InstallAction] = []
    if codex_gui_found:
        actions.append(InstallAction("check_codex_gui", "Codex GUI 已检测到", []))
    else:
        if offline_gui_pkg and offline_gui_pkg.exists():
            # 优先使用离线包
            actions.append(
                InstallAction(
                    "install_codex_gui_offline",
                    "使用离线安装包安装 Codex GUI",
                    [install_codex_gui_offline(offline_gui_pkg)],
                )
            )
        else:
            # 回退到在线安装
            actions.append(
                InstallAction(
                    "install_codex_gui",
                    "通过 Microsoft Store 包链路安装或修复 Codex GUI（需要网络）",
                    [CODEX_GUI_INSTALL_SCRIPT],
                )
            )
    # ... 其余代码
```

#### 2. 处理 Codex CLI 离线安装

**手动下载**（在有 VPN 的环境下执行一次）：

```bash
# 下载官方安装脚本和二进制
mkdir -p resources/codex-cli
curl -fsSL https://chatgpt.com/codex/install.sh > resources/codex-cli/install.sh

# 下载 Linux 二进制（WSL 使用）
# 需要从安装脚本中提取真实下载地址
# 假设为：
curl -fsSL https://cdn.oaistatic.com/codex/codex-linux-x64.tar.gz \
  -o resources/codex-cli/codex-linux-x64.tar.gz
```

**更新 `windows_installer.py`**：

```python
def install_codex_cli_offline(cli_dir: Path) -> str:
    """使用离线资源在 WSL 中安装 Codex CLI"""
    install_sh = cli_dir / "install.sh"
    tarball = cli_dir / "codex-linux-x64.tar.gz"
    return f"""
$ErrorActionPreference = 'Stop'
$installSh = '{install_sh.as_posix()}'
$tarball = '{tarball.as_posix()}'

# 检查 WSL
wsl.exe --status | Out-Null
if ($LASTEXITCODE -ne 0) {{ throw 'WSL 未安装或未启动' }}

# 复制到 WSL 并安装
$wslInstallSh = '/tmp/codex-install.sh'
$wslTarball = '/tmp/codex-linux-x64.tar.gz'

wsl.exe cp (wsl.exe wslpath -a $installSh) $wslInstallSh
wsl.exe cp (wsl.exe wslpath -a $tarball) $wslTarball

# 修改安装脚本使用本地 tarball 而非下载
wsl.exe sh -c "sed -i 's|curl.*codex.*tar.gz|cp /tmp/codex-linux-x64.tar.gz|' $wslInstallSh"
wsl.exe sh -lc "sh $wslInstallSh"
"""
```

#### 3. 更新资源管理

**新建 `src/tina_codex_assistant/offline_resources.py`**：

```python
from __future__ import annotations
from pathlib import Path
from .resources import resource_path

def get_offline_codex_gui() -> Path | None:
    """获取离线 Codex GUI 安装包路径"""
    candidates = [
        resource_path("codex-gui.msixbundle"),
        resource_path("codex-gui.appxbundle"),
    ]
    for path in candidates:
        if path and path.exists():
            return path
    return None

def get_offline_codex_cli_dir() -> Path | None:
    """获取离线 Codex CLI 资源目录"""
    cli_dir = resource_path("codex-cli")
    if cli_dir and cli_dir.exists() and (cli_dir / "install.sh").exists():
        return cli_dir
    return None
```

**更新 `app_service.py`**：

```python
from .offline_resources import get_offline_codex_gui, get_offline_codex_cli_dir

class TinaCodexService:
    def full_install(self, timestamp: str | None = None, execute_commands: bool = True) -> dict:
        paths = resolve_codex_paths(self.env)
        
        # 检测离线资源
        offline_gui = get_offline_codex_gui()
        offline_cli_dir = get_offline_codex_cli_dir()
        
        plan = build_full_install_plan(
            codex_cli_found=self._detect_codex_cli(),
            codex_gui_found=self._detect_codex_gui(),
            git_found=self._detect_git(),
            offline_gui_pkg=offline_gui,  # 传递离线资源
            offline_cli_dir=offline_cli_dir,
        )
        # ... 其余代码
```

#### 4. 更新 PyInstaller 配置

**修改 `TinaCodexAssistant.spec`**：

```python
datas=[
    (str(root / "resources" / "plugin.zip"), "resources"),
    (str(root / "resources" / "statsig-zh-CN-raw-snapshot.json"), "resources"),
    (str(root / "src" / "tina_codex_assistant" / "ui" / "index.html"), "src/tina_codex_assistant/ui"),
    # 新增
    (str(root / "resources" / "codex-gui.msixbundle"), "resources"),
    (str(root / "resources" / "codex-cli"), "resources/codex-cli"),
],
```

#### 5. 更新打包脚本

**修改 `scripts/build-windows.ps1`**：

```powershell
# 在开头添加检查
$offlineResources = @(
    "resources\codex-gui.msixbundle",
    "resources\codex-cli\install.sh",
    "resources\codex-cli\codex-linux-x64.tar.gz"
)

$missing = $offlineResources | Where-Object { -not (Test-Path $_) }
if ($missing) {
    Write-Warning "缺少以下离线资源，将回退到在线安装模式："
    $missing | ForEach-Object { Write-Warning "  - $_" }
    Write-Warning "如需完全离线支持，请在有 VPN 的环境下运行 scripts/download-offline-resources.ps1"
}
```

**新建 `scripts/download-offline-resources.ps1`**：

```powershell
# 自动下载离线资源的脚本（需要在有网络的环境执行）
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "正在下载 Codex GUI 安装包..."
$body = 'type=PackageFamilyName&url=openai.codex&ring=Retail&lang=zh-CN'
$response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'https://store.rg-adguard.net/api/GetFiles' -Body $body
$link = $response.Links | Where-Object { $_.href -match '\.(msixbundle|appxbundle)' } | Select-Object -ExpandProperty href -First 1
if (-not $link) { throw '未找到 Codex GUI 安装包链接' }
Invoke-WebRequest -UseBasicParsing -Uri $link -OutFile "resources\codex-gui.msixbundle"
Write-Host "✓ 下载完成：codex-gui.msixbundle"

Write-Host "正在下载 Codex CLI 资源..."
New-Item -ItemType Directory -Force -Path "resources\codex-cli" | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "https://chatgpt.com/codex/install.sh" -OutFile "resources\codex-cli\install.sh"

# 需要手动从安装脚本中提取真实 tarball URL
Write-Warning "Codex CLI tarball 需要手动从 install.sh 中提取 URL 并下载"
Write-Host "请检查 install.sh 中的下载链接，然后运行："
Write-Host '  Invoke-WebRequest -Uri "<URL>" -OutFile "resources\codex-cli\codex-linux-x64.tar.gz"'
```

#### 6. 更新文档

**修改 `WINDOWS_USAGE.md`**：

```markdown
## 给打包人员

### 准备离线资源（可选，推荐）

为了支持无 VPN 环境下的完整安装，需要预先下载以下资源：

1. 在有 VPN 的 Windows 环境下运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\download-offline-resources.ps1
```

2. 手动完成 Codex CLI tarball 下载（脚本会给出提示）

**不提供离线资源的影响**：
- Codex GUI 安装需要访问 `store.rg-adguard.net`
- Codex CLI 安装需要访问 `chatgpt.com`
- 在国内无 VPN 环境下可能失败

### 打包

然后按原步骤打包即可，离线资源会自动打包进 exe。
```

---

## 方案 B：国内镜像源（需要额外基础设施）

如果有团队维护能力，可以：

1. 搭建 Codex GUI 的国内镜像站
2. 搭建 Codex CLI 的国内镜像/CDN
3. 在代码中添加镜像源配置切换逻辑

**优点**：exe 体积小，易于更新

**缺点**：需要持续维护服务器，成本高

---

## 方案 C：混合模式（最佳用户体验）

结合方案 A 和在线安装：

1. 优先检测是否能访问官方源（网络探测）
2. 如果能访问，使用在线安装（下载最新版本）
3. 如果不能访问，使用离线包（回退方案）
4. 在 UI 中显示当前使用的安装模式

**实现**：

```python
def check_network_access(url: str, timeout: int = 5) -> bool:
    """检测是否能访问指定 URL"""
    try:
        response = subprocess.run(
            ["powershell", "-Command", f"(Invoke-WebRequest -Uri '{url}' -TimeoutSec {timeout} -UseBasicParsing).StatusCode"],
            capture_output=True,
            timeout=timeout + 1,
        )
        return response.returncode == 0
    except:
        return False

# 在 build_full_install_plan 中使用
can_access_store = check_network_access("https://store.rg-adguard.net")
can_access_openai = check_network_access("https://chatgpt.com")
```

---

## 体积影响估算

| 资源 | 估算大小 | 备注 |
|-----|---------|------|
| 当前 exe | ~60MB | plugin.zip + Python + pywebview |
| + Codex GUI | +200-500MB | msixbundle |
| + Codex CLI | +50-100MB | Linux tarball |
| **最终 exe** | **~300-650MB** | 完全离线版本 |

**优化建议**：
- 使用 7-Zip 自解压格式（SFX）压缩资源
- 或者提供两个版本：轻量在线版（60MB）、完全离线版（~400MB）

---

## 实施优先级

1. **P0（必需）**：实现离线 Codex CLI 安装逻辑（目前 100% 失败）
2. **P1（重要）**：实现离线 Codex GUI 安装逻辑
3. **P2（优化）**：添加网络检测和混合模式
4. **P3（体验）**：UI 中显示安装模式和进度条

---

## 风险提示

1. **版本更新**：离线包需要定期更新，建议每月检查一次
2. **许可合规**：确认重新分发 Codex 安装包符合 OpenAI 的服务条款
3. **体积问题**：用户需要下载较大的 exe，考虑提供两个版本
4. **WSL 依赖**：Codex CLI 安装仍需要 WSL，无法完全绕过

---

## 测试清单

- [ ] 完全离线环境下测试 Codex GUI 安装
- [ ] 完全离线环境下测试 Codex CLI 安装
- [ ] 测试在线安装失败后的回退逻辑
- [ ] 测试混合模式的网络检测
- [ ] 测试大体积 exe 的打包和运行
- [ ] 在干净的 Windows 11 虚拟机上全流程测试
