# PageIndex 集成 OpenCode - 常见问题解答

## 🤔 你的三个核心疑惑

### 疑惑 1: PageIndex 怎么不用设置模型？是默认用正在使用的模型吗？

**答案：不是！PageIndex 有自己独立的模型配置，与 OpenCode 的模型是分开的。**

#### 详细解释

**1. PageIndex MCP 服务器的模型配置**

PageIndex MCP 服务器（`npx -y @pageindex/mcp`）实际上是连接到 **PageIndex 云端服务**，它有自己的模型配置：

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"]
      // 这里的 "local" 指的是 MCP 服务器在本地运行
      // 但实际的 PDF 处理是在 PageIndex 云端完成的
    }
  }
}
```

**工作流程**：

```
OpenCode (使用你配置的模型，如 Claude)
    ↓ 调用 MCP 工具
PageIndex MCP 服务器 (本地运行)
    ↓ 转发请求
PageIndex 云端服务 (使用 PageIndex 自己的模型)
    ↓ 返回结果
OpenCode (继续使用 Claude 处理结果)
```

**2. PageIndex 使用的模型**

根据 PageIndex 官方文档，它默认使用：

- **GPT-4o** 系列模型（用于文档分析和树结构生成）
- 这是 PageIndex 服务端配置的，用户无需关心

**3. 如果想完全自托管（包括模型）**

如果你想完全控制模型，需要使用 **方案 D（自建 PageIndex）**：

```bash
# Clone PageIndex 仓库
git clone https://github.com/VectifyAI/PageIndex.git
cd PageIndex

# 配置你自己的模型
cat > .env << EOF
# 使用 OpenAI
CHATGPT_API_KEY=your_openai_key_here

# 或使用本地 Ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5:32b

# 或使用其他兼容 OpenAI API 的服务
OPENAI_API_BASE=https://your-api.com/v1
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_model
EOF
```

然后运行：

```bash
python3 run_pageindex.py \
  --pdf_path /path/to/document.pdf \
  --model qwen2.5:32b  # 指定你想用的模型
```

**4. 两种模型的配合**

实际使用中，有两个模型在工作：

| 阶段         | 使用的模型                             | 作用                             |
| ------------ | -------------------------------------- | -------------------------------- |
| **文档分析** | PageIndex 的模型（GPT-4o）             | 生成文档树结构、提取摘要         |
| **对话交互** | OpenCode 的模型（你配置的，如 Claude） | 理解用户问题、调用工具、生成回答 |

**示例对话流程**：

```
用户: 分析这份 PDF 的主要内容

1. OpenCode (Claude) 理解问题
   → 决定调用 pageindex_analyze_pdf 工具

2. PageIndex (GPT-4o) 处理 PDF
   → 生成树结构、提取章节摘要
   → 返回结构化数据

3. OpenCode (Claude) 处理返回结果
   → 理解树结构数据
   → 生成用户友好的回答
```

---

### 疑惑 2: 没有知识库也可以分析，内部流程有什么区别或优势？

**答案：区别巨大！PageIndex 的核心优势在于它的推理式检索方法，而不是简单的文本分析。**

#### 对比：传统方式 vs PageIndex

**场景：分析一份 200 页的财报**

##### 方式 A: 直接让 LLM 分析（传统方式）

```
用户: 分析 ~/Documents/annual-report.pdf 的主要内容

OpenCode (Claude):
❌ 问题 1: 上下文限制
- Claude 的上下文窗口有限（比如 200K tokens）
- 200 页 PDF 可能超过限制
- 只能分析部分内容或压缩内容

❌ 问题 2: 无法精确定位
- 无法告诉你"第 45 页讨论了什么"
- 无法准确引用页码

❌ 问题 3: 理解不深入
- 缺乏文档结构理解
- 无法建立章节之间的关联
- 容易遗漏重要信息
```

##### 方式 B: 使用传统 RAG（向量检索）

```
用户: 分析 ~/Documents/annual-report.pdf 的主要内容

传统 RAG 流程:
1. 将 PDF 分块（chunking）
   → 每块 500 tokens
   → 丢失上下文关联

2. 生成 embeddings
   → 基于语义相似度

