# 代码索引工具包 - 使用指南

## 📦 工具包内容

这个工具包包含了完整的代码索引解决方案：

```
code-index-toolkit/
├── code_to_markdown.py       # 代码转 Markdown 工具
├── index_codebase.sh          # 自动化索引脚本
├── mcp_server_enhanced.py     # 增强的 MCP 服务器
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 前置要求

1. **已部署 PageIndex**

   ```bash
   # 确认 PageIndex 已安装
   ls ~/pageindex-enterprise/PageIndex/run_pageindex.py
   ```

2. **Python 依赖**

   ```bash
   pip3 install mcp
   ```

3. **配置环境变量**
   ```bash
   export PAGEINDEX_PATH=~/pageindex-enterprise/PageIndex
   ```

---

## 📝 使用方式

### 方式 1: 命令行工具（快速测试）

#### 1.1 转换单个文件

```bash
cd /Users/desire/Desktop/Code/Github/opencode/.doc/opencode-learning/code-index-toolkit

# 转换 Python 文件
python3 code_to_markdown.py -i ~/myproject/app.py -o ~/myproject/docs/app.md

# 转换 JavaScript 文件
python3 code_to_markdown.py -i ~/myproject/index.js -o ~/myproject/docs/index.md
```

#### 1.2 转换整个目录

```bash
# 转换所有 Python 文件
python3 code_to_markdown.py -i ~/myproject/src -o ~/myproject/docs/code

# 转换 Python 和 JavaScript
python3 code_to_markdown.py \
  -i ~/myproject/src \
  -o ~/myproject/docs/code \
  -e .py .js .ts
```

#### 1.3 一键索引代码库

```bash
# 赋予执行权限
chmod +x index_codebase.sh

# 索引代码库
./index_codebase.sh ~/myproject/src ~/myproject/docs/code

# 查看索引报告
cat ~/pageindex-enterprise/PageIndex/results/index_report.md
```

---

### 方式 2: 通过 OpenCode（推荐）

#### 2.1 配置 OpenCode

编辑 `~/.opencode/config.json`:

```json
{
  "mcp": {
    "pageindex-code": {
      "type": "local",
      "command": [
        "python3",
        "/Users/你的用户名/Desktop/Code/Github/opencode/.doc/opencode-learning/code-index-toolkit/mcp_server_enhanced.py"
      ],
      "environment": {
        "PAGEINDEX_PATH": "/Users/你的用户名/pageindex-enterprise/PageIndex",
        "OPENAI_API_BASE": "http://internal-llm.company.com/v1",
        "OPENAI_API_KEY": "sk-company-key",
        "OPENAI_MODEL": "qwen-plus"
      },
      "timeout": 300000
    }
  }
}
```

#### 2.2 验证配置

```bash
opencode mcp list

# 应该看到：
# ┌─────────────────┬───────────┬──────────┐
# │ Name            │ Status    │ Type     │
# ├─────────────────┼───────────┼──────────┤
# │ pageindex-code  │ connected │ local    │
# └─────────────────┴───────────┴──────────┘
```

#### 2.3 在 OpenCode 中使用

```bash
opencode
```

**示例对话**：

```
用户: 索引我的代码库 ~/myproject/src

OpenCode:
[调用 pageindex-code_index_code 工具]
✅ 代码索引完成！

**代码目录**: ~/myproject/src
**文件类型**: .py, .js, .ts
**索引成功**: 45 个文件
**索引失败**: 0 个文件

现在可以使用 `query_code` 工具查询代码了。

─────────────────────────────────────

用户: 查询用户认证相关的代码

OpenCode:
[调用 pageindex-code_query_code 工具]
🔍 找到 8 个相关结果:

1. **Class: UserAuthService**
   文件: `auth/user_auth.py`
   行号: 15
   描述: 用户认证服务，处理登录、注册、权限验证...

2. **Function: authenticate_user**
   文件: `auth/utils.py`
   行号: 42
   描述: 验证用户凭证，返回认证令牌...

3. **Method: login**
   文件: `api/auth_controller.py`
   行号: 28
   描述: 用户登录接口...

...

─────────────────────────────────────

用户: 显示 UserAuthService 类的详细信息

OpenCode:
根据索引，UserAuthService 类位于 `auth/user_auth.py` 第 15 行。

