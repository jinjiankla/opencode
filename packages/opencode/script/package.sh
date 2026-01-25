#!/bin/bash

# OpenCode CLI 打包脚本
# 用于构建和打包 OpenCode CLI 程序

set -e

echo "🚀 开始构建 OpenCode CLI..."

# 切换到 opencode 包目录
cd "$(dirname "$0")/.."

# 运行构建
echo "📦 执行构建..."
bun run script/build.ts --single

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 构建失败: dist 目录不存在"
    exit 1
fi

# 获取构建的目录名
BUILD_DIR=$(ls -d dist/opencode-* 2>/dev/null | head -n 1)

if [ -z "$BUILD_DIR" ]; then
    echo "❌ 未找到构建输出"
    exit 1
fi

BUILD_NAME=$(basename "$BUILD_DIR")
echo "✅ 构建完成: $BUILD_NAME"

# 测试二进制文件
echo "🧪 测试二进制文件..."
if [ -f "$BUILD_DIR/bin/opencode" ]; then
    VERSION=$("$BUILD_DIR/bin/opencode" --version 2>&1 | tail -n 1)
    echo "   版本: $VERSION"
else
    echo "❌ 二进制文件不存在"
    exit 1
fi

# 打包
echo "📦 创建压缩包..."
cd dist
tar -czf "${BUILD_NAME}.tar.gz" "$BUILD_NAME/"
cd ..

# 显示结果
PACKAGE_PATH="dist/${BUILD_NAME}.tar.gz"
PACKAGE_SIZE=$(du -h "$PACKAGE_PATH" | cut -f1)

echo ""
echo "✨ 打包完成!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 包名称: ${BUILD_NAME}.tar.gz"
echo "📊 包大小: $PACKAGE_SIZE"
echo "📍 位置: $PACKAGE_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "安装方法:"
echo "  tar -xzf $PACKAGE_PATH"
echo "  sudo mv $BUILD_NAME/bin/opencode /usr/local/bin/"
echo ""
