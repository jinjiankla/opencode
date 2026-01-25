#!/bin/bash

# OpenCode 遥测日志分析工具
# 用于分析和统计 OpenCode 的遥测日志

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认日志目录
LOG_DIR="${HOME}/.local/share/opencode/log"

# 使用方法
usage() {
    echo "OpenCode 遥测日志分析工具"
    echo ""
    echo "用法: $0 [选项] [日志文件]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -d, --dir DIR       指定日志目录 (默认: ~/.local/share/opencode/log)"
    echo "  -l, --latest        分析最新的日志文件"
    echo "  -a, --all           分析所有日志文件"
    echo "  -s, --session ID    只分析指定 session"
    echo "  -t, --tool NAME     只分析指定工具"
    echo "  -m, --model NAME    只分析指定模型"
    echo "  --stats             显示统计信息"
    echo "  --tokens            显示 token 使用情况"
    echo "  --tools             显示工具调用统计"
    echo "  --llm               显示 LLM 调用统计"
    echo "  --cost              估算成本"
    echo "  --export FILE       导出为 CSV 文件"
    echo ""
    echo "示例:"
    echo "  $0 --latest --stats"
    echo "  $0 --all --tokens"
    echo "  $0 -s 01JKX... --tools"
    echo "  $0 mylog.log --cost"
}

# 解析参数
ANALYZE_LATEST=false
ANALYZE_ALL=false
SHOW_STATS=false
SHOW_TOKENS=false
SHOW_TOOLS=false
SHOW_LLM=false
SHOW_COST=false
SESSION_FILTER=""
TOOL_FILTER=""
MODEL_FILTER=""
EXPORT_FILE=""
LOG_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -d|--dir)
            LOG_DIR="$2"
            shift 2
            ;;
        -l|--latest)
            ANALYZE_LATEST=true
            shift
            ;;
        -a|--all)
            ANALYZE_ALL=true
            shift
            ;;
        -s|--session)
            SESSION_FILTER="$2"
            shift 2
            ;;
        -t|--tool)
            TOOL_FILTER="$2"
            shift 2
            ;;
        -m|--model)
            MODEL_FILTER="$2"
            shift 2
            ;;
        --stats)
            SHOW_STATS=true
            shift
            ;;
        --tokens)
            SHOW_TOKENS=true
            shift
            ;;
        --tools)
            SHOW_TOOLS=true
            shift
            ;;
        --llm)
            SHOW_LLM=true
            shift
            ;;
        --cost)
            SHOW_COST=true
            shift
            ;;
        --export)
            EXPORT_FILE="$2"
            shift 2
            ;;
        *)
            LOG_FILE="$1"
            shift
            ;;
    esac
done

# 如果没有指定任何显示选项,默认显示统计
if ! $SHOW_STATS && ! $SHOW_TOKENS && ! $SHOW_TOOLS && ! $SHOW_LLM && ! $SHOW_COST; then
    SHOW_STATS=true
fi

# 确定要分析的日志文件
if [ -n "$LOG_FILE" ]; then
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${RED}错误: 日志文件不存在: $LOG_FILE${NC}"
        exit 1
    fi
    LOGS="$LOG_FILE"
elif $ANALYZE_LATEST; then
    LOGS=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)
    if [ -z "$LOGS" ]; then
        echo -e "${RED}错误: 未找到日志文件${NC}"
        exit 1
    fi
    echo -e "${CYAN}分析最新日志: $(basename "$LOGS")${NC}"
