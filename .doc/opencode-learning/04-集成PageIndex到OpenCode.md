# OpenCode CLI 集成 PageIndex 完整方案

## 🎯 问题回答

### 问题 1: 能不能通过本地部署 PageIndex 让 OpenCode CLI 调用？

**答案：✅ 完全可以！而且有多种方案可选。**

PageIndex 已经提供了 **官方 MCP 服务器**，OpenCode 原生支持 MCP 协议，所以集成非常简单！

## 📊 集成方案对比

| 方案                           | 部署方式   | 数据隐私              | 功能完整度              | 难度            | 推荐指数   |
| ------------------------------ | ---------- | --------------------- | ----------------------- | --------------- | ---------- |
| **方案 A: 本地 MCP 服务器**    | 本地运行   | ⭐⭐⭐⭐⭐ 完全本地   | ⭐⭐⭐⭐⭐ 支持本地 PDF | ⭐⭐⭐ 简单     | ⭐⭐⭐⭐⭐ |
| **方案 B: 远程 MCP (OAuth)**   | 云端服务   | ⭐⭐⭐ 数据上传到云端 | ⭐⭐⭐⭐⭐ 全功能       | ⭐⭐ 最简单     | ⭐⭐⭐⭐   |
| **方案 C: 远程 MCP (API Key)** | 云端服务   | ⭐⭐⭐ 数据上传到云端 | ⭐⭐⭐⭐ 仅支持 URL     | ⭐⭐ 最简单     | ⭐⭐⭐     |
| **方案 D: 自建 PageIndex**     | 完全自托管 | ⭐⭐⭐⭐⭐ 完全本地   | ⭐⭐⭐⭐⭐ 完全可定制   | ⭐⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐   |

## 🚀 推荐方案：本地 MCP 服务器（方案 A）

**最佳平衡：本地化 + 简单易用 + 功能完整**

### 优势分析

✅ **数据隐私**

- PDF 文件在本地处理
- 不需要上传到云端
- 适合处理敏感文档

✅ **功能完整**

- 支持本地 PDF 文件上传
- 支持在线 PDF URL
- 自动处理认证

✅ **简单易用**

- 一行命令配置
- 自动安装依赖
- 无需手动部署

## 📝 方案 A：本地 MCP 服务器集成步骤

### 前置要求

```bash
# 检查 Node.js 版本（需要 >= 18.0.0）
node --version

# 如果版本不够，安装最新版
# macOS
brew install node

# 或使用 nvm
nvm install 18
nvm use 18
```

### Step 1: 配置 OpenCode

编辑 OpenCode 配置文件：

```bash
# 打开配置文件
vim ~/.opencode/config.json
# 或
code ~/.opencode/config.json
```

添加 PageIndex MCP 配置：

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"]
    }
  }
}
```

**配置说明**：

- `type: "local"` - 本地 MCP 服务器
- `npx -y @pageindex/mcp` - 自动下载并运行 PageIndex MCP 服务器
- `-y` 参数会自动确认安装，无需手动干预

### Step 2: 验证配置

```bash
# 列出所有 MCP 服务器
opencode mcp list

# 应该看到类似输出：
# ┌───────────┬───────────┬──────────┐
# │ Name      │ Status    │ Type     │
# ├───────────┼───────────┼──────────┤
# │ pageindex │ connected │ local    │
# └───────────┴───────────┴──────────┘
```

### Step 3: 开始使用

启动 OpenCode：

```bash
opencode
```

在对话中使用 PageIndex：

```
# 示例 1: 分析本地 PDF
请使用 PageIndex 分析 ~/Documents/report.pdf，告诉我主要内容

# 示例 2: 分析在线 PDF
请使用 PageIndex 分析 https://arxiv.org/pdf/2301.00234.pdf 这篇论文的核心观点

# 示例 3: 多文档对比
使用 PageIndex 对比这两份财报的差异：
1. ~/Documents/q1-report.pdf
2. ~/Documents/q2-report.pdf
```

## 🔧 方案 B：远程 MCP 服务器（OAuth 认证）

**适合场景**：不想本地运行服务，愿意使用云端服务

### Step 1: 配置 OpenCode

```json
{
  "mcp": {
    "pageindex-remote": {
      "type": "remote",
      "url": "https://chat.pageindex.ai/mcp",
      "oauth": true
    }
  }
}
```

### Step 2: 认证

```bash
# 启动 OAuth 认证流程
opencode mcp auth pageindex-remote

# 会自动打开浏览器，完成 OAuth 授权
# 授权后会自动连接
```

### Step 3: 使用

```bash
opencode

# 在对话中使用（仅支持 URL，不支持本地文件）
请使用 PageIndex 分析 https://example.com/document.pdf
```

## 🔑 方案 C：远程 MCP 服务器（API Key 认证）

**适合场景**：需要程序化访问，不想使用 OAuth

### Step 1: 获取 API Key

1. 访问 https://chat.pageindex.ai/chat#settings/api-keys
2. 点击 "Create Key"
3. 复制生成的 API Key（格式：`pi_xxxxx...`）
4. **重要**：API Key 只显示一次，请妥善保存

### Step 2: 配置 OpenCode

```json
{
  "mcp": {
    "pageindex-api": {
      "type": "remote",
      "url": "https://chat.pageindex.ai/mcp",
      "headers": {
        "Authorization": "Bearer pi_your_api_key_here"
      }
    }
  }
}
```

### Step 3: 使用

```bash
opencode