3. 向量检索
   → 找到"相似"的块
   → 但相似 ≠ 相关

❌ 问题 1: 分块破坏结构
- "第三季度营收增长 15%" 和 "原因分析" 可能被分到不同块
- 丢失因果关系

❌ 问题 2: 相似度 ≠ 相关性
- 用户问"为什么营收下降"
- 向量检索可能返回所有提到"营收"的段落
- 但不一定是解释"下降原因"的段落

❌ 问题 3: Top-K 限制
- 只返回前 5 个最相似的块
- 可能遗漏重要信息
```

##### 方式 C: 使用 PageIndex（推理式检索）

```
用户: 分析 ~/Documents/annual-report.pdf 的主要内容

PageIndex 流程:

Step 1: 生成文档树结构
{
  "title": "2023 年度报告",
  "nodes": [
    {
      "title": "财务概览",
      "pages": [3, 8],
      "summary": "全年营收 $500M，同比增长 12%",
      "nodes": [
        {
          "title": "季度分析",
          "pages": [5, 6],
          "summary": "Q4 营收下降 8%，主要受市场波动影响"
        },
        {
          "title": "成本结构",
          "pages": [7, 8],
          "summary": "运营成本上升 15%，主要是研发投入增加"
        }
      ]
    },
    {
      "title": "业务展望",
      "pages": [45, 52],
      "summary": "预计 2024 年增长 20%，新产品线贡献显著"
    }
  ]
}

Step 2: 推理式检索
用户问: "为什么 Q4 营收下降？"

PageIndex 的推理过程:
1. 理解问题 → 需要找"Q4"和"下降原因"
2. 遍历树结构 → 找到"财务概览" → "季度分析"
3. 读取相关页面 (5-6 页)
4. 继续推理 → 可能还需要"成本结构"来完整回答
5. 读取 7-8 页
6. 综合分析 → 给出完整答案

✅ 优势 1: 保留文档结构
- 知道"季度分析"在"财务概览"下
- 理解章节之间的层级关系

✅ 优势 2: 推理式检索
- 不是简单的关键词匹配
- 而是理解"下降原因"需要哪些信息
- 自动关联相关章节

✅ 优势 3: 精确页码引用
- "根据第 5-6 页的季度分析..."
- "结合第 7-8 页的成本数据..."

✅ 优势 4: 无 Top-K 限制
- 自动检索所有相关信息
- 不会因为 Top-5 限制而遗漏
```

#### 核心区别总结

| 维度           | 直接分析          | 传统 RAG        | PageIndex       |
| -------------- | ----------------- | --------------- | --------------- |
| **上下文限制** | ❌ 受限于模型窗口 | ✅ 可处理长文档 | ✅ 可处理长文档 |
| **文档结构**   | ❌ 无结构理解     | ❌ 分块破坏结构 | ✅ 保留层级结构 |
| **检索方式**   | ❌ 无检索         | ⚠️ 语义相似度   | ✅ 推理式检索   |
| **页码引用**   | ❌ 无法引用       | ⚠️ 可能不准确   | ✅ 精确页码     |
| **信息完整性** | ❌ 可能遗漏       | ⚠️ Top-K 限制   | ✅ 自动关联     |
| **推理能力**   | ⚠️ 依赖模型       | ❌ 无推理       | ✅ 多步推理     |

#### 实际案例对比

**问题：分析一份 150 页的技术白皮书，找出"系统架构的安全性设计"**

**传统 RAG**:

```
1. 搜索 "安全性" → 返回 5 个相关段落
2. 可能包括：
   - 第 12 页：安全性概述
   - 第 45 页：网络安全
   - 第 78 页：数据加密
   - 第 92 页：访问控制
   - 第 105 页：安全审计

❌ 问题：
- 遗漏了第 120 页的"架构级安全设计"（因为 Top-5 限制）
- 无法理解这些章节之间的关系
- 不知道哪个是"架构层面"的安全
```

**PageIndex**:

```
1. 理解问题 → 需要"系统架构" + "安全性"
2. 遍历树结构：
   系统架构 (第 30-80 页)
   ├── 整体架构 (30-40)
   ├── 模块设计 (41-60)
   └── 安全性设计 (61-80)  ← 找到了！
       ├── 架构级安全 (61-70)
       ├── 模块级安全 (71-75)
       └── 数据流安全 (76-80)

