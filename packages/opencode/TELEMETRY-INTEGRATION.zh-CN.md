# OpenCode 遥测集成示例

本文档展示如何在 OpenCode 代码库中集成遥测日志系统。

## 目录结构

```
src/
├── util/
│   ├── telemetry-log.ts          # 遥测日志核心模块
│   ├── log.ts                     # 现有日志系统
│   └── debug-log.ts               # 调试日志系统
├── tool/
│   ├── telemetry.ts               # 工具调用遥测包装器
│   └── tool.ts                    # 工具定义
├── session/
│   ├── llm-telemetry.ts           # LLM 调用遥测包装器
│   └── llm.ts                     # LLM 调用逻辑
└── mcp/
    └── client.ts                  # MCP 客户端 (待集成)
```

## 集成步骤

### 1. 在 LLM 调用中集成

修改 `src/session/llm.ts`:

```typescript
import { LLMTelemetry } from "./llm-telemetry"

export namespace LLM {
  export async function stream(input: StreamInput) {
    // 使用遥测包装器
    return LLMTelemetry.wrapStream(input, async (input) => {
      // 原有的 streamText 调用逻辑
      return streamText({
        // ... 现有配置
      })
    })
  }
}
```

### 2. 在工具注册中集成

修改工具注册逻辑 (例如 `src/session/process.ts` 或工具加载器):

```typescript
import { ToolTelemetry } from "../tool/telemetry"
import { ShellTool } from "../tool/shell"
import { EditTool } from "../tool/edit"
// ... 其他工具导入

// 包装所有工具
const tools = {
  shell: ToolTelemetry.wrapTool(ShellTool),
  edit: ToolTelemetry.wrapTool(EditTool),
  // ... 其他工具
}
```

### 3. 在 MCP 调用中集成

创建 `src/mcp/telemetry.ts`:

```typescript
import { TelemetryLog } from "../util/telemetry-log"

export namespace MCPTelemetry {
  export async function wrapMCPCall<T>(
    sessionID: string,
    messageID: string,
    mcpName: string,
    toolName: string,
    input: any,
    fn: () => Promise<T>,
  ): Promise<T> {
    const tracker = TelemetryLog.trackMCPCall({
      sessionID,
      messageID,
      mcpName,
      toolName,
      input,
      timestamp: Date.now(),
    })

    try {
      const result = await fn()

      tracker.end({
        sessionID,
        messageID,
        mcpName,
        toolName,
        success: true,
        output: result,
      })

      return result
    } catch (error) {
      tracker.end({
        sessionID,
        messageID,
        mcpName,
        toolName,
        success: false,
        error: error instanceof Error ? error.message : String(error),
      })

      throw error
    }
  }
}
```

然后在 MCP 客户端中使用:

```typescript
import { MCPTelemetry } from "./telemetry"

class MCPClient {
  async callTool(toolName: string, input: any) {
    return MCPTelemetry.wrapMCPCall(this.sessionID, this.messageID, this.mcpName, toolName, input, async () => {
      // 原有的 MCP 调用逻辑
      return this.client.callTool({ name: toolName, arguments: input })
    })
  }
}
```

### 4. 在 Session 中记录统计

修改 `src/session/session.ts` (或相关文件):

```typescript
import { TelemetryLog } from "../util/telemetry-log"

export class Session {
  private stats = {
    totalMessages: 0,
    totalToolCalls: 0,
    totalMCPCalls: 0,
    totalLLMCalls: 0,
    totalTokens: 0,
    startTime: Date.now(),
  }

  async onMessageComplete() {
    this.stats.totalMessages++

    // 记录 session 统计
    TelemetryLog.sessionStats({
      sessionID: this.id,
      totalMessages: this.stats.totalMessages,
      totalToolCalls: this.stats.totalToolCalls,
      totalMCPCalls: this.stats.totalMCPCalls,
      totalLLMCalls: this.stats.totalLLMCalls,
      totalTokens: this.stats.totalTokens,
      totalDuration: Date.now() - this.stats.startTime,
      timestamp: Date.now(),
    })
  }

  async onToolCall() {
    this.stats.totalToolCalls++
  }

  async onMCPCall() {
    this.stats.totalMCPCalls++
  }

  async onLLMCall(tokens: number) {
    this.stats.totalLLMCalls++
    this.stats.totalTokens += tokens
  }
}
```

## 配置选项

### 环境变量

```bash
# 启用遥测日志
export OPENCODE_TELEMETRY=1

# 或者启用调试模式(包含遥测)
export OPENCODE_DEBUG=1

# 设置日志级别
export OPENCODE_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARN, ERROR
```

### 代码配置

在 `src/util/telemetry-log.ts` 中可以配置:

