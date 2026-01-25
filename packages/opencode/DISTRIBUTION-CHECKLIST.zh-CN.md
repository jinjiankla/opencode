# OpenCode CLI 分发包清单

## 📦 分发文件列表

### 必需文件

1. **二进制压缩包**
   - 文件: `opencode-darwin-arm64.tar.gz`
   - 大小: ~31MB
   - SHA256: `9fb36853e43b03bda26b7df167e892b9645e23311ec139a445eec8b3aee8f3d0`

2. **用户安装指南**
   - 文件: `INSTALL-USER.zh-CN.md`
   - 说明: 提供给最终用户的安装文档

### 可选文件

3. **校验和文件**
   - 文件: `opencode-darwin-arm64.tar.gz.sha256`
   - 用途: 验证文件完整性

## 📋 分发检查清单

在分发前,请确认:

- [ ] 二进制文件已构建并测试
- [ ] 压缩包已创建
- [ ] SHA256 校验和已生成
- [ ] 用户安装文档已准备
- [ ] 在干净环境中测试过安装流程
- [ ] 版本号已记录

## 🚀 分发步骤

### 1. 准备分发包

```bash
# 创建分发目录
mkdir -p release/opencode-darwin-arm64

# 复制必需文件
cp packages/opencode/dist/opencode-darwin-arm64.tar.gz release/opencode-darwin-arm64/
cp packages/opencode/dist/opencode-darwin-arm64.tar.gz.sha256 release/opencode-darwin-arm64/
cp packages/opencode/INSTALL-USER.zh-CN.md release/opencode-darwin-arm64/README.md

# 查看分发包
ls -lh release/opencode-darwin-arm64/
```

### 2. 验证分发包

```bash
cd release/opencode-darwin-arm64

# 验证校验和
shasum -a 256 -c opencode-darwin-arm64.tar.gz.sha256

# 测试解压
tar -tzf opencode-darwin-arm64.tar.gz

# 测试安装
tar -xzf opencode-darwin-arm64.tar.gz
./opencode-darwin-arm64/bin/opencode --version
```

### 3. 分发给用户

**方式 A: 文件共享**

```bash
# 压缩整个分发目录
cd release
zip -r opencode-darwin-arm64-release.zip opencode-darwin-arm64/

# 分发 opencode-darwin-arm64-release.zip
```

**方式 B: 内部文件服务器**

```bash
# 上传到文件服务器
scp -r release/opencode-darwin-arm64 user@fileserver:/path/to/downloads/
```

**方式 C: 企业内部 Git**

```bash
# 推送到内部 Git 仓库的 releases 分支
cd release
git init
git add .
git commit -m "Release opencode-darwin-arm64 v0.0.0-dev-202601250116"
git push origin releases
```

## 📝 给用户的说明

将以下内容发送给用户:

```
主题: OpenCode CLI 分发包

你好,

OpenCode CLI 已准备好供你使用。

下载地址: [内部文件服务器链接]

文件清单:
- opencode-darwin-arm64.tar.gz (31MB) - 主程序
- opencode-darwin-arm64.tar.gz.sha256 - 校验和文件
- README.md - 安装指南

安装步骤:
1. 下载 opencode-darwin-arm64.tar.gz
2. 验证校验和 (可选): shasum -a 256 -c opencode-darwin-arm64.tar.gz.sha256
3. 按照 README.md 中的说明安装

系统要求:
- macOS (Apple Silicon - M1/M2/M3/M4)
- 无需其他依赖

如有问题,请查看 README.md 或联系技术支持。
```

## 🔍 文件完整性验证

### 生成校验和

```bash
# SHA256
shasum -a 256 opencode-darwin-arm64.tar.gz > opencode-darwin-arm64.tar.gz.sha256

# MD5 (可选)
md5 opencode-darwin-arm64.tar.gz > opencode-darwin-arm64.tar.gz.md5
```

### 用户验证

```bash
# 验证 SHA256
shasum -a 256 -c opencode-darwin-arm64.tar.gz.sha256

# 验证 MD5
md5 -c opencode-darwin-arm64.tar.gz.md5
```

## 📊 版本信息

- **版本**: 0.0.0-dev-202601250116
- **构建日期**: 2026-01-25
- **平台**: macOS ARM64 (darwin-arm64)
- **Bun 版本**: 1.3.6
- **文件大小**:
  - 压缩包: ~31MB
  - 解压后: ~94MB

## 🎯 快速分发命令

```bash
#!/bin/bash
# quick-distribute.sh - 快速分发脚本

DIST_DIR="packages/opencode/dist"
RELEASE_DIR="release/opencode-darwin-arm64"

# 创建分发目录
mkdir -p "$RELEASE_DIR"

# 复制文件
cp "$DIST_DIR/opencode-darwin-arm64.tar.gz" "$RELEASE_DIR/"
cp "$DIST_DIR/opencode-darwin-arm64.tar.gz.sha256" "$RELEASE_DIR/"
cp "packages/opencode/INSTALL-USER.zh-CN.md" "$RELEASE_DIR/README.md"

# 创建发布包
cd release
zip -r opencode-darwin-arm64-release.zip opencode-darwin-arm64/

echo "✅ 分发包已准备好: release/opencode-darwin-arm64-release.zip"
ls -lh opencode-darwin-arm64-release.zip
```

## ✅ 分发完成

分发包已准备完毕,包含:

1. ✅ 二进制压缩包 (31MB)
2. ✅ SHA256 校验和
3. ✅ 用户安装指南

用户只需要下载压缩包,按照 README 安装即可使用!
