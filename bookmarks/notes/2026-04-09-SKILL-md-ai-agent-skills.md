# SKILL.md 模式：如何写出真正能用的 AI 智能体技能

> **来源**：微信公众号「Python学研大本营」
> **原文**：https://mp.weixin.qq.com/s/YsfLq_2N3GQ_I_NMJ6RvRQ
> **日期**：2026-04-09
> **标签**：AI工程化、智能体架构、技能系统、LangChain
> **评分**：⭐⭐⭐☆（3.5/5）

---

## 一、核心启示

### 1. 「按需加载」是通用智能的底层逻辑

文章最核心的认知转变：不要让AI启动时记住所有能力，而是让它在遇到问题时自己去找对应的技能说明书。

这和人类学习完全一致——没有人背下整本字典才去查字。我们当前的做法（SOUL.md注入全部Hook+规则）表面上与这个理念矛盾，但**本质不冲突**：Hook是「行为协议」，Skill才是「能力知识」。行为协议必须常驻（否则AI会忘记要验证、要记记忆），能力知识应该按需加载（否则浪费上下文）。

**关键区分**：
- SOUL.md里的Hook → 必须每轮执行的「宪法」，不是「字典」
- Skill里的SKILL.md → 按需加载的「专业手册」，不应该全塞进系统提示

### 2. description 是技能系统的命脉

文章反复强调：SKILL.md的description字段决定AI能否正确判断「什么时候用这个技能」。写得好=精准触发，写得差=从不触发或乱触发。

回头看我们自己的skill系统，OpenClaw的`<available_skills>`正是依赖description做匹配。这意味着**每个skill的description质量，直接决定了系统整体智能程度**。

### 3. 加功能=加文件，不改代码

这个原则我们已经实现了（clawhub install），但文章把它提升到了架构哲学的高度：一个好的系统，扩展能力的方式应该是「添加」而非「修改」。

---

## 二、对我们的建议优化

### ⚡ 建议1：审查所有skill的description质量

当前我们有多少个skill，description是否足够精确？一个模糊的description会导致两种后果：
- AI永远不调用（白装了）
- AI在不该调用时调用（噪音干扰）

**建议行动**：逐一检查 `skills/*/SKILL.md` 的description，确保包含明确的触发条件（「当用户要求…时」）和排除条件（「不适用于…」）。

### ⚡ 建议2：区分「协议层」和「技能层」的上下文占用

当前SOUL.md体积较大，每次对话都注入。可以考虑：
- SOUL.md精简为纯行为协议（Hook定义+核心原则）
- 将详细的执行规则（如bookmark-reader的四步流程、search规则等）全部放在对应的skill SKILL.md里
- SOUL.md只保留一句：「遇到X场景时，读取 rules/X.md 或 skills/X/SKILL.md」

这正好符合文章「按需加载」的核心理念。

### ⚡ 建议3：建立skill「触发率」监控

如果一个skill装了但从不被触发，说明description有问题或者skill本身无价值。可以：
- 在evolver-scan.sh中增加一项：检查各skill最近N天的使用频率
- 触发率为0的skill标黄告警
- 触发率<5%的description需要重写

---

## 三、自我提升改良

### 🔧 改良1：SKILL.md description 增加负面触发词

当前我们的skill description只写了「什么时候用」，缺少「什么时候不用」。例如：

**当前**：`scrapling-mcp` — "Advanced web scraping with Scrapling"
**改良后**：`scrapling-mcp` — "Advanced web scraping with anti-bot handling. Use when jina-reader and playwright-mcp both fail. Do NOT use for simple public pages (use jina-reader instead)."

加入了排除条件和优先级顺序，AI的判断准确率会显著提升。

### 🔧 改良2：bookmark-reader Step 3 增加启发检查维度

当前Step 3已经包含「分析→整理→吸收→优化自我」四步。借鉴本文，增加一个维度：

**新增子步骤：「架构验证」**——读完后反问自己：这篇文章描述的做法，我们的系统是否已实现？实现得更好还是更差？如果有差距，是理念差距还是执行差距？

这就是本文带来的实际价值：它让我从「我们做得不错」的自满中跳出来，去检查description质量、上下文占用、触发率监控这些容易被忽视的细节。

### 🔧 改良3：skill-creator SKILL.md 增加description编写规范

我们已有skill-creator技能，但需要确保它强制要求作者写好description。建议在skill-creator的规则中增加：

```
## description 编写规范（必须）
1. 必须包含明确的触发条件（"Use when..."）
2. 必须包含排除条件（"Do NOT use for..."）
3. 如果与其他skill有优先级关系，必须声明
4. 避免泛泛描述（如"web scraping"），要具体（如"Anti-bot scraping when jina-reader fails"）
```

---

## 四、文章方法论提炼

| 文章原则 | 我们现状 | 差距评估 |
|---------|---------|---------|
| 按需加载而非预加载 | ✅ OpenClaw已实现 | 无差距 |
| description决定触发质量 | ⚠️ 部分skill描述模糊 | 需改进 |
| 加功能=加文件不改代码 | ✅ clawhub实现 | 无差距 |
| allowed-tools白名单 | ✅ OpenClaw原生支持 | 无差距 |
| 技能协作与冲突处理 | ❌ 文章未涉及 | 我们领先（rules/evolution.md） |
| 版本管理 | ❌ 文章未涉及 | 我们领先（clawhub update） |

**总结**：方向正确，细节需打磨。文章最大的价值不是教我们新东西，而是提醒我们去检查那些「以为做好了其实可以更好」的地方。

→ 相关：2026-04-05-capability-evolver-self-upgrade.md
→ 相关：2026-04-05-Clawith-team-OpenClaw.md
→ 相关：2026-04-04-AI-work-paradigm.md
→ 相关：2026-04-07-hermes-agent-deep-dive-evolution-roadmap.md（Hermes技能架构对比）
→ 相关：2026-04-07-OpenClaw-Skills-handbook.md（Skills完整使用手册）


## 相关笔记
- [[2026-04-06-AI-Scientist-v2]] (关键词: ai)
- [[2026-05-03-ai-agent-resources-ecosystem]] (关键词: ai)
- [[2026-05-14-航空结构设计AI短期基础设施]] (关键词: ai)
- [[2026-04-13-rag-vs-mcp-architecture]] (关键词: ai)
- [[2026-04-30-Meta-Hyperagents自适应Agent框架]] (关键词: ai)