```typescript
export namespace TelemetryLog {
  // 可以通过配置文件控制
  const config = {
    enableToolTelemetry: true,
    enableMCPTelemetry: true,
    enableLLMTelemetry: true,
    enableTokenTracking: true,
    enableCostEstimation: true,
  }

  // 检查是否启用遥测
  const enabled = process.env.OPENCODE_TELEMETRY === "1" || process.env.OPENCODE_DEBUG === "1"
}
```

## 使用示例

### 启用遥测并运行

```bash
# 启用遥测
export OPENCODE_TELEMETRY=1

# 运行 OpenCode
opencode

# 在另一个终端实时查看日志
tail -f ~/.local/share/opencode/log/$(ls -t ~/.local/share/opencode/log/ | head -1)
```

### 分析日志

```bash
# 查看统计信息
./packages/opencode/script/analyze-telemetry.sh --latest --stats

# 查看 token 使用
./packages/opencode/script/analyze-telemetry.sh --latest --tokens

# 查看工具调用
./packages/opencode/script/analyze-telemetry.sh --latest --tools

# 估算成本
./packages/opencode/script/analyze-telemetry.sh --latest --cost

# 导出为 CSV
./packages/opencode/script/analyze-telemetry.sh --latest --export telemetry.csv
```

## 日志示例

### 工具调用日志

```
INFO  2026-01-25T09:00:00 +150ms service=telemetry sessionID=01JKX... messageID=01JKY... callID=01JKZ... tool=shell agent=build tool_call_start input={"command":"npm test"}
INFO  2026-01-25T09:00:01 +1200ms service=telemetry sessionID=01JKX... messageID=01JKY... callID=01JKZ... tool=shell tool_call_end success=true duration=1200 outputLength=512
```

### LLM 调用日志

```
INFO  2026-01-25T09:00:02 +50ms service=telemetry sessionID=01JKX... messageID=01JKY... provider=openai model=gpt-4 agent=build llm_call_start inputMessages=5
INFO  2026-01-25T09:00:05 +3000ms service=telemetry sessionID=01JKX... messageID=01JKY... provider=openai model=gpt-4 llm_call_end success=true duration=3000 inputTokens=1500 outputTokens=800 totalTokens=2300 finishReason=stop
```

### Token 使用日志

```
INFO  2026-01-25T09:00:05 +10ms service=telemetry sessionID=01JKX... messageID=01JKY... provider=openai model=gpt-4 token_usage promptTokens=1500 completionTokens=800 totalTokens=2300
💰 [COST] openai/gpt-4: 2.3K tokens ≈ $0.0930
```

## 性能影响

遥测日志系统设计为低开销:

- ✅ 异步写入,不阻塞主流程
- ✅ 只在启用时才记录
- ✅ 使用高效的日志格式
- ✅ 自动日志轮转,避免磁盘占用过大

**性能开销**: < 1% (在大多数情况下可以忽略)

## 扩展功能

### 1. 集成到监控系统

可以将遥测数据导出到监控系统:

```typescript
// 示例: 导出到 Prometheus
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

// 在遥测事件中更新指标
TelemetryLog.toolCallEnd = (event) => {
  // ... 原有逻辑
  toolCallCounter.inc({ tool: event.toolName, success: event.success })
}
```

### 2. 实时仪表板

可以创建一个实时仪表板:

```bash
# 使用 watch 命令实时更新
watch -n 1 './packages/opencode/script/analyze-telemetry.sh --latest --stats'
```

### 3. 告警系统

可以基于遥测数据创建告警:

```bash
#!/bin/bash
# alert-on-high-cost.sh

COST=$(./packages/opencode/script/analyze-telemetry.sh --latest --cost | grep "总计" | awk '{print $2}' | tr -d '$')

if (( $(echo "$COST > 1.0" | bc -l) )); then
    echo "⚠️  警告: Token 成本过高: \$$COST"
    # 发送通知...
fi
```

## 故障排除

### 问题: 日志没有生成

**解决方案:**

1. 检查环境变量是否设置: `echo $OPENCODE_TELEMETRY`
2. 检查日志目录权限: `ls -la ~/.local/share/opencode/log/`
3. 检查日志级别设置

### 问题: 日志文件过大

**解决方案:**

1. OpenCode 自动保留最近 10 个日志文件
2. 可以手动清理旧日志: `rm ~/.local/share/opencode/log/*.log`

### 问题: 性能下降

**解决方案:**

1. 检查是否启用了过多的日志级别
2. 考虑使用采样: 只记录部分事件
3. 禁用遥测: `unset OPENCODE_TELEMETRY`

## 总结

通过集成遥测日志系统,你可以:

- ✅ 追踪所有工具调用和 MCP 调用
- ✅ 监控 AI 模型的使用和 token 消耗
- ✅ 分析性能瓶颈
- ✅ 估算使用成本
- ✅ 调试问题
- ✅ 优化系统性能

遥测数据对于理解和优化 OpenCode 的运行至关重要!
