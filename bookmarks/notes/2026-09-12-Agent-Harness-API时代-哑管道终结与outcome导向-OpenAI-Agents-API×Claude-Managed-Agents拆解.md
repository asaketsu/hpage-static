# Agent Harness API 时代：哑管道终结与 outcome 导向——OpenAI Agents API × Claude Managed Agents 拆解 + harness-agnostic 二阶抽象 + Hermes 位置剖析

> **来源**：X/Twitter @kevinwhinnery（Kevin Whinnery）Article《Agent harness APIs are here to stay》2026-09-10
> **原文链接**：https://x.com/kevinwhinnery/status/2098444890602455431
> **事件背景**：OpenAI Agents API 公开 beta 发布（前日），与 Claude Managed Agents 并列
> **抓取方式**：X Article 直读全文
> **笔记日期**：2026-09-12
> **关联笔记**：harness 簇（mem0/Minara/Google流式/Gipp/beamnxw/SoL-Pi 六篇）《Plano×Hermes判定》（模型亲和/成本感知）《AGENTS.md手册模式》（指令层资产化）

---

## 零、结论先行

**核心命题：推理 API（Chat Completions/Messages）正从 AI 应用的主集成面降级为基础设施层，取而代之的是 agent harness API——连接工具/认证/计算环境/多 agent 编排/可观测/上下文管理的"完整 harness"通过编程接口暴露。** 文章给出两条实践原则：① outcome 导向（描述+评估要的结果，删掉手工管上下文窗口/工具调用的胶水代码）；② **harness-agnostic 而非 model-agnostic**（推理层抽象已不够，harness+model 越来越一体设计，不同 harness 同模型结果差异巨大）。对我们 Hermes 的判定：我们**已经是 harness-native**（Gateway=自带 harness 的完整 agent，不是哑管道），Plano 判定笔记的"模型亲和已有等价物"结论被本文从产业侧再次印证——但"harness-agnostic 多 harness 对比"是值得追踪的新增量。

## 一、事件层：两个 harness API 的并列

| API | 厂商 | 接口模式 | 基础设施 |
|-----|------|---------|---------|
| **Agents API**（公开 beta） | OpenAI | 事件驱动 | 托管 |
| **Claude Managed Agents** | Anthropic | 事件驱动 | 托管 |

用法（用过 Claude Code 或 ChatGPT/Codex 就已熟悉）：连接工具 → 配置认证 → 给 agent 一台计算机（你的或云上的）→ 给一个任务 → 它自己干到完成。

**关键一句**："If you've used either Claude Code or ChatGPT, you already know how these APIs work."——harness API 不是新发明，是把已有产品能力编程化暴露。

## 二、为什么哑管道不够了

> "Getting useful results from a model is rarely possible using a dumb token pipe alone."

真实应用负载需要的：
- 外部系统连接
- 计算环境（模型执行代码/干活的地方）
- 多 agent 编排
- 认证/授权
- 会话可观测性
- 上下文管理（**记忆/压缩/dreaming**）

> **以上全部=我们一直叫的"harness"**

文章的 benchmark 直觉与 Minara 笔记互证："If you tell me 'model XYZ scored 67% on ABC benchmark', my next question is **'using what harness?'** — the model ID is only part of the story."——**配对即性能单位**，正是 Minara 58 分差的总结。

## 三、两条原则（文章核心增量）

### 原则 1：outcome 导向

- 近几个月你用 Claude Code/ChatGPT 的方式变了：**少 hand-hold prompt、少装 skill、精简 AGENTS.md**——最强模型配现代 harness 只需工具+系统权限+指向问题
- harness API 让 API 负载走同一条路：**删掉精心管上下文窗口或拼工具调用的胶水代码**，聚焦描述+评估工作的结果

> 这里要注意：文章说"trimming AGENTS.md"与我们 AGENTS.md 笔记的"<200 行"纪律同源——但**方向有张力**：AGENTS.md 笔记说指令层是资产要积累，本文说最强模型不需要那么多指令——和解方式是"积累决策记忆+精简规则"（memory 增、rules 瘦）

### 原则 2：harness-agnostic 而非 model-agnostic

- 多数 AI 应用用推理 API 抽象层（Vercel AI SDK / OpenRouter）做 model-agnostic——历史上是审慎的降险选型
- **但推理不再是对的东西去抽象**——harness 与 model 越来越一体设计，不同 harness 同模型结果差异巨大
- outcome 导向 + 少 harness 逻辑 → 可以 **delegate work to different harnesses, compare results**（harness-agnostic）
- 早期支持已出现（至少对自建基础设施的 harness），预计成熟化

> 这与 Plano 的 model-agnostic 路由是**不同层**的抽象：Plano 在推理层按价格路由（我们判定不引入），本文在 harness 层按能力对比——后者更接近正确抽象面

## 四、与今日 harness 簇的合流（第七篇收官）

| 篇 | 维度 | 本文增量 |
|----|------|---------|
| mem0 三种写 | 自进化=持久化 | harness API 的上下文管理含"dreaming"——agent 层的 dream 与模型层的关系 |
| Minara 58 分差 | 配对即单位 | "model ID is only part of the story" 互证 |
| Google 流式 | 并行编排消灭延迟 | harness API 暴露的就是编排能力 |
| Gipp 3-15% | 为失败率设计 | harness API 的认证/授权/可观测=Gipp 说的 gate 基础设施化 |
| beamnxw Lane | 身份/记忆分离 | harness API 的 managed infra 消除了自建 Pin 的需要 |
| SoL-Pi | harness 可 RSI 优化 | "harness logic overall decreases"=SoL-Pi 优化的终态 |
| **本文** | **harness 从产品到 API：哑管道终结** | 七篇拼图的收口——harness 不只是内部架构，是新的编程接口面 |

