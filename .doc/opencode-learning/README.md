# OpenCode 深度学习指南

> 📚 专为希望深度理解和二次开发 OpenCode 的专业开发者准备的完整学习资源

## 🎯 关于本指南

本学习指南旨在帮助你：

- ✅ **系统理解** OpenCode 的架构设计和实现原理
- ✅ **快速上手** 进行二次开发和功能扩展
- ✅ **最佳实践** 遵循 OpenCode 的开发规范和模式
- ✅ **贡献代码** 参与开源社区，提交高质量 PR

## 📖 学习文档

### 🌟 核心文档

| 文档                                        | 内容概要                           | 适合人群 | 预计时间 |
| ------------------------------------------- | ---------------------------------- | -------- | -------- |
| [00-项目概览](./00-项目概览.md)             | OpenCode 简介、技术栈、核心概念    | 所有人   | 30分钟   |
| [01-核心架构详解](./01-核心架构详解.md)     | 深入讲解各核心模块的设计与实现     | 开发者   | 2-3小时  |
| [02-深度学习路线图](./02-深度学习路线图.md) | 分阶段学习计划、实践项目、检查清单 | 开发者   | 作为参考 |
| [03-二次开发实战](./03-二次开发实战.md)     | 常见场景的完整代码示例             | 开发者   | 参考使用 |
| [04-CLI架构与调试](./04-CLI架构与调试.md)   | CLI 架构分析、添加日志、流程追踪   | 开发者   | 1-2天    |
| [05-调试日志实战](./05-调试日志实战.md)     | 调试工具使用、实战示例             | 开发者   | 半天     |

### 📄 辅助文档

| 文档                                      | 说明                             |
| ----------------------------------------- | -------------------------------- |
| [构建三大产物指南](./构建三大产物指南.md) | CLI、Desktop、Web 的详细构建步骤 |
| [构建快速参考](./构建快速参考.md)         | 常用构建命令速查                 |
| [快速验证修改](./快速验证修改.md)         | 验证代码修改的方法               |

### 📚 推荐学习路径

#### 快速入门 (1-2天)

```
1. 阅读 00-项目概览.md
   └─ 理解 OpenCode 是什么，核心特性

2. 搭建开发环境
   └─ 参考 02-深度学习路线图.md 的 Day 1

3. 运行并体验 OpenCode
   └─ bun dev，发送测试请求
```

#### 系统学习 (1-2周)

```
1. 精读 01-核心架构详解.md
   └─ 理解各模块的设计和交互

2. 跟随 02-深度学习路线图.md 第一阶段
   └─ Day 1-5 的每日任务

3. 阅读核心源码
   └─ server.ts, agent.ts, tool.ts, session/index.ts

4. 完成基础实践
   └─ 创建简单的自定义工具
```

#### 深度开发 (2-4周)

```
1. 学习 03-二次开发实战.md 的场景
   └─ 选择感兴趣的场景深入实践

2. 跟随 02-深度学习路线图.md 第二、三阶段
   └─ 完成进阶项目

3. 参与开源贡献
   └─ 提交 Issue、PR
```

## 🗂️ 文档结构

```
.doc/opencode-learning/
├── README.md                    # 本文件 - 学习指南总览
├── 00-项目概览.md                # OpenCode 介绍和核心概念
├── 01-核心架构详解.md            # 深入的架构分析
├── 02-深度学习路线图.md          # 学习路径和实践项目
└── 03-二次开发实战.md            # 实战代码示例
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保已安装 Bun
curl -fsSL https://bun.sh/install | bash

# Clone 项目
git clone https://github.com/anomalyco/opencode.git
cd opencode

# 安装依赖
bun install
```

### 2. 运行 OpenCode

```bash
# 启动开发服务器
bun dev

# 或在指定目录运行
bun dev /path/to/your/project
```

### 3. 第一个自定义工具

按照 [02-深度学习路线图.md](./02-深度学习路线图.md) 的 Day 3 创建你的第一个工具。

## 📊 核心模块概览

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端层                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │   TUI    │    │   Web    │    │  Desktop │              │
│  │(Terminal)│    │(Browser) │    │ (Tauri)  │              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
└───────┼───────────────┼───────────────┼─────────────────────┘
        │               │               │
        │     HTTP / WebSocket / SSE   │
        │               │               │
┌───────┼───────────────┼───────────────┼─────────────────────┐
│       └───────────────┴───────────────┘                     │
│                    服务器层                                  │
│  ┌──────────────────────────────────────────────┐          │
│  │          Hono HTTP Server                     │          │
│  └────┬─────────────┬──────────────┬─────────────┘          │
│       │             │              │                        │
│  ┌────▼────┐  ┌────▼────┐  ┌─────▼──────┐                 │
│  │ Session │  │  Agent  │  │    Tool    │                 │
│  │ Manager │  │  Engine │  │  Registry  │                 │
│  └─────────┘  └─────────┘  └────────────┘                 │
│       │             │              │                        │
│  ┌────▼────────────▼──────────────▼─────────┐              │
│  │   LSP │  MCP  │  Storage  │  Provider   │              │
│  └─────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

