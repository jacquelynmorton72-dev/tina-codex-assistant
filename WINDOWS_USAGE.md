# Tina-codex 助手 Windows 使用说明

## 给最终用户

拿到 `Tina-codex助手.exe` 后双击运行。

界面有两个入口：

- `快速注入/修复`：电脑上已经安装 Codex 时使用。它会注入 Tina-codex 中文插件市场，并备份现有配置。
- `一键完整安装`：新电脑或 Codex 不完整时使用。它会检查并安装 Codex GUI、Codex CLI、Git，然后注入插件市场。

### 无 VPN 说明

这个 exe 在国内无需 VPN 即可完成安装，因为所有组件都走国内可直连的来源：

- **Codex GUI**：通过 `store.rg-adguard.net` 查询微软商店离线包，再走微软 CDN 下载。微软 CDN 国内可达性较好。
- **Codex CLI**：通过 `npm install -g @openai/codex` 安装。如果没有 Node.js，会先从 npmmirror（淘宝）国内镜像下载便携版 Node。npm registry 也指向 npmmirror。
- **Git**：从 npmmirror 国内镜像下载 MinGit。

不依赖 WSL，全部是 Windows 原生安装。

### 注意

- 工具不会写入模型服务、API Key、Base URL 或默认中转配置。
- 用户需要在 Codex 里自行配置 OpenAI 登录、API Key、自定义 OpenAI-compatible provider 或本地模型。
- 如果检测到旧 Cooper 配置，工具只提示并备份，不会静默覆盖用户模型配置。

## 给打包人员

需要在 Windows 机器上打包，因为 PyInstaller 不能可靠地在 macOS 上直接生成 Windows exe。也可以用仓库里的 GitHub Actions 工作流在云端打包。

步骤：

1. 把整个 `tina-codex-assistant` 目录复制到 Windows。
2. 安装 Python 3.11+。如果没有 Python，可在 PowerShell 里运行：

```powershell
winget install Python.Python.3.12
```

3. 在项目目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1
```

4. 打包产物在：

```text
dist\Tina-codex助手.exe
```

把 `dist\Tina-codex助手.exe` 发给 Windows 用户即可。用户不需要 Python，文件约 60-70MB。

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
