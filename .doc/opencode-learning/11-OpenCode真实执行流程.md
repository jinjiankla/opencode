# OpenCode 真实执行流程详解

## 🎯 从用户输入到工具调用的完整流程

让我带你深入 OpenCode 源码，看看一个 prompt 是如何找到并调用 tools 和 MCP 的。

---

## 📊 完整流程图

```
用户输入 Prompt
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. OpenCode CLI 启动                                     │
│    packages/opencode/src/cli/cmd/tui/index.tsx          │
│                                                          │
│    - 初始化会话                                          │
│    - 加载配置                                            │
│    - 准备工具列表                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 工具注册表初始化                                      │
│    packages/opencode/src/tool/registry.ts                │
│                                                          │
│    async function all(): Promise<Tool.Info[]> {          │
│      return [                                            │
│        InvalidTool,                                      │
│        QuestionTool,                                     │
│        BashTool,                                         │
│        ReadTool,                                         │
│        EditTool,                                         │
│        ...                                               │
│        ...custom,  // ← 自定义工具                       │
│      ]                                                   │
│    }                                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─────────────────────────────────────┐
                     │                                     │
                     ▼                                     ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ 3a. 加载本地工具                  │  │ 3b. 加载 MCP 工具                 │
│     registry.ts Line 35-62        │  │     mcp/index.ts Line 570-603     │
│                                   │  │                                   │
│ const glob = new Bun.Glob(        │  │ export async function tools() {   │
│   "{tool,tools}/*.{js,ts}"        │  │   const clients = await clients() │
│ )                                 │  │                                   │
│                                   │  │   for (const [name, client]       │
│ for (const dir of                 │  │        of Object.entries(clients))│
│      await Config.directories())  │  │   {                               │
│ {                                 │  │     const toolsResult =           │
│   for await (const match          │  │       await client.listTools()    │
│            of glob.scan(...)) {   │  │                                   │
│     const mod = await import(     │  │     for (const mcpTool            │
│       match                       │  │          of toolsResult.tools) {  │
│     )                             │  │       result[name + "_" +         │
│     custom.push(                  │  │         mcpTool.name] =           │
│       fromPlugin(id, def)         │  │         await convertMcpTool(     │
│     )                             │  │           mcpTool, client         │
│   }                               │  │         )                         │
│ }                                 │  │     }                             │
│                                   │  │   }                               │
│                                   │  │ }                                 │
└──────────────────┬────────────────┘  └──────────────────┬────────────────┘
                   │                                      │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 合并所有工具                                          │
│    registry.ts Line 128-165                              │
│                                                          │
│    export async function tools(model, agent) {           │
│      const tools = await all()  // ← 包含本地 + MCP      │
│      const result = await Promise.all(                   │
│        tools.map(async (t) => ({                         │
│          id: t.id,                                       │
│          ...(await t.init({ agent }))                    │
│        }))                                               │
│      )                                                   │
│      return result                                       │
│    }                                                     │
│                                                          │
│    返回格式:                                             │
│    [                                                     │
│      { id: "bash", description: "...", ... },           │
│      { id: "read", description: "...", ... },           │
│      { id: "pageindex-code_index_code", ... },  ← MCP   │
│      { id: "pageindex-code_query_code", ... },  ← MCP   │
│    ]                                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. 构建 Prompt（包含工具列表）                           │
│    session/prompt.ts Line 728                            │
│                                                          │
│    // 添加 MCP 工具到 prompt                             │
│    for (const [key, item]                                │
│         of Object.entries(await MCP.tools())) {          │
│      tools.push({                                        │
│        name: key,                                        │
│        description: item.description,                    │
│        input_schema: item.parameters                     │
│      })                                                  │
│    }                                                     │
│                                                          │
│    发送给大模型的 Prompt:                                │
│    """                                                   │
│    You have access to the following tools:               │
│                                                          │
│    1. bash: Execute shell commands                       │
│    2. read: Read file contents                           │
│    3. pageindex-code_index_code: 索引代码目录            │
│       Parameters:                                        │
│         - code_dir (string): 代码目录路径                │
│         - extensions (array): 文件扩展名                 │
│    4. pageindex-code_query_code: 查询代码                │
│       Parameters:                                        │
│         - query (string): 查询内容                       │
│    ...                                                   │
│                                                          │
│    User: 索引我的代码 ~/myproject                        │
│    """                                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. 大模型分析并选择工具                                  │
│                                                          │
│    大模型看到工具列表后，分析用户意图：                  │
│                                                          │
│    用户说: "索引我的代码 ~/myproject"                    │
│                                                          │
│    分析:                                                 │
│    - 关键词: "索引"、"代码"                              │
│    - 匹配工具: pageindex-code_index_code                 │
│    - 描述: "索引代码目录，支持 Java, Kotlin, Python"     │
│                                                          │
│    生成工具调用:                                         │
│    {                                                     │
│      "tool": "pageindex-code_index_code",               │
│      "arguments": {                                      │
│        "code_dir": "~/myproject",                        │
│        "extensions": [".java", ".kt"]                    │
│      }                                                   │
│    }                                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 7. OpenCode 路由工具调用                                 │
│    session/process.ts (工具调用处理)                     │
│                                                          │
│    if (toolName.includes("_")) {                         │
│      // 这是 MCP 工具                                    │
│      const [mcpName, ...rest] = toolName.split("_")     │
│      const actualToolName = rest.join("_")               │
│                                                          │
│      // 调用 MCP                                         │
│      await MCP.callTool(                                 │
│        mcpName,                                          │
│        actualToolName,                                   │
│        arguments                                         │
│      )                                                   │
│    } else {                                              │
│      // 这是本地工具                                     │
│      const tool = await ToolRegistry.get(toolName)       │
│      await tool.execute(arguments)                       │
│    }                                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 8. MCP 工具执行                                          │
│    mcp/index.ts Line 120-154                             │
│                                                          │
│    async function convertMcpTool(                        │
│      mcpTool,                                            │
│      client,                                             │
│      timeout                                             │
│    ) {                                                   │
│      return {                                            │
│        description: mcpTool.description,                 │
│        parameters: mcpTool.inputSchema,                  │
│        execute: async (args) => {                        │
│          // 调用 MCP 服务器                              │
│          const result = await client.callTool(           │
│            {                                             │
│              name: mcpTool.name,                         │
│              arguments: args                             │
│            },                                            │
│            { timeout }                                   │
│          )                                               │
│          return result.content                           │
│        }                                                 │
│      }                                                   │
│    }                                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 9. MCP 服务器处理                                        │
│    你的 mcp_server_enhanced.py                           │
│                                                          │
│    # MCP 服务器收到请求                                  │
│    {                                                     │
│      "method": "tools/call",                             │
│      "params": {                                         │
│        "name": "index_code",                             │
│        "arguments": {                                    │
│          "code_dir": "~/myproject",                      │
│          "extensions": [".java", ".kt"]                  │
│        }                                                 │
│      }                                                   │
│    }                                                     │
│                                                          │
│    # 路由到正确的函数                                    │
│    @app.call_tool()                                      │
│    async def call_tool(name, arguments):                 │
│      if name == "index_code":                            │
│        return await index_code(arguments)                │
│                                                          │
│    # 执行索引逻辑                                        │
│    async def index_code(args):                           │
│      # 1. 转换代码为 Markdown                            │
│      # 2. 索引 Markdown                                  │
│      # 3. 返回结果                                       │
│      return "✅ 索引完成！"                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 10. 结果返回链路                                         │
│                                                          │
│     MCP 服务器 → MCP 客户端 → OpenCode → 大模型 → 用户   │
│                                                          │
│     10.1 MCP 服务器返回 (JSON-RPC 响应):                │
│     {                                                    │
│       "jsonrpc": "2.0",                                  │
│       "id": 2,                                           │
│       "result": {                                        │
│         "content": [{                                    │
│           "type": "text",                                │
│           "text": "✅ 代码索引完成！\n成功 45 个文件"    │
│         }]                                               │
│       }                                                  │
│     }                                                    │
│                                                          │
│     10.2 MCP 客户端接收并返回给 OpenCode:                │
│     result.content  // ← 提取内容                       │
│                                                          │
│     10.3 OpenCode 将结果添加到对话历史:                  │
│     {                                                    │
│       "role": "tool",                                    │
│       "tool_call_id": "call_123",                        │
│       "content": "✅ 代码索引完成！\n成功 45 个文件"      │
│     }                                                    │
│                                                          │
│     10.4 OpenCode 再次调用大模型（包含工具结果）:        │
│     [                                                    │
│       { role: "user", content: "索引我的代码" },         │
│       { role: "assistant", tool_calls: [...] },         │
│       { role: "tool", content: "✅ 索引完成！..." }  ← 新 │
│     ]                                                    │
│                                                          │
│     10.5 大模型分析工具结果，生成最终回复:                │
│     "我已经成功索引了你的代码库！\n\n"                    │
│     "📊 索引结果:\n"                                      │
│     "- 代码目录: ~/myproject\n"                          │
│     "- 文件类型: .java, .kt\n"                           │
│     "- 索引成功: 45 个文件\n\n"                           │
│     "现在你可以使用 query_code 工具来查询代码了。"       │
│                                                          │
│     10.6 用户看到最终回复 ✅                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 关键代码详解

### 1. 工具注册表初始化 (registry.ts)

```typescript
// packages/opencode/src/tool/registry.ts

