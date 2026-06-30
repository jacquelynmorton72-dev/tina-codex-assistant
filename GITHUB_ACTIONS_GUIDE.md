# GitHub Actions 配置指南

## ✅ 已完成的准备工作

- ✅ 代码已优化完成
- ✅ GitHub Actions 工作流已创建
- ✅ Git 仓库已初始化
- ✅ 所有文件已提交到本地仓库

---

## 📝 接下来你需要做的事情

### 第一步：创建 GitHub 仓库

1. **打开浏览器，访问 GitHub**
   - 网址：https://github.com
   - 如果没有账号，先注册（免费）

2. **创建新仓库**
   - 点击右上角的 `+` 号
   - 选择 `New repository`

3. **填写仓库信息**
   ```
   仓库名称：tina-codex-assistant（或其他名字）
   描述（可选）：Tina-codex 助手 - 一键安装和汉化 Codex
   
   可见性：
   - ✅ Public（公开，推荐） - GitHub Actions 免费无限使用
   - ⚠️ Private（私有） - GitHub Actions 有时长限制
   
   ❌ 不要勾选：
   - [ ] Add a README file
   - [ ] Add .gitignore
   - [ ] Choose a license
   
   （因为我们已经有这些文件了）
   ```

4. **点击 `Create repository`**

5. **复制仓库 URL**
   - 创建后会看到一个页面
   - 找到形如 `https://github.com/your-username/tina-codex-assistant.git` 的 URL
   - **复制这个 URL，告诉我**

---

## 第二步：推送代码到 GitHub

**告诉我你的仓库 URL 后，我会帮你执行以下命令：**

```bash
# 1. 添加远程仓库
git remote add origin <你的仓库 URL>

# 2. 推送到 GitHub
git push -u origin main
```

---

## 第三步：触发自动打包

推送成功后，你有两种方式触发打包：

### 方式 A：手动触发（推荐新手）

1. 进入你的 GitHub 仓库页面
2. 点击顶部的 **Actions** 标签
3. 左侧找到 **Build Windows EXE** 工作流
4. 点击右侧的 **Run workflow** 按钮
5. 点击绿色的 **Run workflow** 确认

### 方式 B：自动触发（创建 Release）

```bash
# 打一个版本标签
git tag v1.0.0
git push origin v1.0.0
```

---

## 第四步：下载生成的 exe

### 如果是手动触发：

1. 在 **Actions** 页面，等待构建完成（约 5-10 分钟）
2. 构建成功后，点击进入构建详情
3. 下方 **Artifacts** 区域会显示：
   - `Tina-codex助手-轻量版` 或
   - `Tina-codex助手-完全离线版`
4. 点击下载

### 如果是标签触发：

1. 进入仓库的 **Releases** 页面
2. 找到对应的版本
3. 下载 `Tina-codex助手.exe`

---

## 💡 常见问题

### Q1: 我还没有 GitHub 账号
**A:** 访问 https://github.com/signup 注册，完全免费，只需要邮箱。

### Q2: 创建公开仓库会泄露代码吗？
**A:** 
- 不会泄露敏感信息（已经通过 `.gitignore` 排除）
- 公开仓库可以让更多人受益
- 如果担心，可以创建私有仓库（但 Actions 有使用限制）

### Q3: GitHub Actions 要收费吗？
**A:** 
- **公开仓库**：完全免费，无限使用 ✅
- **私有仓库**：每月 2000 分钟免费额度（足够用）

### Q4: 离线资源怎么办？
**A:** 有三个选择：
1. **不上传离线资源**（推荐） - 打包轻量版（60MB）
2. **使用 Git LFS** - 可以存储大文件（需要额外配置）
3. **手动上传到 Release** - 在本地 Windows 打包完全离线版后上传

### Q5: 构建失败了怎么办？
**A:** 
1. 检查 Actions 页面的错误日志
2. 通常是依赖安装问题或路径问题
3. 可以在 Actions 页面重新运行

### Q6: 我能本地测试工作流吗？
**A:** 可以使用 [act](https://github.com/nektos/act) 工具在本地运行 GitHub Actions。

---

## 🎯 你现在需要做的

**只需要完成第一步：创建 GitHub 仓库**

1. 访问 https://github.com
2. 创建新仓库（名称：`tina-codex-assistant`）
3. 复制仓库 URL（类似：`https://github.com/your-username/tina-codex-assistant.git`）
4. **把 URL 告诉我**

然后我会帮你完成剩余的推送和配置工作！

---

## 📊 整个流程预览

```
你创建 GitHub 仓库
    ↓
告诉我仓库 URL
    ↓
我帮你推送代码到 GitHub
    ↓
你在 GitHub Actions 中点击 "Run workflow"
    ↓
等待 5-10 分钟（自动在 Windows 环境打包）
    ↓
下载生成的 exe
    ↓
完成！🎉
```

---

## 🚀 额外说明

### 本地代码状态

当前项目已经：
- ✅ 初始化 git 仓库
- ✅ 提交所有文件到本地
- ✅ 创建 GitHub Actions 工作流
- ⏳ 等待推送到 GitHub

### 工作流功能

GitHub Actions 会自动：
- ✅ 在 Windows Server 环境运行
- ✅ 安装 Python 3.12
- ✅ 安装 PyInstaller 和 pywebview
- ✅ 检查是否有离线资源
- ✅ 打包生成 exe
- ✅ 计算文件大小
- ✅ 上传构建产物
- ✅ （如果是标签触发）自动创建 Release

### 打包时长

- 首次构建：约 8-10 分钟（下载依赖）
- 后续构建：约 3-5 分钟（有缓存）

---

**准备好了吗？现在就去创建 GitHub 仓库，然后把 URL 告诉我！** 🚀
