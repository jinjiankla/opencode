# PageIndex 部署疑问解答

## 🤔 你的两个关键问题

### 问题 1: `run_pageindex.py` 在哪？

**答案**：在 PageIndex 仓库的根目录下。

#### 详细说明

```bash
# Step 1 中 Clone 的仓库结构
~/pageindex-enterprise/
└── PageIndex/                    # ← Clone 的仓库
    ├── run_pageindex.py         # ← 就在这里！
    ├── requirements.txt
    ├── pageindex/               # Python 包
    │   ├── __init__.py
    │   ├── tree_builder.py
    │   └── ...
    ├── tests/
    │   └── pdfs/
    └── results/                 # 生成的树结构保存在这里
```

**完整路径**：

```bash
~/pageindex-enterprise/PageIndex/run_pageindex.py
```

**验证**：

```bash
# 检查文件是否存在
ls ~/pageindex-enterprise/PageIndex/run_pageindex.py

# 应该输出：
# /Users/你的用户名/pageindex-enterprise/PageIndex/run_pageindex.py
```

---

### 问题 2: 为什么需要创建 MCP 包装服务器？不能像云端版一样直接配置吗？

**答案**：你的理解是对的！确实有更简单的方案。**不一定需要自己写代码！**

#### 关键区别

**云端版（方案 A）**：

```json
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["npx", "-y", "@pageindex/mcp"]
      // ↑ 这是一个现成的 npm 包
      // 它已经实现了 MCP 服务器
      // 只是连接到 PageIndex 云端
    }
  }
}
```

**企业内网版（你的需求）**：

```json
{
  "mcp": {
    "pageindex-enterprise": {
      "type": "local",
      "command": ["???", "???"]
      // ↑ 问题：没有现成的包连接到你的内网大模型
      // 需要自己实现一个 MCP 服务器
    }
  }
}
```

---

## 💡 更简单的方案

### 方案对比

| 方案                            | 难度     | 需要写代码 | 说明               |
| ------------------------------- | -------- | ---------- | ------------------ |
| **方案 A: 使用官方 MCP**        | ⭐       | ❌ 不需要  | 连接云端，数据上传 |
| **方案 B: 自己写 MCP 服务器**   | ⭐⭐⭐⭐ | ✅ 需要    | 完全自定义，复杂   |
| **方案 C: 使用 Python MCP SDK** | ⭐⭐     | ⚠️ 少量    | 推荐！简单很多     |
| **方案 D: 直接调用 Python**     | ⭐⭐⭐   | ⚠️ 中等    | 不推荐，绕过 MCP   |

---

## 🚀 推荐方案 C：使用 Python MCP SDK

**好消息**：PageIndex 官方可能会提供 Python MCP 服务器，或者我们用 Python MCP SDK 快速实现。

### Step 1: 安装 Python MCP SDK

```bash
cd ~/pageindex-enterprise
pip3 install mcp
```

### Step 2: 创建简化的 Python MCP 服务器

创建文件 `~/pageindex-enterprise/mcp_server.py`：