export namespace ToolRegistry {
  // Line 35-62: 加载自定义工具
  export const state = Instance.state(async () => {
    const custom = [] as Tool.Info[]
    const glob = new Bun.Glob("{tool,tools}/*.{js,ts}")

    // 扫描配置目录中的工具文件
    for (const dir of await Config.directories()) {
      for await (const match of glob.scan({ cwd: dir, ... })) {
        const mod = await import(match)
        for (const [id, def] of Object.entries<ToolDefinition>(mod)) {
          custom.push(fromPlugin(id, def))
        }
      }
    }

    // 加载插件中的工具
    const plugins = await Plugin.list()
    for (const plugin of plugins) {
      for (const [id, def] of Object.entries(plugin.tool ?? {})) {
        custom.push(fromPlugin(id, def))
      }
    }

    return { custom }
  })

  // Line 96-122: 获取所有工具（内置 + 自定义）
  async function all(): Promise<Tool.Info[]> {
    const custom = await state().then((x) => x.custom)

    return [
      InvalidTool,
      QuestionTool,
      BashTool,
      ReadTool,
      GlobTool,
      GrepTool,
      EditTool,
      WriteTool,
      // ... 更多内置工具
      ...custom,  // ← 自定义工具在这里
    ]
  }

  // Line 128-165: 准备工具列表（发送给大模型）
  export async function tools(model, agent) {
    const tools = await all()  // ← 获取所有工具

    const result = await Promise.all(
      tools
        .filter((t) => {
          // 根据模型过滤工具
          if (t.id === "codesearch" || t.id === "websearch") {
            return model.providerID === "opencode" || Flag.OPENCODE_ENABLE_EXA
          }
          return true
        })
        .map(async (t) => {
          // 初始化每个工具
          return {
            id: t.id,
            ...(await t.init({ agent }))
          }
        })
    )

    return result
  }
}
```

---

### 2. MCP 工具加载 (mcp/index.ts)

```typescript
// packages/opencode/src/mcp/index.ts

