# OpenCode CLI 二次分发指南

## 概述

`opencode-darwin-arm64.tar.gz` 是一个**完全独立的二进制分发包**,可以直接分发给其他开发人员使用,无需任何额外依赖。

## ✅ 分发包特点

### 完全自包含

- ✅ **单一可执行文件**: 所有依赖都已打包进二进制文件
- ✅ **无需 Node.js/Bun**: 用户机器上不需要安装 Bun 或 Node.js
- ✅ **无需 npm install**: 不需要安装任何 npm 包
- ✅ **即开即用**: 解压后直接运行

### 包内容

```
opencode-darwin-arm64.tar.gz (31MB)
└── opencode-darwin-arm64/
    ├── bin/
    │   └── opencode          # 可执行文件 (94MB)
    └── package.json          # 版本信息
```

## 📦 分发方式

### 方式一: 直接分发压缩包

最简单的方式,直接将 `.tar.gz` 文件分发给开发人员:

```bash
# 分发这个文件
packages/opencode/dist/opencode-darwin-arm64.tar.gz
```

**用户安装步骤:**

```bash
# 1. 解压
tar -xzf opencode-darwin-arm64.tar.gz

# 2. 移动到系统路径
sudo mv opencode-darwin-arm64/bin/opencode /usr/local/bin/

# 3. 验证
opencode --version
```

### 方式二: 仅分发二进制文件

如果只需要分发可执行文件:

```bash
# 分发这个文件
packages/opencode/dist/opencode-darwin-arm64/bin/opencode
```

**用户安装步骤:**

```bash
# 1. 添加执行权限
chmod +x opencode

# 2. 移动到系统路径
sudo mv opencode /usr/local/bin/

# 3. 验证
opencode --version
```

### 方式三: 通过内部文件服务器

适合企业内部分发:

```bash
# 上传到文件服务器
scp packages/opencode/dist/opencode-darwin-arm64.tar.gz \
    user@fileserver:/path/to/downloads/

# 用户下载
wget http://fileserver/downloads/opencode-darwin-arm64.tar.gz
tar -xzf opencode-darwin-arm64.tar.gz
sudo mv opencode-darwin-arm64/bin/opencode /usr/local/bin/
```

## 🎯 给用户的安装文档

你可以提供以下安装文档给其他开发人员:

```markdown
# OpenCode CLI 安装指南

## 系统要求

- macOS (Apple Silicon - M1/M2/M3)
- 无需安装 Node.js 或其他运行时

## 快速安装

### 方法一: 全局安装 (推荐)

\`\`\`bash

# 解压

tar -xzf opencode-darwin-arm64.tar.gz

# 安装到系统

sudo mv opencode-darwin-arm64/bin/opencode /usr/local/bin/

# 验证安装

opencode --version
\`\`\`

### 方法二: 用户本地安装

\`\`\`bash

# 创建本地 bin 目录

mkdir -p ~/.local/bin

# 解压并复制

tar -xzf opencode-darwin-arm64.tar.gz
cp opencode-darwin-arm64/bin/opencode ~/.local/bin/

# 添加到 PATH (如果还没有)

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证安装

opencode --version
\`\`\`

## 使用

\`\`\`bash

# 启动 OpenCode

opencode

# 查看帮助

opencode --help
\`\`\`

## 卸载

\`\`\`bash

# 全局安装的卸载

sudo rm /usr/local/bin/opencode

# 本地安装的卸载

rm ~/.local/bin/opencode
\`\`\`
```

## 🔒 安全考虑

### 文件完整性验证

为了确保分发的文件没有被篡改,可以提供校验和:

```bash
# 生成 SHA256 校验和
shasum -a 256 packages/opencode/dist/opencode-darwin-arm64.tar.gz > opencode-darwin-arm64.tar.gz.sha256

# 用户验证
shasum -a 256 -c opencode-darwin-arm64.tar.gz.sha256
```

### 代码签名 (可选)

如果需要更高的安全性,可以对二进制文件进行代码签名:

```bash
# macOS 代码签名 (需要开发者证书)
codesign -s "Developer ID Application: Your Name" \
    packages/opencode/dist/opencode-darwin-arm64/bin/opencode

# 验证签名
codesign -v packages/opencode/dist/opencode-darwin-arm64/bin/opencode
```

