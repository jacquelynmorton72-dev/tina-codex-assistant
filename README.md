# Tina-codex 助手

一键安装和汉化 Codex（OpenAI 的官方 AI 编程工具）的 Windows 工具。

## 功能特性

- ✅ **一键安装 Codex GUI** - 自动从 Microsoft Store 获取安装包
- ✅ **一键安装 Codex CLI** - 通过 WSL 自动安装命令行工具
- ✅ **自动安装 Git** - 使用国内镜像（npmmirror）下载 MinGit
- ✅ **注入中文插件市场** - Tina-codex 中文插件生态
- ✅ **推荐插件自动安装** - 浏览器、GitHub、文档处理等常用插件
- ✅ **配置备份** - 自动备份现有配置，安全可靠
- ✅ **Cooper 检测** - 智能检测并保护旧版 Cooper 配置
- ✅ **完全离线支持** - 可打包离线资源，无需 VPN 即可安装

## 为什么需要这个工具？

在国内使用 Codex 面临以下挑战：

1. **安装困难** - Codex CLI 官方安装脚本依赖 `chatgpt.com`（被墙）
2. **插件生态单一** - 官方插件市场功能有限
3. **中文支持不足** - 缺少针对中文用户的本地化插件

Tina-codex 助手解决了这些问题：

- 🌐 **离线安装模式** - 预打包安装资源，无需 VPN
- 🇨🇳 **国内镜像** - Git 使用淘宝 npmmirror，速度快
- 🔌 **丰富插件** - 集成 Tina-codex 中文插件市场
- 🛡️ **安全可靠** - 不修改模型配置，只注入插件市场

## 快速开始

### 最终用户

1. 获取 `Tina-codex助手.exe`
2. 双击运行
3. 选择：
   - **快速注入/修复** - 已安装 Codex，只需注入插件
   - **一键完整安装** - 新电脑，全自动安装 Codex + 插件

详细说明请查看 [WINDOWS_USAGE.md](WINDOWS_USAGE.md)

### 打包人员

#### 完全离线版（推荐）

在有 VPN 的 Windows 环境下：

```powershell
# 1. 下载离线资源
powershell -ExecutionPolicy Bypass -File scripts\download-offline-resources.ps1

# 2. 打包
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1
```

生成的 exe 包含所有安装包，支持无 VPN 环境。

#### 轻量版

直接打包（跳过下载离线资源）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows.ps1
```

生成的 exe 体积小，但需要网络下载 Codex。

## 项目结构

```
tina-codex-assistant/
├── src/
│   └── tina_codex_assistant/
│       ├── cli.py                    # 命令行入口
│       ├── ui_app.py                 # GUI 应用
│       ├── app_service.py            # 业务逻辑
│       ├── windows_installer.py      # Windows 安装脚本
│       ├── injector.py               # 插件注入逻辑
│       ├── core.py                   # 核心功能
│       ├── offline_resources.py      # 离线资源管理
│       ├── resources.py              # 资源加载
│       └── ui/
│           └── index.html            # GUI 界面
├── resources/
│   ├── plugin.zip                    # Tina-codex 插件包（54MB）
│   ├── statsig-zh-CN-raw-snapshot.json  # 汉化资源（1.8MB）
│   ├── codex-gui.msixbundle          # [可选] 离线 GUI 安装包
│   └── codex-cli/                    # [可选] 离线 CLI 资源
│       ├── install.sh
│       └── codex-linux-x64.tar.gz
├── scripts/
│   ├── download-offline-resources.ps1  # 下载离线资源
│   ├── build-windows.ps1              # 打包脚本
│   └── prepare_resources.py           # 资源准备工具
├── tests/                             # 测试
├── TinaCodexAssistant.spec            # PyInstaller 配置
├── pyproject.toml                     # Python 项目配置
└── WINDOWS_USAGE.md                   # 详细使用说明
```

## 技术栈

- **Python 3.11+** - 核心语言
- **pywebview** - 跨平台 GUI（基于系统 WebView）
- **PyInstaller** - 打包为单文件 exe
- **PowerShell** - Windows 安装脚本

## 工作原理

### 离线安装流程

```
用户运行 exe
    ↓
检测系统状态（Codex GUI/CLI/Git 是否已安装）
    ↓
优先使用内置离线资源安装
    ├─ Codex GUI: 使用 Add-AppxPackage 安装 msixbundle
    ├─ Codex CLI: 在 WSL 中离线安装
    └─ Git: 从 npmmirror 下载（国内镜像）
    ↓
注入 Tina-codex 插件市场
    ├─ 解压 plugin.zip 到 ~/.codex/tina-codex-plugins/
    ├─ 写入 config.toml 配置
    └─ 复制 marketplace.json 到用户目录
    ↓
安装推荐插件（browser、github、superpowers 等）
    ↓
完成 ✓
```

### 在线安装流程（回退方案）

如果没有离线资源，则：

- **Codex GUI** - 从 `store.rg-adguard.net` 获取 Microsoft Store 直链
- **Codex CLI** - 执行官方 `https://chatgpt.com/codex/install.sh`
- **Git** - 仍使用国内镜像（无需 VPN）

## 开发

### 本地运行

```powershell
# 安装依赖
pip install -e .

# 启动 GUI
tina-codex ui

# 命令行模式（dry-run）
tina-codex full-install --dry-run
```

### 测试

```bash
pytest tests/
```

### 更新插件资源

```bash
# 准备插件包（清理和重命名）
python scripts/prepare_resources.py
```

## 注意事项

### WSL 依赖

Codex CLI 需要 WSL（Windows Subsystem for Linux）。如果用户系统未启用 WSL：

```powershell
# 以管理员身份运行
wsl --install
# 重启电脑
```

### 模型配置

本工具**不会**修改模型配置，用户需要在 Codex 中自行配置：

- OpenAI 官方登录
- API Key
- 自定义 OpenAI-compatible provider
- 本地模型

### 许可合规

重新分发 Codex 安装包前，请确认符合 OpenAI 的服务条款。

## 版本对比

| 特性 | 完全离线版 | 轻量版 |
|------|-----------|--------|
| exe 大小 | ~300-600MB | ~60MB |
| Codex GUI 安装 | ✅ 离线 | ⚠️ 需要网络 |
| Codex CLI 安装 | ✅ 离线 | ⚠️ 需要网络 |
| Git 安装 | ✅ 国内镜像 | ✅ 国内镜像 |
| 汉化和插件 | ✅ 离线 | ✅ 离线 |
| 国内无 VPN 可用 | ✅ | ⚠️ |

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发分支

- `main` - 稳定版本
- `dev` - 开发分支

### 报告问题

请包含以下信息：

- Windows 版本
- 是否有 VPN
- 完整的错误日志
- 输出的 JSON 结果

## 许可

本项目采用 MIT 许可证。

## 致谢

- [Codex](https://openai.com/codex) - OpenAI 官方 AI 编程工具
- [pywebview](https://pywebview.flowrl.com/) - 跨平台 GUI 框架
- [npmmirror](https://npmmirror.com/) - 提供 Git for Windows 国内镜像

## 相关链接

- [Codex 官方文档](https://openai.com/codex)
- [Tina-codex 插件市场](https://github.com/tina-codex)
- [问题反馈](https://github.com/your-repo/issues)

---

**免责声明**：本工具仅用于简化 Codex 的安装和配置过程，不修改 Codex 核心功能。用户需遵守 OpenAI 服务条款。
