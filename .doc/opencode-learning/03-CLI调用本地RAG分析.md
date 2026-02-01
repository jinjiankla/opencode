# OpenCode CLI 调用本地 RAG 能力分析

## 📋 问题概述

**问题**：OpenCode 的 CLI 可以调用本地 RAG 吗?

**简短回答**：**可以，但需要通过 MCP (Model Context Protocol) 服务器来实现**。

## 🔍 详细分析

### 1. OpenCode 的架构设计

OpenCode 本身**没有内置的 RAG 功能**，但它提供了强大的扩展机制：

- **MCP (Model Context Protocol)** - 用于扩展工具和资源
- **Tool System** - 内置工具系统
- **Plugin System** - 插件机制

### 2. MCP 支持情况

根据源码分析，OpenCode **完整支持 MCP 协议**：

#### MCP 核心功能

```typescript
// 位置: packages/opencode/src/mcp/index.ts

export namespace MCP {
  // 支持的功能：
  ;-tools() - // 获取 MCP 工具
    prompts() - // 获取 MCP 提示词
    resources() - // 获取 MCP 资源
    readResource() - // 读取资源内容
    // 支持的传输方式：
    StreamableHTTPClientTransport - // HTTP 传输
    SSEClientTransport - // SSE 传输
    StdioClientTransport // 本地进程通信
}
```

#### MCP 配置方式

OpenCode 支持两种 MCP 服务器类型：

**1. 本地 MCP 服务器 (local)**

```json
{
  "mcp": {
    "my-rag-server": {
      "type": "local",
      "command": ["bun", "run", "/path/to/rag-server.ts"],
      "environment": {
        "VECTOR_DB_PATH": "/path/to/chromadb"
      }
    }
  }
}
```

**2. 远程 MCP 服务器 (remote)**

```json
{
  "mcp": {
    "remote-rag": {
      "type": "remote",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

### 3. 实现本地 RAG 的方案

#### 方案 A: 创建本地 MCP RAG 服务器 (推荐)

**优势**：

- ✅ 完全本地化，数据隐私
- ✅ 可以使用本地 embedding 模型
- ✅ 与 OpenCode 无缝集成
- ✅ 支持自定义检索策略

**实现步骤**：

1. **创建 MCP 服务器**

```typescript
// rag-mcp-server/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { ChromaClient } from "chromadb"

const server = new Server({
  name: "local-rag-server",
  version: "1.0.0",
})

// 初始化向量数据库
const chroma = new ChromaClient({ path: process.env.VECTOR_DB_PATH })

// 注册 RAG 工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "search_codebase",
      description: "Search company codebase using semantic search",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Search query",
          },
          topK: {
            type: "number",
            description: "Number of results to return",
            default: 5,
          },
        },
        required: ["query"],
      },
    },
  ],
}))

// 实现搜索逻辑
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "search_codebase") {
    const { query, topK = 5 } = request.params.arguments

    // 使用本地 embedding 模型
    const embedding = await generateEmbedding(query)

    // 在向量数据库中搜索
    const results = await chroma.query({
      queryEmbeddings: [embedding],
      nResults: topK,
    })

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2),
        },
      ],
    }
  }
})

