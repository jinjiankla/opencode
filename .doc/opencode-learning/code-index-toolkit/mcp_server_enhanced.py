#!/usr/bin/env python3
"""
增强的 MCP 服务器
支持代码索引和查询
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 配置
PAGEINDEX_DIR = Path(os.getenv("PAGEINDEX_PATH", Path.home() / "pageindex-enterprise/PageIndex"))
RESULTS_DIR = PAGEINDEX_DIR / "results"
CODE_TOOLKIT_DIR = Path(__file__).parent
RESULTS_DIR.mkdir(exist_ok=True)

# 创建 MCP 服务器
app = Server("pageindex-code-enhanced")


@app.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        {
            "name": "index_code",
            "description": "索引代码目录，支持 Python, JavaScript, TypeScript",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code_dir": {
                        "type": "string",
                        "description": "代码目录路径"
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "文件扩展名列表（可选）",
                        "default": [".java", ".kt", ".py"]
                    }
                },
                "required": ["code_dir"]
            }
        },
        {
            "name": "index_document",
            "description": "索引文档（PDF 或 Markdown）",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "文件路径"
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["pdf", "md", "auto"],
                        "description": "文件类型",
                        "default": "auto"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "query_code",
            "description": "查询代码库中的函数、类等",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询内容（如：用户认证、数据库连接）"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "文件名模式（可选）"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "list_indexed",
            "description": "列出所有已索引的文件",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "过滤条件（可选）"
                    }
                }
            }
        }
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """执行工具"""
    
    if name == "index_code":
        return await index_code(arguments)
    elif name == "index_document":
        return await index_document(arguments)
    elif name == "query_code":
        return await query_code(arguments)
    elif name == "list_indexed":
        return await list_indexed(arguments)
    
    return [{"type": "text", "text": f"未知工具: {name}"}]


async def index_code(args: dict):
    """索引代码目录"""
    code_dir = args["code_dir"]
    extensions = args.get("extensions", [".java", ".kt", ".py"])
    
    if not os.path.isdir(code_dir):
        return [{
            "type": "text",
            "text": f"❌ 目录不存在: {code_dir}"
        }]
    
    # 临时目录用于存放转换后的 Markdown
    docs_dir = RESULTS_DIR / "code_docs"
    docs_dir.mkdir(exist_ok=True)
    
    # 转换代码为 Markdown
    cmd = [
        "python3",
        str(CODE_TOOLKIT_DIR / "code_to_markdown.py"),
        "-i", code_dir,
        "-o", str(docs_dir),
        "-e", *extensions
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return [{
                "type": "text",
                "text": f"❌ 代码转换失败:\n{result.stderr}"
            }]
        
        # 索引所有生成的 Markdown
        md_files = list(docs_dir.rglob("*.md"))
        success_count = 0
        fail_count = 0
        
        for md_file in md_files:
            index_result = subprocess.run(
                [
                    "python3",
                    str(PAGEINDEX_DIR / "run_pageindex.py"),
                    "--md_path", str(md_file)
                ],
                capture_output=True,
                text=True,
                cwd=PAGEINDEX_DIR
            )
            
            if index_result.returncode == 0:
                success_count += 1
            else:
                fail_count += 1
        
        return [{
            "type": "text",
            "text": f"""✅ 代码索引完成！

**代码目录**: {code_dir}
**文件类型**: {', '.join(extensions)}
**索引成功**: {success_count} 个文件
**索引失败**: {fail_count} 个文件

现在可以使用 `query_code` 工具查询代码了。
"""
        }]
    
    except subprocess.TimeoutExpired:
        return [{
            "type": "text",
            "text": "❌ 索引超时（超过 5 分钟）"
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"❌ 错误: {str(e)}"
        }]


async def index_document(args: dict):
    """索引文档"""
    file_path = args["file_path"]
    file_type = args.get("file_type", "auto")
    
    if not os.path.isfile(file_path):
        return [{
            "type": "text",
            "text": f"❌ 文件不存在: {file_path}"
        }]
    
    # 自动检测文件类型
    if file_type == "auto":
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            file_type = "pdf"
        elif ext == ".md":
            file_type = "md"
        else:
            return [{
                "type": "text",
                "text": f"❌ 不支持的文件类型: {ext}"
            }]
    
    # 调用 PageIndex
    if file_type == "pdf":
        flag = "--pdf_path"
    else:
        flag = "--md_path"
    
    try:
        result = subprocess.run(
            [
                "python3",
                str(PAGEINDEX_DIR / "run_pageindex.py"),
                flag, file_path
            ],
            capture_output=True,
            text=True,
            cwd=PAGEINDEX_DIR,
            timeout=600
        )
        
        if result.returncode == 0:
            # 提取树文件名
            tree_file = "unknown"
            for line in result.stdout.split("\n"):
                if "Tree saved to:" in line:
                    tree_file = line.split(":")[-1].strip()
                    break
            
            return [{
                "type": "text",
                "text": f"""✅ 文档索引完成！

