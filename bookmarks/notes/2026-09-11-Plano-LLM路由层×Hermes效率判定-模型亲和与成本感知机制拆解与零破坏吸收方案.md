# Plano LLM 路由层 × Hermes 效率提升判定：模型亲和/成本感知/偏好路由三分机制拆解 + 本机已有设施对照 + 零破坏吸收方案

> **来源**：X/Twitter @_avichawla（Avi Chawla）Article《I cut my Hermes Agent bill 2x (in just 1 min)》2026-08 末（推文 ID 时间线）
> **原文链接**：https://x.com/_avichawla/status/2074068305380618275
> **工具**：Plano（开源 LLM 路由代理，GitHub planoai）+ Arch-Router-1.5B（HuggingFace，人类偏好训练的路由模型）
> **对照对象**：本机 Hermes 实例（config.yaml 实测：主模型 GLM + 8 条 fallback_providers 链 + auxiliary 七个子系统独立配置）
> **抓取方式**：X Article 直读全文 + 本机 config/skills 只读核对
> **笔记日期**：2026-09-11
> **关联笔记**：《Harness重塑AI性能》（配对即性能单位）《LLM八种精度格式》《自进化Harness与记忆》

---

## 零、结论先行

**三分判定：①模型亲和（model affinity）——我们已有等价机制（session 内模型天然钉住），Plano 价值为零；②成本感知选择——我们的成本结构（智谱免费额度+多池分流）与"每 token 计价"前提不符，直接用会倒退；③偏好对齐路由（Arch-Router-1.5B 按任务分类分流）——唯一有真实增量价值的机制，但我们应吸收思想而非引入代理层（在 auxiliary 子系统粒度做静态路由，零新组件）。** Coinbase 5%→60% 缓存命中的核心不是路由模型，是"会话粘性+便宜默认"两条纪律——这两条我们一条已有一条不需要。

## 一、Plano 是什么（忠实还原）

### 1.1 定位

LLM 路由代理：坐在 app 与模型商之间，读每个 prompt、分类任务、自动转发到"能处理它的最便宜模型"。宣称来源：Coinbase 工程组织的做法（Brian Armstrong："人类不该是选模型的人，选模型是 AI 的活"）——Coinbase 实测缓存命中率 5%→60%，花费近减半而用量继续涨。

### 1.2 三种路由方法

| 方法 | 机制 | 适用 |
|------|------|------|
| Model-based | 客户端每次显式指定模型名 | 无路由 |
| Alias-based | 友好名（fast-model/reasoning-model）映射真实模型 | 换模型改一行配置 |
| **Preference-aligned** | 客户端不指定；**Arch-Router-1.5B**（人类偏好数据训练）推断 domain/action 匹配偏好 | 文章主推 |

### 1.3 三个核心机制

**① 模型亲和（解决路由的头号问题）**：一个 agent 任务=多次 LLM 调用链（规划→工具→读输出→分析）。若每次独立分类：call 1 → sonnet-4.5（代码），call 4 → gpt-4o-mini（分析）——**两个灾难**：call 4 的模型没有 call 1 的决策记忆；每次换模型缓存全失效按全价重算。Plano 解法：会话首调路由定模，**pin 到 session ID（header 传递）**，后续同 ID 一律同模型（默认 10 分钟）；换任务换新 ID；多副本用 Redis 共享 pin。

**② 成本感知选择**：两模型都能干时，读定价目录按总 token 成本重排候选——便宜者答，贵者留作失败 fallback。`planoai obs` 观测台带每请求 USD 成本列。

**③ YAML 而非代码**：路由决策全在配置——便宜模型换代改一行；更好模型超越时改偏好指向。agent 代码零改动。

### 1.4 Hermes 接入方式（文章演示）

Hermes 连任意 OpenAI 兼容端点 → 把 base_url 指向 Plano → Plano 分类后经 OpenRouter 转发。"同一 Hermes 会话，简单问题自动 gpt-4o-mini，代码生成自动 claude-sonnet-4.5，零分支逻辑。"

## 二、逐机制判定（×本机实测对照）

### 2.1 模型亲和：✅ 已有等价物，Plano 价值为零

| Plano 假设的问题 | 本机实况 |
|-----------------|---------|
| 每次调用独立分类→会话中途换模型 | **Hermes 会话内模型由 config 钉死**（model: GLM-5.3），无 per-call 路由——问题不存在 |
| 换模型缓存失效全价重算 | 我们无跨模型缓存依赖；智谱 coding_plan 按请求计费无缓存折扣结构 |

**判定**：Plano 的 affinity 是给"无状态 per-call 路由"打的补丁；Hermes 的架构（会话级模型绑定）天然免疫这个问题。**引入 Plano 反而新增一跳代理延迟。**

### 2.2 成本感知选择：❌ 前提不符，直接用会倒退

| Plano 前提 | 本机实况 |
|-----------|---------|
| 每 token 计费，gpt-4o-mini 便宜 | **主力智谱 GLM=订阅额度（coding_plan），边际成本≈0** |
| 定价目录可比 | 池化多号（sensenova×4 池）的成本差异在**限流并发**不在单价（pool@8899 并发≈1 必 429 的教训） |
| 便宜模型失败→贵模型 fallback | 已有 **8 条 fallback_providers 链**（glm-5.2×4 池 → flash-lite×3 池），按池健康度非价格排序 |

**判定**：我们的瓶颈是**池的并发与限流**，不是单价。按价格重排会打乱按池健康的 fallback 设计——model-fallback-chain/model-fallback-troubleshooting 两个 skill 记录的整套经验会被绕过。**明确不引入。**

