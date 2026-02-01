#!/bin/bash
# 代码索引自动化脚本

set -e

# 配置
CODE_DIR="${1:-./src}"                    # 代码目录
DOCS_DIR="${2:-./docs/code}"              # 文档输出目录
PAGEINDEX_DIR="${3:-$HOME/pageindex-enterprise/PageIndex}"  # PageIndex 目录
RESULTS_DIR="$PAGEINDEX_DIR/results"      # 索引结果目录

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   代码索引自动化工具${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}[1/4] 检查依赖...${NC}"

if [ ! -f "code_to_markdown.py" ]; then
    echo -e "${RED}❌ 找不到 code_to_markdown.py${NC}"
    exit 1
fi

if [ ! -d "$PAGEINDEX_DIR" ]; then
    echo -e "${RED}❌ 找不到 PageIndex 目录: $PAGEINDEX_DIR${NC}"
    exit 1
fi

if [ ! -d "$CODE_DIR" ]; then
    echo -e "${RED}❌ 找不到代码目录: $CODE_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 依赖检查完成${NC}"
echo ""

# 转换代码为 Markdown
echo -e "${YELLOW}[2/4] 转换代码为 Markdown...${NC}"
echo -e "代码目录: $CODE_DIR"
echo -e "输出目录: $DOCS_DIR"
echo ""

python3 code_to_markdown.py -i "$CODE_DIR" -o "$DOCS_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 代码转换失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 代码转换完成${NC}"
echo ""

# 索引 Markdown 文件
echo -e "${YELLOW}[3/4] 索引 Markdown 文件...${NC}"

cd "$PAGEINDEX_DIR"

success_count=0
fail_count=0

# 查找所有 Markdown 文件
while IFS= read -r md_file; do
    echo -e "  索引: $md_file"
    
    if python3 run_pageindex.py --md_path "$md_file" > /dev/null 2>&1; then
        ((success_count++))
        echo -e "  ${GREEN}✅${NC}"
    else
        ((fail_count++))
        echo -e "  ${RED}❌${NC}"
    fi
done < <(find "$DOCS_DIR" -name "*.md" -type f)

echo ""
echo -e "${GREEN}✅ 索引完成: $success_count 成功, $fail_count 失败${NC}"
echo ""

# 生成索引报告
echo -e "${YELLOW}[4/4] 生成索引报告...${NC}"

REPORT_FILE="$RESULTS_DIR/index_report.md"

cat > "$REPORT_FILE" << EOF
# 代码索引报告

生成时间: $(date '+%Y-%m-%d %H:%M:%S')

## 统计信息

- 代码目录: \`$CODE_DIR\`
- 文档目录: \`$DOCS_DIR\`
- 索引成功: $success_count
- 索引失败: $fail_count

## 已索引文件

EOF

# 列出所有索引文件
find "$RESULTS_DIR" -name "*.json" -type f -newer "$REPORT_FILE" 2>/dev/null | while read -r json_file; do
    filename=$(basename "$json_file")
    echo "- \`$filename\`" >> "$REPORT_FILE"
done

echo -e "${GREEN}✅ 报告已生成: $REPORT_FILE${NC}"
echo ""

# 完成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 代码索引完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "下一步:"
echo -e "  1. 查看报告: ${BLUE}cat $REPORT_FILE${NC}"
echo -e "  2. 在 OpenCode 中查询代码"
echo ""
