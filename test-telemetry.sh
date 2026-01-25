#!/bin/bash

# OpenCode 遥测测试脚本

echo "================================"
echo "OpenCode 遥测功能测试"
echo "================================"
echo ""

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 使用新打包的版本
OPENCODE_BIN="./packages/opencode/dist/opencode-darwin-arm64/bin/opencode"

if [ ! -f "$OPENCODE_BIN" ]; then
    echo "❌ 错误: 找不到打包的 opencode 二进制文件"
    echo "请先运行: bun run --cwd packages/opencode script/build.ts --single"
    exit 1
fi

echo -e "${BLUE}📦 使用的版本:${NC}"
$OPENCODE_BIN --version
echo ""

echo -e "${BLUE}📝 日志目录:${NC}"
LOG_DIR="${HOME}/.local/share/opencode/log"
echo "$LOG_DIR"
echo ""

# 清理旧日志(可选)
read -p "是否清理旧日志? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🗑️  清理旧日志...${NC}"
    rm -rf "$LOG_DIR"/*.log
    echo "✅ 已清理"
fi
echo ""

echo -e "${GREEN}🚀 启动 OpenCode (启用所有遥测)${NC}"
echo -e "${YELLOW}提示: 请在 OpenCode 中执行一些操作,然后退出${NC}"
echo -e "${YELLOW}例如: 问一个问题,让它调用工具${NC}"
echo ""
echo "按 Enter 继续..."
read

# 启用所有遥测
export OPENCODE_TELEMETRY=1
export OPENCODE_HTTP_LOG=1
export OPENCODE_DEBUG=1

# 运行 OpenCode
$OPENCODE_BIN

echo ""
echo -e "${GREEN}✅ OpenCode 已退出${NC}"
echo ""

# 检查日志
echo -e "${BLUE}📊 检查生成的日志...${NC}"
echo ""

if [ ! -d "$LOG_DIR" ]; then
    echo "❌ 日志目录不存在: $LOG_DIR"
    exit 1
fi

LATEST_LOG=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 没有找到日志文件"
    exit 1
fi

echo -e "${GREEN}📄 最新日志文件:${NC} $(basename "$LATEST_LOG")"
echo ""

# 统计日志
echo -e "${BLUE}📈 日志统计:${NC}"
echo ""

TOOL_CALLS=$(grep -c "tool_call_start" "$LATEST_LOG" 2>/dev/null || echo 0)
HTTP_REQUESTS=$(grep -c "http_request" "$LATEST_LOG" 2>/dev/null || echo 0)
LLM_CALLS=$(grep -c "llm_call_start" "$LATEST_LOG" 2>/dev/null || echo 0)
TOKEN_USAGE=$(grep -c "token_usage" "$LATEST_LOG" 2>/dev/null || echo 0)

echo "  工具调用:     $TOOL_CALLS"
echo "  HTTP 请求:    $HTTP_REQUESTS"
echo "  LLM 调用:     $LLM_CALLS"
echo "  Token 使用:   $TOKEN_USAGE"
echo ""

if [ $TOOL_CALLS -gt 0 ] || [ $HTTP_REQUESTS -gt 0 ] || [ $LLM_CALLS -gt 0 ]; then
    echo -e "${GREEN}✅ 遥测功能正常工作!${NC}"
    echo ""
    
    # 显示一些示例日志
    echo -e "${BLUE}📝 示例日志 (最近 10 条遥测记录):${NC}"
    echo ""
    grep -E "tool_call|http_request|llm_call|token_usage" "$LATEST_LOG" | tail -10
    echo ""
    
    echo -e "${YELLOW}💡 查看完整日志:${NC}"
    echo "  tail -f $LATEST_LOG"
    echo ""
    echo -e "${YELLOW}💡 分析日志:${NC}"
    echo "  ./packages/opencode/script/analyze-telemetry.sh --latest --stats"
else
    echo -e "${YELLOW}⚠️  没有检测到遥测记录${NC}"
    echo "可能的原因:"
    echo "  1. 没有执行任何操作"
    echo "  2. 环境变量未正确设置"
    echo "  3. 遥测功能未启用"
    echo ""
    echo "请确保:"
    echo "  - 在 OpenCode 中问了问题"
    echo "  - 让 AI 调用了工具"
    echo ""
fi

echo "================================"
echo "测试完成"
echo "================================"
