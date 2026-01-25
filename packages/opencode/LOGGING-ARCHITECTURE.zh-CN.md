# OpenCode 日志系统架构与原理

## 目录

1. [系统架构](#系统架构)
2. [日志层次](#日志层次)
3. [HTTP 日志原理](#http-日志原理)
4. [遥测日志原理](#遥测日志原理)
5. [时序图](#时序图)
6. [数据流](#数据流)
7. [实现细节](#实现细节)

---

## 系统架构

OpenCode 的日志系统采用分层架构,包含三个主要层次:

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Application)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Session │  │   Tool   │  │   MCP    │  │   LLM    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    遥测层 (Telemetry)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ToolTelemetry│  │ MCPTelemetry │  │ LLMTelemetry │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                   TelemetryLog                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     传输层 (Transport)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │FetchIntercept│  │   HTTPLog    │  │  DebugLog    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     存储层 (Storage)                         │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │   Log File   │  │    stderr    │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 日志层次

### 1. 基础日志 (Log)

**位置**: `src/util/log.ts`

**功能**:

- 提供基础的日志记录功能
- 支持日志级别 (DEBUG, INFO, WARN, ERROR)
- 写入日志文件
- 自动日志轮转

**使用**:

```typescript
const log = Log.create({ service: "my-service" })
log.info("message", { key: "value" })
```

**输出格式**:

```
INFO  2026-01-25T09:00:00 +150ms service=my-service key=value message
```

### 2. 调试日志 (DebugLog)

**位置**: `src/util/debug-log.ts`

**功能**:

- 开发调试专用
- 彩色终端输出
- 性能追踪
- 流程追踪

**启用**: `export OPENCODE_DEBUG=1`

**特点**:

- 只输出到 stderr,不写入文件
- 提供丰富的上下文信息
- 支持计时器和流程追踪

### 3. 遥测日志 (TelemetryLog)

**位置**: `src/util/telemetry-log.ts`

**功能**:

- 记录业务指标
- 追踪工具调用、MCP 调用、LLM 调用
- Token 使用统计
- 性能指标

**启用**: `export OPENCODE_TELEMETRY=1`

**特点**:

- 结构化日志
- 支持追踪器 (Tracker)
- 自动计算耗时

### 4. HTTP 日志 (HTTPLog)

**位置**: `src/util/http-log.ts`

**功能**:

- 记录 HTTP 请求和响应
- 敏感信息脱敏
- 彩色终端输出

**启用**: `export OPENCODE_HTTP_LOG=1`

**特点**:

- 详细的请求/响应信息
- 自动脱敏
- 智能截断

---

## HTTP 日志原理

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                         应用代码                              │
│                    (Session, LLM, etc.)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI SDK (Vercel AI)                        │
│                  streamText / generateText                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Provider SDK (OpenAI, etc.)                │
│                    使用 fetch 发送请求                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              FetchInterceptor (全局拦截器)                    │
│                  拦截所有 fetch 调用                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      HTTPLog (日志记录)                       │
│              记录请求/响应,脱敏,格式化输出                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    原始 fetch (网络请求)                      │
│                  发送到 AI Provider API                       │
└─────────────────────────────────────────────────────────────┘
```

### 工作流程

#### 1. 初始化阶段

```typescript
// src/session/llm.ts
import { FetchInterceptor } from "@/util/fetch-interceptor"

// 模块加载时自动安装拦截器
FetchInterceptor.install()
```

**发生的事情**:

1. 保存原始的 `globalThis.fetch`
2. 替换为自定义的 fetch 函数
3. 设置 `_isInstalled = true`

#### 2. 请求拦截阶段

当应用发起 HTTP 请求时:

```typescript
// AI SDK 内部调用
fetch("https://api.openai.com/v1/chat/completions", {
  method: "POST",
  headers: { ... },
  body: JSON.stringify({ ... })
})
```

**拦截器处理**:

```typescript
// FetchInterceptor.install() 中的逻辑
globalThis.fetch = async (input, init) => {
  // 1. 检查是否是 AI Provider 请求
  const isAIRequest = url.includes('api.openai.com') || ...

  if (!isAIRequest) {
    // 不是 AI 请求,直接调用原始 fetch
    return originalFetch(input, init)
  }

  // 2. 提取 provider 和 model 信息
  const { provider, model } = extractProviderInfo(url, init)

  // 3. 记录请求
  HTTPLog.logRequest(provider, model, url, method, headers, body)

  // 4. 调用原始 fetch
  const response = await originalFetch(input, init)

  // 5. 记录响应
  HTTPLog.logResponse(provider, model, status, ...)

  return response
}
```

#### 3. 日志输出阶段

**HTTPLog.logRequest()**:

```typescript
export function logRequest(provider, model, url, method, headers, body) {
  if (!enabled) return

  // 1. 脱敏处理
  const sanitizedHeaders = sanitizeHeaders(headers)
  const sanitizedBody = sanitizeBody(body)

  // 2. 终端输出 (彩色)
  console.error(`🌐 HTTP REQUEST`)
  console.error(`Provider: ${provider}`)
  console.error(`Model: ${model}`)
  console.error(`URL: ${url}`)
  console.error(formatJSON(sanitizedBody))

  // 3. 写入日志文件
  log.info("http_request", {
    provider,
    model,
    url,
    headers: JSON.stringify(sanitizedHeaders),
    body: JSON.stringify(sanitizedBody),
  })
}
```

---

## 遥测日志原理

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      工具调用 (Tool)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              ToolTelemetry.wrapTool()                        │
│                  包装工具的 execute 函数                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           TelemetryLog.trackToolCall()                       │
│              创建 Tracker,记录开始时间                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  执行原始工具逻辑                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              tracker.end()                                   │
│          记录结束时间,计算耗时,写入日志                       │
└─────────────────────────────────────────────────────────────┘
```

### 工作流程

#### 1. 工具包装

```typescript
// src/tool/telemetry.ts
export function wrapTool(tool) {
  return {
    ...tool,
    init: async (ctx) => {
      const toolInfo = await tool.init(ctx)
      return wrapToolExecute(toolInfo, tool.id)
    },
  }
}

function wrapToolExecute(toolInfo, toolId) {
  const originalExecute = toolInfo.execute

  toolInfo.execute = async (args, ctx) => {
    // 创建追踪器
    const tracker = TelemetryLog.trackToolCall({
      sessionID: ctx.sessionID,
      messageID: ctx.messageID,
      callID: ctx.callID,
      toolName: toolId,
      agent: ctx.agent,
      input: args,
      timestamp: Date.now(),
    })

    try {
      // 执行原始工具
      const result = await originalExecute(args, ctx)

      // 记录成功
      tracker.end({
        success: true,
        output: result.output,
        metadata: result.metadata,
      })

      return result
    } catch (error) {
      // 记录失败
      tracker.end({
        success: false,
        error: error.message,
      })

      throw error
    }
  }

  return toolInfo
}
```

#### 2. Tracker 机制

```typescript
// src/util/telemetry-log.ts
export class Tracker<TStart, TEnd> {
  private startTime: number

  constructor(startEvent, onStart, onEnd) {
    this.startTime = Date.now()

    // 记录开始事件
    onStart(startEvent)
  }

  end(result) {
    const duration = Date.now() - this.startTime

    // 记录结束事件
    this.onEnd({
      ...result,
      duration,
      timestamp: Date.now(),
    })

    return duration
  }
}
```

---

## 时序图

### 1. HTTP 请求日志时序图

```mermaid
sequenceDiagram
    participant App as 应用代码
    participant SDK as AI SDK
    participant Interceptor as FetchInterceptor
    participant HTTPLog as HTTPLog
    participant Fetch as 原始 fetch
    participant API as AI Provider API
    participant Log as Log File
    participant Terminal as Terminal

    App->>SDK: streamText(...)
    SDK->>Interceptor: fetch(url, options)

    Note over Interceptor: 检查是否是 AI 请求

    Interceptor->>Interceptor: extractProviderInfo()
    Interceptor->>HTTPLog: logRequest(provider, model, ...)

    HTTPLog->>HTTPLog: sanitizeHeaders()
    HTTPLog->>HTTPLog: sanitizeBody()
    HTTPLog->>Terminal: console.error(彩色输出)
    HTTPLog->>Log: log.info("http_request", ...)

    Interceptor->>Fetch: originalFetch(url, options)
    Fetch->>API: HTTP POST
    API-->>Fetch: HTTP Response
    Fetch-->>Interceptor: Response

    Interceptor->>Interceptor: clone response
    Interceptor->>Interceptor: parse response body
    Interceptor->>HTTPLog: logResponse(status, body, ...)

    HTTPLog->>Terminal: console.error(彩色输出)
    HTTPLog->>Log: log.info("http_response", ...)

    Interceptor-->>SDK: Response
    SDK-->>App: StreamTextResult
```

### 2. 工具调用遥测时序图

```mermaid
sequenceDiagram
    participant Session as Session
    participant Tool as Tool (wrapped)
    participant Telemetry as ToolTelemetry
    participant Tracker as Tracker
    participant TLog as TelemetryLog
    participant Log as Log File

    Session->>Tool: execute(args, ctx)

    Note over Tool: 已被 wrapTool 包装

    Tool->>Telemetry: wrapToolExecute()
    Telemetry->>TLog: trackToolCall(event)
    TLog->>Tracker: new Tracker(startEvent)

    Tracker->>Log: log.info("tool_call_start", ...)

    Telemetry->>Tool: originalExecute(args, ctx)

    Note over Tool: 执行工具逻辑

    Tool-->>Telemetry: result

    Telemetry->>Tracker: tracker.end(result)
    Tracker->>Tracker: duration = now - startTime
    Tracker->>Log: log.info("tool_call_end", ...)

    Telemetry-->>Session: result
```

### 3. LLM 调用完整时序图

```mermaid
sequenceDiagram
    participant Session as Session
    participant LLM as LLM.stream()
    participant LLMTelem as LLMTelemetry
    participant Tracker as LLM Tracker
    participant SDK as AI SDK
    participant Interceptor as FetchInterceptor
    participant HTTPLog as HTTPLog
    participant TLog as TelemetryLog
    participant API as AI Provider

    Session->>LLM: stream(input)
    LLM->>LLMTelem: wrapStream(input, streamFn)

    LLMTelem->>TLog: trackLLMCall(event)
    TLog->>Tracker: new Tracker(startEvent)
    Tracker->>TLog: llmCallStart(event)

    LLMTelem->>SDK: streamText(config)
    SDK->>Interceptor: fetch(url, options)

    Interceptor->>HTTPLog: logRequest(...)
    HTTPLog->>HTTPLog: 终端输出 + 日志文件

    Interceptor->>API: HTTP POST
    API-->>Interceptor: HTTP Response (stream)

    Interceptor->>HTTPLog: logResponse(...)
    HTTPLog->>HTTPLog: 终端输出 + 日志文件

    Interceptor-->>SDK: Response
    SDK-->>LLMTelem: StreamTextResult

    Note over LLMTelem: 监听 stream 完成

    LLMTelem->>Tracker: tracker.end(usage)
    Tracker->>TLog: llmCallEnd(event)

    LLMTelem->>TLog: tokenUsage(event)
    TLog->>TLog: 终端输出成本估算

    LLMTelem-->>Session: StreamTextResult
```

---

## 数据流

### 1. HTTP 请求数据流

```
用户输入
   ↓
Session.process()
   ↓
LLM.stream()
   ↓
AI SDK streamText()
   ↓
Provider SDK (OpenAI, etc.)
   ↓
fetch(url, options)
   ↓
┌─────────────────────────────────┐
│   FetchInterceptor.install()    │
│                                 │
│  1. 检查 URL (是否是 AI 请求)    │
│  2. 提取 provider/model         │
│  3. HTTPLog.logRequest()        │
│     ├─ 脱敏 headers/body        │
│     ├─ 终端彩色输出             │
│     └─ 写入日志文件             │
│  4. 调用原始 fetch              │
│  5. 解析响应                    │
│  6. HTTPLog.logResponse()       │
│     ├─ 终端彩色输出             │
│     └─ 写入日志文件             │
└─────────────────────────────────┘
   ↓
原始 fetch → AI Provider API
   ↓
HTTP Response
   ↓
返回给应用
```

### 2. 遥测数据流

```
工具调用
   ↓
ToolTelemetry.wrapTool()
   ↓
┌─────────────────────────────────┐
│  TelemetryLog.trackToolCall()   │
│                                 │
│  1. 创建 Tracker                │
│  2. 记录开始时间                │
│  3. toolCallStart()             │
│     └─ 写入日志文件             │
└─────────────────────────────────┘
   ↓
执行工具逻辑
   ↓
┌─────────────────────────────────┐
│     tracker.end(result)         │
│                                 │
│  1. 计算耗时                    │
│  2. toolCallEnd()               │
│     └─ 写入日志文件             │
└─────────────────────────────────┘
   ↓
返回结果
```

---

## 实现细节

### 1. 全局 Fetch 拦截

**关键代码**:

```typescript
// src/util/fetch-interceptor.ts
export namespace FetchInterceptor {
  let originalFetch: typeof fetch
  let _isInstalled = false

  export function install() {
    if (_isInstalled || !HTTPLog.isEnabled()) {
      return
    }

    // 保存原始 fetch
    originalFetch = globalThis.fetch

    // 替换全局 fetch
    globalThis.fetch = async (input, init) => {
      // 拦截逻辑
      const isAIRequest = checkIfAIRequest(url)

      if (!isAIRequest) {
        return originalFetch(input, init)
      }

      // 记录请求
      HTTPLog.logRequest(...)

      // 调用原始 fetch
      const response = await originalFetch(input, init)

      // 记录响应
      HTTPLog.logResponse(...)

      return response
    }

    _isInstalled = true
  }
}
```

**优点**:

- ✅ 零侵入,无需修改现有代码
- ✅ 自动拦截所有 fetch 调用
- ✅ 可以随时安装/卸载

**缺点**:

- ⚠️ 全局替换,可能影响其他代码
- ⚠️ 需要在模块加载时安装

### 2. 敏感信息脱敏

**关键代码**:

```typescript
// src/util/http-log.ts
function sanitizeHeaders(headers) {
  const sanitized = {}
  const sensitiveKeys = ["authorization", "api-key", "x-api-key", "cookie", "x-opencode-session"]

  for (const [key, value] of Object.entries(headers)) {
    const lowerKey = key.toLowerCase()
    if (sensitiveKeys.some((k) => lowerKey.includes(k))) {
      // 只显示前几个字符
      sanitized[key] = value.substring(0, 10) + "***"
    } else {
      sanitized[key] = value
    }
  }

  return sanitized
}
```

**脱敏规则**:

- `authorization: Bearer sk-1234567890abcdef...` → `Bearer sk-***`
- `api-key: sk-1234567890abcdef...` → `sk-***`
- `cookie: session=abc123...` → `session=ab***`

### 3. Tracker 机制

**关键代码**:

```typescript
// src/util/telemetry-log.ts
export class Tracker<TStart, TEnd> {
  private startTime: number
  private startEvent: TStart
  private onStart: (event: TStart) => void
  private onEnd: (event: TEnd) => void

  constructor(startEvent, onStart, onEnd) {
    this.startTime = Date.now()
    this.startEvent = startEvent
    this.onStart = onStart
    this.onEnd = onEnd

    // 记录开始事件
    this.onStart(startEvent)
  }

  end(result) {
    const duration = Date.now() - this.startTime

    // 记录结束事件
    this.onEnd({
      ...result,
      duration,
      timestamp: Date.now(),
    } as TEnd)

    return duration
  }
}
```

**使用示例**:

```typescript
const tracker = new Tracker(
  { sessionID, toolName, input }, // 开始事件
  toolCallStart, // 开始回调
  toolCallEnd, // 结束回调
)

// ... 执行操作 ...

tracker.end({ success: true, output })
```

### 4. 日志文件写入

**关键代码**:

```typescript
// src/util/log.ts
export namespace Log {
  let write = (msg: any) => {
    process.stderr.write(msg)
    return msg.length
  }

  export async function init(options) {
    const logpath = path.join(Global.Path.log, new Date().toISOString().split(".")[0].replace(/:/g, "") + ".log")

    const logfile = Bun.file(logpath)
    const writer = logfile.writer()

    write = async (msg: any) => {
      const num = writer.write(msg)
      writer.flush()
      return num
    }
  }
}
```

**日志轮转**:

- 每次启动创建新日志文件
- 文件名: `YYYY-MM-DDTHHMMSS.log`
- 自动保留最近 10 个文件
- 旧文件自动删除

---

## 总结

### HTTP 日志系统

**核心原理**: 全局 fetch 拦截

- 在模块加载时替换 `globalThis.fetch`
- 拦截所有 AI Provider 的 HTTP 请求
- 记录请求/响应详情
- 自动脱敏敏感信息

**优势**:

- ✅ 零侵入,自动工作
- ✅ 完整的请求/响应信息
- ✅ 安全的敏感信息处理

### 遥测日志系统

**核心原理**: 包装器 + Tracker

- 使用包装器拦截工具/LLM 调用
- 使用 Tracker 自动计算耗时
- 记录结构化的业务指标

**优势**:

- ✅ 详细的业务指标
- ✅ 自动计算耗时
- ✅ 支持统计分析

### 协同工作

两个系统可以同时启用,提供完整的可观测性:

- **HTTP 日志**: 网络层面的详细信息
- **遥测日志**: 业务层面的统计指标

完美配合,全面监控! 🎉