3. 推理：用户问的是"架构的安全性"
   → 重点读取 61-70 页（架构级安全）
   → 补充 76-80 页（数据流安全，与架构相关）

4. 返回结果：
   "系统架构的安全性设计主要体现在：
   1. 零信任架构（第 62 页）
   2. 多层防御机制（第 65 页）
   3. 安全数据流设计（第 77 页）
   详细内容请参考第 61-80 页的'安全性设计'章节。"

✅ 优势：
- 准确定位到"架构级"安全（不是其他类型的安全）
- 理解章节层级关系
- 提供精确页码
- 不会遗漏相关信息
```

---

### 疑惑 3: PageIndex 内部部署这么简单吗？

**答案：取决于你选择的方案！**

#### 方案对比

##### 方案 A: 使用 PageIndex MCP 服务器（最简单）

**部署复杂度：⭐ (非常简单)**

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

**实际上发生了什么**：

```
1. npx 自动下载 @pageindex/mcp 包
2. 启动本地 MCP 服务器（Node.js 进程）
3. MCP 服务器作为"代理"，转发请求到 PageIndex 云端
4. 云端处理 PDF，返回结果
```

**这不是真正的"本地部署"**！

- ✅ MCP 服务器在本地运行
- ❌ PDF 处理在云端完成
- ❌ 需要网络连接
- ❌ 数据会上传到 PageIndex 服务器

**适合场景**：

- 快速体验 PageIndex
- 处理非敏感文档
- 不想自己维护服务

##### 方案 B: 完全本地部署（复杂）

**部署复杂度：⭐⭐⭐⭐⭐ (很复杂)**

**Step 1: 部署 PageIndex 核心服务**

```bash
# 1. Clone 仓库
git clone https://github.com/VectifyAI/PageIndex.git
cd PageIndex

# 2. 安装 Python 依赖
pip3 install --upgrade -r requirements.txt

# 需要的依赖包括：
# - PyMuPDF (PDF 解析)
# - OpenAI SDK (调用 LLM)
# - 其他 NLP 工具
```

**Step 2: 配置 LLM**

```bash
# 选项 1: 使用 OpenAI API
cat > .env << EOF
CHATGPT_API_KEY=your_openai_key
EOF

# 选项 2: 使用本地 Ollama
# 需要先安装 Ollama
brew install ollama
ollama pull qwen2.5:32b

cat > .env << EOF
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5:32b
EOF
```

**Step 3: 创建 MCP 包装服务器**

需要自己写代码包装 PageIndex：

```typescript
// pageindex-local-mcp/server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { spawn } from "child_process"

// 调用 PageIndex Python 脚本
function analyzePDF(pdfPath: string) {
  return new Promise((resolve, reject) => {
    const process = spawn("python3", ["/path/to/PageIndex/run_pageindex.py", "--pdf_path", pdfPath])

    // 处理输出...
  })
}

// 注册 MCP 工具...
```

**Step 4: 配置 OpenCode**

```json
{
  "mcp": {
    "pageindex-local": {
      "type": "local",
      "command": ["bun", "run", "/path/to/pageindex-local-mcp/server.ts"],
      "environment": {
        "PAGEINDEX_PATH": "/path/to/PageIndex"
      }
    }
  }
}
```

**复杂度分析**：

| 任务                | 难度       | 说明                         |
| ------------------- | ---------- | ---------------------------- |
| **Python 环境配置** | ⭐⭐       | 需要正确的 Python 版本和依赖 |
| **LLM 配置**        | ⭐⭐⭐     | 需要 API Key 或本地模型      |
| **MCP 服务器开发**  | ⭐⭐⭐⭐   | 需要理解 MCP 协议            |
| **错误处理**        | ⭐⭐⭐⭐⭐ | 需要处理各种边界情况         |
| **性能优化**        | ⭐⭐⭐⭐   | 大文档处理可能很慢           |

##### 方案 C: 混合方案（推荐）

**部署复杂度：⭐⭐⭐ (中等)**

**策略**：

- 敏感文档 → 本地处理（方案 B）
- 普通文档 → 云端处理（方案 A）

```json
{
  "mcp": {
    "pageindex-cloud": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"]
    },
    "pageindex-local": {
      "type": "local",
      "command": ["bun", "run", "/path/to/local-mcp/server.ts"],
      "enabled": false // 默认禁用，需要时手动启用
    }
  }
}
```

使用时：

```bash
# 普通文档，使用云端
opencode
"用 pageindex-cloud 分析这份公开报告"

