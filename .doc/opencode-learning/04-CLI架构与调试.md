# OpenCode CLI 架构深度解析与调试指南

> 🎯 **学习目标**: 理解 CLI 的宏观设计，掌握核心流程，通过添加日志快速上手

## 📐 宏观架构设计

### 整体分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    CLI 层 (用户界面)                      │
│  入口: src/index.ts                                      │
│  命令: src/cli/cmd/*.ts                                  │
│  TUI:  src/cli/cmd/tui/                                 │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  Server 层 (核心业务)                     │
│  API:    src/server/server.ts                           │
│  路由:   Hono HTTP endpoints                            │
│  事件:   SSE (Server-Sent Events)                       │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  业务逻辑层                               │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ Session  │  Agent   │   Tool   │ Provider │         │
│  │  会话管理 │  智能体  │  工具系统 │  AI提供商 │         │
│  └──────────┴──────────┴──────────┴──────────┘         │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                  基础设施层                               │
│  Storage │ LSP │ MCP │ PTY │ File │ Permission          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 核心模块详解

### 1️⃣ CLI 入口层 (`src/index.ts` + `src/cli/cmd/`)

**职责**: 命令解析、参数验证、用户交互

**核心文件**:

```
src/
├── index.ts                 # CLI 主入口，使用 yargs
└── cli/
    ├── cmd/
    │   ├── run.ts           # opencode run - 非交互模式
    │   ├── serve.ts         # opencode serve - 无头服务器
    │   ├── auth.ts          # opencode auth - 认证管理
    │   ├── agent.ts         # opencode agent - Agent 管理
    │   ├── models.ts        # opencode models - 模型列表
    │   └── tui/             # TUI 交互界面
    │       ├── thread.ts    # 主 TUI 命令入口
    │       ├── attach.ts    # 连接远程服务器
    │       └── component/   # TUI 组件
    └── ui.ts                # UI 工具函数（logo, 颜色等）
```

**设计模式**:

- **Command Pattern** - 每个命令是独立的模块
- **Middleware Chain** - yargs 中间件处理日志、认证等

---

### 2️⃣ Server 层 (`src/server/server.ts`)

**职责**: HTTP API 服务、事件推送、请求路由

**核心概念**:

```typescript
// Server 是整个系统的中枢
namespace Server {
  // Hono 应用实例
  export const App: () => Hono

  // 主要路由组
  - /global/*        - 全局 API (health, event, dispose)
  - /session/*       - 会话管理 (CRUD, message, fork)
  - /pty/*           - 伪终端 (创建、输入、事件)
  - /lsp/*           - LSP 请求
  - /mcp/*           - MCP 服务器管理
  - /tool/*          - 工具列表和信息
  - /provider/*      - AI 提供商管理
}
```

**关键流程**:

1. **请求接收** → 路由匹配 → 中间件 → 处理器
2. **SSE 推送** → 全局/会话事件 → 实时更新客户端
3. **实例管理** → 多项目隔离 → Instance.provide()

---

### 3️⃣ 会话层 (`src/session/`)

**职责**: 管理对话上下文、消息流、token 统计

**核心组件**:

```
session/
├── index.ts          # Session 命名空间，CRUD 操作
├── message-v2.ts     # 消息定义（支持流式）
├── processor.ts      # 消息处理器（AI 交互核心）
├── prompt.ts         # 提示词构建（60KB 大文件）
├── system.ts         # 系统提示词
├── compaction.ts     # 上下文压缩
└── revert.ts         # 回滚操作
```

**核心流程**:

```typescript
// 1. 创建会话
Session.create() → Storage.write() → Bus.publish(Created)

// 2. 发送消息
MessageV2.create() → SessionProcessor.process()
  ↓
  构建提示词 (SessionPrompt.build)
  ↓
  调用 AI (Provider.chat)
  ↓
  流式处理响应
  ↓
  工具调用 (如需要)
  ↓
  更新统计 (token, cost)
```

**Message 结构**:

```typescript
MessageV2.Info {
  id: string
  sessionID: string
  role: "user" | "assistant" | "system"

  // 支持多种 part 类型（流式友好）
  parts: Array<
    | TextPart          // 文本
    | ToolCallPart      // 工具调用
    | ToolResultPart    // 工具结果
    | ReasoningPart     // 推理过程
    | FilePart          // 文件附件
  >

  usage: {
    inputTokens: number
    outputTokens: number
    cachedInputTokens: number
  }
}
```

---

### 4️⃣ Agent 层 (`src/agent/`)

**职责**: AI 智能体配置、提示词管理

**核心文件**:

```
agent/
├── agent.ts          # Agent 定义和管理
├── generate.txt      # AI 生成的 agent 提示词模板
└── prompt/
    ├── build.txt     # build agent (默认)
    ├── plan.txt      # plan agent (只读)
    └── general.txt   # general agent (子任务)
```

**Agent 配置**:

```typescript
Agent.Info {
  metadata: {
    name: string
    description: string
  }
  model: {
    modelID: string
    providerID: string
  }
  prompt: string        // 自定义提示词
  options: Record       // temperature, maxTokens 等
  steps: number         // 最大推理步数
}
```

---

### 5️⃣ Tool 层 (`src/tool/`)

**职责**: 提供 AI 可调用的能力

**核心结构**:

```
tool/
├── tool.ts           # Tool 定义和基础接口
├── registry.ts       # 工具注册中心
├── bash.ts           # 执行命令
├── read.ts           # 读文件
├── write.ts          # 写文件
├── edit.ts           # 编辑文件（diff）
├── grep.ts           # 搜索
├── lsp.ts            # LSP 请求
└── ... (44个工具)
```

**Tool 执行流程**:

```
AI 决定调用工具
  ↓
Tool.execute(args, context)
  ↓
参数验证 (Zod schema)
  ↓
权限检查 (Permission)
  ↓
执行逻辑
  ↓
输出截断 (Truncation)
  ↓
返回结果 { title, metadata, output }
```

---

### 6️⃣ TUI 层 (`src/cli/cmd/tui/`)

**职责**: 终端用户界面

**技术栈**:

- **SolidJS** - 响应式 UI
- **OpenTUI** - 终端渲染
- **Ghostty** - 终端仿真

**核心结构**:

```
tui/
├── thread.ts         # TUI 主命令
├── worker.ts         # Worker 线程（隔离渲染）
├── routes/           # 路由和页面
│   └── session/      # 会话页面
│       ├── index.tsx       # 主聊天界面
│       ├── sidebar.tsx     # 侧边栏
│       ├── header.tsx      # 顶栏
│       └── permission.tsx  # 权限确认
└── component/        # 可复用组件
    ├── logo.tsx      # Logo 组件
    ├── prompt/       # 输入框
    └── tips.tsx      # 提示信息
```

**TUI ↔ Server 通信**:

```typescript
// 1. 创建 SDK 客户端
const client = createOpencodeClient({ baseUrl })

// 2. 订阅事件 (SSE)
const eventStream = client.global.event()
for await (const event of eventStream) {
  handleEvent(event)
}

// 3. 发送消息
await client.session.message.create({
  sessionID,
  role: "user",
  parts: [{ type: "text", text: input }],
})
```

---

## 🔄 关键流程详解

### 流程 1: CLI 启动流程

```
用户运行 opencode
  ↓
src/index.ts (入口)
  ↓
yargs 解析参数
  ↓
middleware 初始化日志
  ↓
匹配命令 (默认 tui/thread.ts)
  ↓
TuiThreadCommand.handler()
  ↓
启动或连接 Server
  ├─ 启动: Worker.spawn(Server.start)
  └─ 连接: SDK 连接远程
  ↓
渲染 TUI (SolidJS + OpenTUI)
  ↓
用户交互...
```

### 流程 2: 消息发送流程

```
用户在 TUI 输入消息
  ↓
TUI: 捕获输入事件
  ↓
SDK: client.session.message.create()
  ↓
HTTP POST /session/:id/message
  ↓
Server: 路由处理器
  ↓
SessionProcessor.process()
  ├─ 1. 构建完整上下文 (历史消息 + 系统提示)
  ├─ 2. 调用 Provider.chat() (流式)
  ├─ 3. 处理 AI 响应
  │    ├─ text-delta → 更新消息
  │    └─ tool-call → 执行工具
  └─ 4. 更新统计
  ↓
SSE: 推送更新到 TUI
  ↓
TUI: 响应式更新界面
```

### 流程 3: 工具调用流程

```
AI 决定调用工具 (如 read_file)
  ↓
SessionProcessor 收到 tool-call
  ↓
查找工具定义 (ToolRegistry.get)
  ↓
权限检查
  ├─ 白名单 → 直接执行
  ├─ 黑名单 → 拒绝
  └─ 需确认 → 推送 PermissionRequest
      ↓
      用户确认
      ↓
      继续执行
  ↓
Tool.execute(args, ctx)
  ├─ 验证参数 (Zod)
  ├─ 执行业务逻辑
  └─ 返回结果
  ↓
结果返回给 AI
  ↓
AI 继续生成回复
```

---

## 🔧 添加日志进行学习

### 策略 1: 在关键流程入口添加日志

#### 1. CLI 启动日志

```typescript
// src/index.ts (第 115 行附近)

try {
  console.log("🚀 [CLI] Starting OpenCode...")
  console.log("📝 [CLI] Arguments:", process.argv.slice(2))

  await cli.parse()

  console.log("✅ [CLI] Command completed successfully")
} catch (e) {
  console.log("❌ [CLI] Error occurred:", e.message)
  // ... 原有错误处理
}
```

#### 2. Server 启动日志

```typescript
// src/server/server.ts (在 App 定义后)

export const App: () => Hono = lazy(() => {
  console.log("🌐 [SERVER] Initializing Hono app...")

  return app
    .onError((err, c) => {
      console.log("⚠️  [SERVER] Request error:", {
        path: c.req.path,
        method: c.req.method,
        error: err.message,
      })
      // ... 原有处理
    })
    .use(async (c, next) => {
      console.log("📥 [SERVER] Incoming request:", {
        method: c.req.method,
        path: c.req.path,
        headers: Object.fromEntries(c.req.header()),
      })
      await next()
      console.log("📤 [SERVER] Response sent:", {
        status: c.res.status,
        path: c.req.path,
      })
    })
  // ... 其他中间件和路由
})
```

#### 3. 会话处理日志

```typescript
// src/session/processor.ts (找到主处理函数)

export namespace SessionProcessor {
  export async function process(sessionID: string, messageID: string) {
    console.log("💬 [SESSION] Starting message processing:", {
      sessionID,
      messageID,
    })

    // 1. 准备上下文
    console.log("📚 [SESSION] Building context...")
    const messages = await SessionPrompt.build(sessionID)
    console.log("📚 [SESSION] Context built:", {
      messageCount: messages.length,
      totalTokens: estimateTokens(messages),
    })

    // 2. 调用 AI
    console.log("🤖 [SESSION] Calling AI provider...")
    const stream = await provider.chat({ messages, tools })

    // 3. 处理流
    console.log("🌊 [SESSION] Processing stream...")
    for await (const chunk of stream) {
      console.log("🔄 [SESSION] Stream chunk:", {
        type: chunk.type,
        delta: chunk.type === "text-delta" ? chunk.textDelta?.slice(0, 50) : undefined,
      })

      if (chunk.type === "tool-call") {
        console.log("🔧 [SESSION] Tool call detected:", {
          toolName: chunk.toolCall.toolName,
          args: chunk.toolCall.args,
        })
      }
    }

    console.log("✅ [SESSION] Message processing complete")
  }
}
```

#### 4. 工具执行日志

```typescript
// src/tool/tool.ts (在 Tool.define 中)

export function define<Parameters extends z.ZodType, Result extends Metadata>(
  id: string,
  init: Info<Parameters, Result>["init"],
): Info<Parameters, Result> {
  return {
    id,
    init: async (initCtx) => {
      const toolInfo = init instanceof Function ? await init(initCtx) : init
      const execute = toolInfo.execute

      toolInfo.execute = async (args, ctx) => {
        console.log(`🔧 [TOOL:${id}] Executing with args:`, args)
        console.log(`🔧 [TOOL:${id}] Context:`, {
          sessionID: ctx.sessionID,
          messageID: ctx.messageID,
          agent: ctx.agent,
        })

        try {
          // 参数验证
          toolInfo.parameters.parse(args)
          console.log(`✅ [TOOL:${id}] Arguments validated`)
        } catch (error) {
          console.log(`❌ [TOOL:${id}] Validation failed:`, error.message)
          throw new Error(`Invalid arguments for ${id}`)
        }

        // 执行
        const startTime = Date.now()
        const result = await execute(args, ctx)
        const duration = Date.now() - startTime

        console.log(`✅ [TOOL:${id}] Executed in ${duration}ms`)
        console.log(`📊 [TOOL:${id}] Result:`, {
          title: result.title,
          outputLength: result.output.length,
          metadata: result.metadata,
        })

        return result
      }

      return toolInfo
    },
  }
}
```

#### 5. TUI 生命周期日志

```typescript
// src/cli/cmd/tui/thread.ts (handler 函数中)

export const TuiThreadCommand: CommandModule = {
  // ...
  async handler(opts) {
    console.log('🖥️  [TUI] Starting TUI...')
    console.log('🖥️  [TUI] Options:', opts)

    // 启动服务器
    if (shouldStartServer) {
      console.log('🌐 [TUI] Starting embedded server...')
      await startServer()
      console.log('✅ [TUI] Server started')
    }

    // 连接
    console.log('🔌 [TUI] Connecting to server:', url)
    const client = createOpencodeClient({ baseUrl: url })

    // 订阅事件
    console.log('📡 [TUI] Subscribing to events...')
    const events = client.global.event()

    // 渲染
    console.log('🎨 [TUI] Rendering interface...')
    render(() => <App />, container)

    console.log('✅ [TUI] TUI initialized')
  }
}
```

---

### 策略 2: 使用结构化日志

创建一个日志工具函数：

```typescript
// src/util/debug-log.ts (新文件)

export namespace DebugLog {
  const enabled = process.env.OPENCODE_DEBUG === "1"

  export function cli(...args: any[]) {
    if (!enabled) return
    console.log("🚀 [CLI]", new Date().toISOString(), ...args)
  }

  export function server(...args: any[]) {
    if (!enabled) return
    console.log("🌐 [SERVER]", new Date().toISOString(), ...args)
  }

  export function session(...args: any[]) {
    if (!enabled) return
    console.log("💬 [SESSION]", new Date().toISOString(), ...args)
  }

  export function tool(toolName: string, ...args: any[]) {
    if (!enabled) return
    console.log(`🔧 [TOOL:${toolName}]`, new Date().toISOString(), ...args)
  }

  export function tui(...args: any[]) {
    if (!enabled) return
    console.log("🖥️  [TUI]", new Date().toISOString(), ...args)
  }

  export function trace(component: string, fn: string, data?: any) {
    if (!enabled) return
    console.log(`📍 [TRACE:${component}:${fn}]`, new Date().toISOString(), data)
  }
}
```

使用方式：

```bash
# 启用调试日志
export OPENCODE_DEBUG=1
bun dev

# 你会看到详细的执行流程
```

---

## 📝 推荐的学习路径

### Phase 1: 理解启动流程（1-2天）

1. **添加日志**: 在 `src/index.ts` 添加启动日志
2. **跟踪流程**: 运行 `opencode --help`，观察输出
3. **阅读代码**:
   - `src/index.ts` - CLI 入口
   - `src/cli/cmd/tui/thread.ts` - TUI 启动
   - `src/server/server.ts` - Server 初始化

### Phase 2: 理解消息流（2-3天）

1. **添加日志**: 在 Session 和 Tool 层添加日志
2. **发送测试消息**: 启动 TUI，发送 "读取 README.md"
3. **观察流程**:
   - 消息如何到达 Server
   - SessionProcessor 如何处理
   - 工具如何执行
   - 结果如何返回

### Phase 3: 深入 Agent 和 Tool（3-5天）

1. **创建自定义工具**: 参考 `src/tool/hello.ts` 示例
2. **修改 Agent 提示词**: 编辑 `src/agent/prompt/build.txt`
3. **观察行为变化**: 测试不同的提示词效果

### Phase 4: TUI 交互（可选，2-3天）

1. **理解 SolidJS**: 学习响应式 UI
2. **修改组件**: 改变 logo、颜色、布局
3. **添加功能**: 新的快捷键、命令等

---

## 🎯 实战练习

### 练习 1: 添加执行时间统计

在每个工具执行前后记录时间，统计耗时：

```typescript
// src/tool/tool.ts

toolInfo.execute = async (args, ctx) => {
  const startTime = performance.now()

  try {
    const result = await execute(args, ctx)
    const duration = performance.now() - startTime

    // 添加到 metadata
    result.metadata.executionTime = Math.round(duration)

    console.log(`⏱️  [PERF:${id}] Execution time: ${duration.toFixed(2)}ms`)

    return result
  } catch (error) {
    const duration = performance.now() - startTime
    console.log(`⏱️  [PERF:${id}] Failed after: ${duration.toFixed(2)}ms`)
    throw error
  }
}
```

### 练习 2: 跟踪消息流

创建一个消息跟踪器：

```typescript
// src/session/message-tracker.ts

export class MessageTracker {
  private traces = new Map<string, any[]>()

  track(messageID: string, event: string, data?: any) {
    if (!this.traces.has(messageID)) {
      this.traces.set(messageID, [])
    }

    this.traces.get(messageID)!.push({
      timestamp: Date.now(),
      event,
      data,
    })

    console.log(`📊 [TRACK:${messageID}] ${event}`, data)
  }

  getTimeline(messageID: string) {
    return this.traces.get(messageID) || []
  }

  printTimeline(messageID: string) {
    const timeline = this.getTimeline(messageID)
    console.log(`\n📊 Message Timeline for ${messageID}:`)

    const startTime = timeline[0]?.timestamp || 0
    timeline.forEach((event, index) => {
      const elapsed = event.timestamp - startTime
      console.log(`  ${index + 1}. [+${elapsed}ms] ${event.event}`)
    })
  }
}

export const tracker = new MessageTracker()
```

使用：

```typescript
// 在 SessionProcessor.process 中
tracker.track(messageID, "START")
tracker.track(messageID, "CONTEXT_BUILT", { messageCount })
tracker.track(messageID, "AI_CALLED")
tracker.track(messageID, "TOOL_EXECUTED", { toolName })
tracker.track(messageID, "COMPLETE")

tracker.printTimeline(messageID)
```

---

## 📚 关键文件速查

| 层级        | 文件                                         | 核心职责   | 重要度     |
| ----------- | -------------------------------------------- | ---------- | ---------- |
| **CLI**     | `src/index.ts`                               | CLI 入口   | ⭐⭐⭐⭐⭐ |
| **CLI**     | `src/cli/cmd/tui/thread.ts`                  | TUI 主命令 | ⭐⭐⭐⭐⭐ |
| **Server**  | `src/server/server.ts`                       | HTTP API   | ⭐⭐⭐⭐⭐ |
| **Session** | `src/session/index.ts`                       | 会话管理   | ⭐⭐⭐⭐⭐ |
| **Session** | `src/session/processor.ts`                   | 消息处理   | ⭐⭐⭐⭐⭐ |
| **Session** | `src/session/prompt.ts`                      | 提示词构建 | ⭐⭐⭐⭐   |
| **Agent**   | `src/agent/agent.ts`                         | Agent 定义 | ⭐⭐⭐⭐   |
| **Tool**    | `src/tool/tool.ts`                           | 工具基础   | ⭐⭐⭐⭐⭐ |
| **Tool**    | `src/tool/registry.ts`                       | 工具注册   | ⭐⭐⭐⭐   |
| **Tool**    | `src/tool/bash.ts`                           | 命令执行   | ⭐⭐⭐     |
| **Tool**    | `src/tool/edit.ts`                           | 文件编辑   | ⭐⭐⭐     |
| **TUI**     | `src/cli/cmd/tui/routes/session/index.tsx`   | 聊天界面   | ⭐⭐⭐⭐   |
| **TUI**     | `src/cli/cmd/tui/component/prompt/index.tsx` | 输入框     | ⭐⭐⭐     |

---

## 💡 调试技巧

### 1. 使用 Bun 调试器

```bash
# 启动调试模式
bun run --inspect-wait ./src/index.ts

# 在 Chrome 中打开 chrome://inspect
# 连接到调试会话
```

### 2. 条件断点

在关键位置添加条件日志：

```typescript
if (process.env.DEBUG_SESSION) {
  console.log("Debug info:", data)
}
```

### 3. 日志文件

```typescript
import fs from "fs"

const logFile = "/tmp/opencode-debug.log"

function debugLog(...args: any[]) {
  const message = args.map((a) => JSON.stringify(a, null, 2)).join(" ")
  fs.appendFileSync(logFile, `${new Date().toISOString()} ${message}\n`)
}
```

---

## 🎉 总结

通过添加日志，你可以：

1. **理解流程** - 看到数据如何在各层流动
2. **定位问题** - 快速找到异常位置
3. **性能分析** - 识别瓶颈
4. **学习设计** - 理解架构决策

**建议**：

- 从 CLI 入口开始，逐层深入
- 先理解主流程，再关注细节
- 边看日志边阅读代码
- 修改参数观察行为变化

**下一步**：

1. 运行带日志的版本
2. 发送测试消息
3. 分析完整的执行流程
4. 尝试创建自己的工具

祝学习顺利！🚀
