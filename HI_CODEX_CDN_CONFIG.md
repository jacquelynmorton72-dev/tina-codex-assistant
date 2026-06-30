# Hi-Codex CDN 集成配置

## CDN 地址配置

请填入 Hi-Codex 团队的 CDN 地址：

```python
# CDN 配置
HI_CODEX_CDN = {
    # Codex GUI 安装包 CDN 地址
    "codex_gui": "https://your-cdn.example.com/codex-gui.msixbundle",
    
    # Codex CLI 安装包 CDN 地址
    "codex_cli_tarball": "https://your-cdn.example.com/codex-linux-x64.tar.gz",
    
    # Codex CLI 安装脚本
    "codex_cli_script": "https://your-cdn.example.com/codex-install.sh",
    
    # 备用镜像（可选）
    "mirror_gui": "https://mirror2.example.com/codex-gui.msixbundle",
    "mirror_cli": "https://mirror2.example.com/codex-linux-x64.tar.gz",
}
```

## 实际地址

请提供以下信息：

1. **Codex GUI 安装包 CDN**:
   - 主 CDN: `_____________________`
   - 备用 CDN (可选): `_____________________`

2. **Codex CLI 安装包 CDN**:
   - install.sh: `_____________________`
   - tarball: `_____________________`

3. **访问控制**:
   - 是否需要 token/签名: [ ] 是 [ ] 否
   - 是否有 IP 限制: [ ] 是 [ ] 否
   - 是否有请求频率限制: [ ] 是 [ ] 否

---

## 集成方案

一旦提供了 CDN 地址，我会：

1. ✅ 创建 CDN 配置模块
2. ✅ 修改安装脚本使用 CDN 下载
3. ✅ 添加下载失败重试机制
4. ✅ 添加多镜像自动切换
5. ✅ 更新打包配置
6. ✅ 重新打包生成新版本

---

## 预期效果

集成后的 Tina-codex 助手：

- 📦 体积: ~70 MB（不含安装包）
- 🚀 安装速度: 快（使用 Hi-Codex CDN）
- 🇨🇳 国内访问: 无需 VPN
- ✅ 完全离线: 支持（如果下载到本地）

---

**请提供 Hi-Codex 团队的 CDN 地址，我立即开始集成！**
