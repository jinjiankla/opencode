# OpenCode HTTP 请求日志使用指南

## 概述

HTTP 请求日志功能可以打印所有 LLM 调用的 HTTP 请求和响应详情,包括:

- 🌐 **请求 URL 和方法**
- 📋 **请求和响应 Headers**
- 📦 **请求和响应 Body**
- ⏱️ **请求耗时**
- ✅ **响应状态码**
- 🔒 **敏感信息自动脱敏**

## 快速开始

### ✅ 已自动集成!

HTTP 日志功能已经自动集成到 OpenCode 中,**无需任何手动配置**!

只需要设置环境变量即可启用:

### 1. 启用 HTTP 日志

```bash
# 方法 1: 只启用 HTTP 日志
export OPENCODE_HTTP_LOG=1
opencode

# 方法 2: 启用调试模式(包含 HTTP 日志)
export OPENCODE_DEBUG=1
opencode

# 方法 3: 启用详细模式(显示完整的请求/响应)
export OPENCODE_HTTP_VERBOSE=1
export OPENCODE_HTTP_LOG=1
opencode
```

**就这么简单!** 所有的 LLM HTTP 请求都会自动被拦截和记录。

### 2. 查看日志

HTTP 日志会同时输出到:

- **终端 stderr**: 实时彩色输出
- **日志文件**: `~/.local/share/opencode/log/`

```bash
# 实时查看终端输出(已自动显示)
# 或者查看日志文件
tail -f ~/.local/share/opencode/log/$(ls -t ~/.local/share/opencode/log/ | head -1)
```

## 日志格式

### HTTP 请求日志

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 HTTP REQUEST [2026-01-25T09:00:00.000Z]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provider: openai
Model: gpt-4
Method: POST
URL: https://api.openai.com/v1/chat/completions

Headers:
  content-type: application/json
  authorization: Bearer sk-***
  user-agent: opencode/1.1.35

Body:
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant..."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 0.7,
  "stream": true
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### HTTP 响应日志

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HTTP RESPONSE [2026-01-25T09:00:02.345Z]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provider: openai
Model: gpt-4
Status: 200 OK
Duration: 2345ms

Headers:
  content-type: application/json
  x-request-id: req_abc123

Body:
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1706169600,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 10,
    "total_tokens": 25
  }
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### HTTP 错误日志

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ HTTP ERROR [2026-01-25T09:00:00.500Z]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provider: openai
Model: gpt-4
Duration: 500ms
Error: Request failed with status code 429

Stack:
  at fetch (...)
  ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 敏感信息脱敏

HTTP 日志会自动脱敏以下敏感信息:

### 1. Headers 脱敏

以下 headers 会被自动脱敏:

- `authorization`
- `api-key`
- `x-api-key`
- `cookie`
- `x-opencode-session`

**示例:**

```
原始: authorization: Bearer sk-1234567890abcdef...
脱敏: authorization: Bearer sk-***
```

### 2. Body 脱敏

**消息截断** (非详细模式):

- 保留前 2 条消息
- 保留后 2 条消息
- 中间消息用省略标记替代

**示例:**

```json
{
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "..." },
    { "role": "system", "content": "... (8 messages omitted) ..." },
    { "role": "assistant", "content": "..." },
    { "role": "user", "content": "..." }
  ]
}
```

## 详细模式

启用详细模式可以查看完整的请求和响应:

```bash
export OPENCODE_HTTP_VERBOSE=1
export OPENCODE_HTTP_LOG=1
opencode
```

详细模式会:

- ✅ 显示完整的消息历史(不截断)
- ✅ 显示完整的 JSON 输出(不截断)
- ✅ 显示流式响应的每个 chunk
- ✅ 显示完整的错误堆栈

## 日志文件

HTTP 日志同时写入到日志文件:

```
~/.local/share/opencode/log/YYYY-MM-DDTHHMMSS.log
```

**日志文件格式:**

```
INFO  2026-01-25T09:00:00 +150ms service=http provider=openai model=gpt-4 http_request method=POST url=https://api.openai.com/v1/chat/completions
INFO  2026-01-25T09:00:02 +2345ms service=http provider=openai model=gpt-4 http_response status=200 duration=2345
```

## 过滤和分析

### 查看特定 Provider 的请求

```bash
# 查看 OpenAI 的请求
tail -f ~/.local/share/opencode/log/*.log | grep "provider=openai"

# 查看 Anthropic 的请求
tail -f ~/.local/share/opencode/log/*.log | grep "provider=anthropic"
```

### 查看失败的请求

