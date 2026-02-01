# PageIndex 工作流程详解

## 🤔 你的疑问

**问题**：PageIndex 的推理检索需要先对 PDF 进行索引，那么：

1. 什么时候触发索引？
2. 是自动的还是手动的？
3. 完整的工作流程是怎样的？

**答案**：是的！PageIndex 需要**先索引，后检索**。有多种触发方式。

---

## 📊 完整工作流程

### 方式 1: 手动两步式（最基础）

**适合场景**：你明确知道要分析哪份文档

```
用户对话流程：

Step 1: 索引 PDF
─────────────────────────────────────
用户: 请先用 PageIndex 分析 ~/Documents/Q4-report.pdf

OpenCode (Claude):
  → 理解：用户要分析 PDF
  → 调用工具：pageindex_analyze_pdf
  → 参数：{ pdf_path: "~/Documents/Q4-report.pdf" }

PageIndex MCP 服务器:
  → 调用 Python 脚本
  → 处理 PDF（3-5 分钟）
  → 生成树结构
  → 保存：results/Q4-report_tree.json

OpenCode 返回:
  ✅ PDF 分析完成！
  **文档**: Q4-report.pdf
  **树结构文件**: Q4-report_tree.json

  文档包含以下主要章节：
  - 财务概览（第 3-15 页）
  - 季度分析（第 16-25 页）
  - 成本结构（第 26-30 页）
  ...

─────────────────────────────────────

Step 2: 查询文档
─────────────────────────────────────
用户: 为什么 Q4 营收下降？

OpenCode (Claude):
  → 理解：这是关于刚才分析的文档的问题
  → 调用工具：pageindex_query_document
  → 参数：{
      tree_file: "Q4-report_tree.json",
      query: "为什么 Q4 营收下降"
    }

PageIndex MCP 服务器:
  → 读取树结构
  → 推理检索：
    1. 定位到"季度分析"章节（第 16-25 页）
    2. 发现还需要"成本结构"（第 26-30 页）
  → 返回相关章节

OpenCode (Claude):
  → 综合树结构信息
  → 生成回答：

  根据 Q4 报告分析：

  Q4 营收下降主要原因（第 18-20 页）：
  1. 市场需求疲软，同比下降 12%
  2. 竞争加剧，市场份额流失

  成本因素（第 27-28 页）：
  3. 运营成本上升 15%
  4. 研发投入增加

  详细数据请参考第 18-20 页和第 27-28 页。
```

**时间线**：

```
T0: 用户提供 PDF
T1: 索引开始（手动触发）
T2: 索引完成（3-5 分钟后）
T3: 用户提问
T4: 推理检索（几秒钟）
T5: 返回答案
```

---

### 方式 2: 智能自动式（推荐）

**适合场景**：用户直接问问题，OpenCode 自动判断是否需要索引

```
用户对话流程：

用户: 分析 ~/Documents/Q4-report.pdf，告诉我为什么 Q4 营收下降

OpenCode (Claude) 的推理过程:
  → 理解：用户要分析一份新的 PDF 并回答问题
  → 判断：这份 PDF 还没有索引
  → 决策：先索引，再查询

  执行计划：
  1. 调用 pageindex_analyze_pdf（索引）
  2. 等待索引完成
  3. 调用 pageindex_query_document（查询）
  4. 综合回答

OpenCode 返回:
  正在分析 PDF，请稍候...

  [3-5 分钟后]

  ✅ 分析完成！

  根据 Q4 报告：

  Q4 营收下降主要原因：
  1. 市场需求疲软（第 18 页）
  2. 竞争加剧（第 19 页）
  3. 成本上升 15%（第 27 页）

  详细分析：
  ...
```

**关键**：OpenCode (Claude) 足够智能，能够：

- ✅ 判断 PDF 是否已索引
- ✅ 自动调用索引工具
- ✅ 等待索引完成
- ✅ 再调用查询工具
- ✅ 综合返回答案

---

### 方式 3: 批量预索引式（企业场景）

**适合场景**：定期处理大量文档，提前索引好

```bash
# 企业场景：每月财报自动索引

# 1. 创建索引脚本
cat > ~/scripts/index-reports.sh << 'EOF'
#!/bin/bash

REPORTS_DIR="/company/reports/2024"
PAGEINDEX_DIR="$HOME/pageindex-enterprise/PageIndex"

cd $PAGEINDEX_DIR

for pdf in $REPORTS_DIR/*.pdf; do
  echo "Indexing: $pdf"
  python3 run_pageindex.py --pdf_path "$pdf"
done

echo "All reports indexed!"
EOF

chmod +x ~/scripts/index-reports.sh

# 2. 设置定时任务（每月 1 号凌晨 2 点）
crontab -e
# 添加：
# 0 2 1 * * /Users/你的用户名/scripts/index-reports.sh

# 3. 使用时直接查询
```

