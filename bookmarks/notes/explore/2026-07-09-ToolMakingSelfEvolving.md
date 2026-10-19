# Tool-Making and Self-Evolving LLM Agents in Low-Latency Systems

## 元数据

- 论文标题: Tool-Making and Self-Evolving LLM Agents in Low-Latency Systems
- 作者: Kalle Kujanpää, Ning Liu, Shahnawaz Alam, Yeshwanth Reddy Sura, Tianyu Yang, Kristina Klinkner, Shervin Malmasi
- 日期: 2026-07-09
- arXiv ID: 2607.08010
- 领域: cs.CL / cs.LG / cs.SE
- 关键词: tool-making, self-evolving agent, SOP compilation, production deployment, MCP, CodeAct

## 核心问题与研究动机

生产环境 LLM Agent 面临一个核心矛盾：**CodeAct 范式让 Agent 在每次请求时重新生成代码执行相同流程**。当同一个工作流反复执行于稳定的后端时，Agent 反复解释同一段指令、重新发现相同的 schema、重新生成相似代码，导致：

1. **延迟浪费** — 最复杂的场景 sub-agent 循环超过 100 个 LLM turn
2. **可靠性下降** — run-to-run variance 导致相同输入产生不同结果
3. **可审计性差** — 生成的代码每次都不同，难以追踪

论文的场景：亚马逊履约中心（Fulfillment Center）出站月台告警分诊系统。Agent 需要遵循一个 44 节点决策树 SOP（19 个动作节点 + 44 个决策节点），对告警进行诊断并执行操作（从简单的流程告警到昂贵的设备关停）。

## 方法论（详细）

### 整体架构：离线编译 → 在线调用

核心思想：**将推理时的编码循环替换为离线工具编译流水线**。SOP 中每个决策节点被"编译"成一个确定性的、带版本号的工具函数，Agent 在运行时直接调用而非重新生成代码。

### 1. 离线工具制造流水线（3 个模型组件）

**组件 A — 数据采集子 Agent（Data-Collector Sub-Agent）**
- 本质是基线 CodeAct 子 Agent，有生产 MCP 访问权限
- 对每个节点，在 3 个采样训练用例上运行（跨 verdict 标签均衡采样）
- 写代码、执行查询、迭代直到得到最终 verdict
- 产出 trace 包含：查询代码、MCP 响应、观察到的 schema（字段名、数据类型、值范围）、graded verdict
- **关键价值**：补全 SOP 文本中省略的执行细节（人类能推断但 LLM 无法知道的字段名、空值处理、边界约定）

**组件 B — 工具制造 LLM（Tool-Maker LLM）**
- 输入条件：SOP 节点文本 + 节点在决策树中的位置（父节点、子节点）+ 数据采集 trace
- 产出：候选工具函数（统一签名 `(warehouse, timestamp, context) → verdict(true/false/no_data) + 支撑细节`）
- context 携带站点特定参数和父节点 verdict

**组件 C — 反射器 LLM（Reflector LLM）**
- 测试候选工具：对完整标注训练集运行，收集不一致用例
- 反射器接收失败的 `(input, expected, predicted)` 三元组 + 前一个候选，写出简短的失败诊断
- 工具制造 LLM 基于诊断和失败案例进行重写
- 循环上限 3 轮，候选通过全部训练集时提前终止
- 选择训练集 pass rate 最高的候选部署

### 2. Agent 微调（3.2 节）

生产延迟约束将 Agent 限制在小模型。蒸馏方案：

- Teacher（大模型）生成轨迹，rejection sampling 保留观测值/根因/动作全部匹配 ground truth 的轨迹
- Student（小模型）用 LoRA 微调
- **关键设计**：75% 轨迹有工具可用（但每条随机禁用 25% 工具），25% 轨迹全部无工具（回退到 CodeAct）
- 这保证了 Agent 在工具缺失/失败时仍能手动推理
- 实测：工具微调后的 Agent 在禁用工具时，准确率（96.9%）与从未训练工具的 Agent（97.2%）统计无差异 → 混合轨迹微调保留了 fallback 能力

