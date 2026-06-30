# Tina-codex助手 Windows 使用说明

## 给最终用户

拿到 `Tina-codex助手.exe` 后双击运行。

界面有两个入口：

- `快速注入/修复`：电脑上已经安装 Codex 时使用。它会注入 Tina-codex 中文插件市场，并备份现有配置。
- `一键完整安装`：新电脑或 Codex 不完整时使用。它会检查 Codex GUI、Codex CLI、Git/MinGit，然后注入插件市场。

注意：

- 工具不会写入模型服务、API Key、Base URL 或默认中转配置。
- 用户需要在 Codex 里自行配置 OpenAI 登录、API Key、自定义 OpenAI-compatible provider 或本地模型。
- 如果检测到旧 Cooper 配置，工具只提示并备份，不会静默覆盖用户模型配置。

### 关于离线安装

如果你拿到的是**完全离线版** exe（文件较大，约 300-600MB），则：

- ✅ **无需 VPN** 即可完成 Codex GUI 和 CLI 的安装
- ✅ Git 使用国内镜像（npmmirror），无需 VPN
- ✅ 汉化和插件完全离线

如果是**轻量版** exe（约 60MB），则：

- ⚠️ Codex GUI 安装需要访问 `store.rg-adguard.net`（可能需要 VPN）
- ⚠️ Codex CLI 安装需要访问 `chatgpt.com`（在国内需要 VPN）
- ✅ Git 和汉化功能无需 VPN

### WSL 依赖说明

Codex CLI 需要在 WSL（Windows Subsystem for Linux）中运行。如果你的 Windows 还没有启用 WSL，请：

1. 以管理员身份打开 PowerShell
2. 运行：`wsl --install`
3. 重启电脑
4. 然后再运行 Tina-codex助手

## 给打包人员

需要在 Windows 机器上打包，因为 PyInstaller 不能可靠地在 macOS 上直接生成 Windows exe。

### 准备离线资源（推荐）

为了支持无 VPN 环境下的完全离线安装，建议预先下载离线资源。

**在有 VPN 的 Windows 环境下运行：**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\download-offline-resources.ps1
```

此脚本会下载：
- Codex GUI 安装包（~200-500MB）
- Codex CLI 安装脚本和二进制（~50-100MB）

下载后文件位置：
```
resources/
├── codex-gui.msixbundle          # Codex GUI 安装包
└── codex-cli/
    ├── install.sh                # 安装脚本
    └── codex-linux-x64.tar.gz   # CLI 二进制
```

**不提供离线资源的影响：**
- 打包仍然可以进行
- 但在国内无 VPN 环境下，Codex GUI 和 CLI 安装可能失败
- 用户需要自行配置 VPN 或手动安装 Codex

### 打包步骤

1. 把整个 `tina-codex-assistant` 目录复制到 Windows。

2. 安装 Python 3.11+。如果没有 Python，可在 PowerShell 里运行：

```powershell
winget install Python.Python.3.12
```

3. 在项目目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1
```

脚本会：
- 检查离线资源状态
- 自动安装依赖（pyinstaller、pywebview）
- 打包生成 exe
- 显示文件大小和离线支持状态

4. 打包产物在：

```text
dist\Tina-codex助手.exe
```

把 `dist\Tina-codex助手.exe` 发给 Windows 用户即可。用户不需要 Python。

### 版本对比

| 版本 | exe 大小 | 无需 VPN | 说明 |
|------|---------|---------|------|
| **完全离线版** | ~300-600MB | ✅ | 包含所有安装包，推荐 |
| **轻量版** | ~60MB | ⚠️ | 在线下载，国内可能失败 |

## 开发调试

不打包时，可以在 Windows 项目目录运行：

```powershell
python -m pip install -e .
tina-codex ui
```

命令行 dry-run：

```powershell
tina-codex full-install --dry-run
```

## 常见问题

### Q: 为什么需要 WSL？
A: Codex CLI 是为 Linux 环境设计的，在 Windows 上需要通过 WSL 运行。

### Q: 离线资源下载失败怎么办？
A: 确保在有 VPN 的环境下运行 `download-offline-resources.ps1`。如果仍失败，可以：
1. 使用轻量版（跳过离线资源）
2. 让用户自行安装 Codex 后使用"快速注入/修复"功能

### Q: 打包后 exe 很大怎么办？
A: 这是因为包含了离线安装包。可以：
1. 同时提供轻量版和完全离线版
2. 使用压缩工具（如 7-Zip）压缩 exe 分发

### Q: 能跨版本打包吗（在 macOS 打包 Windows exe）？
A: PyInstaller 不支持可靠的交叉编译。必须在 Windows 上打包 Windows exe。
