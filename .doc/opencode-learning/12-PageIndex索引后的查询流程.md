# PageIndex 索引后的查询流程

## 🤔 你的疑问

**问题**：代码首次被 index 过之后，再次查询是怎样的流程？

**答案**：不需要重新索引！直接查询已生成的树结构文件。

---

## 📊 完整流程对比

### 首次索引流程

```
用户: "索引我的代码 ~/myproject/src"
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. OpenCode 调用 MCP 工具                                │
│    工具: pageindex-code_index_code                       │
│    参数: { code_dir: "~/myproject/src" }                │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. MCP 服务器执行索引                                    │
│    mcp_server_enhanced.py                                │
│                                                          │
│    async def index_code(args):                           │
│      # 2.1 转换代码为 Markdown                           │
│      subprocess.run([                                    │
│        "python3", "code_to_markdown.py",                 │
│        "-i", "~/myproject/src",                          │
│        "-o", "/tmp/code_docs"                            │
│      ])                                                  │
│                                                          │
│      # 2.2 索引每个 Markdown 文件                        │
│      for md_file in md_files:                            │
│        subprocess.run([                                  │
│          "python3", "run_pageindex.py",                  │
│          "--md_path", md_file                            │
│        ])                                                │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. PageIndex 生成树结构文件                              │
│    ~/pageindex-enterprise/PageIndex/results/             │
│                                                          │
│    生成的文件:                                           │
│    ├── UserService.java.json                            │
│    ├── AuthManager.kt.json                              │
│    ├── LoginActivity.java.json                          │
│    └── ...                                               │
│                                                          │
│    每个文件包含:                                         │
│    {                                                     │
│      "title": "UserService.java",                       │
│      "nodes": [                                          │
│        {                                                 │
│          "title": "Class: UserService",                 │
│          "line": 10,                                     │
│          "nodes": [                                      │
│            {                                             │
│              "title": "Method: login",                  │
│              "line": 45,                                 │
│              "description": "用户登录方法"               │
│            }                                             │
│          ]                                               │
│        }                                                 │
│      ]                                                   │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
```

---

### 后续查询流程（无需重新索引）

```
用户: "查询用户认证相关的代码"
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. OpenCode 调用 MCP 工具                                │
│    工具: pageindex-code_query_code                       │
│    参数: { query: "用户认证" }                           │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. MCP 服务器执行查询                                    │
│    mcp_server_enhanced.py                                │
│                                                          │
│    async def query_code(args):                           │
│      query = args["query"]  # "用户认证"                 │
│      results = []                                        │
│                                                          │
│      # 2.1 遍历所有已索引的 JSON 文件                    │
│      for json_file in RESULTS_DIR.rglob("*.json"):      │
│        # 2.2 读取树结构                                  │
│        with open(json_file) as f:                        │
│          tree = json.load(f)                             │
│                                                          │
│        # 2.3 递归搜索树结构                              │
│        matches = search_tree(tree, query)                │
│        if matches:                                       │
│          results.extend(matches)                         │
│                                                          │
│      # 2.4 格式化结果                                    │
│      return format_results(results)                      │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 搜索树结构（递归）                                    │
│                                                          │
│    def search_tree(node, query):                         │
│      results = []                                        │
│      query_lower = query.lower()                         │
│                                                          │
│      # 检查当前节点                                      │
│      if query_lower in node["title"].lower():            │
│        results.append(node)                              │
│                                                          │
│      if query_lower in node.get("description", ""):      │
│        results.append(node)                              │
│                                                          │
│      # 递归搜索子节点                                    │
│      for child in node.get("nodes", []):                 │
│        results.extend(search_tree(child, query))         │
│                                                          │
│      return results                                      │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 返回搜索结果                                          │
│                                                          │
│    🔍 找到 3 个相关结果:                                 │
│                                                          │
│    1. **Class: UserAuthManager**                        │
│       文件: `auth/UserAuthManager.kt`                   │
│       行号: 15                                           │
│       描述: 用户认证管理器                               │
│                                                          │
│    2. **Method: authenticateUser**                      │
│       文件: `auth/AuthUtils.kt`                         │
│       行号: 45                                           │
│       描述: 验证用户凭证                                 │
│                                                          │
│    3. **Class: LoginActivity**                          │
│       文件: `ui/LoginActivity.java`                     │
│       行号: 28                                           │
│       描述: 用户登录界面                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 关键区别

### 首次索引 vs 后续查询

| 操作                   | 首次索引                | 后续查询        |
| ---------------------- | ----------------------- | --------------- |
| **触发工具**           | `index_code`            | `query_code`    |
| **需要转换代码**       | ✅ 是                   | ❌ 否           |
| **需要调用 PageIndex** | ✅ 是                   | ❌ 否           |
| **需要调用大模型**     | ✅ 是（PageIndex 内部） | ❌ 否           |
| **操作对象**           | 源代码文件              | JSON 树结构文件 |
| **耗时**               | 1-5 分钟                | 1-2 秒          |
| **成本**               | 有（大模型调用）        | 无              |

---

## 💡 详细代码解析

### 查询代码实现 (mcp_server_enhanced.py)

```python
async def query_code(args: dict):
    """查询代码"""
    query = args["query"]  # 用户查询内容
    file_pattern = args.get("file_pattern")  # 可选的文件名过滤

    # 搜索所有索引文件
    results = []

    # 遍历所有 JSON 文件
    for json_file in RESULTS_DIR.rglob("*.json"):
        try:
            # 读取树结构
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