# 直接使用，无需额外认证
请分析这份文档：https://example.com/report.pdf
```

## 🏗️ 方案 D：自建 PageIndex 服务（完全自托管）

**适合场景**：

- 需要完全控制数据
- 需要定制 PageIndex 功能
- 企业内部部署

### Step 1: Clone PageIndex 仓库

```bash
# Clone 主仓库
git clone https://github.com/VectifyAI/PageIndex.git
cd PageIndex

# 安装依赖
pip3 install --upgrade -r requirements.txt
```

### Step 2: 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
CHATGPT_API_KEY=your_openai_key_here
# 或使用其他兼容的 API
# OPENAI_API_BASE=http://localhost:11434/v1
# OPENAI_API_KEY=ollama
EOF
```

### Step 3: 创建 MCP 包装服务器

创建文件 `pageindex-mcp-wrapper/server.ts`：

```typescript
#!/usr/bin/env bun
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js"
import { spawn } from "child_process"
import path from "path"

const PAGEINDEX_PATH = process.env.PAGEINDEX_PATH || "/path/to/PageIndex"

const server = new Server(
  {
    name: "pageindex-local",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  },
)

// 注册工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze_pdf",
      description: "Analyze a PDF document using PageIndex to create a hierarchical tree structure",
      inputSchema: {
        type: "object",
        properties: {
          pdf_path: {
            type: "string",
            description: "Path to the PDF file (local path or URL)",
          },
          model: {
            type: "string",
            description: "OpenAI model to use",
            default: "gpt-4o-2024-11-20",
          },
          max_pages_per_node: {
            type: "number",
            description: "Maximum pages per node",
            default: 10,
          },
        },
        required: ["pdf_path"],
      },
    },
    {
      name: "query_document",
      description: "Query an analyzed document using reasoning-based retrieval",
      inputSchema: {
        type: "object",
        properties: {
          tree_path: {
            type: "string",
            description: "Path to the generated tree JSON file",
          },
          query: {
            type: "string",
            description: "Question to ask about the document",
          },
        },
        required: ["tree_path", "query"],
      },
    },
  ],
}))

// 实现工具
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  if (name === "analyze_pdf") {
    const { pdf_path, model = "gpt-4o-2024-11-20", max_pages_per_node = 10 } = args as any

    return new Promise((resolve, reject) => {
      const pythonProcess = spawn("python3", [
        path.join(PAGEINDEX_PATH, "run_pageindex.py"),
        "--pdf_path",
        pdf_path,
        "--model",
        model,
        "--max-pages-per-node",
        String(max_pages_per_node),
      ])

      let output = ""
      let error = ""

      pythonProcess.stdout.on("data", (data) => {
        output += data.toString()
      })

      pythonProcess.stderr.on("data", (data) => {
        error += data.toString()
      })

      pythonProcess.on("close", (code) => {
        if (code === 0) {
          resolve({
            content: [
              {
                type: "text",
                text: `Successfully analyzed PDF. Output:\n${output}`,
              },
            ],
          })
        } else {
          reject(new Error(`PageIndex failed: ${error}`))
        }
      })
    })
  }

  if (name === "query_document") {
    const { tree_path, query } = args as any

    // 实现基于树结构的查询逻辑
    // 这里需要实现推理检索算法

    return {
      content: [
        {
          type: "text",
          text: `Query result for: ${query}`,
        },
      ],
    }
  }

  throw new Error(`Unknown tool: ${name}`)
})

// 启动服务器
const transport = new StdioServerTransport()
await server.connect(transport)

console.error("PageIndex MCP server running")
```

### Step 4: 配置 OpenCode

```json
{
  "mcp": {
    "pageindex-local": {
      "type": "local",
      "command": ["bun", "run", "/path/to/pageindex-mcp-wrapper/server.ts"],
      "environment": {
        "PAGEINDEX_PATH": "/path/to/PageIndex",
        "CHATGPT_API_KEY": "your_openai_key"
      }
    }
  }
}
```

## 🎨 高级配置

### 配置超时时间

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"],
      "timeout": 60000 // 60 秒超时
    }
  }
}
```

### 配置环境变量

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"],
      "environment": {
        "PAGEINDEX_API_KEY": "your_key",
        "PAGEINDEX_MODEL": "gpt-4o",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

### 禁用/启用 MCP 服务器

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"],
      "enabled": false // 临时禁用
    }
  }
}
```

## 🔍 故障排查

### 问题 1: MCP 服务器连接失败

```bash
# 查看详细日志
opencode mcp debug pageindex

# 检查 Node.js 版本
node --version  # 应该 >= 18.0.0

# 手动测试 MCP 服务器
npx -y @pageindex/mcp
```

### 问题 2: 认证失败

