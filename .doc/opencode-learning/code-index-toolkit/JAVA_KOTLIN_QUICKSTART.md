# Java/Kotlin 代码索引 - 快速开始

## 🎯 专为 Java 和 Kotlin 优化

这个工具包已经针对 **Java 和 Kotlin** 代码进行了优化配置。

---

## 🚀 5 分钟快速开始

### Step 1: 测试单个文件

```bash
cd /Users/desire/Desktop/Code/Github/opencode/.doc/opencode-learning/code-index-toolkit

# 测试 Java 文件
python3 code_to_markdown.py \
  -i ~/your-project/src/main/java/com/example/UserService.java \
  -o ~/test-output/UserService.md

# 测试 Kotlin 文件
python3 code_to_markdown.py \
  -i ~/your-project/src/main/kotlin/com/example/UserRepository.kt \
  -o ~/test-output/UserRepository.md

# 查看生成的 Markdown
cat ~/test-output/UserService.md
```

### Step 2: 索引整个项目

```bash
# 索引 Java + Kotlin 项目
./index_codebase.sh \
  ~/your-android-project/app/src/main \
  ~/your-android-project/docs/code

# 查看索引报告
cat ~/pageindex-enterprise/PageIndex/results/index_report.md
```

### Step 3: 配置 OpenCode

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

### Step 4: 开始使用

```bash
opencode
```

**示例对话**：

```
用户: 索引我的 Android 项目 ~/MyApp/app/src/main

OpenCode:
[调用 index_code 工具]
✅ 代码索引完成！

**代码目录**: ~/MyApp/app/src/main
**文件类型**: .java, .kt
**索引成功**: 127 个文件
**索引失败**: 0 个文件

─────────────────────────────────────

用户: 查询用户认证相关的代码

OpenCode:
🔍 找到 12 个相关结果:

1. **Class: UserAuthManager**
   文件: `auth/UserAuthManager.kt`
   行号: 15
   修饰符: public
   继承: BaseAuthManager

2. **Class: LoginActivity**
   文件: `ui/LoginActivity.java`
   行号: 28
   继承: AppCompatActivity

3. **Function: authenticateUser**
   文件: `auth/AuthUtils.kt`
   行号: 45
   修饰符: suspend

...
```

---

## 📊 Java 解析器支持的特性

### 识别的元素

- ✅ **Package 声明**
- ✅ **Import 语句**
- ✅ **类 (Class)**
- ✅ **接口 (Interface)**
- ✅ **枚举 (Enum)**
- ✅ **方法 (Method)**
- ✅ **构造函数 (Constructor)**
- ✅ **字段 (Field)**
- ✅ **继承关系 (extends)**
- ✅ **实现关系 (implements)**
- ✅ **修饰符 (public, private, static, final)**

### 示例输入

```java
package com.example.auth;

import com.example.base.BaseService;
import java.util.List;

public class UserAuthService extends BaseService implements AuthInterface {

    private static final String TAG = "UserAuthService";
    private UserRepository userRepository;

    public UserAuthService(UserRepository repo) {
        this.userRepository = repo;
    }

    public boolean login(String username, String password) {
        // 登录逻辑
        return true;
    }

    private void validateCredentials(String username, String password) {
        // 验证逻辑
    }
}
```

### 生成的 Markdown

```markdown
# UserAuthService.java

**Package**: com.example.auth

**Imports**: com.example.base.BaseService, java.util.List, ...

## Class: UserAuthService (Line 5)

**Extends**: BaseService
**Implements**: AuthInterface

### Field: TAG (Line 7)

### Field: userRepository (Line 8)

### Constructor: UserAuthService (Line 10)

**Modifiers**: public

### Method: login (Line 14)

**Modifiers**: public

### Method: validateCredentials (Line 19)

**Modifiers**: private
```

---

## 📊 Kotlin 解析器支持的特性

### 识别的元素

- ✅ **Package 声明**
- ✅ **Import 语句**
- ✅ **类 (Class)**
- ✅ **Data Class**
- ✅ **Sealed Class**
- ✅ **Object**
- ✅ **Interface**
- ✅ **Enum Class**
- ✅ **函数 (Function)**
- ✅ **属性 (Property: val/var)**
- ✅ **继承关系**
- ✅ **修饰符 (private, suspend, inline)**

### 示例输入