该类包含以下方法：
- `__init__`: 初始化认证服务
- `login(username, password)`: 用户登录
- `register(user_data)`: 用户注册
- `verify_token(token)`: 验证令牌
- `logout(user_id)`: 用户登出

详细实现请查看源文件。
```

---

## 🛠️ 可用工具

### 1. `index_code` - 索引代码目录

**功能**：将代码目录转换为 Markdown 并索引

**参数**：

- `code_dir` (必需): 代码目录路径
- `extensions` (可选): 文件扩展名列表，默认 `[".py", ".js", ".ts"]`

**示例**：

```
索引 ~/myproject/src 目录
索引 ~/myproject/backend 目录，只处理 Python 文件
```

---

### 2. `index_document` - 索引文档

**功能**：索引 PDF 或 Markdown 文档

**参数**：

- `file_path` (必需): 文件路径
- `file_type` (可选): 文件类型 (`pdf`, `md`, `auto`)

**示例**：

```
索引文档 ~/Documents/api-spec.pdf
索引 ~/docs/architecture.md
```

---

### 3. `query_code` - 查询代码

**功能**：在已索引的代码中搜索

**参数**：

- `query` (必需): 查询内容
- `file_pattern` (可选): 文件名模式

**示例**：

```
查询用户认证相关的代码
查询数据库连接的实现
在 auth 相关文件中查询登录功能
```

---

### 4. `list_indexed` - 列出已索引文件

**功能**：显示所有已索引的文件

**参数**：

- `filter` (可选): 过滤条件

**示例**：

```
列出所有已索引的文件
列出包含 "auth" 的索引文件
```

---

## 📊 支持的语言

### 完全支持

| 语言           | 扩展名        | 解析内容                                  |
| -------------- | ------------- | ----------------------------------------- |
| **Python**     | `.py`         | 类、函数、方法、docstring、参数、返回类型 |
| **JavaScript** | `.js`, `.jsx` | 类、函数、方法（简化）                    |
| **TypeScript** | `.ts`, `.tsx` | 类、函数、方法（简化）                    |

### 计划支持

- Java (`.java`)
- Go (`.go`)
- Rust (`.rs`)
- C++ (`.cpp`, `.h`)

---

## 🎯 实际应用场景

### 场景 1: 新员工了解代码库

```
新员工: 我想了解这个项目的用户认证是怎么实现的

OpenCode:
[自动索引代码库]
[查询认证相关代码]

找到以下关键组件：

1. **UserAuthService** (auth/user_auth.py)
   - 核心认证服务
   - 处理登录、注册、令牌验证

2. **AuthMiddleware** (middleware/auth.py)
   - 请求认证中间件
   - 验证每个请求的令牌

3. **login API** (api/auth_controller.py)
   - 登录接口实现
   - 返回 JWT 令牌

建议从 UserAuthService 开始阅读。
```

---

### 场景 2: 重构代码前的影响分析

```
开发者: 如果我要修改 DatabaseConnection 类，会影响哪些地方？

OpenCode:
[查询 DatabaseConnection]
[分析依赖关系]

DatabaseConnection 类被以下组件使用：

1. UserRepository (repositories/user_repo.py)
2. OrderRepository (repositories/order_repo.py)
3. ProductService (services/product_service.py)
4. DataMigration (scripts/migrate.py)

共 4 个文件，建议修改前：
1. 确保向后兼容
2. 更新所有调用点
3. 添加单元测试
```

---

### 场景 3: 查找最佳实践

````
开发者: 项目中是怎么处理错误的？

OpenCode:
[查询错误处理相关代码]

项目使用以下错误处理模式：

1. **自定义异常** (exceptions/custom_errors.py)
   - ValidationError
   - AuthenticationError
   - DatabaseError

2. **全局错误处理器** (middleware/error_handler.py)
   - 捕获所有异常
   - 返回统一格式的错误响应

3. **示例用法** (services/user_service.py, Line 45)
   ```python
   if not user:
       raise AuthenticationError("用户不存在")
````

建议遵循这个模式。

````

---

## 🔧 高级配置

### 自定义文件类型支持

编辑 `code_to_markdown.py`，添加新的解析器：