**用户使用**：

```
用户: 对比 2024 年 Q1-Q4 的营收趋势

OpenCode:
  → 发现所有季度报告都已索引
  → 直接查询 4 个树结构文件
  → 快速返回对比结果（无需等待索引）
```

---

### 方式 4: 实时监控式（高级）

**适合场景**：监控特定目录，自动索引新文档

```typescript
// 创建文件监控服务
// ~/pageindex-enterprise/watcher/index.ts

import { watch } from "fs"
import { spawn } from "child_process"
import path from "path"

const WATCH_DIR = "/company/reports"
const PAGEINDEX_PATH = process.env.HOME + "/pageindex-enterprise/PageIndex"

console.log(`Watching: ${WATCH_DIR}`)

watch(WATCH_DIR, { recursive: true }, (eventType, filename) => {
  if (!filename?.endsWith(".pdf")) return
  if (eventType !== "rename") return // 新文件创建

  const pdfPath = path.join(WATCH_DIR, filename)
  console.log(`New PDF detected: ${pdfPath}`)

  // 自动索引
  console.log("Starting auto-indexing...")
  const process = spawn("python3", [path.join(PAGEINDEX_PATH, "run_pageindex.py"), "--pdf_path", pdfPath])

  process.on("close", (code) => {
    if (code === 0) {
      console.log(`✅ Indexed: ${filename}`)
    } else {
      console.error(`❌ Failed to index: ${filename}`)
    }
  })
})
```

**运行监控服务**：

```bash
# 启动监控
bun run ~/pageindex-enterprise/watcher/index.ts

# 或作为系统服务运行（macOS）
# 创建 ~/Library/LaunchAgents/com.company.pageindex-watcher.plist
```

---

## 🔄 索引触发时机对比

| 方式           | 触发时机          | 优点       | 缺点         | 适用场景 |
| -------------- | ----------------- | ---------- | ------------ | -------- |
| **手动两步**   | 用户明确要求索引  | 可控、明确 | 需要两次对话 | 临时分析 |
| **智能自动**   | OpenCode 自动判断 | 用户体验好 | 首次查询慢   | 日常使用 |
| **批量预索引** | 定时任务          | 查询快速   | 需要维护脚本 | 定期报告 |
| **实时监控**   | 文件创建时        | 完全自动   | 需要后台服务 | 企业场景 |

---

## 💡 实际使用建议

### 场景 1: 临时分析单个文档

**推荐**：智能自动式

```
用户: 分析这份合同 ~/Documents/contract.pdf，找出关键条款

OpenCode:
  → 自动索引（首次）
  → 推理检索
  → 返回答案
```

### 场景 2: 定期分析财报

**推荐**：批量预索引

```bash
# 每月自动索引
0 2 1 * * /path/to/index-reports.sh

# 使用时直接查询
用户: 对比 Q1-Q4 营收
OpenCode: [立即返回，无需等待]
```

### 场景 3: 企业知识库

**推荐**：实时监控 + 批量预索引

```
1. 历史文档：批量索引
2. 新文档：自动监控索引
3. 查询：即时响应
```

---

## 🎯 优化索引体验

### 1. 增加索引状态提示

修改 MCP 服务器，添加进度反馈：

```typescript
// 在 server.ts 中
pythonProcess.stdout.on("data", (data) => {
  const text = data.toString()

  // 解析进度
  if (text.includes("Processing page")) {
    const match = text.match(/page (\d+)\/(\d+)/)
    if (match) {
      const [_, current, total] = match
      console.error(`Progress: ${current}/${total} pages`)
    }
  }
})
```

**用户体验**：

```
用户: 分析这份 200 页的报告

OpenCode:
  正在分析 PDF...
  进度: 50/200 页 (25%)
  进度: 100/200 页 (50%)
  进度: 150/200 页 (75%)
  进度: 200/200 页 (100%)

  ✅ 分析完成！
```

### 2. 缓存已索引文档

```typescript
// 在 MCP 服务器中维护索引缓存
const indexedDocs = new Map<string, string>() // pdf_path -> tree_file

// 检查是否已索引
if (indexedDocs.has(pdf_path)) {
  return {
    content: [
      {
        type: "text",
        text: `文档已索引，使用缓存: ${indexedDocs.get(pdf_path)}`,
      },
    ],
  }
}
```

### 3. 智能索引策略