```python
#!/usr/bin/env python3
"""
PageIndex MCP Server for Enterprise
连接到公司内网大模型
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 配置
PAGEINDEX_DIR = Path(__file__).parent / "PageIndex"
RESULTS_DIR = PAGEINDEX_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# 创建 MCP 服务器
app = Server("pageindex-enterprise")

@app.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        {
            "name": "analyze_pdf",
            "description": "分析 PDF 文档，生成层级树结构索引",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "PDF 文件路径（本地路径或 URL）"
                    },
                    "model": {
                        "type": "string",
                        "description": "使用的模型名称",
                        "default": os.getenv("OPENAI_MODEL", "qwen-plus")
                    }
                },
                "required": ["pdf_path"]
            }
        },
        {
            "name": "list_documents",
            "description": "列出所有已分析的文档",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """执行工具"""

    if name == "analyze_pdf":
        pdf_path = arguments["pdf_path"]
        model = arguments.get("model", os.getenv("OPENAI_MODEL", "qwen-plus"))

        # 调用 PageIndex
        cmd = [
            "python3",
            str(PAGEINDEX_DIR / "run_pageindex.py"),
            "--pdf_path", pdf_path,
            "--model", model
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=PAGEINDEX_DIR,
                capture_output=True,
                text=True,
                timeout=600  # 10 分钟超时
            )

            if result.returncode == 0:
                # 提取生成的文件名
                output = result.stdout
                tree_file = "unknown"
                for line in output.split("\n"):
                    if "Tree saved to:" in line:
                        tree_file = line.split(":")[-1].strip()
                        break

                return [{
                    "type": "text",
                    "text": f"""✅ PDF 分析完成！

**文档**: {pdf_path}
**模型**: {model}
**树结构文件**: {tree_file}

已生成层级树结构，可以进行推理式检索。

{output}
"""
                }]
            else:
                return [{
                    "type": "text",
                    "text": f"❌ 分析失败:\n{result.stderr}"
                }]

        except subprocess.TimeoutExpired:
            return [{
                "type": "text",
                "text": "❌ 处理超时（超过 10 分钟）"
            }]
        except Exception as e:
            return [{
                "type": "text",
                "text": f"❌ 错误: {str(e)}"
            }]

    elif name == "list_documents":
        # 列出已分析的文档
        files = list(RESULTS_DIR.glob("*.json"))
        if not files:
            return [{
                "type": "text",
                "text": "📚 还没有分析过任何文档"
            }]

        file_list = "\n".join([f"{i+1}. {f.name}" for i, f in enumerate(files)])
        return [{
            "type": "text",
            "text": f"📚 已分析的文档 ({len(files)} 个):\n\n{file_list}"
        }]

    return [{"type": "text", "text": f"未知工具: {name}"}]

# 启动服务器
if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

**赋予执行权限**：

```bash
chmod +x ~/pageindex-enterprise/mcp_server.py
```

### Step 3: 配置 OpenCode（超简单！）

编辑 `~/.opencode/config.json`：

```json
{
  "mcp": {
    "pageindex-enterprise": {
      "type": "local",
      "command": ["python3", "/Users/你的用户名/pageindex-enterprise/mcp_server.py"],
      "environment": {
        "OPENAI_API_BASE": "http://internal-llm.company.com:8080/v1",
        "OPENAI_API_KEY": "sk-your-company-api-key",
        "OPENAI_MODEL": "qwen-plus"
      },
      "timeout": 120000
    }
  }
}
```

**就这么简单！** 不需要写复杂的 TypeScript 代码。

---

## 📊 方案对比详解

### 原教程方案（TypeScript MCP）

**优点**：

- ✅ 功能完整
- ✅ 性能好（Bun 运行时）
- ✅ 可以添加复杂逻辑

**缺点**：

- ❌ 需要学习 TypeScript
- ❌ 需要学习 MCP SDK
- ❌ 代码量大（200+ 行）
- ❌ 需要安装 Bun

### 新推荐方案（Python MCP）

**优点**：

- ✅ 代码简单（80 行）
- ✅ 使用 Python（与 PageIndex 一致）
- ✅ 不需要学习新语言
- ✅ 容易理解和修改

**缺点**：

- ⚠️ 需要安装 Python MCP SDK
- ⚠️ 性能略低（但足够用）

---

## 🎯 完整部署流程（简化版）

### 前置准备

```bash
# 1. 确认 Python 版本
python3 --version  # 需要 >= 3.8

# 2. 确认公司大模型信息
# - API 地址
# - API Key
# - 模型名称
```

### 部署步骤

```bash
# Step 1: 创建项目目录
mkdir -p ~/pageindex-enterprise
cd ~/pageindex-enterprise

# Step 2: Clone PageIndex
git clone https://github.com/VectifyAI/PageIndex.git

# Step 3: 安装依赖
cd PageIndex
pip3 install -r requirements.txt
cd ..

# Step 4: 安装 Python MCP SDK
pip3 install mcp

# Step 5: 创建 MCP 服务器
# 复制上面的 mcp_server.py 代码
cat > mcp_server.py << 'EOF'
[粘贴上面的 Python 代码]
EOF

chmod +x mcp_server.py

# Step 6: 配置环境变量
cat > .env << 'EOF'
OPENAI_API_BASE=http://internal-llm.company.com:8080/v1
OPENAI_API_KEY=sk-your-company-api-key
OPENAI_MODEL=qwen-plus
EOF

# Step 7: 测试 MCP 服务器
python3 mcp_server.py
# 应该启动成功（等待输入）
# Ctrl+C 退出

# Step 8: 配置 OpenCode
# 编辑 ~/.opencode/config.json
# 添加上面的配置