```kotlin
package com.example.data

import com.example.base.BaseRepository
import kotlinx.coroutines.flow.Flow

data class User(
    val id: Long,
    val username: String,
    val email: String
)

class UserRepository(
    private val database: AppDatabase
) : BaseRepository() {

    suspend fun getUserById(id: Long): User? {
        return database.userDao().findById(id)
    }

    fun observeUser(id: Long): Flow<User> {
        return database.userDao().observeById(id)
    }

    private fun validateUser(user: User): Boolean {
        return user.username.isNotEmpty()
    }
}

object UserCache {
    private val cache = mutableMapOf<Long, User>()

    fun put(user: User) {
        cache[user.id] = user
    }
}
```

### 生成的 Markdown

```markdown
# UserRepository.kt

**Package**: com.example.data

**Imports**: com.example.base.BaseRepository, kotlinx.coroutines.flow.Flow, ...

## Data class: User (Line 5)

### Property: id (val) (Line 6)

### Property: username (val) (Line 7)

### Property: email (val) (Line 8)

## Class: UserRepository (Line 11)

**Inherits**: BaseRepository()

### Property: database (val) (Line 12)

### Function: getUserById (Line 15)

**Modifiers**: suspend

### Function: observeUser (Line 19)

### Function: validateUser (Line 23)

**Modifiers**: private

## Object: UserCache (Line 28)

### Property: cache (val) (Line 29)

### Function: put (Line 31)
```

---

## 🎯 Android 项目示例

### 典型的 Android 项目结构

```
MyApp/
├── app/
│   └── src/
│       └── main/
│           ├── java/
│           │   └── com/
│           │       └── example/
│           │           └── myapp/
│           │               ├── MainActivity.java
│           │               ├── ui/
│           │               └── data/
│           └── kotlin/
│               └── com/
│                   └── example/
│                       └── myapp/
│                           ├── viewmodel/
│                           ├── repository/
│                           └── utils/
```

### 索引整个项目

```bash
# 索引 Java 和 Kotlin 代码
./index_codebase.sh \
  ~/MyApp/app/src/main \
  ~/MyApp/docs/code
```

### 在 OpenCode 中查询

````
用户: 这个 Android 项目的架构是怎样的？

OpenCode:
根据代码索引分析，项目采用 MVVM 架构：

**UI 层** (ui/)
- MainActivity.java: 主界面
- LoginActivity.java: 登录界面
- UserProfileFragment.kt: 用户资料页面

**ViewModel 层** (viewmodel/)
- UserViewModel.kt: 用户数据视图模型
- LoginViewModel.kt: 登录视图模型

**Repository 层** (repository/)
- UserRepository.kt: 用户数据仓库
- AuthRepository.kt: 认证数据仓库

**数据层** (data/)
- AppDatabase.java: Room 数据库
- UserDao.kt: 用户数据访问对象

典型的 Android MVVM 架构模式。

─────────────────────────────────────

用户: UserViewModel 是怎么使用 UserRepository 的？

OpenCode:
UserViewModel 通过依赖注入使用 UserRepository：

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    val user: LiveData<User> = userRepository
        .observeUser(userId)
        .asLiveData()

    fun refreshUser() {
        viewModelScope.launch {
            userRepository.refreshUser(userId)
        }
    }
}
````

这是标准的 Repository 模式，ViewModel 不直接访问数据库。

````

---

## 🔧 高级用法

### 只索引特定包

```bash
# 只索引 auth 相关代码
python3 code_to_markdown.py \
  -i ~/MyApp/app/src/main/java/com/example/myapp/auth \
  -o ~/MyApp/docs/code/auth
````

### 分别索引 Java 和 Kotlin

```bash
# 只索引 Java
python3 code_to_markdown.py \
  -i ~/MyApp/app/src/main/java \
  -o ~/MyApp/docs/code/java \
  -e .java

# 只索引 Kotlin
python3 code_to_markdown.py \
  -i ~/MyApp/app/src/main/kotlin \
  -o ~/MyApp/docs/code/kotlin \
  -e .kt
```

### 定时自动索引

```bash
# 每天凌晨 2 点自动索引
crontab -e

# 添加：
0 2 * * * cd /path/to/code-index-toolkit && ./index_codebase.sh ~/MyApp/app/src/main ~/MyApp/docs/code
```

---

## ✅ 总结

### 已优化配置

- ✅ 默认支持 `.java` 和 `.kt` 文件
- ✅ 完整的 Java 语法解析
- ✅ 完整的 Kotlin 语法解析
- ✅ 支持 Android 项目结构
- ✅ 识别 MVVM 架构模式

### 下一步

1. **测试单个文件**：验证解析器工作正常
2. **索引小项目**：先索引一个模块
3. **配置 OpenCode**：集成到工作流
4. **开始使用**：通过 OpenCode 查询代码

需要帮助？查看 `README.md` 或询问我！🚀
