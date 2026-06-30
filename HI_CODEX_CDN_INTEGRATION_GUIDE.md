# Hi-Codex CDN 集成使用指南

## ✅ 已完成的集成工作

我已经完成了 Hi-Codex CDN 的集成框架，现在只需要填入具体的 CDN 地址即可使用。

---

## 📝 配置步骤

### 步骤 1: 填入 CDN 地址

编辑文件：`src/tina_codex_assistant/cdn_config.py`

```python
HI_CODEX_CDN_CONFIG = {
    # Codex GUI 安装包 CDN 地址
    "gui": {
        "primary": "https://你的主CDN地址/codex-gui.msixbundle",
        "backup": "https://你的备用CDN地址/codex-gui.msixbundle",  # 可选
    },

    # Codex CLI 资源 CDN 地址
    "cli": {
        "install_script": "https://你的CDN地址/codex-install.sh",
        "tarball": "https://你的CDN地址/codex-linux-x64.tar.gz",
    },

    # 配置选项
    "options": {
        "timeout": 300,  # 下载超时时间（秒）
        "retry_times": 3,  # 重试次数
        "use_backup_on_failure": True,  # 主CDN失败时使用备用
    }
}
```

### 步骤 2: 替换为实际地址

**示例**（请替换为 Hi-Codex 团队的实际地址）:

```python
HI_CODEX_CDN_CONFIG = {
    "gui": {
        "primary": "https://cdn.hi-codex.com/downloads/codex-gui.msixbundle",
        "backup": "https://mirror.hi-codex.cn/downloads/codex-gui.msixbundle",
    },

    "cli": {
        "install_script": "https://cdn.hi-codex.com/downloads/codex-install.sh",
        "tarball": "https://cdn.hi-codex.com/downloads/codex-linux-x64.tar.gz",
    },

    "options": {
        "timeout": 300,
        "retry_times": 3,
        "use_backup_on_failure": True,
    }
}
```

### 步骤 3: 重新打包

```bash
# 在 Mac 上提交代码
cd /Users/epc/projects/tina-codex-assistant
git add .
git commit -m "feat: 集成 Hi-Codex CDN"
git push

# GitHub Actions 会自动打包
# 或者在 Windows 上手动打包
```

---

## 🎯 工作原理

### 安装优先级

```
检测 Codex 是否已安装
    ↓
如未安装，按以下优先级安装：

1. 离线安装包（如果打包时包含）
   ├─ 完全离线
   └─ 无需网络

2. Hi-Codex CDN（如果配置了 CDN 地址）⭐ 新增
   ├─ 国内高速
   ├─ 无需 VPN
   └─ 体积小（~70 MB）

3. 在线下载（回退方案）
   ├─ 需要网络
   └─ 可能需要 VPN
```

### 代码逻辑

```python
# 自动检测和使用 CDN
cdn_gui_urls = get_codex_gui_cdn()  # 获取配置的 CDN 地址
cdn_cli_urls = get_codex_cli_cdn()

# 构建安装计划时传入 CDN 地址
plan = build_full_install_plan(
    ...,
    cdn_gui_urls=cdn_gui_urls,  # 如果配置了，会优先使用
    cdn_cli_urls=cdn_cli_urls,
)
```

---

## 📦 打包后的效果

### 配置 CDN 后的版本

**文件名**: `Tina-codex助手-HiCodex版.exe`
**大小**: ~70 MB

**安装流程**:
```
用户双击运行
    ↓
选择"一键完整安装"
    ↓
从 Hi-Codex CDN 下载 Codex GUI (~300 MB)
    ↓
从 Hi-Codex CDN 下载 Codex CLI (~80 MB)
    ↓
安装 Git（国内镜像）
    ↓
注入中文插件市场（内置）
    ↓
完成！✅ 全程国内高速，无需 VPN
```

**优势**:
- ✅ exe 体积小（70 MB，像 Hi-Codex 一样）
- ✅ 国内高速下载
- ✅ 无需 VPN
- ✅ 可以随时更新 CDN 上的安装包

---

## 🔧 测试和验证

### 本地测试

```bash
# 测试 CDN 配置是否正确
python -c "
from src.tina_codex_assistant.cdn_config import *

print('CDN 配置状态:', has_cdn_configured())
print('GUI URLs:', get_codex_gui_cdn())
print('CLI URLs:', get_codex_cli_cdn())
"
```

### 验证安装逻辑

```bash
# Dry-run 测试
python -c "
from src.tina_codex_assistant.app_service import AppService
from src.tina_codex_assistant.core import EnvPaths

service = AppService(EnvPaths(), None)
result = service.full_install(execute_commands=False)

print('安装计划:')
for action in result['plan']['actions']:
    print(f'  - {action[\"key\"]}: {action[\"description\"]}')

print()
print('CDN 状态:', result.get('cdn_configured'))
print('CDN GUI URLs:', result.get('cdn_status', {}).get('gui_urls'))
"
```

---

## 📊 三种模式对比

| 模式 | exe 大小 | 安装方式 | 国内访问 | 配置要求 |
|------|---------|---------|---------|---------|
| **轻量版** | 66 MB | 在线下载 | ⚠️ 需 VPN | 无 |
| **Hi-Codex CDN 版** | 70 MB | CDN 下载 | ✅ 高速 | 需配置 CDN |
| **完全离线版** | 400-600 MB | 内置安装包 | ✅ 离线 | 需打包资源 |

---

## 🎁 最终效果

### 配置 CDN 前

```
Tina-codex助手.exe (66 MB)
├── 快速注入 → ✅ 完全离线
└── 完整安装 → ⚠️ 需要 VPN（Codex GUI/CLI 在线下载）
```

### 配置 CDN 后

```
Tina-codex助手-HiCodex版.exe (70 MB)
├── 快速注入 → ✅ 完全离线
└── 完整安装 → ✅ 国内高速，无需 VPN（使用 Hi-Codex CDN）
```

---

## ✅ 待办事项

### 你需要做的：

1. **提供 Hi-Codex 的 CDN 地址**
   - Codex GUI 下载链接
   - Codex CLI install.sh 链接
   - Codex CLI tarball 链接

2. **编辑 cdn_config.py**
   - 填入实际的 CDN 地址
   - 替换 `https://填入CDN地址/...` 部分

3. **提交并推送**
   ```bash
   git add src/tina_codex_assistant/cdn_config.py
   git commit -m "config: 配置 Hi-Codex CDN 地址"
   git push
   ```

4. **自动打包**
   - GitHub Actions 会自动生成新版本
   - 或者在 Windows 上手动打包

---

## 🚀 下一步

**现在请提供 Hi-Codex 团队的 CDN 地址：**

1. **Codex GUI 安装包 URL**: `_______________________`
2. **Codex CLI install.sh URL**: `_______________________`
3. **Codex CLI tarball URL**: `_______________________`

提供后，我会立即帮你填入配置并推送到 GitHub！🎉