### 3. 运行时架构

两种配置：
- **子 Agent 配置**：主 Agent 将节点委托给子 Agent，子 Agent 调用节点的工具
- **直接调用配置**：主 Agent 直接调用工具，无需子 Agent 层（因为工具输出很小，仅几个 token）

每个工具返回：verdict + 观察值 + 阈值 + 文本解释。"No data" 预留给缺失指标，异常触发回退到 CodeAct。

## 关键实验结果与数据

### 工具制造质量（pass@1）

- 44 个决策节点，每节点 100-200 个标注用例，共 8,011 训练 + 8,022 评估
- 消融实验（GLM-4.7）：
  - 仅 SOP 文本：75.7%
  - SOP + 数据采集 trace（+D）：84.9%
  - SOP + 修复循环（+R）：89.3%
  - SOP + D + R（完整配置）：94.5%
- 四模型对比：GLM-4.7 (94.5%) > GLM-5 (93.6%) > Qwen3 235B (81.1%) > GLM-4.7 Flash (65.8%)
- 4 个节点占了几乎所有剩余错误（3 个有 SOP/标签未覆盖的 edge case，1 个有模糊聚合窗口）
- 澄清 SOP + 增强数据 → Opus 达到 99.9% pass@1

### 生产延迟（Table 3）

- 子 Agent + 工具 vs 子 Agent + 代码：p50 降低 42%，p99 降低 41%
- 输出 token 减少 58%（14,998 → 6,225）
- 子 Agent turn 数减少 45%（33.7 → 18.7）
- 直接调用 vs 子 Agent（同模型隔离）：p50 额外降低 62%，p99 额外降低 30%

### 端到端准确率（Table 4）

- Qwen3 32B：97.2% → 98.2%（错误率降低 36%）
- GLM-4.5-Air：98.3% → 99.2%（子 Agent），99.3%（直接调用，错误率降低 53%）

### 生成成本

- 完整 44 节点工具库一次性成本：800K tokens
- 工具跨模型迁移：GLM-4.7 生成的工具库直接服务于 Qwen3 32B 和 GLM-4.5-Air，无需重新生成

### 生产验证

- 部署后 5,000+ 生产告警调用
- 监控 Agent 发现 3 个上游环境不一致（字段类型差异、累积 vs 当前事件、百分比 → 小数格式漂移）

## 创新点分析

1. **SOP 到工具的编译范式**：不是让 Agent 在线编码，而是离线"编译"SOP 步骤为确定性工具。这是从解释执行到编译执行的范式转变
2. **环境锚定的工具生成**：数据采集 trace 提供了 SOP 文本省略的执行细节（字段名、数据类型、值范围），这是纯文本生成无法获得的
3. **测试-修复循环**：反射器 LLM 诊断失败 → 工具制造 LLM 重写，形成离线 self-improvement loop
4. **工具版本化与漂移检测**：版本化工具的确定性输出使上游数据漂移可见——相同的输入产生相同的输出，偏差可追溯
5. **跨模型迁移**：强模型一次性生成工具库，弱模型在运行时调用——推理成本从每次请求分摊到一次性生成

## 局限性与未来方向

- **单一领域验证**：仅在出站月台告警分诊一个应用上部署，泛化到自由形式 runbook 尚未验证
- **人类监督仍必需**：漂移检测和候选工具生成已自动化，但无法保证完全自动捕获所有失败
- **SOP 澄清本质是人类任务**：SOP 编码了作者对流程应如何执行的意图
- **标注数据仍有价值**：无标签变体落后有标签天花板不到 3pp，但完全无标签尚不可行
- **4/44 节点占大部分错误**：瓶颈在于 SOP 规范质量而非 Agent 能力

## 借鉴点（关联 Hermes Agent / Jetson Orin / 量化交易）

### P0 — 可直接落地

**1. Skill 编译模式（核心借鉴）**