def search_tree(node: dict, query: str, results: list = None, file: str = None) -> list:
    """递归搜索树结构"""
    if results is None:
        results = []
        file = node.get("title", "unknown")

    query_lower = query.lower()

    # 检查当前节点
    title = node.get("title", "").lower()
    description = node.get("description", "").lower()

    # 如果标题或描述包含查询词
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
```

---

## 🎯 实际使用示例

### 场景 1: 首次索引

```bash
用户: 索引我的 Android 项目 ~/MyApp/app/src/main

OpenCode:
[调用 index_code]
✅ 代码索引完成！

**代码目录**: ~/MyApp/app/src/main
**文件类型**: .java, .kt
**索引成功**: 127 个文件
**索引失败**: 0 个文件

生成的文件:
~/pageindex-enterprise/PageIndex/results/
├── MainActivity.java.json
├── UserViewModel.kt.json
├── UserRepository.kt.json
├── LoginActivity.java.json
└── ... (共 127 个文件)
```

### 场景 2: 查询（无需重新索引）

```bash
用户: 查询用户认证相关的代码

OpenCode:
[调用 query_code]
🔍 找到 8 个相关结果:

1. **Class: UserAuthManager**
   文件: `auth/UserAuthManager.kt`
   行号: 15
   类型: class
   描述: 用户认证管理器，处理登录、注册、令牌验证

2. **Method: authenticateUser**
   文件: `auth/AuthUtils.kt`
   行号: 45
   类型: method
   描述: 验证用户凭证，返回认证令牌

3. **Class: LoginActivity**
   文件: `ui/LoginActivity.java`
   行号: 28
   类型: class
   描述: 用户登录界面

4. **Method: login**
   文件: `viewmodel/LoginViewModel.kt`
   行号: 32
   类型: method
   描述: 处理用户登录逻辑

... 还有 4 个结果
```

### 场景 3: 带文件过滤的查询

```bash
用户: 在 ViewModel 相关文件中查询用户数据

OpenCode:
[调用 query_code，参数: query="用户数据", file_pattern="ViewModel"]
🔍 找到 3 个相关结果:

1. **Property: userData (val)**
   文件: `UserViewModel.kt`
   行号: 25
   类型: property

2. **Function: loadUserData**
   文件: `UserViewModel.kt`
   行号: 30
   类型: function
   描述: 加载用户数据

3. **Function: updateUserData**
   文件: `ProfileViewModel.kt`
   行号: 45
   类型: function
   描述: 更新用户数据
```

---

## 📁 索引文件结构

### 生成的 JSON 文件示例

**UserService.java.json**:

```json
{
  "title": "UserService.java",
  "type": "java",
  "package": "com.example.myapp.service",
  "imports": ["com.example.myapp.repository.UserRepository", "com.example.myapp.model.User", "java.util.List"],
  "nodes": [
    {
      "title": "Class: UserService",
      "type": "class",
      "line": 10,
      "extends": "BaseService",
      "implements": "IUserService",
      "nodes": [
        {
          "title": "Field: userRepository",
          "type": "field",
          "line": 12
        },
        {
          "title": "Constructor: UserService",
          "type": "method",
          "line": 14,
          "modifiers": "public"
        },
        {
          "title": "Method: login",
          "type": "method",
          "line": 18,
          "modifiers": "public",
          "description": "用户登录方法"
        },
        {
          "title": "Method: register",
          "type": "method",
          "line": 25,
          "modifiers": "public",
          "description": "用户注册方法"
        },
        {
          "title": "Method: validateUser",
          "type": "method",
          "line": 32,
          "modifiers": "private",
          "description": "验证用户信息"
        }
      ]
    }
  ]
}
```

---

## 🔄 更新索引流程

### 代码修改后如何更新？

**方案 1: 重新索引整个目录**

```bash
用户: 重新索引 ~/MyApp/app/src/main