# 敏感文档，使用本地
opencode mcp connect pageindex-local
"用 pageindex-local 分析这份内部文档"
```

#### 真实的"本地部署"需要什么？

**完整的技术栈**：

```
┌─────────────────────────────────────┐
│         OpenCode CLI                │
│  (你的主要交互界面)                  │
└──────────────┬──────────────────────┘
               │ MCP 协议
┌──────────────▼──────────────────────┐
│     MCP 服务器 (Node.js/Bun)        │
│  - 接收 OpenCode 的工具调用          │
│  - 转发给 PageIndex 核心             │
└──────────────┬──────────────────────┘
               │ 进程调用
┌──────────────▼──────────────────────┐
│    PageIndex 核心 (Python)          │
│  - PDF 解析 (PyMuPDF)                │
│  - 文档分析                          │
│  - 树结构生成                        │
└──────────────┬──────────────────────┘
               │ API 调用
┌──────────────▼──────────────────────┐
│         LLM 服务                    │
│  选项 1: OpenAI API (需要网络)       │
│  选项 2: 本地 Ollama                 │
│  选项 3: 其他兼容 API                │
└─────────────────────────────────────┘
```

**资源需求**：

| 组件                  | CPU | 内存  | 存储  | 网络             |
| --------------------- | --- | ----- | ----- | ---------------- |
| **OpenCode**          | 低  | 512MB | 100MB | 需要（调用 LLM） |
| **MCP 服务器**        | 低  | 256MB | 50MB  | 本地通信         |
| **PageIndex 核心**    | 中  | 2GB   | 500MB | 可选             |
| **本地 LLM (Ollama)** | 高  | 16GB+ | 20GB+ | 不需要           |

**时间成本**：

- 方案 A（云端）：**5 分钟**配置完成
- 方案 B（完全本地）：**1-2 天**（包括学习和调试）
- 方案 C（混合）：**半天**

---

## 🎯 推荐方案选择

### 如果你的目标是...

**1. 快速体验 PageIndex 的能力**
→ 使用方案 A（云端 MCP）

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

**2. 处理公司内部敏感文档**
→ 使用方案 B（完全本地）

- 需要投入时间学习和配置
- 需要准备本地 LLM（如 Ollama）
- 需要编写 MCP 包装服务器

**3. 平衡易用性和隐私**
→ 使用方案 C（混合）

- 日常使用云端服务
- 敏感文档使用本地处理
- 灵活切换

### 成本对比

| 方案     | 时间成本 | 金钱成本             | 维护成本 |
| -------- | -------- | -------------------- | -------- |
| **云端** | 5 分钟   | PageIndex 订阅费     | 零       |
| **本地** | 1-2 天   | 本地服务器 + LLM API | 高       |
| **混合** | 半天     | 两者都有             | 中       |

---

## 💡 总结

### 回答你的三个疑惑：

**1. 模型配置**

- PageIndex 有自己的模型（默认 GPT-4o）
- 与 OpenCode 的模型是分开的
- 如果要自定义，需要完全本地部署

**2. 与传统方式的区别**

- **核心优势**：推理式检索 vs 相似度检索
- **保留结构**：树形索引 vs 分块破坏
- **精确引用**：页码级别 vs 模糊定位
- **信息完整**：自动关联 vs Top-K 限制

**3. 部署复杂度**

- **方案 A（云端）**：非常简单（5 分钟）
- **方案 B（本地）**：很复杂（1-2 天）
- **实际情况**：大多数人用方案 A 就够了

### 建议

1. **先用方案 A 体验**，理解 PageIndex 的价值
2. **如果确实需要本地化**，再投入时间做方案 B
3. **对于企业用户**，考虑联系 PageIndex 的企业版（他们提供私有部署）

需要我帮你配置具体的方案吗？🚀