```python
class JavaParser(CodeParser):
    """Java 代码解析器"""

    def parse(self, code: str, filename: str) -> Dict:
        # 实现 Java 解析逻辑
        pass

# 在 get_parser 函数中注册
def get_parser(filename: str) -> Optional[CodeParser]:
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.py':
        return PythonParser()
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return JavaScriptParser()
    elif ext == '.java':  # 新增
        return JavaParser()
    else:
        return None
````

---

### 定时自动索引

创建定时任务，每天自动索引代码库：

```bash
# 编辑 crontab
crontab -e

# 添加任务（每天凌晨 2 点）
0 2 * * * cd /path/to/code-index-toolkit && ./index_codebase.sh ~/myproject/src ~/myproject/docs/code
```

---

### 集成到 CI/CD

在 `.github/workflows/index-code.yml`:

```yaml
name: Index Codebase

on:
  push:
    branches: [main]

jobs:
  index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"

      - name: Install PageIndex
        run: |
          git clone https://github.com/VectifyAI/PageIndex.git
          pip install -r PageIndex/requirements.txt

      - name: Index Code
        run: |
          cd code-index-toolkit
          ./index_codebase.sh ../src ../docs/code

      - name: Upload Index
        uses: actions/upload-artifact@v2
        with:
          name: code-index
          path: docs/code/
```

---

## 🐛 故障排查

### 问题 1: 转换失败

```bash
# 检查 Python 版本
python3 --version  # 需要 >= 3.8

# 测试单个文件
python3 code_to_markdown.py -i test.py -o test.md

# 查看详细错误
python3 code_to_markdown.py -i test.py -o test.md 2>&1 | tee error.log
```

### 问题 2: MCP 服务器连接失败

```bash
# 检查路径
ls /Users/你的用户名/Desktop/Code/Github/opencode/.doc/opencode-learning/code-index-toolkit/mcp_server_enhanced.py

# 手动测试
python3 mcp_server_enhanced.py

# 查看 OpenCode 日志
opencode mcp debug pageindex-code
```

### 问题 3: 索引超时

```bash
# 增加超时时间
# 在 config.json 中
{
  "mcp": {
    "pageindex-code": {
      "timeout": 600000  // 10 分钟
    }
  }
}
```

---

## 📚 示例项目

### 完整工作流程

```bash
# 1. 准备代码库
cd ~/myproject

# 2. 索引代码
cd /path/to/code-index-toolkit
./index_codebase.sh ~/myproject/src ~/myproject/docs/code

# 3. 启动 OpenCode
opencode

# 4. 查询代码
```

**OpenCode 对话**：

````
用户: 这个项目的主要组件有哪些？

OpenCode: [分析索引]
主要组件包括：

1. **认证模块** (auth/)
   - UserAuthService: 用户认证
   - JWTManager: 令牌管理

2. **数据访问层** (repositories/)
   - UserRepository: 用户数据
   - OrderRepository: 订单数据

3. **业务逻辑** (services/)
   - UserService: 用户业务
   - OrderService: 订单业务

4. **API 层** (api/)
   - AuthController: 认证接口
   - UserController: 用户接口

─────────────────────────────────────

用户: UserService 是怎么使用 UserRepository 的？

OpenCode: [查询相关代码]
UserService 通过依赖注入使用 UserRepository：

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user(self, user_id):
        return self.user_repo.find_by_id(user_id)
````

这是典型的依赖注入模式，便于测试和解耦。

```

---

## ✅ 总结

### 工具包提供

1. ✅ **代码转 Markdown** (`code_to_markdown.py`)
2. ✅ **自动化索引** (`index_codebase.sh`)
3. ✅ **增强 MCP 服务器** (`mcp_server_enhanced.py`)
4. ✅ **完整文档** (本文件)

### 支持的功能

- ✅ 索引 Python, JavaScript, TypeScript 代码
- ✅ 索引 PDF, Markdown 文档
- ✅ 智能代码查询
- ✅ 通过 OpenCode CLI 使用
- ✅ 命令行工具
- ✅ 自动化脚本

### 下一步

1. **测试工具**：转换一个小文件试试
2. **索引代码库**：索引你的项目
3. **配置 OpenCode**：集成到工作流
4. **开始使用**：通过 OpenCode 查询代码

---

需要帮助？查看故障排查部分或联系我！🚀
```
