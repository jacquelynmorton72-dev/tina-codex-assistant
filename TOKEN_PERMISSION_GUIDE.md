# GitHub Token 权限配置详细指南

## 🎯 目标
创建一个有足够权限推送代码和工作流的 GitHub Token

---

## 📋 详细步骤（附截图说明）

### 步骤 1：访问 Token 设置页面

打开浏览器，访问：
```
https://github.com/settings/tokens
```

或者：
1. 点击右上角头像
2. 选择 `Settings`
3. 左侧滚动到最下面，找到 `Developer settings`
4. 点击 `Personal access tokens`
5. 选择 `Tokens (classic)`

---

### 步骤 2：删除旧 Token（如果存在）

如果你之前创建了 Token：
1. 找到名为 `tina-codex-assistant` 的 Token
2. 点击右侧的 `Delete` 按钮
3. 确认删除

---

### 步骤 3：生成新 Token

1. **点击**右上角的 `Generate new token` 按钮
2. **选择** `Generate new token (classic)`（不要选 Fine-grained token）

---

### 步骤 4：配置 Token 信息

#### Note（备注）
```
tina-codex-assistant-full-access
```

#### Expiration（过期时间）
选择以下之一：
- `No expiration`（推荐，永不过期）
- `90 days`（90 天后过期）

---

### 步骤 5：勾选权限（⚠️ 最重要！）

**必须勾选以下权限：**

#### ✅ repo（完整仓库访问权限）
```
✅ repo                          ← 勾选父级，会自动勾选所有子项
   ✅ repo:status
   ✅ repo_deployment
   ✅ public_repo
   ✅ repo:invite
   ✅ security_events
```

**如何勾选：**
- 直接勾选 `repo` 前面的复选框
- 会自动展开并勾选所有子项

---

#### ✅ workflow（工作流权限）
```
✅ workflow                      ← 单独勾选这一项
```

**这个权限非常重要！** 没有它就无法推送 `.github/workflows/` 中的文件。

---

#### 📝 完整权限清单

你的勾选应该看起来像这样：

```
□ repo
  ✅ repo                        ← 必须
     ✅ repo:status
     ✅ repo_deployment
     ✅ public_repo
     ✅ repo:invite
     ✅ security_events

□ admin:repo_hook
□ admin:org
□ admin:public_key
□ admin:org_hook
□ gist
□ notifications
□ user
□ delete_repo
□ write:discussion
□ write:packages
□ read:packages
□ delete:packages
□ admin:gpg_key

✅ workflow                      ← 必须

□ admin:enterprise
```

**只需要勾选：**
- ✅ `repo`（及其所有子项）
- ✅ `workflow`

其他都不需要勾选！

---

### 步骤 6：生成 Token

1. **滚动到页面最底部**
2. **点击**绿色的 `Generate token` 按钮

---

### 步骤 7：复制 Token

⚠️ **重要提示：**
- Token 只会显示一次！
- 必须立即复制保存
- 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**操作：**
1. 点击 Token 右侧的复制按钮 📋
2. 把 Token 粘贴到安全的地方（或直接发给我）

---

## 🎯 Token 权限检查清单

生成 Token 前，确认：

- [ ] 选择的是 `Tokens (classic)`，不是 Fine-grained token
- [ ] Note 填写了（如：`tina-codex-assistant-full-access`）
- [ ] Expiration 选择了（推荐 `No expiration`）
- [ ] **✅ 勾选了 `repo`**
- [ ] **✅ 勾选了 `workflow`**
- [ ] 点击了 `Generate token`
- [ ] 复制了生成的 Token

---

## 📸 关键截图参考

### 权限区域应该这样：

```
Select scopes

Scopes define the access for personal tokens. Read more about OAuth scopes.

✅ repo                                    Full control of private repositories
   ✅ repo:status                          Access commit status
   ✅ repo_deployment                      Access deployment status
   ✅ public_repo                          Access public repositories
   ✅ repo:invite                          Access repository invitations
   ✅ security_events                      Read and write security events

✅ workflow                                Update GitHub Action workflows
```

---

## ✅ 完成后

把生成的 Token（格式：`ghp_xxxxx...`）发给我，我会执行：

```bash
git push https://<YOUR_NEW_TOKEN>@github.com/jacquelynmorton72-dev/tina-codex-assistant.git main
```

---

## 🆘 常见问题

### Q1: 找不到 "workflow" 选项
**A:** 确保你选择的是 `Tokens (classic)`，不是 `Fine-grained tokens`

### Q2: Token 推送还是失败
**A:** 检查：
1. 是否勾选了 `repo` 和 `workflow`
2. Token 是否复制完整（没有多余空格）
3. 仓库是否属于你的账号

### Q3: Token 会过期吗？
**A:** 
- 如果选择 `No expiration`，不会过期
- 如果选择时间限制（如 90 days），到期后需要重新生成

### Q4: Token 安全吗？
**A:** 
- Token 等同于密码，不要分享给其他人
- 不要提交到公开代码仓库
- 使用完可以在 GitHub 删除

---

## 🚀 快速链接

- Token 设置页面：https://github.com/settings/tokens
- GitHub Token 文档：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

**配置好后，把新的 Token 发给我！** 格式：`ghp_xxxxx...`