export namespace MCP {
  // Line 570-603: 获取所有 MCP 工具
  export async function tools() {
    const result: Record<string, Tool> = {}
    const config = cfg.mcp ?? {}
    const clientsSnapshot = await clients() // ← 所有 MCP 客户端

    for (const [clientName, client] of Object.entries(clientsSnapshot)) {
      // 只包含已连接的 MCP
      if (s.status[clientName]?.status !== "connected") {
        continue
      }

      // 获取 MCP 服务器的工具列表
      const toolsResult = await client.listTools().catch((e) => {
        log.error("failed to get tools", { clientName, error: e.message })
        return undefined
      })

      if (!toolsResult) continue

      // 转换每个 MCP 工具
      for (const mcpTool of toolsResult.tools) {
        const sanitizedClientName = clientName.replace(/[^a-zA-Z0-9_-]/g, "_")
        const sanitizedToolName = mcpTool.name.replace(/[^a-zA-Z0-9_-]/g, "_")

        // 工具名格式: "mcp名_工具名"
        result[sanitizedClientName + "_" + sanitizedToolName] = await convertMcpTool(mcpTool, client, timeout)
      }
    }

    return result
  }

  // Line 120-154: 转换 MCP 工具为 OpenCode 工具
  async function convertMcpTool(mcpTool: MCPToolDef, client: MCPClient, timeout?: number): Promise<Tool> {
    return {
      description: mcpTool.description ?? "",
      parameters: mcpTool.inputSchema,
      execute: async (args) => {
        // 调用 MCP 服务器
        const result = await client.callTool(
          {
            name: mcpTool.name,
            arguments: args,
          },
          { timeout },
        )

        // 返回结果
        return result.content
      },
    }
  }
}
```

---

### 3. Prompt 构建 (session/prompt.ts)

```typescript
// packages/opencode/src/session/prompt.ts