## 📋 多平台分发

如果需要支持多个平台,构建所有平台的版本:

```bash
# 构建所有平台
bun run --cwd packages/opencode script/build.ts

# 生成的文件
dist/
├── opencode-darwin-arm64.tar.gz      # macOS Apple Silicon
├── opencode-darwin-x64.tar.gz        # macOS Intel
├── opencode-linux-arm64.tar.gz       # Linux ARM64
├── opencode-linux-x64.tar.gz         # Linux x64
└── opencode-windows-x64.tar.gz       # Windows x64
```

**平台选择指南:**

| 操作系统          | 架构  | 文件名                         |
| ----------------- | ----- | ------------------------------ |
| macOS (M1/M2/M3)  | ARM64 | `opencode-darwin-arm64.tar.gz` |
| macOS (Intel)     | x64   | `opencode-darwin-x64.tar.gz`   |
| Linux (ARM)       | ARM64 | `opencode-linux-arm64.tar.gz`  |
| Linux (Intel/AMD) | x64   | `opencode-linux-x64.tar.gz`    |
| Windows           | x64   | `opencode-windows-x64.tar.gz`  |

## 🚀 自动化分发脚本

创建一个自动化分发脚本:

```bash
#!/bin/bash
# distribute.sh - 自动化分发脚本

VERSION=$(cat packages/opencode/package.json | grep version | cut -d'"' -f4)
DIST_DIR="packages/opencode/dist"
RELEASE_DIR="release-${VERSION}"

# 创建发布目录
mkdir -p "$RELEASE_DIR"

# 复制分发包
cp "$DIST_DIR"/*.tar.gz "$RELEASE_DIR/"

# 生成校验和
cd "$RELEASE_DIR"
for file in *.tar.gz; do
    shasum -a 256 "$file" >> checksums.txt
done

# 创建 README
cat > README.txt << EOF
OpenCode CLI v${VERSION}

安装方法:
1. 选择适合你系统的压缩包
2. 解压: tar -xzf opencode-*.tar.gz
3. 安装: sudo mv opencode-*/bin/opencode /usr/local/bin/
4. 验证: opencode --version

校验和已保存在 checksums.txt
EOF

echo "✅ 发布包已准备好: $RELEASE_DIR"
ls -lh
```

## ❓ 常见问题

### Q: 用户需要安装什么依赖吗?

**A:** 不需要!这是一个完全独立的二进制文件,包含了所有必要的依赖。

### Q: 文件为什么这么大 (94MB)?

**A:** 因为它包含了:

- Bun 运行时
- 所有 Node.js 依赖
- TUI 界面库
- AI SDK 和 provider
- 所有必要的资源文件

### Q: 可以在没有网络的环境使用吗?

**A:** 二进制文件本身可以离线运行,但 OpenCode 连接 AI 服务时需要网络。

### Q: 如何更新版本?

**A:** 重新构建并分发新的压缩包,用户用新版本替换旧的二进制文件即可。

### Q: 支持自动更新吗?

**A:** 当前版本不支持自动更新,需要手动替换二进制文件。

## 📝 版本管理建议

### 版本命名规范

```
opencode-darwin-arm64-v1.1.35.tar.gz
opencode-darwin-arm64-v1.2.0.tar.gz
```

### 发布清单

每次发布时,准备以下文件:

- [ ] 二进制压缩包 (`.tar.gz`)
- [ ] SHA256 校验和文件
- [ ] 安装文档 (`INSTALL.md`)
- [ ] 更新日志 (`CHANGELOG.md`)
- [ ] 版本信息 (`VERSION.txt`)

## 🎓 最佳实践

1. **版本控制**: 在文件名中包含版本号
2. **校验和**: 始终提供 SHA256 校验和
3. **文档**: 提供清晰的安装和使用文档
4. **测试**: 在干净的环境中测试分发包
5. **备份**: 保留历史版本的分发包

## 总结

✅ **是的,`opencode-darwin-arm64.tar.gz` 就够了!**

这个压缩包包含了运行 OpenCode CLI 所需的一切,其他开发人员只需要:

1. 下载压缩包
2. 解压
3. 移动到系统路径
4. 开始使用

无需任何额外的依赖安装或配置!
