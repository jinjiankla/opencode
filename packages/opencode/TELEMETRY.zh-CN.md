# OpenCode 遥测日志系统使用指南

## 概述

OpenCode 遥测日志系统提供了详细的追踪和监控功能,可以记录:

- 🔧 **工具调用** (Tool Calls)
- 🔗 **MCP 调用** (MCP Calls)
- 🤖 **AI 模型调用** (LLM Calls)
- 💰 **Token 消耗** (Token Usage)
- 📊 **上下文管理** (Context Management)
- ⏱️ **性能指标** (Performance Metrics)

## 快速开始

### 1. 启用遥测日志

设置环境变量:

```bash
# 启用遥测日志
export OPENCODE_TELEMETRY=1

# 或者启用调试模式(包含遥测)
export OPENCODE_DEBUG=1

# 启动 OpenCode
opencode
```

### 2. 查看日志

日志会写入到:

```bash
# macOS/Linux
~/.local/share/opencode/log/

# 查看最新日志
tail -f ~/.local/share/opencode/log/$(ls -t ~/.local/share/opencode/log/ | head -1)
```

## 日志格式

### 基本格式

```
[LEVEL] [TIMESTAMP] [DELTA] service=telemetry [TAGS] [MESSAGE]
```

示例:

```
INFO  2026-01-25T09:00:00 +150ms service=telemetry sessionID=01JKX... tool=shell tool_call_start input={"command":"ls -la"}
INFO  2026-01-25T09:00:01 +1200ms service=telemetry sessionID=01JKX... tool=shell tool_call_end success=true duration=1200
```

## 追踪的事件类型

### 1. 工具调用 (Tool Calls)

#### tool_call_start

工具调用开始时记录:

```
INFO service=telemetry sessionID=01JKX... messageID=01JKY... callID=01JKZ... tool=shell agent=build tool_call_start input={"command":"npm test"}
```

**字段说明:**

- `sessionID`: 会话 ID
- `messageID`: 消息 ID
- `callID`: 调用 ID
- `tool`: 工具名称
- `agent`: 代理名称
- `input`: 工具输入参数

#### tool_call_end

工具调用结束时记录:

```
INFO service=telemetry sessionID=01JKX... tool=shell tool_call_end success=true duration=1234 outputLength=512
```

**字段说明:**

- `success`: 是否成功
- `duration`: 执行时间(毫秒)
- `outputLength`: 输出长度
- `error`: 错误信息(如果失败)
- `metadata`: 元数据(JSON)

### 2. MCP 调用 (MCP Calls)

#### mcp_call_start

MCP 工具调用开始:

```
INFO service=telemetry sessionID=01JKX... mcp=filesystem tool=read_file mcp_call_start input={"path":"/path/to/file"}
```

#### mcp_call_end

MCP 工具调用结束:

```
INFO service=telemetry sessionID=01JKX... mcp=filesystem tool=read_file mcp_call_end success=true duration=45
```

### 3. LLM 调用 (AI Model Calls)

#### llm_call_start

AI 模型调用开始:

```
INFO service=telemetry sessionID=01JKX... provider=openai model=gpt-4 agent=build llm_call_start inputMessages=5
```

**字段说明:**

- `provider`: Provider ID (如 openai, anthropic)
- `model`: 模型 ID (如 gpt-4, claude-3-opus)
- `agent`: 代理名称
- `inputMessages`: 输入消息数量

#### llm_call_end

AI 模型调用结束:

```
INFO service=telemetry sessionID=01JKX... provider=openai model=gpt-4 llm_call_end success=true duration=2345 inputTokens=1500 outputTokens=800 totalTokens=2300 finishReason=stop
```

**字段说明:**

- `duration`: 调用时间(毫秒)
- `inputTokens`: 输入 token 数
- `outputTokens`: 输出 token 数
- `totalTokens`: 总 token 数
- `reasoningTokens`: 推理 token 数(如果支持)
- `finishReason`: 完成原因 (stop, length, tool_calls, etc.)

### 4. Token 使用 (Token Usage)