**文件**: {file_path}
**类型**: {file_type.upper()}
**树结构**: {tree_file}

{result.stdout}
"""
            }]
        else:
            return [{
                "type": "text",
                "text": f"❌ 索引失败:\n{result.stderr}"
            }]
    
    except subprocess.TimeoutExpired:
        return [{
            "type": "text",
            "text": "❌ 索引超时（超过 10 分钟）"
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"❌ 错误: {str(e)}"
        }]


async def query_code(args: dict):
    """查询代码"""
    query = args["query"]
    file_pattern = args.get("file_pattern")
    
    # 搜索所有索引文件
    results = []
    
    for json_file in RESULTS_DIR.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                tree = json.load(f)
            
            # 如果有文件名过滤
            if file_pattern and file_pattern not in tree.get("title", ""):
                continue
            
            # 搜索树结构
            matches = search_tree(tree, query)
            if matches:
                results.extend(matches)
        
        except Exception:
            continue
    
    if not results:
        return [{
            "type": "text",
            "text": f"🔍 未找到与 '{query}' 相关的代码"
        }]
    
    # 格式化结果
    output = [f"🔍 找到 {len(results)} 个相关结果:\n"]
    
    for i, match in enumerate(results[:10], 1):  # 最多显示 10 个
        output.append(f"\n{i}. **{match['title']}**")
        if "file" in match:
            output.append(f"   文件: `{match['file']}`")
        if "line" in match:
            output.append(f"   行号: {match['line']}")
        if "description" in match:
            desc = match['description'][:100]
            output.append(f"   描述: {desc}...")
    
    if len(results) > 10:
        output.append(f"\n... 还有 {len(results) - 10} 个结果")
    
    return [{
        "type": "text",
        "text": "\n".join(output)
    }]


async def list_indexed(args: dict):
    """列出已索引文件"""
    filter_str = args.get("filter", "")
    
    files = []
    for json_file in RESULTS_DIR.rglob("*.json"):
        filename = json_file.name
        if filter_str and filter_str not in filename:
            continue
        
        # 获取文件大小和修改时间
        stat = json_file.stat()
        size = stat.st_size
        mtime = stat.st_mtime
        
        files.append({
            "name": filename,
            "size": size,
            "mtime": mtime
        })
    
    if not files:
        return [{
            "type": "text",
            "text": "📚 还没有索引任何文件"
        }]
    
    # 按修改时间排序
    files.sort(key=lambda x: x["mtime"], reverse=True)
    
    output = [f"📚 已索引 {len(files)} 个文件:\n"]
    
    for i, f in enumerate(files[:20], 1):
        size_kb = f["size"] / 1024
        output.append(f"{i}. `{f['name']}` ({size_kb:.1f} KB)")
    
    if len(files) > 20:
        output.append(f"\n... 还有 {len(files) - 20} 个文件")
    
    return [{
        "type": "text",
        "text": "\n".join(output)
    }]


def search_tree(node: dict, query: str, results: list = None, file: str = None) -> list:
    """递归搜索树结构"""
    if results is None:
        results = []
        file = node.get("title", "unknown")
    
    query_lower = query.lower()
    
    # 检查当前节点
    title = node.get("title", "").lower()
    description = node.get("description", "").lower()
    
    if query_lower in title or query_lower in description:
        results.append({
            "title": node.get("title", ""),
            "file": file,
            "line": node.get("line"),
            "description": node.get("description", ""),
            "type": node.get("type", "")
        })
    
    # 递归搜索子节点
    for child in node.get("nodes", []):
        search_tree(child, query, results, file)
    
    return results


# 启动服务器
if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
