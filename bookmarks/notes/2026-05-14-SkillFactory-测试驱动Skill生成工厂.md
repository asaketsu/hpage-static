# SkillFactory：测试驱动的 Skill 自动化生成工厂

- 📅 2026-05-14
- ⭐ 3.5/5 — 有价值的产品设计思路（基线诊断+多路并发），但工程落地细节偏少，更像产品设计文档
- 🏷️ #Skill工程 #测试驱动 #AI自动化 #Harness #Agent技能
- 📰 微信公众号 - 阿里妹导读
- 🔗 https://mp.weixin.qq.com/s/tm7M3N8f45K87YUTwERkhg

关联：[2026-05-14-Agent工程4月实践](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md) — 同为 Agent 工程化实践，该文强调"被问题推过去"，SkillFactory 是"主动造工具"
关联：[2026-05-08-addyosmani-agent-skills](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md) — Addy Osmani 的 Skill 体系是 SkillFactory 的输入源之一（文中引用 superpowers/writing-skills）
关联：[skill-stress-test](../../.hermes/skills/devops/skill-stress-test/SKILL.md) — 已融入基线诊断思路

## 摘要

阿里内部工程师提出 SkillFactory 产品设计，解决当前 AI Agent Skill 生产的两大痛点：人工编写效率低质量波动大，对话生成缺乏自动化验证闭环。核心创新点：基线诊断（先判断有无必要生成）+ 多路并发 Skill 生成（3种策略并行竞优）+ 5维度评测打分 + 单轮回归迭代。未来方向包括 Trace2Skill（执行轨迹蒸馏为 Skill 文档）和 SkillRL（强化学习共同进化）。

## 核心内容

### 1. 三种 Skill 生产模式对比

| 维度 | 模式一：人工编写 | 模式二：对话生成 | 模式三：SkillFactory |
|------|-----------------|-----------------|---------------------|
| 核心逻辑 | 人脑驱动，依赖个人经验 | 对话驱动，依赖Prompt技巧 | 流程驱动，标准化流水线+TDD |
| 生产效率 | 低（天/周级） | 高 | 高 |
| 代码质量 | 波动大，风格不统一 | 随机性强，缺异常处理 | 标准化高，下限有保证 |
| 测试验证 | 依赖人工 | 无自动化闭环 | 自动化闭环，先有测试再生成 |
| 多方案探索 | 单线程 | 串行迭代，上下文易丢失 | 多路并行竞优，同时3版择优 |
| 工程化程度 | 格式/规范易出错 | 缺生产环境鲁棒性 | 可注入测试/优化逻辑达生产级 |
| 知识复用 | 通用逻辑重复造轮子 | 对话记录难共享 | 团队资产，自动识别重复模块 |

### 2. SkillFactory 五阶段流水线

```
技能定义 → 基线诊断 → 测试构建 → 多路并发生成 → 回归迭代
```

**技能定义**：用户输入想生成的技能、测试问题、API接口（后续支持SOP文档）

**基线诊断**（亮点设计）：
- 裸模型评估：直接让模型执行目标任务，作为基线对照
- Skill匹配分析：召回相似skill，执行测试问题，评估现有技能是否满足需求
- 失败点 = Skill 需要解决的真实能力缺口

**测试构建**：复用用户输入的测试问题

**多路并发生成**：
- 并行调用3种不同策略（不同模型/不同Prompt模板）的Creator
- 类似"一次买三张彩票"，只要一路成功就算成功
- 提高首次生成成功率，避免单路径失败的反复重试

**回归迭代**：目前只做单轮测试+优化
- 测试阶段：用户选择某版本/所有版本，从5维度评价打分
- 优化阶段：生成优化版本skill，可下载或发布

### 3. 生态适配

支持知流平台的MCP/HTTP/Dify Agent工具直接生产技能。

### 4. 迭代方向（前瞻性）

