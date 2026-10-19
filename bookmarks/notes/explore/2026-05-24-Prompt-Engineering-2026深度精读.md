# Prompt Engineering 2026 深度精读 — 从 CoT 到 Spec-Driven 开发

> 探索日期：2026-05-24 | 兴趣等级：L3 | 来源数量：6
> 覆盖维度：推理技术、结构化输出、Spec-Driven 开发、Agent 编排、安全防御

---

## 一、核心发现

### 发现 1：CoT 的本质是 Token 预算分配，不是"更聪明"

Zero-Shot CoT 的 "Let's think step by step" 之所以有效，根本原因是**分配了更多 token 给中间推理步骤**。模型本身并不因这句话变聪明 — 它只是有了更多"工作空间"。2026 年前沿模型（Claude Opus 4.6、GPT-5）已将推理能力内化，显式 CoT 更多是**精调信号**而非必要触发器。

**实测数据**：
- GSM8K 数学准确率：17.7% → 78.7%（PaLM，2022）
- 符号推理：~60% → ~95%（+35%）
- 但在 2026 前沿模型上，CoT 提升幅度已收窄至 5-10%

**对 Hermes 的启示**：我们的 `chain-of-thought` 主要用在 Skill 编排和子任务拆解上。对 glm-5.1 这类模型，CoT 格式（编号步骤 + 验证门禁）仍然有效，但不必在简单查找/分类任务上强制 CoT。

### 发现 2：Self-Consistency 的 CISC 变体 — 46% 算力削减

传统 Self-Consistency（Wang et al., 2022）需要 5-18 次采样取多数投票，token 成本 ×3-5。2025 年的 **CISC**（Confidence-Improved Self-Consistency）按每次采样的置信度加权投票，用 10 次采样达到原来 18 次的效果 — **46% 计算削减**。

**适用场景判定**：
- ✅ 高代价错误（医疗/法律/金融决策）
- ✅ 需要校准的置信度分数
- ✅ 单次错误有昂贵下游后果
- ❌ 简单分类/提取（不值得 3-5x 成本）

**温度建议**：0.5-0.8。低于 0.5 → 轨迹趋同无多样性；高于 0.8 → 噪声淹没正确答案。

### 发现 3：Structured Output >99% Schema 遵从率

2026 年的结构化输出已从"尽量输出 JSON"进化为**确定性 Schema 绑定**。对比：
- 自然语言提示"请输出 JSON"：~82% 遵从率
- JSON Mode（response_format=json）：~95%
- Structured Output（Schema 约束）：>99%

**Hermes 关联**：我们的 `outlines` Skill 已实现 regex/Pydantic 约束输出。`verification-gate` Skill 的验收标准也应从"自然语言描述"转向"Schema 可验证"。

### 发现 4：Spec-Driven Development 六区框架

Addy Osmani 提炼的 Spec 模板六区（基于 GitHub 对 2500+ Agent 文件的分析）：

| 区域 | 内容 | 关键原则 |
|------|------|---------|
| **Commands** | 完整可执行命令含 flags | 复制粘贴即可运行 |
| **Testing** | 框架、位置、覆盖率期望 | exit_code=0 才算通过 |
| **Project Structure** | 显式路径 src/tests/docs | 避免路径歧义 |
| **Code Style** | 一段真实代码 > 三段描述 | 命名约定 + 格式 |
| **Git Workflow** | 分支/commit/PR 规则 | 自动化检查 |
| **Boundaries** | 禁区清单 | secrets/vendor/CI |

**GitHub Spec Kit 四阶段门禁**：Specify → Plan → Tasks → Implement，每阶段人工验证后才推进。

**对 Hermes 的启示**：我们的 AGENTS.md 已有类似结构（完成定义 + 工具权限 + 环境锁定），但缺少 **Git Workflow** 和 **Boundaries** 的显式声明。可补充。

### 发现 5：指令诅咒 — 指令越多，遵从率越低

研究确认：随着指令堆积，模型性能**显著下降**。GPT-4 和 Claude 都难以同时遵守大量要求 — 倾向于遵循前几条，忽略后面的。