// Line 728: 添加 MCP 工具到 prompt
for (const [key, item] of Object.entries(await MCP.tools())) {
  tools.push({
    name: key,  // ← "pageindex-code_index_code"
    description: item.description,
    input_schema: item.parameters
  })
}

// 最终发送给大模型的 tools 列表:
[
  {
    name: "bash",
    description: "Execute shell commands",
    input_schema: { ... }
  },
  {
    name: "read",
    description: "Read file contents",
    input_schema: { ... }
  },
  {
    name: "pageindex-code_index_code",  // ← MCP 工具
    description: "索引代码目录，支持 Java, Kotlin, Python",
    input_schema: {
      type: "object",
      properties: {
        code_dir: { type: "string", description: "代码目录路径" },
        extensions: { type: "array", ... }
      }
    }
  },
  {
    name: "pageindex-code_query_code",  // ← MCP 工具
    description: "查询代码库中的函数、类等",
    input_schema: { ... }
  }
]
```

---

## 💡 关键发现

### 1. 工具命名规则

**本地工具**：

```
bash
read
edit
write
```

**MCP 工具**：

```
{mcp_name}_{tool_name}

例如:
pageindex-code_index_code
pageindex-code_query_code
```

### 2. 工具发现流程

```
启动时:
├── 加载内置工具 (BashTool, ReadTool, ...)
├── 扫描 ~/.opencode/tools/*.ts
├── 加载插件工具
└── 连接 MCP 服务器
    └── 调用 client.listTools()
        └── 获取 MCP 工具列表
```

### 3. 工具调用流程

```
大模型返回:
{
  "tool": "pageindex-code_index_code",
  "arguments": { "code_dir": "~/myproject" }
}

OpenCode 解析:
├── 检查工具名是否包含 "_"
├── 如果包含: 这是 MCP 工具
│   ├── 分割: ["pageindex-code", "index_code"]
│   ├── MCP 名: "pageindex-code"
│   └── 工具名: "index_code"
│
└── 调用 MCP:
    MCP.callTool("pageindex-code", "index_code", arguments)
```

---

## 🎯 实际示例

### 用户输入

```
"索引我的 Android 项目 ~/MyApp/app/src/main"
```

### OpenCode 内部流程

**Step 1: 构建 Prompt**

```
System: You have access to the following tools:

1. bash: Execute shell commands
2. read: Read file contents
3. pageindex-code_index_code: 索引代码目录，支持 Java, Kotlin, Python
   Parameters:
     - code_dir (string): 代码目录路径
     - extensions (array): 文件扩展名列表
4. pageindex-code_query_code: 查询代码库中的函数、类等
   Parameters:
     - query (string): 查询内容

User: 索引我的 Android 项目 ~/MyApp/app/src/main
```

**Step 2: 大模型分析**

```
分析:
- 用户想要: 索引代码
- 关键词: "索引"、"Android 项目"
- 匹配工具: pageindex-code_index_code
- 推断: Android 项目使用 Java/Kotlin

生成调用:
{
  "tool": "pageindex-code_index_code",
  "arguments": {
    "code_dir": "~/MyApp/app/src/main",
    "extensions": [".java", ".kt"]
  }
}
```

**Step 3: OpenCode 路由**

```typescript
const toolName = "pageindex-code_index_code"
const [mcpName, ...rest] = toolName.split("_")
// mcpName = "pageindex-code"
// rest = ["index", "code"]
const actualToolName = rest.join("_")
// actualToolName = "index_code"

await MCP.callTool(mcpName, actualToolName, arguments)
```

**Step 4: MCP 客户端调用**

```typescript
const client = clients["pageindex-code"]
const result = await client.callTool({
  name: "index_code",
  arguments: {
    code_dir: "~/MyApp/app/src/main",
    extensions: [".java", ".kt"],
  },
})
```

**Step 5: MCP 服务器处理**

```python
# mcp_server_enhanced.py

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "index_code":
        return await index_code(arguments)

async def index_code(args):
    code_dir = args["code_dir"]
    extensions = args.get("extensions", [".java", ".kt"])

    # 1. 转换代码
    subprocess.run(["python3", "code_to_markdown.py", ...])

    # 2. 索引 Markdown
    for md_file in md_files:
        subprocess.run(["python3", "run_pageindex.py", ...])

    # 3. 返回结果
    return "✅ 索引完成！成功 45 个文件"
```

**Step 6: 结果返回**

```
MCP 服务器 → MCP 客户端 → OpenCode → 大模型 → 用户

用户看到:
✅ 代码索引完成！
**代码目录**: ~/MyApp/app/src/main
**文件类型**: .java, .kt
**索引成功**: 45 个文件
```

---

## ✅ 总结

### 工具发现机制

1. **启动时加载**：
   - 内置工具（BashTool, ReadTool, ...）
   - 自定义工具（~/.opencode/tools/\*.ts）
   - MCP 工具（连接 MCP 服务器，调用 listTools()）

2. **合并工具列表**：
   - 本地工具: `bash`, `read`, `edit`
   - MCP 工具: `{mcp_name}_{tool_name}`

3. **发送给大模型**：
   - 包含所有工具的描述和参数
   - 大模型根据描述选择合适的工具

### 工具调用机制

1. **大模型选择工具**：
   - 分析用户意图
   - 匹配工具描述
   - 生成工具调用

2. **OpenCode 路由**：
   - 检查工具名
   - 如果包含 `_`：调用 MCP
   - 否则：调用本地工具

3. **执行并返回**：
   - MCP 服务器执行逻辑
   - 返回结果给 OpenCode
   - OpenCode 返回给大模型
   - 大模型返回给用户

---

## 🔄 工具结果返回流程详解

### 完整的返回链路

你的问题非常关键！**工具结果必须返回给 OpenCode，然后再由大模型处理**。

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: MCP 服务器返回结果                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JSON-RPC 响应
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: MCP 客户端接收                                   │
│                                                          │
│ const result = await client.callTool(...)               │
│ // result.content = [{                                  │
│ //   type: "text",                                      │
│ //   text: "✅ 索引完成！成功 45 个文件"                 │
│ // }]                                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 返回 result.content
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: OpenCode 接收工具结果                            │
│                                                          │
│ // 将工具结果添加到对话历史                              │
│ const toolResult = {                                     │
│   role: "tool",                                          │
│   tool_call_id: "call_abc123",                           │
│   content: "✅ 索引完成！成功 45 个文件"                  │
│ }                                                        │
│                                                          │
│ messages.push(toolResult)                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 更新后的对话历史
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: OpenCode 再次调用大模型                          │
│                                                          │
│ const messages = [                                       │
│   {                                                      │
│     role: "user",                                        │
│     content: "索引我的代码 ~/myproject"                  │
│   },                                                     │
│   {                                                      │
│     role: "assistant",                                   │
│     content: null,                                       │
│     tool_calls: [{                                       │
│       id: "call_abc123",                                 │
│       type: "function",                                  │
│       function: {                                        │
│         name: "pageindex-code_index_code",              │
│         arguments: '{"code_dir": "~/myproject"}'        │
│       }                                                  │
│     }]                                                   │
│   },                                                     │
│   {                                                      │
│     role: "tool",  // ← 工具结果                        │
│     tool_call_id: "call_abc123",                         │
│     content: "✅ 索引完成！成功 45 个文件"                │
│   }                                                      │
│ ]                                                        │
│                                                          │
│ // 再次调用大模型                                        │
│ const response = await ai.chat(messages)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 大模型分析工具结果
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: 大模型生成最终回复                               │
│                                                          │
│ 大模型看到:                                              │
│ - 用户请求: "索引我的代码 ~/myproject"                   │
│ - 工具调用: pageindex-code_index_code                    │
│ - 工具结果: "✅ 索引完成！成功 45 个文件"                 │
│                                                          │
│ 大模型生成:                                              │
│ "我已经成功索引了你的代码库！\n\n"                        │
│ "📊 索引结果:\n"                                          │
│ "- 代码目录: ~/myproject\n"                              │
│ "- 文件类型: .java, .kt\n"                               │
│ "- 索引成功: 45 个文件\n\n"                               │
│ "现在你可以查询代码了，比如：\n"                          │
│ "- '查询用户认证相关的代码'\n"                            │
│ "- '找到所有的 ViewModel 类'"                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 最终回复
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 6: 用户看到友好的回复                               │
│                                                          │
│ 我已经成功索引了你的代码库！                             │
│                                                          │
│ 📊 索引结果:                                             │
│ - 代码目录: ~/myproject                                  │
│ - 文件类型: .java, .kt                                   │
│ - 索引成功: 45 个文件                                    │
│                                                          │
│ 现在你可以查询代码了，比如：                             │
│ - "查询用户认证相关的代码"                               │
│ - "找到所有的 ViewModel 类"                              │
└─────────────────────────────────────────────────────────┘
```

---

### 关键点说明

#### 1. 工具结果必须返回给 OpenCode

```typescript
// mcp/index.ts Line 189-198
execute: async (args) => {
  const result = await client.callTool({ name: mcpTool.name, arguments: args }, { timeout })

  // ← 这里返回结果给 OpenCode
  return result.content
}
```

#### 2. OpenCode 将结果添加到对话历史

```typescript
// session/process.ts (简化版)
const toolResult = await executeTool(toolName, arguments)

// 添加到消息历史
messages.push({
  role: "tool",
  tool_call_id: toolCallId,
  content: toolResult, // ← 工具返回的内容
})
```

#### 3. OpenCode 再次调用大模型

```typescript
// 对话历史现在包含:
// 1. 用户消息
// 2. 助手的工具调用
// 3. 工具结果 ← 新增

const finalResponse = await ai.chat(messages)
```

#### 4. 大模型分析工具结果并回复

大模型看到工具结果后，会：

- ✅ 理解工具执行的结果
- ✅ 提取关键信息
- ✅ 生成友好的回复
- ✅ 可能建议下一步操作

---

### 实际对话示例

#### 示例 1: 索引代码

```
用户: 索引我的 Android 项目 ~/MyApp/app/src/main

[OpenCode 内部]
→ 调用工具: pageindex-code_index_code
→ 工具返回: "✅ 索引完成！成功 127 个文件"
→ 再次调用大模型（包含工具结果）

大模型回复:
我已经成功索引了你的 Android 项目！

📊 索引结果:
- 代码目录: ~/MyApp/app/src/main
- 文件类型: .java, .kt
- 索引成功: 127 个文件

现在你可以：
1. 查询代码: "查询用户认证相关的代码"
2. 查看架构: "这个项目的架构是怎样的？"
3. 查找类: "找到所有的 ViewModel"
```

#### 示例 2: 查询代码

```
用户: 查询用户认证相关的代码

[OpenCode 内部]
→ 调用工具: pageindex-code_query_code
→ 工具返回:
  "🔍 找到 8 个相关结果:
   1. Class: UserAuthManager (auth/UserAuthManager.kt:15)
   2. Method: authenticateUser (auth/AuthUtils.kt:45)
   ..."
→ 再次调用大模型（包含工具结果）

大模型回复:
我在你的代码库中找到了 8 个与用户认证相关的组件：

🔐 核心认证组件:

1. **UserAuthManager** (auth/UserAuthManager.kt)
   - 用户认证管理器
   - 位置: 第 15 行

2. **authenticateUser** (auth/AuthUtils.kt)
   - 验证用户凭证的方法
   - 位置: 第 45 行

3. **LoginActivity** (ui/LoginActivity.java)
   - 用户登录界面
   - 位置: 第 28 行

主要的认证流程是:
LoginActivity → LoginViewModel → UserAuthManager → AuthUtils

需要我详细解释某个组件吗？
```

---

### 为什么需要这个返回流程？

#### 1. 大模型需要知道工具执行结果

```
❌ 没有返回流程:
用户: "索引我的代码"
OpenCode: [调用工具]
大模型: "我不知道工具执行得怎么样..."

✅ 有返回流程:
用户: "索引我的代码"
OpenCode: [调用工具] → 返回结果
大模型: "我看到索引成功了 45 个文件，现在你可以..."
```

#### 2. 大模型可以基于结果提供建议

```
工具返回: "索引失败: 目录不存在"

大模型回复:
"抱歉，索引失败了。原因是目录不存在。

请检查:
1. 路径是否正确？
2. 是否有权限访问该目录？
3. 目录是否已被删除？

你可以尝试:
- 使用 `bash` 工具查看目录: ls ~/myproject
- 或者提供正确的路径"
```

#### 3. 大模型可以链式调用工具

```
用户: "分析我的代码库并找出所有的 bug"

大模型:
1. 先调用 index_code 索引代码
2. 看到索引成功
3. 再调用 query_code 查询可能的问题
4. 分析结果并给出建议
```

---

### 源码验证

让我们看看 OpenCode 源码中的实际实现：

```typescript
// packages/opencode/src/session/process.ts (简化版)

async function processToolCall(toolCall) {
  // 1. 执行工具
  const toolResult = await executeTool(toolCall.function.name, JSON.parse(toolCall.function.arguments))

  // 2. 添加工具结果到消息历史
  messages.push({
    role: "tool",
    tool_call_id: toolCall.id,
    content: toolResult, // ← 工具返回的内容
  })

  // 3. 再次调用大模型（包含工具结果）
  const response = await ai.chat({
    messages: messages, // ← 包含工具结果
    tools: availableTools,
  })

  // 4. 返回大模型的最终回复
  return response
}
```

---

## ✅ 总结

### 完整的调用链路

```
用户输入
  ↓
OpenCode 构建 Prompt（包含工具列表）
  ↓
大模型选择工具并生成调用
  ↓
OpenCode 执行工具（本地或 MCP）
  ↓
工具返回结果
  ↓
OpenCode 将结果添加到对话历史
  ↓
OpenCode 再次调用大模型（包含工具结果）← 关键！
  ↓
大模型分析工具结果并生成友好回复
  ↓
用户看到最终回复
```

### 关键点

1. ✅ **工具结果必须返回给 OpenCode**
2. ✅ **OpenCode 将结果添加到对话历史**
3. ✅ **OpenCode 再次调用大模型**（包含工具结果）
4. ✅ **大模型分析结果并生成友好回复**
5. ✅ **用户看到的是大模型的回复，不是工具的原始输出**

### 对比

| 步骤       | 工具原始输出                    | 大模型处理后                                                                                                                |
| ---------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **内容**   | `"✅ 索引完成！成功 45 个文件"` | `"我已经成功索引了你的代码库！\n\n📊 索引结果:\n- 代码目录: ~/myproject\n- 索引成功: 45 个文件\n\n现在你可以查询代码了..."` |
| **可读性** | ⭐⭐⭐                          | ⭐⭐⭐⭐⭐                                                                                                                  |
| **建议**   | ❌ 无                           | ✅ 提供下一步建议                                                                                                           |
| **上下文** | ❌ 无                           | ✅ 理解用户意图                                                                                                             |

这就是为什么工具结果必须返回给 OpenCode 和大模型！🎯
