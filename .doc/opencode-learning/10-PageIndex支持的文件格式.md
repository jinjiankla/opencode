# PageIndex 支持的文件格式详解

## 🤔 你的两个问题

### 问题 1: PageIndex 用的模型是我配置的模型吗？

**答案：是的！** PageIndex 使用你配置的模型。

```bash
# 在 .env 中配置
OPENAI_API_BASE=http://internal-llm.company.com/v1
OPENAI_API_KEY=sk-company-key
OPENAI_MODEL=qwen-plus  # ← 你配置的模型

# PageIndex 会使用这个模型来：
# 1. 分析文档结构
# 2. 生成章节摘要
# 3. 创建树形索引
```

### 问题 2: PageIndex 能索引代码和其他文档格式吗？

**答案：部分支持，但有限制。**

---

## 📊 PageIndex 官方支持的格式

### ✅ 完全支持

| 格式         | 支持程度   | 说明               |
| ------------ | ---------- | ------------------ |
| **PDF**      | ⭐⭐⭐⭐⭐ | 完美支持，核心功能 |
| **Markdown** | ⭐⭐⭐⭐   | 支持，基于标题层级 |

### ⚠️ 有限支持

| 格式         | 支持程度 | 说明             |
| ------------ | -------- | ---------------- |
| **TXT**      | ⭐⭐     | 需要转换或自定义 |
| **代码文件** | ⭐       | 需要自定义解析   |
| **HTML**     | ⚠️       | 建议先转 PDF/MD  |
| **Word**     | ⚠️       | 建议先转 PDF     |

---

## 📝 详细说明

### 1. PDF 文件（完美支持）

**使用方式**：

```bash
python3 run_pageindex.py --pdf_path /path/to/document.pdf
```

**工作原理**：

```
PDF → 解析页面 → 识别结构 → 生成树形索引
```

**适用场景**：

- ✅ 财务报告
- ✅ 学术论文
- ✅ 技术手册
- ✅ 合同文档
- ✅ 任何有结构的 PDF

---

### 2. Markdown 文件（原生支持）

**使用方式**：

```bash
python3 run_pageindex.py --md_path /path/to/document.md
```

**工作原理**：

```markdown
# 一级标题 (Level 1)

## 二级标题 (Level 2)

### 三级标题 (Level 3)

PageIndex 使用 # 的数量来确定层级
```

**示例**：

```markdown
# 项目文档

## 架构设计

### 前端架构

- React 组件设计
- 状态管理

### 后端架构

- API 设计
- 数据库设计

## 部署指南

### 开发环境

### 生产环境
```

**生成的树结构**：

```json
{
  "title": "项目文档",
  "nodes": [
    {
      "title": "架构设计",
      "nodes": [
        { "title": "前端架构", "content": "..." },
        { "title": "后端架构", "content": "..." }
      ]
    },
    {
      "title": "部署指南",
      "nodes": [
        { "title": "开发环境", "content": "..." },
        { "title": "生产环境", "content": "..." }
      ]
    }
  ]
}
```

**注意事项**：

- ⚠️ 必须使用正确的标题层级（#, ##, ###）
- ⚠️ 如果 Markdown 是从 PDF 转换的，可能丢失层级
- ✅ 推荐使用 PageIndex OCR 转换 PDF → Markdown

---

### 3. TXT 文件（需要转换）

**问题**：

- ❌ TXT 文件没有明确的层级结构
- ❌ PageIndex 依赖结构来生成树形索引

**解决方案 A：转换为 Markdown**

```bash
# 手动添加标题层级
cat > document.md << 'EOF'
# 文档标题

## 第一章
内容...

## 第二章
内容...
EOF

# 然后用 PageIndex 处理
python3 run_pageindex.py --md_path document.md
```

**解决方案 B：自定义解析器**

创建 `txt_to_tree.py`：

```python
#!/usr/bin/env python3
"""
将 TXT 文件转换为 PageIndex 树结构
假设 TXT 文件使用空行分段
"""

import json
import re

def parse_txt_to_tree(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按段落分割
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    # 简单的树结构
    tree = {
        "title": "TXT Document",
        "nodes": []
    }

    for i, para in enumerate(paragraphs):
        # 如果段落以数字开头，视为章节
        if re.match(r'^\d+\.', para):
            tree["nodes"].append({
                "title": para.split('\n')[0],
                "content": para,
                "index": i
            })
        else:
            # 否则添加到最后一个章节
            if tree["nodes"]:
                tree["nodes"][-1]["content"] += "\n\n" + para

    return tree

# 使用
tree = parse_txt_to_tree("document.txt")
with open("document_tree.json", "w") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)
```