**解决方案**：
1. **拆分为顺序子任务**（我们的小批推进法正是此策略）
2. **扩展目录 + 摘要**：Agent 建立精简大纲引用详细规格
3. **专项子 Agent**：数据库设计、API 编码、测试各一个专家
4. **并行 Agent + 串行合并**：独立部分并行，交叉部分串行

### 发现 6：ReAct — 推理与行动的交织循环

ReAct（Yao et al., 2022）将 CoT 推理与工具使用交织：**Thought → Action → Observation** 循环。

```
Thought: 需要验证 troponin 0.8 是否异常
Action: search("troponin normal range ACS threshold")
Observation: 正常 < 0.04, ACS > 0.1
Thought: 0.8 远超阈值，高度可疑 ACS
```

**对比纯 CoT**：ReAct 在需要实时数据/工具调用的场景下显著优于纯推理。但开销更大（每步一次 API 调用 + 工具执行）。

**Hermes 关联**：我们的 Agent 本质上就在运行 ReAct 模式（工具调用 = Action，工具结果 = Observation）。理解这个框架有助于优化工具选择策略。

---

## 二、技术谱系图

```
Prompt Engineering 谱系（2026）

基础层
├── Zero-Shot（直接指令）
├── Few-Shot（2-5 示例）
└── Role-Based（角色/专家身份）

推理层
├── CoT（逐步推理）
│   ├── Zero-Shot CoT（"Let's think step by step"）
│   ├── Few-Shot CoT（带推理轨迹的示例）
│   ├── Auto-CoT（自动生成推理链）
│   └── SCoT（Structured CoT，代码生成专用）
├── Self-Consistency（多路径投票）
│   └── CISC（置信度加权，-46% 算力）
├── Tree-of-Thoughts（树状探索）
│   └── Graph-of-Thoughts（图状推理）
└── Extended Thinking（模型内置深度思考）

行动层
├── ReAct（推理+工具交织）
├── Plan-and-Solve（先计划后执行）
└── Reflexion（反思+自我修正）

结构层
├── Structured Output（Schema 约束）
├── Prompt Caching（缓存复用，-90% 成本）
└── System Prompt Engineering（系统级指令）

工程层
├── Spec-Driven Development（规格驱动）
│   ├── GitHub Spec Kit（四阶段门禁）
│   └── CLAUDE.md / AGENTS.md（持久规格文件）
└── Verification Gate（机械化验收）
```

---

## 三、2026 关键趋势

### 3.1 模型内化推理 → Prompt Engineering 重心转移

2022-2024：CoT/Self-Consistency 是"必需技巧"，直接提升准确率 20-40%
2026：前沿模型已内化推理能力，Prompt Engineering 的重心从**诱导推理**转向：
- **任务分解**（Spec-Driven）
- **工具编排**（ReAct/MCP）
- **安全约束**（边界声明 + 验证门禁）
- **成本优化**（Prompt Caching + 条件触发）

### 3.2 Spec-Driven > Vibe Coding

"Vibe Coding"（凭感觉写 Prompt 让 AI 生成代码）已证明会产生"纸牌屋代码"——看似完整但在审查下崩塌。

Spec-Driven 的核心差异：
- Spec 先于代码存在，是**可审查的资产**
- AI 从 Spec 生成代码，而非从模糊意图
- 每个验收标准可程序化验证（exit_code、test coverage、lint）

**Addy Osmani 的核心原则**："Minimal does not necessarily mean short" — 不要回避有价值的细节。

### 3.3 Agent Experience (AX) 设计

为 AI Agent 优化文档结构，类比 User Experience (UX)：
- `llms.txt` 文件：专门为 LLM 消费的项目描述
- OpenAPI Schema：机器可读的 API 规范
- MCP 兼容格式：标准化工具描述
- `agents.md`：专项 Agent 角色定义（@docs-agent, @test-agent, @security-agent）

---

## 四、CoT 使用决策矩阵