```
INFO service=telemetry sessionID=01JKX... provider=openai model=gpt-4 token_usage promptTokens=1500 completionTokens=800 totalTokens=2300
```

**字段说明:**

- `promptTokens`: 提示 token 数
- `completionTokens`: 完成 token 数
- `totalTokens`: 总 token 数
- `reasoningTokens`: 推理 token 数(可选)
- `cachedTokens`: 缓存 token 数(可选)

### 5. 上下文管理 (Context Management)

```
INFO service=telemetry sessionID=01JKX... context_management contextSize=45678 messageCount=12 toolCallCount=5 truncated=false
```

**字段说明:**

- `contextSize`: 上下文大小(字节)
- `messageCount`: 消息数量
- `toolCallCount`: 工具调用数量
- `truncated`: 是否被截断

### 6. Session 统计 (Session Stats)

```
INFO service=telemetry sessionID=01JKX... session_stats totalMessages=25 totalToolCalls=15 totalMCPCalls=8 totalLLMCalls=10 totalTokens=50000 totalDuration=120000
```

**字段说明:**

- `totalMessages`: 总消息数
- `totalToolCalls`: 总工具调用数
- `totalMCPCalls`: 总 MCP 调用数
- `totalLLMCalls`: 总 LLM 调用数
- `totalTokens`: 总 token 数
- `totalDuration`: 总时长(毫秒)

## 代码集成示例

### 1. 在工具中使用

```typescript
import { Tool } from "@/tool/tool"
import { ToolTelemetry } from "@/tool/telemetry"
import z from "zod"

// 定义工具
const MyTool = Tool.define("my-tool", {
  description: "My custom tool",
  parameters: z.object({
    input: z.string(),
  }),
  async execute(args, ctx) {
    // 工具逻辑
    return {
      title: "Success",
      metadata: {},
      output: "Result",
    }
  },
})

// 包装工具以启用遥测
export const MyToolWithTelemetry = ToolTelemetry.wrapTool(MyTool)
```

### 2. 在 LLM 调用中使用

```typescript
import { LLM } from "@/session/llm"
import { LLMTelemetry } from "@/session/llm-telemetry"

// 包装 stream 调用
const result = await LLMTelemetry.wrapStream(input, LLM.stream)

// 记录上下文管理
LLMTelemetry.logContextManagement(
  sessionID,
  messageID,
  messages,
  false, // truncated
)
```

### 3. 手动记录事件

```typescript
import { TelemetryLog } from "@/util/telemetry-log"

// 记录工具调用
const tracker = TelemetryLog.trackToolCall({
  sessionID: "01JKX...",
  messageID: "01JKY...",
  callID: "01JKZ...",
  toolName: "shell",
  agent: "build",
  input: { command: "npm test" },
  timestamp: Date.now(),
})

// ... 执行工具 ...

// 记录结果
tracker.end({
  sessionID: "01JKX...",
  messageID: "01JKY...",
  callID: "01JKZ...",
  toolName: "shell",
  success: true,
  output: "Tests passed",
})
```

## 日志分析

### 使用 grep 过滤日志

```bash
# 查看所有工具调用
grep "tool_call" ~/.local/share/opencode/log/*.log

# 查看 LLM 调用
grep "llm_call" ~/.local/share/opencode/log/*.log

# 查看 token 使用
grep "token_usage" ~/.local/share/opencode/log/*.log

# 查看特定 session
grep "sessionID=01JKX" ~/.local/share/opencode/log/*.log

# 查看失败的调用
grep "success=false" ~/.local/share/opencode/log/*.log
```

### 使用 jq 分析 JSON 日志

如果日志包含 JSON 格式的数据:

```bash
# 提取所有 token 使用情况
grep "token_usage" log.txt | \
  grep -o '{.*}' | \
  jq '{provider, model, totalTokens}'

# 计算总 token 消耗
grep "token_usage" log.txt | \
  grep -o 'totalTokens=[0-9]*' | \
  cut -d= -f2 | \
  awk '{sum+=$1} END {print sum}'

# 统计工具调用次数
grep "tool_call_start" log.txt | \
  grep -o 'tool=[^ ]*' | \
  sort | uniq -c | sort -rn
```