```bash
# 清除认证缓存
rm -rf ~/.opencode/mcp-auth/pageindex

# 重新认证
opencode mcp auth pageindex
```

### 问题 3: PDF 处理失败

```bash
# 检查 PDF 文件路径
ls -lh ~/Documents/report.pdf

# 检查 PDF 文件大小（PageIndex 有免费额度限制）
du -h ~/Documents/report.pdf

# 尝试使用 URL 而不是本地文件
# 将 PDF 上传到可访问的 URL
```

### 问题 4: 工具未显示

```bash
# 列出所有可用工具
opencode mcp list

# 检查 MCP 状态
opencode mcp list

# 重启 OpenCode
# Ctrl+C 退出，然后重新运行
opencode
```

## 📊 使用示例

### 示例 1: 分析技术文档

```
用户: 请使用 PageIndex 分析 ~/Documents/api-documentation.pdf，
      总结主要的 API 端点和它们的功能

OpenCode:
[调用 pageindex_analyze_pdf 工具]
已成功分析文档，生成了层级树结构。

根据分析，该文档包含以下主要 API 端点：

1. 用户管理 API (第 5-12 页)
   - POST /api/users - 创建用户
   - GET /api/users/:id - 获取用户信息
   - PUT /api/users/:id - 更新用户

2. 认证 API (第 13-18 页)
   - POST /api/auth/login - 用户登录
   - POST /api/auth/refresh - 刷新令牌

3. 数据查询 API (第 19-35 页)
   - GET /api/data/search - 搜索数据
   - POST /api/data/query - 复杂查询

详细信息请参考相应页码。
```

### 示例 2: 对比多份文档

```
用户: 使用 PageIndex 对比这两份季度报告的财务数据变化：
      - ~/Documents/Q1-2024.pdf
      - ~/Documents/Q2-2024.pdf

OpenCode:
[调用 pageindex_analyze_pdf 处理两份文档]

对比分析如下：

**营收变化**
- Q1: $125M (第 3 页)
- Q2: $142M (第 3 页)
- 增长: +13.6%

**利润率**
- Q1: 18.5% (第 5 页)
- Q2: 21.2% (第 5 页)
- 提升: +2.7 个百分点

**主要变化原因** (Q2 报告第 8-10 页)
1. 新产品线贡献 $12M
2. 运营效率提升
3. 市场份额扩大
```

### 示例 3: 研究论文分析

```
用户: 分析这篇 AI 论文的核心创新点：
      https://arxiv.org/pdf/2401.12345.pdf

OpenCode:
[调用 pageindex_analyze_pdf]

该论文的核心创新点：

1. **新架构设计** (第 3-5 页)
   - 提出了 Hybrid Attention 机制
   - 结合了局部和全局注意力
   - 计算复杂度降低 40%

2. **训练方法** (第 6-8 页)
   - 引入 Progressive Learning 策略
   - 分阶段训练，提升稳定性

3. **实验结果** (第 9-12 页)
   - 在 5 个基准测试上超越 SOTA
   - 推理速度提升 2.3x

4. **理论分析** (第 13-15 页)
   - 证明了收敛性保证
   - 提供了复杂度分析
```

## 🎯 最佳实践

### 1. 选择合适的方案

- **个人使用、敏感文档** → 方案 A（本地 MCP）
- **团队协作、公开文档** → 方案 B（远程 OAuth）
- **自动化脚本** → 方案 C（API Key）
- **企业部署、完全定制** → 方案 D（自建）

### 2. 优化性能

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"],
      "timeout": 120000, // 大文档需要更长时间
      "environment": {
        "MAX_PAGES_PER_NODE": "15", // 调整分块大小
        "MODEL": "gpt-4o-mini" // 使用更快的模型
      }
    }
  }
}
```

### 3. 安全建议

- ✅ 使用环境变量存储 API Key
- ✅ 定期轮换 API Key
- ✅ 限制文件访问权限
- ✅ 审计 MCP 调用日志

### 4. 成本控制

```typescript
// 在 OpenCode 提示词中添加成本意识
"在使用 PageIndex 之前，先评估文档大小。
如果文档超过 100 页，询问用户是否继续。"
```

## 📚 相关资源

- [PageIndex 官方文档](https://docs.pageindex.ai/)
- [PageIndex GitHub](https://github.com/VectifyAI/PageIndex)
- [PageIndex MCP GitHub](https://github.com/VectifyAI/pageindex-mcp)
- [OpenCode MCP 文档](https://opencode.ai/docs/mcp)
- [Model Context Protocol 规范](https://modelcontextprotocol.io)

## ✅ 总结

**问题 1 的答案：完全可以！**

OpenCode CLI 可以通过以下方式调用本地部署的 PageIndex：

1. ✅ **最简单**：使用 `npx -y @pageindex/mcp`（推荐）
2. ✅ **最灵活**：自建 MCP 包装服务器
3. ✅ **最快速**：使用远程 MCP 服务

推荐从 **方案 A（本地 MCP 服务器）** 开始，一行配置即可使用：

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"]
    }
  }
}
```

这样你就可以在 OpenCode 中使用 PageIndex 的强大文档分析能力了！🎉
