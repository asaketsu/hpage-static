# 别再堆 Tools 了：Agent Skills 才是关键抽象层

- 📅 2026-04-02
- ⭐⭐⭐⭐⭐ 5/5 — 高度相关，直接指导我们的 Skill 体系设计
- 🏷️ #AgentSkills #MCP #AI架构 #渐进式披露 #OpenClaw
- 📰 公众号：AI大模型应用开发（转载：53AI、火山引擎、InfoQ）

## 核心论点

**连接性（Connectivity）与能力（Capability）应该分离。**
- MCP = "手" → 让 Agent 够得着外部工具和数据
- Skills = "操作手册/SOP" → 告诉 Agent 如何组合使用这些工具

类比：MCP 是 USB 接口/驱动程序，Skills 是应用程序。有打印机驱动≠会双面打印。

## Agent Skills 的本质

**标准化程序性知识封装格式**，包含三层：

| 层 | 内容 | 作用 |
|---|---|---|
| **Definitions** | 能力描述、触发条件 | 什么时候该用这个技能 |
| **Instructions** | System Prompt + 工具调用逻辑 | 怎么一步步完成 |
| **Resources** | scripts/ + references/ + assets/ | 代码脚本、规范文档、模板 |

## 关键机制：渐进式披露（Progressive Disclosure）

**最重要的设计原则。**

- SKILL.md 控制在 ~500 行
- name + description 在启动时加载（轻量）
- 详细指令按需加载，不一次性灌入上下文
- **Token 消耗降低 90% 以上**

```
上下文窗口变化：
触发前：[系统提示 + 工具定义] ← 仅名称和描述
触发后：+ [SKILL.md 详细指令] ← 按需加载
需要时：+ [references/xxx.md] ← 进一步按需
```

## MCP vs Skills：互补而非竞争

| 维度 | MCP | Skills |
|------|-----|--------|
| 解决什么 | 连接性 | 能力/知识 |
| 类比 | USB 驱动/神经系统 | 应用程序/大脑皮层 |
| 适用场景 | 外部服务连接 | 复杂工作流+领域知识 |
| 格式 | 标准化协议 | 文件系统（灵活） |

**最佳实践：MCP 提供基础设施连接 + Skills 提供业务逻辑**

## LangChain 创始人 Harrison Chase 的观点

> "绝大多数差异化，在于指令、工具和技能。领域知识、专属工具、业务流程指令，这些不会变，才是真正的壁垒。"

核心四组件：
1. **详细系统提示词** = Agent 的 SOP
2. **规划工具** = 任务分解能力
3. **子智能体** = 并行/异步执行
4. **文件系统** = Agent 自己管理上下文窗口

## 行业现状

- Claude Code 对 Skills 触发成功率 ~98%
- 非 Claude 模型（豆包、DeepSeek）成功率 ~80% 或更低
- Skills 格式尚未统一，不同厂商可能不兼容
- 安全性：Skills 含可执行脚本，存在代码注入风险

## 对我们的启发

### ✅ 我们已经在做的
- SOUL.md 就是核心 Skill（行为规则+工作流）
- AGENTS.md = 团队协作 SOP
- Hook 体系 = 自动触发的 Skills
- permanent/ 四分类 = 领域知识文件系统
- 渐进式披露：session 启动只读索引，按需展开（lcm_expand）

### 🔧 可以改进的
- **SKILL.md 行数控制**：部分 skill 可能超过 500 行，需要精简
- **description 优化**：available_skills 里的 description 决定触发准确性
- **非 Claude 模型兼容**：我们用 GLM-5-turbo，需要验证 Skill 触发率
- **安全审计**：安装 Skill 前用 skill-vetter 检查（已有这个 skill）

## 延伸阅读

- [Anthropic Agent Skills 官方文档](https://docs.anthropic.com)
- [LangChain Harrison Chase 访谈 — InfoQ](https://www.infoq.cn/article/pdg3TkbgvSc2PolE5ioy)
- [Agent Skills 详细总结 — 53AI](https://www.53ai.com/news/LargeLanguageModel/2026011326913.html)
- [Agent 一年复盘 — 火山引擎](https://developer.volcengine.com/articles/7589192960529727538)


## 相关笔记
- [[2026-04-26-RAG与MCP架构差异]] (关键词: ai架构, mcp)
- [[2026-05-14-MATLAB-Agentic-Toolkit分析]] (关键词: agentskills, mcp)
- [[2026-04-04-OpenClaw-4.2-stable-backend]] (关键词: openclaw)
- [[2026-04-29-竞品吸收笔记-khazix-skills]] (关键词: skills)
- [[2026-05-16-MCP-协议生态最新发展]] (关键词: mcp)
- [[2026-05-24-AI编码工具战争-CodexClaudeCodeCursor收敛为分层架构.md]]