| 场景 | 用 CoT? | 推荐技术 | 理由 |
|------|---------|---------|------|
| 多步算术/逻辑 | ✅ | Few-Shot CoT | 步骤间依赖关系需显式化 |
| 因果推理 | ✅ | Zero-Shot CoT | "Let's think step by step" |
| 规划任务 | ✅ | Plan-and-Solve | 先规划后执行 |
| 歧义/模糊场景 | ✅ | Self-Consistency | 多路径投票增加可靠性 |
| 直接文本查找 | ❌ | Zero-Shot | CoT 浪费 token |
| 明确信号分类 | ❌ | Few-Shot | 示例比推理链更有效 |
| 单字段提取 | ❌ | Structured Output | Schema 约束更可靠 |
| 需要实时数据 | ✅ | ReAct | 工具调用获取外部信息 |

---

## 五、Prompt Caching 实操

Prompt Caching 可降低高达 **90%** 的 token 成本：

**适用场景**：
- System Prompt 固定不变（每次请求重复）
- Few-Shot 示例集固定
- Spec 文档作为上下文注入

**实现**：将固定部分放在 prompt 前部，动态部分放尾部。大多数 API 提供商（OpenAI/Anthropic）自动缓存前缀匹配的 prompt。

**对 Hermes 的关联**：我们的 L1 常驻记忆（MEMORY.md）每轮注入，是天然的 Prompt Caching 候选。Skill 按需加载机制也减少了不必要的 token 消耗。

---

## 六、安全防御 — Adversarial Prompting

### 常见攻击向量

| 攻击类型 | 描述 | 防御 |
|----------|------|------|
| Prompt Injection | 恶意输入覆盖系统指令 | 输入/输出分离 + 标记化 |
| Prompt Leaking | 诱导模型泄露系统 Prompt | 最小权限 + 敏感信息隔离 |
| Jailbreaking | 绕过安全约束 | 分层防御 + 内容过滤 |
| Data Poisoning | 训练数据/检索内容投毒 | RAG 数据质量门禁 |

**Hermes 防御现状**：我们的 `agent-security-redteam` 和 `llm-code-generation-security` Skill 已覆盖大部分场景。`verification-gate` 提供机械化验收防线。

---

## 七、与 Hermes 体系的融合评估

### ✅ 有利进化（应落实）

1. **Spec-Driven 六区模板** → 补充 AGENTS.md 的 Git Workflow + Boundaries 声明
2. **CISC 自一致性** → 关键决策节点（如交易信号、部署判定）可用多次采样 + 置信度加权

### 📦 有价值备用

3. **Prompt Caching 优化** → 评估 Hermes Gateway 是否已利用 API 提供商的缓存机制
4. **AX 设计模式** → 为 Skill 的 SKILL.md 添加 `llms.txt` 级别的 Agent 可消费描述

### 📚 知识库

5. **技术谱系图** → 完整技术地图已记录于本笔记
6. **CoT 决策矩阵** → 按场景选择推理技术的快速参考

---

## 八、待深入

1. **Tree-of-Thoughts vs Graph-of-Thoughts** 的实际生产环境应用案例
2. **Auto-CoT** 自动推理链生成的质量保证机制
3. **SCoT**（Structured CoT for Code Generation）对 Hermes Skill 代码生成的适用性
4. Prompt Caching 在多轮对话中的缓存命中率实测数据
5. **Extended Thinking** 模式（Claude 系列内置）与显式 CoT 的效果对比

---

## 九、来源列表

1. [Advanced Prompt Engineering Techniques for LLMs in 2026 — Medium](https://medium.com/@pysquad/advanced-prompt-engineering-techniques-for-llms-in-2026-1df5ebb414d1)
2. [Prompt Engineering Guide 2026 — Analytics Vidhya](https://www.analyticsvidhya.com/blog/2026/01/master-prompt-engineering)
3. [How to Write a Good Spec for AI Agents — Addy Osmani](https://addyosmani.com/blog/good-spec)
4. [Advanced PE: CoT to ReAct and Structured Outputs — LetsDataScience](https://letsdatascience.com/blog/advanced-prompt-engineering-chain-of-thought-react-and-structured-outputs)
5. [Prompt Engineering Guide — promptingguide.ai](https://www.promptingguide.ai)
6. [My LLM Coding Workflow Going Into 2026 — Addy Osmani](https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026-52fe1681325e)

## 相关笔记
- [模型不是关键Harness才是](ai-agent/2026-04-19-模型不是关键Harness才是.md)
- [llm-self-prompt-optimization](explore/2026-05-18-llm-self-prompt-optimization.md)