- **Server** - Hono 驱动的 HTTP API 服务器
- **Agent** - AI Agent 引擎，支持多 Agent 协作
- **Tool** - 工具系统，可扩展的能力单元
- **Session** - 会话管理，消息存储和流式处理
- **Provider** - 多 AI 提供商支持
- **LSP** - 语言服务器协议集成
- **MCP** - Model Context Protocol 支持
- **Storage** - 灵活的存储抽象层

## 🎓 学习检查清单

### ✅ 基础阶段

- [ ] 理解 OpenCode 的核心价值和设计理念
- [ ] 熟悉 Monorepo 结构和各 package 的职责
- [ ] 成功搭建并运行开发环境
- [ ] 了解基本的 Bun 和 TypeScript 用法
- [ ] 理解客户端/服务器架构

### ✅ 进阶阶段

- [ ] 深入理解 Tool 系统的实现
- [ ] 掌握 Agent 的提示词工程
- [ ] 熟悉 Hono 服务器的路由和中间件
- [ ] 理解 Session 和 Message 的生命周期
- [ ] 了解多 AI 提供商的集成方式

### ✅ 高级阶段

- [ ] 能够独立开发复杂的自定义工具
- [ ] 理解 LSP 和 MCP 的集成机制
- [ ] 掌握性能优化技巧
- [ ] 熟悉安全和权限系统
- [ ] 能够开发 TUI 和 Web UI 组件

### ✅ 专家阶段

- [ ] 理解整个系统的设计模式和最佳实践
- [ ] 能够提出架构改进建议
- [ ] 向 OpenCode 贡献高质量代码
- [ ] 帮助其他开发者学习和使用 OpenCode

## 💡 学习建议

### 🎯 高效学习的关键

1. **动手实践优先**
   - 每个概念都要亲自编码验证
   - 不要只看文档，要运行和调试代码

2. **循序渐进**
   - 按照文档顺序学习
   - 完成一个阶段的检查清单再进入下一阶段

3. **深入源码**
   - 阅读核心模块的实现
   - 理解设计决策和权衡

4. **参与社区**
   - 在 Discord 提问和讨论
   - 查看和学习其他人的 Issue 和 PR

5. **记录总结**
   - 写学习笔记或技术博客
   - 整理遇到的问题和解决方案

### 📝 实践项目建议

从简单到复杂：

1. **Hello World 工具** - 熟悉工具定义
2. **文件处理工具** - 学习文件操作
3. **Git 集成** - 理解命令执行
4. **代码分析工具** - 集成 LSP
5. **团队协作功能** - 扩展 API
6. **自定义 Agent** - 掌握提示词工程
7. **性能监控** - 优化和监控
8. **插件系统** - 理解扩展机制

## 🔗 相关资源

### 官方资源

- [OpenCode 官网](https://opencode.ai)
- [GitHub 仓库](https://github.com/anomalyco/opencode)
- [官方文档](https://opencode.ai/docs)
- [Discord 社区](https://discord.gg/opencode)
- [Twitter](https://x.com/opencode)

### 技术栈文档

- [Bun](https://bun.sh) - JavaScript 运行时
- [TypeScript](https://www.typescriptlang.org) - 类型系统
- [Hono](https://hono.dev) - Web 框架
- [SolidJS](https://solidjs.com) - UI 框架
- [Zod](https://zod.dev) - Schema 验证
- [Vercel AI SDK](https://sdk.vercel.ai) - AI 集成
- [Tauri](https://tauri.app) - 桌面应用框架

### 相关协议

- [LSP Specification](https://microsoft.github.io/language-server-protocol/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Anthropic Claude](https://anthropic.com)
- [OpenAI API](https://platform.openai.com)

## 🤝 如何贡献

### 向 OpenCode 贡献

1. **Fork 并 Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/opencode.git
   ```

2. **创建功能分支**

   ```bash
   git checkout -b feature/my-awesome-feature
   ```

3. **编写代码和测试**
   - 遵循 [CONTRIBUTING.md](../../CONTRIBUTING.md)
   - 遵循 [STYLE_GUIDE.md](../../STYLE_GUIDE.md)

4. **提交 PR**
   - 清晰的 PR 描述
   - 链接相关 Issue
   - 包含测试和文档

### 向本学习指南贡献

如果你发现文档有误或有改进建议：

1. 创建 Issue 描述问题
2. 或直接提交 PR 修复
3. 欢迎翻译成其他语言
4. 补充更多实战案例

## 📞 获取帮助

遇到问题时：

1. **查看文档** - 本指南和官方文档
2. **搜索 Issues** - [GitHub Issues](https://github.com/anomalyco/opencode/issues)
3. **社区提问** - [Discord](https://discord.gg/opencode)
4. **阅读源码** - 查看测试用例和实现

## 🙏 致谢

感谢 OpenCode 团队创建了这个优秀的开源项目！

特别感谢所有贡献者和社区成员的付出。

## 📄 许可

本学习指南遵循 MIT 许可证，与 OpenCode 项目保持一致。

---

**开始你的 OpenCode 学习之旅吧！** 🚀

如有任何问题或建议，欢迎通过以下方式联系：

- GitHub Issues
- Discord 社区
- Twitter: @opencode

祝学习愉快！

---

**最后更新**: 2026-01-18  
**维护者**: OpenCode 学习小组  
**版本**: v1.0