---

### 4. 代码文件（需要自定义）

**问题**：

- ❌ PageIndex 不原生支持代码文件
- ❌ 代码的"层级"与文档不同（类、函数 vs 章节）

**解决方案：为代码创建自定义索引**

#### 方案 A：使用 AST 解析器

创建 `code_to_tree.py`：

```python
#!/usr/bin/env python3
"""
将 Python 代码文件转换为树结构
"""

import ast
import json

def parse_python_to_tree(py_path):
    with open(py_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree_obj = ast.parse(code)

    tree = {
        "title": py_path,
        "type": "python_file",
        "nodes": []
    }

    for node in ast.iter_child_nodes(tree_obj):
        if isinstance(node, ast.ClassDef):
            # 类
            class_node = {
                "title": f"Class: {node.name}",
                "type": "class",
                "line": node.lineno,
                "nodes": []
            }

            # 类的方法
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    class_node["nodes"].append({
                        "title": f"Method: {item.name}",
                        "type": "method",
                        "line": item.lineno,
                        "docstring": ast.get_docstring(item)
                    })

            tree["nodes"].append(class_node)

        elif isinstance(node, ast.FunctionDef):
            # 函数
            tree["nodes"].append({
                "title": f"Function: {node.name}",
                "type": "function",
                "line": node.lineno,
                "docstring": ast.get_docstring(node)
            })

    return tree

# 使用
tree = parse_python_to_tree("mycode.py")
with open("code_tree.json", "w") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)
```

**生成的树结构**：

```json
{
  "title": "mycode.py",
  "type": "python_file",
  "nodes": [
    {
      "title": "Class: UserService",
      "type": "class",
      "line": 10,
      "nodes": [
        {
          "title": "Method: __init__",
          "type": "method",
          "line": 11
        },
        {
          "title": "Method: create_user",
          "type": "method",
          "line": 15,
          "docstring": "创建新用户"
        }
      ]
    },
    {
      "title": "Function: main",
      "type": "function",
      "line": 50
    }
  ]
}
```

#### 方案 B：转换为 Markdown

```python
#!/usr/bin/env python3
"""
将代码文件转换为 Markdown，然后用 PageIndex 处理
"""

import ast

def code_to_markdown(py_path, md_path):
    with open(py_path, 'r', encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)

    md_lines = [f"# {py_path}\n"]

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            md_lines.append(f"\n## Class: {node.name}\n")
            docstring = ast.get_docstring(node)
            if docstring:
                md_lines.append(f"{docstring}\n")

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    md_lines.append(f"\n### Method: {item.name}\n")
                    method_doc = ast.get_docstring(item)
                    if method_doc:
                        md_lines.append(f"{method_doc}\n")

        elif isinstance(node, ast.FunctionDef):
            md_lines.append(f"\n## Function: {node.name}\n")
            docstring = ast.get_docstring(node)
            if docstring:
                md_lines.append(f"{docstring}\n")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.writelines(md_lines)

# 使用
code_to_markdown("mycode.py", "mycode.md")

# 然后用 PageIndex 处理
# python3 run_pageindex.py --md_path mycode.md
```

---

## 🚀 实际应用方案

### 场景 1: 索引公司代码库

**目标**：为整个代码库创建可搜索的索引

**方案**：

```bash
# 1. 创建代码索引脚本
cat > index_codebase.py << 'EOF'
#!/usr/bin/env python3
import os
import ast
import json
from pathlib import Path

def index_codebase(root_dir):
    """索引整个代码库"""
    codebase_tree = {
        "title": "Codebase Index",
        "nodes": []
    }

    for py_file in Path(root_dir).rglob("*.py"):
        try:
            tree = parse_python_to_tree(str(py_file))
            codebase_tree["nodes"].append(tree)
        except:
            pass

    return codebase_tree

# 索引代码库
tree = index_codebase("/path/to/your/codebase")
with open("codebase_index.json", "w") as f:
    json.dump(tree, f, indent=2, ensure_ascii=False)
EOF

# 2. 运行索引
python3 index_codebase.py

# 3. 在 OpenCode 中使用
# 创建一个 MCP 工具来查询这个索引
```

### 场景 2: 索引技术文档 + 代码

**目标**：同时索引 Markdown 文档和代码

**方案**：

