# DeepSeek Reasonix：开源省钱 Agent

> **来源**：林芯 · 微信公众号 · 2026-05-25
> **原文**：https://mp.weixin.qq.com/s/8LaYH8lpkZTQuEnz2LsoUg
> **关联**：[[2026-05-25-DeepSeek-V4-Pro永久降价75-AI价格战新阶段]] [[2026-05-21-MLA多头潜在注意力-DeepSeek-KV缓存压缩与推理优化]] [[2026-05-15-上下文才是Agent的命门-QClaw上下文竞争论]] [[Claude-Code之父Boris-Cherny-编程已死千级Agent夜间打工]]
> **格式**：双格式(MD + HTML) · 含借鉴进化点 · RAG/wiki联动

## 摘要

DeepSeek Reasonix 是专为 DeepSeek 设计的开源 AI 编码代理，4 月 21 日开源后 35 天获 7000+ star，冲上 HN 热榜。核心创新不在"模型更便宜"，而在**缓存优先架构设计**——通过严格保证 Prompt 前缀绝对稳定，将 KV Cache 命中率从通用 Agent 的 3%-20% 提升到 99.82%。配合双模智能切换（Flash 日常 + Pro 攻坚）和工具呼叫维修机制，实测 4.35 亿 Token 仅花费 12 美元。

## 核心内容

### 三大支柱

**支柱一：缓存优先循环**

DeepSeek 的缓存折扣极其夸张（命中缓存的输入 Token 低至 $0.003625/百万），但通用 Agent 因为每轮动态注入时间戳/Git 分支/文件列表等，导致缓存命中率仅 3%-20%。Reasonix 的工程方案：

| 区域 | 内容 | 缓存策略 |
|------|------|---------|
| **Immutable Prefix** | system + tool_specs + few_shots | 会话期间固定不变，缓存命中核心 |
| **Append-Only Log** | [assistant₁][tool₁][assistant₂]... | 严格保留先前轮次前缀 |
| **Volatile Scratch** | R1 思考、临时计划状态 | 每轮重置，绝不发送给上游 |

并行工具调度支持 `parallelSafe?: boolean` 声明，通过串行屏障确保数据读写顺序一致。

**支柱二：工具呼叫维修**

DeepSeek 在实际使用中的失效模式及修复：

| 失效模式 | 修复方案 |
|---------|---------|
| 工具调用 JSON 遗留在 reasoning_content 中 | Scavenge：正则+JSON 解析器从思考内容中捞出 |
| 参数超过 10 个或深度嵌套时参数丢失 | Flatten：点号标记法展示，调用前重新组装 |
| 连续多轮相同参数调用同一工具 | Storm：滑动窗口检测重复元组，抑制调用并注入反思 |
| max_tokens 导致 JSON 截断 | Truncation：补全右括号或请求续写 |

**支柱三：成本控制**

| 机制 | 说明 |
|------|------|
| **分层默认（Flash 优先）** | 默认 auto 预设：平时 v4-flash，困难轮次自动升级 v4-pro；辅助调用强制用 v4-flash |
| **轮次结束自动压缩** | >3000 tokens 的工具结果就地压缩，后续轮次仅看摘要 |
| **/pro 单轮手动解锁** | 用户输入 /pro 仅让下一轮用 v4-pro，随后自动降级 |
| **失败信号自动升级** | 实时统计"Flash 挣扎"信号（文件报错/找不到文件/工具修复），达到阈值自动升级 v4-pro |

### 实测数据

| 指标 | Reasonix | 不使用缓存 |
|------|---------|-----------|
| 输入 Token | 4.35 亿 | 4.35 亿 |
| 缓存命中率 | **99.82%** | 0% |
| 成本 | **$12** | $61 |
| 节省 | **79%** | — |

## 关键概念