```typescript
// 根据文档大小决定策略
const fileSize = fs.statSync(pdf_path).size
const pages = await getPdfPageCount(pdf_path)

if (pages < 20) {
  // 小文档：快速索引
  max_pages_per_node = 5
} else if (pages < 100) {
  // 中等文档：标准索引
  max_pages_per_node = 10
} else {
  // 大文档：粗粒度索引
  max_pages_per_node = 20
}
```

---

## 📝 完整示例对话

### 示例 1: 首次分析（自动索引）

```
用户: 帮我分析 ~/Documents/annual-report-2024.pdf，
      总结主要财务指标

OpenCode (内部推理):
  1. 检查文档是否已索引 → 否
  2. 决定先索引
  3. 调用 pageindex_analyze_pdf

OpenCode (对用户):
  正在分析文档，这可能需要几分钟...

  [索引中: 3-5 分钟]

  ✅ 文档分析完成！

  根据 2024 年度报告，主要财务指标：

  **营收** (第 5 页)
  - 全年: $500M
  - 同比增长: 12%

  **利润** (第 8 页)
  - 净利润: $85M
  - 利润率: 17%

  **现金流** (第 12 页)
  - 经营现金流: $120M
  - 自由现金流: $95M

  详细分析请参考第 5-15 页的"财务概览"章节。

─────────────────────────────────────

用户: Q4 的表现如何？

OpenCode (内部推理):
  1. 检查文档是否已索引 → 是（刚才索引的）
  2. 直接查询树结构

OpenCode (对用户):
  根据 Q4 季度分析（第 18-22 页）：

  **Q4 营收**: $142M
  - 环比增长: 8%
  - 同比增长: 15%

  **主要驱动因素**:
  1. 新产品线贡献 $12M
  2. 市场份额扩大
  3. 运营效率提升

  [几秒钟内返回，无需重新索引]
```

### 示例 2: 多文档对比（预索引）

```
# 假设已经预索引了 Q1-Q4 报告

用户: 对比 2024 年各季度的营收趋势

OpenCode (内部推理):
  1. 检查 4 份文档是否已索引 → 全部已索引
  2. 并行查询 4 个树结构
  3. 综合分析

OpenCode (对用户):
  2024 年季度营收趋势分析：

  📊 营收对比
  - Q1: $118M (基准)
  - Q2: $125M (+6%)
  - Q3: $131M (+5%)
  - Q4: $142M (+8%)

  📈 增长趋势
  - 全年稳定增长
  - Q4 增速加快
  - 累计增长: 20%

  🔍 关键发现
  - Q2 增长放缓（市场调整，Q2 报告第 15 页）
  - Q4 强劲反弹（新产品线，Q4 报告第 20 页）

  [立即返回，因为都已预索引]
```

---

## ⚡ 性能优化

### 索引时间对比

| 文档大小 | 页数       | 索引时间   | 查询时间 |
| -------- | ---------- | ---------- | -------- |
| 小型     | 10-20 页   | 30-60 秒   | 1-2 秒   |
| 中型     | 50-100 页  | 2-4 分钟   | 2-3 秒   |
| 大型     | 200-500 页 | 5-10 分钟  | 3-5 秒   |
| 超大     | 1000+ 页   | 20-30 分钟 | 5-10 秒  |

**关键点**：

- ✅ 索引慢（一次性）
- ✅ 查询快（重复使用）
- ✅ 适合多次查询同一文档

### 并行索引

```bash
# 批量索引时并行处理
#!/bin/bash

REPORTS_DIR="/company/reports"
MAX_PARALLEL=4

find $REPORTS_DIR -name "*.pdf" | \
  xargs -P $MAX_PARALLEL -I {} \
  python3 run_pageindex.py --pdf_path {}

# 4 个文档同时索引，速度提升 4 倍
```

---

## ✅ 总结

### 回答你的疑问

**1. 是否需要先索引？**

- ✅ 是的，必须先索引才能推理检索

**2. 什么时候触发？**

- 方式 1: 用户手动要求（明确）
- 方式 2: OpenCode 自动判断（智能）
- 方式 3: 定时任务（批量）
- 方式 4: 文件监控（实时）

**3. 推荐方式？**

- 日常使用：**智能自动式**（OpenCode 自动判断）
- 企业场景：**批量预索引** + 实时监控

### 工作流程

```
┌─────────────────────────────────────┐
│ 1. 索引阶段（一次性，3-5 分钟）      │
│    PDF → 树结构 → 保存               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. 查询阶段（重复使用，几秒钟）      │
│    问题 → 推理检索 → 答案            │
└─────────────────────────────────────┘
```

### 关键优势

相比传统 RAG：

- ✅ 索引一次，查询多次
- ✅ 保留文档结构
- ✅ 推理式检索
- ✅ 精确页码引用

需要我帮你配置自动索引吗？🚀