**Trace2Skill** — 基于千问团队论文 Distill Trajectory-Local Lessons into Transferable Agent Skills：
- 将智能体的"隐性经验"（执行轨迹）转化为"显性知识"（结构化技能文档）
- 仅通过开源小模型进行轨迹分析，就能提炼出通用的专家级能力
- 不依赖昂贵人工编写，不需要更新模型参数

**SkillRL** — 强化学习路线：
- 把Agent与环境交互的冗长轨迹蒸馏成紧凑、可复用的"技能卡片"
- 技能库与策略共同进化

**虚拟环境测试** — 对不能实际执行的技能进行模拟回归

### 5. AI Coding 实践

开发过程中使用的工具分工：
- idealab + Qoderwork：产品功能页面设计
- 爱码仕：前端页面生成
- 灵码/aonecopilot：debug、优化、生成编码框架demo

## 三档分类与借鉴点

| 档次 | 借鉴点 | 动作 |
|------|--------|------|
| 🔴 有利进化 | 基线诊断思路（裸模型+已有Skill匹配） | 已 patch 到 skill-stress-test，生成前先判断是否可复用 |
| 🔴 有利进化 | 多路并发Skill生成+择优 | 已 patch 到 auto-skill，5维度打分竞优 |
| 🟡 有价值 | Trace2Skill轨迹蒸馏 | 记入 Memory 备用，未来数据量够时可尝试 |
| 🟡 有价值 | 5维评测打分体系 | 已记入笔记，可参考设计 skill-stress-test 评测维度 |
| 🔵 知识库 | 产品UI/UX设计、知流平台适配 | 仅笔记记录 |

不落实项及理由：
- Trace2Skill：需大量执行轨迹数据积累，当前 session 数据量不足以支撑
- 虚拟环境测试：实现成本高，当前 stress-test subagent 方案已够用
- 知流平台适配：我们不用知流

## 启发

1. **"先判断有没有必要"比"做得更快"更重要** — 基线诊断思路直接节省了不必要的 Skill 生成成本，这在 Hermes 体系中同样适用
2. **多路并发是应对LLM不确定性的实用策略** — 不追求单一最优 Prompt，而是并行多路+择优，用工程手段弥补模型随机性
3. **Trace2Skill 是 Skill 工程的未来方向** — 当前所有 Skill 都是"事前设计"，Trace2Skill 开辟了"事后提炼"路线

## 预判

| 时间 | 预判 |
|------|------|
| 短期 | SkillFactory 作为知流平台增值功能上线，吸引 MCP 生态开发者 |
| 中期 | Trace2Skill 路线若跑通，将颠覆 Skill 手写模式，Agent 日志自动沉淀为 Skill |
| 长期 | Skill 市场可能出现类似 npm 的分发体系，质量评分成为关键基础设施 |
## 相关笔记
- [AI-Agent架构-MCP-A2A协议栈](explore/2026-05-13-AI-Agent架构-MCP-A2A协议栈.md)
- [Agentic-Engineering-从Vibe-Coding到Agent工程](explore/2026-05-14-Agentic-Engineering-从Vibe-Coding到Agent工程.md)
- [Agent工程4月实践-不要一上来就做Agent](2026-05-14-Agent工程4月实践-不要一上来就做Agent.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [MATLAB-Agentic-Toolkit分析](2026-05-14-MATLAB-Agentic-Toolkit分析.md)
- [手撸Agent-ReAct-Loop从零实现](2026-05-14-手撸Agent-ReAct-Loop从零实现.md)
- [ai-agent-architecture](explore/2026-05-15-ai-agent-architecture.md)
- [上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
- [Small-Hermes-自我进化深度解析](2026-05-14-Small-Hermes-自我进化深度解析.md)


## 相关笔记
- [2026-05-12-网络安全-security-automation](2026-05-12-网络安全-security-automation.md)
- [2026-05-12-数据治理-data-catalog](2026-05-12-数据治理-data-catalog.md)
- [20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化](20260513-llm-wiki-obsidian-gbrain-知识自组织与自进化.md)
- [llm-wiki-gbrain-agent-evolution_33aa818c](llm-wiki-gbrain-agent-evolution_33aa818c.md)
- [2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论](2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论.md)
