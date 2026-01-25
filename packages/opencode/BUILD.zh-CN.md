# OpenCode CLI 本地构建指南

本文档说明如何在本地构建和打包 OpenCode CLI 程序。

## 前置要求

- **Bun**: v1.3.5 或更高版本
- **操作系统**: macOS, Linux, 或 Windows
- **架构**: ARM64 或 x64

## 快速开始

### 1. 安装依赖

首先,确保所有依赖都已安装:

```bash
bun install
```

### 2. 构建当前平台的 CLI

使用 `--single` 标志只构建当前平台的版本:

```bash
bun run --cwd packages/opencode script/build.ts --single
```

这将在 `packages/opencode/dist/` 目录下生成对应平台的二进制文件。

### 3. 使用便捷脚本

我们提供了一个便捷的打包脚本,可以自动完成构建和打包:

```bash
cd packages/opencode
./script/package.sh
```

这个脚本会:

- 构建当前平台的 CLI
- 测试二进制文件
- 创建 `.tar.gz` 压缩包
- 显示安装说明

## 构建选项

### 构建所有平台

如果需要构建所有支持的平台(Linux, macOS, Windows):

```bash
bun run --cwd packages/opencode script/build.ts
```

支持的平台包括:

- **Linux**: ARM64, x64 (glibc/musl)
- **macOS**: ARM64, x64
- **Windows**: x64

### 构建 Baseline 版本

Baseline 版本不使用 AVX2 指令,兼容性更好:

```bash
bun run --cwd packages/opencode script/build.ts --single --baseline
```

### 跳过依赖安装

如果依赖已经安装,可以跳过安装步骤:

```bash
bun run --cwd packages/opencode script/build.ts --single --skip-install
```

## 输出结构

构建完成后,输出目录结构如下:

```
packages/opencode/dist/
├── opencode-darwin-arm64/          # macOS ARM64 版本
│   ├── bin/
│   │   └── opencode               # 可执行文件 (~94MB)
│   └── package.json
└── opencode-darwin-arm64.tar.gz   # 压缩包 (~31MB)
```

## 测试构建

测试构建的二进制文件:

```bash
./packages/opencode/dist/opencode-darwin-arm64/bin/opencode --version
```

## 安装到系统

### macOS/Linux

```bash
# 解压
tar -xzf packages/opencode/dist/opencode-darwin-arm64.tar.gz

# 安装到系统路径
sudo mv opencode-darwin-arm64/bin/opencode /usr/local/bin/

# 验证安装
opencode --version
```

### 仅当前用户

```bash
# 创建本地 bin 目录(如果不存在)
mkdir -p ~/.local/bin

# 复制二进制文件
cp packages/opencode/dist/opencode-darwin-arm64/bin/opencode ~/.local/bin/

# 确保 ~/.local/bin 在 PATH 中
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 验证安装
opencode --version
```

## 构建过程说明

构建脚本 (`script/build.ts`) 执行以下步骤:

1. **生成 models snapshot**: 从 models.dev API 获取最新的模型数据
2. **安装平台特定依赖**:
   - `@opentui/core`: TUI 核心库
   - `@parcel/watcher`: 文件监控库
3. **编译 TypeScript**: 使用 Bun 的编译功能
4. **打包二进制**: 将所有依赖打包到单个可执行文件中
5. **生成 package.json**: 包含版本和平台信息

## 环境变量

### MODELS_DEV_API_JSON

如果你有本地的 models.dev API 数据文件,可以使用这个环境变量:

```bash
export MODELS_DEV_API_JSON=/path/to/api.json
bun run --cwd packages/opencode script/build.ts --single
```

## 故障排除

### 找不到模块错误

如果遇到 "Cannot find module" 错误:

```bash
# 清理并重新安装依赖
rm -rf node_modules
bun install
```

### 构建失败

检查 Bun 版本:

```bash
bun --version  # 应该是 1.3.5 或更高
```

### 二进制文件无法运行

确保文件有执行权限:

```bash
chmod +x packages/opencode/dist/opencode-darwin-arm64/bin/opencode
```

## 开发模式

如果只是想在开发中运行 OpenCode,不需要构建:

```bash
bun run --cwd packages/opencode dev
```

## 相关文件

- `script/build.ts`: 主构建脚本
- `script/package.sh`: 便捷打包脚本
- `package.json`: 依赖和版本配置
- `tsconfig.json`: TypeScript 配置

## 版本信息

构建的版本号格式: `0.0.0-dev-YYYYMMDDHHmm`

例如: `0.0.0-dev-202601250116` 表示 2026年1月25日 01:16 构建的开发版本。

## 更多信息

- [OpenCode 官方文档](https://opencode.ai/docs)
- [贡献指南](../../CONTRIBUTING.md)
- [问题反馈](https://github.com/anomalyco/opencode/issues)
