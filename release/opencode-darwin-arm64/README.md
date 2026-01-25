# OpenCode CLI 安装指南

> 适用于 macOS (Apple Silicon - M1/M2/M3/M4)

## 系统要求

- ✅ macOS (Apple Silicon)
- ✅ 无需安装 Node.js、Bun 或其他运行时
- ✅ 即开即用

## 快速安装

### 步骤 1: 解压文件

```bash
tar -xzf opencode-darwin-arm64.tar.gz
```

### 步骤 2: 安装到系统

**方式 A: 全局安装 (推荐,需要管理员权限)**

```bash
sudo mv opencode-darwin-arm64/bin/opencode /usr/local/bin/
```

**方式 B: 用户本地安装 (无需管理员权限)**

```bash
# 创建本地 bin 目录
mkdir -p ~/.local/bin

# 复制文件
cp opencode-darwin-arm64/bin/opencode ~/.local/bin/

# 添加到 PATH (如果还没有)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 步骤 3: 验证安装

```bash
opencode --version
```

如果看到版本号,说明安装成功! 🎉

## 开始使用

### 启动 OpenCode

```bash
opencode
```

### 在指定目录启动

```bash
cd /path/to/your/project
opencode
```

### 查看帮助

```bash
opencode --help
```

## 配置 (可选)

首次运行时,OpenCode 会引导你完成配置:

1. 选择 AI Provider (如 OpenAI, Anthropic 等)
2. 输入 API Key
3. 选择默认模型

配置文件位置: `~/.config/opencode/opencode.json`

## 卸载

### 全局安装的卸载

```bash
sudo rm /usr/local/bin/opencode
```

### 本地安装的卸载

```bash
rm ~/.local/bin/opencode
```

### 清理配置文件 (可选)

```bash
rm -rf ~/.config/opencode
rm -rf ~/.local/share/opencode
```

## 常见问题

### Q: 提示 "command not found: opencode"

**A:** 检查以下几点:

1. 确认已完成步骤 2 的安装
2. 如果使用本地安装,确认 `~/.local/bin` 在 PATH 中
3. 重新打开终端或运行 `source ~/.zshrc`

### Q: 提示 "Permission denied"

**A:** 添加执行权限:

```bash
chmod +x /usr/local/bin/opencode
# 或
chmod +x ~/.local/bin/opencode
```

### Q: macOS 提示 "无法验证开发者"

**A:** 首次运行时,macOS 可能会阻止:

1. 打开 "系统设置" > "隐私与安全性"
2. 找到 "仍要打开" 按钮并点击
3. 或者在终端运行: `xattr -d com.apple.quarantine /usr/local/bin/opencode`

### Q: 需要联网吗?

**A:**

- 安装和运行程序本身不需要网络
- 使用 AI 功能时需要网络连接到 AI Provider

### Q: 支持哪些 AI Provider?

**A:** OpenCode 支持多个 AI Provider:

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- 以及其他兼容 OpenAI API 的服务

## 获取帮助

如果遇到问题:

1. 查看日志: `~/.local/share/opencode/log/`
2. 查看官方文档: https://opencode.ai/docs
3. 联系内部技术支持

---

**版本**: 0.0.0-dev-202601250116  
**构建日期**: 2026-01-25  
**平台**: macOS ARM64