论文的"离线编译 SOP → 工具"直接映射到 Hermes Skill 系统。当前 Hermes Skill 是静态指令文档，缺乏论文中的"环境锚定 + 测试-修复"机制。可借鉴：
- 为高频 Skill 添加"数据采集 trace"步骤：首次执行时记录实际 API 端点、返回 schema、字段类型，写入 Skill 的 references/ 目录
- 为关键 Skill 添加"测试-修复循环"：Skill 中嵌入自验证步骤（如 `extract_arxiv.py` 的各子命令都带降级链就是一种简化版）
- 已有类似实践：daily-paper-reading skill 中积累的"坑点 → patch"循环就是手工版的 test-repair

**2. 混合轨迹微调 → 混合 fallback 设计**

论文的 Agent 微调策略（75% 有工具 / 25% 随机禁用 / 25% 全无）启发 Hermes 的 Skill fallback 设计：
- 每个 Skill 的关键步骤都应有 CodeAct fallback 路径
- 当前已有降级链（如 web_search → curl → DDG），但缺乏系统化的"随机禁用验证"
- 可改进：Skill 执行失败后自动回退到内联 CodeAct，而非直接报错

### P1 — 高价值改进

**3. 版本化工具的漂移检测**

论文中版本化工具发现了 3 个上游环境不一致。Hermes 的 cron job 也可以借鉴：
- cron job 每次执行结果应记录"工具版本 + 输入 + 输出"
- 定期比较历史输出，检测上游 API/数据源的行为漂移
- 已有雏形：watchdog 和 error-monitoring skill，但缺乏系统化的 drift detection

**4. 跨模型工具迁移**

论文证明强模型生成、弱模型调用的可行性。Hermes 可借鉴：
- 用 GLM-5 或 Claude 生成 Skill 模板和 reference 文档
- 日常执行用更便宜的模型（如 GLM-4.5-Air）
- 已有实践：daily-paper-reading 用强模型做深度分析，但选文和提取用弱模型

### P2 — 中期改进

**5. MCP 工具制造自动化**

论文的工具制造流水线（data-collector → tool-maker → reflector）可以自动化应用到 Hermes 的 MCP 工具开发：
- 对频繁调用的 MCP 端点，自动生成封装 Skill
- 使用测试-修复循环验证封装的正确性

**6. 量化交易策略编译**

SOP 决策树编译为确定性工具的模式，可映射到量化交易：
- 将策略规则（如 MA5 择时、连板接力规则）编译为确定性函数
- 减少运行时 LLM 推理开销
- 版本化策略便于回测和审计

## 关联论文

- Eluna (Liu et al., 2026b) — 基础分层多 Agent 架构
- CodeAct (Wang et al., 2024a) — 在线代码生成范式（本文的改进对象）
- EvoSOP (2607.07321) — Agent 自进化工具生命周期管理（四模块 Construct/Merge/Evaluate/Prune），互补视角
- LedgerAgent (2606.20529) — Agent 工具调用架构借鉴
- Beyond the Leaderboard (2607.05775) — LLM Agent 失败模式分类法，论文中 sub-agent 的两种失败模式（偏离 SOP、报告错误）是该分类法的具体实例

## 相关笔记

- [EvoSOP自进化工具优化](./2026-07-10-EvoSOP自进化工具优化.md) — 原子操作→SOP迭代，同一研究谱系
- [MIA记忆智能Agent双向进化](../2026-07-12-MIA记忆智能Agent-参数化非参数化双向进化-2026记忆驱动自进化全景.md) — 参数化+非参数化进化
- [EverMind-Raven自进化框架](../2026-07-08-EverMind-Raven-自进化Agent框架与数字生命L2到L3跨越.md) — 自重写L2→L3跨越
- [EvolveMem-MemRL统一分类法](../2026-07-08-AI-Agent记忆自进化架构2026-EvolveMem-MemRL-统一分类法.md) — 记忆自进化架构
- [自进化Agent2026全景3x3框架](../2026-07-10-自进化Agent2026全景-3x3框架-BDI-LLM-OpenSpace-AutoResearch.md) — BDI+LLM进化矩阵
- [HyperAgents元认知修改](../2026-07-11-HyperAgents自进化Agent元认知修改-图记忆生命周期.md) — 图记忆生命周期