### 2.3 偏好对齐路由（按任务分流）：🟡 唯一有增量价值的机制——但吸收思想而非代理

文章演示的真价值：**简单问题→便宜模型，代码/推理→强模型**。本机对照：

| 我们已有的分流 | 层位 |
|---------------|------|
| auxiliary 七子系统独立 provider/model（approval/compression/curator/mcp/session_search 等各自配 sensenova/zai + 独立 timeout） | **正是静态的任务级路由**——curator 用 sensenova 600s，mcp 用 zai 30s |
| adaptive-inference-routing skill（推理预算自适应） | 复杂度→token 上限的路由思想已在库 |
| free-model-apis skill（智谱+HF+GitHub Models 四线免费） | 供给端分流已有 |
| cron-bulk-management（cron 模型分配） | 定时任务的静态路由 |

**缺口在哪**：auxiliary 的分流是**手配的**（七个子系统逐个设），没有"新增任务类型时自动选便宜模型"的机制。但——我们的任务类型有限（对话主链+七辅助），**静态手配完全够用且可控**；Arch-Router-1.5B 的动态分类对我们是过度工程（还引入 1.5B 推理开销与分类错误风险——错误分类把代码任务送去弱模型=质量事故）。

**结论**：吸收"任务→模型档位"的思想核对一遍 auxiliary 配置是否有明显错档（如 session_search 用了过强模型），**零新组件**。

## 三、Coinbase 案例的祛魅（本笔记核心批判）

文章把 Coinbase 5%→60% 缓存/花费减半归功于"路由层"。拆开看：

1. **缓存命中 5%→60% 的真正来源是会话粘性**（同模型同前缀才命中）——Hermes 会话级绑定模型已天然满足，不需要 Plano 的 pin 机制
2. **"花费近减半"的来源是"默认便宜模型"策略**（routine 任务大量占比）——这与我们"智谱订阅额度内边际≈0"的结构不同；对按 token 付费的用户才是真实节省
3. **Coinbase 自建路由层配了专职工程师**（"inside custom harnesses with engineers assigned to own it"）——维护成本文章一笔带过；Plano 开源版 ≠ Coinbase 规模的工程
4. **文章是教程营销**（导流 Plano repo + 作者日更教程号）——数字全部来自 Coinbase/Plano 自述，无独立验证；"1 min 完成"指安装不指效果

## 四、可吸收的三个增量（零破坏，全部本机原生实现）

| # | 动作 | 依据 | 工作量 |
|---|------|------|--------|
| 1 | **auxiliary 七子系统档位审计**：逐个核对 compression/curator/mcp/session_search 等的 provider/model 是否与任务复杂度匹配（弱任务用强模型=浪费额度，强任务用 flash-lite=质量险） | §2.3 缺口 | 0.5 天（改 config 一处一行，可逆） |
| 2 | **per-request 成本观测列**：`planoai obs` 的启发——我们的 gateway 事件日志加"本请求 provider/model/token 数"聚合（observability-dashboard skill 已有底子，补 model 维度） | §1.3② | 0.5 天 |
| 3 | **alias 思想用于 fallback 链**：config 的 fallback 手列 8 条重复池名——若 Hermes 支持 provider 组概念则一档一行；不支持则写个 config 生成小脚本（源码级，低风险） | §1.3③ | 0.5 天（可选） |

**不做的**（明确记录理由防手痒）：
- ❌ 引入 Plano 代理层——会话级模型绑定已免疫其核心问题；代理跳数+新组件维护成本>收益
- ❌ Arch-Router 动态分类——任务类型有限且手配可控；分类错误风险不可接受
- ❌ 按 price 重排 fallback——池健康度 ≠ 单价，会破坏现有 429 经验

## 五、批判性审视

1. **"bill 2x"标题党**：降 50-70% 是 Coinbase 口径（app 内 routine 占比高）；教程作者的 Hermes 账单数字没给——演示只证明"路由生效"没证明"省钱多少"
2. **模型亲和是补丁不是特性**：如果路由层不做 per-call 独立分类，根本不需要 pin——Plano 先制造问题再解决它的结构值得警惕
3. **Arch-Router-1.5B 的偏好数据偏差**：训练于"开发者偏好"——偏好随模型代际漂移（sonnet-4.5 的偏好数据对 4.6 过时），路由模型本身有维护成本
4. **10 分钟 pin 的边界情况**：长任务（>10min）中途 pin 过期会换模型——恰好在我们长训盯盘/长管线场景是真实风险，文章未讨论
5. **缓存命中的口径**：5%→60% 没说分母（全部请求 or 可缓存请求）——缓存命中率是易操纵指标

## 六、金句提取

> "Model selection is a job for AI."（Brian Armstrong）

> "The routing decision lived in the YAML, not in the agent."

> "The model on call 4 has no memory of decisions made in call 1. And every model switch invalidates the cache."

## 七、局限性

1. Plano 源码未读（路由实现质量以文章为准）；GitHub star 数未核
2. Coinbase 数据全部二手（文章转述 Armstrong），无原始工程博客核对
3. 本机 config.yaml 只读了 model/fallback/auxiliary 段（~340 行），其余配置未全扫
4. §四动作 3 依赖 Hermes 对 provider 组的支持情况未验证（源码未查）
5. 未实际跑 Plano 验证（判定基于机制分析，"不引入"结论不依赖实测）

## 出处标注

| 章节 | 来源类型 |
|------|---------|
| 一 | **原文忠实还原**（X Article 全文直读） |
| 二 | **本机对照判定**（config.yaml 实测 + skills 库盘点） |
| 三、五 | **批判性审视**（本笔记扩展） |
| 四 | **零破坏吸收方案**（待拍板，零代码改动） |