elif $ANALYZE_ALL; then
    LOGS=$(ls -t "$LOG_DIR"/*.log 2>/dev/null)
    if [ -z "$LOGS" ]; then
        echo -e "${RED}错误: 未找到日志文件${NC}"
        exit 1
    fi
    echo -e "${CYAN}分析所有日志文件 ($(echo "$LOGS" | wc -l) 个)${NC}"
else
    echo -e "${YELLOW}请指定日志文件或使用 --latest / --all${NC}"
    usage
    exit 1
fi

# 应用过滤器
FILTER_CMD="cat"
if [ -n "$SESSION_FILTER" ]; then
    FILTER_CMD="$FILTER_CMD | grep 'sessionID=$SESSION_FILTER'"
fi
if [ -n "$TOOL_FILTER" ]; then
    FILTER_CMD="$FILTER_CMD | grep 'tool=$TOOL_FILTER'"
fi
if [ -n "$MODEL_FILTER" ]; then
    FILTER_CMD="$FILTER_CMD | grep 'model=$MODEL_FILTER'"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  OpenCode 遥测日志分析${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 统计信息
if $SHOW_STATS; then
    echo -e "${GREEN}📊 统计信息${NC}"
    echo ""
    
    TOOL_CALLS=$(eval "$FILTER_CMD $LOGS" | grep -c "tool_call_start" || echo 0)
    MCP_CALLS=$(eval "$FILTER_CMD $LOGS" | grep -c "mcp_call_start" || echo 0)
    LLM_CALLS=$(eval "$FILTER_CMD $LOGS" | grep -c "llm_call_start" || echo 0)
    
    echo -e "  工具调用:    ${CYAN}$TOOL_CALLS${NC}"
    echo -e "  MCP 调用:    ${CYAN}$MCP_CALLS${NC}"
    echo -e "  LLM 调用:    ${CYAN}$LLM_CALLS${NC}"
    
    # 成功率
    TOOL_SUCCESS=$(eval "$FILTER_CMD $LOGS" | grep "tool_call_end" | grep -c "success=true" || echo 0)
    TOOL_FAILED=$(eval "$FILTER_CMD $LOGS" | grep "tool_call_end" | grep -c "success=false" || echo 0)
    TOOL_TOTAL=$((TOOL_SUCCESS + TOOL_FAILED))
    
    if [ $TOOL_TOTAL -gt 0 ]; then
        TOOL_SUCCESS_RATE=$(echo "scale=1; $TOOL_SUCCESS * 100 / $TOOL_TOTAL" | bc)
        echo -e "  工具成功率:  ${GREEN}${TOOL_SUCCESS_RATE}%${NC} ($TOOL_SUCCESS/$TOOL_TOTAL)"
    fi
    
    echo ""
fi

# Token 使用情况
if $SHOW_TOKENS; then
    echo -e "${GREEN}💰 Token 使用情况${NC}"
    echo ""
    
    TOTAL_TOKENS=$(eval "$FILTER_CMD $LOGS" | grep "totalTokens=" | \
        grep -o 'totalTokens=[0-9]*' | cut -d= -f2 | \
        awk '{sum+=$1} END {print sum}')
    
    PROMPT_TOKENS=$(eval "$FILTER_CMD $LOGS" | grep "promptTokens=" | \
        grep -o 'promptTokens=[0-9]*' | cut -d= -f2 | \
        awk '{sum+=$1} END {print sum}')
    
    COMPLETION_TOKENS=$(eval "$FILTER_CMD $LOGS" | grep "completionTokens=" | \
        grep -o 'completionTokens=[0-9]*' | cut -d= -f2 | \
        awk '{sum+=$1} END {print sum}')
    
    echo -e "  总 Token:       ${CYAN}${TOTAL_TOKENS:-0}${NC}"
    echo -e "  提示 Token:     ${CYAN}${PROMPT_TOKENS:-0}${NC}"
    echo -e "  完成 Token:     ${CYAN}${COMPLETION_TOKENS:-0}${NC}"
    
    # 按模型统计
    echo ""
    echo -e "  ${YELLOW}按模型统计:${NC}"
    eval "$FILTER_CMD $LOGS" | grep "token_usage" | \
        grep -o 'provider=[^ ]* model=[^ ]* .* totalTokens=[0-9]*' | \
        awk '{
            provider=$1; model=$2; tokens=$NF;
            gsub(/provider=/, "", provider);
            gsub(/model=/, "", model);
            gsub(/totalTokens=/, "", tokens);
            key=provider"/"model;
            sum[key]+=tokens;
        }
        END {
            for (key in sum) {
                printf "    %-40s %10d tokens\n", key, sum[key];
            }
        }' | sort -k2 -rn | head -10
    
    echo ""
fi

# 工具调用统计
if $SHOW_TOOLS; then
    echo -e "${GREEN}🔧 工具调用统计${NC}"
    echo ""
    
    echo -e "  ${YELLOW}最常用工具:${NC}"
    eval "$FILTER_CMD $LOGS" | grep "tool_call_start" | \
        grep -o 'tool=[^ ]*' | cut -d= -f2 | \
        sort | uniq -c | sort -rn | head -10 | \
        awk '{printf "    %-30s %5d 次\n", $2, $1}'
    
    echo ""
    echo -e "  ${YELLOW}平均执行时间:${NC}"
    eval "$FILTER_CMD $LOGS" | grep "tool_call_end" | \
        grep -o 'tool=[^ ]* .* duration=[0-9]*' | \
        awk '{
            tool=$1; duration=$NF;
            gsub(/tool=/, "", tool);
            gsub(/duration=/, "", duration);
            sum[tool]+=duration;
            count[tool]++;
        }
        END {
            for (tool in sum) {
                avg=sum[tool]/count[tool];
                printf "    %-30s %8.0f ms\n", tool, avg;
            }
        }' | sort -k2 -rn | head -10
    
    echo ""
fi

# LLM 调用统计
if $SHOW_LLM; then
    echo -e "${GREEN}🤖 LLM 调用统计${NC}"
    echo ""
    
    echo -e "  ${YELLOW}按模型统计:${NC}"
    eval "$FILTER_CMD $LOGS" | grep "llm_call_start" | \
        grep -o 'provider=[^ ]* model=[^ ]*' | \
        awk '{
            provider=$1; model=$2;
            gsub(/provider=/, "", provider);
            gsub(/model=/, "", model);
            key=provider"/"model;
            count[key]++;
        }
        END {
            for (key in count) {
                printf "    %-40s %5d 次\n", key, count[key];
            }
        }' | sort -k2 -rn
    
    echo ""
    echo -e "  ${YELLOW}平均响应时间:${NC}"
    eval "$FILTER_CMD $LOGS" | grep "llm_call_end" | \
        grep -o 'provider=[^ ]* model=[^ ]* .* duration=[0-9]*' | \
        awk '{
            provider=$1; model=$2; duration=$NF;
            gsub(/provider=/, "", provider);
            gsub(/model=/, "", model);
            gsub(/duration=/, "", duration);
            key=provider"/"model;
            sum[key]+=duration;
            count[key]++;
        }
        END {
            for (key in sum) {
                avg=sum[key]/count[key];
                printf "    %-40s %8.0f ms\n", key, avg;
            }
        }' | sort -k2 -rn
    
    echo ""
fi

# 成本估算
if $SHOW_COST; then
    echo -e "${GREEN}💵 成本估算${NC}"
    echo ""
    echo -e "  ${YELLOW}注意: 这是基于示例价格的粗略估算${NC}"
    echo ""
    
    # 简单的成本估算 (需要根据实际价格更新)
    eval "$FILTER_CMD $LOGS" | grep "token_usage" | \
        grep -o 'provider=[^ ]* model=[^ ]* promptTokens=[0-9]* completionTokens=[0-9]*' | \
        awk '{
            provider=$1; model=$2; prompt=$3; completion=$4;
            gsub(/provider=/, "", provider);
            gsub(/model=/, "", model);
            gsub(/promptTokens=/, "", prompt);
            gsub(/completionTokens=/, "", completion);
            
            # 示例价格 (美元/1K tokens)
            if (provider == "openai" && model ~ /gpt-4/) {
                input_price = 0.03;
                output_price = 0.06;
            } else if (provider == "openai" && model ~ /gpt-3.5/) {
                input_price = 0.0015;
                output_price = 0.002;
            } else if (provider == "anthropic" && model ~ /claude-3-opus/) {
                input_price = 0.015;
                output_price = 0.075;
            } else if (provider == "anthropic" && model ~ /claude-3-sonnet/) {
                input_price = 0.003;
                output_price = 0.015;
            } else {
                input_price = 0;
                output_price = 0;
            }
            
            cost = (prompt * input_price + completion * output_price) / 1000;
            key = provider"/"model;
            total_cost[key] += cost;
            total_tokens[key] += prompt + completion;
        }
        END {
            grand_total = 0;
            for (key in total_cost) {
                printf "    %-40s $%8.4f (%d tokens)\n", key, total_cost[key], total_tokens[key];
                grand_total += total_cost[key];
            }
            printf "\n    总计: $%.4f\n", grand_total;
        }' | sort -k2 -rn
    
    echo ""
fi

# 导出为 CSV
if [ -n "$EXPORT_FILE" ]; then
    echo -e "${GREEN}📤 导出数据到: $EXPORT_FILE${NC}"
    echo ""
    
    echo "timestamp,event_type,session_id,tool,provider,model,duration,tokens,success" > "$EXPORT_FILE"
    
    eval "$FILTER_CMD $LOGS" | grep -E "tool_call_end|llm_call_end|token_usage" | \
        awk '{
            # 提取字段
            timestamp = $1 " " $2;
            event_type = "";
            session_id = "";
            tool = "";
            provider = "";
            model = "";
            duration = "";
            tokens = "";
            success = "";
            
            if ($0 ~ /tool_call_end/) event_type = "tool_call";
            if ($0 ~ /llm_call_end/) event_type = "llm_call";
            if ($0 ~ /token_usage/) event_type = "token_usage";
            
            for (i=1; i<=NF; i++) {
                if ($i ~ /^sessionID=/) session_id = substr($i, 11);
                if ($i ~ /^tool=/) tool = substr($i, 6);
                if ($i ~ /^provider=/) provider = substr($i, 10);
                if ($i ~ /^model=/) model = substr($i, 7);
                if ($i ~ /^duration=/) duration = substr($i, 10);
                if ($i ~ /^totalTokens=/) tokens = substr($i, 13);
                if ($i ~ /^success=/) success = substr($i, 9);
            }
            
            print timestamp "," event_type "," session_id "," tool "," provider "," model "," duration "," tokens "," success;
        }' >> "$EXPORT_FILE"
    
    echo -e "  ✅ 已导出 $(wc -l < "$EXPORT_FILE") 行数据"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