## 五、与 Hermes 体系的对照

| 文章主张 | 本机现状 | 判定 |
|---------|---------|------|
| 推理 API 不再是主集成面 | Hermes Gateway=自带 harness 的完整 agent（工具/记忆/压缩/编排/认证全有），不是哑 Chat Completions 管道 | ✅ **已是 harness-native** |
| model-agnostic 抽象层不够 | Plano 判定已否决推理层路由；fallback 链按池健康非价格 | ✅ 结论一致——推理层抽象不够 |
| harness-agnostic（多 harness 对比） | 无等价物——单 harness（Hermes），无第二 harness 做对比 | 🟡 **值得追踪**——但当前无第二 harness 可比 |
| outcome 导向（删胶水代码） | AGENTS.md 质量门禁机械化准则；execute_code 批处理合并 | ✅ 精神已有 |
| "dreaming"上下文管理 | auto-dream/idle-busy-loop 系列已有 agent 层 dream | ✅ 已有——文章用这个词说明 harness API 的上下文管理范围 |

## 六、增量判定与 Nugget 归宿

**不形成新 skill**——理由三条：
1. 我们是 harness-native 架构（Gateway 即 harness），文章描述的"从哑管道迁移到 harness API"对我们不适用——我们生在正确的一侧
2. harness-agnostic 多 harness 对比当前无第二 harness 可比（与 AGENTS.md 笔记的触发条件同理：等第二个厂商 agent 协作时再动）
3. 七篇 harness 簇的模式总结已充分，再建 skill 是通胀

**两个 Nugget 归宿**：
- **"harness-agnostic"概念** → 记入 AGENTS.md 笔记的同款触发条件：当出现第二 harness（最可能=OpenAI Agents API 或 Claude Managed Agents 走云端版接入我们的工作流），当天把"harness 对比评估"提炼为 skill——本笔记即素材
- **"outcome 导向=删胶水"** → 已有实践（门禁机械化/批处理），记入下次 AGENTS.md 审计的检查项："哪些手工管上下文/工具调用的代码可以删了"

## 七、批判性审视

1. **"dumb token pipe is ending" 过强**：推理 API 不会消失——正如 Unix 没被云计算消灭而是降到基础设施层；文章自己也说"will have their place"，但标题选了更激进的口径
2. **harness-agnostic 的实操缺失**：文章只说"delegate to different harnesses, compare results"——**怎么比？用什么 benchmark？成本如何？** 全无（比 Minara 的六道滤网差远了）——这是概念文不是实操文
3. **OpenAI Agents API 的 vendor lock-in 风险未提**：托管 harness API = 你的工具/认证/计算环境全在厂商侧——beamnxw 的"identity separate from memory"在这里更关键了，文章一笔带过"authentication/authorization"
4. **"trimming AGENTS.md"与资产积累的张力**未调和——本文立场是"强模型不需要那么多指令"，但 AGENTS.md 笔记的"决策日志只增不删"也是真的；和解方式=rules 瘦+memory 增（本文没说这层）
5. **作者背景**：Google/Chrome DevRel 出身，现做 AI 应用——视角是"应用开发者"，不是"infra 工程师"；harness-agnostic 的可行性论证偏乐观

## 八、金句提取

> "The era of the dumb token pipe is ending."

> "If you tell me 'model XYZ scored 67% on ABC benchmark', my next question is 'using what harness?'"

> "Be harness-agnostic rather than model-agnostic."（引用 @katelyn_lesse）

> "You'll be well-served to start thinking about your AI applications in terms of tasks you want to accomplish."

> "Agent harness APIs will become increasingly cheap and sophisticated, and will enable you to delete the proprietary harness code that has nothing to do with the actual work you want done."

## 九、局限性

1. 文章约 900 字，概念文/立场文，无实测数据无代码——价值在框架不在细节
2. OpenAI Agents API 的具体能力面（工具定义/事件格式/计费/限制）未展开——需读官方文档
3. "harness-agnostic 支持已出现在某些抽象层"未点名是哪些——引用空泛
4. §五对照与 §六判定基于本机 Hermes 架构理解，未实际跑 OpenAI Agents API
5. 与 AGENTS.md 笔记的"trimming vs accumulating"张力未充分展开——留作后续思考

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一至三 | **原文忠实还原**（X Article 全文直读） |
| 四 | **harness 簇收口**（今日七篇联动） |
| 五、六 | **体系映射+判定**（本笔记扩展） |
| 七 | **批判性审视**（本笔记扩展） |

## 相关笔记

- [AGENTS.md手册模式](./2026-09-12-AGENTS.md手册模式-厂商文件薄适配器化与三重验证法-Skill必要性判定.md) — 指令层资产化（同日姊妹篇）
- [Loop与Graph两层架构](./2026-09-12-Loop与Graph-停止babysitting-agent的两层架构-循环内验证与图间编排拆解.md) — 循环内验证×图编排
- [Harness-Engineering完整指南](./2026-09-12-Harness-Engineering完整指南-19层从prompt到环境的工程纪律-LunarResearcher体系化拆解.md) — 19层工程纪律总纲
- [Ecdysis论文](./2026-09-12-Ecdysis论文-模型特异迁就vs-harness级修复-跨任务失败聚合与FDCR四角色拆解.md) — harness级修复vs模型迁就
- [Plano×Hermes效率判定](./2026-09-11-Plano-LLM路由层×Hermes效率判定-模型亲和与成本感知机制拆解与零破坏吸收方案.md) — 路由层/成本感知
- [MemSkill与自进化Agent分类学](./2026-09-12-MemSkill与自进化Agent分类学.md) — 自进化agent谱系定位