```bash
# 查看 HTTP 错误
tail -f ~/.local/share/opencode/log/*.log | grep "http_error"

# 查看非 200 状态码
tail -f ~/.local/share/opencode/log/*.log | grep "http_response" | grep -v "status=200"
```

### 统计请求耗时

```bash
# 提取所有请求耗时
grep "http_response" ~/.local/share/opencode/log/*.log | \
  grep -o 'duration=[0-9]*' | \
  cut -d= -f2 | \
  awk '{sum+=$1; count++} END {print "平均耗时:", sum/count, "ms"}'
```

## 集成到代码

### 使用 fetch 拦截器

```typescript
import { HTTPLog } from "@/util/http-log"

// 创建拦截器
const interceptedFetch = HTTPLog.createFetchInterceptor(
  "openai",
  "gpt-4"
)

// 使用拦截器
const response = await interceptedFetch(
  "https://api.openai.com/v1/chat/completions",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "gpt-4",
      messages: [...],
    }),
  }
)
```

### 手动记录请求

```typescript
import { HTTPLog } from "@/util/http-log"

// 记录请求
HTTPLog.logRequest(
  "openai",
  "gpt-4",
  "https://api.openai.com/v1/chat/completions",
  "POST",
  {
    "content-type": "application/json",
    "authorization": "Bearer sk-...",
  },
  {
    model: "gpt-4",
    messages: [...],
  }
)

// 记录响应
HTTPLog.logResponse(
  "openai",
  "gpt-4",
  200,
  "OK",
  {
    "content-type": "application/json",
  },
  {
    id: "chatcmpl-...",
    choices: [...],
  },
  2345
)

// 记录错误
HTTPLog.logError(
  "openai",
  "gpt-4",
  new Error("Request failed"),
  500
)
```

## 性能影响

HTTP 日志的性能影响:

- ✅ **最小开销**: 只在启用时才记录
- ✅ **异步写入**: 不阻塞主流程
- ✅ **智能截断**: 自动截断过长的内容

**性能开销**: < 0.5% (在大多数情况下可以忽略)

## 常见问题

### Q: 如何只查看请求不查看响应?

A: 使用 grep 过滤:

```bash
tail -f ~/.local/share/opencode/log/*.log | grep "http_request"
```

### Q: 日志太多,如何减少输出?

A:

1. 不启用详细模式 (不设置 `OPENCODE_HTTP_VERBOSE`)
2. 使用 grep 过滤特定内容
3. 只在需要调试时启用

### Q: 如何查看完整的 API Key?

A: HTTP 日志会自动脱敏敏感信息,这是安全特性。如果需要查看完整信息,请查看代码中的配置。

### Q: 流式响应会记录吗?

A:

- 默认模式: 只记录最终响应
- 详细模式: 记录每个 chunk

### Q: 如何导出 HTTP 日志?

A: 日志文件位于 `~/.local/share/opencode/log/`,可以直接复制:

```bash
cp ~/.local/share/opencode/log/*.log ./http-logs/
```

## 调试技巧

### 1. 对比不同 Provider 的请求格式

```bash
# 查看 OpenAI 的请求
grep "provider=openai" log.txt | grep "http_request"

# 查看 Anthropic 的请求
grep "provider=anthropic" log.txt | grep "http_request"
```

### 2. 检查 Rate Limit

```bash
# 查看 429 错误
grep "status=429" log.txt
```

### 3. 分析响应时间

```bash
# 查看慢请求 (>5秒)
grep "http_response" log.txt | \
  grep -o 'duration=[0-9]*' | \
  awk -F= '$2 > 5000 {print}'
```

### 4. 检查 Token 使用

```bash
# 从响应中提取 token 使用情况
grep "http_response" log.txt | \
  grep -o '"usage":{[^}]*}' | \
  jq .
```

## 与遥测日志的区别

| 功能         | HTTP 日志       | 遥测日志   |
| ------------ | --------------- | ---------- |
| **用途**     | 调试 HTTP 请求  | 统计和分析 |
| **详细程度** | 完整的请求/响应 | 汇总信息   |
| **输出位置** | 终端 + 日志文件 | 日志文件   |
| **性能开销** | 稍高            | 很低       |
| **适用场景** | 开发调试        | 生产监控   |

**建议:**

- 开发时: 启用 HTTP 日志
- 生产时: 只启用遥测日志

## 总结

HTTP 请求日志功能提供了:

- ✅ 完整的 HTTP 请求和响应详情
- ✅ 自动脱敏敏感信息
- ✅ 彩色终端输出,易于阅读
- ✅ 同时写入日志文件
- ✅ 支持详细模式
- ✅ 低性能开销

通过启用 HTTP 日志,你可以深入了解 OpenCode 与 AI Provider 的交互细节,快速定位和解决问题!
