# Tina-codex 助手

一键安装并汉化 Codex（OpenAI 官方 AI 编程工具）的 Windows 工具。

所有组件都走国内可直连来源，**无需 VPN**。

## 功能特性

- ✅ **一键安装 Codex GUI** —— 通过 `store.rg-adguard.net` 查询微软商店离线包，走微软 CDN 下载（国内可达）
- ✅ **一键安装 Codex CLI** —— Windows 原生方案：`npm install -g @openai/codex`，Node/npm 全走 npmmirror 国内镜像
- ✅ **自动安装 Git** —— 从 npmmirror 国内镜像下载 MinGit
- ✅ **注入中文插件市场** —— Tina-codex 中文插件生态
- ✅ **推荐插件自动安装** —— 浏览器、GitHub、文档处理等常用插件
- ✅ **配置备份** —— 注入前自动备份现有配置
- ✅ **不绑定任何模型服务** —— 不写入 API Key、base_url 或中转配置

## 为什么走这套方案

在国内安装 Codex 的主要障碍是境外网络：官方 CLI 安装脚本依赖 `chatgpt.com`（基本被墙）。本工具用国内可直连的来源绕开这个问题：

| 组件 | 来源 | 国内直连 |
|------|------|---------|
| Codex GUI | 微软商店离线包（`store.rg-adguard.net` 查询 + 微软 CDN） | ✅ |
| Codex CLI | npm 包 `@openai/codex`（registry 指向 npmmirror） | ✅ |
| Node.js（CLI 依赖） | npmmirror 二进制镜像 | ✅ |
| Git | npmmirror 二进制镜像（MinGit） | ✅ |

不依赖 WSL，不依赖任何自建服务器或 CDN。

## 快速开始

### 最终用户

1. 双击 `Tina-codex助手.exe`
2. 选择入口：
   - **快速注入/修复** —— 已安装 Codex，只注入中文插件市场（完全离线）
   - **一键完整安装** —— 全新电脑，自动安装 Codex GUI / CLI / Git，再注入插件市场
3. 完成

详见 [WINDOWS_USAGE.md](WINDOWS_USAGE.md)。

### 打包人员

需要在 **Windows** 机器上打包（PyInstaller 不能可靠地在 macOS 上交叉编译 Windows exe）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1
```

产物：`dist\Tina-codex助手.exe`（约 66 MB）。发给用户即可，用户无需安装 Python。

也可用 GitHub Actions 在 Windows runner 上自动打包（见仓库 Actions 配置）。

## 项目结构

```
tina-codex-assistant/
├── src/
│   └── tina_codex_assistant/
│       ├── cli.py                  # 命令行入口
│       ├── ui_app.py               # GUI 应用（pywebview）
│       ├── app_service.py          # 业务逻辑
│       ├── windows_installer.py    # Windows 安装脚本与计划
│       ├── injector.py             # 插件注入
│       ├── core.py                 # 路径解析、配置处理、cooper 检测
│       ├── resources.py            # 资源加载
│       └── ui/index.html           # GUI 界面
├── resources/
│   ├── plugin.zip                          # Tina-codex 插件包
│   └── statsig-zh-CN-raw-snapshot.json     # 汉化资源
├── scripts/
│   ├── build-windows.ps1           # Windows 打包脚本
│   └── prepare_resources.py        # 插件资源准备工具
├── tests/
├── TinaCodexAssistant.spec         # PyInstaller 配置
├── pyproject.toml
└── WINDOWS_USAGE.md
```

## 技术栈

- **Python 3.11+**
- **pywebview** —— 基于系统 WebView 的 GUI
- **PyInstaller** —— 打包为单文件 exe
- **PowerShell** —— Windows 安装脚本

## 工作原理

```
用户运行 exe
    ↓
检测系统状态（Codex GUI / CLI / Git 是否已安装）
    ↓
按需安装缺失组件（已安装的自动跳过）
    ├─ Codex GUI: store.rg-adguard.net 查询 → 微软 CDN 下 msixbundle → Add-AppxPackage
    ├─ Codex CLI: 确保 Node（缺则从 npmmirror 装便携版）→ npm registry 指向 npmmirror → npm i -g @openai/codex
    └─ Git:       从 npmmirror 下 MinGit → 加入用户 PATH
    ↓
注入 Tina-codex 插件市场
    ├─ 解压 plugin.zip 到 ~/.codex/tina-codex-plugins/
    ├─ 写入 config.toml 的 marketplace 配置
    └─ 复制 marketplace.json 到用户目录
    ↓
安装推荐插件（browser、github、superpowers 等）
    ↓
完成
```

## 开发

```powershell
# 安装依赖
pip install -e .

# 启动 GUI
tina-codex ui

# 命令行 dry-run（只生成计划，不执行）
tina-codex full-install --dry-run
```

测试：

```bash
pytest tests/
```

更新插件资源：

```bash
python scripts/prepare_resources.py
```

## 注意事项

### 不修改模型配置

本工具**不会**写入任何模型服务配置。用户需在 Codex 中自行配置：OpenAI 官方登录、API Key、自定义 OpenAI-compatible provider 或本地模型。

如果检测到用户已有的 cooper 模型配置，工具只会**提示并备份**，不会覆盖。

### 许可合规

重新分发 Codex 安装包前，请确认符合 OpenAI 的服务条款。

## 许可

MIT