```bash
# 1. 索引所有 Markdown 文档
for md in docs/*.md; do
  python3 run_pageindex.py --md_path "$md"
done

# 2. 将代码转换为 Markdown
python3 code_to_markdown.py src/ docs/code/

# 3. 索引转换后的代码文档
for md in docs/code/*.md; do
  python3 run_pageindex.py --md_path "$md"
done

# 4. 在 OpenCode 中统一查询
```

### 场景 3: 混合文档索引

**目标**：索引 PDF、Markdown、代码

**创建统一的 MCP 服务器**：

```python
#!/usr/bin/env python3
"""
统一文档索引 MCP 服务器
支持 PDF, Markdown, 代码
"""

from mcp.server import Server
import subprocess
import os

app = Server("unified-doc-index")

@app.list_tools()
async def list_tools():
    return [
        {
            "name": "index_document",
            "description": "索引文档（支持 PDF, MD, PY, TXT）",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "file_type": {
                        "type": "string",
                        "enum": ["pdf", "md", "py", "txt"]
                    }
                },
                "required": ["file_path"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "index_document":
        file_path = arguments["file_path"]
        file_type = arguments.get("file_type") or detect_file_type(file_path)

        if file_type == "pdf":
            # 直接用 PageIndex
            result = subprocess.run([
                "python3", "run_pageindex.py",
                "--pdf_path", file_path
            ], capture_output=True, text=True)

        elif file_type == "md":
            # 直接用 PageIndex
            result = subprocess.run([
                "python3", "run_pageindex.py",
                "--md_path", file_path
            ], capture_output=True, text=True)

        elif file_type == "py":
            # 先转换为 Markdown
            md_path = file_path.replace(".py", ".md")
            code_to_markdown(file_path, md_path)

            # 再用 PageIndex
            result = subprocess.run([
                "python3", "run_pageindex.py",
                "--md_path", md_path
            ], capture_output=True, text=True)

        elif file_type == "txt":
            # 先转换为 Markdown
            md_path = file_path.replace(".txt", ".md")
            txt_to_markdown(file_path, md_path)

            # 再用 PageIndex
            result = subprocess.run([
                "python3", "run_pageindex.py",
                "--md_path", md_path
            ], capture_output=True, text=True)

        return [{"type": "text", "text": result.stdout}]

def detect_file_type(file_path):
    """自动检测文件类型"""
    ext = os.path.splitext(file_path)[1].lower()
    return ext[1:]  # 去掉点号

# 启动服务器
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))
```

---

## 📊 推荐方案总结

### 对于不同文件类型

| 文件类型     | 推荐方案                        | 复杂度 |
| ------------ | ------------------------------- | ------ |
| **PDF**      | 直接使用 PageIndex              | ⭐     |
| **Markdown** | 直接使用 PageIndex              | ⭐     |
| **TXT**      | 转换为 Markdown → PageIndex     | ⭐⭐   |
| **代码**     | AST 解析 → Markdown → PageIndex | ⭐⭐⭐ |
| **Word**     | 导出为 PDF → PageIndex          | ⭐     |
| **HTML**     | 转换为 PDF/MD → PageIndex       | ⭐⭐   |

### 对于你的需求（代码 + 文档）

**推荐方案**：

1. **文档（MD/TXT）**：直接或转换后使用 PageIndex
2. **代码**：创建自定义解析器 → 转换为 Markdown → PageIndex

**实现步骤**：

```bash
# 1. 为代码创建解析器
python3 code_to_markdown.py src/ docs/code/

# 2. 索引所有文档
for md in docs/**/*.md; do
  python3 run_pageindex.py --md_path "$md"
done

# 3. 在 OpenCode 中统一查询
```

---

## ✅ 总结

### 回答你的问题

**问题 1: PageIndex 用的是我配置的模型吗？**

```
✅ 是的！
PageIndex 使用你在 .env 中配置的模型：
- OPENAI_API_BASE
- OPENAI_API_KEY
- OPENAI_MODEL
```

**问题 2: 能索引代码和其他格式吗？**

```
✅ PDF: 完美支持
✅ Markdown: 原生支持
⚠️ TXT: 需要转换为 Markdown
⚠️ 代码: 需要自定义解析器

推荐方案:
代码 → AST 解析 → Markdown → PageIndex
```

### 关键点

1. **PageIndex 依赖文档结构**
   - 需要明确的层级（章节、标题）
   - 代码需要先提取结构

2. **代码索引需要自定义**
   - 使用 AST 解析器
   - 转换为 Markdown 格式
   - 然后用 PageIndex 处理

3. **统一索引方案**
   - 创建统一的 MCP 服务器
   - 支持多种文件格式
   - 自动检测和转换

需要我帮你实现代码索引的具体方案吗？🚀