# Step 9: 验证
opencode mcp list
# 应该看到 pageindex-enterprise 状态为 connected
```

**总耗时**：30-60 分钟（比原方案简单很多）

---

## 🔍 为什么需要 MCP 包装服务器？

### 理解 MCP 的作用

```
┌─────────────────────────────────────────────────────┐
│              OpenCode CLI                           │
│  - 理解用户问题                                      │
│  - 决定调用哪个工具                                  │
│  - 只知道如何通过 MCP 协议调用工具                   │
└──────────────┬──────────────────────────────────────┘
               │ MCP 协议（标准化接口）
               │ - list_tools()
               │ - call_tool(name, args)
               │
┌──────────────▼──────────────────────────────────────┐
│           MCP 服务器（包装层）                       │
│  - 实现 MCP 协议                                     │
│  - 翻译 OpenCode 的调用 → PageIndex 的调用          │
│  - 处理错误、超时等                                  │
└──────────────┬──────────────────────────────────────┘
               │ 直接调用
               │
┌──────────────▼──────────────────────────────────────┐
│         PageIndex 核心（Python）                     │
│  - run_pageindex.py                                 │
│  - 处理 PDF                                          │
│  - 调用大模型                                        │
│  - 生成树结构                                        │
└─────────────────────────────────────────────────────┘
```

### 为什么不能直接配置？

**问题**：OpenCode 只理解 MCP 协议，不理解 PageIndex 的 Python 脚本。

```json
// ❌ 这样不行
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["python3", "run_pageindex.py", "--pdf_path", "???"]
      // 问题：
      // 1. OpenCode 不知道如何传递参数
      // 2. OpenCode 不知道如何解析返回结果
      // 3. 没有实现 MCP 协议
    }
  }
}
```

**解决方案**：需要一个"翻译层"（MCP 服务器）

```json
// ✅ 这样才行
{
  "mcp": {
    "pageindex": {
      "type": "local",
      "command": ["python3", "mcp_server.py"]
      // mcp_server.py 实现了：
      // 1. MCP 协议（OpenCode 能理解）
      // 2. 调用 run_pageindex.py（内部实现）
      // 3. 处理参数和返回值
    }
  }
}
```

---

## 💡 类比理解

### 类比 1: 餐厅点餐

```
你（OpenCode）想吃饭，但：
- 你只会说英语（MCP 协议）
- 厨师只会说中文（PageIndex Python 脚本）

解决方案：
- 服务员（MCP 服务器）会双语
- 你用英语点餐 → 服务员翻译成中文 → 厨师做菜
- 厨师做好 → 服务员端给你
```

### 类比 2: USB 转接头

```
你的电脑（OpenCode）：只有 USB-C 接口（MCP 协议）
你的设备（PageIndex）：只有 USB-A 接口（Python 脚本）

解决方案：
- USB 转接头（MCP 服务器）
- 一端是 USB-C（对接 OpenCode）
- 一端是 USB-A（对接 PageIndex）
```

---

## 🆚 云端版 vs 企业版对比

### 云端版（方案 A）

```
OpenCode
  ↓ MCP
@pageindex/mcp（npm 包，现成的）
  ↓ HTTP
PageIndex 云端服务
  ↓
GPT-4o（OpenAI）
```

**特点**：

- ✅ 一行配置
- ✅ 不需要写代码
- ❌ 数据上传到云端
- ❌ 需要付费

### 企业版（你的需求）

```
OpenCode
  ↓ MCP
mcp_server.py（需要自己创建）
  ↓ subprocess
PageIndex 核心（本地）
  ↓ HTTP
公司内网大模型
```

**特点**：

- ⚠️ 需要创建 MCP 服务器（但很简单）
- ✅ 数据不出内网
- ✅ 无额外费用
- ✅ 完全可控

---

## ✅ 总结

### 回答你的两个问题

**问题 1: `run_pageindex.py` 在哪？**

```bash
~/pageindex-enterprise/PageIndex/run_pageindex.py
# 在 Clone 的仓库根目录下
```

**问题 2: 为什么需要创建 MCP 服务器？**

**简答**：

- OpenCode 只理解 MCP 协议
- PageIndex 是 Python 脚本
- 需要一个"翻译层"连接两者

**好消息**：

- ✅ 不需要写复杂的 TypeScript
- ✅ 用 Python 写很简单（80 行）
- ✅ 我已经提供了完整代码

### 推荐方案

**使用 Python MCP 服务器**（方案 C）：

1. 代码简单（80 行 Python）
2. 容易理解和修改
3. 与 PageIndex 语言一致
4. 30-60 分钟完成部署

### 下一步

需要我帮你：

1. **完善 Python MCP 服务器代码**？
2. **一步步指导部署**？
3. **解决具体问题**？

告诉我你想从哪里开始！🚀