// 启动服务器
const transport = new StdioServerTransport()
await server.connect(transport)
```

2. **配置 OpenCode**

```json
// ~/.opencode/config.json
{
  "mcp": {
    "local-rag": {
      "type": "local",
      "command": ["bun", "run", "/path/to/rag-mcp-server/index.ts"],
      "environment": {
        "VECTOR_DB_PATH": "/path/to/chromadb",
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

3. **使用 RAG 功能**

```bash
# 启动 OpenCode
opencode

# 在对话中使用
"搜索公司代码库中关于用户认证的实现"
# OpenCode 会自动调用 local-rag_search_codebase 工具
```

#### 方案 B: 使用 MCP Resources

MCP 还支持 **Resources** 功能，可以提供静态或动态的知识库：

```typescript
// 注册资源
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "codebase://docs/architecture",
      name: "Architecture Documentation",
      description: "Company codebase architecture",
      mimeType: "text/markdown",
    },
  ],
}))

// 读取资源
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params

  if (uri === "codebase://docs/architecture") {
    const content = await loadFromVectorDB(uri)
    return {
      contents: [
        {
          uri,
          mimeType: "text/markdown",
          text: content,
        },
      ],
    }
  }
})
```

### 4. 技术栈选择

#### 本地 Embedding 模型

```typescript
// 使用 Transformers.js (纯 JavaScript)
import { pipeline } from "@xenova/transformers"

const embedder = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2")

async function generateEmbedding(text: string) {
  const output = await embedder(text, { pooling: "mean", normalize: true })
  return Array.from(output.data)
}
```

#### 向量数据库选项

1. **ChromaDB** (推荐)
   - 轻量级
   - 支持本地部署
   - Python/JavaScript SDK

2. **LanceDB**
   - 高性能
   - 嵌入式数据库
   - TypeScript 原生支持

3. **简单方案：文件 + 内存**

   ```typescript
   // 适合小规模知识库
   const embeddings = new Map<string, number[]>()

   function cosineSimilarity(a: number[], b: number[]): number {
     // 实现余弦相似度
   }
   ```

### 5. CLI 命令支持

OpenCode 提供了完整的 MCP 管理命令：

```bash
# 列出所有 MCP 服务器
opencode mcp list

# 添加 MCP 服务器
opencode mcp add

# 认证（如果需要）
opencode mcp auth <name>

# 调试 MCP 连接
opencode mcp debug <name>
```

### 6. 实际应用场景

#### 场景 1: 公司代码库知识库

```typescript
// 索引公司代码
async function indexCodebase(repoPath: string) {
  const files = await glob("**/*.{ts,js,py}", { cwd: repoPath })

  for (const file of files) {
    const content = await Bun.file(path.join(repoPath, file)).text()
    const chunks = splitIntoChunks(content, 500) // 分块

    for (const chunk of chunks) {
      const embedding = await generateEmbedding(chunk)
      await chroma.add({
        ids: [generateId()],
        embeddings: [embedding],
        documents: [chunk],
        metadatas: [
          {
            file,
            type: "code",
          },
        ],
      })
    }
  }
}
```

#### 场景 2: 文档问答

```typescript
// 索引 Markdown 文档
async function indexDocs(docsPath: string) {
  const docs = await glob("**/*.md", { cwd: docsPath })

  for (const doc of docs) {
    const content = await Bun.file(path.join(docsPath, doc)).text()
    // 按标题分块
    const sections = splitByHeadings(content)

    for (const section of sections) {
      const embedding = await generateEmbedding(section.content)
      await chroma.add({
        ids: [generateId()],
        embeddings: [embedding],
        documents: [section.content],
        metadatas: [
          {
            file: doc,
            heading: section.heading,
            type: "documentation",
          },
        ],
      })
    }
  }
}
```

## 📊 对比：不同实现方案

| 方案                    | 优势                         | 劣势                 | 适用场景       |
| ----------------------- | ---------------------------- | -------------------- | -------------- |
| **MCP + 本地向量库**    | 完全本地化、隐私安全、可定制 | 需要自己实现         | 企业内部代码库 |
| **MCP + 远程 RAG 服务** | 易于部署、可共享             | 需要网络、数据外传   | 团队协作       |
| **内置 Tool**           | 简单直接                     | 功能受限、不符合架构 | 简单关键词搜索 |
| **MCP Resources**       | 轻量级、适合静态内容         | 不支持语义搜索       | 文档查询       |

## ✅ 结论

**OpenCode CLI 完全支持调用本地 RAG**，推荐方案：

1. ✅ **使用 MCP 协议创建本地 RAG 服务器**
2. ✅ **使用本地 embedding 模型（如 Transformers.js）**
3. ✅ **使用轻量级向量数据库（如 ChromaDB）**
4. ✅ **通过 StdioClientTransport 进行本地通信**

这种方案：

- 🔒 **数据完全本地化**，不会外传
- ⚡ **性能优秀**，无网络延迟
- 🎯 **高度可定制**，可以针对公司代码库优化
- 🔌 **无缝集成**，OpenCode 原生支持

## 🚀 下一步行动

1. 参考 [之前对话](conversation://2ac8cfc7-1ce2-4718-8c63-b0327dd7f486) 中的 MCP 实现方案
2. 创建本地 RAG MCP 服务器
3. 索引公司代码库
4. 配置 OpenCode 使用本地 RAG
5. 测试和优化检索效果

## 📚 参考资源

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [OpenCode MCP 源码](packages/opencode/src/mcp/index.ts)
- [ChromaDB 文档](https://docs.trychroma.com)
- [Transformers.js](https://huggingface.co/docs/transformers.js)