### 创建分析脚本

```bash
#!/bin/bash
# analyze-telemetry.sh

LOG_FILE="$1"

echo "=== OpenCode 遥测分析 ==="
echo ""

echo "📊 统计信息:"
echo "  工具调用: $(grep -c "tool_call_start" "$LOG_FILE")"
echo "  MCP 调用: $(grep -c "mcp_call_start" "$LOG_FILE")"
echo "  LLM 调用: $(grep -c "llm_call_start" "$LOG_FILE")"
echo ""

echo "💰 Token 使用:"
TOTAL_TOKENS=$(grep "totalTokens=" "$LOG_FILE" | \
  grep -o 'totalTokens=[0-9]*' | \
  cut -d= -f2 | \
  awk '{sum+=$1} END {print sum}')
echo "  总计: $TOTAL_TOKENS tokens"
echo ""

echo "⏱️  平均响应时间:"
AVG_DURATION=$(grep "llm_call_end" "$LOG_FILE" | \
  grep -o 'duration=[0-9]*' | \
  cut -d= -f2 | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count}')
echo "  LLM: ${AVG_DURATION}ms"
echo ""

echo "🔧 最常用工具:"
grep "tool_call_start" "$LOG_FILE" | \
  grep -o 'tool=[^ ]*' | \
  sort | uniq -c | sort -rn | head -5
```

## 性能优化建议

### 1. 减少日志开销

遥测日志只在启用时才会记录,默认情况下不影响性能。

### 2. 日志轮转

OpenCode 自动保留最近 10 个日志文件,旧文件会被自动删除。

### 3. 选择性启用

如果只需要特定类型的日志,可以修改代码:

```typescript
// 只记录 LLM 调用
export const ENABLE_TOOL_TELEMETRY = false
export const ENABLE_LLM_TELEMETRY = true
export const ENABLE_MCP_TELEMETRY = false
```

## 常见问题

### Q: 遥测日志会影响性能吗?

A: 遥测日志使用异步写入,对性能影响很小。只有在启用时才会记录。

### Q: 日志文件会占用多少空间?

A: 取决于使用频率。OpenCode 自动保留最近 10 个日志文件,通常每个文件 1-10MB。

### Q: 如何导出日志进行分析?

A: 日志文件是纯文本格式,可以直接复制或使用工具分析:

```bash
# 复制最新日志
cp ~/.local/share/opencode/log/$(ls -t ~/.local/share/opencode/log/ | head -1) ./opencode.log

# 或者合并所有日志
cat ~/.local/share/opencode/log/*.log > all-logs.txt
```

### Q: 如何在生产环境中使用?

A: 建议在开发和调试时启用,生产环境可以选择性启用或使用采样:

```bash
# 只在需要时启用
OPENCODE_TELEMETRY=1 opencode

# 或者在配置文件中设置
```

## 扩展功能

### 1. 集成到监控系统

可以将日志导出到监控系统(如 Prometheus, Grafana):

```typescript
// 示例: 导出到 Prometheus
import { TelemetryLog } from "@/util/telemetry-log"
import { register, Counter, Histogram } from "prom-client"

const toolCallCounter = new Counter({
  name: "opencode_tool_calls_total",
  help: "Total number of tool calls",
  labelNames: ["tool", "success"],
})

const llmDuration = new Histogram({
  name: "opencode_llm_duration_seconds",
  help: "LLM call duration",
  labelNames: ["provider", "model"],
})
```

### 2. 实时监控

可以创建一个实时监控工具:

```bash
# 实时查看 token 消耗
tail -f ~/.local/share/opencode/log/*.log | grep "token_usage"

# 实时查看工具调用
tail -f ~/.local/share/opencode/log/*.log | grep "tool_call"
```

## 总结

OpenCode 遥测日志系统提供了全面的追踪和监控功能,帮助开发者:

- ✅ 了解 AI 模型的使用情况
- ✅ 优化 token 消耗和成本
- ✅ 调试工具调用问题
- ✅ 监控性能指标
- ✅ 分析用户行为

通过启用遥测日志,你可以获得对 OpenCode 运行的深入洞察!