OpenCode:
[调用 index_code]
✅ 代码索引完成！
**索引成功**: 127 个文件

# 会覆盖之前的索引文件
```

**方案 2: 只索引修改的文件**

```bash
用户: 索引文件 ~/MyApp/app/src/main/java/UserService.java

OpenCode:
[调用 index_document]
✅ 文档索引完成！
**文件**: UserService.java
**树结构**: UserService.java.json

# 只更新这一个文件的索引
```

**方案 3: 自动监控（未实现，可扩展）**

```python
# 可以添加文件监控
import watchdog

def on_file_modified(event):
    if event.src_path.endswith(('.java', '.kt')):
        # 自动重新索引修改的文件
        index_file(event.src_path)
```

---

## ⚡ 性能对比

### 首次索引

```
操作: 索引 100 个 Java/Kotlin 文件
时间: 2-5 分钟
步骤:
  1. 转换代码为 Markdown: 30 秒
  2. PageIndex 分析 (调用大模型): 2-4 分钟
  3. 生成 JSON 文件: 10 秒
成本: 约 $0.50-2.00 (取决于模型)
```

### 后续查询

```
操作: 查询 "用户认证"
时间: 1-2 秒
步骤:
  1. 读取 JSON 文件: 0.5 秒
  2. 搜索树结构: 0.3 秒
  3. 格式化结果: 0.2 秒
成本: $0 (无需调用大模型)
```

---

## 💡 优化建议

### 1. 增量索引

```python
async def index_code_incremental(args):
    """增量索引：只索引新增或修改的文件"""
    code_dir = args["code_dir"]

    # 获取所有代码文件
    code_files = get_all_code_files(code_dir)

    # 检查哪些文件需要重新索引
    files_to_index = []
    for code_file in code_files:
        json_file = get_json_path(code_file)

        # 如果 JSON 不存在，或代码文件更新
        if not json_file.exists() or \
           code_file.stat().st_mtime > json_file.stat().st_mtime:
            files_to_index.append(code_file)

    # 只索引需要更新的文件
    for code_file in files_to_index:
        index_file(code_file)

    return f"✅ 增量索引完成！更新了 {len(files_to_index)} 个文件"
```

### 2. 缓存搜索结果

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_cached(query: str):
    """缓存常见查询的结果"""
    return query_code({"query": query})
```

### 3. 建立倒排索引

```python
def build_inverted_index():
    """建立倒排索引，加速搜索"""
    index = {}

    for json_file in RESULTS_DIR.rglob("*.json"):
        tree = json.load(json_file)

        # 提取所有关键词
        keywords = extract_keywords(tree)

        # 建立倒排索引
        for keyword in keywords:
            if keyword not in index:
                index[keyword] = []
            index[keyword].append(json_file)

    return index
```

---

## ✅ 总结

### 关键点

1. **首次索引**：
   - 转换代码 → Markdown
   - PageIndex 分析（调用大模型）
   - 生成 JSON 树结构文件
   - 耗时：2-5 分钟
   - 有成本

2. **后续查询**：
   - 直接搜索 JSON 文件
   - 无需调用大模型
   - 耗时：1-2 秒
   - 无成本

3. **更新索引**：
   - 重新索引整个目录
   - 或只索引修改的文件
   - 可以实现增量索引

### 优势

- ✅ **快速查询**：秒级响应
- ✅ **无额外成本**：查询不调用大模型
- ✅ **离线可用**：索引后可离线查询
- ✅ **精确匹配**：基于树结构的智能搜索

### 工作流程

```
第一天:
  索引代码 (5 分钟) → 生成 JSON 文件

之后每天:
  查询代码 (1 秒) → 直接搜索 JSON
  查询代码 (1 秒) → 直接搜索 JSON
  查询代码 (1 秒) → 直接搜索 JSON
  ...

代码修改后:
  重新索引 (5 分钟) → 更新 JSON 文件
```

这就是 PageIndex 索引后的查询流程！🎯
