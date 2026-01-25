#!/bin/bash

# OpenCode CLI 快速分发脚本
# 自动准备分发包,包含所有必需文件

set -e

echo "📦 OpenCode CLI 分发包准备工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 切换到 opencode 包目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PACKAGE_DIR"

DIST_DIR="dist"
RELEASE_DIR="../../release"

# 检查构建产物是否存在
if [ ! -d "$DIST_DIR" ]; then
    echo "❌ 错误: dist 目录不存在"
    echo "请先运行构建: bun run script/build.ts --single"
    exit 1
fi

# 查找构建的平台
BUILD_NAME=$(ls -d "$DIST_DIR"/opencode-* 2>/dev/null | head -n 1 | xargs basename)

if [ -z "$BUILD_NAME" ]; then
    echo "❌ 错误: 未找到构建产物"
    exit 1
fi

echo "✅ 找到构建: $BUILD_NAME"

# 检查压缩包是否存在
TARBALL="$DIST_DIR/${BUILD_NAME}.tar.gz"
if [ ! -f "$TARBALL" ]; then
    echo "📦 创建压缩包..."
    cd "$DIST_DIR"
    tar -czf "${BUILD_NAME}.tar.gz" "$BUILD_NAME/"
    cd ..
fi

# 生成校验和
echo "🔐 生成校验和..."
cd "$DIST_DIR"
shasum -a 256 "${BUILD_NAME}.tar.gz" > "${BUILD_NAME}.tar.gz.sha256"
cd ..

# 创建发布目录
RELEASE_SUBDIR="$RELEASE_DIR/$BUILD_NAME"
mkdir -p "$RELEASE_SUBDIR"

echo "📋 准备分发文件..."

# 复制文件
cp "$TARBALL" "$RELEASE_SUBDIR/"
cp "$DIST_DIR/${BUILD_NAME}.tar.gz.sha256" "$RELEASE_SUBDIR/"

# 复制用户安装指南
if [ -f "INSTALL-USER.zh-CN.md" ]; then
    cp "INSTALL-USER.zh-CN.md" "$RELEASE_SUBDIR/README.md"
else
    echo "⚠️  警告: 未找到 INSTALL-USER.zh-CN.md"
fi

# 创建版本信息文件
VERSION=$(cat "$DIST_DIR/$BUILD_NAME/package.json" | grep version | cut -d'"' -f4)
cat > "$RELEASE_SUBDIR/VERSION.txt" << EOF
OpenCode CLI
版本: $VERSION
平台: $BUILD_NAME
构建日期: $(date '+%Y-%m-%d %H:%M:%S')
SHA256: $(cat "$DIST_DIR/${BUILD_NAME}.tar.gz.sha256" | cut -d' ' -f1)
EOF

# 验证分发包
echo "🧪 验证分发包..."
cd "$RELEASE_SUBDIR"

# 验证校验和
if shasum -a 256 -c "${BUILD_NAME}.tar.gz.sha256" > /dev/null 2>&1; then
    echo "   ✅ 校验和验证通过"
else
    echo "   ❌ 校验和验证失败"
    exit 1
fi

# 测试解压
if tar -tzf "${BUILD_NAME}.tar.gz" > /dev/null 2>&1; then
    echo "   ✅ 压缩包完整"
else
    echo "   ❌ 压缩包损坏"
    exit 1
fi

cd - > /dev/null

# 创建最终发布包
echo "📦 创建最终发布包..."
cd "$RELEASE_DIR"
RELEASE_ZIP="${BUILD_NAME}-release.zip"
rm -f "$RELEASE_ZIP"
zip -r "$RELEASE_ZIP" "$BUILD_NAME/" > /dev/null

# 显示结果
echo ""
echo "✨ 分发包准备完成!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 版本: $VERSION"
echo "🏷️  平台: $BUILD_NAME"
echo "📍 位置: $RELEASE_DIR/$BUILD_NAME/"
echo ""
echo "📂 分发文件:"
ls -lh "$BUILD_NAME/" | tail -n +2 | awk '{printf "   %s  %s\n", $5, $9}'
echo ""
echo "📦 发布包: $RELEASE_ZIP"
echo "   大小: $(du -h "$RELEASE_ZIP" | cut -f1)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 分发方式:"
echo ""
echo "方式 1: 分发整个目录"
echo "  cp -r $RELEASE_DIR/$BUILD_NAME /path/to/share/"
echo ""
echo "方式 2: 分发压缩包"
echo "  cp $RELEASE_DIR/$RELEASE_ZIP /path/to/share/"
echo ""
echo "方式 3: 上传到文件服务器"
echo "  scp $RELEASE_DIR/$RELEASE_ZIP user@server:/path/"
echo ""
echo "📝 用户安装步骤:"
echo "  1. 解压: tar -xzf ${BUILD_NAME}.tar.gz"
echo "  2. 安装: sudo mv $BUILD_NAME/bin/opencode /usr/local/bin/"
echo "  3. 验证: opencode --version"
echo ""