- **KV Cache 前缀缓存**：DeepSeek 仅在与前一个请求的字节前缀完全匹配时激活缓存，任何前缀变动都会使缓存失效
- **Append-Only Log**：仅追加不修改的历史日志，保证前缀链不断裂
- **Volatile Scratch**：易失性草稿区，思考过程不发送给模型，避免污染缓存
- **Scavenge/Flatten/Truncation/Storm**：工具呼叫维修的四个阶段管道

## 能力边界

- 专为 DeepSeek API 设计，不兼容其他模型
- 终端 Agent，不适合图形界面场景
- 缓存策略依赖 DeepSeek 的缓存折扣机制，其他模型无此优势
- 官网页面体验较差（动画文字导致页面抖动）

## 最佳实践

- 编码 Agent 应严格分离"不可变前缀"和"易失性草稿"
- 工具调用失败时优先尝试自动修复而非直接重试
- 工具结果超过阈值时主动压缩，避免上下文滚雪球
- Flash/Pro 双模切换是低成本使用前沿模型的有效策略

## 🔍 借鉴学习进化点

| # | 点 | 原文要点 | 对当前系统的借鉴 | 行动计划 |
|---|-----|---------|---------------|---------|
| 1 | **Append-Only Log 缓存优先** | 将上下文分为 Immutable Prefix + Append-Only Log + Volatile Scratch 三区，缓存命中率 99.82% | Hermes 的 session_search 用 FTS5 全文索引，但 Prompt Memory 每次注入可能破坏缓存 | 在 config.yaml 的 Prompt Memory 中分离"固定系统提示"和"动态上下文"，固定部分注入一次后不再变动 |
| 2 | **工具呼叫维修管道** | Scavenge/Flatten/Truncation/Storm 四阶段自动修复工具调用失效 | Hermes 工具调用失败时直接报错，无自动修复机制 | 在 skill 层增加工具调用失败后的自动修复逻辑（正则捞出、JSON 补全、重复抑制） |
| 3 | **Flash/Pro 双模切换** | 默认 Flash，困难轮次自动升级 Pro，/pro 手动单轮解锁 | 当前 ubot 主模型 zai/glm-5.1 固定不变，无动态降级/升级 | 在 fallback_providers 中配置多模型降级链，结合 antigravity failover 实现智能切换 |
| 4 | **工具结果自动压缩** | >3000 tokens 的工具结果就地压缩，后续轮次仅看摘要 | Hermes 工具输出直接注入上下文，无压缩机制 | 在 execute_code 的 terminal 输出处理中增加自动压缩（摘要提取） |
| 5 | **失败信号自动升级** | 实时统计"挣扎信号"（报错/找不到文件/工具修复），达到阈值自动升级 | 当前无失败信号监测 | 在 cron 或 skill 中增加失败信号计数器，触发升级策略 |

**三问自检结果**：
- ✅ 可复用方法/模式？缓存优先架构（三区划分）+ 工具维修管道 → 可沉淀为 skill
- ✅ 可优化自身配置？Prompt Memory 固定/动态分离 + 工具结果压缩 → 已有 antigravity failover，可扩展
- ✅ 关键事实？Reasonix 是 DeepSeek 生态首个缓存优先 Agent，HN 热榜+7k star → 记入 Memory

## 🔗 RAG / Wiki 联动

### 当前状态
- session_search：✅ FTS5 全文索引覆盖
- 工具调用失败修复：❌ 无自动修复机制
- 多模型动态切换：⚠️ antigravity failover 已安装但未与模型质量信号联动
- 工具结果压缩：❌ 无压缩机制

### 改进方案
1. 在 config.yaml 中分离 Prompt Memory 的固定部分和动态部分
2. 在 skill 层增加工具调用失败后的四阶段修复管道
3. 工具输出增加自动压缩（摘要提取，>3000 tokens 触发）
4. 与 antigravity failover 联动，增加"挣扎信号"监测

### 已执行操作
- ✅ 三问自检完成，识别出 5 个进化点
- ✅ 关联已有笔记建立双链

## 相关笔记

<!-- 使用 @note 链接相关笔记 -->
